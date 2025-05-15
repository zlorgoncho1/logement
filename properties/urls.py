from django.urls import path
from .views import PropertySearchView, PropertyDetailView

app_name = 'properties'

urlpatterns = [
    path('search/', PropertySearchView.as_view(), name='property_search'),
    path('<uuid:pk>/', PropertyDetailView.as_view(), name='property_detail'),
]