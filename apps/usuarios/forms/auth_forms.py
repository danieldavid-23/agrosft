from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from apps.usuarios.models.profile_model import Tblusuarios
from django.contrib.auth.hashers import make_password


class CustomUserCreationForm(UserCreationForm):
    correo = forms.EmailField(required=True, label='Correo Electrónico')
    nombres = forms.CharField(max_length=255, required=True, label='Nombres')  # Ajustado al tamaño real
    apellidos = forms.CharField(max_length=255, required=True, label='Apellidos')
    telefono = forms.CharField(max_length=20, required=False, label='Teléfono')

    class Meta:
        model = Tblusuarios
        fields = ("correo", "nombres", "apellidos", "telefono", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.correo = self.cleaned_data["correo"].lower().strip()
        user.nombres = self.cleaned_data["nombres"]
        user.apellidos = self.cleaned_data["apellidos"]
        user.telefono = self.cleaned_data["telefono"]
        
        if commit:
            user.save()
        return user


class RegistroTblusuariosForm(forms.Form):  # Cambiar a forms.Form para manejar manualmente los campos
    """Formulario para registrar usuarios en la tabla tblusuarios"""
    nombres = forms.CharField(max_length=255, required=True, label='Nombres', widget=forms.TextInput(attrs={'class': 'form-control'}))
    apellidos = forms.CharField(max_length=255, required=True, label='Apellidos', widget=forms.TextInput(attrs={'class': 'form-control'}))
    telefono = forms.CharField(max_length=20, required=True, label='Teléfono', widget=forms.TextInput(attrs={'class': 'form-control'}))
    correo = forms.EmailField(required=True, label='Correo Electrónico', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Confirmar Contraseña', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean(self):
        """Validación general del formulario"""
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        
        # Validar que las contraseñas coincidan
        if password1 and password2:
            if password1 != password2:
                self.add_error('password2', "Las contraseñas no coinciden. Por favor, verifica que ambas sean iguales.")
        
        # Validar longitud mínima de la contraseña
        if password1 and len(password1) < 8:
            self.add_error('password1', "La contraseña debe tener al menos 8 caracteres.")
        
        return cleaned_data

    def clean_password2(self):
        """Validación adicional de password2"""
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        
        if password1 and password2 and password1 == password2:
            # Si coinciden, retornamos password2
            return password2
        return password2

    def clean_correo(self):
        correo = self.cleaned_data.get('correo')
        if correo:
            correo = correo.lower().strip()
            if Tblusuarios.objects.filter(correo=correo).exists():
                raise forms.ValidationError('Este correo electrónico ya está registrado.')
        return correo

    def save(self, commit=True):
        user = Tblusuarios(
            correo=self.cleaned_data['correo'].lower().strip(),
            nombres=self.cleaned_data['nombres'],
            apellidos=self.cleaned_data['apellidos'],
            contraseña=make_password(self.cleaned_data['password1']),
            is_active=True,
        )
        if 'telefono' in self.cleaned_data and self.cleaned_data['telefono']:
            user.telefono = self.cleaned_data['telefono']

        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    username = forms.CharField(label='Correo electrónico', max_length=255)  # Ajustado al tamaño real
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        # Ensure password doesn't consist only of spaces.
        password = self.data.get('password', '')
        if password and not password.strip():
            self.add_error('password', "La contraseña no puede estar formada solo por espacios.")
        return cleaned_data


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Tblusuarios  # Changed to use the custom user model
        fields = ['nombres', 'apellidos', 'telefono', 'correo']  # Removidos campos que no existen en la tabla real
        widgets = {
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class TblusuariosForm(forms.ModelForm):
    class Meta:
        model = Tblusuarios
        fields = ['nombres', 'apellidos', 'telefono', 'correo']
        widgets = {
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class PerfilForm(forms.ModelForm):
    """Formulario para editar perfil de usuario"""
    class Meta:
        model = Tblusuarios
        fields = ('nombres', 'apellidos', 'telefono')
        widgets = {
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }


class AdminUsuarioForm(forms.ModelForm):
    """Formulario para que un administrador cree o edite usuarios"""
    password = forms.CharField(
        label='Contraseña', 
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña (Dejar vacío para mantener actual en edición)'}), 
        required=False
    )

    class Meta:
        model = Tblusuarios
        fields = ('nombres', 'apellidos', 'telefono', 'correo', 'is_active', 'is_staff', 'is_superuser')
        widgets = {
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_superuser': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_correo(self):
        correo = self.cleaned_data.get('correo')
        if correo:
            qs = Tblusuarios.objects.filter(correo=correo)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('Este correo electrónico ya está registrado.')
        return correo

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        # Si es creación, la contraseña es obligatoria
        if not self.instance.pk and not password:
            self.add_error('password', 'La contraseña es obligatoria al crear un nuevo usuario.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


# Alias para mantener compatibilidad con el controller
RegistroForm = RegistroTblusuariosForm