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
using namespace websockets;

#include <esp_system.h> // Include header pentru esp_random și esp_fill_random

String websocket_server = "home-control-dbba5bec072c.herokuapp.com";
const uint16_t websocket_port = 443;               // Folosește portul 443 pentru WSS
const char *websocket_path = "/ws/socket-server/"; // URL-ul WebSocket definit în routing.py
bool useSecureWebSocket = true;                    // Asigură-te că folosești WSS
String rootCACertificate = "";


const char* websockets_connection_string = "wss://home-control-dbba5bec072c.herokuapp.com/ws/socket-server/";
void onMessageCallback(WebsocketsMessage message) {
    Serial.print("Got Message: ");
    Serial.println(message.data());
}

void onEventsCallback(WebsocketsEvent event, String data) {
    if(event == WebsocketsEvent::ConnectionOpened) {
        Serial.println("Connection Opened");
    } else if(event == WebsocketsEvent::ConnectionClosed) {
        Serial.println("Connection Closed");
    } else if(event == WebsocketsEvent::GotPing) {
        Serial.println("Got a Ping!");
    } else if(event == WebsocketsEvent::GotPong) {
        Serial.println("Got a Pong!");
    }
}




WebSocketsClient webSocket;
WiFiClientSecure client;
// WiFiClient client;

//============================================================================

struct Light;

struct Room;

std::map<String, Room> roomLightMap;

//============================================================================
mbedtls_entropy_context entropy;
mbedtls_ctr_drbg_context ctr_drbg;

#define M5CORE2
#ifdef M5CORE2
#include <M5Unified.h>
M5GFX &lcd = M5.Lcd;
#endif

AsyncWebServer server(80);

String base64Encode(String str);
void addBasicAuth(HTTPClient &http);
void reconnectWiFi();
void print(String msg, uint16_t col, uint16_t row);
void fetchInitialLightStates();
void printLightStates();
void serverSetup();
void displayIP();
void processSerialCommands();
void checkDjangoOnline();
void print(String msg, uint16_t col, uint16_t row);

void detectIPHandler(AsyncWebServerRequest *request);
bool localServer = true; // Variable that determines if using local or Heroku server

String ssid = WIFI_SSID;                 // Modifiable variable for WiFi SSID
String password = WIFI_PASSWORD;         // Modifiable variable for WiFi password
String djangoUserName = DJANGO_USERNAME; // Modifiable variable for Django username
String djangoPassword = DJANGO_PASSWORD; // Modifiable variable for Django password
unsigned long lastSendTime = 0;          // Variabilă pentru a reține timpul ultimei trimiteri
uint16_t setup_debug_time = 1000;
uint16_t loop_debug_time = 10000;
String clientIPAddress = "";
bool checkServer = true;
bool djangoOnline = false;
bool update = true;
uint32_t lastPingTime = 0;
// Variabile globale
int checkInterval = 0; // pentru a stoca valoarea ca int

String serverCheckUrl = "";
String lightStatusUrl = "";
String serialPostUrl = "";

// Endpoint for posting serial data
//============================================================================

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

void monitorHeap(String tag)
{
    Serial.println(tag + ": Free heap memory: " + String(ESP.getFreeHeap()) + " bytes");
}

void spiffsInit()
{
    if (!SPIFFS.begin(true))
    {
        Serial.println("An error has occurred while mounting SPIFFS");
        return;
    }
    else
    {
        Serial.println("SPIFFS mounted successfully");
    }
    // Example: List all files in SPIFFS
    File root = SPIFFS.open("/");
    File certFile = SPIFFS.open("/cert.pem", "r");
    Serial.println(certFile.size());
    if (certFile)
    {
        String cert = certFile.readString();
        if (cert.length() == 0)
        {
            Serial.println("Certificatul este gol.");
        }
        else
        {
            Serial.println("Certificat is: " + cert);
        }

        Serial.println("Certificat is :" + cert);
        Serial.println("Certificat is :" + certFile);
        rootCACertificate = cert;

        certFile.close();

        // Setează certificatul pentru conexiunea SSL
        client.setCACert(cert.c_str());
        
        Serial.println("Certificat încărcat din SPIFFS.");
    }
    else
    {
        Serial.println("Nu s-a găsit certificatul în SPIFFS.");
    }
    File file = root.openNextFile();
    while (file)
    {
        Serial.print("FILE: ");
        Serial.println(file.name());
        file = root.openNextFile();
    }
    
}

void webSocketEvent(WStype_t type, uint8_t *payload, size_t length)
{
    switch (type)
    {
    case WStype_DISCONNECTED:
        Serial.println("WebSocket Disconnected!");
        break;
    case WStype_CONNECTED:
        Serial.println("WebSocket Connected!");
        break;
    case WStype_TEXT:
        Serial.printf("Received message: %s\n", payload);
        break;
    case WStype_ERROR:
        Serial.println("WebSocket Error occurred!");
        break;
    case WStype_BIN:
        Serial.printf("Binary message received, length: %d\n", length);
        break;
    default:
        Serial.println("Unknown WebSocket event");
        break;
    }
}

// Funcție care folosește esp_fill_random pentru a genera random data
void init_rng()
{
    uint8_t rng_seed[32];
    esp_fill_random(rng_seed, sizeof(rng_seed)); // Umplem buffer-ul cu date aleatorii

    mbedtls_entropy_init(&entropy);
    mbedtls_ctr_drbg_init(&ctr_drbg);

    const char *personalization = "ssl_rng";
    int ret = mbedtls_ctr_drbg_seed(&ctr_drbg, mbedtls_entropy_func, &entropy, rng_seed, sizeof(rng_seed));

    if (ret != 0)
    {
        Serial.println("Failed to initialize RNG.");
    }
    else
    {
        Serial.println("RNG initialized.");
    }
}

void checkSSLError()
{
    char error_buf[100]; // Buffer pentru mesajul de eroare
    if (client.lastError(error_buf, sizeof(error_buf)) != 0)
    {
        Serial.print("SSL Error: ");
        Serial.println(error_buf);
    }
    else
    {
        Serial.println("No SSL Error.");
    }
}

void setup()
{
#ifdef M5CORE2
    auto cfg = M5.config();
    M5.begin(cfg);
    M5.Display.setTextSize(2);
    M5.Display.setCursor(0, 0);
    M5.Display.fillScreen(BLACK); // Clear the screen
#endif
    Serial.begin(115200);
    if (djangoUserName.isEmpty() || djangoPassword.isEmpty())
    {
        print("Django credentials are missing.", 0, 0);
        delay(setup_debug_time);
    }
    else
    {
        Serial.println("Django credentials are present.");
        print("Django credentials are present.", 0, 0);
        print("Django Username: " + djangoUserName, 0, 20);
        print("Django Password: " + djangoPassword, 0, 40);
        delay(setup_debug_time);
    }

    reconnectWiFi();
    spiffsInit();
    serverSetup();
    displayIP();
#ifdef M5CORE2
    M5.Display.setTextSize(2);
    M5.Display.setCursor(0, 0);
    M5.Display.fillScreen(BLACK); // Clear the screen
#endif
    if (useSecureWebSocket)
    {
        // Folosește WebSocket securizat (wss)
        webSocket.beginSSL(websocket_server.c_str(), websocket_port, websocket_path, rootCACertificate, "arduino");
        Serial.println("Using wss:// connection");
    }
    else
    {
        // Folosește WebSocket nesecurizat (ws)
        webSocket.begin(websocket_server, websocket_port, websocket_path);
        Serial.println("Using ws:// connection");
    }
    webSocket.onEvent(webSocketEvent);
    webSocket.setReconnectInterval(20000); // 20 secunde în loc de 10 secunde
    client.setHandshakeTimeout(60);        // Setează timeout-ul handshake la 60 de secunde
    // Alte inițializări
    if (useSecureWebSocket)
    {
        webSocket.beginSSL(websocket_server.c_str(), websocket_port, websocket_path, rootCACertificate, "arduino");
        Serial.println("Using wss:// connection");
        checkSSLError(); // Verifică imediat erorile SSL
    }
    else
    {
        webSocket.begin(websocket_server, websocket_port, websocket_path);
        Serial.println("Using ws:// connection");
    }
}

//============================================================================

void loop()
{
    static uint32_t serverTimer;
    static unsigned long lastReconnectAttempt = 0;

    if (!webSocket.isConnected() && (millis() - lastReconnectAttempt > 10000))
    { // 10 secunde între încercările de reconectare
        Serial.println("WebSocket not connected. Trying to reconnect...");
        webSocket.beginSSL(websocket_server.c_str(), websocket_port, websocket_path, rootCACertificate, "arduino");
        lastReconnectAttempt = millis();
    }

    webSocket.loop();

    if ((millis() - serverTimer > (checkInterval == 0 ? 5000 : checkInterval)))
    {
        IPAddress serverIP;
        if (WiFi.hostByName(websocket_server.c_str(), serverIP))
        {
            Serial.print("WebSocket server IP: ");
            Serial.println(serverIP);
        }
        else
        {
            Serial.println("Failed to resolve WebSocket server IP");
        }

        Serial.println("Attempting WebSocket connection to: wss://" + websocket_server + websocket_path);
        printVariables();
        static uint16_t count;
        serverTimer = millis();
        print(String(djangoOnline ? "Django Online" : "Django Offline"), 0, 0);
        // Trimiterea mesajului către server
       String message = "Hello from ESP32 at " + String(millis());

        // Trimite mesajul prin WebSocket
        webSocket.sendTXT(message);
        update = false;
    }
    checkDjangoOnline();
    processSerialCommands(); // Continuously process serial commands    webSocket.loop(); // WebSocket trebuie să fie procesat constant pentru a gestiona conexiunile și mesajele
}

//============================================================================
void checkDjangoOnline()
{
    static uint32_t currentTime = 0;

    if ((millis() - lastPingTime) > (checkInterval == 0 ? 10000 : checkInterval * 2))
    {
        if (djangoOnline == true)
        {
            djangoOnline = false;
            update = true;
        }
    }
}

//============================================================================

// Structures to hold light information dynamically
struct Light
{
    String name;
    bool state;
};

//============================================================================

struct Room
{
    String state;
    std::vector<Light> lights;
};

//============================================================================
void processSerialCommands()
{
    if (Serial.available() > 0)
    {
        String input = Serial.readStringUntil('\n');
        input.trim();

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
                djangoPassword = input.substring(17);
            }
            else if (input.startsWith("set interval "))
            {
                loop_debug_time = input.substring(13).toInt();
            }
            // Setăm URL pentru verificarea serverului
            else if (input.startsWith("set url_check "))
            {
                serverCheckUrl = input.substring(14); // Scoate partea "set url_check "
                Serial.println("Server check URL updated to: " + serverCheckUrl);
            }
            // Setăm URL pentru starea luminilor
            else if (input.startsWith("set url_light "))
            {
                lightStatusUrl = input.substring(14); // Scoate partea "set url_light "
                Serial.println("Light status URL updated to: " + lightStatusUrl);
            }
            // Setăm URL pentru trimiterea de date seriale
            else if (input.startsWith("set url_serial "))
            {
                serialPostUrl = input.substring(15); // Scoate partea "set url_serial "
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

// Function to add Basic Authentication header to each HTTP request
void addBasicAuth(HTTPClient &http)
{
    if (djangoUserName.isEmpty() || djangoPassword.isEmpty())
    {
        print("Username or password for django is missing.", 0, 180);
        return;
    }
    String auth = base64Encode(djangoUserName + ":" + djangoPassword);
    print(String("Auth urlcode = " + auth), 0, 180);
    http.addHeader("Authorization", "Basic " + auth);
}

//============================================================================
bool isLocalServer(const String &ipAddress)
{
    return ipAddress.startsWith("192.168") || ipAddress.startsWith("10.") || ipAddress == "127.0.0.1";
}

//============================================================================
void fetchInitialLightStates()
{
    if (WiFi.status() == WL_CONNECTED)
    {
        // Creăm un obiect local HTTPClient
        HTTPClient http;

        // Verificăm dacă URL-ul este valid
        if (!lightStatusUrl.startsWith("http"))
        {
            print("Invalid lightStatusUrl format!", 0, 20);
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
                print("Invalid light format!", 0, 20);
                return;
            }

            size_t jsonCapacity = 1048; // Capacitate ajustată
            DynamicJsonDocument doc(jsonCapacity);
            DeserializationError error = deserializeJson(doc, payload);

            if (error)
            {
                Serial.print(F("Error parsing JSON: "));
                print("Error parsing JSON:", 0, 20);
                Serial.println(error.f_str());
                return;
            }

            roomLightMap.clear(); // Șterge datele anterioare

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

        http.end(); // Încheie conexiunea
    }
}

//============================================================================

// Function to print the current light states
void printLightStates()
{
    int line = 0;
    for (const auto &roomEntry : roomLightMap)
    {
        Serial.printf("Room: %s\n", roomEntry.first.c_str());
        print("Room: " + roomEntry.first, 0, line);
        line += 20;
        for (const Light &light : roomEntry.second.lights)
        {
            String lightStateText = "Light: " + light.name + ", State: " + (light.state ? "on" : "off");
            Serial.println(lightStateText);
            print(lightStateText, 0, line);
            line += 20;
        }
    }
}

//============================================================================

// Function to reconnect to Wi-Fi
void reconnectWiFi()
{

    WiFi.begin(ssid, password);
    unsigned long startAttemptTime = millis();

    while (WiFi.status() != WL_CONNECTED && (millis() - startAttemptTime) < 10000)
    {
        delay(1000);
        Serial.println("Connecting to WiFi...");
        print("Connecting to WiFi...", 0, 40);
    }
    if (WiFi.status() != WL_CONNECTED)
    {
        Serial.println("Failed to connect. Rebooting...");
    }
    Serial.println("Conectat la WiFi.");
    print("Connected to WiFi.", 0, 40);
}

//============================================================================

// Function to display the IP address
void displayIP()
{
    IPAddress ip = WiFi.localIP();
    String ipText = "MY IP: " + ip.toString();
    print(ipText, 0, 10);
}

//============================================================================

void handleUpdateStart(AsyncWebServerRequest *request, String filename, size_t index, uint8_t *data, size_t len, bool final)
{
    if (!index)
    {
        Serial.printf("Update Start: %s\n", filename.c_str());
        print("Update start:", 0, 60);
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
            print("File is not supported ", 0, 60);
            return;
        }
    }
    if (!Update.hasError())
    {
        Update.write(data, len);
        int progress = (index + len) * 100 / request->contentLength();
        String progressStr = String(progress); // Creăm un String separat
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
            request->send(500, "text/plain", "Update Failed: " + String(Update.errorString())); // Adaugă un răspuns clar către client
        }
    }
}

void detectIPHandler(AsyncWebServerRequest *request = nullptr)
{
    djangoOnline = true;
    lastPingTime = millis();

    // Verificăm dacă adresa IP a clientului este setată
    if (clientIPAddress.isEmpty())
    {
        IPAddress clientIP = request->client()->remoteIP();
        clientIPAddress = clientIP.toString();
        websocket_server = clientIPAddress; // IP-ul serverului Django

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
        }
    }
    else
    {
        // Dacă IP-ul este deja setat și nu există check_interval
        if (request->hasParam("check_interval"))
        {
            checkInterval = request->getParam("check_interval")->value().toInt() * 1000;
            request->send(200, "text/plain", "New interval received: " + String(checkInterval));
        }
        else
        {
            request->send(200, "text/plain", "Home is Online");
        }
    }
}

// Function to set up the server
void serverSetup()
{

    // Handler pentru primirea certificatului prin POST
    server.on("/upload_cert", HTTP_POST, [](AsyncWebServerRequest *request)
              {
    if (request->hasParam("certificate", true)) {
        // Certificatul este trimis printr-un parametru POST
        AsyncWebParameter* p = request->getParam("certificate", true);
        String certificate = p->value();

        // Salvează certificatul în SPIFFS
        File certFile = SPIFFS.open("/cert.pem", FILE_WRITE);
        if (certFile) {
            certFile.print(certificate);
            certFile.close();
            Serial.println("Certificat salvat cu succes!");

            // Răspunde clientului că certificatul a fost primit și salvat
            request->send(200, "text/plain", "Certificate received and saved successfully.");
        } else {
            Serial.println("Failed to open cert.pem for writing.");
            request->send(500, "text/plain", "Failed to save certificate.");
        }
        rootCACertificate = certificate;
    } else {
        Serial.println("No certificate received.");
        request->send(400, "text/plain", "No certificate received.");
    } });

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
                  djangoOnline=true;
                  print(combinedText,0,80);
                  request->send(200, "application/json", " {\"status\":\"success\"} "); });

    //============================================================================

    // Handler pentru cererile OPTIONS (preflight request pentru CORS)
    server.on("/django_update_firmware", HTTP_OPTIONS, [](AsyncWebServerRequest *request)
              {
    djangoOnline=true;
    AsyncWebServerResponse *response = request->beginResponse(200);
    response->addHeader("Access-Control-Allow-Origin", "*");  // Permite accesul de pe orice sursă
    response->addHeader("Access-Control-Allow-Methods", "POST, GET, OPTIONS");
    response->addHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");
    request->send(response); });

    //============================================================================
    // Handler pentru cererile POST
    server.on("/django_update_firmware", HTTP_POST, [](AsyncWebServerRequest *request)
              {

    if (!Update.hasError()) {
        AsyncWebServerResponse *response = request->beginResponse(200, "text/plain", "Update Success! Rebooting...");
        
        response->addHeader("Access-Control-Allow-Origin", "*");  // Permite accesul de pe orice sursă
        response->addHeader("Connection", "close");
        request->send(response);
        ESP.restart();
    } else {
        AsyncWebServerResponse *response = request->beginResponse(500, "text/plain", "Update Failed");
        response->addHeader("Access-Control-Allow-Origin", "*");  // Permite accesul de pe orice sursă
        request->send(response);
    } }, handleUpdateStart);

    //============================================================================

    server.on("/", HTTP_GET, detectIPHandler);
    //============================================================================

    server.begin();
}

//============================================================================

String base64Encode(String str)
{
    return base64::encode(str); // Encode using densaugeo/base64 library
}

//============================================================================

void print(String msg, uint16_t col, uint16_t row)
{
    Serial.println(msg);
#ifdef M5CORE2
    lcd.setCursor(col, row);
    lcd.fillRect(col, row, 320, 20, BLACK); // Clear the area where the text will be displayed
    lcd.println(msg);
#endif
}