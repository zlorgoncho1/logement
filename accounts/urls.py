from django.urls import path
from .views import (
    ClientRegistrationStartView,
    OTPVerificationView,
    ClientProfileCompletionView,
    UserLoginView,
    UserLogoutView,
    AgentRegisterView
)

app_name = 'accounts'

urlpatterns = [
    path('register/', ClientRegistrationStartView.as_view(), name='register_start'),
    path('verify-otp/', OTPVerificationView.as_view(), name='verify_otp'),
    path('complete-profile/', ClientProfileCompletionView.as_view(), name='complete_profile'),
    path('register/agent/', AgentRegisterView.as_view(), name='agent_register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
] 