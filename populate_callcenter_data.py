#!/usr/bin/env python
"""
Script para poblar la base de datos con datos de ejemplo del Call Center
Crea operadores, productos, leads y conversaciones de prueba
"""

import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tvservices.settings')
django.setup()

from django.contrib.auth.models import User
from callcenter.models import (
    Operador, Producto, Lead, Conversacion, LlamadaIA, Venta,
    TipoServicio, ClasificacionLead, EstadoLead, FuenteLead,
    CanalConversacion, TipoConversacion, SentimientoConversacion,
    ResultadoLlamada, EstadoVenta
)


def crear_operadores():
    """Crea los operadores de telecomunicaciones"""
    print("\n📱 Creando operadores...")
    
    operadores_data = [
        {
            'nombre': 'Claro',
            'color_principal': '#E30613',
            'sitio_web': 'https://www.claro.com.pe',
            'telefono_atencion': '123',
            'orden': 1
        },
        {
            'nombre': 'Movistar',
            'color_principal': '#019DF4',
            'sitio_web': 'https://www.movistar.com.pe',
            'telefono_atencion': '104',
            'orden': 2
        },
        {
            'nombre': 'Entel',
            'color_principal': '#0033A0',
            'sitio_web': 'https://www.entel.pe',
            'telefono_atencion': '106',
            'orden': 3
        },
        {
            'nombre': 'Bitel',
            'color_principal': '#FF6B00',
            'sitio_web': 'https://www.bitel.com.pe',
            'telefono_atencion': '611',
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
            print(f"  ✅ Creado: {operador.nombre}")
        else:
            print(f"  ℹ️  Ya existe: {operador.nombre}")
    
    return operadores


def crear_productos(operadores):
    """Crea productos de ejemplo para cada operador"""
    print("\n📦 Creando productos...")
    
    productos_creados = 0
    
    for operador in operadores:
        # Internet Hogar
        productos_internet = [
            {
                'nombre_plan': f'{operador.nombre} Internet 50 Mbps',
                'tipo': TipoServicio.INTERNET,
                'velocidad_mbps': 50,
                'precio_mensual': Decimal('35.00'),
                'precio_instalacion': Decimal('0.00'),
                'descuento_porcentaje': Decimal('10.00'),
                'beneficios': ['50 Mbps de velocidad', 'Router WiFi incluido', 'Instalación gratis'],
                'zonas_disponibles': 'Lima Metropolitana, Callao',
            },
            {
                'nombre_plan': f'{operador.nombre} Internet 100 Mbps',
                'tipo': TipoServicio.INTERNET,
                'velocidad_mbps': 100,
                'precio_mensual': Decimal('50.00'),
                'precio_instalacion': Decimal('0.00'),
                'descuento_porcentaje': Decimal('15.00'),
                'beneficios': ['100 Mbps de velocidad', 'Router WiFi Dual Band', 'Instalación gratis', 'Soporte 24/7'],
                'zonas_disponibles': 'Lima Metropolitana, Callao, Arequipa',
                'is_destacado': True,
            },
            {
                'nombre_plan': f'{operador.nombre} Internet 200 Mbps',
                'tipo': TipoServicio.INTERNET,
                'velocidad_mbps': 200,
                'precio_mensual': Decimal('70.00'),
                'precio_instalacion': Decimal('50.00'),
                'descuento_porcentaje': Decimal('20.00'),
                'beneficios': ['200 Mbps de velocidad', 'Router WiFi 6', 'Instalación gratis', 'Soporte premium 24/7', 'IP fija'],
                'zonas_disponibles': 'Lima Metropolitana, principales ciudades',
            },
        ]
        
        # Planes Móviles
        productos_movil = [
            {
                'nombre_plan': f'{operador.nombre} Móvil 10GB',
                'tipo': TipoServicio.MOVIL,
                'gigas_datos': 10,
                'minutos_llamadas': 500,
                'precio_mensual': Decimal('25.00'),
                'precio_instalacion': Decimal('0.00'),
                'beneficios': ['10 GB de datos', '500 minutos', 'Redes sociales ilimitadas'],
                'zonas_disponibles': 'Cobertura nacional',
            },
            {
                'nombre_plan': f'{operador.nombre} Móvil 20GB',
                'tipo': TipoServicio.MOVIL,
                'gigas_datos': 20,
                'minutos_llamadas': 1000,
                'precio_mensual': Decimal('35.00'),
                'precio_instalacion': Decimal('0.00'),
                'descuento_porcentaje': Decimal('10.00'),
                'beneficios': ['20 GB de datos', '1000 minutos', 'Redes sociales ilimitadas', 'WhatsApp ilimitado'],
                'zonas_disponibles': 'Cobertura nacional',
                'is_destacado': True,
            },
        ]
        
        # TV por Cable
        productos_tv = [
            {
                'nombre_plan': f'{operador.nombre} TV Básico',
                'tipo': TipoServicio.TV,
                'canales_tv': 80,
                'precio_mensual': Decimal('30.00'),
                'precio_instalacion': Decimal('50.00'),
                'beneficios': ['80 canales', 'HD incluido', 'Decodificador incluido'],
                'zonas_disponibles': 'Lima Metropolitana',
            },
        ]
        
        # Combos
        productos_combo = [
            {
                'nombre_plan': f'{operador.nombre} Combo Total',
                'tipo': TipoServicio.COMBO,
                'velocidad_mbps': 100,
                'canales_tv': 120,
                'minutos_llamadas': 1000,
                'precio_mensual': Decimal('90.00'),
                'precio_instalacion': Decimal('0.00'),
                'descuento_porcentaje': Decimal('25.00'),
                'beneficios': [
                    'Internet 100 Mbps',
                    '120 canales de TV',
                    'Telefonía fija ilimitada',
                    'Router WiFi incluido',
                    'Instalación gratis'
                ],
                'zonas_disponibles': 'Lima Metropolitana, Callao',
                'is_destacado': True,
            },
        ]
        
        # Crear todos los productos
        todos_productos = productos_internet + productos_movil + productos_tv + productos_combo
        
        for prod_data in todos_productos:
            prod_data['operador'] = operador
            producto, created = Producto.objects.get_or_create(
                nombre_plan=prod_data['nombre_plan'],
                defaults=prod_data
            )
            if created:
                productos_creados += 1
                print(f"  ✅ {producto.nombre_plan}")
    
    print(f"\n  Total productos creados: {productos_creados}")
    return Producto.objects.all()


def crear_leads(productos):
    """Crea leads de ejemplo"""
    print("\n👥 Creando leads...")
    
    # Obtener o crear usuario admin para asignar leads
    admin_user, _ = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@callcenter.com',
            'is_staff': True,
            'is_superuser': True
        }
    )
    
    leads_data = [
        # HOT LEADS
        {
            'nombre': 'Carlos',
            'apellido': 'Rodríguez',
            'telefono': '+51987654321',
            'email': 'carlos.rodriguez@email.com',
            'zona': 'San Isidro',
            'direccion': 'Av. Javier Prado 123',
            'tipo_servicio_interes': TipoServicio.INTERNET,
            'presupuesto_estimado': Decimal('50.00'),
            'score': 95,
            'clasificacion': ClasificacionLead.HOT,
            'estado': EstadoLead.NEGOCIANDO,
            'fuente': FuenteLead.WHATSAPP,
            'agente_asignado': admin_user,
            'notas': 'Cliente muy interesado, quiere contratar esta semana',
        },
        {
            'nombre': 'María',
            'apellido': 'González',
            'telefono': '+51987654322',
            'email': 'maria.gonzalez@email.com',
            'zona': 'Miraflores',
            'direccion': 'Calle Las Flores 456',
            'tipo_servicio_interes': TipoServicio.COMBO,
            'presupuesto_estimado': Decimal('90.00'),
            'score': 90,
            'clasificacion': ClasificacionLead.HOT,
            'estado': EstadoLead.CALIFICADO,
            'fuente': FuenteLead.LLAMADA_ENTRANTE,
            'agente_asignado': admin_user,
            'notas': 'Quiere combo completo, ya tiene fecha de instalación',
        },
        
        # WARM LEADS
        {
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'telefono': '+51987654323',
            'email': 'juan.perez@email.com',
            'zona': 'Surco',
            'tipo_servicio_interes': TipoServicio.MOVIL,
            'presupuesto_estimado': Decimal('35.00'),
            'score': 65,
            'clasificacion': ClasificacionLead.WARM,
            'estado': EstadoLead.CONTACTADO,
            'fuente': FuenteLead.WHATSAPP,
            'notas': 'Interesado en plan móvil, comparando precios',
        },
        {
            'nombre': 'Ana',
            'apellido': 'Torres',
            'telefono': '+51987654324',
            'email': 'ana.torres@email.com',
            'zona': 'La Molina',
            'tipo_servicio_interes': TipoServicio.INTERNET,
            'score': 55,
            'clasificacion': ClasificacionLead.WARM,
            'estado': EstadoLead.SEGUIMIENTO,
            'fuente': FuenteLead.WEB,
            'notas': 'Preguntó por cobertura en su zona',
        },
        
        # COLD LEADS
        {
            'nombre': 'Pedro',
            'apellido': 'Sánchez',
            'telefono': '+51987654325',
            'zona': 'Los Olivos',
            'score': 30,
            'clasificacion': ClasificacionLead.COLD,
            'estado': EstadoLead.NUEVO,
            'fuente': FuenteLead.WHATSAPP,
            'notas': 'Solo preguntó precios, no dio más información',
        },
        {
            'nombre': 'Laura',
            'apellido': 'Martínez',
            'telefono': '+51987654326',
            'email': 'laura.martinez@email.com',
            'zona': 'San Juan de Lurigancho',
            'score': 25,
            'clasificacion': ClasificacionLead.COLD,
            'estado': EstadoLead.NUEVO,
            'fuente': FuenteLead.REDES_SOCIALES,
            'notas': 'Preguntó por promociones pero no respondió más',
        },
    ]
    
    leads = []
    for lead_data in leads_data:
        # Asignar producto de interés si tiene tipo de servicio
        if 'tipo_servicio_interes' in lead_data and lead_data['tipo_servicio_interes']:
            producto = productos.filter(
                tipo=lead_data['tipo_servicio_interes'],
                is_destacado=True
            ).first()
            if producto:
                lead_data['producto_interes'] = producto
                lead_data['operador_interes'] = producto.operador
        
        lead, created = Lead.objects.get_or_create(
            telefono=lead_data['telefono'],
            defaults=lead_data
        )
        leads.append(lead)
        if created:
            print(f"  ✅ {lead.nombre_completo} - {lead.get_clasificacion_display()}")
        else:
            print(f"  ℹ️  Ya existe: {lead.nombre_completo}")
    
    return leads


def crear_conversaciones(leads):
    """Crea conversaciones de ejemplo"""
    print("\n💬 Creando conversaciones...")
    
    conversaciones_data = [
        # Conversación de Carlos (HOT)
        {
            'lead': leads[0],  # Carlos
            'canal': CanalConversacion.WHATSAPP,
            'tipo': TipoConversacion.ENTRANTE,
            'mensaje_cliente': 'Hola, quiero contratar internet de 100 megas para mi casa',
            'respuesta_sistema': '¡Hola Carlos! 👋 Excelente elección. Tenemos el plan perfecto para ti. ¿En qué zona vives?',
            'sentimiento': SentimientoConversacion.POSITIVO,
            'fue_atendido_por_ia': True,
            'intenciones_detectadas': ['INTERES_COMPRA', 'CONSULTA_TECNICA'],
        },
        {
            'lead': leads[0],  # Carlos - Segunda conversación
            'canal': CanalConversacion.WHATSAPP,
            'tipo': TipoConversacion.ENTRANTE,
            'mensaje_cliente': 'Vivo en San Isidro. Cuánto cuesta?',
            'respuesta_sistema': 'Perfecto! En San Isidro tenemos cobertura. El plan de 100 Mbps está en promoción a $42.50/mes (antes $50). Incluye instalación gratis. ¿Te interesa?',
            'sentimiento': SentimientoConversacion.POSITIVO,
            'fue_atendido_por_ia': True,
            'intenciones_detectadas': ['CONSULTA_PRECIO', 'CONSULTA_DISPONIBILIDAD'],
        },
        
        # Conversación de María (HOT)
        {
            'lead': leads[1],  # María
            'canal': CanalConversacion.LLAMADA,
            'tipo': TipoConversacion.ENTRANTE,
            'mensaje_cliente': 'Buenos días, quiero información sobre paquetes combo',
            'respuesta_sistema': 'Buenos días María! Con gusto. Tenemos combos desde $67.50/mes con Internet + TV + Teléfono.',
            'transcripcion': 'Cliente llamó preguntando por combos. Muy interesada en el combo total.',
            'duracion_segundos': 180,
            'sentimiento': SentimientoConversacion.POSITIVO,
            'fue_atendido_por_ia': False,
            'intenciones_detectadas': ['INTERES_COMPRA', 'CONSULTA_PRECIO'],
        },
        
        # Conversación de Juan (WARM)
        {
            'lead': leads[2],  # Juan
            'canal': CanalConversacion.WHATSAPP,
            'tipo': TipoConversacion.ENTRANTE,
            'mensaje_cliente': 'Hola, cuánto cuesta el plan de 20GB?',
            'respuesta_sistema': 'Hola Juan! El plan de 20GB está en $31.50/mes con descuento. Incluye 1000 minutos y redes sociales ilimitadas.',
            'sentimiento': SentimientoConversacion.NEUTRAL,
            'fue_atendido_por_ia': True,
            'intenciones_detectadas': ['CONSULTA_PRECIO'],
        },
        
        # Conversación de Pedro (COLD)
        {
            'lead': leads[4],  # Pedro
            'canal': CanalConversacion.WHATSAPP,
            'tipo': TipoConversacion.ENTRANTE,
            'mensaje_cliente': 'Precios de internet?',
            'respuesta_sistema': 'Hola! Tenemos planes desde $31.50/mes (50 Mbps) hasta $56/mes (200 Mbps). ¿En qué zona vives?',
            'sentimiento': SentimientoConversacion.NEUTRAL,
            'fue_atendido_por_ia': True,
            'intenciones_detectadas': ['CONSULTA_PRECIO'],
        },
    ]
    
    conversaciones_creadas = 0
    for conv_data in conversaciones_data:
        conversacion = Conversacion.objects.create(**conv_data)
        conversaciones_creadas += 1
        print(f"  ✅ Conversación con {conversacion.lead.nombre_completo}")
    
    print(f"\n  Total conversaciones creadas: {conversaciones_creadas}")


def crear_ventas(leads, productos):
    """Crea ventas de ejemplo"""
    print("\n💰 Creando ventas...")
    
    admin_user = User.objects.get(username='admin')
    
    ventas_data = [
        {
            'lead': leads[0],  # Carlos
            'producto': productos.filter(nombre_plan__contains='100 Mbps').first(),
            'agente': admin_user,
            'fue_venta_ia': False,
            'precio_final': Decimal('42.50'),
            'descuento_aplicado': Decimal('7.50'),
            'comision_agente': Decimal('50.00'),
            'fecha_instalacion': (timezone.now() + timedelta(days=3)).date(),
            'direccion_instalacion': 'Av. Javier Prado 123, San Isidro',
            'estado': EstadoVenta.PENDIENTE,
            'notas': 'Cliente confirmó instalación para el viernes',
        },
    ]
    
    ventas_creadas = 0
    for venta_data in ventas_data:
        if venta_data['producto']:
            venta = Venta.objects.create(**venta_data)
            ventas_creadas += 1
            print(f"  ✅ Venta a {venta.lead.nombre_completo} - ${venta.precio_final}")
    
    print(f"\n  Total ventas creadas: {ventas_creadas}")


def main():
    """Función principal"""
    print("=" * 80)
    print("🚀 POBLANDO BASE DE DATOS - CALL CENTER IA")
    print("=" * 80)
    
    try:
        # Crear datos
        operadores = crear_operadores()
        productos = crear_productos(operadores)
        leads = crear_leads(productos)
        crear_conversaciones(leads)
        crear_ventas(leads, productos)
        
        # Resumen
        print("\n" + "=" * 80)
        print("✅ DATOS CREADOS EXITOSAMENTE")
        print("=" * 80)
        print(f"📱 Operadores: {Operador.objects.count()}")
        print(f"📦 Productos: {Producto.objects.count()}")
        print(f"👥 Leads: {Lead.objects.count()}")
        print(f"   🔥 HOT: {Lead.objects.filter(clasificacion='HOT').count()}")
        print(f"   🌡️  WARM: {Lead.objects.filter(clasificacion='WARM').count()}")
        print(f"   ❄️  COLD: {Lead.objects.filter(clasificacion='COLD').count()}")
        print(f"💬 Conversaciones: {Conversacion.objects.count()}")
        print(f"💰 Ventas: {Venta.objects.count()}")
        print("=" * 80)
        print("\n🎉 ¡Listo! Ahora puedes acceder al admin:")
        print("   http://localhost:8000/admin/")
        print("\n   Usuario: admin")
        print("   Contraseña: admin123 (si usaste create_superuser.py)")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
