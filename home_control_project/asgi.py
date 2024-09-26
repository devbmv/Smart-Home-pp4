# asgi.py

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from firmware_manager.routing import (
    websocket_urlpatterns,
)  # Asigură-te că ai definit websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "home_control_project.settings")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)  # Definește rutele WebSocket
        ),
    }
)
