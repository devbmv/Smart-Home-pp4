import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from asgiref.sync import sync_to_async


class MyWebSocketConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json.get("action")
        attribute_name = text_data_json.get("attribute_name")
        user_id = text_data_json.get("user_id")

        if action is None or attribute_name is None:
            await self.send(text_data=json.dumps({
                'error': "Action or attribute name was not\
                      provided or is invalid."
            }))
            return

        try:
            # Dacă acțiunea este `get`, returnăm valoarea variabilei
            if action == "get":
                await self.handle_get_request(attribute_name, user_id)

            # Dacă acțiunea este `set`, setăm valoarea variabilei
            elif action == "set":
                value = text_data_json.get("value")
                if value is None:
                    await self.send(text_data=json.dumps({
                        'error': "Value for setting the attribute \
                            was not provided."
                    }))
                    return

                await self.handle_set_request(attribute_name, value, user_id)

            else:
                await self.send(text_data=json.dumps({
                    'error': "Invalid action. Supported actions\
                          are 'get' and 'set'."
                }))

        except Exception as e:
            await self.send(text_data=json.dumps({
                'error': f"An error occurred: {str(e)}"
            }))

    async def handle_get_request(self, attribute_name, user_id):
        """
        Gestionăm cererea de a obține un atribut din settings.py\
              sau dintr-un model.
        """
        from light_app.models import UserSettings
        from django.contrib.auth.models import User

        # Încercăm să obținem variabila din settings.py
        if hasattr(settings, attribute_name):
            value = getattr(settings, attribute_name)
            await self.send(text_data=json.dumps({
                'attribute_name': attribute_name,
                'value': value
            }))
        else:
            try:
                user = await sync_to_async(User.objects.get)(id=user_id)
                user_settings = await sync_to_async(UserSettings.
                                                    objects.get)(user=user)

                if hasattr(user_settings, attribute_name):
                    value = getattr(user_settings, attribute_name)
                    await self.send(text_data=json.dumps({
                        'attribute_name': attribute_name,
                        'value': value
                    }))
                else:
                    await self.send(text_data=json.dumps({
                        'error': f"Attribute '{attribute_name}'\
                              does not exist in UserSettings."
                    }))
            except User.DoesNotExist:
                await self.send(text_data=json.dumps({
                    'error': f"User with ID '{user_id}' does not exist."
                }))
            except UserSettings.DoesNotExist:
                await self.send(text_data=json.dumps({
                    'error': f"User settings for user ID '{user_id}'\
                          do not exist."
                }))

    async def handle_set_request(self, attribute_name, value, user_id):
        """
        Gestionăm cererea de a seta un atribut \
            în settings.py sau într-un model.
        """
        from light_app.models import UserSettings
        from django.contrib.auth.models import User

        # Încercăm să setăm în settings.py
        if hasattr(settings, attribute_name):
            value_casted = self.cast_value(value)
            setattr(settings, attribute_name, value_casted)

            await self.send(text_data=json.dumps({
                'message': f"Attribute '{attribute_name}'\
                      in settings set to '{value_casted}'."
            }))
        else:
            try:
                user = await sync_to_async(User.objects.get)(id=user_id)
                user_settings = (await sync_to_async(UserSettings.
                                                     objects.get)(user=user))

                if hasattr(user_settings, attribute_name):
                    value_casted = self.cast_value(value)
                    setattr(user_settings, attribute_name, value_casted)
                    await sync_to_async(user_settings.save)()

                    await self.send(text_data=json.dumps({
                        'message': f"Attribute '{attribute_name}'\
                              in UserSettings set to '{value_casted}'."
                    }))
                else:
                    await self.send(text_data=json.dumps({
                        'error': f"Attribute '{attribute_name}' \
                            does not exist in UserSettings."
                    }))
            except User.DoesNotExist:
                await self.send(text_data=json.dumps({
                    'error': f"User with ID '{user_id}' does not exist."
                }))
            except UserSettings.DoesNotExist:
                await self.send(text_data=json.dumps({
                    'error': f"User settings for user ID '{user_id}' \
                        do not exist."
                }))

    def cast_value(self, value):
        """ Convertește valoarea într-un tip Python corespunzător """
        if isinstance(value, str):
            value = value.lower()
            if value == "true":
                return True
            elif value == "false":
                return False
            elif value.isdigit():
                return int(value)
            try:
                return float(value)
            except ValueError:
                return value
        return value
