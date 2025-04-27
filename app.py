# -*- coding: utf-8 -*-
"""
Created on Fri Apr 25 20:07:48 2025

@author: HP
"""

# app.py
from flask import Flask, render_template, request, jsonify, redirect, url_for
from core.database_utils import get_all_databases, get_all_tables, get_columns_for_table, get_recent_records
from core.sql_pipeline import generate_prompt, run_nl_to_sql_pipeline
from core.data_loader import upload_and_insert_table, upload_and_insert_multiple_files, create_mysql_engine, create_sqlserver_engine, upload_to_blob
import pandas as pd
import os, sys

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(BASE_DIR)

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Define your preferred DB type (can be dynamic later)
DB_TYPE = "sqlserver"  # or "mysql"

@app.route("/", methods=["GET"])
def index():
    databases = get_all_databases(db_type=DB_TYPE)
    return render_template("index.html", databases=databases)

@app.route("/upload_files", methods=["POST"])
def upload_files():
    selected_db = request.form.get("database")
    uploaded_files = request.files.getlist("file")
    filepaths = []

    for file in uploaded_files:
        if file.filename:
            filename = file.filename
            ext = filename.split(".")[-1].lower()
            if ext in ["csv", "xlsx"]:
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                filepaths.append(filepath)

                # ✅ Upload to Azure Blob
                upload_to_blob(filepath, filename)

    if filepaths and selected_db:
        upload_and_insert_multiple_files(filepaths, selected_db, db_type=DB_TYPE)

    return ("", 204)

@app.route("/get_tables", methods=["GET"])
def get_tables():
    db = request.args.get("db")
    if db:
        tables = get_all_tables(db, db_type=DB_TYPE)
        return jsonify(tables)
    return jsonify([])

@app.route("/get_columns", methods=["GET"])
def get_columns():
    db = request.args.get("db")
    table = request.args.get("table")
    if db and table:
        columns = get_columns_for_table(db, table, db_type=DB_TYPE)
        return jsonify(columns)
    return jsonify([])

@app.route("/get_recent_records", methods=["GET"])
def get_recent_records_route():
    db = request.args.get("db")
    table = request.args.get("table")
    if db and table:
        try:
            records = get_recent_records(db, table, db_type=DB_TYPE)
            return jsonify(records)
        except Exception as e:
            return jsonify({"error": str(e)})
    return jsonify([])

@app.route("/run_query", methods=["POST"])
def run_query():
    db = request.form.get("database")
    nl_query = request.form.get("query")

    if db and nl_query:
        try:
            tables = get_all_tables(db, db_type=DB_TYPE)
            engine = create_mysql_engine(db) if DB_TYPE == "mysql" else create_sqlserver_engine(db)

            tables_schema = {}
            for table in tables:
                if DB_TYPE == "mysql":
                    df = pd.read_sql(f"SELECT * FROM `{table}` LIMIT 1", engine)
                else:
                    df = pd.read_sql(f"SELECT TOP 1 * FROM [{table}]", engine)

                tables_schema[table] = list(df.columns)

            prompt = generate_prompt(nl_query, tables_schema)
            sql, result_df = run_nl_to_sql_pipeline(prompt, db, db_type=DB_TYPE)

            result = result_df.to_string(index=False) if not isinstance(result_df, str) else result_df
            return jsonify({"sql": sql, "result": result})

        except Exception as e:
            return jsonify({"sql": "", "result": f"❌ Error: {str(e)}"})

    return jsonify({"sql": "", "result": "❌ No query or database selected."})

@app.route("/reset", methods=["GET"])
def reset():
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
