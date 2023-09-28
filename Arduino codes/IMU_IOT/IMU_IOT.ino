#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_MPU6050.h>
#include <WiFi.h>
#include <PubSubClient.h>

// Replace with your network credentials
const char* ssid = "Tec-IoT";
const char* password = "spotless.magnetic.bridge";

// MQTT broker information
const char* mqtt_server = "10.25.75.245";
const int mqtt_port = 1883;

WiFiClient espClient;
PubSubClient client(espClient);

Adafruit_MPU6050 mpu;

const char* start_topic = "start_process";
const char* acceleration_topic = "Acceleration";

bool send_data = false;

void setup() {
  Serial.begin(115200);

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");

  // Set up MQTT
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);

  Wire.begin();
  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 sensor");
    while (1);
  }
  //client.subscribe(start_topic);
}

void callback(char* topic, byte* payload, unsigned int length) {
  String received_message = "";
  for (int i = 0; i < length; i++) {
    received_message += (char)payload[i];
  }

  Serial.print("Received message on topic '");
  Serial.print(topic);
  Serial.print("': ");
  Serial.println(received_message);

  if (strcmp(topic, start_topic) == 0) {
    if (received_message == "send_data") {
      send_data = true;
    } else if (received_message == "stop_send_data") {
      send_data = false;
    }
  }
}

void reconnect() {
  while (!client.connected()) {
    Serial.println("Attempting MQTT connection...");
    if (client.connect("ESP32Client")) {
      Serial.println("Connected to MQTT broker");
      client.subscribe(start_topic);
    } else {
      Serial.print("Failed, rc=");
      Serial.print(client.state());
      Serial.println(" Retrying in 5 seconds...");
      delay(5000);
    }
  }
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  if (send_data == true) {
    sensors_event_t a, g, temp;
    mpu.getEvent(&a, &g, &temp);

    float ax = a.acceleration.x;
    float ay = a.acceleration.y;
    float az = a.acceleration.z;

    // Calculate the average acceleration
    float absoluteAcc = sqrt(ax * ax + ay * ay + az * az);

    // Publish the average acceleration to the MQTT topic
    char message[10];
    snprintf(message, sizeof(message), "%.2f", absoluteAcc);
    client.publish(acceleration_topic, message);

    Serial.print("Average Acceleration: ");
    Serial.println(absoluteAcc);
  }

  delay(1000);
}