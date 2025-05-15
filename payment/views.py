import os
from django.shortcuts import render
import json
import hmac
import hashlib
import logging

from django.views import View
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseServerError, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

from .models import Paiement
from bookings.models import Reservation

logger = logging.getLogger(__name__)

def generate_signature(payload_bytes, secret_key):
    return hmac.new(secret_key.encode(), payload_bytes, hashlib.sha256).hexdigest()

@method_decorator(csrf_exempt, name='dispatch')
class NabooPayWebhookView(View):
    def post(self, request, *args, **kwargs):
        webhook_secret = os.getenv('NABOOPAY_WEBHOOK_SECRET')
        if not webhook_secret:
            logger.error("NABOOPAY_WEBHOOK_SECRET is not configured.")
            return HttpResponseServerError("Webhook secret not configured.")

        signature = request.headers.get('X-Signature') # Or the header NabooPay uses
        if not signature:
            logger.warning("Webhook request missing signature.")
            return HttpResponseForbidden("Invalid signature.")

        try:
            # The signature is usually generated from the raw request body bytes
            payload_bytes = request.body
            expected_signature = generate_signature(payload_bytes, webhook_secret)
        except Exception as e:
            logger.error(f"Error generating expected signature: {e}")
            return HttpResponseServerError("Signature generation error.")

        if not hmac.compare_digest(signature, expected_signature):
            logger.warning(f"Invalid webhook signature. Received: {signature}, Expected: {expected_signature}")
            return HttpResponseForbidden("Invalid signature.")

        try:
            payload = json.loads(payload_bytes.decode('utf-8'))
            logger.info(f"NabooPay Webhook received payload: {payload}")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding webhook JSON payload: {e}")
            return HttpResponse("Invalid JSON payload", status=400)

        # Process the payload
        # IMPORTANT: Confirm these field names with NabooPay's webhook documentation
        naboopay_order_id = payload.get("order_id") # This should be the ID NabooPay assigned
        # client_order_id = payload.get("client_order_id") # This might be your reservation.id if you passed it
        transaction_status = payload.get("transaction_status") # e.g., "SUCCESSFUL", "FAILED", "PENDING"
        amount_paid = payload.get("amount")

        if not naboopay_order_id or not transaction_status:
            logger.error("Webhook payload missing order_id or transaction_status.")
            return HttpResponse("Missing required fields in payload", status=400)

        try:
            with transaction.atomic():
                # Try to find the payment record using NabooPay's transaction ID
                paiement = Paiement.objects.select_related('reservation', 'reservation__logement').get(transaction_id=naboopay_order_id)
                reservation = paiement.reservation

                # Idempotency check: Only process if payment is still pending
                if paiement.statut != Paiement.StatutPaiement.EN_ATTENTE:
                    logger.info(f"Webhook for already processed payment {paiement.id} (status: {paiement.statut}). Ignoring.")
                    return JsonResponse({"message": "Webhook received, payment already processed"})

                # --- IMPORTANT: Confirm NabooPay's actual status strings --- 
                if transaction_status.upper() == "SUCCESSFUL": # Or "COMPLETED", "PAID", etc.
                    paiement.statut = Paiement.StatutPaiement.REUSSI
                    # Potentially update amount if it can differ, though webhook should match initial amount.
                    # paiement.montant = Decimal(amount_paid) 
                    paiement.save()

                    reservation.statut = Reservation.StatutReservation.CONFIRMEE
                    reservation.save()
                    logger.info(f"Payment {paiement.id} for Reservation {reservation.id} confirmed via webhook.")
                    # TODO: Send confirmation email/SMS to client
                    # TODO: Notify property owner/agent

                elif transaction_status.upper() == "FAILED": # Or "DECLINED", "CANCELLED"
                    paiement.statut = Paiement.StatutPaiement.ECHOUE
                    paiement.save()

                    # Decide if reservation should be cancelled or remain pending for another attempt
                    reservation.statut = Reservation.StatutReservation.ANNULEE
                    reservation.save()
                    logger.info(f"Payment {paiement.id} for Reservation {reservation.id} failed via webhook.")
                    # TODO: Notify client about payment failure
                
                else: # Handle other statuses like PENDING, REFUNDED etc. if needed
                    logger.info(f"Webhook for payment {paiement.id} received with status: {transaction_status}. No action taken for this status yet.")

            return JsonResponse({"message": "Webhook received and processed successfully"})

        except Paiement.DoesNotExist:
            logger.error(f"Webhook received for unknown NabooPay transaction_id: {naboopay_order_id}")
            return HttpResponse("Payment record not found", status=404)
        except Reservation.DoesNotExist: # Should not happen if Paiement exists and has reservation FK
            logger.error(f"Webhook: Reservation not found for Paiement with transaction_id: {naboopay_order_id}")
            return HttpResponseServerError("Associated reservation not found")
        except Exception as e:
            logger.error(f"Error processing webhook payload for naboopay_order_id {naboopay_order_id}: {e}")
            return HttpResponseServerError("Error processing webhook")
