from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import BaseUserManager
import uuid
from datetime import datetime


class TblusuariosManager(BaseUserManager):
    def normalize_email(self, email):
        return email.lower().strip() if email else email

    def create_user(self, correo, nombres, apellidos, password=None, **extra_fields):
        if not correo:
            raise ValueError('El correo es obligatorio')
        if not nombres:
            raise ValueError('Los nombres son obligatorios')
        if not apellidos:
            raise ValueError('Los apellidos son obligatorios')

        # Asegurar que telefono tenga valor (MySQL no permite NULL)
        extra_fields.setdefault('telefono', '')
            
        user = self.model(
            correo=self.normalize_email(correo),
            nombres=nombres,
            apellidos=apellidos,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, correo, nombres, apellidos, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')

        return self.create_user(correo, nombres, apellidos, password, **extra_fields)


class Tblusuarios(models.Model):
    """
    Modelo que representa la tabla tblusuarios en la base de datos
    Almacena la información de todos los usuarios registrados en el sistema
    """
    id_users = models.AutoField(primary_key=True, db_column='id_users')
    nombres = models.CharField(max_length=45, db_column='nombres')
    apellidos = models.CharField(max_length=45, db_column='apellidos')
    telefono = models.CharField(max_length=45, db_column='Telefono', blank=True, default='')
    correo = models.CharField(unique=True, max_length=45, db_column='correo')
    contraseña = models.CharField(max_length=255, db_column='contraseña')
    fecha_creacion = models.DateTimeField(db_column='fecha_creacion', auto_now_add=True)
    last_login = models.DateTimeField(db_column='last_login', blank=True, null=True)
    is_superuser = models.BooleanField(default=False, db_column='is_superuser')
    is_staff = models.BooleanField(default=False, db_column='is_staff')
    is_active = models.BooleanField(default=True, db_column='is_active')
    
    # Campos requeridos por Django para el modelo de usuario personalizado
    USERNAME_FIELD = 'correo'  # Use correo as the unique identifier
    REQUIRED_FIELDS = ['nombres', 'apellidos', 'telefono']  # Fields required when creating a superuser

    # Campo date_joined removido ya que no existe en la base de datos

    objects = TblusuariosManager()

    class Meta:
        db_table = 'tblusuarios'
        managed = False  # Indica a Django que no gestione esta tabla
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.correo})"

    def save(self, *args, **kwargs):
        if self.telefono is None:
            self.telefono = ''
        super().save(*args, **kwargs)

    def set_password(self, raw_password):
        """Establece la contraseña cifrada"""
        self.contraseña = make_password(raw_password)
        # Actualizar fecha de último cambio de clave si existe el campo
        if hasattr(self, 'ultimo_cambio_clave'):
            self.ultimo_cambio_clave = datetime.now()

    def check_password(self, raw_password):
        """Verifica si la contraseña coincide"""
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.contraseña)

    def get_full_name(self):
        """Devuelve el nombre completo del usuario"""
        return f"{self.nombres} {self.apellidos}"

    def get_short_name(self):
        """Devuelve el primer nombre del usuario"""
        return self.nombres.split()[0] if self.nombres else ""

    def is_active_user(self):
        """Verifica si el usuario está activo"""
        return self.is_active

    def is_admin(self):
        """Verifica si el usuario es administrador"""
        return self.is_superuser

    def is_agricultor(self):
        """Verifica si el usuario es agricultor"""
        # Este campo puede no existir en la base de datos original
        return getattr(self, 'rol', None) == 'agricultor'

    def is_cliente(self):
        """Verifica si el usuario es cliente"""
        # Este campo puede no existir en la base de datos original
        return getattr(self, 'rol', None) == 'cliente'

    # Métodos y propiedades requeridos por Django
    @property
    def profile(self):
        """Obtiene el perfil extendido del usuario"""
        from apps.usuarios.models.profile_model import UserProfile
        return UserProfile.get_or_create_for_user(self)

    @property
    def password(self):
        return self.contraseña

    @property
    def is_anonymous(self):
        """Verifica si el usuario es anónimo"""
        return False

    @property
    def is_authenticated(self):
        """Verifica si el usuario está autenticado - siempre True para objetos usuario"""
        return True

    def has_perm(self, perm, obj=None):
        """Verifica si el usuario tiene un permiso específico"""
        return self.is_active and self.is_staff

    def has_perms(self, perm_list, obj=None):
        """Verifica si el usuario tiene múltiples permisos"""
        return all(self.has_perm(perm, obj) for perm in perm_list)

    def has_module_perms(self, app_label):
        """Verifica si el usuario tiene permisos para una aplicación específica"""
        return self.is_active and self.is_staff


class UserDevice(models.Model):
    """
    Modelo para almacenar información sobre los dispositivos utilizados por el usuario
    """
    id_dispositivo = models.AutoField(primary_key=True, db_column='id_dispositivo')
    usuario = models.ForeignKey(
        Tblusuarios, 
        on_delete=models.CASCADE,
        db_column='id_usuario'
    )
    dispositivo_id = models.CharField(max_length=255, db_column='dispositivo_id')
    tipo_dispositivo = models.CharField(max_length=50, db_column='tipo_dispositivo')  # desktop, mobile, tablet
    sistema_operativo = models.CharField(max_length=100, db_column='sistema_operativo')
    navegador = models.CharField(max_length=100, db_column='navegador')
    ultima_conexion = models.DateTimeField(db_column='ultima_conexion', auto_now=True)
    fecha_registro = models.DateTimeField(db_column='fecha_registro', auto_now_add=True)
    esta_activo = models.BooleanField(default=True, db_column='esta_activo')

    class Meta:
        db_table = 'user_devices'
        managed = False  # Indica a Django que no gestione esta tabla
        verbose_name = 'Dispositivo de Usuario'
        verbose_name_plural = 'Dispositivos de Usuario'

    def __str__(self):
        return f"Dispositivo {self.tipo_dispositivo} de {self.usuario.nombres} {self.usuario.apellidos}"
        
    def cerrar_sesion_en_dispositivo(self):
        """Marca el dispositivo como inactivo"""
        self.esta_activo = False
        self.save()
        return True


class UserAddress(models.Model):
    """
    Modelo para almacenar múltiples direcciones de usuario
    """
    id_direccion = models.AutoField(primary_key=True, db_column='id_direccion')
    usuario = models.ForeignKey(
        Tblusuarios, 
        on_delete=models.CASCADE,
        db_column='id_usuario'
    )
    direccion = models.CharField(max_length=255, db_column='direccion')
    ciudad = models.CharField(max_length=100, db_column='ciudad')
    departamento = models.CharField(max_length=100, db_column='departamento')
    codigo_postal = models.CharField(max_length=20, db_column='codigo_postal')
    pais = models.CharField(max_length=100, db_column='pais')
    es_principal = models.BooleanField(default=False, db_column='es_principal')
    fecha_creacion = models.DateTimeField(db_column='fecha_creacion', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(db_column='fecha_actualizacion', auto_now=True)

    class Meta:
        db_table = 'user_addresses'
        managed = False  # Indica a Django que no gestione esta tabla
        verbose_name = 'Dirección de Usuario'
        verbose_name_plural = 'Direcciones de Usuario'

    def __str__(self):
        return f"Dirección de {self.usuario.nombres} {self.usuario.apellidos}: {self.direccion}, {self.ciudad}, {self.pais}"
        
    def marcar_como_principal(self):
        """Marca esta dirección como principal y desmarca las demás"""
        UserAddress.objects.filter(
            usuario=self.usuario, 
            es_principal=True
        ).update(es_principal=False)
        self.es_principal = True
        self.save()
        return True


class UserProfile(models.Model):
    """
    Modelo que representa la tabla user_profiles en la base de datos
    Extiende la información del usuario con datos específicos de perfil
    """
    id_perfil = models.AutoField(primary_key=True, db_column='id_perfil')
    id_usuario = models.IntegerField(db_column='id_usuario')  # Referencia directa como ID
    imagen_perfil = models.ImageField(db_column='imagen_perfil', blank=True, null=True, upload_to='profile_pictures/')
    biografia = models.TextField(db_column='biografia', blank=True, null=True)
    sitio_web = models.URLField(db_column='sitio_web', blank=True, null=True)
    telefono_contacto = models.CharField(max_length=20, db_column='telefono_contacto', blank=True, null=True)
    direccion_envio_predeterminada = models.TextField(db_column='direccion_envio_predeterminada', blank=True, null=True)
    fecha_creacion = models.DateTimeField(db_column='fecha_creacion', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(db_column='fecha_actualizacion', auto_now=True)
    notificaciones_activas = models.BooleanField(default=True, db_column='notificaciones_activas')
    idioma_preferido = models.CharField(max_length=10, default='es', db_column='idioma_preferido')
    zona_horaria = models.CharField(max_length=50, default='America/Bogota', db_column='zona_horaria')

    class Meta:
        db_table = 'user_profiles'
        managed = False  # Indica a Django que no gestione esta tabla
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'

    def __str__(self):
        return f"Perfil de {self.id_usuario}"

    @classmethod
    def get_or_create_for_user(cls, user):
        """Obtiene o crea el perfil de un usuario"""
        try:
            profile = cls.objects.get(id_usuario=user.id_users)
        except cls.DoesNotExist:
            try:
                profile = cls.objects.create(
                    id_usuario=user.id_users,
                    idioma_preferido='es',
                    zona_horaria='America/Bogota'
                )
            except Exception:
                # Si la tabla no existe o hay error, retornar None
                return None
        except Exception:
            # Cualquier otro error (tabla no existe, etc.)
            return None
        return profile

    def get_imagen_url(self):
        """Retorna la URL de la imagen de perfil o None"""
        if self.imagen_perfil:
            try:
                return self.imagen_perfil.url
            except ValueError:
                return None
        return None


# Crear una clase temporal para simular un usuario si no existe la tabla
class TemporalUsuario:
    """
    Clase temporal para simular un usuario cuando no existe la tabla en la base de datos
    """
    def __init__(self, id_users=1, nombres='Temporal', apellidos='User', correo='temp@example.com', estado='activo'):
        self.id_users = id_users
        self.nombres = nombres
        self.apellidos = apellidos
        self.correo = correo
        self.estado = estado
        self.is_active = True
        self.is_staff = False
        self.is_superuser = False
        
    def check_password(self, raw_password):
        # Simular verificación de contraseña
        return True  # En producción, esto debería verificar la contraseña real
    
    def get_full_name(self):
        return f"{self.nombres} {self.apellidos}"
    
    @property
    def password(self):
        return "temp_password"