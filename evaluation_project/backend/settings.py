"""
Configuration Django pour MongoDB avec Djongo
Copie de backend/settings.py adaptée pour MongoDB
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', os.getenv('SECRET_KEY', 'django-insecure-temp-key'))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False  # Toujours False en production

# Autoriser le domaine Azure
ALLOWED_HOSTS = ['django-education-app-hwevdqa0ara5fwgp.francecentral-01.azurewebsites.net']

# CSRF Configuration
CSRF_TRUSTED_ORIGINS = [
    'django-education-app-hwevdqa0ara5fwgp.francecentral-01.azurewebsites.net',
]

CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_USE_SESSIONS = False
CSRF_COOKIE_NAME = 'csrftoken'
CSRF_HEADER_NAME = 'HTTP_X_CSRFTOKEN'

# Session Configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 86400  # 24 heures

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Applications personnalisées
    'evaluation.apps.EvaluationConfig',
    'exercise_generator',
    'analytics_dashboard',
    'resources',
]

MIDDLEWARE = [
    'backend.djongo_fix_middleware.DjongoFixMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'backend.middleware.SubjectVisitTrackingMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'

# =============================================================================
# CONFIGURATION MONGODB AVEC DJONGO
# =============================================================================
USE_MONGO = True
MONGO_URI = 'mongodb+srv://salmamejri17_db_user:IdBS3lUgfmYEyGQ8@cluster.uxsk5qc.mongodb.net/?appName=Cluster'

DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'django_education',
        'ENFORCE_SCHEMA': False,
        'CLIENT': {
            'host': MONGO_URI,
        }
    }
}

# =============================================================================
# FIN CONFIGURATION MONGODB
# =============================================================================

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# Authentication backends
AUTHENTICATION_BACKENDS = [
    'evaluation.auth_backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Internationalization
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# === Production static files + sécurité TLS (Whitenoise) ===
if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Session configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400

# Authentication
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler',},
        'file': {'class': 'logging.FileHandler','filename': BASE_DIR / 'logs' / 'django.log',},
    },
    'loggers': {
        'django': {'handlers': ['console', 'file'],'level': 'INFO',},
        'djongo': {'handlers': ['console', 'file'],'level': 'DEBUG',},
    },
}

# Créer le dossier logs s'il n'existe pas
os.makedirs(BASE_DIR / 'logs', exist_ok=True)
