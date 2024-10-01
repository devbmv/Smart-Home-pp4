"""
ASGI configuration for home_control_project.

This file configures the ASGI application which is responsible for handling 
HTTP and WebSocket connections.
It includes a ProtocolTypeRouter that handles HTTP requests using Django's 
ASGI application and WebSocket
connections using Django Channels' routing system.

For more information on this file, see:
https://channels.readthedocs.io/en/stable/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from firmware_manager.routing import websocket_urlpatterns  

# Set the default settings module for the 'asgi' application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", 
                      "home_control_project.settings")

# Define the ASGI application, handling both HTTP and WebSocket protocols
application = ProtocolTypeRouter(
    {
        # HTTP requests are handled by Django's ASGI application
        "http": get_asgi_application(),
        
        # WebSocket connections are handled via the Channels routing and
        #  authentication stack
        "websocket": AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)  # Define URL routing for WebS.
        ),
    }
)
