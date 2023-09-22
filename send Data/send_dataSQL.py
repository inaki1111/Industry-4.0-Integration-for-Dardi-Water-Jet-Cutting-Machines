from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import pandas as pd
import json
import io
import boto3
import os

# Get API Keys
content = open('config.json')
config = json.load(content)
access_key = config['access_key']
secret_access_key = config['secret_access_key']

# SQL Server details
dr = "SQL Server Native Client 11.0"
srvr = "localhost"
db = "prueba1"
uid = "your_sql_server_username"  # Replace with your SQL Server username
pwd = "your_sql_server_password"  # Replace with your SQL Server password

# Extract data from SQL Server
def extract():
    try:
        engine = create_engine(f"mssql+pyodbc://{uid}:{pwd}@{srvr}:1433/{db}?driver={dr}")
        Session = scoped_session(sessionmaker(bind=engine))
        s = Session()
        
        # List of tables to extract data from
        tables_to_extract = ['Fecha', 'Hora']
        
        for tbl in tables_to_extract:
            # Query and load data to a DataFrame
            df = pd.read_sql_query(f'SELECT * FROM {tbl}', engine)
            load(df, tbl)
    except Exception as e:
        print("Data extract error: " + str(e))

# Load data to Amazon S3
def load(df, tbl):
    try:
        rows_imported = 0
        print(f'Importing rows {rows_imported} to {rows_imported + len(df)} for table {tbl}')
        
        # Upload to S3
        upload_file_bucket = 'mybucketcima'
        upload_file_key = f'public/{tbl}/{tbl}.csv'
        filepath = upload_file_key
        
        s3_client = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_access_key, region_name='us-east-1')
        
        with io.StringIO() as csv_buffer:
            df.to_csv(csv_buffer, index=False)
            response = s3_client.put_object(
                Bucket=upload_file_bucket,
                Key=filepath,
                Body=csv_buffer.getvalue()
            )
            status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
            
            if status == 200:
                print(f"Successful S3 put_object response. Status - {status}")
            else:
                print(f"Unsuccessful S3 put_object response. Status - {status}")
            
            rows_imported += len(df)
            print("Data imported successfully")
    except Exception as e:
        print("Data load error: " + str(e))

try:
    # Call the extract function
    extract()
except Exception as e:
    print("Error while extracting data: " + str(e))
