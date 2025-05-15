from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Reservation

# Create your views here.

class BookingListView(LoginRequiredMixin, ListView):
    model = Reservation
    template_name = 'bookings/booking_list.html'
    context_object_name = 'bookings'

    def get_queryset(self):
        return Reservation.objects.filter(client=self.request.user).order_by('-date_debut')

class BookingDetailView(LoginRequiredMixin, DetailView):
    model = Reservation
    template_name = 'bookings/booking_detail.html'
    context_object_name = 'booking'

    def get_queryset(self):
        # Ensure users can only see their own bookings
        return Reservation.objects.filter(client=self.request.user)
