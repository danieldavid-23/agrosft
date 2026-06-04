from django import forms
from django.forms import inlineformset_factory
from apps.ventas.models.solicitud import SolicitudCompra, DetalleSolicitudCompra

class SolicitudCompraForm(forms.ModelForm):
    class Meta:
        model = SolicitudCompra
        fields = ['cliente_id', 'observaciones']
        widgets = {
            'cliente_id': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'ID del cliente'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observaciones adicionales'}),
        }

class CheckoutSolicitudForm(forms.ModelForm):
    class Meta:
        model = SolicitudCompra
        fields = ['observaciones']
        widgets = {
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observaciones adicionales'}),
        }

class DetalleSolicitudCompraForm(forms.ModelForm):
    class Meta:
        model = DetalleSolicitudCompra
        fields = ['producto_id', 'cantidad']  # Cambiado de 'producto' a 'producto_id'
        widgets = {
            'producto_id': forms.NumberInput(attrs={'class': 'form-control producto-id-input', 'placeholder': 'ID del producto'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control cantidad-input', 'min': '1'}),
        }

# Formset para poder agregar múltiples detalles en una sola solicitud
DetalleSolicitudFormSet = inlineformset_factory(
    SolicitudCompra,
    DetalleSolicitudCompra,
    form=DetalleSolicitudCompraForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True
)