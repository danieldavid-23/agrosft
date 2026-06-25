from django.apps import AppConfig

class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.usuarios'  # Full module path
    label = 'usuarios'      # Simple label for internal references
    verbose_name = 'Usuarios'
    
    def ready(self):
        import sys
        if 'makemigrations' in sys.argv:
            return
            
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                # Crear tabla user_profiles
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    id_perfil INT AUTO_INCREMENT PRIMARY KEY,
                    id_usuario INT NOT NULL UNIQUE,
                    imagen_perfil VARCHAR(255) NULL,
                    biografia TEXT NULL,
                    sitio_web VARCHAR(200) NULL,
                    telefono_contacto VARCHAR(20) NULL,
                    direccion_envio_predeterminada TEXT NULL,
                    fecha_creacion DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                    fecha_actualizacion DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
                    notificaciones_activas TINYINT(1) NOT NULL DEFAULT 1,
                    idioma_preferido VARCHAR(10) NOT NULL DEFAULT 'es',
                    zona_horaria VARCHAR(50) NOT NULL DEFAULT 'America/Bogota',
                    FOREIGN KEY (id_usuario) REFERENCES tblusuarios (id_users) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """)
                
                # Crear tabla user_devices
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_devices (
                    id_dispositivo INT AUTO_INCREMENT PRIMARY KEY,
                    id_usuario INT NOT NULL,
                    dispositivo_id VARCHAR(255) NOT NULL,
                    tipo_dispositivo VARCHAR(50) NOT NULL,
                    sistema_operativo VARCHAR(100) NOT NULL,
                    navegador VARCHAR(100) NOT NULL,
                    ultima_conexion DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                    fecha_registro DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                    esta_activo TINYINT(1) NOT NULL DEFAULT 1,
                    FOREIGN KEY (id_usuario) REFERENCES tblusuarios (id_users) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """)
                
                # Crear tabla user_addresses
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_addresses (
                    id_direccion INT AUTO_INCREMENT PRIMARY KEY,
                    id_usuario INT NOT NULL,
                    direccion VARCHAR(255) NOT NULL,
                    ciudad VARCHAR(100) NOT NULL,
                    departamento VARCHAR(100) NOT NULL,
                    codigo_postal VARCHAR(20) NOT NULL,
                    pais VARCHAR(100) NOT NULL,
                    es_principal TINYINT(1) NOT NULL DEFAULT 0,
                    fecha_creacion DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                    fecha_actualizacion DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                    FOREIGN KEY (id_usuario) REFERENCES tblusuarios (id_users) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error al crear las tablas de perfil/dispositivos/direcciones: {e}")

        # Clean up temporary diagnostic files if they exist
        import os
        for temp_file in ["perfil_table_check.txt", "profile_run_test.txt", "post_test_result.txt"]:
            path = os.path.join("c:/Users/daniel/Downloads/agrosft GIT HUB --CONECCION", temp_file)
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    pass