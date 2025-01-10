## flights/urls.py
## description: URL patterns for the blog app

from django.urls import path
from django.conf import settings
from . import views
from django.contrib.auth import views as auth_views

# all of the URLs that are part of this app
urlpatterns = [
    # All URLs for the flight app
    path(r'', views.FlightListView.as_view(), name='all_flights'), # Detail view to show all flights
    path(r'flight/<int:pk>/', views.FlightDetailView.as_view(), name='flight_detail'),  # Detail view for a specific flight

    path(r'login/', auth_views.LoginView.as_view(template_name='flights/login.html'), name='login'), # Login feature
    path(r'logout/', auth_views.LogoutView.as_view(next_page='all_flights'), name='logout'), # Logout feature
    path(r'register/', views.RegistrationView.as_view(), name='register'), # Register

    path(r'cart/', views.ShoppingCartView.as_view(), name='shopping_cart'), # Shopping Cart view
    path(r'cart/create/', views.ShoppingCartCreateView.as_view(), name='create_cart'), # Create Shopping Cart
    path(r'cart/add/<int:pk>/', views.AddFlightToCartView.as_view(), name='add_to_cart'), # Add things to Shopping Cart
    path(r'cart/delete/', views.DeleteShoppingCartView.as_view(), name='delete_cart'), # Delete Shopping Cart
    path(r'checkout/', views.CheckoutView.as_view(), name='checkout'),  # Checkout view

    path(r'airports/', views.AirportListView.as_view(), name='airport_list'),  # URL for the list of airports
    path(r'airports/<int:pk>/', views.AirportDetailView.as_view(), name='airport_detail'),  # URL for airport details

    path(r'flights/import/', views.FlightCreateView.as_view(), name='import-flights'), # Create new flights
    path(r'flights/<int:pk>/update/', views.FlightUpdateView.as_view(), name='flight-update'), # Update flights
    path(r'flights/<int:pk>/delete/', views.FlightDeleteView.as_view(), name='flight-delete'), # Delete a flight
]