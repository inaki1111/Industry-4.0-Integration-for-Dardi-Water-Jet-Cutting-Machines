from flask import Flask, render_template, Response
import cv2
import socket
import threading
import time
import paho.mqtt.client as mqtt
import os
import logging
import boto3
import json



# Load AWS credentials from config.json
with open('/home/cimatec/Documentos/Sistema-de-industria-4.0-/live stream/config.json') as config_file:
    config = json.load(config_file)
    aws_access_key_id = config.get('access_key')
    aws_secret_access_key = config.get('secret_access_key')


s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

BUCKET_NAME = 'mybucketcima'
# Setup logging
LOG_DIR = "Logs"
LOG_FILE = os.path.join(LOG_DIR, "logs.txt")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s]: %(message)s",
                    handlers=[
                        logging.FileHandler(LOG_FILE, mode='a'),
                        logging.StreamHandler()
                    ])

app = Flask(__name__, static_url_path='/images', static_folder='images')

frames_buffer = None
camera = None
active_feed = False  # Flag to determine if the feed is active

MQTT_BROKER = 'localhost'
MQTT_PORT = 1883  # Default port
MQTT_TOPIC = 'start_process'
CLIENT_ID = 'FlaskMQTTClient'
SAVE_PATH = 'images'

if not os.path.exists(SAVE_PATH):
    os.mkdir(SAVE_PATH)

def on_connect(client, userdata, flags, rc):
    logging.info("Connected to MQTT broker with result code "+str(rc))
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    global active_feed
    logging.info(f"Received MQTT message: {msg.payload.decode()}")
    if msg.payload.decode() == 'send_data':
        active_feed = True
    elif msg.payload.decode() == 'stop_send_data':
        active_feed = False

mqtt_client = mqtt.Client(CLIENT_ID)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()

def capture_frames():
    global frames_buffer, camera
    camera = cv2.VideoCapture(0)

    # Set resolution
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    last_saved_time = time.time()
    filename = os.path.join(SAVE_PATH, "captured_image.jpg")  # Consistent image name
    while True:
        success, frame = camera.read()
        if not success:
            logging.warning("Failed to grab frame.")
            continue

        ret, buffer = cv2.imencode('.jpg', frame)
        frames_buffer = buffer.tobytes()

        if active_feed:
            elapsed_time = time.time() - last_saved_time
            if elapsed_time >= 120:  # Save every 2 minutes
                cv2.imwrite(filename, frame)
                logging.info(f"Image saved locally at: {filename}")  # Print the local save location

                # Upload to S3
                with open(filename, "rb") as f:
                    s3.upload_fileobj(f, BUCKET_NAME, "Industria 40/live_feed/captured_image.jpg")
                logging.info(f"Image uploaded to S3: {BUCKET_NAME}/Industria40/captured_image.jpg")

                last_saved_time = time.time()

def generate_frames():
    global frames_buffer
    while True:
        if frames_buffer:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frames_buffer + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    threading.Thread(target=capture_frames, daemon=True).start()

    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)
    port = 5000
    logging.info(f"Running on http://{IPAddr}:{port}/")
    app.run(debug=True, host='0.0.0.0', use_reloader=False)

    if camera:
        camera.release()
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
