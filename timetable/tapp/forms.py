from django import forms
from .models import unit, Availlability

class UnitForm(forms.ModelForm):
    class Meta:
        fields = ('name', 'difficulty')