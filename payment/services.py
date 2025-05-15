import os
import requests
from django.conf import settings
import logging
from django.urls import reverse
import json

logger = logging.getLogger(__name__)

class NabooPayService:
    BASE_URL = 'https://api.naboopay.com/api/v1'
    API_TOKEN = os.getenv('NABOOPAY_API_TOKEN')

    def __init__(self):
        if not self.API_TOKEN:
            logger.error("NABOOPAY_API_TOKEN is not configured as an environment variable.")

    def create_transaction(self, payment_details, request=None):
        """
        Creates a transaction with NabooPay.
        payment_details should be a dict containing:
            - 'amount': float (total amount for the product)
            - 'product_name': str
            - 'product_category': str (e.g., 'Reservation Deposit')
            - 'quantity': int (usually 1 for a reservation deposit)
            - 'order_id': str (unique order identifier, e.g., reservation.id)
            - 'method_of_payment': list (e.g., ["WAVE"], ["ORANGE_MONEY"])
            - 'is_escrow': bool (True for escrow, False otherwise)
            - 'product_description': str (optional)
        request: The Django HttpRequest object, used for building absolute URLs if needed.
        Returns a tuple (payment_redirect_url, naboopay_transaction_id) or (None, None) on failure.
        """
        print("DEBUG: Création de la transaction NabooPay")
        if not self.API_TOKEN:
            logger.error("Cannot create NabooPay transaction: API token missing.")
            return None, None
        print("DEBUG: API token présent")
        endpoint = f'{self.BASE_URL}/transaction/create-transaction'
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.API_TOKEN}'
        }
        print("DEBUG: Headers présents")
        # Construct product details for NabooPay
        products_payload = [{
            "name": payment_details.get('product_name', 'Paiement Réservation'),
            "category": payment_details.get('product_category', 'Service Digital'),
            "amount": payment_details.get('amount', 0),
            "quantity": payment_details.get('quantity', 1),
            "description": payment_details.get('product_description', '')
        }]
        print("DEBUG: Products payload présents")
        payload = {
            "method_of_payment": ["WAVE", "ORANGE_MONEY", "BANK"],
            "products": products_payload,
            "is_escrow": payment_details.get('is_escrow', True),
            "success_url": request.build_absolute_uri(reverse('bookings:reservation_detail', kwargs={'pk': payment_details.get('booking_id')})).replace('http', 'https'),
            "is_merchant": True,
            "error_url": request.build_absolute_uri(reverse('properties:property_detail', kwargs={'pk': payment_details.get('property_id')})).replace('http', 'https'),
        }
        print("DEBUG: Payload présents")
        try:
            print("DEBUG: Tentative de création de la transaction")
            logger.debug(f"NabooPay Create Transaction Request Payload: {payload}")
            print(endpoint, payload, headers)
            response = requests.put(endpoint, data=json.dumps(payload), headers=headers, timeout=30)
            print("DEBUG: Réponse de la transaction")
            response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
            print(response.text)
            response_data = response.json()
            print(response_data)
            print("DEBUG: Réponse de la transaction")
            logger.info(f"NabooPay Create Transaction Response: {response_data}")
              
            payment_redirect_url = response_data.get('checkout_url')            
            naboopay_transaction_id = response_data.get('order_id')
            print("DEBUG: URL de paiement et ID de transaction")
            if not payment_redirect_url and not naboopay_transaction_id:
                 logger.warning("NabooPay response did not contain a recognizable payment URL or transaction ID.")
            print("DEBUG: URL de paiement et ID de transaction")
            return payment_redirect_url, naboopay_transaction_id

        except requests.exceptions.HTTPError as http_err:
            logger.error(f"NabooPay API HTTP error: {http_err} - Response: {http_err.response.text}")
        except requests.exceptions.RequestException as req_err:
            logger.error(f"NabooPay API request failed: {req_err}")
        except Exception as e:
            logger.error(f"Error processing NabooPay response or request: {e}")
            
        return None, None 