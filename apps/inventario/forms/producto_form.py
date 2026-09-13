from django import forms
from django.core.validators import FileExtensionValidator
from core.utils.helpers import validate_image_size
from apps.inventario.models import Producto, Categoria, UnidadMedida, ProductoUsuario


class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        attrs = kwargs.get("widget", {}).attrs if hasattr(kwargs.get("widget", None), "attrs") else {}
        attrs.update({
            'class': 'form-control',
            'id': 'id_imagen',
            'accept': 'image/jpeg,image/png,image/webp,image/jpg',
            'multiple': True,
        })
        kwargs.setdefault("widget", MultipleFileInput(attrs=attrs))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            if not data and self.required:
                raise forms.ValidationError(self.error_messages['required'], code='required')
            result = [single_file_clean(d, initial) for d in data if d]
        else:
            result = single_file_clean(data, initial)
        return result


class ProductoForm(forms.Form):
    # Campos para el catálogo maestro de productos (tblproductos)
    nombre = forms.CharField(
        max_length=45,  # Coincide con BD VARCHAR(45)
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del producto'})
    )
    descripcion = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción del producto'}),
        required=False
    )
    id_categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.filter(activo=True),
        empty_label="Seleccione una categoría",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    unidad_medida = forms.ModelChoiceField(
        queryset=UnidadMedida.objects.filter(activo=True),
        empty_label="Seleccione una unidad de medida",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    imagen = MultipleFileField(
        required=False,
        error_messages={'required': 'Campo obligatorio'},
        validators=[
            FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp']),
            validate_image_size
        ]
    )
    
    # Campo stock_minimo
    stock_minimo = forms.IntegerField(
        min_value=0,
        required=False,
        error_messages={
            'min_value': 'El stock mínimo para alerta no puede ser un número negativo.',
            'invalid': 'Ingrese un número entero válido para la alerta de stock.'
        },
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Stock mínimo para alerta', 'min': '0'})
    )
    
    # Campos para la relación específica usuario-producto (tblproductos_has_tblusuarios)
    cantidad = forms.IntegerField(
        min_value=1,
        error_messages={
            'required': 'El número de unidades es obligatorio.',
            'min_value': 'No se permiten números negativos ni cero. Ingrese solo números positivos.',
            'invalid': 'Ingrese un número entero positivo válido para las unidades.'
        },
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Cantidad disponible (mínimo 1)',
            'step': '1',
            'min': '1'
        })
    )
    precio = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Precio unitario'})
    )

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if not nombre:
            raise forms.ValidationError('El nombre del producto es obligatorio.')
        if len(nombre) < 3:
            raise forms.ValidationError('El nombre del producto debe tener al menos 3 caracteres.')
        if len(nombre) > 45:
            raise forms.ValidationError('El nombre del producto no puede superar los 45 caracteres.')
        return nombre

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad is not None and cantidad <= 0:
            raise forms.ValidationError('No se permiten números negativos ni cero. Ingrese solo números positivos.')
        return cantidad

    def __init__(self, *args, **kwargs):
        initial_data = kwargs.pop('initial', {})
        requerir_imagen = kwargs.pop('requerir_imagen', False)
        super().__init__(*args, **kwargs)
        if requerir_imagen:
            self.fields['imagen'].required = True
        
        if initial_data:
            if 'nombre' in initial_data and hasattr(initial_data['nombre'], 'pk'):
                producto = initial_data['nombre']
                self.fields['nombre'].initial = producto.nombre
                self.fields['descripcion'].initial = producto.descripcion
                self.fields['id_categoria'].initial = producto.id_categoria
                self.fields['unidad_medida'].initial = producto.unidad_medida
                self.fields['stock_minimo'].initial = producto.stock_minimo
                if hasattr(producto, 'imagen'):
                    self.fields['imagen'].initial = producto.imagen
            elif 'nombre' in initial_data:
                self.fields['nombre'].initial = initial_data.get('nombre', '')
                self.fields['descripcion'].initial = initial_data.get('descripcion', '')
                self.fields['id_categoria'].initial = initial_data.get('id_categoria')
                self.fields['unidad_medida'].initial = initial_data.get('unidad_medida')
                self.fields['stock_minimo'].initial = initial_data.get('stock_minimo', 5)
                self.fields['imagen'].initial = initial_data.get('imagen')
            
            cantidad_initial = initial_data.get('cantidad', 0)
            self.fields['cantidad'].initial = int(cantidad_initial) if cantidad_initial is not None else 0
            self.fields['precio'].initial = initial_data.get('precio', 0)


class ProductoBusquedaForm(forms.Form):
    nombre = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del producto'})
    )
    categoria_id = forms.ModelChoiceField(
        queryset=Categoria.objects.all(),
        required=False,
        empty_label="Todas las categorías",
        widget=forms.Select(attrs={'class': 'form-control'})
    )