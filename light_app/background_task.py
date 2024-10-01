import threading
from time import sleep
from django.contrib.sessions.models import Session
from django.utils import timezone
import requests
import logging
from light_app.models import UserSettings, User
from .context_processors import home_online_status, debug

# Initialize logger for custom logging
logger = logging.getLogger("my_custom_logger")

# Global variables
update = True
response_text = ""
count = 0
lock = threading.Lock()


def start_permanent_task():
    """
    This function runs a continuous background task that monitors user
      settings and checks the status of the user's
    M5Core2 device. It updates the `home_online_status` dictionary for
      each user based on the device's status.

    The task:
    - Checks if there are active user sessions.
    - If a user is in "test mode", it toggles their `home_online_status`.
    - Otherwise, it sends an HTTP request to the user's M5Core2 IP to check 
    if the device is online.
    - Logs and handles any errors related to connectivity.

    This function is designed to run indefinitely within a separate thread.

    Returns:
        None
    """
    global home_online_status, update, response_text, count

    while True:
        # Retrieve active sessions
        active_sessions = Session.objects.filter(
            expire_date__gte=timezone.now())

        if active_sessions.exists():
            for user in User.objects.all():
                user_id = user.id
                try:
                    # Retrieve user settings
                    user_settings = UserSettings.objects.get(user=user)

                    # Check if the user is in test mode
                    if user_settings.test_mode:
                        with lock:
                           # Toggle the current home_online_status for the user
                            current_status = home_online_status.get(user_id, False)
                            home_online_status[user_id] = not current_status
                        update = True

                    else:
                        try:
                        # Send a GET request to check the M5Core2 device status
                            response = requests.get(
                                f"http://{user_settings.m5core2_ip}?check_interval={user_settings.server_check_interval}",
                                timeout=30,
                            )

                            if response.status_code == 200:
                                count += 1
                                debug(f"home_online {count}")

                                with lock:
                                    # Mark home as online
                                    home_online_status[user_id] = True
                            else:
                                debug(f"home_Offline {count}")
                                with lock:
                                    # Mark home as offline
                                    home_online_status[user_id] = False
                        except requests.exceptions.RequestException as e:
                            # Handle connection error, mark home as offline
                            with lock:
                                home_online_status[user_id] = False
                            response_text = f"Server offline: {e}"
                            logger.error(response_text)

                except UserSettings.DoesNotExist:
                    # If UserSettings do not exist for a user, skip them
                    continue

        # Sleep for the defined interval
        if "user_settings" in locals():
            sleep(user_settings.server_check_interval)
        else:
            sleep(10)


def start_background_task():
    """
    Starts the permanent background task that monitors the user's home status
      in a separate daemon thread.
    This thread will run continuously and update home statuses without 
    blocking the main application.

    Returns:
        None
    """
    task_thread = threading.Thread(target=start_permanent_task)
    # Ensure the thread will not prevent the program from exiting
    task_thread.daemon = True
    task_thread.start()
