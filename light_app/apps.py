from django.apps import AppConfig
from django.db import connections


class LightAppConfig(AppConfig):
    """
    Configuration class for the 'light_app' Django application.

    This class ensures that database migrations are checked at startup
    and starts the ping task for all users if there are no pending migrations.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "light_app"

    def ready(self):
        """
        This method is executed when the app is ready.

        It ensures that there are no pending migrations before the application
        starts interacting with the database, and it initiates the
          task to start
        pinging for all users.
        """
        # Open a connection to the default database

        connection = connections["default"]
        connection.prepare_database()  # Ensure the database is prepared
        # Pornește task-ul în background
        from .background_task import start_background_task

        start_background_task()
