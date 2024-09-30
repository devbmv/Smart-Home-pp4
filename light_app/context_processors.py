from light_app.models import UserSettings, User
from home_control_project.settings import DEBUG
# Dicționar global pentru a stoca starea online a fiecărui utilizator
home_online_status = {1: False}  # Folosim valori booleane True/False

def debug(data):
    if DEBUG:
        print(data)

# Context Processor pentru a adăuga variabile globale la template
def global_variables(request):
    global home_online_status
    user_settings=None
    if request.user.is_authenticated:
        # Obținem sau creăm setările utilizatorului curent
        user_settings, created = UserSettings.objects.get_or_create(user=request.user)
        user_id = request.user.id

        # Obținem starea online curentă din dicționarul global
        online_status = home_online_status.get(user_id, False)

        return {
            "home_online_status": online_status,  # Returnează doar starea utilizatorului curent
            "silence_mode": user_settings.silence_mode,
            "check_interval": user_settings.server_check_interval,  # Returnează intervalul corect
            "user_ip": request.META["REMOTE_ADDR"],
        }
    else:
        return {
            "home_online_status": False,  # Dacă utilizatorul nu este autentificat
            "test_mode": False,
            "silence_mode": user_settings,
            "check_interval": 10,  # Poți pune o valoare implicită pentru utilizatorii neautentificați
            "user_ip": request.META.get("REMOTE_ADDR", ""),
        }
