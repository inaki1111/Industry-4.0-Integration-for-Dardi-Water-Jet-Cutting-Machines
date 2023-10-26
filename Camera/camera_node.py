import cv2
import boto3
import paho.mqtt.client as mqtt
import time
import json

# Load AWS credentials from the config file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

aws_access_key_id = config['access_key']
aws_secret_access_key = config['secret_access_key']

# AWS S3 bucket information
bucket_name = 'mybucketcima'
s3_key = 'photo.jpg'  # Replace 'photo.jpg' with the desired file name

# MQTT broker information
mqtt_broker = "localhost"  # Replace with your MQTT broker address
mqtt_topic = "machine_state"


# Specify the desired resolution here
width = 640  # Width of the resolution
height = 480  # Height of the resolution



# Initialize the webcam (0 represents the default camera, but you can change it)
cap = cv2.VideoCapture(0)

# Set the resolution
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

# Flag to control photo capture
capture_photo = False

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with code", rc)
    client.subscribe(mqtt_topic)

def on_message(client, userdata, msg):
    global capture_photo
    message = msg.payload.decode("utf-8")
    
    if message == "send_data":
        capture_photo = True
    elif message == "stop_send_data":
        capture_photo = False

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(username=mqtt_username, password=mqtt_password)

client.connect(mqtt_broker, 1883, 60)

while True:
    client.loop()
    
    if capture_photo:
        # Capture a single frame
        ret, frame = cap.read()

        if ret:
            # Save the captured frame as an image file (e.g., photo.jpg)
            cv2.imwrite("photo.jpg", frame)
            print("Photo captured and saved as 'photo.jpg'")

            # Upload the photo to the S3 bucket
            s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
            s3.upload_file("photo.jpg", bucket_name, s3_key)
            print("Photo uploaded to S3")

            # Sleep for 60 seconds before capturing another photo
            time.sleep(60)

        else:
            print("Error: Could not capture a frame")

# Release the webcam
cap.release()
