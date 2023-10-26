import paho.mqtt.client as mqtt
import time

# Define MQTT settings
mqtt_broker_host = "localhost"  # Replace with your MQTT broker's host
mqtt_topic = "topic"             # Replace with the MQTT topic you want to subscribe to

# Global variables
counting = False
count = 0

# Callback when a connection to the MQTT broker is established
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code " + str(rc))
    # Subscribe to the MQTT topic upon connection
    client.subscribe(mqtt_topic)

# Callback when a message is received from the MQTT broker
def on_message(client, userdata, msg):
    global counting, count  # Use the global variables
    payload = msg.payload.decode("utf-8")  # Convert the payload to a string
    print("Received message on topic '" + msg.topic + "': " + payload)

    if payload == "start":
        counting = True
        start_counting()
    elif payload == "stop":
        counting = False
        count = 0
        print("Count reset.")

# Function to start counting and print numbers
def start_counting():
    global count
    while counting:
        print("Count:", count)
        count += 1
        time.sleep(1)  # Sleep for 1 second between counts

# Create an MQTT client instance
client = mqtt.Client()

# Set callback functions
client.on_connect = on_connect
client.on_message = on_message

# Connect to the MQTT broker
client.connect(mqtt_broker_host, 1883, 60)

# Start the MQTT client loop
client.loop_forever()
