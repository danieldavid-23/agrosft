from django.core.management.base import BaseCommand
from apps.usuarios.models import Termino

class Command(BaseCommand):
    help = 'Crea términos y condiciones iniciales'
    
    def handle(self, *args, **kwargs):
        # Verificar si ya existen términos
        if Termino.objects.exists():
            self.stdout.write(self.style.WARNING('Ya existen términos en la base de datos.'))
            return
        
        # Crear nuevo término
        termino = Termino.objects.create(
            version="1.0.0",
            titulo="Términos y Condiciones de Uso - AgroSFT",
            contenido="""BIENVENIDO A AGROSFT

Al acceder y utilizar este sistema de gestión agrícola, aceptas los siguientes términos y condiciones:

1. ACEPTACIÓN DE TÉRMINOS
   El uso del sistema AgroSFT implica la aceptación plena y sin reservas de todas las disposiciones establecidas en estos términos.

2. REGISTRO DE USUARIO
   - La información proporcionada durante el registro debe ser veraz y completa.
   - Eres responsable de mantener la confidencialidad de tus credenciales.
   - Notificarás inmediatamente cualquier uso no autorizado de tu cuenta.

3. USO DEL SISTEMA
   - El sistema está diseñado para gestión agrícola y fines relacionados.
   - No utilizarás el sistema para actividades ilícitas o no autorizadas.
   - Respetarás los derechos de propiedad intelectual.

4. PRIVACIDAD DE DATOS
   - La información ingresada será tratada conforme a las leyes de protección de datos.
   - AgroSFT implementa medidas de seguridad para proteger tu información.
   - No compartiremos tus datos sin tu consentimiento.

5. RESPONSABILIDAD
   - Eres responsable de la precisión de los datos ingresados.
   - AgroSFT no se hace responsable por decisiones basadas en la información del sistema.
   - El sistema se proporciona "tal cual", sin garantías de disponibilidad continua.

6. MODIFICACIONES
   - AgroSFT se reserva el derecho de modificar estos términos.
   - Las modificaciones serán notificadas con anticipación.
   - El uso continuado del sistema implica la aceptación de las modificaciones.

Fecha de entrada en vigencia: 24 de febrero de 2026
Versión 1.0.0"""
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Términos iniciales creados exitosamente: v{termino.version}')
        )