from django import forms
from apps.inventario.models import Producto, Categoria, ProductoUsuario, Estado


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
    
    # Campo stock_minimo (solo administradores pueden editar)
    stock_minimo = forms.IntegerField(
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Stock mínimo para alerta'})
    )
    
    # Campos para la relación específica usuario-producto (tblproductos_has_tblusuarios)
    cantidad = forms.IntegerField(  # IntegerField: solo permite números enteros
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Cantidad disponible',
            'step': '1'  # Solo permite incrementos de 1 (enteros)
        })
    )
    precio = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Precio unitario'})
    )
    id_estado = forms.ModelChoiceField(
        queryset=Estado.objects.all(),
        empty_label="Seleccione un estado",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False  # Solo para ediciones por parte del admin
    )

    def __init__(self, *args, **kwargs):
        # Permitir inicializar con datos de ProductoUsuario
        initial_data = kwargs.pop('initial', {})
        super().__init__(*args, **kwargs)
        
        # Si se proporcionan datos iniciales de un ProductoUsuario existente
        if initial_data:
            # Mapear los campos relacionados
            if 'nombre' in initial_data and hasattr(initial_data['nombre'], 'pk'):
                # Si se pasó un objeto Producto, extraer sus datos
                producto = initial_data['nombre']
                self.fields['nombre'].initial = producto.nombre
                self.fields['descripcion'].initial = producto.descripcion
                self.fields['id_categoria'].initial = producto.id_categoria
                self.fields['stock_minimo'].initial = producto.stock_minimo
            elif 'nombre' in initial_data:
                # Si se pasaron valores directamente
                self.fields['nombre'].initial = initial_data.get('nombre', '')
                self.fields['descripcion'].initial = initial_data.get('descripcion', '')
                self.fields['id_categoria'].initial = initial_data.get('id_categoria')
                self.fields['stock_minimo'].initial = initial_data.get('stock_minimo', 5)
            
            # Datos específicos del ProductoUsuario
            self.fields['cantidad'].initial = initial_data.get('cantidad', 0)
            self.fields['precio'].initial = initial_data.get('precio', 0)
            self.fields['id_estado'].initial = initial_data.get('id_estado')


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
    estado = forms.ModelChoiceField(
        queryset=Estado.objects.all(),
        required=False,
        empty_label="Todos los estados",
        widget=forms.Select(attrs={'class': 'form-control'})
    )