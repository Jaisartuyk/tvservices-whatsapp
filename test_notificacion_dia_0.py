#!/usr/bin/env python
"""
Script para probar notificaciones del día 0 (vence hoy)
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
from django.contrib.auth.models import User

def create_test_subscription_today():
    """Crea una suscripción que vence HOY para probar"""
    print("📊 Creando suscripción de prueba que vence HOY...")
    
    # Crear o obtener un servicio
    service, created = Service.objects.get_or_create(
        nombre='Netflix Día 0',
        defaults={
            'nombre_mostrar': 'Netflix Premium - Vence Hoy',
            'descripcion': 'Servicio de prueba para notificación día 0',
            'precio_base': 15.99,
            'is_active': True
        }
    )
    
    # Crear o obtener usuario admin
    user, _ = User.objects.get_or_create(
        username='admin',
        defaults={'is_staff': True, 'is_superuser': True}
    )
    
    # Crear o obtener cliente de prueba
    cliente, created = Cliente.objects.get_or_create(
        nombres='Cliente',
        apellidos='Día Cero Ecuador',
        defaults={
            'email': 'dia0@tvservices.com',
            'telefono': '0968196046',  # Tu número de Ecuador
            'creado_por': user,
            'is_active': True
        }
    )
    
    if created:
        print(f"✅ Cliente creado: {cliente.nombre_completo}")
    else:
        print(f"📋 Usando cliente existente: {cliente.nombre_completo}")
        # Actualizar teléfono
        cliente.telefono = '0968196046'
        cliente.save()
    
    # Crear suscripción que vence HOY
    today = date.today()
    
    subscription, created = Subscription.objects.get_or_create(
        cliente=cliente,
        service=service,
        defaults={
            'price': service.precio_base,
            'start_date': today - timedelta(days=30),
            'end_date': today,  # Vence HOY
            'is_active': True,
            'payment_status': 'paid'
        }
    )
    
    if created:
        print(f"✅ Suscripción creada que vence HOY: {subscription.end_date}")
    else:
        print(f"📋 Actualizando suscripción existente para que venza HOY")
        # Actualizar fecha para que venza hoy
        subscription.end_date = today
        subscription.is_active = True
        subscription.save()
        print(f"✅ Suscripción actualizada que vence HOY: {subscription.end_date}")
    
    return cliente, service, subscription

def test_notification_day_0():
    """Prueba la notificación para día 0"""
    print("\n🚨 PROBANDO NOTIFICACIÓN DÍA 0 (VENCE HOY)")
    print("=" * 60)
    
    cliente, service, subscription = create_test_subscription_today()
    
    # Verificar que efectivamente vence hoy
    days_remaining = subscription.days_remaining
    print(f"📅 Días restantes: {days_remaining}")
    
    if days_remaining != 0:
        print(f"⚠️ Advertencia: La suscripción no vence hoy (días restantes: {days_remaining})")
        print("🔧 Ajustando fecha de vencimiento...")
        subscription.end_date = date.today()
        subscription.save()
        print("✅ Fecha ajustada para que venza hoy")
    
    # Probar envío de notificación día 0
    notification_service = NotificationService()
    
    print(f"\n📱 Enviando notificación DÍA 0 a: {cliente.telefono}")
    print(f"🎯 Cliente: {cliente.nombre_completo}")
    print(f"📺 Servicio: {service.nombre_mostrar}")
    print(f"📅 Vence: {subscription.end_date} (HOY)")
    
    # Crear el mensaje para mostrar preview
    message = notification_service._create_expiration_message(subscription, 0)
    print(f"\n💬 MENSAJE A ENVIAR:")
    print("-" * 50)
    print(message)
    print("-" * 50)
    
    # Enviar la notificación
    result = notification_service.send_expiration_notification(subscription, 0)
    
    if result['success']:
        print("\n✅ ¡NOTIFICACIÓN DÍA 0 ENVIADA EXITOSAMENTE!")
        
        # Verificar que se creó el registro en la base de datos
        notification_log = NotificationLog.objects.filter(
            subscription=subscription,
            notification_type='expiration_warning'
        ).order_by('-created_at').first()
        
        if notification_log:
            print(f"📋 Registro creado en BD: ID {notification_log.id}")
            print(f"📊 Estado: {notification_log.get_status_display()}")
            print(f"🕐 Enviado: {notification_log.sent_at}")
            print(f"📱 Teléfono: {notification_log.phone_number}")
        
        return True
    else:
        print(f"\n❌ Error enviando notificación día 0: {result.get('error')}")
        return False

def test_command_day_0():
    """Prueba el comando de Django para día 0"""
    print("\n⚙️ PROBANDO COMANDO DJANGO PARA DÍA 0")
    print("=" * 60)
    
    import subprocess
    
    try:
        # Ejecutar comando para día 0 en modo dry-run
        print("🧪 Ejecutando en modo DRY-RUN...")
        result = subprocess.run([
            sys.executable, 'manage.py', 'send_expiration_notifications', 
            '--days', '0', '--dry-run'
        ], capture_output=True, text=True, timeout=30)
        
        print("📊 Salida del comando (dry-run):")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Errores:")
            print(result.stderr)
        
        # Ejecutar comando real para día 0
        print("\n🚀 Ejecutando envío REAL...")
        result = subprocess.run([
            sys.executable, 'manage.py', 'send_expiration_notifications', 
            '--days', '0'
        ], capture_output=True, text=True, timeout=30)
        
        print("📊 Salida del comando (real):")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Errores:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error ejecutando comando: {str(e)}")
        return False

def show_day_0_statistics():
    """Muestra estadísticas específicas del día 0"""
    print("\n📈 ESTADÍSTICAS DÍA 0")
    print("=" * 60)
    
    # Notificaciones día 0
    day_0_notifications = NotificationLog.objects.filter(
        notification_type='expiration_warning',
        message__icontains='vence ¡HOY!'
    )
    
    total_day_0 = day_0_notifications.count()
    successful_day_0 = day_0_notifications.filter(status='sent').count()
    
    print(f"📊 Total notificaciones día 0: {total_day_0}")
    print(f"✅ Exitosas día 0: {successful_day_0}")
    
    if total_day_0 > 0:
        success_rate = (successful_day_0 / total_day_0) * 100
        print(f"📈 Tasa de éxito día 0: {success_rate:.1f}%")
    
    # Suscripciones que vencen hoy
    today = date.today()
    subscriptions_today = Subscription.objects.filter(
        end_date=today,
        is_active=True
    )
    
    print(f"\n📅 Suscripciones que vencen HOY: {subscriptions_today.count()}")
    
    for sub in subscriptions_today:
        print(f"  • {sub.cliente.nombre_completo} - {sub.service.nombre_mostrar}")

def main():
    """Función principal"""
    print("🚨 PRUEBA COMPLETA DE NOTIFICACIONES DÍA 0")
    print("=" * 60)
    
    success_count = 0
    total_tests = 3
    
    # Prueba 1: Notificación directa día 0
    print("🚨 PRUEBA 1: Notificación Directa Día 0")
    print("-" * 40)
    if test_notification_day_0():
        success_count += 1
        print("✅ Prueba 1 EXITOSA")
    else:
        print("❌ Prueba 1 FALLIDA")
    
    # Prueba 2: Comando Django día 0
    print("\n⚙️ PRUEBA 2: Comando Django Día 0")
    print("-" * 40)
    if test_command_day_0():
        success_count += 1
        print("✅ Prueba 2 EXITOSA")
    else:
        print("❌ Prueba 2 FALLIDA")
    
    # Prueba 3: Estadísticas día 0
    print("\n📈 PRUEBA 3: Estadísticas Día 0")
    print("-" * 40)
    try:
        show_day_0_statistics()
        success_count += 1
        print("✅ Prueba 3 EXITOSA")
    except Exception as e:
        print(f"❌ Prueba 3 FALLIDA: {str(e)}")
    
    # Resumen final
    print("\n" + "=" * 60)
    print("🎯 RESUMEN DE PRUEBAS DÍA 0")
    print("=" * 60)
    print(f"✅ Pruebas exitosas: {success_count}/{total_tests}")
    print(f"❌ Pruebas fallidas: {total_tests - success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("\n🎉 ¡TODAS LAS PRUEBAS DÍA 0 EXITOSAS!")
        print("🚨 El sistema de notificaciones día 0 está completamente funcional.")
        print("📱 Revisa tu WhatsApp para confirmar la recepción del mensaje.")
        print("\n📋 Configuración recomendada para automatización:")
        print("# Cron para notificaciones múltiples (incluyendo día 0)")
        print("0 9 * * * cd /proyecto && python manage.py send_expiration_notifications --days 0")
        print("0 9 * * * cd /proyecto && python manage.py send_expiration_notifications --days 1")
        print("0 9 * * * cd /proyecto && python manage.py send_expiration_notifications --days 3")
        print("0 9 * * * cd /proyecto && python manage.py send_expiration_notifications --days 7")
    else:
        print("\n⚠️ Algunas pruebas fallaron. Revisa los errores arriba.")
    
    return success_count == total_tests

if __name__ == "__main__":
    main()
