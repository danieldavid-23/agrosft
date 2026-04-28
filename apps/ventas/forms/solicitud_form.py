from django import forms
from django.forms import inlineformset_factory
from apps.ventas.models.solicitud import SolicitudCompra, DetalleSolicitudCompra

class SolicitudCompraForm(forms.ModelForm):
    class Meta:
        model = SolicitudCompra
        fields = ['cliente', 'observaciones']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observaciones adicionales'}),
        }

class DetalleSolicitudCompraForm(forms.ModelForm):
    class Meta:
        model = DetalleSolicitudCompra
        fields = ['producto', 'cantidad']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select producto-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control cantidad-input', 'min': '1'}),
        }

# Formset para poder agregar múltiples detalles en una sola solicitud
DetalleSolicitudFormSet = inlineformset_factory(
    SolicitudCompra,
    DetalleSolicitudCompra,
    form=DetalleSolicitudCompraForm,
    extra=1,
    can_delete=True
)
