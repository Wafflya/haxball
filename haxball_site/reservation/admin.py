from django.contrib import admin
from .models import ReservationHost,ReservationEntry, Replay
# Register your models here.

admin.site.register(ReservationHost)
admin.site.register(ReservationEntry)
admin.site.register(Replay)