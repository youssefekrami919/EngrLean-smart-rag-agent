# EngrLean Smart RAG Agent (`LeanBot`)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.39+-FF4B4B.svg)](https://streamlit.io/)
[![Google Gemini](https://img.shields.io/badge/Gemini-1.5%20Flash-4285F4.svg)](https://aistudio.google.com/)
[![ChromaDB](https://img.shields.io/badge/VectorStore-ChromaDB-green.svg)](https://www.trychroma.com/)
[![Architecture](https://img.shields.io/badge/Architecture-Clean%20Layered-orange.svg)](ARCHITECTURE.md)

Production-grade, API-first Retrieval-Augmented Generation (RAG) and autonomous agent system for **EngrLean** ([https://engrlean.com/](https://engrlean.com/)).

* **Chief Executive Officer:** Eng. Mohamed Yahia
* **Corporate Taglines:**
  * *"Built on engineering. Driven by technology."*
  * *"Engineering meets Technology."*
* **Core Business Pillars:**
  1. **Digital Transformation:** IT consulting, enterprise governance (ISO/COBIT/ITIL), and cybersecurity advisory.
  2. **Software & Integration:** Custom enterprise software, ERP/CRM implementations, APIs, and DevOps.
  3. **ICT & Smart Systems:** Data centers, structured cabling, smart buildings, and emerging Smart Home / IoT automation.

---

## Key Features

* **Zero Vendor Lock-in & Clean Architecture:** Pure Python codebase (`.py`) cleanly separated into `core`, `rag`, `agent`, and `ui` packages.
* **Cost-Efficient & High-Speed:** Powered by Google's **Gemini 1.5 Flash** (1M token context window) and **`text-embedding-004`** via Google AI Studio.
* **Native Bilingual Capability:** Automatically and fluently handles cross-lingual inquiries across Arabic and English.
* **Strict Guardrails (Zero-Hallucination):** Strictly answers from verified corporate knowledge. Out-of-scope questions automatically trigger polite disclaimers redirecting visitors to official Phone, WhatsApp, and Email contacts.
* **Self-Bootstrapping Vector Database:** Local ChromaDB persistent store that automatically builds itself on startup if missing.
* **One-Click Streamlit Cloud Compatibility:** Root-level orchestrator (`main.py`) designed for zero-configuration deployment to Streamlit Community Cloud.
* **Modular Extensibility:** Built-in abstract tool foundation ready for Gmail API notifications, WhatsApp business webhooks, and headless FastAPI endpoints.

---

## Architecture Overview

```text
EngrLean-smart-rag-agent/
├── .env.example                # Template for local environment variables
├── .gitignore                  # Git exclusions for secrets and local DB
├── ARCHITECTURE.md             # In-depth architectural blueprint & diagrams
├── FUTURE_WORK.md              # Roadmap for tools, database, and FastAPI
├── README.md                   # This operations manual
├── requirements.txt            # Pinned dependencies
├── main.py                     # Root entrypoint for Streamlit Community Cloud
├── ingest.py                   # Standalone CLI knowledge base ingestion script
├── data/
│   └── knowledge/              # Knowledge repository
│       └── engrlean_profile.md # Structured corporate profile & services catalog
└── src/
    ├── core/                   # Central settings, secrets manager, LLM client
    ├── rag/                    # Loader, recursive chunker, ChromaDB, pipeline
    ├── agent/                  # LeanBot logic, system prompts, tool abstractions
    └── ui/                     # EngrLean brand CSS and Streamlit presentation
```

---

## Getting Started

### 1. Prerequisites
* Python 3.10 or higher.
* A free Google AI Studio API key.

### 2. Obtain Your Google Gemini API Key
1. Visit [Google AI Studio API Keys](https://aistudio.google.com/apikey).
2. Sign in with your Google Account.
3. Click **"Create API key"** (in a new project).
4. Copy the generated key (typically starts with `AIzaSy...`).

### 3. Installation
Clone the repository and install the dependencies:
```bash
git clone https://github.com/your-org/EngrLean-smart-rag-agent.git
cd EngrLean-smart-rag-agent

python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 4. Configure Environment Variables (Local Development)
Create a `.env` file in the project root:
```bash
cp .env.example .env
```
Open `.env` and set your key:
```env
GEMINI_API_KEY=AIzaSyYourActualKeyHere
```

---

## Running the Application

### Launch the Streamlit Web Interface
Run the single root entrypoint:
```bash
streamlit run main.py
```
Open your browser at `http://localhost:8501`.

### CLI Knowledge Base Ingestion & Updates
Whenever you add or modify documents inside `data/knowledge/`, update the vector database by running:
```bash
python ingest.py
```
> **Tip:** You can also trigger re-indexing directly from the Streamlit web interface using the **"🔄 Re-index Knowledge Base"** button in the sidebar.

---

## Deploying to Streamlit Community Cloud

This project is explicitly structured for one-click deployment directly onto Streamlit Community Cloud:

1. **Push Repository to GitHub:**
   Ensure all files (including `main.py`, `requirements.txt`, and `data/knowledge/`) are pushed to your GitHub repository.
2. **Deploy on Streamlit:**
   * Go to [share.streamlit.io](https://share.streamlit.io/).
   * Select your repository, branch (`main`), and set **Main file path** to: `main.py`.
3. **Configure Secrets (Crucial):**
   In your Streamlit Cloud App Dashboard, navigate to **Settings** -> **Secrets**, and enter your API key in TOML format:
   ```toml
   GEMINI_API_KEY = "AIzaSyYourActualKeyHere"
   ```
4. **Bootstrapping:**
   Upon boot, `LeanBot` will automatically detect the absence of the vector store, read `data/knowledge/`, generate embeddings, and build the ChromaDB index in seconds!

---

## How to Add or Update Corporate Knowledge

1. Navigate to the `data/knowledge/` directory.
2. Add any `.md` or `.txt` file containing your updated company profile, project case studies, or service catalogs.
3. Run `python ingest.py` or click **"🔄 Re-index Knowledge Base"** in the sidebar.
4. LeanBot immediately begins answering queries using the updated facts!

---

## Contact & Corporate Information

* **Company:** EngrLean
* **CEO:** Eng. Mohamed Yahia
* **Website:** [https://engrlean.com/](https://engrlean.com/)
* **Support Email:** contact@engrlean.com / support@engrlean.com
* **Phone / WhatsApp:** +20 100 000 0000 (https://wa.me/201000000000)

