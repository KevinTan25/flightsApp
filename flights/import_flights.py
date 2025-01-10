# File: import_flights.py
# Author: Kevin Tan (ktan03@bu.edu)
# Description: Temporary code to import data for the flight app 
# This code is put into FlightCreateView in views

import requests
from datetime import timedelta
from flights.models import Airport, AircraftType, Flight

# Example: Fetch data from an external API
def fetch_flight_data():
    api_key = "d764904413d0f85fcb35954a94356a3cb2c27e21726f437941bcdbfdeb166d3d"  # API
    endpoint = "https://serpapi.com/search"
    params = {
        "engine": "google_flights",
        "departure_id": "HND",  # Example departure airport code
        "arrival_id": "ICN",   # Example arrival airport code
        "outbound_date": "2024-12-23",
        "return_date": "2024-12-31",
        "currency": "USD",
        "hl": "en",
        "api_key": api_key,
    }

    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error fetching flight data: {response.status_code}, {response.text}")

# Function to fetch and import flights into the database
def fetch_and_import_flights():
    data = fetch_flight_data()

    # Parse flight data
    for flight_data in data.get("best_flights", []):
        for leg in flight_data["flights"]:
            # Handle departure airport
            departure_airport, _ = Airport.objects.get_or_create(
                name=leg["departure_airport"]["name"],
                code=leg["departure_airport"]["id"],
                city=leg.get("departure_city", "Unknown"),
                country=leg.get("departure_country", "Unknown"),
                amenities="",
                avg_security_time=timedelta(minutes=30)  # Default to 30 minutes
            )

            # Handle arrival airport
            arrival_airport, _ = Airport.objects.get_or_create(
                name=leg["arrival_airport"]["name"],
                code=leg["arrival_airport"]["id"],
                city=leg.get("arrival_city", "Unknown"),
                country=leg.get("arrival_country", "Unknown"),
                amenities="",
                avg_security_time=timedelta(minutes=30)  # Default to 30 minutes
            )

            # Handle aircraft type
            aircraft, _ = AircraftType.objects.get_or_create(
                manufacturer="Unknown",  # Replace with actual manufacturer if available
                model=leg.get("airplane", "Unknown"),
                seat_capacity=200,  # Replace with actual seat capacity if available
            )

            # Create or update the flight
            flight, _ = Flight.objects.update_or_create(
                flight_number=leg["flight_number"],
                defaults={
                    "departure_airport": departure_airport,
                    "arrival_airport": arrival_airport,
                    "departure_time": leg["departure_airport"]["time"],
                    "arrival_time": leg["arrival_airport"]["time"],
                    "cost": flight_data.get("price", 0.0),
                    "aircraft": aircraft,
                    "amenities": ", ".join(leg.get("extensions", [])),
                    "seats_left": 100,  # Replace with actual seat data if available
                },
            )

    print("Flight data imported successfully.")



# from flights.models import Airport, Flight, AircraftType
# from datetime import datetime, timedelta

# def check_and_import_airport(code, name, city, country):
#     """
#     Check if an airport with the given code exists. If not, create it.
#     """
#     airport, created = Airport.objects.get_or_create(
#         code=code,
#         defaults={
#             "name": name,
#             "city": city,
#             "country": country,
#             "avg_security_time": timedelta(minutes=30),  # Default to 30 minutes
#         }
#     )
#     if created:
#         print(f"Airport {code} created: {airport}")
#     else:
#         print(f"Airport {code} already exists: {airport}")
#     return airport

# def check_and_import_aircraft(manufacturer, model, seat_capacity):
#     """
#     Check if an aircraft type exists. If not, create it.
#     """
#     aircraft, created = AircraftType.objects.get_or_create(
#         manufacturer=manufacturer,
#         model=model,
#         defaults={"seat_capacity": seat_capacity}
#     )
#     if created:
#         print(f"Aircraft {manufacturer} {model} created.")
#     else:
#         print(f"Aircraft {manufacturer} {model} already exists.")
#     return aircraft

# def check_and_import_flight(flight_number, departure_airport, arrival_airport, departure_time, arrival_time, cost, aircraft):
#     """
#     Check if a flight with the given flight number exists. If not, create it.
#     """
#     flight, created = Flight.objects.get_or_create(
#         flight_number=flight_number,
#         defaults={
#             "departure_airport": departure_airport,
#             "arrival_airport": arrival_airport,
#             "departure_time": departure_time,
#             "arrival_time": arrival_time,
#             "cost": cost,
#             "aircraft": aircraft,
#             "seats_left": aircraft.seat_capacity,  # Default seats left to aircraft capacity
#         }
#     )
#     if created:
#         print(f"Flight {flight_number} created.")
#     else:
#         print(f"Flight {flight_number} already exists.")
#     return flight

# # Example usage
# def import_flight_data():
#     # Example flight data
#     flight_data = {
#         "departure_code": "BOS",
#         "departure_name": "Boston Logan International Aiport",
#         "departure_city": "Boston",
#         "departure_country": "USA",
#         "arrival_code": "HND",
#         "arrival_name": "Tokyo International Airport",
#         "arrival_city": "Tokyo",
#         "arrival_country": "Japan",
#         "departure_time": "2024-12-10",
#         "arrival_time": "2024-12-16",
#         "aircraft_model": "777",
#         "manufacturer": "Boeing",
#         "seat_capacity": 300,
#         "cost": 1200.00,
#     }

#     # Check and import airports
#     departure_airport = check_and_import_airport(
#         code=flight_data["departure_code"],
#         name=flight_data["departure_name"],
#         city=flight_data["departure_city"],
#         country=flight_data["departure_country"],
#     )
#     arrival_airport = check_and_import_airport(
#         code=flight_data["arrival_code"],
#         name=flight_data["arrival_name"],
#         city=flight_data["arrival_city"],
#         country=flight_data["arrival_country"],
#     )

#     # Check and import aircraft
#     aircraft = check_and_import_aircraft(
#         manufacturer=flight_data["manufacturer"],
#         model=flight_data["aircraft_model"],
#         seat_capacity=flight_data["seat_capacity"],
#     )

#     # Check and import flight
#     check_and_import_flight(
#         flight_number=flight_data["flight_number"],
#         departure_airport=departure_airport,
#         arrival_airport=arrival_airport,
#         departure_time=datetime.fromisoformat(flight_data["departure_time"]),
#         arrival_time=datetime.fromisoformat(flight_data["arrival_time"]),
#         cost=flight_data["cost"],
#         aircraft=aircraft,
#     )

# # Run the script
# import_flight_data()
