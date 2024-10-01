from django.urls import path
from . import views

# Define the URL patterns for the light app.
urlpatterns = [
    path("", views.home, name="home"),  # Home page route.

    path("settings/", views.user_settings_view, name="user_settings"),
    # Route for user settings page.

    path("toggle-light/<str:room_name>/<str:light_name>/",views.toggle_light,name="toggle_light",),
    # Route to toggle the light in a specific room and light by their names.

    path("rooms/", views.room_list_view, name="room_list"),
    # Route to display the list of rooms.

    path("lights_status/", views.lights_status, name="lights_status"),
    # Route to check the status of lights.

    path("add_room/", views.add_room, name="add_room"),
    # Route to add a new room.

    path("edit_room/<int:room_id>/", views.edit_room, name="edit_room"),
    # Route to edit an existing room by its ID.

    path("delete_room/<int:room_id>/", views.delete_room, name="delete_room"),
    # Route to delete a room by its ID.

    path("add_light/", views.add_light, name="add_light"),
    # Route to add a new light.

    path("edit_light/<int:light_id>/", views.edit_light, name="edit_light"),
    # Route to edit an existing light by its ID.

    path("delete_light/<int:light_id>/",
         views.delete_light, name="delete_light"),
    # Route to delete a light by its ID.

    path("check_home_status/", views.check_home_status,
         name="check_home_status"),
    # Route to check the current status of the home (online/offline).
]
