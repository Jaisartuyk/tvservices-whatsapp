#!/usr/bin/env python
"""
Script para crear datos iniciales de servicios de streaming
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tvservices.settings')
django.setup()

from subscriptions.models import Service

def create_initial_services():
    """Crear servicios iniciales si no existen"""
    
    services_data = [
        {
            'name': 'netflix',
            'display_name': 'Netflix',
            'price': 15.99,
            'description': 'Películas y series originales, contenido en 4K'
        },
        {
            'name': 'hbo_max',
            'display_name': 'HBO Max',
            'price': 14.99,
            'description': 'Contenido premium de HBO, Warner Bros y DC'
        },
        {
            'name': 'disney_plus',
            'display_name': 'Disney+',
            'price': 12.99,
            'description': 'Disney, Pixar, Marvel, Star Wars y National Geographic'
        },
        {
            'name': 'amazon_prime',
            'display_name': 'Amazon Prime Video',
            'price': 8.99,
            'description': 'Contenido original de Amazon y películas populares'
        },
        {
            'name': 'apple_tv',
            'display_name': 'Apple TV+',
            'price': 6.99,
            'description': 'Contenido original de Apple con calidad cinematográfica'
        }
    ]
    
    created_count = 0
    
    for service_data in services_data:
        service, created = Service.objects.get_or_create(
            name=service_data['name'],
            defaults={
                'display_name': service_data['display_name'],
                'price': service_data['price'],
                'description': service_data['description'],
                'active': True
            }
        )
        
        if created:
            created_count += 1
            print(f"✅ Creado: {service.display_name} - ${service.price}")
        else:
            print(f"ℹ️  Ya existe: {service.display_name}")
    
    print(f"\n🎉 Proceso completado. {created_count} servicios nuevos creados.")
    print(f"📊 Total de servicios activos: {Service.objects.filter(active=True).count()}")

if __name__ == '__main__':
    print("🚀 Creando datos iniciales para TV Services...\n")
    create_initial_services()
