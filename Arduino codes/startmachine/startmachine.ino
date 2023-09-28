#include <WiFi.h>
#include <PubSubClient.h>

const char* ssid = "Tec-IoT";
const char* password = "spotless.magnetic.bridge";

const char* mqtt_server = "10.25.75.245";
const int mqtt_port = 1883;
const char* mqtt_topic1 = "machine_state";
const char* mqtt_topic2 = "Tipo_corte";

const int digitalInputPin1 = 23; // Use GPIO pin 23
const int digitalInputPin2 = 22; // Use GPIO pin 22
const int digitalInputPin3 = 21; // Use GPIO pin 21

WiFiClient espClient;
PubSubClient client(espClient);

bool isCutting = false;

int prevState1 = LOW;
int prevState2 = LOW;
int prevState3 = LOW;

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
  pinMode(digitalInputPin1, INPUT);
  pinMode(digitalInputPin2, INPUT);
  pinMode(digitalInputPin3, INPUT);

  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
}

unsigned long lastPublishTime = 0;
unsigned long publishInterval = 1000;

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  int state1 = digitalRead(digitalInputPin1);
  int state2 = digitalRead(digitalInputPin2);
  int state3 = digitalRead(digitalInputPin3);

  if (state1 != prevState1 || state2 != prevState2 || state3 != prevState3) {
    prevState1 = state1;
    prevState2 = state2;
    prevState3 = state3;

    int highCount = state1 + state2 + state3;

    unsigned long currentTime = millis();
    if (currentTime - lastPublishTime >= publishInterval) {
      lastPublishTime = currentTime;
      Serial.print("Sensor states at ");
      Serial.print(currentTime);
      Serial.print("ms: ");
      Serial.print(state1);
      Serial.print(state2);
      Serial.println(state3);
    }

    if (state1 == HIGH && state2 == HIGH && state3 == HIGH) {
      if (!isCutting) {
        Serial.println("Cortando Baja");
        client.publish(mqtt_topic2, "Baja");
        client.publish(mqtt_topic1, "start_cutting");
        isCutting = true;
      }
    } else if (state1 == HIGH && state2 == LOW) {
      if (!isCutting) {
        Serial.println("Cortando ALta");
        client.publish(mqtt_topic2, "ALta");
        client.publish(mqtt_topic1, "start_cutting");
        isCutting = true;
      }
    } else if (state1 == LOW && state2 == LOW && state3 == LOW) {
      if (isCutting) {
        client.publish(mqtt_topic1, "stop_cutting");
        Serial.println("Stop cutting");
        isCutting = false;
      }
    }
  }

  delay(10);
}