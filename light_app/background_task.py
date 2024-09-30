import threading
import time
from django.contrib.sessions.models import Session
from light_app.models import UserSettings, User
from .context_processors import home_online_status
from time import sleep
import requests
from django.utils import timezone
import logging
from .context_processors import debug
logger = logging.getLogger('my_custom_logger')

update = True
response_text = ""
count = 0
lock = threading.Lock()

def start_permanent_task():
    global home_online_status, update, response_text, count
    while True:
        active_sessions = Session.objects.filter(
            expire_date__gte=timezone.now())
        if active_sessions.exists():

            for user in User.objects.all():
                user_id = user.id
                try:
                    user_settings = UserSettings.objects.get(user=user)
                    if user_settings.test_mode:
                        with lock:
                            current_status = home_online_status.get(user_id, False)
                            home_online_status[user_id] = not current_status
                        update = True
                    else:
                        try:
                            response = requests.get(
                                f"http://{user_settings.m5core2_ip}?check_interval={user_settings.server_check_interval}", timeout=5)
                            if response.status_code == 200:
                                count += 1
                                debug(f"home_online {count}")
                                with lock:
                                    home_online_status[user_id] = True
                            else:
                                debug(f"home_Offline {count}")
                                with lock:
                                    home_online_status[user_id] = False
                        except requests.exceptions.RequestException as e:
                            with lock:
                                home_online_status[user_id] = False
                            response_text = f"Server offline: {e}"
                            logger.error(response_text)
                except UserSettings.DoesNotExist:
                    # Dacă utilizatorul nu are setări, continuăm cu următorul
                    continue

        # Verifică dacă `user_settings` este definit înainte de a folosi `server_check_interval`
        if 'user_settings' in locals():
            sleep(user_settings.server_check_interval)
        else:
            # Dacă nu există `user_settings`, setează un timp de așteptare implicit (ex. 10 secunde)
            sleep(10)

# Funcția pentru a porni thread-ul separat
def start_background_task():
    task_thread = threading.Thread(target=start_permanent_task)
    task_thread.daemon = True  # Oprește thread-ul când se oprește programul principal
    task_thread.start()
