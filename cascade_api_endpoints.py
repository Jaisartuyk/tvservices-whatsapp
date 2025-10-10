# 🚀 ENDPOINTS ADICIONALES PARA CASCADE INTEGRATION
# Complemento al archivo cascade_integration.py

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.serializers import serialize
from django.core.paginator import Paginator
import json
from datetime import datetime, timedelta

# =============================================================================
# 📊 ENDPOINTS ESPECÍFICOS PARA DATOS
# =============================================================================

@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_get_utensilios(request):
    """📊 API para obtener datos de utensilios"""
    try:
        if not validate_cascade_request(request):
            return JsonResponse({"error": "Unauthorized"}, status=401)
        
        from control_utensilios.models import StockUtensilio, ControlDiario
        
        # Parámetros de consulta
        fecha = request.GET.get('fecha', datetime.now().date())
        modulo_id = request.GET.get('modulo_id')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 50))
        
        # Construir query
        if isinstance(fecha, str):
            fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
        
        queryset = ControlDiario.objects.filter(fecha=fecha).select_related('modulo')
        
        if modulo_id:
            queryset = queryset.filter(modulo_id=modulo_id)
        
        # Paginación
        paginator = Paginator(queryset, per_page)
        page_obj = paginator.get_page(page)
        
        # Serializar datos
        data = []
        for control in page_obj:
            data.append({
                'id': control.id,
                'fecha': control.fecha.isoformat(),
                'modulo': {
                    'id': control.modulo.id,
                    'nombre': control.modulo.nombre
                },
                'utensilios': {
                    'cuchillos': {
                        'entregados': control.cuchillos_entregados,
                        'devueltos': control.cuchillos_devueltos,
                        'danados': getattr(control, 'cuchillos_danados', 0),
                        'perdidos': getattr(control, 'cuchillos_perdidos', 0)
                    },
                    'crochet': {
                        'entregados': control.crochet_entregados,
                        'devueltos': control.crochet_devueltos,
                        'danados': getattr(control, 'crochet_danados', 0),
                        'perdidos': getattr(control, 'crochet_perdidos', 0)
                    },
                    'tijeras': {
                        'entregadas': control.tijeras_entregadas,
                        'devueltas': control.tijeras_devueltas,
                        'danadas': getattr(control, 'tijeras_danadas', 0),
                        'perdidas': getattr(control, 'tijeras_perdidas', 0)
                    }
                },
                'timestamp': control.created_at.isoformat() if hasattr(control, 'created_at') else None
            })
        
        return JsonResponse({
            'status': 'success',
            'data': data,
            'pagination': {
                'current_page': page,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'per_page': per_page,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous()
            },
            'filters': {
                'fecha': fecha.isoformat(),
                'modulo_id': modulo_id
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def api_get_dashboard(request):
    """📈 API para datos del dashboard"""
    try:
        if not validate_cascade_request(request):
            return JsonResponse({"error": "Unauthorized"}, status=401)
        
        from control_utensilios.models import ControlDiario, Modulo
        from django.db.models import Sum, Count
        
        # Fecha por defecto: hoy
        fecha = request.GET.get('fecha', datetime.now().date())
        if isinstance(fecha, str):
            fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
        
        # Datos generales del día
        controles_dia = ControlDiario.objects.filter(fecha=fecha)
        
        totales = controles_dia.aggregate(
            total_cuchillos_entregados=Sum('cuchillos_entregados'),
            total_cuchillos_devueltos=Sum('cuchillos_devueltos'),
            total_crochet_entregados=Sum('crochet_entregados'),
            total_crochet_devueltos=Sum('crochet_devueltos'),
            total_tijeras_entregadas=Sum('tijeras_entregadas'),
            total_tijeras_devueltas=Sum('tijeras_devueltas'),
            total_controles=Count('id')
        )
        
        # Datos por módulo
        modulos_data = []
        modulos = Modulo.objects.all()
        
        for modulo in modulos:
            controles_modulo = controles_dia.filter(modulo=modulo)
            resumen_modulo = controles_modulo.aggregate(
                cuchillos_entregados=Sum('cuchillos_entregados'),
                cuchillos_devueltos=Sum('cuchillos_devueltos'),
                crochet_entregados=Sum('crochet_entregados'),
                crochet_devueltos=Sum('crochet_devueltos'),
                tijeras_entregadas=Sum('tijeras_entregadas'),
                tijeras_devueltas=Sum('tijeras_devueltas')
            )
            
            modulos_data.append({
                'id': modulo.id,
                'nombre': modulo.nombre,
                'resumen': {
                    'entregados': {
                        'cuchillos': resumen_modulo['cuchillos_entregados'] or 0,
                        'crochet': resumen_modulo['crochet_entregados'] or 0,
                        'tijeras': resumen_modulo['tijeras_entregadas'] or 0
                    },
                    'devueltos': {
                        'cuchillos': resumen_modulo['cuchillos_devueltos'] or 0,
                        'crochet': resumen_modulo['crochet_devueltos'] or 0,
                        'tijeras': resumen_modulo['tijeras_devueltas'] or 0
                    }
                }
            })
        
        # Tendencia de los últimos 7 días
        fecha_inicio = fecha - timedelta(days=6)
        tendencia = []
        
        for i in range(7):
            fecha_actual = fecha_inicio + timedelta(days=i)
            controles_fecha = ControlDiario.objects.filter(fecha=fecha_actual)
            
            totales_fecha = controles_fecha.aggregate(
                entregados=Sum('cuchillos_entregados') + Sum('crochet_entregados') + Sum('tijeras_entregadas'),
                devueltos=Sum('cuchillos_devueltos') + Sum('crochet_devueltos') + Sum('tijeras_devueltas')
            )
            
            tendencia.append({
                'fecha': fecha_actual.isoformat(),
                'entregados': totales_fecha['entregados'] or 0,
                'devueltos': totales_fecha['devueltos'] or 0,
                'danados': 0,  # Agregar si tienes estos campos
                'perdidos': 0   # Agregar si tienes estos campos
            })
        
        return JsonResponse({
            'status': 'success',
            'data': {
                'fecha': fecha.isoformat(),
                'totales': {
                    'entregados': {
                        'cuchillos': totales['total_cuchillos_entregados'] or 0,
                        'crochet': totales['total_crochet_entregados'] or 0,
                        'tijeras': totales['total_tijeras_entregadas'] or 0
                    },
                    'devueltos': {
                        'cuchillos': totales['total_cuchillos_devueltos'] or 0,
                        'crochet': totales['total_crochet_devueltos'] or 0,
                        'tijeras': totales['total_tijeras_devueltas'] or 0
                    },
                    'danados': {
                        'cuchillos': 0,
                        'crochet': 0,
                        'tijeras': 0
                    },
                    'perdidos': {
                        'cuchillos': 0,
                        'crochet': 0,
                        'tijeras': 0
                    }
                },
                'data_modulos': modulos_data,
                'tendencia': tendencia,
                'total_controles': totales['total_controles'] or 0
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def api_create_report(request):
    """📋 API para crear reportes"""
    try:
        if not validate_cascade_request(request):
            return JsonResponse({"error": "Unauthorized"}, status=401)
        
        data = json.loads(request.body)
        
        fecha = data.get('fecha', datetime.now().date())
        modulo_id = data.get('modulo_id')
        tipo_reporte = data.get('tipo', 'completo')
        formato = data.get('formato', 'pdf')  # pdf, excel, json
        
        if isinstance(fecha, str):
            fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
        
        # Generar reporte según el tipo
        if tipo_reporte == 'completo':
            reporte_data = generate_complete_report(fecha, modulo_id)
        elif tipo_reporte == 'resumen':
            reporte_data = generate_summary_report(fecha, modulo_id)
        elif tipo_reporte == 'auditoria':
            reporte_data = generate_audit_report(fecha, modulo_id)
        else:
            return JsonResponse({'error': 'Tipo de reporte no válido'}, status=400)
        
        # Generar archivo según formato
        if formato == 'pdf':
            file_path = generate_pdf_report(reporte_data, fecha, tipo_reporte)
        elif formato == 'excel':
            file_path = generate_excel_report(reporte_data, fecha, tipo_reporte)
        else:
            file_path = None
        
        return JsonResponse({
            'status': 'success',
            'reporte': {
                'tipo': tipo_reporte,
                'formato': formato,
                'fecha': fecha.isoformat(),
                'modulo_id': modulo_id,
                'file_path': file_path,
                'data': reporte_data if formato == 'json' else None
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def api_system_status(request):
    """🔍 API para estado del sistema"""
    try:
        from django.db import connection
        import psutil
        import os
        
        # Estado de la base de datos
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            db_status = "OK"
            db_response_time = "< 1ms"
        except Exception as e:
            db_status = f"ERROR: {str(e)}"
            db_response_time = "N/A"
        
        # Estado del sistema
        try:
            system_info = {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory': {
                    'percent': psutil.virtual_memory().percent,
                    'available_gb': round(psutil.virtual_memory().available / (1024**3), 2),
                    'total_gb': round(psutil.virtual_memory().total / (1024**3), 2)
                },
                'disk': {
                    'percent': psutil.disk_usage('/').percent,
                    'free_gb': round(psutil.disk_usage('/').free / (1024**3), 2),
                    'total_gb': round(psutil.disk_usage('/').total / (1024**3), 2)
                }
            }
        except:
            system_info = {'error': 'Could not retrieve system info'}
        
        # Estado de la aplicación
        from control_utensilios.models import ControlDiario, StockUtensilio
        
        app_status = {
            'total_controles_hoy': ControlDiario.objects.filter(
                fecha=datetime.now().date()
            ).count(),
            'total_stocks_activos': StockUtensilio.objects.count(),
            'ultima_actividad': ControlDiario.objects.order_by('-id').first().fecha.isoformat() if ControlDiario.objects.exists() else None
        }
        
        return JsonResponse({
            'status': 'success',
            'system_status': {
                'overall': 'OK' if db_status == 'OK' else 'WARNING',
                'database': {
                    'status': db_status,
                    'response_time': db_response_time
                },
                'system': system_info,
                'application': app_status,
                'python_version': os.sys.version.split()[0],
                'django_version': '4.2.0',  # Actualizar según tu versión
                'uptime': 'N/A'  # Implementar si necesitas
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def api_health_check(request):
    """💚 Health check simple"""
    return JsonResponse({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@csrf_exempt
@require_http_methods(["POST"])
def api_send_notification(request):
    """📱 API para enviar notificaciones"""
    try:
        if not validate_cascade_request(request):
            return JsonResponse({"error": "Unauthorized"}, status=401)
        
        data = json.loads(request.body)
        
        notification_type = data.get('type', 'info')
        message = data.get('message', '')
        recipients = data.get('recipients', [])
        channel = data.get('channel', 'whatsapp')  # whatsapp, email, sms
        
        # Aquí implementarías la lógica de notificaciones
        # Por ejemplo, integración con WhatsApp Business API
        
        results = []
        for recipient in recipients:
            try:
                # Simular envío de notificación
                result = send_notification_to_recipient(
                    recipient, message, channel, notification_type
                )
                results.append({
                    'recipient': recipient,
                    'status': 'sent',
                    'result': result
                })
            except Exception as e:
                results.append({
                    'recipient': recipient,
                    'status': 'failed',
                    'error': str(e)
                })
        
        return JsonResponse({
            'status': 'success',
            'notification': {
                'type': notification_type,
                'channel': channel,
                'message': message[:100] + '...' if len(message) > 100 else message,
                'recipients_count': len(recipients),
                'sent_count': len([r for r in results if r['status'] == 'sent']),
                'failed_count': len([r for r in results if r['status'] == 'failed'])
            },
            'results': results,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }, status=500)

# =============================================================================
# 🛠️ FUNCIONES AUXILIARES
# =============================================================================

def validate_cascade_request(request):
    """🔐 Validar que la request viene de Cascade"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return False
    
    token = auth_header.split(' ')[1]
    # Aquí deberías validar el token con tu sistema de autenticación
    return token == "tu_cascade_api_key"  # Cambiar por validación real

def generate_complete_report(fecha, modulo_id):
    """📊 Generar reporte completo"""
    from control_utensilios.models import ControlDiario
    
    queryset = ControlDiario.objects.filter(fecha=fecha)
    if modulo_id:
        queryset = queryset.filter(modulo_id=modulo_id)
    
    data = []
    for control in queryset:
        data.append({
            'modulo': control.modulo.nombre,
            'cuchillos_entregados': control.cuchillos_entregados,
            'cuchillos_devueltos': control.cuchillos_devueltos,
            'crochet_entregados': control.crochet_entregados,
            'crochet_devueltos': control.crochet_devueltos,
            'tijeras_entregadas': control.tijeras_entregadas,
            'tijeras_devueltas': control.tijeras_devueltas
        })
    
    return data

def generate_summary_report(fecha, modulo_id):
    """📋 Generar reporte resumen"""
    # Implementar lógica de reporte resumen
    return {'tipo': 'resumen', 'fecha': fecha.isoformat()}

def generate_audit_report(fecha, modulo_id):
    """🔍 Generar reporte de auditoría"""
    # Implementar lógica de reporte de auditoría
    return {'tipo': 'auditoria', 'fecha': fecha.isoformat()}

def generate_pdf_report(data, fecha, tipo):
    """📄 Generar reporte en PDF"""
    # Implementar generación de PDF
    filename = f"reporte_{tipo}_{fecha.strftime('%Y%m%d')}.pdf"
    return f"/reports/{filename}"

def generate_excel_report(data, fecha, tipo):
    """📊 Generar reporte en Excel"""
    # Implementar generación de Excel
    filename = f"reporte_{tipo}_{fecha.strftime('%Y%m%d')}.xlsx"
    return f"/reports/{filename}"

def send_notification_to_recipient(recipient, message, channel, notification_type):
    """📱 Enviar notificación a un destinatario específico"""
    # Implementar lógica de envío según el canal
    if channel == 'whatsapp':
        return send_whatsapp_message(recipient, message)
    elif channel == 'email':
        return send_email_message(recipient, message)
    elif channel == 'sms':
        return send_sms_message(recipient, message)
    else:
        raise ValueError(f"Canal no soportado: {channel}")

def send_whatsapp_message(phone, message):
    """📱 Enviar mensaje de WhatsApp"""
    # Implementar con tu API de WhatsApp
    return {'message_id': 'wa_123456', 'status': 'sent'}

def send_email_message(email, message):
    """📧 Enviar email"""
    # Implementar con Django email
    return {'message_id': 'email_123456', 'status': 'sent'}

def send_sms_message(phone, message):
    """📱 Enviar SMS"""
    # Implementar con tu proveedor de SMS
    return {'message_id': 'sms_123456', 'status': 'sent'}
