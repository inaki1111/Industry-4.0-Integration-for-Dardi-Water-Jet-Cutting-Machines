import paho.mqtt.client as mqtt

# MQTT broker details
mqtt_broker = "localhost"
print("brocker", mqtt_broker)
mqtt_port = 1883

# Topics
subscribe_topic = "machine_state"
publish_topic = "start_process"

# Define states
IDLE_STATE = 0
CUTTING_STATE = 1

# Initialize the current state
current_state = IDLE_STATE

# Callback when the client receives a CONNACK response from the server
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(subscribe_topic)

# Callback when a message is received from the subscribed topic
def on_message(client, userdata, msg):
    global current_state  # Use the global current_state variable

    message = msg.payload.decode("utf-8")
    print(f"Received message: {message}")

    # Check the current state and handle messages accordingly
    if current_state == IDLE_STATE:
        if message == "start_cutting":
            print("The process has started (IDLE to CUTTING)")
            current_state = CUTTING_STATE
            # Publish a message to another topic
            client.publish(publish_topic, "send_data")
    elif current_state == CUTTING_STATE:
        if message == "stop_cutting":
            print("The process has stopped (CUTTING to IDLE)")
            current_state = IDLE_STATE
            # Publish a message to another topic
            client.publish(publish_topic, "stop_send_data")
    else:
        print("Invalid state")

# Create an MQTT client
client = mqtt.Client()

# Set the callbacks
client.on_connect = on_connect
client.on_message = on_message

# Connect to the MQTT broker
client.connect(mqtt_broker, mqtt_port, 60)

# Start the MQTT client loop to handle incoming messages
client.loop_forever()
