from django import forms
from .models import Room, Light, UserSettings
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.core.exceptions import ValidationError
import re


class UserUpdateForm(forms.ModelForm):
    """
    A form for updating user information, such as the username and email.

    This form is bound to the Django `User` model and provides fields for
      updating the user's `username` and `email`.
    """
    class Meta:
        model = User
        fields = ["username", "email"]


class PasswordUpdateForm(PasswordChangeForm):
    """
    A form for changing the user's password.

    Inherits from Django's built-in `PasswordChangeForm`. It does not need
      additional customization.
    """
    pass


class RoomForm(forms.ModelForm):
    """
    A form for creating or updating a `Room` instance.

    This form allows users to input a room name, which is associated 
    with a user.
    """
    class Meta:
        model = Room
        fields = ["name"]
        widgets = {
            # Text input for room name with autocomplete off.
            "name": forms.TextInput(attrs={"autocomplete": "name"})
        }


class LightForm(forms.ModelForm):
    """
    A form for creating or updating a `Light` instance.

    This form allows users to input the name, room, description, and state of 
    the light. The `room` queryset is 
    restricted to rooms associated with the currently authenticated user.
    """
    class Meta:
        model = Light
        fields = ["name", "room", "description", "state"]
        widgets = {
            # Text input for light name with autocomplete off.
            "name": forms.TextInput(attrs={"autocomplete": "off"}),
            # Textarea for description.
            "description": forms.Textarea(attrs={"autocomplete": "off"}),
            # Dropdown to select the state of the light.
            "state": forms.Select(attrs={"autocomplete": "off"}),
        }

    def __init__(self, *args, **kwargs):
        """
        Custom initializer for the `LightForm`.

        This constructor takes the `user` keyword argument to filter the rooms
          available in the dropdown list, ensuring 
        that the user can only select rooms that they own.

        Args:
            user (User, optional): The currently authenticated user. If not
              provided, defaults to `None`.
        """
        user = kwargs.pop(
            "user", None)  # Capture the current user from view if passed.
        super(LightForm, self).__init__(*args, **kwargs)
        if user:
            # Filter the available rooms to only those owned by the user.
            self.fields["room"].queryset = Room.objects.filter(user=user)
        # Ensure autocomplete is off for the room selection widget.
        self.fields["room"].widget.attrs.update({"autocomplete": "off"})


class UserSettingsForm(forms.ModelForm):
    """
    A form for managing user settings, including display preferences, 
    notifications, and M5Core2 device settings.

    This form is bound to the `UserSettings` model and provides fields
      for managing various settings related to the user.
    """
    class Meta:
        model = UserSettings
        fields = [
            "display_name", "email", "preferred_language", "timezone",
            "theme", "font_size", "primary_color",
            "email_notifications", "push_notifications",
            "two_factor_authentication", "scheduled_lights", "silence_mode",
            "test_mode", "m5core2_ip", "server_check_interval"
        ]
        widgets = {
            # Text input for display name.
            "display_name": forms.TextInput(attrs={"class":"form-control auto-expand"}),
            # Email input with custom styling.
            "email": forms.EmailInput(attrs={"class":"form-control auto-expand"}),
            # Input for M5Core2 IP address.
            "m5core2_ip": forms.TextInput(attrs={"class":"form-control auto-expand"}),
        }


