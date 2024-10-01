#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <ArduinoJson.h>
#include <WiFiClientSecure.h>
#include <base64.h>    // Base64 library for encoding
#include <M5Unified.h> // M5Core2 support
#include <mbedtls/md.h>
#include <mbedtls/sha1.h>
#include <map>
#include <SPIFFS.h>
#include <Update.h>
#include <WebSocketsServer.h>
#include <mbedtls/entropy.h>
#include <mbedtls/ctr_drbg.h>
#include <esp_task_wdt.h>
#include <WebSocketsClient.h>
#include <Websockets.h>
#include <ArduinoWebsockets.h>

WiFiClient client; // Global Wi-Fi client object

//============================================================================

struct Light; // Forward declaration for Light struct
struct Room;  // Forward declaration for Room struct

// Map to hold the room and associated light structures
std::map<String, Room> roomLightMap;

//============================================================================
#define SERIAL_DEBUG
#define M5CORE2_DEBUG
#ifdef M5CORE2_DEBUG
#include <M5Unified.h>
M5GFX &lcd = M5.Lcd;
#endif

AsyncWebServer server(80); // Async web server on port 80

// Function declarations
String base64Encode(String str);
void addBasicAuth(HTTPClient &http);
void reconnectWiFi();
void m5_debug(String msg, uint16_t col, uint16_t row);
void s_debug(String msg);
void fetchInitialLightStates();
void printLightStates();
void serverSetup();
void displayIP();
void processSerialCommands();
void checkDjangoOnline();

void detectIPHandler(AsyncWebServerRequest *request);
bool localServer = false; // Determines if the server is local (true) or Heroku (false)

// Wi-Fi and Django configuration variables
String ssid = WIFI_SSID;
String password = WIFI_PASSWORD;
String djangoUserName = DJANGO_USERNAME;
String djangoPassword = DJANGO_PASSWORD;
unsigned long lastSendTime = 0;
uint16_t setup_debug_time = 1000;
uint16_t loop_debug_time = 10000;
String clientIPAddress = "";
bool checkServer = true;
bool djangoOnline = false;
bool update = true;
uint32_t lastPingTime = 0;
int checkInterval = 0; // Variable to store the interval as an integer

// URL variables for checking server and sending data
String serverCheckUrl = "";
String lightStatusUrl = "";
String serialPostUrl = "";

//============================================================================

/**
 * @brief Prints all global variables for debugging purposes.
 */
void printVariables()
{
    Serial.println("=== Variables State ===");
    Serial.println("Local Server: " + String(localServer ? "True" : "False"));
    Serial.println("SSID: " + ssid);
    Serial.println("Password: " + password);
    Serial.println("Django Username: " + djangoUserName);
    Serial.println("Django Password: " + djangoPassword);
    Serial.println("Client IP Address: " + clientIPAddress);
    Serial.println("Check Server: " + String(checkServer ? "True" : "False"));
    Serial.println("Django Online: " + String(djangoOnline ? "True" : "False"));
    Serial.println("Update: " + String(update ? "True" : "False"));
    Serial.println("Last Send Time: " + String(lastSendTime));
    Serial.println("Setup Debug Time: " + String(setup_debug_time));
    Serial.println("Loop Debug Time: " + String(loop_debug_time));
    Serial.println("Last Ping Time: " + String(lastPingTime));
    Serial.println("Check Interval: " + String(checkInterval));
    Serial.println("Server Check URL: " + serverCheckUrl);
    Serial.println("Light Status URL: " + lightStatusUrl);
    Serial.println("Serial Post URL: " + serialPostUrl);
    Serial.println("========================");
}

/**
 * @brief Monitors the available heap memory and prints it with a custom tag.
 * @param tag The tag that identifies the context.
 */
void monitorHeap(String tag)
{
    Serial.println(tag + ": Free heap memory: " + String(ESP.getFreeHeap()) + " bytes");
}

/**
 * @brief Initializes the SPIFFS filesystem and loads the SSL certificate.
 * Prints and processes available files in the SPIFFS.
 */
void spiffsInit()
{
    if (!SPIFFS.begin(true))
    {
        Serial.println("An error occurred while mounting SPIFFS.");
        return;
    }
    else
    {
        Serial.println("SPIFFS mounted successfully.");
    }

    // List all files in SPIFFS
    File root = SPIFFS.open("/");
    File certFile = SPIFFS.open("/cert.pem", "r");
    Serial.println(certFile.size());

    if (certFile)
    {
        String cert = certFile.readString();
        if (cert.length() == 0)
        {
            Serial.println("Certificate is empty.");
        }
        else
        {
            Serial.println("Certificate: " + cert);
        }

        certFile.close();
        Serial.println("Certificate loaded from SPIFFS.");
    }
    else
    {
        Serial.println("No certificate found in SPIFFS.");
    }

    File file = root.openNextFile();
    while (file)
    {
        s_debug("FILE: ");
        Serial.println(file.name());
        file = root.openNextFile();
    }
}

/**
 * @brief Main setup function for initializing Wi-Fi, M5Core2, and server.
 * Also prints initial diagnostic information.
 */
void setup()
{
#ifdef M5CORE2_DEBUG
    auto cfg = M5.config();
    M5.begin(cfg);
    M5.Display.setTextSize(2);
    M5.Display.setCursor(0, 0);
    M5.Display.fillScreen(BLACK); // Clear the screen
#endif
    Serial.begin(115200);

    // Check if Django credentials are present
    if (!djangoUserName.isEmpty() || djangoPassword.isEmpty())
    {
        s_debug("Django credentials are missing.");
        delay(setup_debug_time);
    }
    else
    {
        Serial.println("Django credentials are present.");
        s_debug("Django credentials are present.");
        s_debug("Django Username: " + djangoUserName);
        s_debug("Django Password: " + djangoPassword);
        delay(setup_debug_time);
    }

    reconnectWiFi(); // Connect to Wi-Fi
    serverSetup();   // Setup the server

    displayIP(); // Display the current IP address
#ifdef M5CORE2_DEBUG
    M5.Display.setTextSize(2);
    M5.Display.setCursor(0, 0);
    M5.Display.fillScreen(BLACK); // Clear the screen
#endif
}

/**
 * @brief Main loop function to continuously check Django status and process serial commands.
 * Executes at regular intervals defined by checkInterval.
 */
void loop()
{
    static uint32_t serverTimer;
    static unsigned long lastReconnectAttempt = 0;

    if ((millis() - serverTimer > (checkInterval == 0 ? 2000 : checkInterval)))
    {
        printVariables();
        serverTimer = millis();
        s_debug(String(djangoOnline ? "Django Online" : "Django Offline"));
    }

    checkDjangoOnline();     // Checks if Django server is online
    processSerialCommands(); // Continuously process serial commands
}

/**
 * @brief Checks if Django is still online based on last ping time.
 * Marks Django as offline if no response within the defined interval.
 */
void checkDjangoOnline()
{
    if ((millis() - lastPingTime) > (checkInterval == 0 ? 4000 : checkInterval * 2))
    {
        if (djangoOnline == true)
        {
            djangoOnline = false;
            update = true;
        }
    }
}

//============================================================================

/**
 * @brief Structure to represent a Light with a name and state.
 */
struct Light
{
    String name; // Name of the light
    bool state;  // Light state (true = on, false = off)
};

/**
 * @brief Structure to represent a Room, containing lights and its state.
 */
struct Room
{
    String state;              // Room state
    std::vector<Light> lights; // Lights in the room
};

//============================================================================

/**
 * @brief Processes serial commands for configuring Wi-Fi, server, or other variables.
 */
void processSerialCommands()
{
    if (Serial.available() > 0)
    {
        String input = Serial.readStringUntil('\n');
        input.trim();

        // Handle 'set' commands for SSID, password, Django credentials, etc.
        if (input.startsWith("set "))
        {
            if (input.startsWith("set ssid "))
            {
                ssid = input.substring(9);
            }
            else if (input.startsWith("set password "))
            {
                password = input.substring(13);
            }
            else if (input.startsWith("set username "))
            {
                djangoUserName = input.substring(13);
            }
            else if (input.startsWith("set djangoPassword "))
            {
                djangoPassword = input.substring(19);
            }
            else if (input.startsWith("set interval "))
            {
                loop_debug_time = input.substring(13).toInt();
            }
            else if (input.startsWith("set url_check "))
            {
                serverCheckUrl = input.substring(14);
                Serial.println("Server check URL updated to: " + serverCheckUrl);
            }
            else if (input.startsWith("set url_light "))
            {
                lightStatusUrl = input.substring(14);
                Serial.println("Light status URL updated to: " + lightStatusUrl);
            }
            else if (input.startsWith("set url_serial "))
            {
                serialPostUrl = input.substring(15);
                Serial.println("Serial data post URL updated to: " + serialPostUrl);
            }
            else
            {
                Serial.println("Unknown command: " + input);
            }
            Serial.println("Settings updated.");
        }
        else if (input == "!local")
        {
            localServer = !localServer;
            Serial.println("Local server: " + String(localServer));
        }
        else if (input == "!check")
        {
            checkServer = !checkServer;
            Serial.println("Check server is: " + String(checkServer ? "ON" : "OFF"));
        }
        else
        {
            Serial.println("Unknown command: " + input);
        }
    }
}

//============================================================================

/**
 * @brief Adds Basic Authentication headers to HTTP requests using Django credentials.
 * @param http Reference to the HTTPClient object.
 */
void addBasicAuth(HTTPClient &http)
{
    if (djangoUserName.isEmpty() || djangoPassword.isEmpty())
    {
        s_debug("Username or password for Django is missing.");
        return;
    }
    String auth = base64Encode(djangoUserName + ":" + djangoPassword);
    s_debug("Auth urlcode = " + auth);
    http.addHeader("Authorization", "Basic " + auth);
}

//============================================================================

/**
 * @brief Determines if the IP address belongs to a local network.
 * @param ipAddress The IP address to check.
 * @return true if the IP is local, false otherwise.
 */
bool isLocalServer(const String &ipAddress)
{
    localServer = ipAddress.startsWith("192.168") || ipAddress.startsWith("10.") || ipAddress == "127.0.0.1";
    return localServer;
}

//============================================================================

/**
 * @brief Fetches the initial light states from the server.
 * Handles JSON deserialization and error checking.
 */
void fetchInitialLightStates()
{
    if (WiFi.status() == WL_CONNECTED)
    {
        HTTPClient http;

        if ((localServer && !lightStatusUrl.startsWith("http")) || (!localServer && !lightStatusUrl.startsWith("https")))
        {
            s_debug("Invalid lightStatusUrl format!");
            return;
        }

        http.begin(lightStatusUrl);
        addBasicAuth(http);

        int httpResponseCode = http.GET();
        if (httpResponseCode == 200)
        {
            String payload = http.getString();
            if (ESP.getMaxAllocHeap() < 500)
            {
                Serial.println("Low memory: Unable to allocate space for JSON parsing.");
                s_debug("Invalid light format!");
                return;
            }

            // Deserialize JSON payload
            JsonDocument doc;
            DeserializationError error = deserializeJson(doc, payload);

            if (error)
            {
                s_debug("Error parsing JSON:");
                Serial.println(error.f_str());
                return;
            }

            roomLightMap.clear(); // Clear previous data

            for (JsonObject roomEntry : doc.as<JsonArray>())
            {
                String roomName = roomEntry["room"];
                String lightName = roomEntry["light"];
                bool lightState = String(roomEntry["state"].as<const char *>()) == "on";

                if (roomLightMap.find(roomName) == roomLightMap.end())
                {
                    roomLightMap[roomName] = Room{roomName};
                }

                roomLightMap[roomName].lights.push_back(Light{lightName, lightState});
            }

            Serial.println("Room and light states fetched from server.");
            printLightStates();
        }
        else
        {
            Serial.printf("Error fetching light states: %d\n", httpResponseCode);
            String responsePayload = http.getString();
            Serial.println("Response payload: " + responsePayload);
        }

        http.end(); // Close the connection
    }
}

//============================================================================

/**
 * @brief Prints the current light states stored in the roomLightMap.
 */
void printLightStates()
{
    int line = 0;
    for (const auto &roomEntry : roomLightMap)
    {
        String info = "Room: " + String(roomEntry.first.c_str()) + "\n";
        s_debug(info + "Room: " + roomEntry.first);
        line += 20;
        for (const Light &light : roomEntry.second.lights)
        {
            String lightStateText = "Light: " + light.name + ", State: " + (light.state ? "on" : "off");
            s_debug(lightStateText);
            line += 20;
        }
    }
}

//============================================================================

/**
 * @brief Reconnects to Wi-Fi using the given SSID and password.
 * Prints connection status.
 */
void reconnectWiFi()
{
    WiFi.begin(ssid, password);
    unsigned long startAttemptTime = millis();

    while (WiFi.status() != WL_CONNECTED && (millis() - startAttemptTime) < 10000)
    {
        delay(1000);
        Serial.println("Connecting to WiFi...");
        s_debug("Connecting to WiFi...");
    }

    if (WiFi.status() != WL_CONNECTED)
    {
        Serial.println("Failed to connect. Rebooting...");
    }
    Serial.println("Connected to WiFi.");
    s_debug("Connected to WiFi.");
}

//============================================================================
/**
 * @brief Detecting django server ip adress .
 */
void detectIPHandler(AsyncWebServerRequest *request = nullptr)
{
    djangoOnline = true;
    lastPingTime = millis();

    // Verificăm dacă adresa IP a clientului este setată
if (clientIPAddress.isEmpty() || clientIPAddress != request->client()->remoteIP().toString())
    {
        IPAddress clientIP = request->client()->remoteIP();
        clientIPAddress = clientIP.toString();

        // Verificăm dacă a fost primit parametrul "check_interval"
        if (request->hasParam("check_interval"))
        {
            checkInterval = request->getParam("check_interval")->value().toInt() * 1000;
        }
        else
        {
            request->send(200, "text/plain", "No check_interval provided.");
        }

        // Setarea URL-urilor în funcție de IP
        if (isLocalServer(clientIPAddress))
        {
            lightStatusUrl = "http://" + clientIPAddress + ":8000/lights_status/";
            serialPostUrl = "http://" + clientIPAddress + ":8000/esp/serial_data/";
        }
        else
        {
            lightStatusUrl = "http://" + clientIPAddress + "/lights_status/";
            serialPostUrl = "http://" + clientIPAddress + "/esp/serial_data/";
        }

        Serial.println("Django IP is: " + clientIPAddress);
    }
    else if (checkInterval == 0)
    {
        // Dacă IP-ul este deja setat și nu există check_interval
        if (request->hasParam("check_interval"))
        {
            checkInterval = request->getParam("check_interval")->value().toInt() * 1000;
            request->send(200, "Give me check_interval var");
                        s_debug("cjeck=0 and hasparam");

        }
                    s_debug("In check=0");

    }
    else
    {
        // Dacă IP-ul este deja setat și nu există check_interval
        if (request->hasParam("check_interval"))
        {
            checkInterval = request->getParam("check_interval")->value().toInt() * 1000;
            request->send(200, "text/plain", "New interval received: " + String(checkInterval));
            s_debug("In hasPar");
        }
        else
        {
            request->send(200, "text/plain", "Home is Online");
                        s_debug("in else has par");

        }
    }
}
/**
 * @brief Displays the current IP address of the device.
 */
void displayIP()
{
    IPAddress ip = WiFi.localIP();
    String ipText = "MY IP: " + ip.toString();
    s_debug(ipText);
}

//============================================================================

/**
 * @brief Handles OTA firmware updates from the server.
 * Prints progress and handles errors.
 */
void handleUpdateStart(AsyncWebServerRequest *request, String filename, size_t index, uint8_t *data, size_t len, bool final)
{
    if (!index)
    {
        Serial.printf("Update Start: %s\n", filename.c_str());
        s_debug("Update start:");
        if (filename == "firmware.bin")
        {
            Update.begin(UPDATE_SIZE_UNKNOWN);
        }
        else if (filename == "spiffs.bin")
        {
            Update.begin(UPDATE_SIZE_UNKNOWN, U_SPIFFS);
        }
        else if (filename == "bootloader.bin")
        {
            Update.begin(UPDATE_SIZE_UNKNOWN, U_FLASH, 0x1000);
        }
        else if (filename == "partitions.bin")
        {
            Update.begin(UPDATE_SIZE_UNKNOWN, U_FLASH, 0x8000);
        }
        else
        {
            Serial.println("File is not supported for updates.");
            s_debug("File is not supported ");
            return;
        }
    }

    if (!Update.hasError())
    {
        Update.write(data, len);
        int progress = (index + len) * 100 / request->contentLength();
    }

    if (final)
    {
        if (Update.end(true))
        {
            Serial.printf("Update Success: %u\n", index + len);
        }
        else
        {
            Serial.printf("Update Error: %s\n", Update.errorString());
            request->send(500, "text/plain", "Update Failed: " + String(Update.errorString()));
        }
    }
}

//============================================================================

/**
 * @brief Encodes the input string in Base64.
 * @param str Input string.
 * @return Base64 encoded string.
 */
String base64Encode(String str)
{
    return base64::encode(str); // Encode using densaugeo/base64 library
}

//============================================================================
// Function to set up the server
void serverSetup()
{
    //============================================================================
    server.on("/control_led", HTTP_GET, [](AsyncWebServerRequest *request)
              {
                  String room, light, action;
                  if (request->hasParam("room"))
                  {
                      room = request->getParam("room")->value();
                      Serial.println("Room: " + room);
                  }
                  if (request->hasParam("light"))
                  {
                      light = request->getParam("light")->value();
                      Serial.println("Light: " + light);
                  }
                  if (request->hasParam("action"))
                  {
                      action = request->getParam("action")->value();
                      Serial.println("Action: " + action);
                  }
                  String combinedText = room + " " + light + " is: " + action;
                  djangoOnline = true;
                  s_debug(combinedText);
                  request->send(200, "application/json", " {\"status\":\"success\"} "); });

    //============================================================================

    // Handler for OPTIONS requests (preflight request for CORS)
    server.on("/django_update_firmware", HTTP_OPTIONS, [](AsyncWebServerRequest *request)
              {
    djangoOnline = true;
    AsyncWebServerResponse *response = request->beginResponse(200);
    response->addHeader("Access-Control-Allow-Origin", "*");  // Allow access from any origin
    response->addHeader("Access-Control-Allow-Methods", "POST, GET, OPTIONS");
    response->addHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");
    request->send(response); });

    //============================================================================
    // Handler for POST requests
    server.on("/django_update_firmware", HTTP_POST, [](AsyncWebServerRequest *request)
              {
    if (!Update.hasError()) {
        AsyncWebServerResponse *response = request->beginResponse(200, "text/plain", "Update Success! Rebooting...");
        response->addHeader("Access-Control-Allow-Origin", "*");  // Allow access from any origin
        response->addHeader("Connection", "close");
        request->send(response);
        ESP.restart();
    } else {
        AsyncWebServerResponse *response = request->beginResponse(500, "text/plain", "Update Failed");
        response->addHeader("Access-Control-Allow-Origin", "*");  // Allow access from any origin
        request->send(response);
    } }, handleUpdateStart);

    //============================================================================

    server.on("/", HTTP_GET, detectIPHandler);
    //============================================================================

    // New route to get or set variables
    server.on("/variable", HTTP_GET, [](AsyncWebServerRequest *request)
              {
        if (request->hasParam("action") && request->hasParam("var_name")) {
            String action = request->getParam("action")->value();
            String var_name = request->getParam("var_name")->value();

            // Handle "get" action
            if (action == "get") {
                if (var_name == "ssid") {
                    request->send(200, "application/json", "{\"value\": \"" + ssid + "\"}");
                } else if (var_name == "password") {
                    request->send(200, "application/json", "{\"value\": \"" + password + "\"}");
                } else if (var_name == "djangoUserName") {
                    request->send(200, "application/json", "{\"value\": \"" + djangoUserName + "\"}");
                } else {
                    request->send(404, "application/json", "{\"error\": \"Unknown variable.\"}");
                }
            }

            // Handle "set" action
            else if (action == "set" && request->hasParam("value")) {
                String value = request->getParam("value")->value();
                if (var_name == "ssid") {
                    ssid = value;
                    request->send(200, "application/json", "{\"status\": \"success\", \"message\": \"SSID updated.\"}");
                } else if (var_name == "password") {
                    password = value;
                    request->send(200, "application/json", "{\"status\": \"success\", \"message\": \"Password updated.\"}");
                } else if (var_name == "djangoUserName") {
                    djangoUserName = value;
                    request->send(200, "application/json", "{\"status\": \"success\", \"message\": \"Django username updated.\"}");
                } else {
                    request->send(404, "application/json", "{\"error\": \"Unknown variable.\"}");
                }
            } else {
                request->send(400, "application/json", "{\"error\": \"Invalid action or missing value.\"}");
            }
        } else {
            request->send(400, "application/json", "{\"error\": \"Missing action or variable name.\"}");
        } });

    server.begin();
}

//============================================================================

/**
 * @brief Prints a message to the serial console and the M5 display (if present).
 * @param msg Message to print.
 * @param col Column position on the display.
 * @param row Row position on the display.
 */
void m5_debug(String msg, uint16_t col, uint16_t row)
{
#ifdef M5CORE2_DEBUG
    lcd.setCursor(col, row);
    lcd.fillRect(col, row, 320, 20, BLACK); // Clear the area where the text will be displayed
    lcd.println(msg);
#endif
}
void s_debug(String msg)
{
#ifdef SERIAL_DEBUG
    Serial.println(msg);
#endif
}