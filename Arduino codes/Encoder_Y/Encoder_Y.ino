#include <Arduino.h>
#include <PubSubClient.h>
#include <WiFi.h>
#include <Encoder.h>

const char* ssid = "Tec-IoT";
const char* password = "spotless.magnetic.bridge";
const char* mqtt_server = "MQTT_BROKER_IP";   // raspberrypi ip

WiFiClient espClient;
PubSubClient client(espClient);

const char* controlTopic = "esp32/start_stop_control";
const char* encoderTopic = "encoder_y";

bool sendData = false;

Encoder myEncoder(2, 3); // Change pins to your encoder pins

void setup() {
  Serial.begin(115200);
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
    // Read encoder position and publish to MQTT topic
    long encoderValue = myEncoder.read();
    client.publish(encoderTopic, String(encoderValue).c_str());
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
      Serial.println("Started sending encoder data.");
    } else if (msg == "stop") {
      sendData = false;
      Serial.println("Stopped sending encoder data.");
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
