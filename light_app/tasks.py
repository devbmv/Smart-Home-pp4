import threading
from time import sleep
import requests
from home_control_project.settings import debug, home_online_status
import os
from datetime import datetime
from .models import UserSettings
import ssl, socket
from django.db import connection

ip_sent = False
home_home_url = ""
last_message = ""
last_check_interval=0
# Funcția pentru a obține timpul curent ca string
def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def send_ping_to_esp32(user_ip, check_interval, user_id):
    
    global ip_sent
    global home_home_url
    global last_message
    global last_check_interval
   # Așteaptă puțin înainte de a șterge consola
    settings = UserSettings.objects.get(user_id=user_id)

    while True:
        try:
            check_interval = settings.server_check_interval  # Actualizează intervalul

            # Construim URL-ul și trimitem intervalul doar dacă s-a schimbat sau alte condiții sunt îndeplinite
            if (
                not ip_sent
                or not home_online_status[user_id]
                or last_message == "Give me check_interval var"
                or last_check_interval != check_interval
            ):
                home_url = f"http://{user_ip}?check_interval={check_interval}"
                last_check_interval = check_interval
                ip_sent = True
            else:
                home_url = f"http://{user_ip}"
                try:
                    response = requests.get(home_url, timeout=20)
                    last_message = response.text
                except requests.RequestException as e:
                    last_message = f"Error: {str(e)}"
            current_time = get_current_time()
            debug(f"[{current_time}] ESP32 status code: {response.status_code}")
            debug(f"[{current_time}] ESP32 response: {response.text}\n")

            # Verificăm dacă ESP32 a primit cu succes IP-ul
            if "I succesful received your IP:" in response.text:
                debug(f"[{current_time}] ESP32 has successfully received the IP.")
                ip_sent = True
            elif "I have you offline" in response.text:
                ip_sent = False

            # Actualizăm starea online a utilizatorului
            home_online_status[user_id] = True

        except requests.RequestException as e:
            current_time = get_current_time()
            if e.response:
                error_code = e.response.status_code
                debug(f"[{current_time}] Error sending request to ESP32: HTTP Status Code {error_code}\n")
            else:
                debug(f"[{current_time}] Error sending request to ESP32: {type(e).__name__}\n")
            home_online_status[user_id] = False
        connection.close()
        sleep(check_interval)


def start_ping_for_user(user):
    try:
        settings = UserSettings.objects.get(user=user)
        user_ip = settings.m5core2_ip
        check_interval = settings.server_check_interval
        if user_ip:
            # Inițializăm starea home_online ca False pentru acest utilizator
            home_online_status[user.id] = False

            # Pornim un thread separat pentru a trimite ping-ul în mod continuu
            ping_thread = threading.Thread(
                target=send_ping_to_esp32, args=(user_ip, check_interval, user.id)
            )
            ping_thread.daemon = True  # Setăm daemon pentru a nu bloca la shutdown
            ping_thread.start()

            current_time = get_current_time()
            debug(
                f"[{current_time}] Started pinging ESP32 for user: {user.username} every {check_interval} seconds"
            )
        else:
            current_time = get_current_time()
            debug(
                f"[{current_time}] No IP found for user: {user.username}. Cannot start pinging."
            )
    except UserSettings.DoesNotExist:
        current_time = get_current_time()
        debug(f"[{current_time}] UserSettings not found for user: {user.username}")


# Funcția care inițiază procesul de ping pentru toți utilizatorii
def start_ping_for_all_users():
    from django.contrib.auth.models import User

    users = User.objects.all()

    for user in users:
        start_ping_for_user(user)
