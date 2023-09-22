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
s3_key = 'data.csv'  # Remove 's3://mybucketcima/' from the key

# Load the last checkpoint row from a separate file
try:
    with open('checkpoint.txt', 'r') as checkpoint_file:
        last_checkpoint_row = int(checkpoint_file.read())
except FileNotFoundError:
    last_checkpoint_row = 0

# Load the CSV file from S3 into memory
s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
s3_object = s3.get_object(Bucket=bucket_name, Key=s3_key)
s3_data = s3_object['Body'].read().decode('utf-8')

# Create a DataFrame from the S3 data
df_s3 = pd.read_csv(StringIO(s3_data))

# Load the local CSV file into a DataFrame (assuming it's named 'local_file.csv')
df_local = pd.read_csv('/home/inaki/Documents/Industria 4.0/Sistema-de-industria-4.0-/Forms/data.csv')

# Identify missing rows based on a unique identifier or criteria
# For example, you can use the merge function to identify rows that exist in df_local but not in df_s3
missing_rows = df_local.loc[last_checkpoint_row:].merge(df_s3, on='Fecha', how='left', indicator=True).query('_merge == "left_only"').drop(columns=['_merge'])

# Append the missing rows to the in-memory DataFrame
combined_df = pd.concat([df_s3, missing_rows], ignore_index=True)

# Convert the combined DataFrame back to CSV format
combined_csv = combined_df.to_csv(index=False)

# Upload the updated CSV data back to S3
s3.put_object(Bucket=bucket_name, Key=s3_key, Body=combined_csv)

# Update the checkpoint file with the index of the last appended row
with open('checkpoint.txt', 'w') as checkpoint_file:
    checkpoint_file.write(str(len(df_local)))

# Print a message indicating the update
print(f"Appended {len(missing_rows)} rows to the S3 file.")
