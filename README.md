# FastAPI Financial Document Management & Semantic Search

This project is a high-performance **FastAPI** backend designed to securely store, manage, and semantically analyze financial documents (invoices, reports, contracts). It incorporates an AI-powered Retrieval-Augmented Generation (RAG) pipeline allowing users to query documents using natural language and instantly retrieve exact relevant passages.

## 🚀 Features

*   **Authentication & Role-Based Access (RBAC)**: Secured via JWT tokens with granular roles (`Admin`, `Financial Analyst`, `Auditor`, `Client`).
*   **Relational Document Management**: Secure Uploads and relational tracking of document metadata (`Company Name`, `Document Type`, `Uploaded By`, etc.).
*   **AI-Powered RAG Pipeline**: Langchain orchestrated PDF ingestion and chunking. 
*   **Vector Database Context**: Deep context retrieval powered by local **ChromaDB**.
*   **Semantic Reranking**: Integrates HuggingFace Sentence Transformers (`all-MiniLM-L6-v2`) and cross-encoder reranking (`ms-marco`) to intelligently identify the top 5 most relevant paragraph chunks for any financial query.

## 🛠️ Tech Stack

*   **API Framework**: FastAPI
*   **Database**: SQLite (Relational), ChromaDB (Vector)
*   **AI Models**: HuggingFace (`all-MiniLM-L6-v2`), Sentence-Transformers
*   **Semantic Tooling**: LangChain, PyPDF

---

## ⚙️ Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/VDongarkar/Finance-project.git
cd Finance-project
```

### 2. Set up the Virtual Environment
Create and activate a Python virtual environment:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
*(On Linux/Mac use `source venv/bin/activate`)*

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize Database & Default Roles
Run the seeder script. This strictly builds your SQL tables and initializes the Default Roles and the root Admin user (`admin` / `admin123`).
```bash
python seed.py
```

### 5. Run the Application
```bash
uvicorn main:app --reload
```
The server will boot up locally at `http://127.0.0.1:8000`.

---

## 📚 API Overview and Swagger UI

FastAPI automatically generates an interactive API documentation interface.
Once the server is running, navigate directly to:
**[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

### Standard Workflow:
1.  **Authorize**: Click the "Authorize" button on the top right. Login with the seeded admin credentials:
    *   **Username**: `admin`
    *   **Password**: `admin123`
2.  **Upload Document**: Post a PDF file to `/documents/upload` with its metadata.
3.  **Index Document**: Retrieve your generated Document ID, and pass it to `/rag/index-document`. This chunks and vectorizes your PDF.
4.  **Semantic Search**: Query `/rag/search` with natural language to hit your ChromaDB implementation and return highly relevant financial data cross-referenced with your query.
