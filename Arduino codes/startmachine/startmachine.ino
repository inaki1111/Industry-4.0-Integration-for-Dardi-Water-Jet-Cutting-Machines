#include <WiFi.h>
#include <PubSubClient.h>

// Replace with your Wi-Fi credentials
const char* ssid = "Tec-IoT";
const char* password = "spotless.magnetic.bridge";

// Replace with your MQTT broker details
const char* mqtt_server = "10.25.75.245";
const int mqtt_port = 1883;
const char* mqtt_topic = "machine_state"; // rapsp

// Digital input pin (D23)
const int digitalInputPin = 23; // Use GPIO pin 23

WiFiClient espClient;
PubSubClient client(espClient);

bool isHigh = false; // To keep track of the input state

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

void callback(char* topic, byte* payload, unsigned int length) {
  // Handle MQTT messages if needed
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP32Client")) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(digitalInputPin, INPUT);

  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
}

unsigned long lastPublishTime = 0; // To track the last time we published
unsigned long publishInterval = 1000; // Adjust this interval as needed (in milliseconds)

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  bool currentInputState = digitalRead(digitalInputPin);

  // Print sensor state with timestamp continuously
  unsigned long currentTime = millis();
  if (currentTime - lastPublishTime >= publishInterval) {
    lastPublishTime = currentTime;
    Serial.print("Sensor state at ");
    Serial.print(currentTime);
    Serial.print("ms: ");
    Serial.println(currentInputState);
  }

  if (currentInputState != isHigh) {
    isHigh = currentInputState; // Update the state

    if (isHigh) {
      client.publish(mqtt_topic, "send_data");
      Serial.println("Input state changed to HIGH");
    } else {
      client.publish(mqtt_topic, "stop_send_data");
      Serial.println("Input state changed to LOW");
    }
  }

  // Add a small delay to prevent excessive serial printing
  delay(10);
}
