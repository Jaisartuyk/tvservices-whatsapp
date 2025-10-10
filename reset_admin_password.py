#!/usr/bin/env python
"""
Script para resetear la contraseña del superusuario admin
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tvservices.settings')
django.setup()

from django.contrib.auth.models import User

def reset_admin_password():
    """Resetear contraseña del superusuario admin"""
    username = 'admin'
    new_password = 'admin123'  # Contraseña por defecto
    
    try:
        user = User.objects.get(username=username)
        user.set_password(new_password)
        user.save()
        
        print("=" * 80)
        print("✅ CONTRASEÑA RESETEADA EXITOSAMENTE")
        print("=" * 80)
        print(f"👤 Usuario: {username}")
        print(f"📧 Email: {user.email}")
        print(f"🔑 Nueva Contraseña: {new_password}")
        print("=" * 80)
        print("⚠️  IMPORTANTE: Cambia esta contraseña después del primer login")
        print("=" * 80)
        print()
        print("🌐 Accede al admin en: http://localhost:8000/admin/")
        print()
        
    except User.DoesNotExist:
        print(f"❌ Error: El usuario '{username}' no existe")
        print("💡 Ejecuta 'python create_superuser.py' para crear uno nuevo")

if __name__ == '__main__':
    reset_admin_password()
