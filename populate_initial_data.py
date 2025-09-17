#!/usr/bin/env python
"""
Script para poblar datos iniciales en la base de datos de producción
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tvservices.settings')
django.setup()

from django.contrib.auth.models import User
from subscriptions.models import Service, CategoriaServicio, Cliente, Subscription
from datetime import date, timedelta

def create_initial_data():
    """Crear datos iniciales básicos"""
    
    print("🔄 Creando datos iniciales...")
    
    # 1. Crear categorías de servicios
    streaming_cat, created = CategoriaServicio.objects.get_or_create(
        nombre="Streaming",
        defaults={'descripcion': 'Servicios de streaming de video'}
    )
    if created:
        print("✅ Categoría Streaming creada")
    
    # 2. Crear servicios básicos
    services_data = [
        {
            'nombre': 'Netflix',
            'nombre_mostrar': 'Netflix',
            'precio_base': 12.99,
            'descripcion': 'Servicio de streaming de Netflix',
            'categoria': streaming_cat,
            'is_active': True
        },
        {
            'nombre': 'HBO Max',
            'nombre_mostrar': 'HBO Max',
            'precio_base': 9.99,
            'descripcion': 'Servicio de streaming de HBO Max',
            'categoria': streaming_cat,
            'is_active': True
        },
        {
            'nombre': 'Disney Plus',
            'nombre_mostrar': 'Disney+',
            'precio_base': 7.99,
            'descripcion': 'Servicio de streaming de Disney Plus',
            'categoria': streaming_cat,
            'is_active': True
        },
        {
            'nombre': 'Amazon Prime',
            'nombre_mostrar': 'Amazon Prime Video',
            'precio_base': 8.99,
            'descripcion': 'Servicio de streaming de Amazon Prime',
            'categoria': streaming_cat,
            'is_active': True
        },
        {
            'nombre': 'Paramount Plus',
            'nombre_mostrar': 'Paramount+',
            'precio_base': 5.99,
            'descripcion': 'Servicio de streaming de Paramount Plus',
            'categoria': streaming_cat,
            'is_active': True
        }
    ]
    
    created_services = []
    for service_data in services_data:
        service, created = Service.objects.get_or_create(
            nombre=service_data['nombre'],
            defaults=service_data
        )
        if created:
            print(f"✅ Servicio {service.nombre_mostrar} creado")
        created_services.append(service)
    
    # 3. Crear superusuario si no existe
    if not User.objects.filter(username='admin').exists():
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@tvservices.com',
            password='admin123'
        )
        print("✅ Superusuario 'admin' creado")
        print("   Usuario: admin")
        print("   Contraseña: admin123")
    else:
        admin_user = User.objects.get(username='admin')
        print("ℹ️  Superusuario 'admin' ya existe")
    
    # 4. Crear algunos clientes de ejemplo
    clientes_data = [
        {
            'nombres': 'María',
            'apellidos': 'González',
            'email': 'maria.gonzalez@email.com',
            'telefono': '+593987654321',
            'direccion': 'Quito, Ecuador',
            'fecha_nacimiento': date(1990, 5, 15),
            'creado_por': admin_user,
            'is_active': True
        },
        {
            'nombres': 'Carlos',
            'apellidos': 'Pérez',
            'email': 'carlos.perez@email.com',
            'telefono': '+593976543210',
            'direccion': 'Guayaquil, Ecuador',
            'fecha_nacimiento': date(1985, 8, 22),
            'creado_por': admin_user,
            'is_active': True
        },
        {
            'nombres': 'Ana',
            'apellidos': 'López',
            'email': 'ana.lopez@email.com',
            'telefono': '+593965432109',
            'direccion': 'Cuenca, Ecuador',
            'fecha_nacimiento': date(1992, 12, 3),
            'creado_por': admin_user,
            'is_active': True
        }
    ]
    
    created_clients = []
    for cliente_data in clientes_data:
        cliente, created = Cliente.objects.get_or_create(
            email=cliente_data['email'],
            defaults=cliente_data
        )
        if created:
            print(f"✅ Cliente {cliente.nombre_completo} creado")
        created_clients.append(cliente)
    
    # 5. Crear algunas suscripciones de ejemplo
    if created_clients and created_services:
        suscripciones_data = [
            {
                'cliente': created_clients[0],  # María
                'service': created_services[0],  # Netflix
                'start_date': date.today() - timedelta(days=20),
                'end_date': date.today() + timedelta(days=10),  # Vence en 10 días
                'price': 12.99,
                'payment_method': 'Tarjeta de Crédito',
                'is_active': True
            },
            {
                'cliente': created_clients[1],  # Carlos
                'service': created_services[1],  # HBO Max
                'start_date': date.today() - timedelta(days=15),
                'end_date': date.today() + timedelta(days=3),  # Vence en 3 días
                'price': 9.99,
                'payment_method': 'PayPal',
                'is_active': True
            },
            {
                'cliente': created_clients[2],  # Ana
                'service': created_services[2],  # Disney+
                'start_date': date.today() - timedelta(days=25),
                'end_date': date.today() + timedelta(days=1),  # Vence mañana
                'price': 7.99,
                'payment_method': 'Transferencia',
                'is_active': True
            }
        ]
        
        for sub_data in suscripciones_data:
            subscription, created = Subscription.objects.get_or_create(
                cliente=sub_data['cliente'],
                service=sub_data['service'],
                defaults=sub_data
            )
            if created:
                print(f"✅ Suscripción {subscription.service.nombre_mostrar} para {subscription.cliente.nombre_completo} creada")
    
    print("\n🎉 ¡Datos iniciales creados exitosamente!")
    print("\n📊 Resumen:")
    print(f"   • Servicios: {Service.objects.count()}")
    print(f"   • Clientes: {Cliente.objects.count()}")
    print(f"   • Suscripciones: {Subscription.objects.count()}")
    print(f"   • Usuarios admin: {User.objects.filter(is_superuser=True).count()}")
    
    print("\n🔑 Acceso admin:")
    print("   URL: https://tvservices-whatsapp-production.up.railway.app/admin/")
    print("   Usuario: admin")
    print("   Contraseña: admin123")

if __name__ == '__main__':
    create_initial_data()
