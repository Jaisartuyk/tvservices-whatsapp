"""
Management command para poblar datos del Call Center en Railway
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
import pytz

from callcenter.models import (
    Operador, Producto, Lead, Conversacion, LlamadaIA, Venta,
    TipoServicio, ClasificacionLead, EstadoLead, FuenteLead,
    CanalConversacion, TipoConversacion, SentimientoConversacion,
    ResultadoLlamada, EstadoVenta
)

ECUADOR_TZ = pytz.timezone('America/Guayaquil')


class Command(BaseCommand):
    help = 'Pobla la base de datos con datos de ejemplo para Ecuador'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🇪🇨 Poblando datos de Call Center para Ecuador...'))
        
        # Crear operadores
        self.stdout.write('📱 Creando operadores...')
        operadores_data = [
            {
                'nombre': 'Claro Ecuador',
                'color_principal': '#E30613',
                'sitio_web': 'https://www.claro.com.ec',
                'telefono_atencion': '*611',
                'orden': 1
            },
            {
                'nombre': 'Movistar Ecuador',
                'color_principal': '#019DF4',
                'sitio_web': 'https://www.movistar.com.ec',
                'telefono_atencion': '*150',
                'orden': 2
            },
            {
                'nombre': 'CNT',
                'color_principal': '#0066CC',
                'sitio_web': 'https://www.cnt.gob.ec',
                'telefono_atencion': '1800-266-826',
                'orden': 3
            },
            {
                'nombre': 'Tuenti Ecuador',
                'color_principal': '#00D9FF',
                'sitio_web': 'https://www.tuenti.ec',
                'telefono_atencion': '*611',
                'orden': 4
            },
        ]
        
        operadores = []
        for data in operadores_data:
            operador, created = Operador.objects.get_or_create(
                nombre=data['nombre'],
                defaults=data
            )
            operadores.append(operador)
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✅ {operador.nombre}'))
        
        # Crear productos
        self.stdout.write('📦 Creando productos...')
        productos_count = 0
        for operador in operadores:
            # Internet
            for velocidad, precio in [(20, 25), (50, 35), (100, 50)]:
                Producto.objects.get_or_create(
                    nombre_plan=f'{operador.nombre} Internet {velocidad} Mbps',
                    defaults={
                        'operador': operador,
                        'tipo': TipoServicio.INTERNET,
                        'velocidad_mbps': velocidad,
                        'precio_mensual': Decimal(str(precio)),
                        'precio_instalacion': Decimal('0.00'),
                        'descuento_porcentaje': Decimal('15.00'),
                        'beneficios': [f'{velocidad} Mbps', 'Router WiFi', 'Instalación gratis'],
                        'zonas_disponibles': 'Guayaquil, Quito, Cuenca',
                        'is_destacado': velocidad == 50,
                    }
                )
                productos_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✅ {productos_count} productos creados'))
        
        # Crear admin user
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@callcenter.ec',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if not admin_user.has_usable_password():
            admin_user.set_password('admin123')
            admin_user.save()
        
        # Crear leads
        self.stdout.write('👥 Creando leads...')
        ahora = timezone.now().astimezone(ECUADOR_TZ)
        
        leads_data = [
            {
                'nombre': 'Carlos',
                'apellido': 'Mendoza',
                'telefono': '+593987654321',
                'email': 'carlos.mendoza@email.com',
                'zona': 'Urdesa, Guayaquil',
                'tipo_servicio_interes': TipoServicio.INTERNET,
                'presupuesto_estimado': Decimal('35.00'),
                'score': 95,
                'clasificacion': ClasificacionLead.HOT,
                'estado': EstadoLead.NEGOCIANDO,
                'fuente': FuenteLead.WHATSAPP,
                'agente_asignado': admin_user,
                'notas': 'Cliente muy interesado',
                'ultima_interaccion': ahora - timedelta(hours=2),
            },
            {
                'nombre': 'María',
                'apellido': 'Rodríguez',
                'telefono': '+593987654322',
                'email': 'maria.rodriguez@email.com',
                'zona': 'La Carolina, Quito',
                'tipo_servicio_interes': TipoServicio.COMBO,
                'presupuesto_estimado': Decimal('60.00'),
                'score': 90,
                'clasificacion': ClasificacionLead.HOT,
                'estado': EstadoLead.CALIFICADO,
                'fuente': FuenteLead.LLAMADA_ENTRANTE,
                'agente_asignado': admin_user,
                'notas': 'Quiere combo completo',
                'ultima_interaccion': ahora - timedelta(hours=5),
            },
        ]
        
        for lead_data in leads_data:
            lead, created = Lead.objects.get_or_create(
                telefono=lead_data['telefono'],
                defaults=lead_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✅ {lead.nombre_completo}'))
        
        # Resumen
        self.stdout.write(self.style.SUCCESS('\n✅ Datos poblados exitosamente!'))
        self.stdout.write(f'📱 Operadores: {Operador.objects.count()}')
        self.stdout.write(f'📦 Productos: {Producto.objects.count()}')
        self.stdout.write(f'👥 Leads: {Lead.objects.count()}')
