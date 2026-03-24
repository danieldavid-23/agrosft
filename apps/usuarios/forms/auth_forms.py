from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re
from ..models import UserProfile

class RegistroForm(UserCreationForm):
    """Formulario para registro de nuevos usuarios"""
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email', 'oninput': "this.value = this.value.replace(/\\s/g, '')"}))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre', 'oninput': "this.value = this.value.replace(/^\\s+/, '')"}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido', 'oninput': "this.value = this.value.replace(/^\\s+/, '')"}))
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clases CSS a los campos
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nombre de usuario', 'oninput': "this.value = this.value.replace(/\\s/g, '')"})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Contraseña'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirmar contraseña'})
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name', '')
        if not first_name or not first_name.strip():
            raise ValidationError("Este campo no puede estar vacío ni contener solo espacios.")
        return first_name.strip()

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name', '')
        if not last_name or not last_name.strip():
            raise ValidationError("Este campo no puede estar vacío ni contener solo espacios.")
        return last_name.strip()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Este email ya está registrado")
        if email and not email.strip():
            raise ValidationError("El email no puede contener solo espacios.")
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username or not username.strip():
            raise ValidationError("El usuario no puede estar vacío ni contener solo espacios.")
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValidationError("El usuario solo puede contener letras, números y guión bajo (sin espacios)")
        return username
        
    def clean(self):
        cleaned_data = super().clean()
        # Ensure passwords don't consist only of spaces.
        p1 = self.data.get('password1', '')
        p2 = self.data.get('password2', '')
        if p1 and not p1.strip():
            self.add_error('password1', "La contraseña no puede estar formada solo por espacios.")
        if p2 and not p2.strip():
            self.add_error('password2', "La contraseña no puede estar formada solo por espacios.")
        return cleaned_data


class LoginForm(forms.Form):
    """Formulario para inicio de sesión"""
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario o Email', 'oninput': "this.value = this.value.replace(/\\s/g, '')"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}))
    
    def clean(self):
        cleaned_data = super().clean()
        username = self.data.get('username', '')
        password = self.data.get('password', '')
        
        # Validación de espacios vacíos
        if not username or not username.strip():
            self.add_error('username', "El usuario no puede estar vacío ni contener solo espacios.")
        if not password or not password.strip():
            self.add_error('password', "La contraseña no puede estar vacía ni contener solo espacios.")
            
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        
        # Si hay errores en 'username' o 'password', detenemos la validación aquí
        if self.errors:
            return cleaned_data
        
        if username and password:
            # Verificar si es email o username
            from django.contrib.auth import authenticate
            user = authenticate(username=username, password=password)
            if not user:
                # Intentar con email
                try:
                    user_obj = User.objects.get(email=username)
                    user = authenticate(username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass
            
            if not user:
                raise ValidationError("Usuario o contraseña incorrectos")
            
            if not user.is_active:
                raise ValidationError("Esta cuenta está desactivada")
            
            self.user = user
        
        return cleaned_data


class PerfilForm(UserChangeForm):
    """Formulario para editar perfil de usuario"""
    password = None  # Ocultar campo de contraseña
    profile_picture = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})
        
        # Hacer username de solo lectura
        self.fields['username'].disabled = True
        
        # Inicializar profile_picture si existe
        if self.instance and hasattr(self.instance, 'userprofile'):
            self.fields['profile_picture'].initial = self.instance.userprofile.profile_picture
    
    def save(self, commit=True):
        user = super().save(commit=commit)
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.profile_picture = profile_picture
            if commit:
                profile.save()
        return user
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        
        # Verificar si el email ya existe (excepto para este usuario)
        if User.objects.exclude(username=username).filter(email=email).exists():
            raise ValidationError("Este email ya está en uso")
        return email