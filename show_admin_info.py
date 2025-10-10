#!/usr/bin/env python
"""
Script para mostrar información del superusuario admin
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tvservices.settings')
django.setup()

from django.contrib.auth.models import User

def show_admin_info():
    """Mostrar información del superusuario admin"""
    username = 'admin'
    
    try:
        user = User.objects.get(username=username)
        
        print("=" * 80)
        print("👤 INFORMACIÓN DEL SUPERUSUARIO")
        print("=" * 80)
        print(f"Usuario: {user.username}")
        print(f"Email: {user.email}")
        print(f"Nombre: {user.first_name or '(No configurado)'}")
        print(f"Apellido: {user.last_name or '(No configurado)'}")
        print(f"Staff: {'✅ Sí' if user.is_staff else '❌ No'}")
        print(f"Superusuario: {'✅ Sí' if user.is_superuser else '❌ No'}")
        print(f"Activo: {'✅ Sí' if user.is_active else '❌ No'}")
        print(f"Último login: {user.last_login or 'Nunca'}")
        print(f"Fecha de creación: {user.date_joined}")
        print("=" * 80)
        print()
        print("🌐 URL del Admin: http://localhost:8000/admin/")
        print()
        print("💡 Comandos útiles:")
        print("   - Resetear contraseña: python reset_admin_password.py")
        print("   - Crear nuevo superusuario: python manage.py createsuperuser")
        print("=" * 80)
        
    except User.DoesNotExist:
        print("=" * 80)
        print("❌ ERROR: El usuario 'admin' no existe")
        print("=" * 80)
        print()
        print("💡 Para crear un superusuario, ejecuta:")
        print("   python create_superuser.py")
        print()
        print("O usa el comando de Django:")
        print("   python manage.py createsuperuser")
        print("=" * 80)

if __name__ == '__main__':
    show_admin_info()
