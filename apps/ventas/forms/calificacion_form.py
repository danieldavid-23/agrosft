from django import forms
from apps.ventas.models.movimiento import ProductoUsuarioMovimiento


class CalificacionForm(forms.ModelForm):
    """
    Formulario para calificar una transacción de compra/venta
    """
    class Meta:
        model = ProductoUsuarioMovimiento
        fields = ['calificacion']
        widgets = {
            'calificacion': forms.NumberInput(
                attrs={
                    'min': '1.0',
                    'max': '5.0',
                    'step': '0.5',
                    'class': 'form-control',
                    'placeholder': 'Calificación (1.0 - 5.0)'
                }
            )
        }
        labels = {
            'calificacion': 'Calificación'
        }
        help_texts = {
            'calificacion': 'Califica esta transacción de 1.0 a 5.0 (pasos de 0.5)'
        }

    def clean_calificacion(self):
        calificacion = self.cleaned_data.get('calificacion')
        if calificacion is not None:
            if calificacion < 1.0 or calificacion > 5.0:
                raise forms.ValidationError('La calificación debe estar entre 1.0 y 5.0')
            # Validar que sea múltiplo de 0.5
            if (calificacion * 2) % 1 != 0:
                raise forms.ValidationError('La calificación debe ser múltiplo de 0.5 (ej: 1.0, 1.5, 2.0, etc.)')
        return calificacion
