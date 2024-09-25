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

env_path = Path(__file__).resolve().parent / "env.py"
if os.path.isfile("env.py"):
    try:
        import env
    except ImportError as e:
        print(f"Could not import env.py: {e}", file=sys.stderr)
else:
    print("env.py not found. Skipping environment variable setup.")
# Base directory for the project
home_online_status = {}

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("DEBUG", "False") == "False"
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
    CSRF_TRUSTED_ORIGINS = json.loads(os.getenv("CSRF_TRUSTED_ORIGINS", '["https://home-control-dbba5bec072c.herokuapp.com"]'))
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
    'debug_toolbar',
    "channels",
]
SITE_ID = 1

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"
ACCOUNT_EMAIL_VERIFICATION = "none"
# Channel layers for real-time communication (WebSockets)
ASGI_APPLICATION = "home_control_project.asgi.application"
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
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    'debug_toolbar.middleware.DebugToolbarMiddleware',
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
WSGI_APPLICATION = "home_control_project.wsgi.application"


if os.getenv('DATABASE_URL'):
    # Dacă ai variabila DATABASE_URL, folosește PostgreSQL (sau alta specificată)
    DATABASES = {
        'default': dj_database_url.config(default=os.getenv('DATABASE_URL'))
    }
else:
    # Dacă nu ai DATABASE_URL, folosește SQLite local
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
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
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Primary key field type

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
WHITENOISE_SKIP_COMPRESS_EXTENSIONS = {'js'}
django_heroku.settings(locals())
