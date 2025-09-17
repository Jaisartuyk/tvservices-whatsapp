from .whatsapp_service import WhatsAppService

# Alias para compatibilidad con el comando existente
def send_expiration_notifications(subscriptions, days_notice, dry_run=False):
    """
    Función de compatibilidad para el comando de management
    """
    whatsapp_service = WhatsAppService()
    results = []
    
    for subscription in subscriptions:
        if dry_run:
            results.append({
                'subscription': subscription,
                'success': True,
                'message': 'Modo de prueba - no se envió mensaje real'
            })
        else:
            result = whatsapp_service.send_expiration_notification(
                subscription=subscription,
                days_notice=days_notice
            )
            result['subscription'] = subscription
            results.append(result)
    
    return results
