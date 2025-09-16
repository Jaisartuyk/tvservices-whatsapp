#!/usr/bin/env python
"""
Script detallado para probar WaSender API y ver la respuesta completa
"""

import requests
import json
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

def test_detailed():
    """Prueba detallada con logging completo"""
    
    print("🔍 PRUEBA DETALLADA DE WASENDER API")
    print("=" * 50)
    
    # Configuración
    api_key = os.getenv('WASENDER_API_KEY')
    session_id = os.getenv('WASENDER_SESSION_ID')
    base_url = os.getenv('WASENDER_API_URL')
    
    print(f"🔧 Configuración:")
    print(f"   API Key: {api_key[:20]}..." if api_key else "❌ No configurado")
    print(f"   Session ID: {session_id}")
    print(f"   Base URL: {base_url}")
    
    # URL completa
    url = f"{base_url}/api/send-message"
    print(f"📡 URL completa: {url}")
    
    # Headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    print(f"📋 Headers: {json.dumps(headers, indent=2)}")
    
    # Payload con diferentes variaciones
    payloads_to_test = [
        {
            'to': '+573001234567',
            'text': '🧪 Prueba 1: Mensaje básico',
            'session_id': int(session_id) if session_id else None
        },
        {
            'to': '+573001234567',
            'message': '🧪 Prueba 2: Con campo message',
            'session_id': int(session_id) if session_id else None
        },
        {
            'phone': '+573001234567',
            'text': '🧪 Prueba 3: Con campo phone',
            'session_id': int(session_id) if session_id else None
        },
        {
            'to': '+573001234567',
            'text': '🧪 Prueba 4: Sin session_id'
        }
    ]
    
    for i, payload in enumerate(payloads_to_test, 1):
        print(f"\n🧪 PRUEBA {i}:")
        print(f"📦 Payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            print(f"📊 Status Code: {response.status_code}")
            print(f"📄 Response Headers: {dict(response.headers)}")
            
            try:
                response_json = response.json()
                print(f"📋 Response JSON: {json.dumps(response_json, indent=2)}")
            except:
                print(f"📄 Response Text: {response.text}")
            
            if response.status_code == 200:
                print("✅ ¡Éxito!")
                return True
            else:
                print(f"⚠️ Error {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión: {str(e)}")
        except Exception as e:
            print(f"❌ Error inesperado: {str(e)}")
    
    return False

def test_webhook_format():
    """Prueba usando el formato que vimos en el webhook"""
    print(f"\n🔗 PRUEBA CON FORMATO DE WEBHOOK")
    print("=" * 50)
    
    # Basándome en tu webhook de ejemplo
    api_key = os.getenv('WASENDER_API_KEY')
    base_url = os.getenv('WASENDER_API_URL')
    
    url = f"{base_url}/api/send-message"
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    # Formato similar al webhook que recibiste
    payload = {
        'session_id': 8359,
        'to': '+573001234567',
        'text': '🧪 Mensaje de prueba desde TV Services - Formato webhook'
    }
    
    print(f"📦 Payload webhook format: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        
        try:
            response_json = response.json()
            print(f"📋 Response: {json.dumps(response_json, indent=2)}")
        except:
            print(f"📄 Response Text: {response.text}")
            
        if response.status_code == 200:
            print("✅ ¡Webhook format funciona!")
            return True
        else:
            print(f"⚠️ Error con webhook format: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    return False

if __name__ == "__main__":
    success = test_detailed()
    if not success:
        test_webhook_format()
