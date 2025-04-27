# data_loader.py
import pandas as pd
from sqlalchemy import create_engine, inspect, text
from config import MYSQL_CONFIG, SQLSERVER_CONFIG, AZURE_BLOB_CONFIG
from azure.storage.blob import BlobServiceClient
import os, sys

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(BASE_DIR)

# ✅ Create Engine for MySQL
def create_mysql_engine(database):
    conn_str = f"mysql+pymysql://{MYSQL_CONFIG['user']}:{MYSQL_CONFIG['password']}@{MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}/{database}"
    return create_engine(conn_str)

# ✅ Create Engine for SQL Server
def create_sqlserver_engine(database):
    conn_str = (
        f"mssql+pyodbc://{SQLSERVER_CONFIG['username']}:{SQLSERVER_CONFIG['password']}"
        f"@{SQLSERVER_CONFIG['server']}/{database}"
        f"?driver={SQLSERVER_CONFIG['driver'].replace(' ', '+')}"
    )
    return create_engine(conn_str)

# ✅ Upload File to Azure Blob Storage
def upload_to_blob(file_path, blob_name):
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_BLOB_CONFIG["connection_string"])
    blob_client = blob_service_client.get_blob_client(container=AZURE_BLOB_CONFIG["container_name"], blob=blob_name)
    with open(file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
    print(f"[✓] Uploaded {blob_name} to Azure Blob Storage.")

# ✅ Check if Table Exists
def table_exists(engine, table_name):
    inspector = inspect(engine)
    return inspector.has_table(table_name)

# ✅ Upload and Insert Table
def upload_and_insert_table(filepath, database, table_name, db_type="mysql"):
    ext = filepath.split('.')[-1].lower()
    df = pd.read_csv(filepath) if ext == "csv" else pd.read_excel(filepath)

    # Choose engine
    engine = create_mysql_engine(database) if db_type == "mysql" else create_sqlserver_engine(database)

    with engine.begin() as conn:
        if table_name in ["products", "sales_pipeline", "data_dictionary"]:
            if table_name == "products":
                df = df[["product", "series", "sales_price"]]
            if table_name == "sales_pipeline":
                df = df[["opportunity_id", "sales_agent", "product", "account", "deal_stage", "engage_date", "close_date", "close_value"]]
            if table_name == "data_dictionary":
                df = df[["Table", "Field", "Description"]]
            conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
            df.to_sql(table_name, engine, index=False)
            print(f"[✓] Recreated table: {table_name} with {len(df)} records")
            return

        if not table_exists(engine, table_name):
            df.to_sql(table_name, engine, index=False)
            print(f"[✓] Created new table: {table_name} with {len(df)} records")
            return

        try:
            existing = pd.read_sql(f"SELECT {df.columns[0]} FROM {table_name}", conn)
            existing_keys = set(existing[df.columns[0]].astype(str).tolist())
            new_df = df[~df[df.columns[0]].astype(str).isin(existing_keys)]
        except Exception as e:
            print(f"[!] Could not fetch existing keys: {e}")
            new_df = df

        if not new_df.empty:
            new_df.to_sql(table_name, engine, index=False, if_exists="append")
            print(f"[+] Inserted {len(new_df)} new records into table: {table_name}")
        else:
            print(f"[-] No new records to insert for table: {table_name}")

# ✅ Upload and Insert Multiple Files
def upload_and_insert_multiple_files(filepaths, database, db_type="mysql"):
    for path in filepaths:
        table_name = os.path.splitext(os.path.basename(path))[0]
        upload_and_insert_table(path, database, table_name, db_type=db_type)

# ✅ Get Limited Content from a Table
def get_table_content(database, table_name, limit=10, db_type="mysql"):
    engine = create_mysql_engine(database) if db_type == "mysql" else create_sqlserver_engine(database)
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT * FROM {table_name} LIMIT {limit}" if db_type=="mysql" else f"SELECT TOP {limit} * FROM {table_name}"))
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return df
