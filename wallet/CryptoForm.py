from django import forms
from .models import Crypto

class CryptoForm(forms.ModelForm):
    class Meta:
        model = Crypto
        fields = ['name', 'price', 'quantity']
