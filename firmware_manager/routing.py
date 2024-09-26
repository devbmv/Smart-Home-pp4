# light_app/routing.py
from django.urls import path
from . import consumers  # Asigură-te că ai un fișier consumers.py

websocket_urlpatterns = [
    path('ws/goo/', consumers.MyWebSocketConsumer.as_asgi()),  # Definim ruta WebSocket
]
