from django import forms
from apps.ventas.models.resena import Resena


class ResenaForm(forms.ModelForm):
    """
    Formulario para dejar una reseña (calificación en estrellas + comentario)
    sobre un producto comprado.
    """
    calificacion = forms.IntegerField(
        min_value=1,
        max_value=5,
        required=True,
        help_text='Califica de 1 a 5 estrellas'
    )

    class Meta:
        model = Resena
        fields = ['calificacion', 'comentario']
        widgets = {
            'calificacion': forms.HiddenInput(attrs={'id': 'rating-value'}),
            'comentario': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Cuéntanos tu experiencia con este producto...',
                    'maxlength': 1000,
                }
            ),
        }
        labels = {
            'calificacion': 'Calificación',
            'comentario': 'Comentario',
        }

    def clean_comentario(self):
        comentario = self.cleaned_data.get('comentario', '')
        return comentario.strip() if comentario else None