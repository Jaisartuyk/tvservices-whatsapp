#!/usr/bin/env python
"""
Script para crear superusuario en Railway
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tvservices.settings')
django.setup()

from django.contrib.auth.models import User

def create_superuser():
    """Crear superusuario si no existe"""
    username = 'admin'
    email = 'admin@tvservices.com'
    password = 'admin123'  # Cambiar por contraseña segura
    
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username, email, password)
        print(f'✅ Superusuario creado: {username}')
        print(f'📧 Email: {email}')
        print(f'🔑 Password: {password}')
        print('⚠️  IMPORTANTE: Cambia la contraseña después del primer login')
    else:
        print(f'ℹ️  Superusuario {username} ya existe')

if __name__ == '__main__':
    create_superuser()
