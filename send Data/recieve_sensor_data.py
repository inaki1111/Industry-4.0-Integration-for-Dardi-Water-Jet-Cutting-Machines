import datetime
import csv
import time
import paho.mqtt.client as mqtt

filename = "sensor_data.csv"
fields = ["Time", "Encoder_X", "Encoder_Y", "Acceleration", "Current_1", "Current_2", "Current_3"]

data_state = {field: None for field in fields[1:]}  # Do not include 'Time' as it will be populated separately

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        global data_state
        for field in fields[1:]:  # Subscribe to fields excluding 'Time'
            client.subscribe(field)
    else:
        print("Connection failed")

def on_message(client, userdata, message):
    print(f"Received message '{message.payload}' on topic '{message.topic}'")
    global data_state
    data_state[message.topic] = message.payload.decode('utf-8')
    
    if all(value is not None for value in data_state.values()):
        data_state["Time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(filename, 'a', newline='') as csvfile:
            csvwriter = csv.DictWriter(csvfile, fieldnames=fields)
            csvwriter.writerow(data_state)
        # Resetting data_state
        data_state = {field: None for field in fields[1:]}

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("your_broker_address", 1883, 60)

with open(filename, 'w', newline='') as csvfile:
    csvwriter = csv.DictWriter(csvfile, fieldnames=fields)
    csvwriter.writeheader()

client.loop_start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting...")

client.loop_stop()
client.disconnect()
