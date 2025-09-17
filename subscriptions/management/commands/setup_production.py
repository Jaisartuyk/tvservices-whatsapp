from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from subscriptions.models import Service, CategoriaServicio, Cliente, Subscription
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Setup production data for Railway deployment'

    def handle(self, *args, **options):
        self.stdout.write("🚀 Setting up production data...")
        
        try:
            # 1. Crear categoría
            streaming_cat, created = CategoriaServicio.objects.get_or_create(
                nombre="Streaming",
                defaults={'descripcion': 'Servicios de streaming de video'}
            )
            self.stdout.write(f"✅ Categoría Streaming: {'creada' if created else 'ya existe'}")
            
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
                self.stdout.write(f"✅ Servicio {service.nombre_mostrar}: {'creado' if created else 'ya existe'}")
            
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
                self.stdout.write("✅ Superusuario 'admin' creado")
            else:
                self.stdout.write("✅ Superusuario 'admin' ya existe")
            
            # 4. Crear clientes de ejemplo
            clientes_data = [
                {
                    'nombres': 'María', 'apellidos': 'González',
                    'email': 'maria.gonzalez@email.com',
                    'telefono': '+593968196046',  # Número real con WhatsApp
                    'direccion': 'Quito, Ecuador',
                    'fecha_nacimiento': date(1990, 5, 15)
                },
                {
                    'nombres': 'Carlos', 'apellidos': 'Pérez',
                    'email': 'carlos.perez@email.com',
                    'telefono': '+593968196046',  # Número real con WhatsApp
                    'direccion': 'Guayaquil, Ecuador',
                    'fecha_nacimiento': date(1985, 8, 22)
                },
                {
                    'nombres': 'Ana', 'apellidos': 'López',
                    'email': 'ana.lopez@email.com',
                    'telefono': '+593968196046',  # Número real con WhatsApp
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
                self.stdout.write(f"✅ Cliente {cliente.nombre_completo}: {'creado' if created else 'ya existe'}")
            
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
                        self.stdout.write(f"✅ Suscripción {subscription.service.nombre_mostrar} para {subscription.cliente.nombre_completo} creada")
            
            # 6. Mostrar resumen
            self.stdout.write("\n🎉 ¡Datos poblados exitosamente!")
            self.stdout.write(f"📊 Resumen:")
            self.stdout.write(f"   • Servicios: {Service.objects.count()}")
            self.stdout.write(f"   • Clientes: {Cliente.objects.count()}")
            self.stdout.write(f"   • Suscripciones: {Subscription.objects.count()}")
            self.stdout.write(f"   • Usuarios admin: {User.objects.filter(is_superuser=True).count()}")
            
            self.stdout.write("\n🔑 Acceso admin:")
            self.stdout.write("   Usuario: admin")
            self.stdout.write("   Contraseña: admin123")
            
        except Exception as e:
            self.stdout.write(f"❌ Error: {e}")
            raise e
