# -*- coding: utf-8 -*-
"""
Created on Sun Apr 27 10:07:17 2025

@author: HP
"""

# sql_pipeline.py
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from core.data_loader import create_mysql_engine, create_sqlserver_engine
import pandas as pd
from core.system_prompt import SYSTEM_PROMPT

# Load model and tokenizer once globally
tokenizer = AutoTokenizer.from_pretrained("defog/sqlcoder-7b-2")
model = AutoModelForCausalLM.from_pretrained(
    "defog/sqlcoder-7b-2",
    device_map="auto",
    torch_dtype=torch.float16
)

# ✅ Generate Prompt for LLM
def generate_prompt(nl_query, tables_schema_dict):
    schema_lines = [f"# Table: {tbl}({', '.join(cols)})" for tbl, cols in tables_schema_dict.items()]
    schema_info = "\n".join(schema_lines)

    return f"""{SYSTEM_PROMPT}

### Database Schema:
{schema_info}

### User Question:
{nl_query.strip()}

### SQL Query:
SELECT""".strip()

# ✅ Run Prompt through Model and Execute SQL
def run_nl_to_sql_pipeline(prompt, db, db_type="mysql"):
    # Choose engine based on db_type
    engine = create_mysql_engine(db) if db_type == "mysql" else create_sqlserver_engine(db)

    # Tokenize and generate SQL using the model
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024).to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=256, do_sample=False)
    sql = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Clean up: Ensure SQL starts with SELECT
    if "SELECT" in sql.upper():
        sql = "SELECT" + sql.split("SELECT", 1)[-1]

    try:
        if db_type == "mysql":
            result_df = pd.read_sql(sql, engine)
        else:  # SQL Server may require minor cleaning (optional)
            result_df = pd.read_sql(sql, engine)
    except Exception as e:
        result_df = f"SQL Execution Error: {e}"

    return sql.strip(), result_df
