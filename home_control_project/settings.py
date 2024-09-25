import os
from pathlib import Path
import dj_database_url
from django.contrib.messages import constants as messages
import django_heroku
from django.utils.translation import gettext_lazy as _
import json
import sys

env_path = Path(__file__).resolve().parent / "env.py"
if env_path.exists():
    try:
        import env
    except ImportError as e:
        print(f"Could not import env.py: {e}", file=sys.stderr)
else:
    print("env.py not found. Skipping environment variable setup.")
# Base directory for the project
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# Reading environment variables
SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("DEBUG", "False") == "True"

API_USERNAME = os.getenv("DJANGO_API_USERNAME")
API_PASSWORD = os.getenv("DJANGO_API_PASSWORD")
home_online_status = {}

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


def debug(data):
    if DEBUG:
        print(data)


# Allowed hosts configuration
# try:
#ALLOWED_HOSTS = ["*"]  # json.loads(os.getenv("ALLOWED_HOSTS", "[]"))
ALLOWED_HOSTS = ['*']

# except json.JSONDecodeError:
#     ALLOWED_HOSTS = []
#     print("Invalid ALLOWED_HOSTS format, defaulting to empty list.")

# try:
CSRF_TRUSTED_ORIGINS = json.loads(os.getenv("CSRF_TRUSTED_ORIGINS", "[]"))
CORS_ALLOW_ALL_ORIGINS = True

# except json.JSONDecodeError:
#     CSRF_TRUSTED_ORIGINS = []
#     print("Invalid CSRF_TRUSTED_ORIGINS format, defaulting to empty list.")

# Installed applications
INSTALLED_APPS = [
    # Aplicațiile esențiale ale Django
    "django.contrib.sites",  # Pune `django.contrib.sites` după aplicațiile esențiale Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Aplicații terțe
    "cloudinary_storage",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "crispy_forms",
    "crispy_bootstrap5",
    "django_summernote",
    "cloudinary",
    "django_resized",
    "django_extensions",
    # Aplicațiile tale personalizate
    "light_app",
    "firmware_manager",
    # `channels` după celelalte aplicații
    "channels",
]


# Channel layers for real-time communication (WebSockets)
ASGI_APPLICATION = "home_control_project.asgi.application"
CHANNEL_LAYERS = {
'default': {
    'BACKEND': 'channels.layers.InMemoryChannelLayer',
},
}


# Authentication settings
SITE_ID = 1
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"
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
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
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
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "light_app.context_processors.home_status_processor",  # Calea către funcția context processor
                "firmware_manager.context_processors.user_ip_processor",  # Adaugă aici context processor-ul tău
            ],
        },
    },
]

# WSGI application
WSGI_APPLICATION = "home_control_project.asgi.application"
if not DEBUG
    DATABASES = {
            "default": dj_database_url.config(
                conn_max_age=1800,  # Menține conexiunile deschise timp de 30 de minute
                ssl_require=True,   # Asigură-te că conexiunea folosește SSL pentru securitate
            )
        }

else:
    # Configurare pentru local (de exemplu SQLite sau PostgreSQL local)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",  # Sau PostgreSQL local
            "NAME": BASE_DIR / "db.sqlite3",  # Dacă vrei să folosești SQLite local
            # Pentru PostgreSQL local, folosește următoarele setări:
            # 'ENGINE': 'django.db.backends.postgresql_psycopg2',
            # 'NAME': 'numele_bazei_de_date',
            # 'USER': 'utilizatorul_tau',
            # 'PASSWORD': 'parola_ta',
            # 'HOST': 'localhost',
            # 'PORT': '5432',
        }
    }

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
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Primary key field type

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

if not DEBUG:
    # Configurații specifice pentru producție
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"

    # Configurare SSL pentru Heroku
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    django_heroku.settings(locals())
else:
    # Configurații pentru mediul local
    SECURE_SSL_REDIRECT = False
    SECURE_HSTS_SECONDS = 0
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False
