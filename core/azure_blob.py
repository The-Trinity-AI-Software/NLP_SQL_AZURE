from azure.storage.blob import BlobServiceClient
from config import AZURE_BLOB_CONFIG
import os

def upload_to_blob(file_path, blob_name):
    blob_service = BlobServiceClient.from_connection_string(AZURE_BLOB_CONFIG['connection_string'])
    blob_client = blob_service.get_blob_client(container=AZURE_BLOB_CONFIG['container_name'], blob=blob_name)
    with open(file_path, 'rb') as f:
        blob_client.upload_blob(f, overwrite=True)