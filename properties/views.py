from django.http import Http404
from django.shortcuts import render
from django.views import View
from django.urls import reverse_lazy
from django.views.generic import DetailView, CreateView, ListView, UpdateView
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from decimal import Decimal

from accounts.models import CustomUser
from .models import Logement, Disponibilite
from .forms import PropertySearchForm, PropertyForm, AvailabilityFormSet
from fichiers.models import Fichier
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
                    return redirect(reverse_lazy('index')) # Placeholder - create a proper pending page
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

class PropertyCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Logement
    form_class = PropertyForm
    template_name = 'properties/property_form.html' # Or property_create_form.html
    # success_url = reverse_lazy('properties:property_list_agent') # TODO: Define an agent property list URL

    def test_func(self):
        # Check if the user is an agent
        return self.request.user.is_authenticated and self.request.user.type == CustomUser.UserType.AGENT

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['availability_formset'] = AvailabilityFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            # For a new Logement, self.object is None. 
            # Inline formsets need an instance if they are to be saved against one immediately.
            # However, for a CreateView, the instance is only created *after* the main form is validated.
            # So, we create an empty formset or one bound to an unsaved instance for initial display.
            # Let's pass an empty formset initially. The saving logic will handle instance assignment.
            data['availability_formset'] = AvailabilityFormSet(instance=Logement()) # Pass a dummy unsaved instance
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        availability_formset = context['availability_formset']
        
        with transaction.atomic():
            # Set agent and initial status before saving the main form
            form.instance.agent = self.request.user
            # The Logement model defaults statut to EN_ATTENTE, so no need to set it here unless overriding
            # form.instance.statut = Logement.StatutLogement.EN_ATTENTE 
            self.object = form.save() # Save the Logement instance

            if availability_formset.is_valid():
                availability_formset.instance = self.object
                availability_formset.save()
            else:
                # If formset is invalid, we need to roll back or prevent main form save.
                # Transaction ensures this, but good to explicitly handle.
                messages.error(self.request, _("Erreur dans les informations de disponibilité. Veuillez corriger."))
                # Re-render the form with errors by returning form_invalid
                return self.form_invalid(form)

            # Handle photo uploads
            photos = self.request.FILES.getlist('photos_upload')
            for photo_file in photos:
                fichier_instance = Fichier.objects.create(
                    fichier=photo_file,
                    nom_fichier=photo_file.name
                    # uploaded_by=self.request.user # Optional: if Fichier model tracks uploader
                )
                self.object.photos.add(fichier_instance)
        
        messages.success(self.request, _("Le logement '%(titre)s' a été ajouté avec succès et est en attente de validation.") % {'titre': self.object.titre})
        return redirect(reverse_lazy('properties:agent_property_list')) # Changed to agent_property_list

    def form_invalid(self, form):
        messages.error(self.request, _("Erreur lors de l'ajout du logement. Veuillez vérifier les informations saisies."))
        context = self.get_context_data()
        # Ensure the formset is also passed back with its errors if any
        # If availability_formset was POSTed, it should be in context already with errors.
        return self.render_to_response(context)

    def get_success_url(self):
        # This method is called if form_valid successfully returns an HttpResponse.
        # Since form_valid now handles the redirect, this might not be strictly necessary
        # unless we remove the redirect from form_valid.
        return reverse_lazy('properties:agent_property_list') # Ensure consistency

class AgentPropertyListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Logement
    template_name = 'properties/agent_property_list.html'
    context_object_name = 'properties'
    paginate_by = 10 # Optional: Add pagination

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.type == CustomUser.UserType.AGENT

    def get_queryset(self):
        return Logement.objects.filter(agent=self.request.user).order_by('-date_creation')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _("Mes Annonces de Logement")
        return context

class PropertyUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Logement
    form_class = PropertyForm
    template_name = 'properties/property_form.html' # Can reuse the same form template
    # success_url will be defined in get_success_url or by direct redirect

    def test_func(self):
        # Check if the user is an agent and owns this property
        if not (self.request.user.is_authenticated and self.request.user.type == CustomUser.UserType.AGENT):
            return False
        # It's better to check ownership in get_queryset or by trying to get the object
        # For UpdateView, self.get_object() will be called. We can override it or get_queryset.
        try:
            logement = self.get_object() # self.get_object() is called by UpdateView internally
            return logement.agent == self.request.user
        except Http404:
             # This case should ideally not be reached if get_queryset is set up correctly,
             # but as a safeguard or if get_object is overridden differently.
            return False

    def get_queryset(self):
        # Ensure agents can only update their own properties
        return super().get_queryset().filter(agent=self.request.user)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        # self.object is the Logement instance being updated
        if self.request.POST:
            data['availability_formset'] = AvailabilityFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            data['availability_formset'] = AvailabilityFormSet(instance=self.object)
        data['form_title'] = _("Modifier le Logement: %(titre)s") % {'titre': self.object.titre}
        data['is_update_form'] = True # Flag for template if needed
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        availability_formset = context['availability_formset']

        with transaction.atomic():
            # Agent is already set and should not change here. Statut might change based on edits.
            # If an edit is made, it might be prudent to reset status to EN_ATTENTE for admin review, depending on policy.
            # For now, let's assume editing doesn't automatically change status unless specified.
            self.object = form.save()

            if availability_formset.is_valid():
                availability_formset.instance = self.object
                availability_formset.save()
            else:
                messages.error(self.request, _("Erreur dans les informations de disponibilité. Veuillez corriger."))
                return self.form_invalid(form)

            # Handle new photo uploads. 
            # Deleting existing photos would require more complex logic (e.g., checkboxes next to existing photos).
            new_photos = self.request.FILES.getlist('photos_upload')
            for photo_file in new_photos:
                fichier_instance = Fichier.objects.create(
                    fichier=photo_file,
                    nom_fichier=photo_file.name
                )
                self.object.photos.add(fichier_instance)
        
        messages.success(self.request, _("Le logement '%(titre)s' a été modifié avec succès.") % {'titre': self.object.titre})
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, _("Erreur lors de la modification du logement. Veuillez vérifier les informations saisies."))
        context = self.get_context_data()
        return self.render_to_response(context)

    def get_success_url(self):
        # Redirect to the agent's list of properties or the updated property's detail page
        return reverse_lazy('properties:agent_property_list')

class PropertyChangeStatusView(LoginRequiredMixin, UserPassesTestMixin, View):
    allowed_statuses_map = {}
    success_message = ""
    error_message = _("Action non autorisée ou propriété non trouvée.")

    def test_func(self):
        if not (self.request.user.is_authenticated and self.request.user.type == CustomUser.UserType.AGENT):
            return False
        try:
            logement = Logement.objects.get(pk=self.kwargs.get('pk'), agent=self.request.user)
            # Check if the current status allows this action
            return logement.statut in self.allowed_statuses_map.keys()
        except Logement.DoesNotExist:
            return False # Property not found or not owned by user

    def post(self, request, *args, **kwargs):
        try:
            logement = Logement.objects.get(pk=kwargs.get('pk'), agent=request.user)
            if logement.statut in self.allowed_statuses_map:
                new_status = self.allowed_statuses_map[logement.statut]
                logement.statut = new_status
                logement.save()
                messages.success(request, self.success_message % {'titre': logement.titre, 'statut': logement.get_statut_display()})
            else:
                messages.error(request, self.error_message)
        except Logement.DoesNotExist:
            messages.error(request, self.error_message)
        return redirect(reverse_lazy('properties:agent_property_list'))

class PropertyDeactivateView(PropertyChangeStatusView):
    # Agent can deactivate a published property
    allowed_statuses_map = {Logement.StatutLogement.PUBLIE: Logement.StatutLogement.DESACTIVE}
    success_message = _("Le logement '%(titre)s' a été désactivé avec succès.")
    error_message = _("Impossible de désactiver ce logement. Il n'est peut-être pas publié ou ne vous appartient pas.")

class PropertyActivateView(PropertyChangeStatusView):
    # Agent can request to re-publish a deactivated property (goes to pending)
    # Or an agent might want to "activate" a property that is in ATTENTE (though this is usually admin action to PUBLIE)
    # For simplicity, let's assume this action is for properties that were DESACTIVE
    allowed_statuses_map = {
        Logement.StatutLogement.DESACTIVE: Logement.StatutLogement.EN_ATTENTE,
        # Potentially also from ATTENTE back to EN_ATTENTE if they want to re-submit before admin action (no status change)
        # Logement.StatutLogement.ATTENTE: Logement.StatutLogement.EN_ATTENTE 
    }
    success_message = _("Le logement '%(titre)s' a été soumis pour révision et est maintenant en attente de validation.")
    error_message = _("Impossible d'activer ce logement. Il n'est peut-être pas désactivé, ou ne vous appartient pas.")

class PropertyManageAvailabilityView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Logement
    template_name = 'properties/manage_availability.html'
    # We are not using a form_class for the Logement model itself in this view,
    # but UpdateView requires it or fields. We'll override relevant methods.
    fields = [] # No fields from Logement model itself are being edited here.

    def test_func(self):
        if not (self.request.user.is_authenticated and self.request.user.type == CustomUser.UserType.AGENT):
            return False
        try:
            logement = self.get_object()
            return logement.agent == self.request.user
        except Http404:
            return False

    def get_queryset(self):
        return super().get_queryset().filter(agent=self.request.user)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        # self.object is the Logement instance
        if self.request.POST:
            data['availability_formset'] = AvailabilityFormSet(self.request.POST, instance=self.object)
        else:
            data['availability_formset'] = AvailabilityFormSet(instance=self.object)
        data['page_title'] = _("Gérer les Disponibilités pour: %(titre)s") % {'titre': self.object.titre}
        return data

    def post(self, request, *args, **kwargs):
        self.object = self.get_object() # Ensure self.object is set
        formset = AvailabilityFormSet(request.POST, instance=self.object)
        
        if formset.is_valid():
            with transaction.atomic():
                formset.save()
            messages.success(request, _("Les disponibilités pour '%(titre)s' ont été mises à jour avec succès.") % {'titre': self.object.titre})
            return redirect(reverse_lazy('properties:agent_property_list')) # Or back to this page
        else:
            messages.error(request, _("Erreur lors de la mise à jour des disponibilités. Veuillez corriger les erreurs."))
            # Need to pass the invalid formset back to the template
            # Call get_context_data to reconstruct context with the invalid formset
            # Re-render the page with the formset containing errors
            context = self.get_context_data(object=self.object) # Pass object to satisfy UpdateView context needs
            context['availability_formset'] = formset # Ensure the invalid formset is in context
            return self.render_to_response(context)

    def get_success_url(self):
        # This is called if not redirecting directly in post()
        return reverse_lazy('properties:agent_manage_availability', kwargs={'pk': self.object.pk})

# Placeholder for agent's list of properties (to be created later)
# class AgentPropertyListView(LoginRequiredMixin, UserPassesTestMixin, ListView):

