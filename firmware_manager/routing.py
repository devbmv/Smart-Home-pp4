from django.urls import path
from .consumers import MyWebSocketConsumer

websocket_urlpatterns = [
    path('ws/socket-server/', MyWebSocketConsumer.as_asgi()),
]
