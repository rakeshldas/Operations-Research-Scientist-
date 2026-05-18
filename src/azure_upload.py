"""
Azure Blob Storage Upload Script

Before running:
1. Create Azure Storage Account
2. Create two containers:
   - or-input-data
   - or-output-results
3. Install packages:
   pip install azure-storage-blob azure-identity
4. Login:
   az login
"""

from pathlib import Path
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient


ACCOUNT_NAME = "YOUR_STORAGE_ACCOUNT_NAME"
INPUT_CONTAINER = "or-input-data"
OUTPUT_CONTAINER = "or-output-results"


def upload_folder_to_blob(local_folder: str, container_name: str):
    account_url = f"https://{ACCOUNT_NAME}.blob.core.windows.net"
    credential = DefaultAzureCredential()
    blob_service_client = BlobServiceClient(account_url=account_url, credential=credential)
    container_client = blob_service_client.get_container_client(container_name)

    local_path = Path(local_folder)
    for file_path in local_path.glob("*.csv"):
        blob_name = file_path.name
        with open(file_path, "rb") as data:
            container_client.upload_blob(name=blob_name, data=data, overwrite=True)
        print(f"Uploaded {file_path} to container {container_name}/{blob_name}")


if __name__ == "__main__":
    upload_folder_to_blob("data", INPUT_CONTAINER)
    upload_folder_to_blob("outputs", OUTPUT_CONTAINER)
