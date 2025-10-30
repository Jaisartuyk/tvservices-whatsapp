"""
Vistas para importación de Leads desde CSV/Excel
"""
import csv
import io
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import Lead, Operador, TipoServicio, FuenteLead
import logging

logger = logging.getLogger(__name__)

# Intentar importar openpyxl para Excel
try:
    import openpyxl
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False


@login_required
@require_POST
def import_leads(request):
    """
    Importar leads desde archivo CSV o Excel
    
    Estructura esperada:
    nombre,apellido,telefono,email,zona,operador,tipo_servicio,presupuesto,notas
    """
    try:
        # Validar archivo
        if 'file' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No se proporcionó ningún archivo'
            }, status=400)
        
        file = request.FILES['file']
        operador_default_id = request.POST.get('operador_id')
        
        # Obtener operador por defecto
        operador_default = None
        if operador_default_id:
            try:
                operador_default = Operador.objects.get(id=operador_default_id)
            except Operador.DoesNotExist:
                pass
        
        # Validar extensión
        file_extension = file.name.split('.')[-1].lower()
        if file_extension not in ['csv', 'xlsx', 'xls']:
            return JsonResponse({
                'success': False,
                'error': 'Formato no válido. Use CSV o Excel (.xlsx)'
            }, status=400)
        
        # Procesar archivo según tipo
        leads_data = []
        
        if file_extension == 'csv':
            # Procesar CSV
            decoded_file = file.read().decode('utf-8-sig')  # utf-8-sig para manejar BOM
            csv_reader = csv.DictReader(io.StringIO(decoded_file))
            leads_data = list(csv_reader)
            
        elif file_extension in ['xlsx', 'xls']:
            # Procesar Excel
            if not OPENPYXL_AVAILABLE:
                return JsonResponse({
                    'success': False,
                    'error': 'No se puede procesar archivos Excel. Use CSV.'
                }, status=400)
            
            workbook = openpyxl.load_workbook(file)
            sheet = workbook.active
            
            # Obtener headers (primera fila)
            headers = [cell.value for cell in sheet[1]]
            
            # Leer datos
            for row in sheet.iter_rows(min_row=2, values_only=True):
                row_dict = {}
                for i, value in enumerate(row):
                    if i < len(headers) and headers[i]:
                        row_dict[headers[i]] = value
                if row_dict:  # Solo agregar si tiene datos
                    leads_data.append(row_dict)
        
        # Validar que hay datos
        if not leads_data:
            return JsonResponse({
                'success': False,
                'error': 'El archivo está vacío'
            }, status=400)
        
        # Procesar leads
        leads_creados = 0
        leads_duplicados = 0
        errores = []
        
        for idx, row in enumerate(leads_data, start=2):  # start=2 porque la fila 1 son headers
            try:
                # Validar campos requeridos
                nombre = row.get('nombre', '').strip()
                apellido = row.get('apellido', '').strip()
                telefono = row.get('telefono', '').strip()
                zona = row.get('zona', '').strip()
                
                if not all([nombre, apellido, telefono, zona]):
                    errores.append(f"Fila {idx}: Faltan campos requeridos (nombre, apellido, telefono, zona)")
                    continue
                
                # Normalizar teléfono
                telefono_limpio = ''.join(filter(str.isdigit, telefono))
                if telefono_limpio.startswith('593'):
                    telefono_normalizado = '+' + telefono_limpio
                elif len(telefono_limpio) == 10 and telefono_limpio.startswith('0'):
                    telefono_normalizado = '+593' + telefono_limpio[1:]
                elif len(telefono_limpio) == 9:
                    telefono_normalizado = '+593' + telefono_limpio
                else:
                    telefono_normalizado = '+' + telefono_limpio
                
                # Verificar si ya existe
                if Lead.objects.filter(telefono=telefono_normalizado).exists():
                    leads_duplicados += 1
                    continue
                
                # Buscar operador
                operador = operador_default
                operador_nombre = row.get('operador', '').strip()
                if operador_nombre:
                    try:
                        operador = Operador.objects.get(nombre__iexact=operador_nombre)
                    except Operador.DoesNotExist:
                        pass  # Usar operador por defecto
                
                # Validar tipo de servicio
                tipo_servicio = row.get('tipo_servicio', '').strip().upper()
                if tipo_servicio and tipo_servicio not in dict(TipoServicio.choices):
                    tipo_servicio = ''
                
                # Crear lead
                lead = Lead.objects.create(
                    nombre=nombre,
                    apellido=apellido,
                    telefono=telefono_normalizado,
                    email=row.get('email', '').strip() or None,
                    zona=zona,
                    operador_interes=operador,
                    tipo_servicio_interes=tipo_servicio or '',
                    presupuesto_estimado=row.get('presupuesto') or None,
                    notas=row.get('notas', '').strip(),
                    clasificacion='COLD',
                    estado='NUEVO',
                    fuente='WEB',
                    score=30,
                    created_at=timezone.now()
                )
                
                leads_creados += 1
                
            except Exception as e:
                logger.exception(f"Error procesando fila {idx}")
                errores.append(f"Fila {idx}: {str(e)}")
        
        # Preparar respuesta
        return JsonResponse({
            'success': True,
            'leads_creados': leads_creados,
            'leads_duplicados': leads_duplicados,
            'total_procesados': len(leads_data),
            'errores': errores[:10]  # Máximo 10 errores para no saturar
        })
        
    except Exception as e:
        logger.exception('Error en importación de leads')
        return JsonResponse({
            'success': False,
            'error': f'Error al procesar archivo: {str(e)}'
        }, status=500)
