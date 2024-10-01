from django.utils import translation
from django.conf import settings
from light_app.models import UserSettings


class UserSettingsMiddleware:
    """
    Middleware to manage user settings such as theme, font size,
      language preferences, and M5Core2 IP address.

    This middleware activates the user's preferred language, sets session
      variables for theme and font size, and 
    provides access to user-specific settings such as the primary color and 
    IP address for M5Core2 devices.

    Attributes:
        get_response (callable): The next middleware or view in the stack.
    """

    def __init__(self, get_response):
        """
        Initialize the middleware with the next middleware or view.

        Args:
            get_response (callable): A callable to get the response for the 
            next middleware or view.
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Process each request before passing it to the next middleware or view.

        If the user is authenticated, this middleware fetches or creates the 
        user's settings, activates their
        preferred language, and sets various session variables (theme, font 
        size, primary color). It also attaches
        the M5Core2 IP address to the request object.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            HttpResponse: The response object from the next middleware or view.
        """
        if request.user.is_authenticated:
            # Retrieve or create the user's settings.
            user_settings, created = UserSettings.objects.get_or_create(user=request.user)

            # Activate the user's preferred language.
            translation.activate(user_settings.preferred_language)
            request.LANGUAGE_CODE = user_settings.preferred_language

            # Store theme, font size, and primary color in session.
            request.session["theme"] = user_settings.theme
            request.session["font_size"] = user_settings.font_size
            request.session["primary_color"] = user_settings.primary_color

            # Attach user settings and M5Core2 IP address to the request obj.
            request.user_settings = user_settings
            request.user_ip = user_settings.m5core2_ip if user_settings.m5core2_ip else "none"

        # Process the response from the next middleware or view.
        response = self.get_response(request)

        # Deactivate the translation after the request is processed.
        translation.deactivate()

        return response


class UserLanguageMiddleware:
    """
    Middleware to activate the preferred language of an authenticated user or 
    set a default language for anonymous users.

    This middleware activates the language selected in the user's settings.
      If the user is not authenticated, 
    the default language is set to English.

    Attributes:
        get_response (callable): The next middleware or view in the stack.
    """

    def __init__(self, get_response):
        """
        Initialize the middleware with the next middleware or view.

        Args:
            get_response (callable): A callable to get the response for the
              next middleware or view.
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Process each request and activate the user's preferred language.

        If the user is authenticated, this middleware fetches or creates the
          user's settings and activates 
        the user's preferred language. If the user is not authenticated, the 
        default language is set to English.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            HttpResponse: The response object from the next middleware or view.
        """
        if request.user.is_authenticated:
            # Retrieve or create the user's settings.
            user_settings, created = UserSettings.objects.get_or_create(
                user=request.user)

            # Activate the user's preferred language.
            translation.activate(user_settings.preferred_language)
            request.LANGUAGE_CODE = user_settings.preferred_language
        else:
            # Activate default language (English) for non-authenticated users.
            translation.activate("en")

        # Process the response from the next middleware or view.
        response = self.get_response(request)

        # Deactivate the translation after the request is processed.
        translation.deactivate()

        return response
