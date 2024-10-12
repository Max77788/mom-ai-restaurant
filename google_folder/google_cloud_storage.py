from google.cloud import storage
from dotenv import load_dotenv, find_dotenv
from urllib.parse import urlparse, unquote
from google.cloud import vision
import requests
from io import BytesIO
import os

load_dotenv(find_dotenv())

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google_folder/credentials.json"

from typing import List

def set_bucket_public_iam(
    bucket_name: str = "your-bucket-name",
    members: List[str] = ["allUsers"],
):
    """Set a public IAM Policy to bucket"""
    # bucket_name = "your-bucket-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    policy = bucket.get_iam_policy(requested_policy_version=3)
    policy.bindings.append(
        {"role": "roles/storage.objectViewer", "members": members}
    )

    bucket.set_iam_policy(policy)

    print(f"Bucket {bucket.name} is now publicly readable")

# set_bucket_public_iam("mom-ai-restaurant-pictures", ["allUsers"])

# Initialize a client for Google Cloud Storage
def initialize_storage_client():
    return storage.Client()

# Upload a file to a bucket
def upload_file_google(source_file_name, object_name="", folder_name="", bucket_name="mom-ai-restaurant-pictures"):
    client = initialize_storage_client()
    bucket = client.bucket(bucket_name)
    
    if not object_name:
        object_name = source_file_name
    destination_blob_name = f"{folder_name}/{object_name}"
    blob = bucket.blob(destination_blob_name)


    
    blob.upload_from_filename(source_file_name)
    print(f"File {source_file_name} uploaded to {destination_blob_name}.")

    # Make the file publicly accessible
    # blob.make_public()
    
    # Return the public URL of the file
    return blob.public_url


def upload_file_bytes_google(file_data, object_name, folder_name="", bucket_name="mom-ai-restaurant-pictures", content_type=None):
    """
    Upload a file to Google Cloud Storage from a byte array.

    Args:
    file_data (bytes): The file content as a byte array.
    object_name (str): The name of the object to create in the bucket.
    folder_name (str, optional): The folder within the bucket to place the file. Defaults to "".
    bucket_name (str, optional): The name of the bucket. Defaults to "mom-ai-restaurant-pictures".
    content_type (str, optional): The content type of the file. If None, it will be guessed.

    Returns:
    str: The public URL of the uploaded file.
    """
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    
    destination_blob_name = f"{folder_name}/{object_name}".strip('/')
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_file(file_data, content_type=content_type)
    print(f"File {object_name} uploaded to {destination_blob_name}.")
    
    # Make the file publicly accessible if needed
    # blob.make_public()
    
    return blob.public_url


def delete_file_by_url_google(file_url):
    # Parse the URL to extract the bucket name and blob name
    parsed_url = urlparse(file_url)
    path_parts = parsed_url.path.split('/')
    
    # The bucket name is the first part of the path, and the blob name is the rest
    bucket_name = path_parts[1]
    
    # URL-decode the blob name to handle special characters correctly
    blob_name = unquote('/'.join(path_parts[2:]))
    
    # Initialize the storage client and access the blob
    client = storage.Client()  # Assuming client initialization like this
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    # Delete the blob (file)
    blob.delete()
    print(f"File {blob_name} deleted from bucket {bucket_name}.")



# Download a file from a bucket
def download_file_google(source_blob_name, destination_file_name, bucket_name="mom-ai-restaurant-pictures"):
    client = initialize_storage_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    
    blob.download_to_filename(destination_file_name)
    print(f"Blob {source_blob_name} downloaded to {destination_file_name}.")

# List all files in a bucket
def list_files_google(bucket_name):
    client = initialize_storage_client()
    bucket = client.bucket(bucket_name="mom-ai-restaurant-pictures")
    
    blobs = bucket.list_blobs()
    
    for blob in blobs:
        print(blob.name)


def extract_text_from_image_google(image_path):
    # Initialize Google Vision API client
    client = vision.ImageAnnotatorClient()

    try:
        # Download the image from the provided URL
        response = requests.get(image_path)

        # Check if the request was successful
        if response.status_code != 200:
            raise Exception(f"Failed to download image from {image_path}, status code: {response.status_code}")

        # Read the image in binary mode (in memory)
        image_bytes = BytesIO(response.content).getvalue()

        # Prepare the image for Google Vision
        image = vision.Image(content=image_bytes)

        # Call Google Vision API to detect text in the image
        response = client.text_detection(image=image)
        annotations = response.text_annotations

        # Extract and return detected text
        if not annotations:
            return "No text detected in the image."

        # print(f"Annotations: {annotations}")
        
        # The first annotation usually contains the entire text
        extracted_text = annotations[0].description
        # print(f"Extracted Text: {extracted_text}")
        return extracted_text

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

# Usage example
bucket_name = 'mom-ai-restaurant-pictures'
source_file_name = 'downloaded_video.mp4'
destination_blob_name = 'restaurant_intros/downloaded_video.mp4'
destination_file_name = 'downloaded_video.mp4'

# Upload a file
# link = upload_file(bucket_name, source_file_name, destination_blob_name)
# print(link)

# List all files
# list_files(bucket_name)

# Download the file
# download_file(bucket_name, destination_blob_name, destination_file_name)
