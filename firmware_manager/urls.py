# urls.py (în aplicația ta Django)
from django.urls import path
from . import views  # Pentru views HTTP
from . import consumers  # Pentru WebSocket
from django.urls import re_path


urlpatterns = [
    path('update_esp_firmware/', views.update_esp_firmware,
         name='update_esp_firmware'),
    path('upload_firmware/', views.upload_firmware, name='upload_firmware'),
    path('upload_to_esp32/', views.upload_to_esp32, name='upload_to_esp32'),
    path('chat/', views.chatHome, name='chat'),
]
