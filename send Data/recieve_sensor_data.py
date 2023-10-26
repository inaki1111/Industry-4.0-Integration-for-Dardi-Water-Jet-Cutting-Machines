import csv
import paho.mqtt.client as mqtt

# MQTT topics to subscribe to
topics = ["Time", "Encoder_X", "Encoder_Y", "Acceleration", "Current_1", "Current_2", "Current_3", "Tipo_Corte"]

# CSV file settings
filename = "sensor_data.csv"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        for topic in topics:
            client.subscribe(topic)
    else:
        print("Connection failed")

def on_message(client, userdata, message):
    topic = message.topic
    payload = message.payload.decode('utf-8')
    
    with open(filename, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow([topic, payload])

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("10.25.11.206", 1883, 60)


with open(filename, 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)

client.loop_forever()
import csv
import paho.mqtt.client as mqtt

# MQTT topics to subscribe to
topics = ["Time", "Encoder_X", "Encoder_Y", "Acceleration", "Current_1", "Current_2", "Current_3", "Tipo_Corte"]

# CSV file settings
filename = "sensor_data.csv"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        for topic in topics:
            client.subscribe(topic)
            print("Subscribed to topic:", topic)
    else:
        print("Connection failed")

def on_message(client, userdata, message):
    topic = message.topic
    payload = message.payload.decode('utf-8')
    print(f"Received message on topic '{topic}': {payload}")
    
    with open(filename, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow([topic, payload])

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)

with open(filename, 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(["Topic", "Data"])  # Write header row

client.loop_forever()
