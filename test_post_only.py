#!/usr/bin/env python3
"""
Script para probar solo POST al endpoint de cron
"""
import requests
import json

def test_post_cron():
    """Probar solo POST request"""
    
    url = "https://tvservices-whatsapp-production.up.railway.app/cron/notifications/"
    
    print(f"🔍 Probando POST a: {url}")
    
    try:
        response = requests.post(url, timeout=60)
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        print(f"📄 Response Text: {response.text}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ JSON Response:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
            except:
                print("⚠️  No es JSON válido")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_post_cron()
