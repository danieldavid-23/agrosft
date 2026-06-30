from django.urls import reverse
from django.conf import settings
from django.contrib.messages import get_messages


def layout_data(request):
    data = {
        'urls': {},
        'user': None,
        'is_authenticated': False,
        'cart_count': 0,
        'messages': [],
    }

    urls = data['urls']
    urls['logo'] = f"{settings.STATIC_URL}img/agrosft_o.svg"
    urls['home'] = reverse('home')

    urls['login'] = reverse('usuarios:login')
    urls['registro'] = reverse('usuarios:registro')
    urls['logout'] = reverse('usuarios:logout')
    urls['terminos'] = reverse('usuarios:terminos')

    urls['marketplace'] = reverse('inventario:marketplace')
    urls['mi_inventario'] = reverse('inventario:listar')

    urls['ventas'] = reverse('ventas:venta_list')
    urls['solicitudes'] = reverse('ventas:solicitud_list')
    urls['mis_compras'] = reverse('ventas:compra_list')
    urls['carrito'] = reverse('ventas:carrito_detalle')

    urls['clientes'] = reverse('clientes:cliente_list')

    urls['facturacion_historial'] = reverse('facturacion:historial_facturas')
    urls['perfil'] = reverse('usuarios:perfil')
    urls['historial'] = reverse('usuarios:historial')
    urls['cambiar_password'] = reverse('usuarios:cambiar_password')

    urls['admin_usuarios'] = reverse('usuarios:admin_usuarios_list')
    urls['admin_moderacion'] = reverse('usuarios:admin_moderacion')
    urls['admin_categorias'] = reverse('usuarios:admin_categorias_list')
    urls['admin_auditoria'] = reverse('usuarios:admin_audit_logs')
    urls['admin_estadisticas'] = reverse('usuarios:admin_estadisticas')
    urls['admin_panel'] = reverse('admin:index')

    if request.user.is_authenticated:
        user = request.user
        user_data = {
            'id': user.id_users,
            'correo': user.correo,
            'nombre_corto': user.get_short_name(),
            'nombre_completo': user.get_full_name(),
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
        }
        try:
            profile = user.profile
            if profile and profile.imagen_perfil:
                user_data['imagen_perfil_url'] = profile.imagen_perfil.url
        except Exception:
            pass
        data['user'] = user_data
        data['is_authenticated'] = True

    try:
        carrito = request.session.get('carrito', [])
        data['cart_count'] = len(carrito)
    except Exception:
        pass

    storage = get_messages(request)
    if storage:
        for message in storage:
            data['messages'].append({
                'tags': message.tags,
                'text': str(message.message),
            })

    return {'layout_data': data}
