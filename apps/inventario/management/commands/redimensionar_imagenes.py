from PIL import Image
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand

from apps.inventario.models import Producto, ProductoImagen
from apps.usuarios.models.profile_model import UserProfile
from core.utils.helpers import MAX_IMAGE_DIMENSION, resize_uploaded_image


class Command(BaseCommand):
    help = (
        "Redimensiona en su lugar (sin cambiar rutas en BD) las imágenes ya "
        "almacenadas que superen el límite de {0}x{0} px, reutilizando la misma "
        "lógica de optimización de las nuevas subidas.".format(MAX_IMAGE_DIMENSION)
    )

    def handle(self, *args, **options):
        total_ok = total_skip = total_error = 0
        for modelo, campo, etiqueta in (
            (Producto, 'imagen', 'Producto'),
            (ProductoImagen, 'imagen', 'ProductoImagen'),
            (UserProfile, 'imagen_perfil', 'UserProfile'),
        ):
            ok, skip, error = self._procesar_modelo(modelo, campo, etiqueta)
            total_ok += ok
            total_skip += skip
            total_error += error

        self.stdout.write(self.style.SUCCESS(
            f'\nResumen: {total_ok} optimizada(s), {total_skip} omitida(s) '
            f'(ya cumplen el límite), {total_error} con error.'
        ))

    def _procesar_modelo(self, modelo, campo, etiqueta):
        self.stdout.write(f'\n== {etiqueta}.{campo} ==')
        registros = modelo._default_manager.exclude(**{campo: ''}).exclude(**{campo: None})
        self.stdout.write(f'Registros con imagen: {registros.count()}')

        ok = skip = error = 0
        for obj in registros:
            resultado = self._optimizar(getattr(obj, campo))
            if resultado == 'ok':
                ok += 1
            elif resultado == 'skip':
                skip += 1
            else:
                error += 1

        self.stdout.write(
            f'{etiqueta}: {ok} optimizadas, {skip} omitidas, {error} errores'
        )
        return ok, skip, error

    def _optimizar(self, field):
        if not field.name:
            return 'skip'
        if not default_storage.exists(field.name):
            self.stdout.write(self.style.WARNING(f'  [faltante] {field.name}'))
            return 'error'

        try:
            field.file.close()
        except Exception:
            pass

        opened = default_storage.open(field.name)
        try:
            try:
                with Image.open(opened) as img:
                    excede = img.width > MAX_IMAGE_DIMENSION or img.height > MAX_IMAGE_DIMENSION
            except Exception:
                excede = True
        finally:
            try:
                opened.close()
            except Exception:
                pass

        if not excede:
            return 'skip'

        opened = default_storage.open(field.name)
        try:
            resized = resize_uploaded_image(opened, field.field.name)
        finally:
            try:
                opened.close()
            except Exception:
                pass

        if resized is None:
            self.stdout.write(self.style.WARNING(f'  [no procesable] {field.name}'))
            return 'error'

        default_storage.delete(field.name)
        default_storage.save(field.name, ContentFile(resized.read()))
        self.stdout.write(self.style.SUCCESS(f'  [ok] {field.name}'))
        return 'ok'