"""
Middleware para prevenir caché del navegador en páginas autenticadas.
Evita que al cerrar sesión y presionar "atrás" se muestre la página anterior.
"""


class NoCacheMiddleware:
    """
    Agrega headers HTTP para prevenir que el navegador guarde en caché
    las páginas de usuarios autenticados. Así, al presionar "atrás"
    después de cerrar sesión, el navegador hace una petición nueva
    y Django redirige al login.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Solo aplicar a usuarios autenticados
        if hasattr(request, 'user') and request.user.is_authenticated:
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'

        return response
