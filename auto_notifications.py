#!/usr/bin/env python
"""
Script para ejecutar automáticamente las notificaciones diarias
Ejecutar este script en segundo plano o con Task Scheduler
"""

import schedule
import time
import subprocess
import sys
from datetime import datetime
import os

# Configurar el directorio del proyecto
PROJECT_DIR = r"c:\Users\H P\Downloads\tvservices_project"
os.chdir(PROJECT_DIR)

def send_notifications(days):
    """Envía notificaciones para un día específico"""
    try:
        print(f"🕘 {datetime.now().strftime('%H:%M:%S')} - Enviando notificaciones día {days}...")
        
        result = subprocess.run([
            sys.executable, 'manage.py', 'send_expiration_notifications', 
            '--days', str(days)
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print(f"✅ Notificaciones día {days} enviadas exitosamente")
            if result.stdout:
                print(f"📊 Resultado: {result.stdout.strip()}")
        else:
            print(f"❌ Error enviando notificaciones día {days}: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error inesperado día {days}: {str(e)}")

def daily_notifications():
    """Ejecuta todas las notificaciones diarias"""
    print(f"\n🚀 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} - Iniciando notificaciones diarias")
    
    # Enviar notificaciones para todos los días configurados
    for days in [0, 1, 3, 7]:
        send_notifications(days)
        time.sleep(2)  # Esperar 2 segundos entre envíos
    
    print("✅ Todas las notificaciones diarias completadas\n")

# Programar envío diario a las 9:00 AM
schedule.every().day.at("09:00").do(daily_notifications)

# También programar a las 6:00 PM para casos urgentes
schedule.every().day.at("18:00").do(lambda: send_notifications(0))

def main():
    """Función principal"""
    print("🤖 SISTEMA DE NOTIFICACIONES AUTOMÁTICAS INICIADO")
    print("=" * 60)
    print("📅 Programación:")
    print("   • 09:00 AM - Todas las notificaciones (0, 1, 3, 7 días)")
    print("   • 06:00 PM - Solo notificaciones día 0 (urgentes)")
    print("=" * 60)
    
    # Ejecutar inmediatamente al iniciar (opcional)
    print("🚀 Ejecutando notificaciones iniciales...")
    daily_notifications()
    
    # Mantener el script corriendo
    print("⏰ Esperando horarios programados... (Ctrl+C para detener)")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Verificar cada minuto

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Sistema de notificaciones detenido por el usuario")
    except Exception as e:
        print(f"\n❌ Error en el sistema: {str(e)}")
