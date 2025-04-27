# NLP-to-SQL Dashboard (Azure + MySQL + SQL Server Ready)

This project allows you to:
- Upload CSV/XLSX files to Azure Blob and Database (MySQL/SQL Server)
- Run Natural Language queries and automatically generate SQL
- Display query results dynamically on a beautiful dashboard

---

## 🌐 Tech Stack

- Flask (Web App)
- SQLAlchemy (Database ORM)
- Azure Blob Storage (File Uploads)
- MySQL / Azure SQL Server (Database Backends)
- HuggingFace Transformers (`defog/sqlcoder-7b-2` for SQL Generation)
- Torch (for model loading)
- Pandas (for data manipulation)

---

## 📦 Setup Instructions

### 1. Install Python Libraries

```bash
pip install -r requirements.txt
