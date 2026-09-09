"""
Controlador para la gestión de usuarios en el Panel de Administración.
"""
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Q
from apps.usuarios.models.profile_model import Tblusuarios, UserProfile
from .admin_controller import admin_required, registrar_auditoria


@admin_required
def lista_usuarios(request):
    """Listado de usuarios con búsqueda y filtros."""
    q = request.GET.get('q', '').strip()
    filtro = request.GET.get('filtro', 'todos')

    usuarios = Tblusuarios.objects.all().order_by('-fecha_creacion')

    if q:
        usuarios = usuarios.filter(
            Q(nombres__icontains=q) | Q(apellidos__icontains=q) | Q(correo__icontains=q)
        )

    if filtro == 'activos':
        usuarios = usuarios.filter(is_active=True)
    elif filtro == 'inactivos':
        usuarios = usuarios.filter(is_active=False)
    elif filtro == 'staff':
        usuarios = usuarios.filter(is_staff=True)
    elif filtro == 'admin':
        usuarios = usuarios.filter(is_superuser=True)

    contexto = {
        'titulo': 'Usuarios',
        'usuarios': usuarios,
        'q': q,
        'filtro': filtro,
        'seccion_activa': 'usuarios',
    }
    return render(request, 'administracion/usuarios/lista.html', contexto)


@admin_required
def detalle_usuario(request, pk):
    """Detalle de un usuario con sus métricas."""
    usuario = get_object_or_404(Tblusuarios, id_users=pk)
    try:
        perfil = UserProfile.objects.filter(id_usuario=pk).first()
    except Exception:
        perfil = None

    publicaciones = usuario.productousuario_set.count()
    movimientos = usuario.movimientos.count()

    contexto = {
        'titulo': f'Usuario: {usuario.get_full_name()}',
        'usuario': usuario,
        'perfil': perfil,
        'publicaciones': publicaciones,
        'movimientos': movimientos,
        'seccion_activa': 'usuarios',
    }
    return render(request, 'administracion/usuarios/detalle.html', contexto)


@admin_required
def cambiar_estado_usuario(request, pk):
    """Activa o desactiva una cuenta de usuario."""
    usuario = get_object_or_404(Tblusuarios, id_users=pk)
    if request.method == 'POST':
        if usuario == request.user:
            messages.error(request, 'No puedes desactivar tu propia cuenta.')
        else:
            usuario.is_active = not usuario.is_active
            usuario.save(update_fields=['is_active'])
            estado = 'activado' if usuario.is_active else 'desactivado'
            registrar_auditoria(
                request.user, f'Cambiar estado usuario',
                objetivo=f'{usuario.get_full_name()} ({usuario.correo})',
                detalles=f'Cuenta {estado}', request=request,
            )
            messages.success(request, f'La cuenta de {usuario.get_full_name()} fue {estado}.')
    return redirect('administracion:usuario_detalle', pk=pk)