import json
from channels.generic.websocket import WebsocketConsumer

class MyWebSocketConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()  # Acceptă conexiunea WebSocket

    def disconnect(self, close_code):
        print('Client disconnected.')  # Afișează un mesaj la deconectare

    def receive(self, text_data):
        if text_data.startswith('{'):
            # Încercăm să interpretăm textul ca JSON
            try:
                text_data_json = json.loads(text_data)
                message = text_data_json.get('message', 'No message key found.')

                # Afișează mesajul primit în consola serverului
                print(f'Message received (JSON): {message}')

                # Trimite un răspuns înapoi clientului
                self.send(text_data=json.dumps({
                    'message': f'Received: {message}'
                }))
            except json.JSONDecodeError:
                print('Invalid JSON received.')  # Gestionare erori pentru JSON
                self.send(text_data=json.dumps({
                    'error': 'Invalid JSON format.'
                }))
        else:
            # Dacă nu este JSON, tratăm ca text simplu
            message = text_data

            # Afișează mesajul primit în consola serverului
            print(f'Message received (text): {message}')

            # Trimite un răspuns înapoi clientului
            self.send(text_data=json.dumps({
                'message': f'Received: {message}'
            }))
