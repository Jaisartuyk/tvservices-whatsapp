from django.http import JsonResponse
import stripe
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def health_check(request):
    """Endpoint de verificación de salud"""
    results = {
        'status': 'ok',
        'checks': {}
    }
    
    # Verificar conexión a la base de datos
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            results['checks']['database'] = 'ok'
    except Exception as e:
        logger.error(f"Error de conexión a la base de datos: {str(e)}")
        results['checks']['database'] = 'error'
        results['status'] = 'error'
    
    # Verificar conexión a Stripe
    try:
        if hasattr(settings, 'STRIPE_SECRET_KEY') and settings.STRIPE_SECRET_KEY:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            stripe.Price.list(limit=1)  # Intenta listar precios
            results['checks']['stripe'] = 'ok'
            
            # Verificar precios configurados
            if hasattr(settings, 'STRIPE_PRICES'):
                results['stripe_prices'] = settings.STRIPE_PRICES
            else:
                results['stripe_prices'] = 'no_configured'
        else:
            results['checks']['stripe'] = 'not_configured'
            results['status'] = 'error'
    except Exception as e:
        logger.error(f"Error de conexión a Stripe: {str(e)}")
        results['checks']['stripe'] = f'error: {str(e)}'
        results['status'] = 'error'
    
    return JsonResponse(results)
