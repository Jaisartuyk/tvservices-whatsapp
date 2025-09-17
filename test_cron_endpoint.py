#!/usr/bin/env python3
"""
Script para probar el endpoint de cron notifications
"""
import requests
import json

def test_cron_endpoint():
    """Probar el endpoint de notificaciones cron"""
    
    # URL real de tu aplicación en Railway
    url = "https://tvservices-whatsapp-production.up.railway.app/cron/notifications/"
    
    print(f"🔍 Probando endpoint: {url}")
    
    try:
        # Probar GET (debería devolver error de método)
        print("\n📡 Probando GET request...")
        response_get = requests.get(url, timeout=30)
        print(f"GET Status: {response_get.status_code}")
        print(f"GET Response: {response_get.text[:200]}...")
        
        # Probar POST (método correcto)
        print("\n📡 Probando POST request...")
        response_post = requests.post(url, timeout=30)
        print(f"POST Status: {response_post.status_code}")
        print(f"POST Response: {response_post.text[:500]}...")
        
        if response_post.status_code == 200:
            try:
                data = response_post.json()
                print(f"✅ Respuesta JSON: {json.dumps(data, indent=2)}")
            except:
                print("⚠️  Respuesta no es JSON válido")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_cron_endpoint()
