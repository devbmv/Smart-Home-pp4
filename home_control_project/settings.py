import os
from pathlib import Path
import dj_database_url
from django.contrib.messages import constants as messages
import cloudinary
import cloudinary.uploader
import cloudinary.api
import django_heroku
# Load environment variables from 'env.py' if the file exists
if os.path.isfile(os.path.join(Path(__file__).resolve().parent.parent,
                               "env.py")):
    import env

# BASE_DIR holds the path to the project's root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# TEMPLATES_DIR holds the path to the templates folder
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# Load secret key from environment variables
SECRET_KEY = os.getenv("SECRET_KEY")

# Load debug mode from environment variables, default to False
DEBUG = os.getenv("DEBUG", "False") == "False"

# Allowed hosts configuration for both local and production environments
ALLOWED_HOSTS = [
    ".herokuapp.com",
    "192.168.1.15",
    "127.0.0.1",
    "192.168.1.7",
    "86.45.36.88",
    "home-control-dbba5bec072c.herokuapp.com",
    "*gitpod.io",
    "localhost"
]

# API credentials loaded from environment variables
API_USERNAME = os.getenv("DJANGO_API_USERNAME")
API_PASSWORD = os.getenv("DJANGO_API_PASSWORD")

# Installed applications (both third-party and custom)
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "cloudinary_storage",  # For Cloudinary storage
    "django.contrib.sites",
    "allauth",  # Django allauth for authentication
    "allauth.account",
    "allauth.socialaccount",
    "crispy_forms",  # For form styling
    "crispy_bootstrap5",  # Bootstrap 5 support for Crispy Forms
    "django_summernote",  # Text editor
    "cloudinary",  # Cloudinary media storage
    "django_resized",  # Resizing images
    "light_app",  # Custom app for handling light functionalities
    "firmware_manager",  # Custom app for firmware management
    "channels",  # Django Channels for WebSockets
    "django_extensions",  # Extensions for additional Django functionality
]

# Site ID configuration for Django sites framework
SITE_ID = 1

# Redirect URLs after login/logout
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# Crispy Forms configuration for Bootstrap 5
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Custom messages styling using Bootstrap
MESSAGE_TAGS = {
    messages.DEBUG: "alert-secondary",
    messages.INFO: "alert-info",
    messages.SUCCESS: "alert-success",
    messages.WARNING: "alert-warning",
    messages.ERROR: "alert-danger",
}

# Disabling email verification for Django allauth
ACCOUNT_EMAIL_VERIFICATION = "none"

# Channels configuration
ASGI_APPLICATION = "home_control_project.asgi.application"
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

# Middleware configuration for request handling and session management
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Static file serving for production
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Allauth middleware for authentication
    "allauth.account.middleware.AccountMiddleware",
    # Custom middleware for user settings
    "light_app.middleware.UserSettingsMiddleware",
    # Custom middleware for user language
    "light_app.middleware.UserLanguageMiddleware",
]

# Root URL configuration for the project
ROOT_URLCONF = "home_control_project.urls"

# Template configuration
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [TEMPLATES_DIR],  # Path to templates directory
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "firmware_manager.context_processors.user_ip_processor",
                "light_app.context_processors.global_variables",
            ],
        },
    },
]

# WSGI application for traditional web requests
WSGI_APPLICATION = "home_control_project.wsgi.application"

# DATABASE CONFIGURATION

# Database configuration using dj_database_url
DATABASES = {
    "default": dj_database_url.config(default=os.environ.get("DATABASE_URL"))
}
# Cloudinary configuration for storing media files
CLOUDINARY_URL = os.getenv("CLOUDINARY_URL")

# Static and media file configuration based on DEBUG mode
if DEBUG:
    # Development static and media files configuration
    STATIC_URL = "/static/"
    STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
    STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
    STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
    MEDIA_URL = "/media/"
    MEDIA_ROOT = os.path.join(BASE_DIR, "media")
else:
    # Production static and media files configuration
    STATIC_URL = "/static/"
    STATICFILES_STORAGE = "whitenoise.storage.\
        CompressedManifestStaticFilesStorage"
    STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
    STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
    MEDIA_URL = "/media/"
    DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.\
        MediaCloudinaryStorage"

# CSRF trusted origins configuration for securing
#  cross-site request forgery protection
CSRF_TRUSTED_ORIGINS = [
    "https://*.gitpod.io",
    "https://*.heroku.com",
    "https://192.168.1.15",
    "https://192.168.1.7",
    "https://86.45.36.88",
    "https://home-control-dbba5bec072c.herokuapp.com",
]

# Authentication password validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Summernote configuration for the text editor
SUMMERNOTE_CONFIG = {
    "summernote": {
        "width": "100%",
        "height": "480px",
        "fontNames": ["Lato", "Sans Serif"],
        "fontNamesIgnoreCheck": ["Lato", "Sans Serif"],
        "fontsizes": ["18"],
        "fontSizeUnits": ["px"],
        "disableResizeEditor": True,  # Prevent resizing the editor
    },
}

# Default primary key field type for Django models
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Apply Heroku-specific settings like static file handling and database
if "DYNO" in os.environ:
    django_heroku.settings(locals())
