import cv2
import boto3
import paho.mqtt.client as mqtt
import time
import json
import signal
import sys

# Load AWS credentials from the config file
with open('/home/cimatec/Documentos/Sistema-de-industria-4.0-/send Data/config.json', 'r') as config_file:
    config = json.load(config_file)

# AWS credentials
aws_access_key_id = config['access_key']
aws_secret_access_key = config['secret_access_key']

# AWS S3 bucket information
bucket_name = 'mybucketcima'
s3_key = 'photo.jpg'  # Replace 'photo.jpg' with the desired file name

# MQTT broker information
mqtt_broker = "localhost"  # Replace with your MQTT broker address
mqtt_topic = "machine_state"

# Specify the desired camera index
camera_index = 0  # Change this to the index of your desired camera

# Specify the desired resolution here
width = 640  # Width of the resolution
height = 480  # Height of the resolution

# Initialize the webcam using the selected camera index
cap = cv2.VideoCapture(camera_index)

# Set the resolution
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

# Flag to control photo capture
capture_photo = False

# Time of the last capture
last_capture_time = 0

# Function to release the camera gracefully
def release_camera(signal, frame):
    global cap
    print("Releasing the camera...")
    if cap.isOpened():
        cap.release()
    sys.exit(0)

# Register a signal handler to release the camera on script termination
signal.signal(signal.SIGINT, release_camera)

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with code", rc)
    client.subscribe(mqtt_topic)

def on_message(client, userdata, msg):
    global capture_photo, last_capture_time
    message = msg.payload.decode("utf-8")
    
    if message == "start_cutting":
        capture_photo = True
    else:
        capture_photo = False

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_broker, 1883, 60)

while True:
    client.loop()
    
    if capture_photo:
        current_time = time.time()
        # Capture a single frame every 2 minutes
        if current_time - last_capture_time >= 120:
            ret, frame = cap.read()

            if ret:
                # Save the captured frame as an image file (e.g., photo.jpg) locally
                local_file_name = "local_photo.jpg"
                cv2.imwrite(local_file_name, frame)
                print("Local photo captured and saved as 'local_photo.jpg'")

                # Upload the photo to the S3 bucket
                s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
                s3.upload_file(local_file_name, bucket_name, s3_key)
                print("Photo uploaded to S3")

                # Update the last capture time
                last_capture_time = current_time

            else:
                print("Error: Could not capture a frame")

    # Check for keyboard input ('q' key to quit)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam
cap.release()
cv2.destroyAllWindows()
