from home_control_project.settings import home_online_status
from light_app.models import UserSettings
from django.core.cache import cache

def home_status_processor(request):
    user_id = cache.get(f"user_{request.user.id}") if request.user.is_authenticated else None
    
    # În loc să interogăm baza de date, încercăm să recuperăm setările utilizatorului din cache
    user_settings = cache.get(f"user_settings_{user_id}") if user_id else None

    silence_mode = False
    if not user_settings and request.user.is_authenticated:
        try:
            # Dacă setările nu sunt în cache, interogăm baza de date și salvăm în cache
            user_settings = UserSettings.objects.get(user=request.user)
            cache.set(f"user_settings_{user_id}", user_settings, timeout=300)  # Păstrăm în cache pentru 5 minute
            silence_mode = user_settings.silence_mode
        except UserSettings.DoesNotExist:
            user_settings = None
    
    # Returnează contextul cu informațiile dorite
    context = {
        'home_online_status': home_online_status.get(user_id, False),
        'silence_mode': silence_mode,
        'server_check_interval': user_settings.server_check_interval if user_settings else 5,
        'm5core2_ip': user_settings.m5core2_ip if user_settings else "",
        'user_id': user_id
    }
    
    return context