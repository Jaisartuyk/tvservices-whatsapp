import stripe
import json
import logging
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Subscription

def create_stripe_checkout_session(request, service, price_id):
    """Crea una sesión de pago de Stripe"""
    if not hasattr(settings, 'STRIPE_SECRET_KEY') or not settings.STRIPE_SECRET_KEY:
        messages.error(request, 'Error de configuración: Falta la clave secreta de Stripe.')
        return redirect('checkout', service_id=service.id)
    
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    try:
        # Verificar que el precio existe en Stripe
        try:
            price = stripe.Price.retrieve(price_id)
            if not price.active:
                messages.error(request, 'El plan seleccionado no está disponible.')
                return redirect('checkout', service_id=service.id)
        except stripe.error.InvalidRequestError as e:
            messages.error(request, f'Error al verificar el plan de pago: {str(e)}')
            return redirect('checkout', service_id=service.id)
        
        # Crear la sesión de pago
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.build_absolute_uri(reverse('payment_success')) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.build_absolute_uri(reverse('checkout', kwargs={'service_id': service.id})),
            customer_email=request.user.email,
            client_reference_id=f"user_{request.user.id}_service_{service.id}",
            metadata={
                'service_id': str(service.id),
                'service_name': service.name,
                'user_id': str(request.user.id),
                'user_email': request.user.email
            }
        )
        
        # Redirigir al checkout de Stripe
        return redirect(checkout_session.url, code=303)
        
    except stripe.error.CardError as e:
        # Tarjeta rechazada
        error_message = e.error.message if hasattr(e, 'error') and hasattr(e.error, 'message') else str(e)
        messages.error(request, f'Error en la tarjeta: {error_message}')
    except stripe.error.RateLimitError:
        messages.error(request, 'Demasiadas solicitudes a Stripe. Por favor, inténtalo de nuevo en unos momentos.')
    except stripe.error.InvalidRequestError as e:
        messages.error(request, f'Error en la solicitud a Stripe: {str(e)}')
    except stripe.error.AuthenticationError:
        messages.error(request, 'Error de autenticación con Stripe. Por favor, contacta al soporte.')
    except stripe.error.APIConnectionError:
        messages.error(request, 'Error de conexión con Stripe. Por favor, verifica tu conexión a internet.')
    except stripe.error.StripeError as e:
        messages.error(request, f'Error de Stripe: {str(e)}')
    except Exception as e:
        # Error inesperado
        import traceback
        logger.error(f'Error inesperado en create_stripe_checkout_session: {str(e)}\n{traceback.format_exc()}')
        messages.error(request, 'Ocurrió un error inesperado. Por favor, inténtalo de nuevo.')
    
    return redirect('checkout', service_id=service.id)

@csrf_exempt
def handle_stripe_webhook(request):
    """Maneja los webhooks de Stripe para actualizar el estado de las suscripciones"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    # Modo desarrollo: Si no hay firma, intentar decodificar el JSON igualmente
    if settings.DEBUG and not sig_header:
        try:
            event = json.loads(payload)
            logger.warning('Modo desarrollo: Webhook procesado sin verificación de firma')
            return _process_webhook_event(event)
        except json.JSONDecodeError as e:
            logger.error(f'Error al decodificar JSON: {str(e)}')
            return JsonResponse({'error': 'JSON inválido'}, status=400)
    
    # Modo producción: Verificación estricta de la firma
    try:
        event = stripe.Webhook.construct_event(
            payload, 
            sig_header, 
            settings.STRIPE_WEBHOOK_SECRET
        )
        return _process_webhook_event(event)
    except ValueError as e:
        logger.error(f'Error en el payload del webhook: {str(e)}')
        return JsonResponse({'error': 'Payload inválido'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f'Firma de webhook inválida: {str(e)}')
        logger.error(f'Firma recibida: {sig_header}')
        logger.error(f'Payload: {payload.decode()}')
        return JsonResponse({'error': f'Firma inválida: {str(e)}'}, status=400)
    except Exception as e:
        logger.error(f'Error al procesar webhook: {str(e)}', exc_info=True)
        return JsonResponse({'error': f'Error al procesar webhook: {str(e)}'}, status=400)
    
def _process_webhook_event(event):
    """Procesa el evento del webhook después de la validación"""
    logger.info(f'Evento recibido: {json.dumps(event, indent=2, default=str)}')
    event_type = event.get('type')
    logger.info(f'Procesando evento de webhook: {event_type}')
    
    if event_type == 'checkout.session.completed':
        try:
            session = event['data']['object']
            logger.info(f'Datos de la sesión: {json.dumps(session, indent=2, default=str)}')
            
            # Verificar que los datos necesarios estén presentes
            if not all(key in session.get('metadata', {}) for key in ['service_id', 'user_id']):
                error_msg = 'Faltan metadatos requeridos en la sesión'
                logger.error(f'{error_msg}. Metadata: {session.get("metadata")}')
                return JsonResponse({'status': 'error', 'message': error_msg}, status=400)
                
            result = handle_successful_payment(session)
            if result is True:
                return JsonResponse({'status': 'success', 'message': 'Pago procesado correctamente'})
            else:
                error_msg = result if isinstance(result, str) else 'Error al procesar el pago'
                return JsonResponse({'status': 'error', 'message': error_msg}, status=500)
                
        except Exception as e:
            error_msg = f'Error al procesar pago exitoso: {str(e)}'
            logger.error(error_msg, exc_info=True)
            return JsonResponse({'status': 'error', 'message': error_msg}, status=500)
    
    return JsonResponse({'status': 'success', 'message': 'Evento recibido pero no manejado'})

logger = logging.getLogger(__name__)

def handle_successful_payment(session):
    """Actualiza la base de datos cuando un pago es exitoso"""
    try:
        logger.info('='*80)
        logger.info('INICIANDO PROCESAMIENTO DE PAGO')
        logger.info('='*80)
        logger.info(f'Datos completos de la sesión:\n{json.dumps(session, indent=2, default=str)}')
        
        # Obtener los metadatos de la sesión
        metadata = session.get('metadata', {})
        service_id = metadata.get('service_id')
        user_id = metadata.get('user_id')
        
        logger.info(f'\nMetadatos extraídos:')
        logger.info(f'- service_id: {service_id} (tipo: {type(service_id)})')
        logger.info(f'- user_id: {user_id} (tipo: {type(user_id)})')
        
        if not service_id or not user_id:
            error_msg = f'Faltan service_id o user_id en los metadatos de la sesión. Metadata: {metadata}'
            logger.error(error_msg)
            return error_msg
        
        try:
            # Convertir los IDs a enteros para la base de datos
            try:
                service_id = int(service_id)
                user_id = int(user_id)
            except (ValueError, TypeError) as e:
                error_msg = f'Error al convertir IDs: {str(e)}. service_id: {service_id}, user_id: {user_id}'
                logger.error(error_msg)
                return error_msg
                
            logger.info(f'\nIDs convertidos:')
            logger.info(f'- service_id: {service_id} (tipo: {type(service_id)})')
            logger.info(f'- user_id: {user_id} (tipo: {type(user_id)})')
            
            # Verificar si el servicio y el usuario existen
            from django.contrib.auth import get_user_model
            from .models import Service, Subscription
            
            User = get_user_model()
            
            try:
                user = User.objects.get(id=user_id)
                logger.info(f'\nUsuario encontrado:')
                logger.info(f'- ID: {user.id}')
                logger.info(f'- Username: {user.username}')
                logger.info(f'- Email: {user.email}')
            except User.DoesNotExist:
                error_msg = f'Usuario con ID {user_id} no encontrado en la base de datos'
                logger.error(error_msg)
                return error_msg
            except Exception as e:
                error_msg = f'Error al buscar usuario: {str(e)}'
                logger.error(error_msg, exc_info=True)
                return error_msg
            
            try:
                service = Service.objects.get(id=service_id)
                logger.info(f'\nServicio encontrado:')
                logger.info(f'- ID: {service.id}')
                logger.info(f'- Nombre: {service.name if hasattr(service, "name") else "N/A"}')
            except Service.DoesNotExist:
                error_msg = f'Servicio con ID {service_id} no encontrado en la base de datos'
                logger.error(error_msg)
                return error_msg
            except Exception as e:
                error_msg = f'Error al buscar servicio: {str(e)}'
                logger.error(error_msg, exc_info=True)
                return error_msg
            
                # Obtener el precio del servicio
            price_paid = service.price  # Obtenemos el precio del servicio
            logger.info(f'\nPrecio del servicio: {price_paid}')
            
            # Preparar datos de la suscripción
            subscription_data = {
                'payment_method': 'card',
                'payment_status': 'paid',
                'price_paid': price_paid,  # Añadimos el precio pagado
                'stripe_subscription_id': session.get('subscription'),
                'stripe_customer_id': session.get('customer'),
                'stripe_payment_intent': session.get('payment_intent'),
                'active': True,
                'payment_details': {
                    'amount_paid': float(price_paid),
                    'currency': 'USD',  # O la moneda que estés usando
                    'payment_method': 'card',
                    'stripe_session_id': session.get('id')
                }
            }
            
            logger.info('\nIntentando crear/actualizar suscripción con datos:')
            for key, value in subscription_data.items():
                logger.info(f'- {key}: {value}')
            
            try:
                # Primero intentamos obtener la suscripción existente
                try:
                    subscription = Subscription.objects.get(
                        user_id=user_id,
                        service_id=service_id
                    )
                    # Si existe, actualizamos los datos
                    for key, value in subscription_data.items():
                        setattr(subscription, key, value)
                    subscription.save()
                    created = False
                    logger.info('\n✅ SUSCRIPCIÓN EXISTENTE ACTUALIZADA')
                except Subscription.DoesNotExist:
                    # Si no existe, la creamos
                    subscription = Subscription.objects.create(
                        user_id=user_id,
                        service_id=service_id,
                        **subscription_data
                    )
                    created = True
                    logger.info('\n✅ NUEVA SUSCRIPCIÓN CREADA')
                
                logger.info('='*80)
                logger.info(f'ID: {subscription.id}')
                logger.info(f'Usuario: {subscription.user_id}')
                logger.info(f'Servicio: {subscription.service_id}')
                logger.info(f'Precio: {subscription.price_paid}')
                logger.info(f'Estado: {subscription.get_payment_status_display()}')
                logger.info(f'Activa: {subscription.is_active}')
                logger.info('='*80)
                
                return True
                
            except Exception as e:
                error_msg = f'Error al crear/actualizar suscripción: {str(e)}'
                logger.error('\n❌ ' + '='*80)
                logger.error('ERROR AL PROCESAR SUSCRIPCIÓN')
                logger.error('='*80)
                logger.error(error_msg, exc_info=True)
                logger.error('\nDatos de la transacción que falló:')
                logger.error(f'- User ID: {user_id}')
                logger.error(f'- Service ID: {service_id}')
                logger.error(f'- Subscription Data: {subscription_data}')
                logger.error('='*80)
                return error_msg
            
        except Exception as e:
            error_msg = f'Error inesperado en handle_successful_payment: {str(e)}'
            logger.error('\n❌ ' + '='*80)
            logger.error('ERROR INESPERADO')
            logger.error('='*80)
            logger.error(error_msg, exc_info=True)
            logger.error('\nDatos del error:')
            logger.error(f'- service_id: {service_id} (tipo: {type(service_id)})')
            logger.error(f'- user_id: {user_id} (tipo: {type(user_id)})')
            logger.error('='*80)
            return error_msg
            
    except Exception as e:
        error_msg = f'Error crítico en handle_successful_payment: {str(e)}'
        logger.error('\n❌ ' + '='*80)
        logger.error('ERROR CRÍTICO')
        logger.error('='*80)
        logger.error(error_msg, exc_info=True)
        logger.error('\nDatos de la sesión que causó el error:')
        logger.error(f'{json.dumps(session, indent=2, default=str)}')
        logger.error('='*80)
        return error_msg
