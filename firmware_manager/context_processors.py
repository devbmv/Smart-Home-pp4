from django.conf import settings

def user_ip_processor(request):
    user_ip = request.META.get('REMOTE_ADDR') 
    print(f"USER IP IN CONTEXT {user_ip}")
    return {
        'user_ip': user_ip 
    }
