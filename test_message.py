#!/usr/bin/env python
"""
Script simple para probar el envío de mensajes de WhatsApp
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

from subscriptions.services import WhatsAppService

def test_message():
    """Prueba el envío de un mensaje simple"""
    print("🧪 Probando envío de mensaje de WhatsApp...")
    
    # Crear servicio
    whatsapp = WhatsAppService()
    
    # Número de prueba (cambia por tu número real)
    phone = "+573001234567"  # Formato: +57XXXXXXXXX
    message = "🧪 ¡Hola! Este es un mensaje de prueba desde TV Services. El sistema de notificaciones funciona correctamente. 🚀"
    
    print(f"📱 Enviando mensaje a: {phone}")
    print(f"💬 Mensaje: {message}")
    
    # Enviar mensaje
    result = whatsapp.send_message(phone, message)
    
    if result['success']:
        print("✅ ¡Mensaje enviado exitosamente!")
        print(f"📊 Respuesta de la API: {result.get('data', {})}")
    else:
        print(f"❌ Error enviando mensaje: {result.get('error')}")
    
    return result

if __name__ == "__main__":
    test_message()
