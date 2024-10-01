from light_app.models import UserSettings, User
from home_control_project.settings import DEBUG

# Global dictionary to store the online status of each user
# The keys are user IDs, and the values are booleans representing the 
# online status
home_online_status = {1: False}  # Using boolean values True/False


def debug(data):
    """
    Prints the debug information if the DEBUG setting is True.

    Args:
        data (str): The data to be printed for debugging purposes.
    """
    if DEBUG:
        print(data)


def global_variables(request):
    """
    Context processor to add global variables to the template context.

    This function adds the current user's online status, silence mode, server
      check interval,
    and user IP address to the context, making them available in templates.

    Args:
        request (HttpRequest): The current HTTP request object.

    Returns:
        dict: A dictionary containing global variables like
          'home_online_status',
              'silence_mode', 'check_interval', and 'user_ip' for the
                authenticated user.
              If the user is not authenticated, default values are returned.
    """
    global home_online_status  # Access the global online status dictionary
    user_settings = None

    if request.user.is_authenticated:
        # Get or create user settings for the authenticated user
        user_settings, created = UserSettings.objects.get_or_create(
            user=request.user)
        user_id = request.user.id

        # Get the current online status from the global dictionary for  user
        online_status = home_online_status.get(user_id, False)

        return {
            # Return the online status for the current user
            "home_online_status": online_status,
            # Return the silence mode setting from user settings
            "silence_mode": user_settings.silence_mode,
            # Return the correct server check interval from user settings
            "check_interval": user_settings.server_check_interval,
            # Return the user's IP address from the request metadata
            "user_ip": request.META.get("REMOTE_ADDR", ""),
        }
    else:
        # Return default values if the user is not authenticated
        return {
            "home_online_status": False,  # Default to offline status
            "test_mode": False,           # Default test mode
            "silence_mode": user_settings,  # No user settings if not auth.
            # Default check interval (in seconds)
            "check_interval": 10,
            # IP address or empty string if not available
            "user_ip": request.META.get("REMOTE_ADDR", ""),
        }
