//Mark Ireland
//Code for ESP8266 Party Button!
#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>
#include <ESP8266HTTPClient.h>
#include "wifiConfig.h"

ESP8266WiFiMulti WiFiMulti;

bool partyStarted = 0;

void setup() {
    Serial.begin(115200);
    delay(50);
    WiFiMulti.addAP(ssid, pass);
    while(WiFiMulti.run() != WL_CONNECTED)
    {
      delay(500);
    }
    IPAddress ip = WiFi.localIP();
    Serial.println();
    Serial.println("{\"ip\":\"" + String(ip[0]) + "." + String(ip[1]) + "." + String(ip[2]) + "." + String(ip[3]) + "\"}");
    pinMode(2, INPUT);
}

void loop(){
  if (digitalRead(2) == LOW && partyStarted == 0)
  {
    Serial.println("Start the Party!");
    startParty();
  }
}


void startParty() {
        HTTPClient http;
        Serial.println("[HTTP] begin");
        http.begin("192.168.1.222", 3000, "/start"); //HTTP

        Serial.println("[HTTP] GET");
        // start connection and send HTTP header
        int httpCode = http.GET();
        if(httpCode) {
            // HTTP header has been send and Server response header has been handled
            Serial.printf("[HTTP] GET... code: %d\n", httpCode);

            // file found at server
            if(httpCode == 200) {
                String payload = http.getString();
                Serial.println("Party has Started!");
                partyStarted = 1;
            }
        } else {
            Serial.println("[HTTP] GET... failed, no connection or no HTTP server");
        }
}

