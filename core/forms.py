# core/forms.py

from django import forms
from .models import Usuario, Cliente
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

# core/forms.py

from django import forms
from .models import Usuario, Cliente
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth.hashers import make_password
# core/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Cliente

class RegistroForm(UserCreationForm):
    direccion = forms.CharField(max_length=255)
    telefono = forms.CharField(max_length=20)

    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.rol = 'cliente'
        if commit:
            user.save()
            Cliente.objects.create(
                usuario=user,
                direccion=self.cleaned_data['direccion'],
                telefono=self.cleaned_data['telefono']
            )
        return user



class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Correo electrónico'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'}))
