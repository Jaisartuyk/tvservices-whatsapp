#!/usr/bin/env python
"""
Test simple de WhatsApp API - Exactamente como el curl
"""
import requests
import json

def test_whatsapp_simple():
    """Probar WhatsApp con el formato exacto del curl"""
    
    # Configuración exacta
    url = "https://wasenderapi.com/api/send-message"
    api_key = "e736f86d08e73ce5ee6f209098dc701a60deb8157f26b79485f66e1249aabee6"
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # Payload corregido con 'text'
    payload = {
        "to": "+593968196046",  # Número de Ecuador
        "text": "🧪 Prueba desde Python - TV Services"
    }
    
    print("🔍 Probando WhatsApp API...")
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        print(f"\n📊 Status Code: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        print(f"📝 Response Text: {response.text}")
        
        if response.status_code == 200:
            print("✅ ¡Éxito! WhatsApp enviado")
            try:
                data = response.json()
                print(f"📱 Respuesta JSON: {json.dumps(data, indent=2)}")
            except:
                print("⚠️  Respuesta no es JSON")
        else:
            print(f"❌ Error {response.status_code}")
            try:
                error_data = response.json()
                print(f"🔍 Error JSON: {json.dumps(error_data, indent=2)}")
            except:
                print(f"🔍 Error Text: {response.text}")
                
    except Exception as e:
        print(f"💥 Excepción: {e}")

if __name__ == "__main__":
    test_whatsapp_simple()
