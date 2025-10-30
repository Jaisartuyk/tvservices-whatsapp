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
