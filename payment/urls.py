from django.urls import path
from .views import NabooPayWebhookView

app_name = 'payment'

urlpatterns = [
    path('webhook/naboopay/', NabooPayWebhookView.as_view(), name='naboopay_webhook'),
] 