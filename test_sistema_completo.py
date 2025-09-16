#!/usr/bin/env python
"""
Prueba completa del sistema de notificaciones de WhatsApp
"""

import os
import sys
import django
from pathlib import Path
from datetime import date, timedelta

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tvservices.settings')
django.setup()

from subscriptions.services import NotificationService
from subscriptions.models import Cliente, Service, Subscription, NotificationLog

def create_test_data():
    """Crea datos de prueba para el sistema"""
    print("📊 Creando datos de prueba...")
    
    # Crear o obtener un servicio
    service, created = Service.objects.get_or_create(
        nombre='Netflix Test',
        defaults={
            'nombre_mostrar': 'Netflix Premium Test',
            'descripcion': 'Servicio de prueba para notificaciones',
            'precio_base': 15.99,
            'is_active': True
        }
    )
    
    if created:
        print(f"✅ Servicio creado: {service.nombre_mostrar}")
    else:
        print(f"📋 Usando servicio existente: {service.nombre_mostrar}")
    
    # Crear o obtener un cliente de prueba
    from django.contrib.auth.models import User
    user, _ = User.objects.get_or_create(
        username='admin',
        defaults={'is_staff': True, 'is_superuser': True}
    )
    
    cliente, created = Cliente.objects.get_or_create(
        nombres='Usuario',
        apellidos='Prueba Ecuador',
        defaults={
            'email': 'prueba@tvservices.com',
            'telefono': '0968196046',  # Tu número de Ecuador
            'creado_por': user,
            'is_active': True
        }
    )
    
    if created:
        print(f"✅ Cliente creado: {cliente.nombre_completo}")
    else:
        print(f"📋 Usando cliente existente: {cliente.nombre_completo}")
        # Actualizar teléfono si es necesario
        cliente.telefono = '0968196046'
        cliente.save()
    
    # Crear suscripción que vence mañana
    tomorrow = date.today() + timedelta(days=1)
    
    subscription, created = Subscription.objects.get_or_create(
        cliente=cliente,
        service=service,
        defaults={
            'price': service.precio_base,
            'start_date': date.today() - timedelta(days=29),
            'end_date': tomorrow,
            'is_active': True,
            'payment_status': 'paid'
        }
    )
    
    if created:
        print(f"✅ Suscripción creada que vence: {subscription.end_date}")
    else:
        print(f"📋 Usando suscripción existente que vence: {subscription.end_date}")
        # Actualizar fecha para que venza mañana
        subscription.end_date = tomorrow
        subscription.save()
    
    return cliente, service, subscription

def test_notification_service():
    """Prueba el servicio de notificaciones completo"""
    print("\n🔔 Probando servicio de notificaciones...")
    
    cliente, service, subscription = create_test_data()
    
    # Probar envío de notificación de vencimiento
    notification_service = NotificationService()
    
    print(f"📱 Enviando notificación a: {cliente.telefono}")
    print(f"🎯 Cliente: {cliente.nombre_completo}")
    print(f"📺 Servicio: {service.nombre_mostrar}")
    print(f"📅 Vence: {subscription.end_date}")
    
    result = notification_service.send_expiration_notification(subscription, 1)
    
    if result['success']:
        print("✅ ¡Notificación enviada exitosamente!")
        
        # Verificar que se creó el registro en la base de datos
        notification_log = NotificationLog.objects.filter(
            subscription=subscription
        ).order_by('-created_at').first()
        
        if notification_log:
            print(f"📋 Registro creado en BD: {notification_log}")
            print(f"📊 Estado: {notification_log.get_status_display()}")
            print(f"🕐 Enviado: {notification_log.sent_at}")
        
        return True
    else:
        print(f"❌ Error enviando notificación: {result.get('error')}")
        return False

def test_management_command():
    """Prueba el comando de Django"""
    print("\n⚙️ Probando comando de Django...")
    
    import subprocess
    
    try:
        # Ejecutar comando en modo dry-run
        result = subprocess.run([
            sys.executable, 'manage.py', 'send_expiration_notifications', 
            '--days', '1', '--dry-run'
        ], capture_output=True, text=True, timeout=30)
        
        print("📊 Salida del comando:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Errores:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error ejecutando comando: {str(e)}")
        return False

def show_statistics():
    """Muestra estadísticas del sistema"""
    print("\n📈 Estadísticas del sistema:")
    
    total_notifications = NotificationLog.objects.count()
    successful_notifications = NotificationLog.objects.filter(status='sent').count()
    failed_notifications = NotificationLog.objects.filter(status='failed').count()
    
    print(f"📊 Total de notificaciones: {total_notifications}")
    print(f"✅ Exitosas: {successful_notifications}")
    print(f"❌ Fallidas: {failed_notifications}")
    
    if total_notifications > 0:
        success_rate = (successful_notifications / total_notifications) * 100
        print(f"📈 Tasa de éxito: {success_rate:.1f}%")
    
    # Mostrar últimas notificaciones
    recent_notifications = NotificationLog.objects.order_by('-created_at')[:5]
    
    if recent_notifications:
        print(f"\n📋 Últimas {len(recent_notifications)} notificaciones:")
        for notif in recent_notifications:
            status_icon = "✅" if notif.status == 'sent' else "❌"
            print(f"  {status_icon} {notif.cliente_name} - {notif.get_notification_type_display()} - {notif.created_at.strftime('%d/%m/%Y %H:%M')}")

def main():
    """Función principal de prueba"""
    print("🧪 PRUEBA COMPLETA DEL SISTEMA DE NOTIFICACIONES")
    print("=" * 60)
    
    success_count = 0
    total_tests = 3
    
    # Prueba 1: Servicio de notificaciones
    print("🔔 PRUEBA 1: Servicio de Notificaciones")
    print("-" * 40)
    if test_notification_service():
        success_count += 1
        print("✅ Prueba 1 EXITOSA")
    else:
        print("❌ Prueba 1 FALLIDA")
    
    # Prueba 2: Comando de Django
    print("\n⚙️ PRUEBA 2: Comando de Django")
    print("-" * 40)
    if test_management_command():
        success_count += 1
        print("✅ Prueba 2 EXITOSA")
    else:
        print("❌ Prueba 2 FALLIDA")
    
    # Prueba 3: Estadísticas
    print("\n📈 PRUEBA 3: Estadísticas y Registros")
    print("-" * 40)
    try:
        show_statistics()
        success_count += 1
        print("✅ Prueba 3 EXITOSA")
    except Exception as e:
        print(f"❌ Prueba 3 FALLIDA: {str(e)}")
    
    # Resumen final
    print("\n" + "=" * 60)
    print("🎯 RESUMEN DE PRUEBAS")
    print("=" * 60)
    print(f"✅ Pruebas exitosas: {success_count}/{total_tests}")
    print(f"❌ Pruebas fallidas: {total_tests - success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("\n🎉 ¡TODAS LAS PRUEBAS EXITOSAS!")
        print("🚀 El sistema de notificaciones está completamente funcional.")
        print("📱 Revisa tu WhatsApp para confirmar la recepción del mensaje.")
        print("\n📋 Próximos pasos:")
        print("1. Configurar automatización con cron/Task Scheduler")
        print("2. Agregar más clientes con números reales")
        print("3. Monitorear logs en Django Admin")
    else:
        print("\n⚠️ Algunas pruebas fallaron. Revisa los errores arriba.")
    
    return success_count == total_tests

if __name__ == "__main__":
    main()
