# File: views.py
# Author: Kevin Tan (ktan03@bu.edu)
# Description: Views for the flight app 

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy
from django.shortcuts import render
from .models import Flight, Airport, AirplaneRental, ShoppingCart, ShoppingCartFlight, ShoppingCartRental, AircraftType
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm
from django.http.response import HttpResponse as HttpResponse
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.contrib.auth import login
from typing import Any
from django.urls import reverse
from django.http import HttpResponseRedirect
import requests
from django.contrib import messages
from datetime import timedelta
import random



# List view for flights
class FlightListView(ListView):
    """
    Displays a paginated list of all flights.

    This view is responsible for showing the available flights in the system.
    It supports searching by flight number and filtering based on departure 
    and arrival airports. The results are paginated for better user experience.
    """
    model = Flight
    template_name = 'flights/show_all_flights.html'
    context_object_name = 'flights'
    paginate_by = 10

    def get_queryset(self):
        """
        Retrieves the queryset of flights to display based on search filters.

        If a search query is provided (flight number, departure airport, or arrival airport),
        it filters the flights accordingly.
        """
        queryset = super().get_queryset()
        query = self.request.GET.get('q')  # Text search
        departure_airport = self.request.GET.get('departure_airport')  # Selected departure airport
        arrival_airport = self.request.GET.get('arrival_airport')  # Selected arrival airport

        if query:
            queryset = queryset.filter(
                Q(flight_number__icontains=query)  # Search by flight number
            )
        if departure_airport and departure_airport != "all":
            queryset = queryset.filter(departure_airport__id=departure_airport)
        if arrival_airport and arrival_airport != "all":
            queryset = queryset.filter(arrival_airport__id=arrival_airport)

        return queryset

    def get_context_data(self, **kwargs):
        """
        Adds additional context data for the template.

        Includes search filters, available airports, and whether the user has an active shopping cart.
        """

        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')  # Pass search term to template
        context['selected_departure_airport'] = self.request.GET.get('departure_airport', 'all')  # Selected departure airport
        context['selected_arrival_airport'] = self.request.GET.get('arrival_airport', 'all')  # Selected arrival airport
        context['airports'] = Airport.objects.all()  # Pass all airports to template
        context['user'] = self.request.user # Return a user

        if self.request.user.is_authenticated: # Checking if user is authenticated to create carts
            context['has_cart'] = ShoppingCart.objects.filter(user=self.request.user).exists()
        else:
            context['has_cart'] = False
        return context

# Detail view for a specific flight
class FlightDetailView(DetailView):
    """
    Displays detailed information about a specific flight.

    This view provides additional information about a flight, such as
    its departure and arrival airports, associated aircraft, and amenities.
    """

    model = Flight
    template_name = 'flights/flight_detail.html'
    context_object_name = 'flight'

    def get_context_data(self, **kwargs):
        """
        Adds additional context data for the flight.

        Includes the related departure and arrival airports, and whether
        the user has an active shopping cart.
        """

        context = super().get_context_data(**kwargs)
        # Add the related Airport objects to the context
        context['departure_airport'] = self.object.departure_airport
        context['arrival_airport'] = self.object.arrival_airport

        if self.request.user.is_authenticated: # Checking if user is authenticated to create carts
            context['has_cart'] = ShoppingCart.objects.filter(user=self.request.user).exists()
        else:
            context['has_cart'] = False
        return context


# Create view for adding a flight
class FlightCreateView(LoginRequiredMixin, CreateView):
    """
    Allows authenticated users to add flights by fetching data from an external API.

    Users can specify departure and arrival airports and dates, and the system
    fetches relevant flight data from an external service and saves it to the database.
    """

    template_name = 'flights/import_flights.html'

    def get(self, request, *args, **kwargs):
        """
        Render the flight import form with available airports.
        """
        airports = Airport.objects.all()
        return render(request, self.template_name, {"airports": airports})

    def post(self, request, *args, **kwargs):
        """
        Handle the flight import request triggered by the user.
        """
        departure_id = request.POST.get("departure_id")
        arrival_id = request.POST.get("arrival_id")
        outbound_date = request.POST.get("outbound_date")
        departure_city = request.POST.get("departure_city")
        departure_country = request.POST.get("departure_country")
        arrival_city = request.POST.get("arrival_city")
        arrival_country = request.POST.get("arrival_country")


        # API setup
        api_key = "d764904413d0f85fcb35954a94356a3cb2c27e21726f437941bcdbfdeb166d3d"
        endpoint = "https://serpapi.com/search"
        params = {
            "engine": "google_flights",
            "departure_id": departure_id,
            "arrival_id": arrival_id,
            "outbound_date": outbound_date,
            "currency": "USD",
            "hl": "en",
            "type": 2,
            "api_key": api_key,
        }

        try:
            # Fetch data from API
            response = requests.get(endpoint, params=params)
            if response.status_code != 200:
                raise Exception(f"API Error: {response.status_code}, {response.text}")

            data = response.json()
            self.import_flights(data, departure_city, departure_country, arrival_city, arrival_country)
            messages.success(request, "Flights imported successfully!")
            return redirect("all_flights")
        except Exception as e:
            messages.error(request, f"Error importing flights: {str(e)}")
            return render(request, self.template_name, {"airports": Airport.objects.all()})

    def import_flights(self, data, departure_city, departure_country, arrival_city, arrival_country):
        """
        Manually Parses and imports flight data into the database.
        """
        for flight_data in data.get("best_flights", []):
            for leg in flight_data["flights"]:
                # Handle departure airport
                departure_airport, _ = Airport.objects.get_or_create(
                    name=leg["departure_airport"]["name"],
                    code=leg["departure_airport"]["id"],
                    defaults={
                        "city": departure_city,
                        "country": departure_country,
                        "amenities": "",
                        "avg_security_time": timedelta(minutes=random.randint(5, 30)),
                    },
                )


                # Handle arrival airport
                arrival_airport, _ = Airport.objects.get_or_create(
                    name=leg["arrival_airport"]["name"],
                    code=leg["arrival_airport"]["id"],
                    defaults={
                        "city": arrival_city,
                        "country": arrival_country,
                        "amenities": "",
                        "avg_security_time": timedelta(minutes=random.randint(5, 30)),
                    },
                )


                # Handle aircraft type
                aircraft, _ = AircraftType.objects.get_or_create(
                    model=leg.get("airplane", "Unknown"),
                    seat_capacity=200,
                )

                # Create or update the flight
                Flight.objects.update_or_create(
                    flight_number=leg["flight_number"],
                    defaults={
                        "departure_airport": departure_airport,
                        "arrival_airport": arrival_airport,
                        "departure_time": leg["departure_airport"]["time"],
                        "arrival_time": leg["arrival_airport"]["time"],
                        "cost": flight_data.get("price", 0.0),
                        "aircraft": aircraft,
                        "amenities": ", ".join(leg.get("extensions", [])),
                        "seats_left": random.randint(50, 200),
                    },
                )


# Update view for editing a flight
class FlightUpdateView(LoginRequiredMixin, UpdateView):
    """
    View to update the details of an existing flight.
    """
    model = Flight
    template_name = 'flights/flight_update.html'  # New template
    fields = [
        'flight_number', 'departure_airport', 'arrival_airport', 
        'departure_time', 'arrival_time', 'cost', 'aircraft', 
        'amenities', 'seats_left'
    ]

    def get_context_data(self, **kwargs):
        """
        Add additional context to the template.
        """
        context = super().get_context_data(**kwargs)
        context['airports'] = Airport.objects.all()
        context['aircrafts'] = AircraftType.objects.all()
        return context

    def get_success_url(self):
        """
        Redirects to the detail page of the updated flight.
        """
        return reverse('flight_detail', kwargs={'pk': self.object.pk})

# Delete view for removing a flight
class FlightDeleteView(LoginRequiredMixin, DeleteView):
    """
    View to delete an existing flight.
    """
    model = Flight
    template_name = 'flights/flight_confirm_delete.html'

    def get_success_url(self):
        """
        Redirects to the detail page of the deletion of flight.
        """
        return reverse('all_flights')


# List view for airports
class AirportListView(ListView):
    """
    Handles the display of a list of all airports.
    """
    model = Airport
    template_name = 'flights/airport_list.html' 
    context_object_name = 'airports' 

    def get_context_data(self, **kwargs):
        """
        Adds extra context data to the list view if needed.
        """
        context = super().get_context_data(**kwargs)
        return context


# Detail view for a specific airport
class AirportDetailView(DetailView):
    """
    Handles the display of details for a specific airport.
    """
    model = Airport
    template_name = 'flights/airport_detail.html' 
    context_object_name = 'airport'  

    def get_context_data(self, **kwargs):
        """
        Adds extra context data to the detail view if needed.
        """
        context = super().get_context_data(**kwargs)
        context['departing_flights'] = Flight.objects.filter(departure_airport=self.object)
        context['arriving_fligths'] = Flight.objects.filter(arrival_airport=self.object)
        return context


# Shopping cart creation view
class ShoppingCartCreateView(LoginRequiredMixin, CreateView):
    """
    View to create a shopping cart for the logged-in user.
    """
    model = ShoppingCart
    template_name = 'flights/create_cart.html'  # Optional: Create a specific template if needed
    fields = []  # No fields required, as the user is assigned programmatically

    def form_valid(self, form):
        """
        Automatically assigns the logged-in user to the shopping cart upon creation.
        """
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """
        Redirects the user to their shopping cart after it is created.
        """
        return reverse_lazy('shopping_cart')


# Shopping cart view
class ShoppingCartView(LoginRequiredMixin, ListView):
    """
    Handle the display of the shopping cart.
    Displays all flights in the logged-in user's shopping cart, along with the total price.
    """
    model = ShoppingCart
    template_name = 'flights/shopping_cart.html'
    context_object_name = 'shopping_cart'

    def get_context_data(self, **kwargs):
        """
        Retrieves the shopping cart data, including flights and total price, for the logged-in user.
        """
        context = super().get_context_data(**kwargs)
        # Ensure a shopping cart exists for the user
        cart, created = ShoppingCart.objects.get_or_create(user=self.request.user)
        context['cart_flights'] = ShoppingCartFlight.objects.filter(cart=cart)
        context['total_price'] = cart.total_price
        return context

class CheckoutView(LoginRequiredMixin, View):
    """
    Handles the checkout process for the shopping cart.
    Queries the SerpAPI for purchasing options for flights in the shopping cart.
    """

    def get(self, request, *args, **kwargs):
        """
        Handles the GET request for the checkout page.
        Retrieves flights in the shopping cart and queries SerpAPI.
        """
        cart = request.user.shopping_cart
        cart_flights = cart.cart_flights.all()
        serpapi_results = []

        for cart_flight in cart_flights:
            # Prepare parameters for SerpAPI
            print(cart_flight.flight.departure_airport.code)
            print(cart_flight.flight.arrival_airport.code)
            print(cart_flight.flight.departure_time.strftime("%Y-%m-%d"))
            airline_code = cart_flight.flight.flight_number[:2]
            params = {
                "engine": "google_flights",
                "departure_id": cart_flight.flight.departure_airport.code,
                "arrival_id": cart_flight.flight.arrival_airport.code,
                "outbound_date": cart_flight.flight.departure_time.strftime("%Y-%m-%d"),
                "currency": "USD",
                "hl": "en",
                "type": "2",
                # "include_airlines": airline_code,
                # "deep_search": "true",
                "api_key": "d764904413d0f85fcb35954a94356a3cb2c27e21726f437941bcdbfdeb166d3d",
            }

            # Make the request to SerpAPI
            try:
                response = requests.get("https://serpapi.com/search.json", params=params)
                if response.status_code == 200:
                    flight_data = response.json()
                    for best_flight in flight_data.get("best_flights", []):
                        best_flight["last_arrival_airport"] = best_flight["flights"][-1]["arrival_airport"]["name"]
                    serpapi_results.append(flight_data)
                else:
                    serpapi_results.append({"error": response.text})  # Log full error
            except requests.RequestException as e:
                serpapi_results.append({"error": str(e)})


        # Render the checkout page with SerpAPI results
        return render(request, "flights/checkout.html", {"serpapi_results": serpapi_results})


# Add flight to shopping cart view
class AddFlightToCartView(LoginRequiredMixin, UpdateView):
    """
    Add a flight to the logged-in user's shopping cart.
    """
    model = ShoppingCartFlight
    fields = []  # No additional input required; handled internally.

    def post(self, request, *args, **kwargs):
        """
        Adds a flight to the user's shopping cart and redirects back to the shopping cart view.
        Ensures the cart exists for the user before adding the flight.
        """
        cart, created = ShoppingCart.objects.get_or_create(user=self.request.user)
        flight = Flight.objects.get(pk=kwargs['pk'])
        ShoppingCartFlight.objects.create(cart=cart, flight=flight)
        return redirect('shopping_cart')


# Delete shopping cart view
class DeleteShoppingCartView(LoginRequiredMixin, DeleteView):
    """
    Delete the entire shopping cart for the logged-in user.
    """
    model = ShoppingCart

    def get_object(self, queryset=None):
        """
        Fetches the shopping cart object belonging to the logged-in user.
        """
        print("DeleteShoppingCartView is being called")
        return ShoppingCart.objects.get(user=self.request.user)
    
    def get_success_url(self):
        """Return the URL to redirect to after successfully deleting the cart."""
        return reverse('all_flights')

class RegistrationView(CreateView):
    '''Handle registration of new Users.'''

    template_name = 'flights/register.html'
    form_class = UserCreationForm

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        '''Handle the User creation form submission'''

        if self.request.POST:
            print(f"ReigstrationView.dispatch: self.request.POST={self.request.POST}")

            # reconstruct the UserCreateForm from the POST data
            form = UserCreationForm(self.request.POST)
            
            # if the form isn't value e.c. passwords don't match
            if not form.is_valid():
                print(f"form.errors={form.errors}")
                
                # let CreateView.dispatch handle the problem
                return super().dispatch(request, *args, **kwargs)

            # save the form, which creates a new User
            user = form.save() # this will commit the insert to the database
            print(f"RegistrationView.dispatch: created user {user}")

            # log the user in
            login(self.request, user)
            print(f"RegistrationView.dispatch: {user} is logged in")
            

            # return a response
            return redirect(reverse('all_flights'))

        # let CreateView.dispatch handle the HTTP GET request
        return super().dispatch(request, *args, **kwargs)