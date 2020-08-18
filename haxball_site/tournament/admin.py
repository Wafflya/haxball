from django.contrib import admin

# Register your models here.
from .models import FreeAgent, PlayerPositions


@admin.register(FreeAgent)
class FreeAgentAdmin(admin.ModelAdmin):
    #def player_pos(self, instance):
    #    return instance.player_positions
    list_display = ('id', 'player','description',)

@admin.register(PlayerPositions)
class PlayerPositionsAdmin(admin.ModelAdmin):
    list_display = ('position',)
