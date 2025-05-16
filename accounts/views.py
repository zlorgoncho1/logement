import random
import string
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.utils.translation import gettext_lazy as _
from django.views.generic import View
from django.db import transaction

from .forms import (
    ClientRegistrationStartForm, 
    OTPVerificationForm, 
    ClientProfileCompletionForm,
    UserLoginForm,
    AgentRegistrationForm
)
from .models import CustomUser # Ensure CustomUser is imported
from fichiers.models import Fichier # For creating Fichier instances

# For dummy OTP generation
def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))

class UserLoginView(LoginView):
    template_name = 'accounts/login.html' # Path to your custom login template
    form_class = UserLoginForm
    redirect_authenticated_user = True # Redirect if user is already logged in
    # success_url = reverse_lazy('index') # Or set LOGIN_REDIRECT_URL in settings.py

    # def get_success_url(self):
    #     # You can customize the redirect URL after successful login here if needed
    #     # For example, redirect based on user type, or to a specific dashboard.
    #     # If not overridden, it uses settings.LOGIN_REDIRECT_URL (defaults to /accounts/profile/)
    #     # or the ?next parameter if present.
    #     return reverse_lazy('index') # Example: redirect to homepage named 'index'

    def form_invalid(self, form):
        messages.error(self.request, _("Email ou mot de passe incorrect. Veuillez réessayer."))
        return super().form_invalid(form)

class UserLogoutView(LogoutView):
    next_page = reverse_lazy('index') # Redirect to homepage after logout

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        messages.success(request, _("Vous avez été déconnecté avec succès."))
        return response

class ClientRegistrationStartView(FormView):
    template_name = 'accounts/client_register_start.html'
    form_class = ClientRegistrationStartForm
    success_url = reverse_lazy('accounts:verify_otp') # Namespace 'accounts' assumed

    def form_valid(self, form):
        email_or_phone = form.cleaned_data['email_or_phone']
        # In a real app, you'd send OTP via email/SMS here
        otp = generate_otp()
        self.request.session['registration_otp'] = otp
        self.request.session['registration_contact'] = email_or_phone # Store email or phone
        
        # For demonstration, print OTP to console
        print(f"Generated OTP for {email_or_phone}: {otp}") 
        messages.info(self.request, _(f'Un code OTP a été envoyé (pour démo : {otp}).'))
        return super().form_valid(form)

class OTPVerificationView(FormView):
    template_name = 'accounts/client_verify_otp.html'
    form_class = OTPVerificationForm
    success_url = reverse_lazy('accounts:complete_profile')

    # This method checks if the required session data exists before processing the OTP verification view.
    # It ensures that users can't access the OTP verification page directly without first
    # going through the registration start process where the OTP is generated.
    # If the session data is missing, it redirects users back to the registration start page
    # with an error message.
    def dispatch(self, request, *args, **kwargs):
        if 'registration_otp' not in request.session or 'registration_contact' not in request.session:
            messages.error(request, _("Session invalide ou expirée. Veuillez recommencer."))
            return redirect(reverse_lazy('accounts:register_start'))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        submitted_otp = form.cleaned_data['otp']
        stored_otp = self.request.session.get('registration_otp')

        if submitted_otp == stored_otp:
            self.request.session['otp_verified'] = True
            messages.success(self.request, _("OTP vérifié avec succès."))
            return super().form_valid(form)
        else:
            messages.error(self.request, _("Code OTP incorrect. Veuillez réessayer."))
            return self.form_invalid(form)

class ClientProfileCompletionView(FormView):
    template_name = 'accounts/client_complete_profile.html'
    form_class = ClientProfileCompletionForm
    success_url = reverse_lazy('index') # Assuming 'home' is the name of your homepage URL

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('otp_verified'):
            messages.error(request, _("Veuillez d'abord vérifier votre OTP."))
            return redirect(reverse_lazy('accounts:verify_otp'))
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pre-fill email or phone if available from session for user convenience
        # The form's clean_email will still validate and check for uniqueness.
        contact_info = self.request.session.get('registration_contact', '')
        initial_data = {}
        if '@' in contact_info: # Basic check for email
            initial_data['email'] = contact_info
        else:
            initial_data['telephone'] = contact_info
        kwargs['initial'] = initial_data
        return kwargs

    def form_valid(self, form):
        user = form.save(commit=False)
        contact_info = self.request.session.get('registration_contact')
        
        # The form itself now handles email and telephone, ensuring email is present
        # and unique as per form definition. We can rely on the form's cleaned_data.
        # The user type is also set in the form's save method.
        user.save()

        # Clean up session variables
        del self.request.session['registration_otp']
        del self.request.session['registration_contact']
        del self.request.session['otp_verified']

        login(self.request, user) # Log the user in
        messages.success(self.request, _("Votre compte a été créé avec succès et vous êtes connecté."))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Veuillez corriger les erreurs ci-dessous."))
        return super().form_invalid(form)

class AgentRegisterView(View):
    template_name = 'accounts/agent_register.html'
    form_class = AgentRegistrationForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic(): # Ensure all operations succeed or none do
                    # 1. Create CustomUser
                    user = CustomUser.objects.create_user(
                        email=form.cleaned_data['email'],
                        password=form.cleaned_data['password'],
                        nom=form.cleaned_data['nom'],
                        prenom=form.cleaned_data['prenom'],
                        telephone=form.cleaned_data.get('telephone'),
                        type=CustomUser.UserType.AGENT,
                        is_active=False,  # Account inactive until KYC validated by admin
                        kyc_verified=False # KYC not verified initially
                    )

                    # 2. Handle KYC Document Upload and Fichier creation
                    kyc_document_file = form.cleaned_data.get('document_kyc')
                    if kyc_document_file:
                        fichier_instance = Fichier.objects.create(
                            fichier=kyc_document_file,
                            nom_fichier=kyc_document_file.name
                            # If Fichier model has a field to link to the user, set it here if appropriate
                            # e.g., uploaded_by=user, if such a field exists on Fichier
                        )
                        # Add to the user's KYC documents
                        user.documents_kyc.add(fichier_instance)
                        # user.save() # Not strictly necessary after .add() for M2M unless other fields on user changed before this call.
                                      # create_user already saves the user.

                messages.success(request, _("Votre compte agent a été créé avec succès. Il est en attente de validation par un administrateur après vérification de votre document KYC."))
                # Redirect to login or a specific "pending review" page
                return redirect(reverse_lazy('accounts:login')) 
            
            except Exception as e:
                # It's good practice to log the error: import logging; logger = logging.getLogger(__name__); logger.error(str(e))
                messages.error(request, _("Une erreur s'est produite lors de la création de votre compte. Veuillez réessayer."))
                # Consider more specific error messages for common issues if possible

        return render(request, self.template_name, {'form': form})
