import cv2
import boto3
import pandas as pd
from io import StringIO
import json

# Load AWS credentials from the config file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

aws_access_key_id = config['access_key']
aws_secret_access_key = config['secret_access_key']

# AWS S3 bucket information
bucket_name = 'mybucketcima'
s3_key = 'photo.jpg'  # Replace 'photo.jpg' with the desired file name

# Initialize the webcam (0 represents the default camera, but you can change it)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open the webcam")
else:
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

    else:
        print("Error: Could not capture a frame")

    # Release the webcam
    cap.release()

# Close any open OpenCV windows (if any)
cv2.destroyAllWindows()
