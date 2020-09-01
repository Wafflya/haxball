from django import forms
from colorfield.widgets import ColorWidget

from .models import FreeAgent, Team


class FreeAgentForm(forms.ModelForm):
    class Meta:
        model = FreeAgent
        fields = ('position_main', 'description')


class EditTeamProfileForm(forms.ModelForm):


    class Meta:
        model = Team
        fields = ('color_1', 'color_2', 'short_title',)
        widgets = {
            'color_1': ColorWidget,
            'color_2': ColorWidget,
        }

