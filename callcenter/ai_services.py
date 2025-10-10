"""
Servicios de IA para Call Center
- WhatsApp Bot
- Análisis de conversaciones
- Scoring de leads
- Generación de respuestas
"""

import json
import re
from typing import Dict, List, Tuple
from decimal import Decimal


class LeadScorer:
    """Calcula el score de un lead basado en sus interacciones"""
    
    @staticmethod
    def calcular_score(lead, mensaje: str = "") -> int:
        """
        Calcula el score de un lead (0-100)
        
        Factores:
        - Interacción (30%)
        - Preguntas sobre precios (25%)
        - Información específica (20%)
        - Tiempo de conversación (15%)
        - Respuestas positivas (10%)
        """
        score = 0
        
        # 1. Puntos por tener producto de interés específico (30 puntos)
        if lead.producto_interes:
            score += 30
        elif lead.tipo_servicio_interes:
            score += 15
        
        # 2. Puntos por presupuesto definido (25 puntos)
        if lead.presupuesto_estimado:
            score += 25
        
        # 3. Puntos por información específica (20 puntos)
        if lead.zona:
            score += 10
        if lead.direccion:
            score += 10
        
        # 4. Puntos por número de conversaciones (15 puntos)
        num_conversaciones = lead.conversaciones.count()
        score += min(num_conversaciones * 5, 15)
        
        # 5. Análisis del mensaje actual (10 puntos)
        if mensaje:
            mensaje_lower = mensaje.lower()
            
            # Palabras clave de alta intención
            palabras_compra = ['quiero', 'necesito', 'contratar', 'comprar', 'cuándo', 'precio', 'costo']
            if any(palabra in mensaje_lower for palabra in palabras_compra):
                score += 10
        
        # Limitar score entre 0 y 100
        return min(max(score, 0), 100)
    
    @staticmethod
    def clasificar_lead(score: int) -> str:
        """Clasifica el lead según su score"""
        if score >= 80:
            return 'HOT'
        elif score >= 50:
            return 'WARM'
        else:
            return 'COLD'


class IntentDetector:
    """Detecta intenciones en mensajes de clientes"""
    
    INTENCIONES = {
        'CONSULTA_PRECIO': [
            'cuánto cuesta', 'precio', 'costo', 'cuánto vale', 'cuánto es',
            'cuánto sale', 'valor', 'tarifa'
        ],
        'CONSULTA_DISPONIBILIDAD': [
            'hay cobertura', 'llega a', 'disponible en', 'tienen en',
            'cobertura', 'zona'
        ],
        'INTERES_COMPRA': [
            'quiero', 'necesito', 'me interesa', 'contratar', 'comprar',
            'adquirir', 'solicitar'
        ],
        'COMPARACION': [
            'diferencia', 'comparar', 'mejor que', 'versus', 'vs',
            'cuál es mejor'
        ],
        'CONSULTA_TECNICA': [
            'velocidad', 'mbps', 'gigas', 'gb', 'megas', 'canales',
            'dispositivos', 'instalación'
        ],
        'OBJECION_PRECIO': [
            'muy caro', 'muy costoso', 'no puedo pagar', 'es mucho',
            'demasiado', 'más barato', 'descuento', 'promoción'
        ],
        'SOLICITUD_CONTACTO': [
            'llámame', 'contacto', 'hablar con', 'agente', 'asesor',
            'representante'
        ]
    }
    
    @classmethod
    def detectar_intenciones(cls, mensaje: str) -> List[str]:
        """Detecta todas las intenciones presentes en un mensaje"""
        mensaje_lower = mensaje.lower()
        intenciones_detectadas = []
        
        for intencion, palabras_clave in cls.INTENCIONES.items():
            if any(palabra in mensaje_lower for palabra in palabras_clave):
                intenciones_detectadas.append(intencion)
        
        return intenciones_detectadas
    
    @classmethod
    def extraer_informacion(cls, mensaje: str) -> Dict:
        """Extrae información estructurada del mensaje"""
        info = {
            'zona': None,
            'presupuesto': None,
            'tipo_servicio': None
        }
        
        mensaje_lower = mensaje.lower()
        
        # Detectar tipo de servicio
        if any(palabra in mensaje_lower for palabra in ['internet', 'wifi', 'fibra']):
            info['tipo_servicio'] = 'INTERNET'
        elif any(palabra in mensaje_lower for palabra in ['móvil', 'celular', 'plan', 'gigas']):
            info['tipo_servicio'] = 'MOVIL'
        elif any(palabra in mensaje_lower for palabra in ['tv', 'cable', 'televisión']):
            info['tipo_servicio'] = 'TV'
        elif any(palabra in mensaje_lower for palabra in ['combo', 'paquete', 'todo']):
            info['tipo_servicio'] = 'COMBO'
        
        # Detectar presupuesto (números con $ o S/)
        presupuesto_match = re.search(r'[\$S/]?\s*(\d+)', mensaje)
        if presupuesto_match:
            info['presupuesto'] = int(presupuesto_match.group(1))
        
        return info


class SentimentAnalyzer:
    """Analiza el sentimiento de mensajes"""
    
    PALABRAS_POSITIVAS = [
        'excelente', 'perfecto', 'genial', 'bueno', 'gracias', 'sí',
        'me gusta', 'interesante', 'bien', 'ok', 'vale'
    ]
    
    PALABRAS_NEGATIVAS = [
        'no', 'malo', 'caro', 'costoso', 'problema', 'difícil',
        'complicado', 'no me gusta', 'no me interesa', 'nunca'
    ]
    
    @classmethod
    def analizar_sentimiento(cls, mensaje: str) -> str:
        """Analiza el sentimiento del mensaje"""
        mensaje_lower = mensaje.lower()
        
        positivos = sum(1 for palabra in cls.PALABRAS_POSITIVAS if palabra in mensaje_lower)
        negativos = sum(1 for palabra in cls.PALABRAS_NEGATIVAS if palabra in mensaje_lower)
        
        if positivos > negativos:
            return 'POSITIVO'
        elif negativos > positivos:
            return 'NEGATIVO'
        else:
            return 'NEUTRAL'


class WhatsAppBotIA:
    """Bot de WhatsApp con IA para atención de leads"""
    
    def __init__(self):
        self.scorer = LeadScorer()
        self.intent_detector = IntentDetector()
        self.sentiment_analyzer = SentimentAnalyzer()
    
    def procesar_mensaje(self, lead, mensaje: str) -> Dict:
        """
        Procesa un mensaje del cliente y genera una respuesta
        
        Returns:
            Dict con:
            - respuesta: str
            - intenciones: List[str]
            - sentimiento: str
            - score: int
            - clasificacion: str
            - siguiente_accion: str
        """
        # Detectar intenciones
        intenciones = self.intent_detector.detectar_intenciones(mensaje)
        
        # Analizar sentimiento
        sentimiento = self.sentiment_analyzer.analizar_sentimiento(mensaje)
        
        # Extraer información
        info_extraida = self.intent_detector.extraer_informacion(mensaje)
        
        # Actualizar lead con información extraída
        if info_extraida['tipo_servicio'] and not lead.tipo_servicio_interes:
            lead.tipo_servicio_interes = info_extraida['tipo_servicio']
        
        if info_extraida['presupuesto'] and not lead.presupuesto_estimado:
            lead.presupuesto_estimado = Decimal(str(info_extraida['presupuesto']))
        
        # Calcular score
        score = self.scorer.calcular_score(lead, mensaje)
        clasificacion = self.scorer.clasificar_lead(score)
        
        # Generar respuesta basada en intenciones
        respuesta = self._generar_respuesta(lead, intenciones, info_extraida)
        
        # Determinar siguiente acción
        siguiente_accion = self._determinar_siguiente_accion(clasificacion, intenciones)
        
        return {
            'respuesta': respuesta,
            'intenciones': intenciones,
            'sentimiento': sentimiento,
            'score': score,
            'clasificacion': clasificacion,
            'siguiente_accion': siguiente_accion,
            'info_extraida': info_extraida
        }
    
    def _generar_respuesta(self, lead, intenciones: List[str], info: Dict) -> str:
        """Genera una respuesta apropiada basada en las intenciones detectadas"""
        
        # Saludo inicial si es el primer mensaje
        if lead.conversaciones.count() == 0:
            return (
                f"¡Hola {lead.nombre}! 👋\n\n"
                "Soy tu asistente virtual de telecomunicaciones. "
                "Estoy aquí para ayudarte a encontrar el mejor plan para ti.\n\n"
                "¿En qué puedo ayudarte hoy?"
            )
        
        # Respuesta según intención principal
        if 'INTERES_COMPRA' in intenciones:
            if info['tipo_servicio']:
                return (
                    f"¡Excelente! Veo que estás interesado en {info['tipo_servicio']}. 📱\n\n"
                    "Para ofrecerte las mejores opciones, necesito saber:\n"
                    "1️⃣ ¿En qué zona vives?\n"
                    "2️⃣ ¿Cuál es tu presupuesto aproximado?\n\n"
                    "Así podré mostrarte los planes perfectos para ti. 😊"
                )
            else:
                return (
                    "¡Perfecto! Me encantaría ayudarte. 🎯\n\n"
                    "Tenemos planes de:\n"
                    "📱 Internet Hogar\n"
                    "📞 Planes Móviles\n"
                    "📺 TV por Cable\n"
                    "📦 Paquetes Combo\n\n"
                    "¿Cuál te interesa?"
                )
        
        elif 'CONSULTA_PRECIO' in intenciones:
            return (
                "Con gusto te ayudo con los precios. 💰\n\n"
                "Para darte información exacta, necesito saber:\n"
                "• ¿Qué tipo de servicio buscas? (Internet, Móvil, TV, Combo)\n"
                "• ¿En qué zona vives?\n\n"
                "Los precios varían según la zona y el plan. 📍"
            )
        
        elif 'CONSULTA_DISPONIBILIDAD' in intenciones:
            return (
                "Déjame verificar la cobertura en tu zona. 📍\n\n"
                "¿Podrías decirme tu distrito o zona específica?\n\n"
                "Así podré confirmarte qué operadores tienen cobertura allí."
            )
        
        elif 'OBJECION_PRECIO' in intenciones:
            return (
                "Entiendo tu preocupación por el precio. 💡\n\n"
                "Tenemos varias opciones que podrían ajustarse mejor a tu presupuesto:\n"
                "• Planes básicos desde $25/mes\n"
                "• Promociones especiales vigentes\n"
                "• Descuentos por pago adelantado\n\n"
                "¿Cuál sería tu presupuesto ideal?"
            )
        
        elif 'SOLICITUD_CONTACTO' in intenciones:
            return (
                "¡Por supuesto! Un agente se pondrá en contacto contigo pronto. 📞\n\n"
                "¿Prefieres que te llamemos o te escribamos por WhatsApp?\n"
                "¿En qué horario te viene mejor?"
            )
        
        elif 'COMPARACION' in intenciones:
            return (
                "Te ayudo a comparar las opciones. 📊\n\n"
                "Trabajamos con los principales operadores:\n"
                "• Claro\n"
                "• Movistar\n"
                "• Entel\n\n"
                "¿Qué tipo de servicio quieres comparar?"
            )
        
        else:
            # Respuesta genérica
            return (
                "Gracias por tu mensaje. 😊\n\n"
                "Puedo ayudarte con:\n"
                "📱 Información de planes\n"
                "💰 Precios y promociones\n"
                "📍 Cobertura en tu zona\n"
                "📞 Agendar una llamada\n\n"
                "¿Qué necesitas?"
            )
    
    def _determinar_siguiente_accion(self, clasificacion: str, intenciones: List[str]) -> str:
        """Determina la siguiente acción recomendada"""
        
        if clasificacion == 'HOT':
            return "🔥 URGENTE: Transferir a agente de ventas inmediatamente"
        
        elif clasificacion == 'WARM':
            if 'SOLICITUD_CONTACTO' in intenciones:
                return "📞 Agendar llamada en las próximas 2 horas"
            else:
                return "📧 Enviar información detallada y agendar seguimiento en 24h"
        
        else:  # COLD
            if 'CONSULTA_PRECIO' in intenciones:
                return "📊 Enviar catálogo de precios y agregar a campaña de nurturing"
            else:
                return "💡 Continuar conversación automática y educar sobre beneficios"


class CallAI:
    """Servicio de IA para llamadas telefónicas"""
    
    @staticmethod
    def generar_script_llamada(lead, tipo_llamada: str = 'SALIENTE') -> str:
        """Genera un script para la llamada basado en el lead"""
        
        if tipo_llamada == 'SALIENTE':
            script = f"""
Hola {lead.nombre}, buenos días/tardes.

Te llamo de [Nombre de la Empresa]. Hace unos días mostraste interés en nuestros servicios de telecomunicaciones.

¿Sigues interesado en {lead.get_tipo_servicio_interes_display() if lead.tipo_servicio_interes else 'nuestros servicios'}?

[ESPERAR RESPUESTA]

Si SÍ:
    Perfecto. Tengo una promoción especial que podría interesarte.
    {f'Para tu zona ({lead.zona})' if lead.zona else 'Para tu zona'}, tenemos planes desde $X/mes.
    ¿Te gustaría que te cuente los detalles?

Si NO:
    Entiendo. ¿Hay algo que te preocupe o alguna duda que pueda resolver?
    
Si OBJECIÓN DE PRECIO:
    Comprendo. Déjame contarte sobre nuestras opciones más económicas...

CIERRE:
    ¿Te parece si agendamos la instalación para esta semana?
"""
        else:  # ENTRANTE
            script = f"""
Gracias por llamar a [Nombre de la Empresa].

Mi nombre es [Agente]. ¿En qué puedo ayudarte hoy?

[ESCUCHAR NECESIDAD]

Perfecto, déjame ayudarte con eso.
Para darte la mejor opción, necesito saber:
1. ¿En qué zona vives?
2. ¿Qué tipo de servicio buscas?
3. ¿Cuál es tu presupuesto aproximado?

[RECOPILAR INFORMACIÓN]

Excelente. Tengo el plan perfecto para ti...
"""
        
        return script.strip()
    
    @staticmethod
    def analizar_transcripcion(transcripcion: str) -> Dict:
        """Analiza la transcripción de una llamada"""
        
        analyzer = SentimentAnalyzer()
        detector = IntentDetector()
        
        # Analizar sentimiento
        sentimiento = analyzer.analizar_sentimiento(transcripcion)
        
        # Detectar intenciones
        intenciones = detector.detectar_intenciones(transcripcion)
        
        # Detectar objeciones
        objeciones = []
        if 'OBJECION_PRECIO' in intenciones:
            objeciones.append('Precio alto')
        
        # Extraer palabras clave
        palabras_clave = []
        for palabra in ['precio', 'instalación', 'velocidad', 'cobertura', 'promoción']:
            if palabra in transcripcion.lower():
                palabras_clave.append(palabra)
        
        return {
            'sentimiento': sentimiento,
            'intenciones': intenciones,
            'objeciones': objeciones,
            'palabras_clave': palabras_clave,
            'duracion_palabras': len(transcripcion.split())
        }
