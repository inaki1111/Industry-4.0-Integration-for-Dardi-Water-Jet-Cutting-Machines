import serial
import paho.mqtt.client as mqtt

# MQTT broker details
mqtt_broker = "localhost"
mqtt_port = 1883

# Define states
IDLE_STATE = "000"
START_STATE = ["110", "111", "101", "100"]

publish_topic = "start_process"
status_topic = "Tipo_corte"  # This is the new topic for "alta" and "baja"
process_started_msg = "send_data"
process_stopped_msg = "stop_send_data"

# Initialize the current state
current_state = IDLE_STATE

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")

def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))

# MQTT Setup
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(mqtt_broker, mqtt_port, 60)
client.loop_start()

def read_from_serial(port, baudrate=115200):
    global current_state
    # Open the serial port
    with serial.Serial(port, baudrate, timeout=1) as ser:
        try:
            while True:
                # Read a line from the serial port
                line_bytes = ser.readline()
                # Try decoding the bytes
                try:
                    line_str = line_bytes.decode('utf-8').strip()
                    if line_str:
                        print(line_str)
                        
                        # Check state transitions
                        if line_str in START_STATE and current_state == IDLE_STATE:
                            current_state = line_str
                            client.publish(publish_topic, process_started_msg)

                            # Check for the "alta" and "baja" conditions
                            if line_str == "110":
                                client.publish(status_topic, "011")
                                print("Cortando en alta")
                            elif line_str == "111":
                                client.publish(status_topic, "111")
                                print("Cortando en baja")

                            elif line_str == "000":
                                client.publish(status_topic, "000")
                                print("apagado")

                            elif line_str == "101":
                                client.publish(status_topic, "101")
                                print("baja sin abrasivo")

                            elif line_str == "001":
                                client.publish(status_topic, "001")
                                print("alta sin abrasivo")


                        elif line_str == IDLE_STATE and current_state in START_STATE:
                            current_state = IDLE_STATE
                            client.publish(publish_topic, process_stopped_msg)
                except UnicodeDecodeError:
                    print("Received non-UTF-8 encoded data: ", line_bytes)
        except KeyboardInterrupt:
            client.loop_stop()  # Stop the MQTT loop
            client.disconnect()  # Disconnect from the broker
            print("\nExiting...")

if __name__ == "__main__":
    port_name = "/dev/ttyUSB0"
    read_from_serial(port_name)
