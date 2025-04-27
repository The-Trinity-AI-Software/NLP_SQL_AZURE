# database_utils.py
import pymysql
from core.data_loader import create_mysql_engine, create_sqlserver_engine
from config import MYSQL_CONFIG, SQLSERVER_CONFIG
from sqlalchemy import text
import os, sys

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(BASE_DIR)

# ✅ Get all MySQL Databases
def get_all_mysql_databases():
    cfg = MYSQL_CONFIG
    conn = pymysql.connect(
        host=cfg["host"],
        user=cfg["user"],
        password=cfg["password"],
        port=cfg["port"]
    )
    cursor = conn.cursor()
    cursor.execute("SHOW DATABASES")
    dbs = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return dbs

# ✅ Get all SQL Server Databases
def get_all_sqlserver_databases():
    engine = create_sqlserver_engine("master")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT name FROM sys.databases WHERE database_id > 4"))
        dbs = [row[0] for row in result.fetchall()]
    return dbs

# ✅ General Get Databases Function
def get_all_databases(db_type="mysql"):
    if db_type == "mysql":
        return get_all_mysql_databases()
    else:
        return get_all_sqlserver_databases()

# ✅ Get Tables for a Database
def get_all_tables(database, db_type="mysql"):
    engine = create_mysql_engine(database) if db_type == "mysql" else create_sqlserver_engine(database)

    with engine.connect() as conn:
        if db_type == "mysql":
            query = f"""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = '{database}' AND table_type = 'BASE TABLE';
            """
        else:  # SQL Server
            query = f"""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_catalog = '{database}' AND table_type = 'BASE TABLE';
            """
        result = conn.execute(text(query))
        return [row[0] for row in result]

# ✅ Get Columns for a Table
def get_columns_for_table(database, table, db_type="mysql"):
    engine = create_mysql_engine(database) if db_type == "mysql" else create_sqlserver_engine(database)

    with engine.connect() as conn:
        if db_type == "mysql":
            result = conn.execute(text(f"SHOW COLUMNS FROM `{table}`;"))
            return [row[0] for row in result]
        else:  # SQL Server
            query = f"""
                SELECT COLUMN_NAME
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = '{table}';
            """
            result = conn.execute(text(query))
            return [row[0] for row in result]

# ✅ Get Recent Records from a Table
def get_recent_records(database, table, db_type="mysql", limit=10):
    engine = create_mysql_engine(database) if db_type == "mysql" else create_sqlserver_engine(database)

    with engine.connect() as conn:
        if db_type == "mysql":
            query = f"SELECT * FROM `{table}` ORDER BY 1 DESC LIMIT {limit}"
        else:  # SQL Server
            query = f"SELECT TOP {limit} * FROM [{table}] ORDER BY 1 DESC"
        result = conn.execute(text(query))
        columns = result.keys()
        rows = [dict(zip(columns, row)) for row in result.fetchall()]
    return rows
