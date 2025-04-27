# config.py
import os
import sys

# Base Directory Setup
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(BASE_DIR)

SQLSERVER_CONFIG = {
    "server": "your-sqlserver.database.windows.net",  # your Azure SQL Server name
    "database": "your_database_name",                 # target database name
    "username": "your_sqlserver_username",            # your SQL Server login
    "password": "your_sqlserver_password",            # your SQL Server password
    "driver": "ODBC Driver 17 for SQL Server"          # ODBC driver installed
}

# ✅ Azure Blob Storage Configuration
AZURE_BLOB_CONFIG = {
    "connection_string": "your_azure_blob_storage_connection_string",  # full connection string
    "container_name": "your_container_name"                            # container name inside blob
}