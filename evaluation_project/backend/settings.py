from pathlib import Path
import os

# ============================
# PATHS
# ============================
BASE_DIR = Path(__file__).resolve().parent.parent

# ============================
# SECRET & DEBUG (Lire depuis ENV)
# ============================
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', "3zkgq8zc10vqj9q($4ftu!i#6a&1n(^7%l!x$^_29$kv+@jd38")
DEBUG = os.getenv('DEBUG', '0') == '1'  # '1' = True, '0' = False

print(f"🔧 Django DEBUG mode: {DEBUG}")
print(f"🔧 SECRET_KEY loaded: {'Yes' if SECRET_KEY else 'No'}")

# ============================
# ALLOWED HOSTS - Compatible Render
# ============================
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.onrender.com',  # Tous les sous-domaines Render
]

# ============================
# CSRF & SESSION
# ============================
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

# Ajouter dynamiquement les domaines Render
if not DEBUG:
    CSRF_TRUSTED_ORIGINS.extend([
        'https://*.onrender.com',
    ])

CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 86400

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
    'evaluation.apps.EvaluationConfig',
    'exercise_generator',
    'analytics_dashboard',
    'resources',
]

MIDDLEWARE = [
    'backend.djongo_fix_middleware.DjongoFixMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # WhiteNoise pour static files
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
# DATABASE (MongoDB Atlas - Lire depuis ENV)
# ============================
USE_MONGO = os.getenv('USE_MONGO', '1') == '1'
MONGO_URI = os.getenv('MONGO_URI', 'mongodb+srv://salmamejri17_db_user:IdBS3lUgfmYEyGQ8@cluster.uxsk5qc.mongodb.net/?appName=Cluster')
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'django_education')

print(f"🔧 USE_MONGO: {USE_MONGO}")
print(f"🔧 MONGO_DB_NAME: {MONGO_DB_NAME}")
print(f"🔧 MONGO_URI: {MONGO_URI[:50]}... (truncated)")

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
# STATIC & MEDIA FILES (Optimisé pour Render avec WhiteNoise)
# ============================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Configuration WhiteNoise pour compression et cache
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

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
    },
    'loggers': {
        'django': {'handlers': ['console'], 'level': 'INFO'},
        'djongo': {'handlers': ['console'], 'level': 'DEBUG'},
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'