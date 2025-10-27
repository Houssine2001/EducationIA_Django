"""
Configuration Django pour MongoDB avec Djongo
Copie de backend/settings.py adaptée pour MongoDB
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# Support multiple env var names and safer production defaults
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', os.getenv('SECRET_KEY', 'django-insecure-2ydi0(zc%3jtz!8pyqjp&g352lbs1g^i2kl*hh(w51g!j^y(n7'))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DJANGO_DEBUG', os.getenv('DEBUG', 'False')).lower() in ('1', 'true', 'yes')

# Allow configuring hosts via an env var (comma-separated)
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')

# CSRF Configuration for localhost
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
]

# CSRF - Configuration simplifiée pour développement
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_USE_SESSIONS = False
CSRF_COOKIE_NAME = 'csrftoken'
CSRF_HEADER_NAME = 'HTTP_X_CSRFTOKEN'

# Session Configuration - CORRECTION POUR DJONGO
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'  # Changé de 'db' à 'cache'
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
    'evaluation.apps.EvaluationConfig',  # Fix pour Djongo
    'exercise_generator',  # Générateur d'exercices IA
    'analytics_dashboard',
    'resources',  # Espace Apprenant & Publications de Ressources
]

MIDDLEWARE = [
    'backend.djongo_fix_middleware.DjongoFixMiddleware',  # FIX DJONGO EN PREMIER !
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise for serving static files on platforms like Azure App Service
    'whitenoise.middleware.WhiteNoiseMiddleware',
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
MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
MONGO_PORT = int(os.getenv('MONGO_PORT', 27017))
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'django_education')
MONGO_USERNAME = os.getenv('MONGO_USERNAME', '')
MONGO_PASSWORD = os.getenv('MONGO_PASSWORD', '')

# Full MongoDB URI (Atlas). If provided, prefer this for SRV connections.
MONGO_URI = os.getenv('MONGO_URI', '').strip()

# Configuration de la base de données
# Le projet utilise Djongo/MongoDB en production. Pour faciliter la dockerisation
# en développement (et éviter des conflits de versions dans l'image), on permet
# d'utiliser SQLite lorsque USE_MONGO != '1'.
USE_MONGO = os.getenv('USE_MONGO', '0') == '1'

if USE_MONGO:
    # Prefer a full MONGO_URI (mongodb+srv://...) when present (required for Atlas SRV)
    client = {}
    if MONGO_URI:
        client['host'] = MONGO_URI
    else:
        # Fallback to host/port style (useful when running a local mongo container)
        client.update({
            'host': MONGO_HOST,
            'port': MONGO_PORT,
            'serverSelectionTimeoutMS': 5000,
            'connectTimeoutMS': 30000,
            'socketTimeoutMS': None,
            'maxPoolSize': 50,
            'minPoolSize': 10,
            'maxIdleTimeMS': None,
        })

    DATABASES = {
        'default': {
            'ENGINE': 'djongo',
            'NAME': MONGO_DB_NAME,
            'ENFORCE_SCHEMA': False,
            'CONN_MAX_AGE': None,
            'CLIENT': client,
        }
    }
else:
    # Fallback simple pour le développement local / docker sans MongoDB
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
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
