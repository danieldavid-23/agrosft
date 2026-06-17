"""
Script para crear o actualizar el superusuario de AgroSFT.
Ejecutar con: python crear_superusuario.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.usuarios.models.profile_model import Tblusuarios
from django.db import connection

CORREO = 'agrosft84@gmail.com'
PASSWORD = 'Agrosft2026'

# Usar SQL directo para evitar problemas de cascade con tablas inexistentes
with connection.cursor() as cursor:
    cursor.execute("SELECT id_users FROM tblusuarios WHERE correo = %s", [CORREO])
    rows = cursor.fetchall()

if rows:
    # Tomar el primer ID
    user_id = rows[0][0]
    
    # Eliminar duplicados con SQL directo (sin cascade)
    if len(rows) > 1:
        other_ids = [r[0] for r in rows if r[0] != user_id]
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM tblusuarios WHERE id_users IN ({})".format(
                    ','.join(str(i) for i in other_ids)
                )
            )
        print(f"Eliminados {len(other_ids)} usuarios duplicados")

    # Actualizar password con Django ORM
    user = Tblusuarios.objects.get(id_users=user_id)
    user.set_password(PASSWORD)
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.save()
    print(f"Usuario actualizado: {user.correo} (ID: {user.id_users})")
else:
    user = Tblusuarios.objects.create_user(
        correo=CORREO,
        nombres='daniel',
        apellidos='hernandez',
        password=PASSWORD,
        telefono='3011327929',
        is_staff=True,
        is_superuser=True,
        is_active=True
    )
    print(f"Superusuario creado: {user.correo} (ID: {user.id_users})")

print(f"\n  Correo:      {CORREO}")
print(f"  Contrasena:  {PASSWORD}")
print(f"\nAccede al admin en: http://127.0.0.1:8000/admin/")
