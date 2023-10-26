from flask import Flask, render_template, Response
import cv2
import socket
import threading
import time
import paho.mqtt.client as mqtt

app = Flask(__name__)

# MQTT configuration
BROKER = 'localhost'
PORT = 1883
TOPIC = 'test/topic'
CLIENT_ID = 'FlaskMQTTClient'

# Global buffer to store the latest frame
frames_buffer = None
camera = cv2.VideoCapture(0)

# MQTT callback when a message is received
def on_message(client, userdata, message):
    print(f"Received message '{message.payload.decode()}' on topic '{message.topic}'")

# Create and setup the MQTT client
client = mqtt.Client(CLIENT_ID)
client.on_message = on_message
client.connect(BROKER, PORT)
client.subscribe(TOPIC)
client.loop_start()

def capture_frames():
    """Capture frames from the camera and update the global frames_buffer."""
    global frames_buffer
    while True:
        success, frame = camera.read()
        if not success:
            print("Failed to grab frame.")
            break
        ret, buffer = cv2.imencode('.jpg', frame)
        frames_buffer = buffer.tobytes()
        time.sleep(0.03)  # Delay for around 30 FPS

def generate_frames():
    """Generate frames for the client from the global frames_buffer."""
    global frames_buffer
    while True:
        if frames_buffer:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frames_buffer + b'\r\n')
        time.sleep(0.03)  # Match the capture delay for consistency

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    # Start capturing frames in a separate thread
    threading.Thread(target=capture_frames, daemon=True).start()

    # Get the host IP address
    hostname = socket.gethostname()    
    IPAddr = socket.gethostbyname(hostname)
    port = 5000  # default port for Flask in debug mode
    
    print(f"Running on http://{IPAddr}:{port}/")
    app.run(debug=True, host='0.0.0.0')  # Host 0.0.0.0 allows it to be externally visible

# Remember to release the camera resource when you're done
camera.release()
