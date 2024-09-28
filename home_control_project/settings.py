import os
from pathlib import Path
import dj_database_url
from django.contrib.messages import constants as messages
import django_heroku
from django.utils.translation import gettext_lazy as _
import json
import sys
from pathlib import Path
import os
import dj_database_url
import cloudinary
import cloudinary.uploader
import cloudinary.api
import logging

env_path = Path(__file__).resolve().parent / "env.py"
if os.path.isfile("env.py"):
    try:
        import env
    except ImportError as e:
        print(f"Could not import env.py: {e}", file=sys.stderr)
else:
    print("env.py not found. Skipping environment variable setup.")
# Base directory for the project

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("DEBUG")=="True"
API_USERNAME = os.getenv("DJANGO_API_USERNAME")
API_PASSWORD = os.getenv("DJANGO_API_PASSWORD")
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


def debug(data):
    if DEBUG:
        print(data)


# Allowed hosts configuration
try:
    ALLOWED_HOSTS = json.loads(os.getenv("ALLOWED_HOSTS", "[]"))

except json.JSONDecodeError:
    ALLOWED_HOSTS = []
    print("Invalid ALLOWED_HOSTS format, defaulting to empty list.")

try:
    CSRF_TRUSTED_ORIGINS = json.loads(
        os.getenv(
            "CSRF_TRUSTED_ORIGINS",
            '["https://home-control-dbba5bec072c.herokuapp.com"]',
        )
    )
    CORS_ALLOW_ALL_ORIGINS = True

except json.JSONDecodeError:
    CSRF_TRUSTED_ORIGINS = []
    print("Invalid CSRF_TRUSTED_ORIGINS format, defaulting to empty list.")

# Installed applications
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "cloudinary_storage",
    "django.contrib.staticfiles",
    "cloudinary",
    "allauth.socialaccount.providers.google",
    "crispy_forms",
    "crispy_bootstrap5",
    "django_summernote",
    "django_resized",
    "django_extensions",
    "light_app",
    "firmware_manager",
    "debug_toolbar",
    "channels",
]
SITE_ID = 1

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"
ACCOUNT_EMAIL_VERIFICATION = "none"
# Channel layers for real-time communication (WebSockets)
ASGI_APPLICATION = "home_control_project.asgi.application"  # Înlocuiește cu numele proiectului tău
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}


# Authentication settings
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Django messages settings (Bootstrap compatibility)
MESSAGE_TAGS = {
    messages.DEBUG: "alert-secondary",
    messages.INFO: "alert-info",
    messages.SUCCESS: "alert-success",
    messages.WARNING: "alert-warning",
    messages.ERROR: "alert-danger",
}

# Middleware configuration
MIDDLEWARE = [
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "light_app.middleware.UserSettingsMiddleware",
    "light_app.middleware.UserLanguageMiddleware",
]

ROOT_URLCONF = "home_control_project.urls"

# Template configuration
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [TEMPLATES_DIR],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
                "firmware_manager.context_processors.user_ip_processor", 
                'light_app.context_processors.global_variables',
            ],
        },
    },
]


# WSGI application
WSGI_APPLICATION = "home_control_project.wsgi.application"

if DEBUG:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": dj_database_url.config(
            default=os.getenv("DATABASE_URL")
        )
    }

print("DEBUG:", DEBUG)
print("DATABASES:", DATABASES)

CLOUDINARY_URL = os.getenv("CLOUDINARY_URL")

# Password validation settings
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# AllAuth settings
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = "username"
ACCOUNT_USERNAME_REQUIRED = True

# Internationalization settings
LANGUAGE_CODE = "en-us"
LANGUAGES = [
    ("en", _("English")),
    ("fr", _("French")),
    ("de", _("German")),
]
LOCALE_PATHS = [os.path.join(BASE_DIR, "locale")]

USE_I18N = True
TIME_ZONE = "UTC"
USE_L10N = True
USE_TZ = True

# Static files configuration
STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

if DEBUG:
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
    MEDIA_ROOT = os.path.join(BASE_DIR, "media")
else:
    DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Primary key field type
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Salvează sesiunile în baza de date
# Durata de viață a sesiunii în secunde (de exemplu, 2 săptămâni)
SESSION_COOKIE_AGE = 1209600  # 2 săptămâni

# Asigură-te că sesiunea nu expiră la închiderea browserului
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
CSRF_COOKIE_AGE = 31449600  # 1 an

# Asigură-te că Django salvează sesiunea la fiecare cerere, chiar dacă nu este modificată
SESSION_SAVE_EVERY_REQUEST = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
WHITENOISE_SKIP_COMPRESS_EXTENSIONS = {"js"}
if "DYNO" in os.environ:  # Dacă rulezi pe Heroku (sau altă platformă cu variabila DYNO)
    django_heroku.settings(locals())
    SESSION_COOKIE_SECURE = True  # Asigură-te că aceste cookie-uri sunt trimise doar prin HTTPS
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True  # Redirecționează automat HTTP -> HTTPS în producție
    SECURE_HSTS_SECONDS = 31536000  # Activează HSTS pentru un an
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
else:
    SESSION_COOKIE_SECURE = False  # În dezvoltare locală fără HTTPS
    CSRF_COOKIE_SECURE = False
    SECURE_SSL_REDIRECT = False


    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,  # Păstrează loggerii existenți activi
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            # Logger personalizat pentru logurile tale
            'my_custom_logger': {
                'handlers': ['console'],
                'level': 'DEBUG',  # Schimbă la INFO sau WARNING dacă vrei să filtrezi nivelul
                'propagate': False,
            },
            # Logger pentru request-urile HTTP Django
            'django': {
                'handlers': ['console'],
                'level': 'INFO',  # INFO sau DEBUG pentru a afișa request-urile și alte informații
                'propagate': True,
            },
            'django.request': {
                'handlers': ['console'],
                'level': 'DEBUG',  # DEBUG pentru a vedea toate request-urile și răspunsurile
                'propagate': False,
            },
        },
    }
