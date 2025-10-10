# 🧪 CLIENTE DE PRUEBAS PARA INTEGRACIÓN CASCADE
# Script para probar la conexión con tu app en PythonAnywhere

import requests
import json
from datetime import datetime, date
import time

class CascadeTestClient:
    """🧪 Cliente para probar la integración con Cascade"""
    
    def __init__(self, base_url, api_key):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
    
    def test_health_check(self):
        """💚 Probar health check"""
        print("🧪 Testing Health Check...")
        try:
            response = self.session.get(f"{self.base_url}/api/cascade/health/")
            response.raise_for_status()
            
            data = response.json()
            print(f"✅ Health Check OK: {data['status']}")
            return True
            
        except Exception as e:
            print(f"❌ Health Check Failed: {str(e)}")
            return False
    
    def test_system_status(self):
        """🔍 Probar estado del sistema"""
        print("\n🧪 Testing System Status...")
        try:
            response = self.session.get(f"{self.base_url}/api/cascade/status/")
            response.raise_for_status()
            
            data = response.json()
            status = data['system_status']
            
            print(f"✅ System Status: {status['overall']}")
            print(f"   Database: {status['database']['status']}")
            print(f"   CPU: {status['system'].get('cpu_percent', 'N/A')}%")
            print(f"   Memory: {status['system'].get('memory', {}).get('percent', 'N/A')}%")
            
            return True
            
        except Exception as e:
            print(f"❌ System Status Failed: {str(e)}")
            return False
    
    def test_utensilios_api(self):
        """📊 Probar API de utensilios"""
        print("\n🧪 Testing Utensilios API...")
        try:
            params = {
                'fecha': date.today().isoformat(),
                'page': 1,
                'per_page': 10
            }
            
            response = self.session.get(
                f"{self.base_url}/api/cascade/utensilios/",
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            
            print(f"✅ Utensilios API OK")
            print(f"   Records: {len(data['data'])}")
            print(f"   Total Pages: {data['pagination']['total_pages']}")
            print(f"   Total Items: {data['pagination']['total_items']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Utensilios API Failed: {str(e)}")
            return False
    
    def test_dashboard_api(self):
        """📈 Probar API del dashboard"""
        print("\n🧪 Testing Dashboard API...")
        try:
            params = {
                'fecha': date.today().isoformat()
            }
            
            response = self.session.get(
                f"{self.base_url}/api/cascade/dashboard/",
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            dashboard_data = data['data']
            
            print(f"✅ Dashboard API OK")
            print(f"   Fecha: {dashboard_data['fecha']}")
            print(f"   Total Controles: {dashboard_data['total_controles']}")
            print(f"   Módulos: {len(dashboard_data['data_modulos'])}")
            print(f"   Tendencia días: {len(dashboard_data['tendencia'])}")
            
            return True
            
        except Exception as e:
            print(f"❌ Dashboard API Failed: {str(e)}")
            return False
    
    def test_webhook(self):
        """🤖 Probar webhook principal"""
        print("\n🧪 Testing Webhook...")
        try:
            payload = {
                'command': 'get_system_status',
                'parameters': {}
            }
            
            response = self.session.post(
                f"{self.base_url}/api/cascade/webhook/",
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            
            print(f"✅ Webhook OK")
            print(f"   Status: {data['status']}")
            print(f"   Result: {data['result']['system_status']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Webhook Failed: {str(e)}")
            return False
    
    def test_report_creation(self):
        """📋 Probar creación de reportes"""
        print("\n🧪 Testing Report Creation...")
        try:
            payload = {
                'fecha': date.today().isoformat(),
                'tipo': 'completo',
                'formato': 'json'
            }
            
            response = self.session.post(
                f"{self.base_url}/api/cascade/reports/",
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            reporte = data['reporte']
            
            print(f"✅ Report Creation OK")
            print(f"   Tipo: {reporte['tipo']}")
            print(f"   Formato: {reporte['formato']}")
            print(f"   Fecha: {reporte['fecha']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Report Creation Failed: {str(e)}")
            return False
    
    def test_notification_api(self):
        """📱 Probar API de notificaciones"""
        print("\n🧪 Testing Notification API...")
        try:
            payload = {
                'type': 'test',
                'message': 'Mensaje de prueba desde Cascade Test Client',
                'recipients': ['+593999999999'],
                'channel': 'whatsapp'
            }
            
            response = self.session.post(
                f"{self.base_url}/api/cascade/notify/",
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            notification = data['notification']
            
            print(f"✅ Notification API OK")
            print(f"   Type: {notification['type']}")
            print(f"   Channel: {notification['channel']}")
            print(f"   Recipients: {notification['recipients_count']}")
            print(f"   Sent: {notification['sent_count']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Notification API Failed: {str(e)}")
            return False
    
    def run_all_tests(self):
        """🚀 Ejecutar todas las pruebas"""
        print("🤖 CASCADE INTEGRATION TEST SUITE")
        print("=" * 50)
        
        tests = [
            self.test_health_check,
            self.test_system_status,
            self.test_utensilios_api,
            self.test_dashboard_api,
            self.test_webhook,
            self.test_report_creation,
            self.test_notification_api
        ]
        
        results = []
        start_time = time.time()
        
        for test in tests:
            try:
                result = test()
                results.append(result)
                time.sleep(0.5)  # Pausa entre tests
            except Exception as e:
                print(f"❌ Test failed with exception: {str(e)}")
                results.append(False)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Resumen
        print("\n" + "=" * 50)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 50)
        
        passed = sum(results)
        total = len(results)
        
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        print(f"⏱️ Duration: {duration:.2f} seconds")
        print(f"📈 Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED! Cascade integration is ready!")
        else:
            print(f"\n⚠️ {total - passed} tests failed. Check the errors above.")
        
        return passed == total

def main():
    """🚀 Función principal"""
    print("🤖 Cascade Integration Test Client")
    print("=" * 50)
    
    # Configuración - ACTUALIZAR CON TUS DATOS
    BASE_URL = "https://tuusuario.pythonanywhere.com"  # ⚠️ CAMBIAR AQUÍ
    API_KEY = "tu_api_key_aqui"  # ⚠️ CAMBIAR AQUÍ
    
    if BASE_URL == "https://tuusuario.pythonanywhere.com":
        print("⚠️ WARNING: Please update BASE_URL with your PythonAnywhere URL")
        print("⚠️ WARNING: Please update API_KEY with your actual API key")
        print("\nExample:")
        print("BASE_URL = 'https://miusuario.pythonanywhere.com'")
        print("API_KEY = 'mi_api_key_secreta'")
        return
    
    # Crear cliente de pruebas
    client = CascadeTestClient(BASE_URL, API_KEY)
    
    # Ejecutar pruebas
    success = client.run_all_tests()
    
    if success:
        print("\n🎯 NEXT STEPS:")
        print("1. Configure Cascade to use these endpoints")
        print("2. Set up monitoring and alerts")
        print("3. Test with real data")
        print("4. Deploy to production")
    else:
        print("\n🔧 TROUBLESHOOTING:")
        print("1. Check your PythonAnywhere app is running")
        print("2. Verify API_KEY is correct")
        print("3. Check Django logs for errors")
        print("4. Ensure URLs are properly configured")

if __name__ == "__main__":
    main()

# =============================================================================
# 🧪 TESTS INDIVIDUALES - Ejecutar por separado si es necesario
# =============================================================================

def test_individual_endpoint():
    """🔍 Probar un endpoint específico"""
    BASE_URL = "https://tuusuario.pythonanywhere.com"
    API_KEY = "tu_api_key_aqui"
    
    client = CascadeTestClient(BASE_URL, API_KEY)
    
    # Probar solo health check
    client.test_health_check()

def test_with_custom_data():
    """📊 Probar con datos personalizados"""
    BASE_URL = "https://tuusuario.pythonanywhere.com"
    API_KEY = "tu_api_key_aqui"
    
    client = CascadeTestClient(BASE_URL, API_KEY)
    
    # Probar con fecha específica
    print("🧪 Testing with custom date...")
    try:
        params = {
            'fecha': '2024-01-15',  # Fecha específica
            'modulo_id': 1          # Módulo específico
        }
        
        response = client.session.get(
            f"{BASE_URL}/api/cascade/utensilios/",
            params=params
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Custom data test OK: {len(data['data'])} records")
        else:
            print(f"❌ Custom data test failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Custom data test error: {str(e)}")

# Ejemplo de uso:
# python cascade_test_client.py
