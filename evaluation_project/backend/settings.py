"""
Configuration Django pour MongoDB avec Djongo
Copie de backend/settings.py adaptée pour MongoDB
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-2ydi0(zc%3jtz!8pyqjp&g352lbs1g^i2kl*hh(w51g!j^y(n7')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True') == 'True'

# Allowed hosts - pour production
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost,testserver').split(',')
# Nettoyer les espaces
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS]

# CSRF Configuration
CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', 'http://127.0.0.1:8000,http://localhost:8000').split(',')
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in CSRF_TRUSTED_ORIGINS]

# CSRF - Configuration sécurisée pour production
CSRF_COOKIE_SECURE = not DEBUG  # True en production
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_USE_SESSIONS = False
CSRF_COOKIE_NAME = 'csrftoken'
CSRF_HEADER_NAME = 'HTTP_X_CSRFTOKEN'

# Session Configuration - CORRECTION POUR DJONGO
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'  # Changé de 'db' à 'cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_SECURE = not DEBUG  # True en production
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
    'evaluation.apps.EvaluationConfig',  # Fix pour Djongo
    'exercise_generator',  # Générateur d'exercices IA
    'analytics_dashboard',
    'resources',  # Espace Apprenant & Publications de Ressources
]

MIDDLEWARE = [
    'backend.djongo_fix_middleware.DjongoFixMiddleware',  # FIX DJONGO EN PREMIER !
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Pour servir les fichiers statiques en production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'backend.middleware.SubjectVisitTrackingMiddleware',  # Tracking automatique des visites
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

# Récupérer les variables d'environnement
# Pour MongoDB Atlas, utilisez MONGODB_URI
MONGODB_URI = os.getenv('MONGODB_URI', '')

# Pour MongoDB local (développement)
MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
MONGO_PORT = int(os.getenv('MONGO_PORT', 27017))
MONGO_DB_NAME = os.getenv('MONGODB_NAME', 'django_education')
MONGO_USERNAME = os.getenv('MONGO_USERNAME', '')
MONGO_PASSWORD = os.getenv('MONGO_PASSWORD', '')

# Configuration de la base de données
if MONGODB_URI:
    # Configuration pour MongoDB Atlas (Production)
    DATABASES = {
        'default': {
            'ENGINE': 'djongo',
            'NAME': MONGO_DB_NAME,
            'ENFORCE_SCHEMA': False,
            'CLIENT': {
                'host': MONGODB_URI,
            }
        }
    }
else:
    # Configuration pour MongoDB local (Développement)
    DATABASES = {
        'default': {
            'ENGINE': 'djongo',
            'NAME': MONGO_DB_NAME,
            'ENFORCE_SCHEMA': False,
            'CONN_MAX_AGE': None,
            'CLIENT': {
                'host': MONGO_HOST,
                'port': MONGO_PORT,
                'serverSelectionTimeoutMS': 5000,
                'connectTimeoutMS': 30000,
                'socketTimeoutMS': None,
                'maxPoolSize': 50,
                'minPoolSize': 10,
                'maxIdleTimeMS': None,
            },
        }
    }


# Alternative : MongoDB Atlas (cloud)
# Si vous utilisez MongoDB Atlas, décommentez et configurez :
"""
DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': MONGO_DB_NAME,
        'ENFORCE_SCHEMA': False,
        'CLIENT': {
            'host': os.getenv('MONGO_URI', 'mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority'),
        }
    }
}
"""

# =============================================================================
# FIN CONFIGURATION MONGODB
# =============================================================================


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

# Authentication backends - Permet la connexion avec email
AUTHENTICATION_BACKENDS = [
    'evaluation.auth_backends.EmailBackend',  # Backend personnalisé (email ou username)
    'django.contrib.auth.backends.ModelBackend',  # Backend par défaut (fallback)
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

# Configuration de WhiteNoise pour les fichiers statiques en production
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Media files (uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Session configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400  # 24 heures


# Authentication
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'


# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
        'djongo': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
    },
}

# Créer le dossier logs s'il n'existe pas
os.makedirs(BASE_DIR / 'logs', exist_ok=True)
