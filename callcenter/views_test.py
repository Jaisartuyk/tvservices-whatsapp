"""
Vista de prueba para verificar deployment
"""
from django.http import HttpResponse


def test_view(request):
    """Vista de prueba simple"""
    return HttpResponse("TEST VIEW WORKS - Build: 2025-10-30-16:02")
