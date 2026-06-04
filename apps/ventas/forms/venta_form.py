from django import forms
from ..models import Venta

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['cliente_id', 'total', 'vendedor_id']
        widgets = {
            'cliente_id': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'ID del cliente'}),
            'total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'vendedor_id': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'ID del vendedor'}),
        }

class CheckoutVentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['total']
        widgets = {
            'total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }