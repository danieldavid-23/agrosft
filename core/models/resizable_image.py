from django.db.models import ImageField
from django.db.models.fields.files import ImageFieldFile

from core.utils.helpers import resize_uploaded_image


class ResizableImageFieldFile(ImageFieldFile):
    """
    ImageFieldFile que redimensiona la imagen antes de escribirla en el storage.

    Intercepta `FieldFile.save()` (llamada por `FileField.pre_save()` durante el
    guardado del modelo) y aplica `resize_uploaded_image()` al contenido, de modo
    que el archivo original de alta resolución nunca llega a persistirse en disco.
    """

    def save(self, name, content, save=True):
        resized = resize_uploaded_image(content, self.field.name)
        if resized is not None:
            content = resized
        super().save(name, content, save=save)


class ResizableImageField(ImageField):
    """
    ImageField con redimensionado automático en el punto de persistencia
    (antes de escribir en storage). Usar en imágenes de productos y perfiles.
    """

    attr_class = ResizableImageFieldFile