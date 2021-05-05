from django.contrib import admin
from .models import ReservationHost,ReservationEntry
# Register your models here.

admin.site.register(ReservationHost)
admin.site.register(ReservationEntry)