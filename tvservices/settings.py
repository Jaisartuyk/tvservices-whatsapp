"""
Django settings for tvservices project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-your-secret-key-here')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True').lower() in ['true', '1', 'yes']

# ALLOWED_HOSTS configuration
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Add Railway domain if in production
if 'RAILWAY_ENVIRONMENT' in os.environ:
    railway_domain = os.environ.get('RAILWAY_STATIC_URL', '').replace('https://', '').replace('http://', '')
    if railway_domain and railway_domain not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(railway_domain)
    # Also add the production domain pattern
    ALLOWED_HOSTS.extend([
        'tvservices-whatsapp-production.up.railway.app',
        '*.up.railway.app',
        '*.railway.app'
    ])

# CSRF Configuration for Railway
CSRF_TRUSTED_ORIGINS = [
    'https://tvservices-whatsapp-production.up.railway.app',
    'http://tvservices-whatsapp-production.up.railway.app',
    'https://localhost:8000',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

# Add dynamic CSRF origins from environment
if 'RAILWAY_ENVIRONMENT' in os.environ:
    railway_url = os.environ.get('RAILWAY_STATIC_URL', '')
    if railway_url:
        # Ensure URL has scheme
        if not railway_url.startswith(('http://', 'https://')):
            railway_url = 'https://' + railway_url
        
        if railway_url not in CSRF_TRUSTED_ORIGINS:
            CSRF_TRUSTED_ORIGINS.append(railway_url)
            # Also add HTTP version
            http_url = railway_url.replace('https://', 'http://')
            if http_url not in CSRF_TRUSTED_ORIGINS:
                CSRF_TRUSTED_ORIGINS.append(http_url)

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'subscriptions.apps.SubscriptionsConfig',
    'callcenter.apps.CallcenterConfig',  # Call Center IA para Ecuador
    'crispy_forms',
    'crispy_bootstrap5',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # 'whitenoise.middleware.WhiteNoiseMiddleware',  # Desactivado temporalmente
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'tvservices.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'tvservices.wsgi.application'

# Database configuration
import dj_database_url

if 'DATABASE_URL' in os.environ:
    # Production (Railway) - PostgreSQL
    DATABASES = {
        'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
    }
else:
    # Development - SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'es-co'
# Configuración para Ecuador - Guayaquil
TIME_ZONE = 'America/Guayaquil'  # GMT-5
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

# Directories where Django looks for static files
STATICFILES_DIRS = []

# Add main static directory if it exists
static_dir = os.path.join(BASE_DIR, 'static')
if os.path.exists(static_dir):
    STATICFILES_DIRS.append(static_dir)

# Directory where collectstatic puts all static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Static files finders (Django will find static files in apps automatically)
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Static files storage - using default for now
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Whitenoise settings (desactivadas temporalmente)
# WHITENOISE_USE_FINDERS = True
# WHITENOISE_AUTOREFRESH = True

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# WaSender API Configuration
WASENDER_API_URL = os.environ.get('WASENDER_API_URL', 'https://wasenderapi.com')
WASENDER_API_KEY = os.environ.get('WASENDER_API_KEY', 'e736f86d08e73ce5ee6f209098dc701a60deb8157f26b79485f66e1249aabee6')
WASENDER_SESSION_ID = os.environ.get('WASENDER_SESSION_ID', '8359')
WASENDER_WEBHOOK_URL = os.environ.get('WASENDER_WEBHOOK_URL', 'https://www.iqautoec.com/webhook/whatsapp/')
WASENDER_WEBHOOK_SECRET = os.environ.get('WASENDER_WEBHOOK_SECRET', '')

# Notification Settings
NOTIFICATION_SETTINGS = {
    'ENABLE_WHATSAPP_NOTIFICATIONS': os.environ.get('ENABLE_WHATSAPP_NOTIFICATIONS', 'True').lower() == 'true',
    'NOTIFICATION_TIME_HOUR': int(os.environ.get('NOTIFICATION_TIME_HOUR', '9')),
}

# Configuración de logs
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'subscriptions': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# WhatsApp Notifications - WaSender API Configuration
# Obtener estas credenciales de https://wasenderapi.com/
WASENDER_API_URL = os.environ.get('WASENDER_API_URL', 'https://wasenderapi.com')
WASENDER_API_KEY = os.environ.get('WASENDER_API_KEY', '')
WASENDER_SESSION_ID = os.environ.get('WASENDER_SESSION_ID', '')
WASENDER_WEBHOOK_URL = os.environ.get('WASENDER_WEBHOOK_URL', '')
WASENDER_WEBHOOK_SECRET = os.environ.get('WASENDER_WEBHOOK_SECRET', '')

# Configuración de notificaciones
NOTIFICATION_SETTINGS = {
    'ENABLE_WHATSAPP_NOTIFICATIONS': True,
    'EXPIRATION_DAYS_NOTICE': [0, 1, 3, 7],  # Días antes del vencimiento para notificar (0 = vence hoy)
    'NOTIFICATION_TIME_HOUR': 9,  # Hora del día para enviar notificaciones (24h format)
}

# Authentication
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

# Stripe Configuration
STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY', 'your-stripe-public-key')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', 'your-stripe-secret-key')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', 'your-stripe-webhook-secret')
STRIPE_SUCCESS_URL = 'http://localhost:8000/payment/success/'
STRIPE_CANCEL_URL = 'http://localhost:8000/payment/cancel/'

# Crispy Forms Configuration
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Email Configuration (Development)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@tvservices.com'
