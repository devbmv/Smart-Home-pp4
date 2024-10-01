from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserSettings


@receiver(post_save, sender=User)
def create_user_settings(sender, instance, created, **kwargs):
    """
    Signal receiver that creates a UserSettings instance whenever a new User
      is created.

    Args:
    - sender: The model class that sends the signal (User).
    - instance: The instance of the User that was created.
    - created: Boolean; True if a new record was created.
    - **kwargs: Additional keyword arguments.

    If a new User is created, this function ensures a corresponding 
    UserSettings object is also created.
    """
    if created:
        UserSettings.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_settings(sender, instance, **kwargs):
    """
    Signal receiver that saves the UserSettings instance when the User 
    instance is saved.

    Args:
    - sender: The model class that sends the signal (User).
    - instance: The instance of the User that was saved.
    - **kwargs: Additional keyword arguments.

    This function ensures that any changes to the User instance are reflected 
    in the corresponding UserSettings object.
    """
    instance.usersettings.save()
