# File: models.py
# Author: Kevin Tan (ktan03@bu.edu)
# Description: Models for the flight app 

from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from datetime import timedelta

"""
This module defines the models for an airline booking system. 
The models include airports, aircraft types, flights, airplane rentals, 
shopping carts for users, and user profiles. Each model represents a 
specific component of the system, with attributes and relationships 
that allow for efficient data management and operations.
"""

# Airport model
class Airport(models.Model):
    """
    Represents an airport with details such as name, IATA/ICAO code, city, 
    country, available amenities, average security time, and an optional 
    image URL for visualization.
    """
    name = models.CharField(max_length=100)  # Name of the airport
    code = models.CharField(max_length=10, unique=True)  # IATA or ICAO code
    city = models.CharField(max_length=100)  # City where the airport is located
    country = models.CharField(max_length=100)  # Country where the airport is located
    amenities = models.TextField(blank=True, null=True)  # List of amenities available
    avg_security_time = models.DurationField(default=timedelta(minutes=30))  # Default to 30 mins
    image_url = models.URLField(blank=True)  # Optional image URL for the airport

    def __str__(self):
        """
        Returns a string representation of the airport, displaying its 
        name and code.
        """
        return f"{self.name} ({self.code})"

# Aircraft type model
class AircraftType(models.Model):
    """
    Represents a type of aircraft with attributes for its model name 
    and seating capacity.
    """
    model = models.CharField(max_length=50)  # Specific model name
    seat_capacity = models.PositiveIntegerField()  # Total number of seats

    def __str__(self):
        """
        Returns a string representation of the aircraft type, displaying 
        its model.
        """
        return f"{self.model}"

# Flights model
class Flight(models.Model):
    """
    Represents a flight with details such as flight number, departure 
    and arrival airports, departure and arrival times, cost, aircraft, 
    amenities, and seats left to book.
    """
    flight_number = models.CharField(max_length=10, unique=True)  # Unique flight number
    departure_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='departing_flights')
    arrival_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='arriving_flights')
    departure_time = models.DateTimeField()  # Scheduled departure time
    arrival_time = models.DateTimeField()  # Scheduled arrival time
    cost = models.DecimalField(max_digits=10, decimal_places=2)  # Cost of the flight
    aircraft = models.ForeignKey(AircraftType, on_delete=models.CASCADE)  # Aircraft used
    amenities = models.TextField(blank=True, null=True)  # Specific amenities for this flight
    seats_left = models.PositiveIntegerField()  # Number of seats left to book

    def __str__(self):
        """
        Returns a string representation of the flight, displaying its 
        flight number, departure airport code, and arrival airport code.
        """
        return f"{self.flight_number}: {self.departure_airport.code} to {self.arrival_airport.code}"

    @property
    def flight_duration(self):
        """
        Calculates and returns the duration of the flight as the 
        difference between the arrival and departure times.
        """
        return self.arrival_time - self.departure_time

# Airplane Rentals model
class AirplaneRental(models.Model):
    """
    Represents an airplane rental with details such as the aircraft, 
    rental cost, available amenities, and availability status.
    """
    aircraft = models.ForeignKey(AircraftType, on_delete=models.CASCADE)  # Aircraft for rental
    rental_cost = models.DecimalField(max_digits=10, decimal_places=2)  # Rental cost
    amenities = models.TextField(blank=True, null=True)  # Specific amenities for this rental
    available = models.BooleanField(default=True)  # Whether the airplane is available for rental

    def __str__(self):
        """
        Returns a string representation of the airplane rental, 
        displaying the aircraft model and rental status.
        """
        return f"{self.aircraft} - Rental"

# Shopping Cart model
class ShoppingCart(models.Model):
    """
    Represents a shopping cart for a user, which can contain flights 
    and airplane rentals. Each user can have only one shopping cart.
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name="shopping_cart"
    )  # Link each shopping cart to one user

    def __str__(self):
        """
        Returns a string representation of the shopping cart, displaying 
        the username of the associated user.
        """
        return f"Shopping Cart for {self.user.username}"

    @property
    def total_price(self):
        """
        Calculates and returns the total price of all flights in the 
        shopping cart. Rentals can be added later.
        """
        flights_total = self.cart_flights.filter(cart=self).aggregate(total=Sum('flight__cost'))['total'] or 0
        return flights_total

# Relationship between ShoppingCart and Flight
class ShoppingCartFlight(models.Model):
    """
    Represents the relationship between a shopping cart and a flight, 
    allowing users to add multiple flights to their cart.
    """
    cart = models.ForeignKey(ShoppingCart, on_delete=models.CASCADE, related_name='cart_flights')  # Cart reference
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)  # Flight reference
    quantity = models.PositiveIntegerField(default=1)  # Optional, e.g., if one user books multiple tickets

    def __str__(self):
        """
        Returns a string representation of the shopping cart flight, 
        displaying the username and flight number.
        """
        return f"{self.cart.user.username}'s Cart - Flight {self.flight.flight_number}"

# Relationship between ShoppingCart and AirplaneRental
class ShoppingCartRental(models.Model):
    """
    Represents the relationship between a shopping cart and an airplane 
    rental, allowing users to rent aircraft for a specified number of days.
    """
    cart = models.ForeignKey(ShoppingCart, on_delete=models.CASCADE, related_name='cart_rentals')  # Cart reference
    rental = models.ForeignKey(AirplaneRental, on_delete=models.CASCADE)  # Rental reference
    rental_days = models.PositiveIntegerField(default=1)  # Number of days for rental

    def __str__(self):
        """
        Returns a string representation of the shopping cart rental, 
        displaying the username and rented aircraft.
        """
        return f"{self.cart.user.username}'s Cart - Rental {self.rental.aircraft}"

# Profile model for additional user preferences
class Profile(models.Model):
    """
    Represents a user's profile with additional preferences for filtering 
    flights or rentals.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="flights_profile")
    preferences = models.TextField(blank=True, null=True)  # Preferences for filtering flights or rentals

    def __str__(self):
        """
        Returns a string representation of the user profile, displaying 
        the username.
        """
        return f"{self.user.username}'s Profile"
