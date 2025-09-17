#!/usr/bin/env python
"""
Script para ejecutar migraciones directamente en Railway PostgreSQL
"""
import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno de Railway
load_dotenv('.env.railway')

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tvservices.settings')

import django
django.setup()

from django.core.management import execute_from_command_line

def migrate_to_railway():
    """Ejecutar migraciones en Railway PostgreSQL"""
    
    print("🚀 Conectando a Railway PostgreSQL...")
    print(f"📊 Database URL: {os.environ.get('DATABASE_URL', 'Not set')[:50]}...")
    
    try:
        # Verificar conexión
        print("🔍 Verificando conexión a base de datos...")
        execute_from_command_line(['manage.py', 'dbshell', '--command=SELECT 1;'])
        print("✅ Conexión exitosa!")
        
    except Exception as e:
        print(f"⚠️  Advertencia de conexión: {e}")
        print("Continuando con migraciones...")
    
    try:
        # Crear migraciones
        print("📝 Creando migraciones...")
        execute_from_command_line(['manage.py', 'makemigrations'])
        
        # Aplicar migraciones
        print("🔄 Aplicando migraciones...")
        execute_from_command_line(['manage.py', 'migrate', '--verbosity=2'])
        
        # Verificar tablas creadas
        print("🔍 Verificando tablas creadas...")
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE 'subscriptions_%'
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            
        print("📊 Tablas de subscriptions creadas:")
        for table in tables:
            print(f"   ✅ {table[0]}")
            
        if not tables:
            print("❌ No se encontraron tablas de subscriptions")
            return False
            
        print("🎉 ¡Migraciones completadas exitosamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error durante migraciones: {e}")
        return False

if __name__ == '__main__':
    success = migrate_to_railway()
    if success:
        print("\n✅ Listo para poblar datos iniciales")
        print("Ejecuta: python populate_railway_data.py")
    else:
        print("\n❌ Migraciones fallaron")
        sys.exit(1)
