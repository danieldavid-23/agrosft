from django import forms
from ..models import Cultivo

class CultivoForm(forms.ModelForm):
    class Meta:
        model = Cultivo
        fields = ['nombre', 'descripcion', 'area_hectareas', 'fecha_siembra', 'estado']