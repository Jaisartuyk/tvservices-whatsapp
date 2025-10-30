"""
Vista para actualizar leads
"""
import json
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Lead


@login_required
@require_POST
def update_lead(request, lead_id):
    """Actualizar informacion de un lead"""
    try:
        lead = get_object_or_404(Lead, id=lead_id)
        data = json.loads(request.body)
        
        # Actualizar campos basicos
        lead.nombre = data.get('nombre', lead.nombre)
        lead.apellido = data.get('apellido', lead.apellido)
        lead.telefono = data.get('telefono', lead.telefono)
        lead.email = data.get('email') or None
        lead.direccion = data.get('direccion', lead.direccion)
        lead.zona = data.get('zona', lead.zona)
        lead.clasificacion = data.get('clasificacion', lead.clasificacion)
        lead.estado = data.get('estado', lead.estado)
        lead.tipo_servicio_interes = data.get('tipo_servicio_interes', lead.tipo_servicio_interes)
        lead.presupuesto_estimado = data.get('presupuesto_estimado') or None
        lead.score = int(data.get('score', lead.score))
        lead.notas = data.get('notas', lead.notas)
        
        # Actualizar operador de interes
        operador_id = data.get('operador_interes_id')
        if operador_id:
            from .models import Operador
            try:
                lead.operador_interes = Operador.objects.get(id=operador_id)
            except Operador.DoesNotExist:
                pass
        else:
            lead.operador_interes = None
        
        # Actualizar producto de interes
        producto_id = data.get('producto_interes_id')
        if producto_id:
            from .models import Producto
            try:
                lead.producto_interes = Producto.objects.get(id=producto_id)
            except Producto.DoesNotExist:
                pass
        else:
            lead.producto_interes = None
        
        lead.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Lead actualizado exitosamente'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
