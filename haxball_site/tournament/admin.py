from django.contrib import admin

# Register your models here.
from .models import FreeAgent


@admin.register(FreeAgent)
class FreeAgentAdmin(admin.ModelAdmin):
    #def player_pos(self, instance):
    #    return instance.player_positions
    list_display = ('id', 'player', 'position_main','position_second','description',)

