import boto3
import requests
from botocore.exceptions import NoCredentialsError
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.environ.get("AWS_SECRET_KEY")

# Initialize the S3 client
s3 = boto3.client('s3',
                  aws_access_key_id=AWS_ACCESS_KEY,
                    aws_secret_access_key=AWS_SECRET_KEY,
                    region_name='eu-north-1'  # e.g., 'us-west-2'
                  )

def download_file_from_url(url, local_filename):
    """
    Downloads a file from the provided URL and saves it locally.

    :param url: URL to the file
    :param local_filename: Local file path where the file will be saved
    """
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(local_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"File downloaded successfully from {url}")
    else:
        print(f"Failed to download file: Status code {response.status_code}")

def upload_to_s3(file_name, bucket, object_name=None):
    """
    Uploads a file to an S3 bucket.

    :param file_name: Local file to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified, file_name is used
    :return: True if file was uploaded, else False
    """
    if object_name is None:
        object_name = file_name

    try:
        s3.upload_file(file_name, bucket, "restaurant_intros/"+object_name)
        print(f"File '{file_name}' uploaded to '{bucket}/{object_name}'")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False

# Example usage:
url = r"https://d-id-talks-prod.s3.us-west-2.amazonaws.com/google-oauth2%7C109894292927535905362/tlk_B2bFghmjirJgz4zPXJOzD/1726677571628.mp4?AWSAccessKeyId=AKIA5CUMPJBIK65W6FGA&Expires=1726763975&Signature=8litGJqlEw%2FeZeQrs4l%2B9NxSFwM%3D"
local_filename = "downloaded_video.mp4"  # The name of the file to save locally
bucket_name = "mom-ai-restaurant-images"  # Your S3 bucket name

# Step 1: Download the file from the URL
download_file_from_url(url, local_filename)

# Step 2: Upload the downloaded file to the S3 bucket
upload_to_s3(local_filename, bucket_name)
