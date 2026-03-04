from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from core.controllers.base_controller import BaseController
from apps.usuarios.services.terminos_service import TerminosService

class TerminosView(BaseController, View):  # ← CAMBIA EL ORDEN: BaseController primero
    """Vista para mostrar los términos y condiciones"""
    
    def get(self, request):
        terminos = TerminosService.obtener_terminos_activos()
        
        ya_acepto = False
        if request.user.is_authenticated:
            ya_acepto = not TerminosService.usuario_debe_aceptar_terminos(request.user)
        
        context = {
            'terminos': terminos,
            'ya_acepto': ya_acepto,
            'titulo': terminos.titulo if terminos else "Términos y Condiciones",
            'contenido': terminos.contenido if terminos else "",
            'version': terminos.version if terminos else "1.0.0",
            'fecha': terminos.fecha_publicacion if terminos else None
        }
        
        return render(request, 'usuarios/terminos.html', context)


class AceptarTerminosView(LoginRequiredMixin, BaseController, View):  # ← BaseController antes que View
    """Vista para procesar la aceptación de términos"""
    login_url = '/admin/login/'
    
    def get(self, request):
        terminos = TerminosService.obtener_terminos_activos()
        
        if not terminos:
            messages.error(request, "No hay términos para aceptar.")
            return redirect('home')
        
        if not TerminosService.usuario_debe_aceptar_terminos(request.user):
            messages.info(request, "Ya has aceptado los términos actuales.")
            return redirect('home')
        
        context = {
            'terminos': terminos,
            'titulo': terminos.titulo,
            'version': terminos.version
        }
        
        return render(request, 'usuarios/aceptar_terminos.html', context)
    
    def post(self, request):
        exito, mensaje = TerminosService.aceptar_terminos(request.user, request)
        
        if exito:
            messages.success(request, mensaje)
            return redirect('home')
        else:
            messages.error(request, mensaje)
            return redirect('usuarios:terminos')


class HistorialTerminosView(LoginRequiredMixin, BaseController, View):  # ← BaseController antes que View
    """Vista para mostrar el historial de aceptaciones"""
    login_url = '/admin/login/'
    
    def get(self, request):
        historial = TerminosService.obtener_historial_usuario(request.user)
        
        context = {
            'historial': historial,
            'titulo': 'Mi historial de aceptaciones'
        }
        
        return render(request, 'usuarios/historial_terminos.html', context)