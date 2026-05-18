"""
Read CSV data from Azure Blob Storage into pandas.

This is the Azure version of local file reading.
"""

import pandas as pd
from io import StringIO
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient


ACCOUNT_NAME = "YOUR_STORAGE_ACCOUNT_NAME"
CONTAINER_NAME = "or-input-data"


def read_csv_from_blob(blob_name: str):
    account_url = f"https://{ACCOUNT_NAME}.blob.core.windows.net"
    credential = DefaultAzureCredential()
    blob_service_client = BlobServiceClient(account_url=account_url, credential=credential)
    blob_client = blob_service_client.get_blob_client(
        container=CONTAINER_NAME,
        blob=blob_name
    )
    downloaded = blob_client.download_blob().readall()
    return pd.read_csv(StringIO(downloaded.decode("utf-8")))


if __name__ == "__main__":
    plants = read_csv_from_blob("plants.csv")
    warehouses = read_csv_from_blob("warehouses.csv")
    transport_cost = read_csv_from_blob("transport_cost.csv")

    print(plants.head())
    print(warehouses.head())
    print(transport_cost.head())
