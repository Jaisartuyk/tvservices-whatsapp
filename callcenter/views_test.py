"""
Vista de prueba para verificar deployment
"""
from django.http import HttpResponse


def test_view(request):
    """Vista de prueba simple"""
    try:
        from . import views_whatsapp
        has_whatsapp = "YES"
        whatsapp_detail = str(hasattr(views_whatsapp, 'whatsapp_detail'))
    except Exception as e:
        has_whatsapp = f"NO - Error: {str(e)}"
        whatsapp_detail = "N/A"
    
    return HttpResponse(f"TEST VIEW WORKS - Build: 2025-10-30-16:08<br>views_whatsapp imported: {has_whatsapp}<br>has whatsapp_detail: {whatsapp_detail}")


def test_whatsapp(request, conversacion_id):
    """Test que simula la vista de whatsapp"""
    return HttpResponse(f"TEST WHATSAPP VIEW WORKS - conversacion_id: {conversacion_id}")


def test_whatsapp_real(request, conversacion_id):
    """Test que llama a la vista real de whatsapp"""
    from . import views_whatsapp
    try:
        # Llamar a la vista real sin el decorador
        response = views_whatsapp.whatsapp_detail.__wrapped__(request, conversacion_id)
        return HttpResponse(f"Real whatsapp view returned: {type(response).__name__}")
    except Exception as e:
        return HttpResponse(f"Error calling real view: {str(e)}")
