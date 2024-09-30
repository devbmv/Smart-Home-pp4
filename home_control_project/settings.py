from pathlib import Path
import os
import dj_database_url
from django.contrib.messages import constants as messages
if os.path.isfile('env.py'):
    import env

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
SECRET_KEY = os.environ.get("SECRET_KEY")
DEBUG = os.getenv("DEBUG", "False") == "True"
ALLOWED_HOSTS = ['*.herokuapp.com',
                 '192.168.1.15', '192.168.1.7', '86.45.36.88']


API_USERNAME = os.getenv("DJANGO_API_USERNAME")
API_PASSWORD = os.getenv("DJANGO_API_PASSWORD")


# Installed applications
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "cloudinary_storage",
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
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
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# messages for users
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-secondary',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

ACCOUNT_EMAIL_VERIFICATION = "none"


# Înlocuiește cu numele proiectului tău
ASGI_APPLICATION = "home_control_project.asgi.application"
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
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
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "firmware_manager.context_processors.user_ip_processor",
                'light_app.context_processors.global_variables',
            ],
        },
    },
]


WSGI_APPLICATION = "home_control_project.wsgi.application"



DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL)
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

CSRF_TRUSTED_ORIGINS = [
    "https://*.gitpod.io",
    "https://*.heroku.com",
    "https://*192.168.1.15",
    "https://*192.168.1.7",
    "https://*86.45.36.88",
    
    
]

CLOUDINARY_URL = os.getenv("CLOUDINARY_URL")

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

STATIC_URL = '/static/'
STATICFILES_STORAGE = 'cloudinary_storage.storage.StaticHashedCloudinaryStorage'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# django_summernote config
SUMMERNOTE_CONFIG = {
    'summernote': {
        # Change editor size
        'width': '100%',
        'height': '480px',

        'fontNames': ['Lato', 'Sans Serif'],
        'fontNamesIgnoreCheck': ['Lato', 'Sans Serif'],
        'fontsizes': ['18'],
        'fontSizeUnits': ['px'],

        'disableResizeEditor': True,
    },
}
