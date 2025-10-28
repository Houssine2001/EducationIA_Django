# settings.py - Django 4.x - Azure + Docker + MongoDB Atlas (sans .env)

from pathlib import Path
import os

# ============================
# PATHS
# ============================
BASE_DIR = Path(__file__).resolve().parent.parent

# ============================
# SECRET & DEBUG
# ============================
SECRET_KEY = "3zkgq8zc10vqj9q($4ftu!i#6a&1n(^7%l!x$^_29$kv+@jd38"  # Remplace par ta clé sécurisée
DEBUG = False  # False pour production

# ============================
# ALLOWED HOSTS
# ============================
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'asp-django-container-fthxd3adcjb5hwgt.italynorth-01.azurewebsites.net',
]

# ============================
# CSRF & SESSION
# ============================
CSRF_TRUSTED_ORIGINS = [
    'https://asp-django-container-fthxd3adcjb5hwgt.italynorth-01.azurewebsites.net',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 86400  # 24h

# ============================
# APPLICATIONS
# ============================
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
    'backend.djongo_fix_middleware.DjongoFixMiddleware',  # si utilisé
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
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

# ============================
# DATABASE (MongoDB Atlas)
# ============================
USE_MONGO = True
MONGO_URI = "mongodb+srv://salmamejri17_db_user:IdBS3lUgfmYEyGQ8@cluster.uxsk5qc.mongodb.net/?retryWrites=true&w=majority"
MONGO_DB_NAME = "django_education"

if USE_MONGO:
    DATABASES = {
        'default': {
            'ENGINE': 'djongo',
            'NAME': MONGO_DB_NAME,
            'ENFORCE_SCHEMA': False,
            'CLIENT': {
                'host': MONGO_URI,
            },
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ============================
# AUTHENTICATION
# ============================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTHENTICATION_BACKENDS = [
    'evaluation.auth_backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
]

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# ============================
# INTERNATIONALIZATION
# ============================
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_TZ = True

# ============================
# STATIC & MEDIA
# ============================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ============================
# LOGGING
# ============================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
        'file': {'class': 'logging.FileHandler', 'filename': BASE_DIR / 'logs' / 'django.log'},
    },
    'loggers': {
        'django': {'handlers': ['console', 'file'], 'level': 'INFO'},
        'djongo': {'handlers': ['console', 'file'], 'level': 'DEBUG'},
    },
}

# Créer le dossier logs s'il n'existe pas
os.makedirs(BASE_DIR / 'logs', exist_ok=True)
