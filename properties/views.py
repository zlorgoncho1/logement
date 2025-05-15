from django.shortcuts import render
from django.views import View

from accounts.models import CustomUser
from .models import Logement
from .forms import PropertySearchForm
from django.views.generic import DetailView
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal

from bookings.forms import BookingForm
from bookings.models import Reservation
from payment.models import Paiement
from payment.services import NabooPayService

# Create your views here.

class PropertySearchView(View):
    def get(self, request):
        form = PropertySearchForm(request.GET or None)
        properties = Logement.objects.filter(statut='PUBLIE')
        if form.is_valid():
            location = form.cleaned_data.get('location')
            property_type = form.cleaned_data.get('property_type')
            min_price = form.cleaned_data.get('min_price')
            max_price = form.cleaned_data.get('max_price')

            if location:
                properties = properties.filter(adresse__icontains=location)
            if property_type and property_type != 'Tous':
                properties = properties.filter(type=property_type)
            if min_price is not None:
                properties = properties.filter(prix_par_nuit__gte=min_price)
            if max_price is not None:
                properties = properties.filter(prix_par_nuit__lte=max_price)
        
        context = {
            'form': form,
            'properties': properties
        }
        return render(request, 'properties/property_search.html', context)

class PropertyDetailView(DetailView):
    model = Logement
    template_name = 'properties/property_detail.html'
    context_object_name = 'property'

    def get_queryset(self):
        return super().get_queryset().filter(statut=Logement.StatutLogement.PUBLIE)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['booking_form'] = BookingForm()
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.type != CustomUser.UserType.CLIENT:
            messages.error(request, "Vous devez être connecté en tant que client pour réserver.")
            return redirect('accounts:login') # Or a relevant page
        print("DEBUG: User is authenticated")
        self.object: Logement = self.get_object()
        form = BookingForm(request.POST)
        if form.is_valid():
            print("DEBUG: Form is valid")
            date_arrivee = form.cleaned_data['date_arrivee']
            date_depart = form.cleaned_data['date_depart']
            
            # Basic check for availability (can be expanded with Disponibilité model)
            # For now, let's assume if it's published, it's bookable for any date in future.
            # More complex availability check would query the Disponibilité model or existing reservations.
            nombre_nuits = (date_depart - date_arrivee).days
            if nombre_nuits <= 0:
                message_error = "La durée du séjour doit être d'au moins une nuit."
                messages.error(request, message_error)
                context = self.get_context_data(booking_form=form)
                context['error_message'] = message_error
                return self.render_to_response(context)
            print("DEBUG: Nombre de nuits calculé")
            montant_total = self.object.prix_par_nuit * nombre_nuits
            acompte = montant_total * Decimal('0.20') # 20% deposit

            try:
                print("DEBUG: Création de la réservation")
                reservation = Reservation.objects.create(
                    client=request.user,
                    logement=self.object,
                    date_debut=date_arrivee,
                    date_fin=date_depart,
                    montant_total=montant_total,
                    acompte=acompte, # Store the calculated deposit amount
                    statut=Reservation.StatutReservation.EN_ATTENTE
                )
                print("DEBUG: Réservation créée")
                # Create a pending payment record
                # The actual payment initiation with NabooPay will happen next.
                # For now, we create the Paiement record and will later integrate the redirect.
                paiement = Paiement.objects.create(
                    reservation=reservation,
                    montant=acompte, # Payment is for the deposit amount
                    methode=Paiement.MethodePaiement.MOBILE_MONEY, # Default or choose based on user input later
                    statut=Paiement.StatutPaiement.EN_ATTENTE
                )
                print("DEBUG: Paiement créé")
                # Initiate NabooPay payment
                naboopay_service = NabooPayService()
                payment_info_for_naboo = {
                    'property_id': str(self.object.id),
                    'booking_id': str(reservation.id),
                    'amount': int(montant_total),
                    'product_name': f"Acompte réservation: {self.object.titre} - Nuit(s): {nombre_nuits}",
                    'product_category': 'Logement Reservation',
                    'quantity': 1,
                    'order_id': str(reservation.id), # Our internal reservation ID
                    'is_escrow': True # As per spec, escrow by default
                    # 'product_description': f"Réservation pour {self.object.titre} du {date_arrivee.strftime('%Y-%m-%d')} au {date_depart.strftime('%Y-%m-%d')}"
                }
                print("DEBUG: Création de la transaction NabooPay")
                payment_url, transaction_id = naboopay_service.create_transaction(payment_info_for_naboo, request)
                print("DEBUG: Transaction NabooPay créée")
                print(payment_url, transaction_id)
                
                if payment_url and transaction_id:
                    paiement.transaction_id = transaction_id
                    paiement.save()
                    messages.success(request, f"Réservation initiée pour {self.object.titre}. Redirection vers le paiement...")
                    return redirect(payment_url)
                elif transaction_id: # Payment initiated, but no direct redirect URL (e.g. USSD push)
                    paiement.transaction_id = transaction_id
                    paiement.save()
                    messages.info(request, f"Paiement initié pour {self.object.titre}. Veuillez suivre les instructions sur votre téléphone.")
                    # Redirect to a page that explains next steps or a pending payment page
                    return redirect(reverse('index')) # Placeholder - create a proper pending page
                else:
                    # Handle NabooPay initiation failure
                    reservation.statut = Reservation.StatutReservation.ANNULEE 
                    reservation.save()
                    paiement.statut = Paiement.StatutPaiement.ECHOUE
                    paiement.save()
                    messages.error(request, "Erreur lors de l'initiation du paiement via NabooPay. Veuillez réessayer ou contacter le support.")
                    return self.render_to_response(self.get_context_data(booking_form=form))

            except Exception as e:
                print("DEBUG: Erreur lors de la création de la réservation")
                print(e)
                messages.error(request, f"Une erreur est survenue lors de la création de la réservation: {e}")
                return self.render_to_response(self.get_context_data(booking_form=form))
        else:
            print("DEBUG: Formulaire invalide")
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
            return self.render_to_response(self.get_context_data(booking_form=form))
