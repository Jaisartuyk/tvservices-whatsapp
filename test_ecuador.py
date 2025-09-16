#!/usr/bin/env python
"""
Script para probar WhatsApp con número de Ecuador
"""

import os
import sys
import django
import time
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tvservices.settings')
django.setup()

from subscriptions.services import WhatsAppService

def test_ecuador_number():
    """Prueba con número de Ecuador"""
    print("🇪🇨 Probando envío a número de Ecuador...")
    
    # Tu número con código de país de Ecuador (+593)
    ecuador_number = "+593968196046"  # 0968196046 -> +593968196046
    
    print(f"📱 Número de destino: {ecuador_number}")
    print(f"🌍 País: Ecuador (+593)")
    
    # Mensaje de prueba
    message = """🧪 ¡Hola desde TV Services!

Este es un mensaje de prueba del sistema de notificaciones automáticas.

✅ El sistema está funcionando correctamente
🚀 Listo para enviar notificaciones de vencimiento

¡Saludos desde Ecuador! 🇪🇨"""
    
    print(f"💬 Mensaje a enviar:")
    print(message)
    print("-" * 50)
    
    # Crear servicio y enviar
    whatsapp = WhatsAppService()
    
    print("📡 Enviando mensaje...")
    result = whatsapp.send_message(ecuador_number, message)
    
    if result['success']:
        print("✅ ¡MENSAJE ENVIADO EXITOSAMENTE!")
        print(f"📊 Respuesta de la API: {result.get('data', {})}")
        print("\n🎉 ¡El sistema de notificaciones está funcionando!")
        print("📱 Revisa tu WhatsApp para confirmar la recepción del mensaje.")
    else:
        error = result.get('error', 'Error desconocido')
        print(f"❌ Error enviando mensaje: {error}")
        
        # Sugerencias según el tipo de error
        if "429" in str(error):
            print("💡 Sugerencia: Rate limit alcanzado. Espera unos minutos y vuelve a intentar.")
        elif "422" in str(error):
            print("💡 Sugerencia: Verifica que el número tenga WhatsApp activo.")
        elif "404" in str(error):
            print("💡 Sugerencia: Verifica la configuración de la API.")
    
    return result

def test_different_formats():
    """Prueba diferentes formatos del número ecuatoriano"""
    print("\n🔧 Probando diferentes formatos del número...")
    
    formats_to_test = [
        "0968196046",      # Formato local
        "593968196046",    # Con código sin +
        "+593968196046",   # Formato internacional completo
        "593 968 196 046", # Con espacios
        "+593-968-196-046" # Con guiones
    ]
    
    whatsapp = WhatsAppService()
    
    for phone_format in formats_to_test:
        print(f"\n📞 Probando formato: {phone_format}")
        cleaned = whatsapp._clean_phone_number(phone_format)
        print(f"🧹 Número limpio: {cleaned}")
        
        if cleaned:
            # Agregar + si no lo tiene
            if not cleaned.startswith('+'):
                cleaned = '+' + cleaned
            print(f"📱 Formato final: {cleaned}")
        else:
            print("❌ Formato inválido")

if __name__ == "__main__":
    print("🇪🇨 PRUEBA CON NÚMERO DE ECUADOR")
    print("=" * 60)
    
    # Primero probar los formatos
    test_different_formats()
    
    # Luego enviar el mensaje real
    print("\n" + "=" * 60)
    test_ecuador_number()
