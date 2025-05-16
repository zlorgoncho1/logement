from django.urls import path
from . import views as properties_views # Alias to avoid conflict if importing from bookings.views
from bookings import views as bookings_views # Assuming CreateBookingView is in bookings.views

app_name = 'properties'

urlpatterns = [
    path('search/', properties_views.PropertySearchView.as_view(), name='property_search'),
    path('<uuid:pk>/', properties_views.PropertyDetailView.as_view(), name='property_detail'),
    path('<uuid:pk>/book/', properties_views.PropertyDetailView.as_view(), name='property_book'),
    # URL for adding a new property by an agent
    path('add/', properties_views.PropertyCreateView.as_view(), name='property_add'),
    # URL for agents to view their list of properties
    path('my-properties/', properties_views.AgentPropertyListView.as_view(), name='agent_property_list'),
    # URL for an agent to edit one of their properties
    path('<uuid:pk>/edit/', properties_views.PropertyUpdateView.as_view(), name='property_edit'),
    # URLs for an agent to deactivate/activate their properties
    path('<uuid:pk>/deactivate/', properties_views.PropertyDeactivateView.as_view(), name='property_deactivate'),
    path('<uuid:pk>/activate/', properties_views.PropertyActivateView.as_view(), name='property_activate'),
    path('<uuid:pk>/manage-availability/', properties_views.PropertyManageAvailabilityView.as_view(), name='property_manage_availability'),
]