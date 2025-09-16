#!/usr/bin/env python
"""
Script de debug para probar la API de WaSender directamente
"""

import requests
import json
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

def test_wasender_direct():
    """Prueba directa de la API de WaSender"""
    
    # Configuración
    api_key = os.getenv('WASENDER_API_KEY')
    base_url = os.getenv('WASENDER_API_URL', 'https://wasenderapi.com/api')
    
    print("🔧 Configuración:")
    print(f"API Key: {api_key[:20]}..." if api_key else "❌ No configurado")
    print(f"Base URL: {base_url}")
    
    if not api_key:
        print("❌ Error: API Key no configurado")
        return
    
    # Probar diferentes endpoints
    endpoints_to_test = [
        "/send-message",
        "/send",
        "/message/send",
        "/v1/send-message"
    ]
    
    for endpoint in endpoints_to_test:
        print(f"\n🧪 Probando endpoint: {endpoint}")
        test_endpoint(base_url, endpoint, api_key)

def test_endpoint(base_url, endpoint, api_key):
    """Prueba un endpoint específico"""
    
    url = f"{base_url}{endpoint}"
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    # Payload de prueba
    payload = {
        'to': '+573001234567',  # Número de prueba
        'text': '🧪 Mensaje de prueba desde debug script'
    }
    
    try:
        print(f"📡 Enviando POST a: {url}")
        print(f"📋 Headers: {headers}")
        print(f"📦 Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(
            url, 
            json=payload, 
            headers=headers, 
            timeout=10
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        try:
            response_json = response.json()
            print(f"📋 Response JSON: {json.dumps(response_json, indent=2)}")
        except:
            print(f"📄 Response Text: {response.text}")
        
        if response.status_code == 200:
            print("✅ ¡Endpoint funciona!")
            return True
        else:
            print(f"⚠️ Endpoint retornó código: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {str(e)}")
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
    
    return False

def test_curl_equivalent():
    """Reproduce exactamente el comando curl que proporcionaste"""
    
    print("\n" + "="*60)
    print("🔄 Reproduciendo tu comando curl exacto...")
    print("="*60)
    
    api_key = "e736f86d08e73ce5ee6f209098dc701a60deb8157f26b79485f66e1249aabee6"
    url = "https://wasenderapi.com/api/send-message"
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'to': '+1234567890',  # Tu número de ejemplo
        'text': 'Hello from API!'
    }
    
    try:
        print(f"📡 URL: {url}")
        print(f"🔑 Authorization: Bearer {api_key[:20]}...")
        print(f"📦 Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        print(f"\n📊 Status Code: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"📋 Response: {json.dumps(response_data, indent=2)}")
        except:
            print(f"📄 Response Text: {response.text}")
            
        if response.status_code == 200:
            print("✅ ¡API funciona correctamente!")
        else:
            print(f"⚠️ API retornó código de error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("🔍 DIAGNÓSTICO DE WASENDER API")
    print("="*60)
    
    test_wasender_direct()
    test_curl_equivalent()
