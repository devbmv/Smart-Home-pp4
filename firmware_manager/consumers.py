# light_app/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class MyWebSocketConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Acceptăm conexiunea WebSocket
        await self.accept()

    async def disconnect(self, close_code):
        # Acțiuni la deconectare
        pass

    async def receive(self, text_data):
        # Primesc mesajul de la client
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Trimit un răspuns înapoi la client
        await self.send(text_data=json.dumps({
            'message': f"Received : {message}"
        }))
