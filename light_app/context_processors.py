from home_control_project.settings import home_online_status
from light_app.models import UserSettings

def home_status_processor(request):
    user_id = request.user.id if request.user.is_authenticated else None
    
    # Asigură-te că utilizatorul este logat și există setări pentru utilizator
    user_settings = None
    silence_mode = False
    if request.user.is_authenticated:
        try:
            user_settings = UserSettings.objects.get(user=request.user)
            silence_mode = user_settings.silence_mode
        except UserSettings.DoesNotExist:
            pass
    
    # Returnează contextul cu informațiile dorite
    context = {
        'home_online_status': home_online_status.get(user_id, False),
        'silence_mode': silence_mode,
        'server_check_interval': user_settings.server_check_interval if user_settings else 5,
        'm5core2_ip': user_settings.m5core2_ip if user_settings else "",
        'user_id': user_id
    }
    
    return context
