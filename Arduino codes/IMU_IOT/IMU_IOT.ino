#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>
#include <WiFi.h>
#include <PubSubClient.h>

#define BNO055_SAMPLERATE_DELAY_MS (100)
Adafruit_BNO055 bno = Adafruit_BNO055(55);

const char* ssid = "Tec-IoT";
const char* password = "Tec-IoT";
const char* mqtt_server = "MQTT_BROKER_IP"; // rasp ip

WiFiClient espClient;
PubSubClient client(espClient);

const char* controlTopic = "esp32/start_stop_control";
const char* accelerationTopic = "acceleration";

bool sendData = false;

void setup() {
  Serial.begin(115200);
  if (!bno.begin())
  {
    Serial.print("No BNO055 detected.");
    while (1);
  }

  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  if (sendData) {
    sensors_event_t event;
    bno.getEvent(&event);
    
    float accelerationX = event.acceleration.x;
    float accelerationY = event.acceleration.y;
    float accelerationZ = event.acceleration.z;
    
    // Calculate average acceleration
    float averageAcceleration = (accelerationX + accelerationY + accelerationZ) / 3.0;
    
    // Publish average acceleration to MQTT topic
    client.publish(accelerationTopic, String(averageAcceleration).c_str());
    
    delay(1000); // Send data every second
  }
}

void callback(char* topic, byte* payload, unsigned int length) {
  String msg = "";
  for (unsigned int i = 0; i < length; i++) {
    msg += (char)payload[i];
  }
  Serial.println("Received message on topic: " + String(topic) + " - Message: " + msg);

  if (strcmp(topic, controlTopic) == 0) {
    if (msg == "start") {
      sendData = true;
      Serial.println("Started sending average acceleration data.");
    } else if (msg == "stop") {
      sendData = false;
      Serial.println("Stopped sending average acceleration data.");
    }
  }
}

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ArduinoClient")) {
      Serial.println("connected");
      client.subscribe(controlTopic);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}
