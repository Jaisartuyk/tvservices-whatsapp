#!/usr/bin/env python
"""
Script para poblar datos iniciales en Railway PostgreSQL
"""
import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno de Railway
load_dotenv('.env.railway')

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tvservices.settings')

import django
django.setup()

from django.contrib.auth.models import User
from subscriptions.models import Service, CategoriaServicio, Cliente, Subscription
from datetime import date, timedelta

def populate_railway_data():
    """Poblar datos iniciales en Railway"""
    
    print("🚀 Poblando datos en Railway PostgreSQL...")
    
    try:
        # 1. Crear categoría
        streaming_cat, created = CategoriaServicio.objects.get_or_create(
            nombre="Streaming",
            defaults={'descripcion': 'Servicios de streaming de video'}
        )
        print(f"✅ Categoría Streaming: {'creada' if created else 'ya existe'}")
        
        # 2. Crear servicios
        services_data = [
            {'nombre': 'Netflix', 'nombre_mostrar': 'Netflix', 'precio_base': 12.99},
            {'nombre': 'HBO Max', 'nombre_mostrar': 'HBO Max', 'precio_base': 9.99},
            {'nombre': 'Disney Plus', 'nombre_mostrar': 'Disney+', 'precio_base': 7.99},
            {'nombre': 'Amazon Prime', 'nombre_mostrar': 'Amazon Prime Video', 'precio_base': 8.99},
            {'nombre': 'Paramount Plus', 'nombre_mostrar': 'Paramount+', 'precio_base': 5.99}
        ]
        
        created_services = []
        for service_data in services_data:
            service, created = Service.objects.get_or_create(
                nombre=service_data['nombre'],
                defaults={
                    'nombre_mostrar': service_data['nombre_mostrar'],
                    'precio_base': service_data['precio_base'],
                    'descripcion': f'Servicio de streaming de {service_data["nombre_mostrar"]}',
                    'categoria': streaming_cat,
                    'is_active': True
                }
            )
            created_services.append(service)
            print(f"✅ Servicio {service.nombre_mostrar}: {'creado' if created else 'ya existe'}")
        
        # 3. Crear superusuario
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@tvservices.com',
                'is_superuser': True,
                'is_staff': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            print("✅ Superusuario 'admin' creado")
        else:
            print("✅ Superusuario 'admin' ya existe")
        
        # 4. Crear clientes de ejemplo
        clientes_data = [
            {
                'nombres': 'María', 'apellidos': 'González',
                'email': 'maria.gonzalez@email.com',
                'telefono': '+593987654321',
                'direccion': 'Quito, Ecuador',
                'fecha_nacimiento': date(1990, 5, 15)
            },
            {
                'nombres': 'Carlos', 'apellidos': 'Pérez',
                'email': 'carlos.perez@email.com',
                'telefono': '+593976543210',
                'direccion': 'Guayaquil, Ecuador',
                'fecha_nacimiento': date(1985, 8, 22)
            },
            {
                'nombres': 'Ana', 'apellidos': 'López',
                'email': 'ana.lopez@email.com',
                'telefono': '+593965432109',
                'direccion': 'Cuenca, Ecuador',
                'fecha_nacimiento': date(1992, 12, 3)
            }
        ]
        
        created_clients = []
        for cliente_data in clientes_data:
            cliente, created = Cliente.objects.get_or_create(
                email=cliente_data['email'],
                defaults={
                    **cliente_data,
                    'creado_por': admin_user,
                    'is_active': True
                }
            )
            created_clients.append(cliente)
            print(f"✅ Cliente {cliente.nombre_completo}: {'creado' if created else 'ya existe'}")
        
        # 5. Crear suscripciones de ejemplo
        if created_clients and created_services:
            suscripciones_data = [
                {
                    'cliente': created_clients[0], 'service': created_services[0],
                    'start_date': date.today() - timedelta(days=20),
                    'end_date': date.today() + timedelta(days=10),
                    'price': 12.99, 'payment_method': 'Tarjeta de Crédito'
                },
                {
                    'cliente': created_clients[1], 'service': created_services[1],
                    'start_date': date.today() - timedelta(days=15),
                    'end_date': date.today() + timedelta(days=3),
                    'price': 9.99, 'payment_method': 'PayPal'
                },
                {
                    'cliente': created_clients[2], 'service': created_services[2],
                    'start_date': date.today() - timedelta(days=25),
                    'end_date': date.today() + timedelta(days=1),
                    'price': 7.99, 'payment_method': 'Transferencia'
                }
            ]
            
            for sub_data in suscripciones_data:
                subscription, created = Subscription.objects.get_or_create(
                    cliente=sub_data['cliente'],
                    service=sub_data['service'],
                    defaults={
                        **sub_data,
                        'is_active': True
                    }
                )
                if created:
                    print(f"✅ Suscripción {subscription.service.nombre_mostrar} para {subscription.cliente.nombre_completo} creada")
        
        # 6. Mostrar resumen
        print("\n🎉 ¡Datos poblados exitosamente!")
        print(f"📊 Resumen:")
        print(f"   • Servicios: {Service.objects.count()}")
        print(f"   • Clientes: {Cliente.objects.count()}")
        print(f"   • Suscripciones: {Subscription.objects.count()}")
        print(f"   • Usuarios admin: {User.objects.filter(is_superuser=True).count()}")
        
        print("\n🔑 Acceso admin:")
        print("   URL: https://tvservices-whatsapp-production.up.railway.app/admin/")
        print("   Usuario: admin")
        print("   Contraseña: admin123")
        
        return True
        
    except Exception as e:
        print(f"❌ Error poblando datos: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = populate_railway_data()
    if not success:
        sys.exit(1)
