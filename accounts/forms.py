from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import accountUser as User

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=254, required=True, help_text='Required')
    last_name = forms.CharField(max_length=254, required=True, help_text='Required')
    email = forms.CharField(max_length=254, required=True, widget=forms.EmailInput())
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name','email', 'password1', 'password2')
