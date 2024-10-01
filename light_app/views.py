import os
import requests

from django.core.paginator import Paginator
from django.core.cache import cache
from django.db import connections
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import gettext as _
from django.utils.functional import SimpleLazyObject

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from .models import Room, Light, UserSettings
from .forms import RoomForm, LightForm, UserSettingsForm
from .context_processors import home_online_status, debug

# Global variables
user_id = False
ping_active = True



def home(request):
    """
    Renders the home page for authenticated users.

    This function handles the HTTP GET request and renders the 
    home page template `index.html` for authenticated users.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: The rendered home page template.
    """
    return render(request, "light_app/index.html")



@login_required
def check_home_status(request):
    """
    Returns the current online status of the user's home automation system.

    This function checks the global 'home_online_status' variable for the 
    status of the home system specific to the authenticated user. 
    The status is returned as a JSON response.

    Args:
        request: The HTTP request object containing user information.

    Returns:
        JsonResponse: A JSON object containing the home online status 
        for the authenticated user.
    """
    global home_online_status
    user_id = request.user.id
    return JsonResponse({"home_online_status":
                         home_online_status.get(user_id)})


# =============================================================================

@login_required
def user_settings_view(request):
    """
    Displays and processes the user settings form for authenticated users.

    This function handles both GET and POST requests. On GET, it retrieves the 
    existing user settings or creates a new instance if none exists,
      and displays 
    the settings form. On POST, it processes the form, saves any valid changes, 
    and redirects the user to the home page upon successful form submission.

    Args:
        request: The HTTP request object containing user information
          and form data.

    Returns:
        HttpResponse: If the request method is GET, renders the user
          settings form. 
        If the request method is POST and the form is valid, redirects to the
          home page.
    """
    user_settings, created = UserSettings.objects.get_or_create(user=request.user)
    form = UserSettingsForm(instance=user_settings)

    if request.method == "POST":
        form = UserSettingsForm(request.POST, instance=user_settings)

        if form.is_valid():
            form.save()
            # Redirect to the home page after successful save
            return redirect("home")

    return render(
        request,
        "light_app/user_settings.html",
        {
            "form": form,
        },
    )


# =============================================================================

@login_required
def room_list_view(request):
    """
    Displays a list of rooms for the authenticated user, with pagination.

    Retrieves all rooms associated with the authenticated user and paginates 
    the result to show 3 rooms per page.It then renders the room list template.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: The rendered rooms list template with paginated rooms.
    """
    rooms = Room.objects.filter(user=request.user).prefetch_related("lights")
    paginator = Paginator(rooms, 3)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "room_list": page_obj,
        "is_paginated": page_obj.has_other_pages(),
        "page_obj": page_obj,
    }
    return render(request, "light_app/rooms_list.html", context)

# =============================================================================


def lights_status(request):
    """
    Returns the status of all lights in all rooms.

    Retrieves all rooms and their associated lights, then returns a JSON 
    response containing the state of each light ("on" or "off").

    Args:
        request: The HTTP request object.

    Returns:
        JsonResponse: A JSON list containing the status of lights in each room.
    """
    lights_data = []
    rooms = Room.objects.all()
    for room in rooms:
        lights = room.lights.all()
        for light in lights:
            lights_data.append(
                {
                    "room": room.name,
                    "light": light.name,
                    "state": "on" if light.state == 1 else "off",
                }
            )
    return JsonResponse(lights_data, safe=False)

# =============================================================================


@login_required
def toggle_light(request, room_name, light_name):
    """
    Toggles the state of a light in the specified room.

    Finds the room and light by their names for the authenticated user, 
    toggles the light state (on/off), and communicates the change to the 
    ESP32 device if the user's IP address is configured. 
    Returns a JSON response for AJAX requests or redirects to the room list.

    Args:
        request: The HTTP request object.
        room_name: The name of the room.
        light_name: The name of the light.

    Returns:
        JsonResponse or HttpResponse: If the request is AJAX, returns the 
        light state in a JSON response, otherwise redirects to the room list.
    """
    room = get_object_or_404(Room, name=room_name, user=request.user)
    light = get_object_or_404(Light, room=room, name=light_name)

    user_ip = request.user_ip
    if not user_ip or user_ip == "none":
        return JsonResponse({"error": "ESP32 IP not configured for user", "action":"go_to_settings"},status=400,)

    response_text = ""
    action = "off" if light.state == 1 else "on"

    if user_ip:
        try:
            try:
                response = requests.get(
                    f"http://{request.user_ip}", timeout=30)
                if response.status_code == 200:
                    home_online = True
            except requests.exceptions.RequestException as e:
                home_online = False
                response_text = f"Server offline: {e}"

            if home_online:
                response = requests.get(f"http://{request.user_ip}/control_led",params={"room": room_name,"light": light_name, "action": action},timeout=30,)
                if response.ok:
                    light.state = 1 if action == "on" else 2
                    light.save()
                    response_text = response.json()
                else:
                    response_text = "Failed to change light state on M5Core2\
                          server."
        except Exception as e:
            response_text = f"Error: {e}"

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse(
            {"state": light.get_state_display(), "esp_response": response_text}
        )

    return redirect("room_list")

# =============================================================================


@login_required
def add_room(request):
    """
    Handles the addition of a new room for the authenticated user.

    Renders a form for creating a new room. If the request method is POST, 
    validates and saves the new room, associating it with the current user.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: The rendered room addition form or redirects
          to the room list.
    """
    if request.method == "POST":
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.user = request.user
            room.save()
            return redirect("room_list")
    else:
        form = RoomForm()

    return render(request, "light_app/add_room.html", {"form": form})

# =============================================================================


@login_required
def add_light(request):
    """
    Handles the addition of a new light for the authenticated user.

    Renders a form for creating a new light. If the request method is POST, 
    validates and saves the new light, ensuring it is associated with the 
    correct room.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: The rendered light addition form or redirects to the
          room list.
    """
    if request.method == "POST":
        form = LightForm(request.POST, user=request.user)
        if form.is_valid():
            light = form.save(commit=False)
            light.room.user = request.user
            light.save()
            return redirect("room_list")
    else:
        form = LightForm(user=request.user)

    return render(request, "light_app/add_light.html", {"form": form})

# =============================================================================


@login_required
def edit_room(request, room_id):
    """
    Handles editing of an existing room for the authenticated user.

    Retrieves the room by its ID and renders a form for editing the room. 
    If the request method is POST, validates and saves the updated room.

    Args:
        request: The HTTP request object.
        room_id: The ID of the room to be edited.

    Returns:
        HttpResponse:The rendered room edit form or redirects to the room list.
    """
    room = get_object_or_404(Room, id=room_id, user=request.user)
    if request.method == "POST":
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect("room_list")
    else:
        form = RoomForm(instance=room)

    return render(request, "light_app/edit_room.html", {"form": form,
                                                        "room": room})


@login_required
def delete_room(request, room_id):
    """
    Handles the deletion of an existing room for the authenticated user.

    Retrieves the room by its ID and deletes it if the request method is POST.

    Args:
        request: The HTTP request object.
        room_id: The ID of the room to be deleted.

    Returns:
        HttpResponse: The rendered delete confirmation page or redirects
          to the room list.
    """
    room = get_object_or_404(Room, id=room_id)
    if request.method == "POST":
        room.delete()
        return redirect("room_list")

    return render(request, "light_app/delete_room.html", {"room": room})

# =============================================================================


@login_required
def edit_light(request, light_id):
    """
    Handles editing of an existing light for the authenticated user.

    Retrieves the light by its ID and renders a form for editing the light. 
    If the request method is POST, validates and saves the updated light.

    Args:
        request: The HTTP request object.
        light_id: The ID of the light to be edited.

    Returns:
        HttpResponse: The rendered light edit form or redirects to the
          room list.
    """
    light = get_object_or_404(Light, id=light_id, room__user=request.user)
    if request.method == "POST":
        form = LightForm(request.POST, instance=light, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("room_list")
    else:
        form = LightForm(instance=light, user=request.user)

    return render(request, "light_app/edit_light.html", {"form": form,
                                                         "light": light})


@login_required
def delete_light(request, light_id):
    """
    Handles the deletion of an existing light for the authenticated user.

    Retrieves the light by its ID and deletes it if the request method is POST.

    Args:
        request: The HTTP request object.
        light_id: The ID of the light to be deleted.

    Returns:
        HttpResponse: The rendered delete confirmation page or redirects to
          the room list.
    """
    light = get_object_or_404(Light, id=light_id)
    if request.method == "POST":
        light.delete()
        return redirect("room_list")

    return render(request, "light_app/delete_light.html", {"light": light})
