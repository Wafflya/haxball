from django.contrib import admin

from .models import ReservationHost, ReservationEntry, Replay

# Register your models here.

admin.site.register(ReservationHost)
# admin.site.register(ReservationEntry)
admin.site.register(Replay)


@admin.register(ReservationEntry)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("author", "match", "time_date", "host", "created")
    raw_id_fields = ('match',)
    list_filter = ('host', 'author')
