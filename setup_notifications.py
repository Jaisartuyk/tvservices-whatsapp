#!/usr/bin/env python
"""
Script de configuración automática para el sistema de notificaciones de WhatsApp
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header():
    print("=" * 60)
    print("🚀 CONFIGURACIÓN DE NOTIFICACIONES WHATSAPP")
    print("   Sistema automático para TV Services")
    print("=" * 60)

def check_requirements():
    """Verifica que los requisitos estén instalados"""
    print("\n📋 Verificando requisitos...")
    
    try:
        import django
        print(f"✅ Django {django.get_version()} instalado")
    except ImportError:
        print("❌ Django no está instalado")
        return False
    
    try:
        import requests
        print("✅ Requests instalado")
    except ImportError:
        print("❌ Requests no está instalado. Instalando...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        print("✅ Requests instalado exitosamente")
    
    return True

def create_env_file():
    """Crea el archivo .env si no existe"""
    print("\n📄 Configurando archivo .env...")
    
    env_path = Path(".env")
    env_example_path = Path(".env.example")
    
    if env_path.exists():
        print("⚠️ El archivo .env ya existe. No se sobrescribirá.")
        return
    
    if env_example_path.exists():
        # Copiar desde .env.example
        with open(env_example_path, 'r') as f:
            content = f.read()
        
        with open(env_path, 'w') as f:
            f.write(content)
        
        print("✅ Archivo .env creado desde .env.example")
        print("⚠️ IMPORTANTE: Edita el archivo .env con tus credenciales de WaSender")
    else:
        # Crear archivo básico
        env_content = """# Configuración de Django
DEBUG=True
SECRET_KEY=tu-clave-secreta-aqui

# Configuración de WaSender API
WASENDER_API_URL=https://wasenderapi.com/api
WASENDER_API_KEY=tu-api-key-de-wasender
WASENDER_INSTANCE_ID=tu-instance-id-de-wasender

# Configuración de notificaciones
ENABLE_WHATSAPP_NOTIFICATIONS=True
NOTIFICATION_TIME_HOUR=9
"""
        
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        print("✅ Archivo .env creado con configuración básica")

def run_migrations():
    """Ejecuta las migraciones de Django"""
    print("\n🔄 Ejecutando migraciones...")
    
    try:
        # Crear migraciones
        result = subprocess.run([
            sys.executable, "manage.py", "makemigrations"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Migraciones creadas exitosamente")
        else:
            print(f"⚠️ Advertencia en makemigrations: {result.stderr}")
        
        # Aplicar migraciones
        result = subprocess.run([
            sys.executable, "manage.py", "migrate"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Migraciones aplicadas exitosamente")
        else:
            print(f"❌ Error aplicando migraciones: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando migraciones: {str(e)}")
        return False
    
    return True

def create_logs_directory():
    """Crea el directorio de logs"""
    print("\n📁 Creando directorio de logs...")
    
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    print("✅ Directorio de logs creado")

def test_configuration():
    """Prueba la configuración básica"""
    print("\n🧪 Probando configuración...")
    
    try:
        result = subprocess.run([
            sys.executable, "manage.py", "test_whatsapp_service"
        ], capture_output=True, text=True)
        
        print("📊 Resultado de la prueba:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Advertencias:")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Error ejecutando prueba: {str(e)}")

def show_next_steps():
    """Muestra los próximos pasos"""
    print("\n" + "=" * 60)
    print("🎉 ¡CONFIGURACIÓN COMPLETADA!")
    print("=" * 60)
    
    print("\n📝 PRÓXIMOS PASOS:")
    print("\n1. 🔑 Configura tus credenciales de WaSender:")
    print("   - Ve a https://wasenderapi.com/")
    print("   - Crea una cuenta y configura tu instancia")
    print("   - Edita el archivo .env con tus credenciales")
    
    print("\n2. 🧪 Prueba el sistema:")
    print("   python manage.py test_whatsapp_service --phone 573001234567")
    
    print("\n3. 📱 Envía notificaciones de prueba:")
    print("   python manage.py send_expiration_notifications --days 1 --dry-run")
    
    print("\n4. ⏰ Configura la automatización:")
    print("   - Linux/Mac: Configura crontab")
    print("   - Windows: Usa Task Scheduler")
    print("   - Ejemplo cron: 0 9 * * * cd /tu/proyecto && python manage.py send_expiration_notifications --days 1")
    
    print("\n5. 📊 Monitorea las notificaciones:")
    print("   - Django Admin: Registros de Notificaciones")
    print("   - Logs: logs/notifications.log")
    
    print("\n📚 Documentación completa: NOTIFICACIONES_WHATSAPP.md")

def main():
    """Función principal"""
    print_header()
    
    # Verificar que estamos en el directorio correcto
    if not Path("manage.py").exists():
        print("❌ Error: No se encontró manage.py")
        print("   Ejecuta este script desde el directorio raíz del proyecto Django")
        sys.exit(1)
    
    # Verificar requisitos
    if not check_requirements():
        print("❌ Error: Requisitos no cumplidos")
        sys.exit(1)
    
    # Configurar archivo .env
    create_env_file()
    
    # Crear directorio de logs
    create_logs_directory()
    
    # Ejecutar migraciones
    if not run_migrations():
        print("❌ Error: No se pudieron aplicar las migraciones")
        sys.exit(1)
    
    # Probar configuración
    test_configuration()
    
    # Mostrar próximos pasos
    show_next_steps()

if __name__ == "__main__":
    main()
