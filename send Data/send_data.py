import boto3
import schedule
import time

# AWS credentials and S3 bucket information
aws_access_key = 'YOUR_AWS_ACCESS_KEY'
aws_secret_key = 'YOUR_AWS_SECRET_KEY'
bucket_name = 'your-s3-bucket-name'
csv_file_path = 'path-to-your-csv-file.csv'
s3_key = 'destination-file-name.csv'  # The file name in the S3 bucket

# Function to upload the CSV file to S3
def upload_csv_to_s3():
    try:
        # Create an S3 client
        s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)

        # Upload the CSV file to the S3 bucket
        s3.upload_file(csv_file_path, bucket_name, s3_key)

        print(f"Uploaded {csv_file_path} to {bucket_name}/{s3_key} successfully.")

    except Exception as e:
        print(f"Error uploading to S3: {str(e)}")

# Schedule the upload job to run once a day at a specific time (adjust as needed)
schedule.every().day.at("12:00").do(upload_csv_to_s3)

while True:
    schedule.run_pending()
    time.sleep(1)
