#!/usr/bin/env python
"""
Script para ejecutar notificaciones automáticas en Railway
Se ejecuta como cron job
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tvservices.settings')
django.setup()

import subprocess
from datetime import datetime

def run_notifications():
    """Ejecuta todas las notificaciones diarias"""
    print(f"🕘 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Iniciando notificaciones automáticas")
    
    # Lista de días a notificar
    days_to_notify = [0, 1, 3, 7]
    
    for days in days_to_notify:
        try:
            print(f"📱 Enviando notificaciones día {days}...")
            
            result = subprocess.run([
                sys.executable, 'manage.py', 'send_expiration_notifications', 
                '--days', str(days)
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"✅ Notificaciones día {days} enviadas exitosamente")
                if result.stdout:
                    print(f"📊 Resultado: {result.stdout.strip()}")
            else:
                print(f"❌ Error enviando notificaciones día {days}: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Error inesperado día {days}: {str(e)}")
    
    print("✅ Proceso de notificaciones completado")

if __name__ == "__main__":
    run_notifications()
