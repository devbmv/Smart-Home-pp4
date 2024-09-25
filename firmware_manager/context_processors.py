from django.conf import settings

# Funcție care extrage adresa IP din request și o include în contextul template-urilor
def user_ip_processor(request):
    user_ip = request.META.get('REMOTE_ADDR')  # Obține adresa IP a utilizatorului
    print(f"USER IP IN CONTEXT {user_ip}")
    return {
        'user_ip': user_ip  # Include adresa IP în contextul template-ului
    }
