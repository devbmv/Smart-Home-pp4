import threading
import time
from django.contrib.sessions.models import Session
from light_app.models import UserSettings, User
from .context_processors import home_online_status
from time import sleep
import time
from django.utils import timezone
import logging
logger = logging.getLogger('my_custom_logger')
update=True
def start_permanent_task():
    global home_online_status,update
    while True:
        active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
        if active_sessions.exists():

            for user in User.objects.all():
                user_id = user.id
                try:
                    user_settings = UserSettings.objects.get(user=user)
                    if user_settings.test_mode:
                            
                        current_status = home_online_status.get(user_id, False)
                        home_online_status[user_id] = not current_status
                        update=True
                    else:
                        if update:
                            home_online_status[user_id] = False
                            update=False

                except UserSettings.DoesNotExist:
                    # Dacă utilizatorul nu are setări, continuăm cu următorul
                    continue
        sleep(user_settings.server_check_interval)
        logger.debug(user_settings.server_check_interval)


# Funcția pentru a porni thread-ul separat
def start_background_task():
    task_thread = threading.Thread(target=start_permanent_task)
    task_thread.daemon = True  # Oprește thread-ul când se oprește programul principal
    task_thread.start()

