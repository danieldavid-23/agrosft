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

    def _url(name, fallback='#'):
        try:
            return reverse(name)
        except Exception:
            return fallback

    urls['home'] = _url('home')

    urls['login'] = _url('usuarios:login')
    urls['registro'] = _url('usuarios:registro')
    urls['logout'] = _url('usuarios:logout')
    urls['terminos'] = _url('usuarios:terminos')

    urls['marketplace'] = _url('inventario:marketplace')
    urls['mi_inventario'] = _url('inventario:listar')

    urls['ventas'] = _url('ventas:venta_list')
    urls['solicitudes'] = _url('ventas:solicitud_list')
    urls['mis_compras'] = _url('ventas:compra_list')
    urls['carrito'] = _url('ventas:carrito_detalle')

    urls['clientes'] = _url('clientes:cliente_list')

    urls['facturacion_historial'] = _url('facturacion:historial_facturas')
    urls['perfil'] = _url('usuarios:perfil')
    urls['historial'] = _url('usuarios:historial')
    urls['cambiar_password'] = _url('usuarios:cambiar_password')

    urls['admin_usuarios'] = _url('usuarios:admin_usuarios_list')
    urls['admin_moderacion'] = _url('usuarios:admin_moderacion')
    urls['admin_categorias'] = _url('usuarios:admin_categorias_list')
    urls['admin_auditoria'] = _url('usuarios:admin_audit_logs')
    urls['admin_estadisticas'] = _url('usuarios:admin_estadisticas')
    urls['admin_panel'] = _url('admin:index')

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
