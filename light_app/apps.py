from django.apps import AppConfig
from django.db import OperationalError
from django.db.migrations.executor import MigrationExecutor
from django.db import connections
from django.db.utils import ProgrammingError


class LightAppConfig(AppConfig):
    """
    Configuration class for the 'light_app' Django application.
    
    This class ensures that database migrations are applied at startup
    if there are any pending migrations, and starts the ping task for all users.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "light_app"

    def ready(self):
        """
        This method is executed when the app is ready.

        It ensures that any pending migrations are applied before the application
        starts interacting with the database, and it initiates the task to start
        pinging for all users.
        """
        try:
            # Open a connection to the default database
            connection = connections["default"]
            
            # Create an instance of the migration executor to manage migrations
            executor = MigrationExecutor(connection)
            
            # Check if there are any pending migrations
            if executor.migration_plan(executor.loader.graph.leaf_nodes()):
                # Apply any pending migrations
                executor.migrate(executor.loader.graph.leaf_nodes())
        
        except (OperationalError, ProgrammingError) as e:
            # If there's a database error or missing schema, it is ignored
            # The application can continue running without breaking
            pass
        
        # Import and start the task to ping all users
        from .tasks import start_ping_for_all_users
        start_ping_for_all_users()
