# ContextEngine 
##### ContextEngine is a production-grade Retrieval-Augmented Generation (RAG) implementation designed for reliable, scalable AI workflows. While most RAG implementations are simple scripts, ContextEngine is built with durable execution, rate limiting, and throttling to handle real-world document processing at scale.

&nbsp;
Home Screen
<img width="1600" height="777" alt="Home Screen" src="https://github.com/user-attachments/assets/2fe2b002-f9d9-4f38-9c78-07046b5c2b4a" />

Ingest and Ask
<img width="1600" height="779" alt="Ingest and Ask" src="https://github.com/user-attachments/assets/595c7187-b379-46c8-bea3-70eb2b59af81" />

Answer
<img width="1600" height="758" alt="Answer" src="https://github.com/user-attachments/assets/97b62540-f1dc-41cc-b10a-7c3ac8f8b2d5" />

# ✨ Key Features
- Durable Orchestration: Powered by Inngest, ensuring document ingestion never fails silently. Supports auto-retries, state persistence, and event-driven triggers.
- Production-Grade Flow Control: Built-in Throttling and Rate Limiting to protect LLM quotas (OpenAI) and prevent Qdrant resource exhaustion.
- High-Performance Retrieval: Leverages Qdrant for lightning-fast vector similarity searches with advanced filtering.
- Scalable API Layer: FastAPI backend providing asynchronous endpoints for low-latency AI responses.
- Interactive UI: A polished Streamlit dashboard for managing data sources and testing context retrieval.

# 🛠️ Tech Stack
- Language: Python 3.10+
- API Framework: FastAPI 
- Orchestration: Inngest (Durable functions & event-driven architecture)
- Vector Database: Qdrant
- Frontend: Streamlit
- Data Processing: LlamaIndex

# 🚀 Getting Started
### Prerequisites
- Python 3.10+
- Inngest Dev Server
- Qdrant Instance (Local or Cloud)

### Quick Start
##### 1. Clone & Install
```sh
git clone https://github.com/Aman-Papaney/ContextEngine.git
cd ContextEngine
pip install . 
```
##### 2. Environment Setup: Create a .env file:

LLM_API_KEY = 


QDRANT_API_KEY = 


QDRANT_CLUSTER_ENDPOINT = 


GEMINI_API_KEY = 

##### 3. Launch Services
Terminal 1: Inngest


 ```sh
inngest dev
```

Terminal 2: FastAPI


 ```sh
uvicorn main:app --reload
```

 Terminal 3: Streamlit

 ```sh
streamlit run app.py
```
