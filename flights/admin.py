from django.contrib import admin

from .models import *

# Register your models here.
admin.site.register(Airport)
admin.site.register(AircraftType)
admin.site.register(Flight)
admin.site.register(AirplaneRental)
admin.site.register(ShoppingCart)
admin.site.register(ShoppingCartFlight)
admin.site.register(ShoppingCartRental)
