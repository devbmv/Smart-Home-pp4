from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import os
from django.conf import settings


@csrf_exempt
def update_esp_firmware(request):
    # Renders the HTML page where the user can upload firmware
    return render(request, "firmware_manager/update.html")

def chatHome(request):
    # Renders the HTML page where the user can upload firmware
    return render(request, "firmware_manager/chat.html")


@csrf_exempt
def upload_firmware(request):
    try:
        if request.method == "POST":
            firmware_file = request.FILES.get("firmware")
            if not firmware_file:
                raise Exception("No firmware file found in request.")

            file_path = os.path.join(settings.MEDIA_ROOT, firmware_file.name)
            print(f"Received firmware file: {firmware_file.name}")
            print(f"Saving to: {file_path}")

            # Salvează fișierul pe serverul Django
            with open(file_path, "wb+") as destination:
                for chunk in firmware_file.chunks():
                    destination.write(chunk)

            # Etapa 1 completă – notifică clientul
            return JsonResponse(
                {
                    "status": "uploaded_to_django",
                    "message": "Firmware uploaded to Django successfully. Now uploading to ESP32..."
                }
            )
        return HttpResponse(status=405)
    except Exception as e:
        return JsonResponse(
            {"status": "error", "message": f"An error occurred: {str(e)}"},
            status=500,
        )


@csrf_exempt
def upload_to_esp32(request):
    try:
        file_path = os.path.join(
            settings.MEDIA_ROOT, "firmware.bin"
        )  # Fișierul deja uploadat

        # Trimite fișierul către ESP32 prin endpoint-ul /django_update_firmware
        with open(file_path, "rb") as f:
            url = f"http://{request.user_ip}/django_update_firmware"  # Adresa IP a ESP32
            response = requests.post(url, files={"firmware": f})

        if response.status_code == 200:
            return JsonResponse(
                {
                    "status": "success",
                    "message": "Firmware uploaded to ESP32 successfully",
                }
            )
        else:
            return JsonResponse(
                {"status": "error", "message": "Failed to upload firmware to ESP32"},
                status=500,
            )
    except Exception as e:
        return JsonResponse(
            {"status": "error", "message": f"An error occurred: {str(e)}"},
            status=500,
        )
