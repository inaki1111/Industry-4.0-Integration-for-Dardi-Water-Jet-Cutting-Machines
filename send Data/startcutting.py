import paho.mqtt.client as mqtt

# MQTT broker details
mqtt_broker = "10.25.75.245"
mqtt_port = 1883

# Topics
subscribe_topic = "machine_state"
publish_topic = "start_process"

# Callback when the client receives a CONNACK response from the server
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(subscribe_topic)

# Callback when a message is received from the subscribed topic
def on_message(client, userdata, msg):
    message = msg.payload.decode("utf-8")
    print(f"Received message: {message}")

    # Check if the received message is the trigger message
    if message == "send_data":
        print("python The process has started")
        # Publish a message to another topic
        client.publish(publish_topic, "send_data")
    else:
        print(" python The process has stopped ")
        client.publish(publish_topic, "stop_send_data")

# Create an MQTT client
client = mqtt.Client()

# Set the callbacks
client.on_connect = on_connect
client.on_message = on_message

# Connect to the MQTT broker
client.connect(mqtt_broker, mqtt_port, 60)

# Start the MQTT client loop to handle incoming messages
client.loop_forever()
