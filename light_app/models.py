from django.db import models
from django.contrib.auth.models import User
import datetime

# =============================================================================
# Choices for light state (on, off, timer)
STATE_CHOICES = [
    (1, "on"),
    (2, "off"),
    (3, "timer"),
]

# =============================================================================


class Choice(models.Model):
    """
    A model to represent a generic choice that can be associated with a Light.

    Fields:
    - name: Name of the choice.
    """

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]

# =============================================================================


class Room(models.Model):
    """
    A model representing a room owned by a specific user.

    Fields:
    - name: Name of the room.
    - user: A foreign key referencing the user who owns the room.
    """

    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="rooms")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        unique_together = ("name", "user")

# =============================================================================


class Light(models.Model):
    """
    A model to represent a light in a room. Each light is associated with a 
    room and can have a state.

    Fields:
    - name: Name of the light.
    - room: Foreign key to the Room model.
    - description: Optional description of the light.
    - state: Current state of the light, chosen from STATE_CHOICES.
    - choices: Many-to-many relationship with the Choice model.
    """

    name = models.CharField(max_length=100, default="")
    room = models.ForeignKey(
        Room, on_delete=models.CASCADE, related_name="lights")
    description = models.TextField(null=True, blank=True, default="")
    state = models.IntegerField(choices=STATE_CHOICES, default=2)
    choices = models.ManyToManyField(Choice, related_name="lights", blank=True)

    def __str__(self):
        return f"{self.name} in {self.room}"

    class Meta:
        ordering = ["id"]

# =============================================================================


class UserSettings(models.Model):
    """
    A model to store user-specific settings, including notification
      preferences, theme, and more.

    Fields:
    - user: One-to-one relationship with the Django User model.
    - api_password: Password used for API authentication.
    - server_check_interval: Interval (in seconds) for checking server status.
    - display_name: Display name of the user.
    - email: Email address of the user.
    - preferred_language: The user's preferred language.
    - timezone: The user's timezone.
    - theme: UI theme setting (light or dark).
    - font_size: Preferred font size.
    - primary_color: User's selected primary color for the UI.
    - email_notifications: Boolean to indicate if email notifications are 
    enabled.
    - push_notifications: Boolean to indicate if push notifications are 
    enabled.
    - two_factor_authentication: Boolean to indicate if 2FA is enabled.
    - scheduled_lights: Boolean to indicate if the user has scheduled lights.
    - silence_mode: Boolean to enable or disable silence mode.
    - test_mode: Boolean to indicate if the user is in test mode.
    - m5core2_ip: IP address for the M5Core2 device.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    api_password = models.CharField(max_length=128)  # API password

    server_check_interval = models.IntegerField(
        default=5, help_text="Interval in seconds for checking server status."
    )

    display_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(max_length=255, blank=True)
    preferred_language = models.CharField(max_length=50,choices=[("en", "English"), ("fr","French"), ("de", "German")],
        default="en",
    )
    timezone = models.CharField(max_length=50, default="UTC")
    theme = models.CharField(
        max_length=10, choices=[("light", "Light"), ("dark", "Dark")],
        default="light"
    )
    font_size = models.CharField(max_length=10,choices=[("small", "Small"), ("medium", "Medium"), ("large", "Large")],
        default="medium",
    )
    primary_color = models.CharField(max_length=7, default="#2980b9")  # Default color is blue
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    two_factor_authentication = models.BooleanField(default=False)
    scheduled_lights = models.BooleanField(default=False)
    silence_mode = models.BooleanField(default=False)
    test_mode = models.BooleanField(default=True)
    # User's M5Core2 IP address
    m5core2_ip = models.CharField(max_length=100, blank=True, default="")

    def save(self, *args, **kwargs):
        """
        Custom save method that ensures the server check interval is between 1
          second and 7200 seconds (2 hours).
        """
        if self.server_check_interval < 1:
            self.server_check_interval = 1
        elif self.server_check_interval > 7200:
            self.server_check_interval = 7200
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} Settings"
