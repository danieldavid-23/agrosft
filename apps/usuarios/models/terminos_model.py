from django.db import models
from apps.usuarios.models.profile_model import Tblusuarios
from core.models.base_model import BaseModel

class Termino:
    """Clase simulada para términos y condiciones sin base de datos"""
    
    def __init__(self, version="1.0", titulo="Términos y Condiciones", contenido="", fecha_publicacion=None, es_activo=True):
        self.version = version
        self.titulo = titulo
        self.contenido = contenido
        self.fecha_publicacion = fecha_publicacion or "2026-01-01 00:00:00"
        self.es_activo = es_activo
    
    def __str__(self):
        return f"Versión {self.version}"


class AceptacionTermino:
    """Clase simulada para aceptación de términos sin base de datos"""
    
    def __init__(self, usuario, termino, fecha_aceptacion=None, ip_aceptacion=None):
        self.usuario = usuario
        self.termino = termino
        self.fecha_aceptacion = fecha_aceptacion or "2026-01-01 00:00:00"
        self.ip_aceptacion = ip_aceptacion


class TerminoManager:
    """Simulación de un manager para manejar términos estáticos"""
    
    @staticmethod
    def get_terminos_por_defecto():
        """Devuelve los términos y condiciones por defecto"""
        contenido = """TÉRMINOS Y CONDICIONES GENERALES DE USO DE AGROSFT

Última actualización: 10 de junio de 2026

Bienvenido a AgroSFT. Los presentes Términos y Condiciones de Uso (en adelante, los "Términos") constituyen un acuerdo legal vinculante entre el usuario (en adelante, el "Usuario", "Productor" o "Comprador") y AgroSFT (en adelante, la "Plataforma"). Le solicitamos leer detenidamente este documento antes de utilizar nuestros servicios.

1. OBJETO Y ALCANCE DE LA PLATAFORMA
AgroSFT es una plataforma tecnológica digital diseñada para facilitar el encuentro, la negociación y la intermediación comercial directa entre productores del sector agropecuario y compradores o distribuidores. El objeto principal de la Plataforma es promover un canal eficiente de comercio justo para productos frescos y locales.

2. ACEPTACIÓN EXPRESA DE LOS TÉRMINOS
La creación de una cuenta y el acceso o uso de los servicios de AgroSFT implican la aceptación expresa y sin reservas de todos y cada uno de los presentes Términos. Si usted no está de acuerdo con las condiciones establecidas en este documento, deberá abstenerse inmediatamente de registrarse, acceder o utilizar la Plataforma.

3. CAPACIDAD LEGAL Y REGISTRO DE CUENTA
Para ser usuario de la Plataforma se requiere:
- Ser persona natural con plena capacidad legal para contratar (mínimo 18 años de edad) o actuar en representación de una persona jurídica debidamente constituida.
- Suministrar información exacta, verídica, actual y comprobable durante el proceso de registro.
- Resguardar la confidencialidad de sus credenciales de acceso, siendo el Usuario el único responsable por todas las actividades realizadas bajo su cuenta.

4. NATURALEZA DE LOS SERVICIOS Y EXCLUSIÓN DE RELACIÓN CONTRACTUAL
- AgroSFT actúa exclusivamente como un facilitador de conectividad digital.
- AgroSFT no es propietaria, productora, poseedora, ni distribuidora de los productos agrícolas publicados.
- AgroSFT no interviene de manera directa ni garantiza la ejecución de las transacciones comerciales, pagos, envíos ni la calidad o el estado de los productos entregados. Los acuerdos y contratos de compraventa se celebran de manera exclusiva e independiente entre el Productor y el Comprador.

5. OBLIGACIONES Y COMPROMISOS DEL USUARIO
- Información del Producto: Los Productores se comprometen a describir con veracidad y precisión el estado, origen, variedad, cantidad y precio de los bienes ofertados.
- Precios Transparentes: Los precios ofertados deben ser claros e incluir todos los impuestos de ley aplicables si a ello hubiere lugar.
- Uso Correcto: El Usuario se obliga a hacer uso de la Plataforma bajo principios de buena fe y respeto de las leyes aplicables, absteniéndose de realizar conductas fraudulentas o engañosas.

6. POLÍTICA DE PROTECCIÓN DE DATOS PERSONALES (HABEAS DATA)
En cumplimiento de la Ley 1581 de 2012 y demás normas concordantes sobre protección de datos personales en Colombia, AgroSFT se compromete a garantizar la seguridad, confidencialidad y el tratamiento adecuado de los datos proporcionados por los Usuarios. Al aceptar estos Términos, el Usuario autoriza expresamente el tratamiento de su información personal con fines de optimización del servicio y seguridad de la Plataforma.

7. PROPIEDAD INTELECTUAL Y DERECHOS RESERVADOS
Todo el contenido, diseño, logotipos, marcas, código fuente, algoritmos y desarrollos de software asociados a AgroSFT son propiedad intelectual exclusiva de AgroSFT o de sus licenciantes y están protegidos por las leyes nacionales e internacionales de propiedad industrial y derechos de autor.

8. LIMITACIÓN DE RESPONSABILIDAD
- AgroSFT no será responsable por pérdidas financieras, lucro cesante o daños resultantes de transacciones fallidas, demoras en las entregas de mercancía o discrepancias en la calidad de los productos.
- La Plataforma no garantiza la continuidad ininterrumpida de sus servicios en caso de fallas técnicas externas o mantenimientos preventivos.

9. LEY APLICABLE Y RESOLUCIÓN DE CONTROVERSIAS
Los presentes Términos se regirán e interpretarán de conformidad con las leyes de la República de Colombia. Cualquier diferencia o reclamación derivada de la interpretación o ejecución de este acuerdo se resolverá preferentemente mediante arreglo directo o, en su defecto, ante los tribunales competentes de Colombia.

10. MODIFICACIONES A LAS CONDICIONES
AgroSFT se reserva el derecho a actualizar, complementar o modificar los presentes Términos en cualquier momento. Los cambios se notificarán a través de la Plataforma y requerirán la aceptación del Usuario al iniciar una nueva sesión posterior a la actualización.
"""
        return Termino(
            version="1.1.0",
            titulo="Términos y Condiciones de Uso - AgroSFT",
            contenido=contenido,
            fecha_publicacion="2026-06-10 00:00:00",
            es_activo=True
        )


# Creamos un objeto global para simular el acceso a través del modelo
fake_termino_manager = TerminoManager()