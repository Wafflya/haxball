from django import forms

from .models import FreeAgent


class FreeAgentForm(forms.ModelForm):
    class Meta:
        model = FreeAgent
        fields = ('position_main', 'description')