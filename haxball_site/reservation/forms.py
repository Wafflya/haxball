from .models import ReservationEntry
from django import forms


class ReservationEntryForm(forms.ModelForm):
    class Meta:
        model = ReservationEntry
        fields = ('author', 'match', 'time_date',)
