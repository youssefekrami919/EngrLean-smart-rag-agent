# EngrLean Smart RAG Agent — Future Work & Roadmap

This document outlines the architectural roadmap and modular enhancement blueprints for the **EngrLean Smart RAG Agent (`LeanBot`)** as it transitions beyond the MVP stage.

---

## 1. Executive Tools & Autonomous Agent Capabilities

The core architecture includes an abstract tool foundation (`AbstractTool` and `ToolRegistry` in `src/agent/tools/base.py`). Future implementations can register execution tools without modifying the RAG pipeline or core agent loop:

### 1.1. Qualified Lead Capture & Gmail API Dispatch
* **Objective:** Automatically extract lead details (Visitor Name, Company, Email, Phone, Project Pillar, Inquiry Scope) and notify the sales and executive team.
* **Component Blueprint:**
  * Implement `LeadCaptureTool(AbstractTool)`.
  * Implement `GmailNotificationTool(AbstractTool)` using Google Workspace APIs to send formatted executive briefings directly to `contact@engrlean.com` and `Eng. Mohamed Yahia`.
* **Trigger Boundary:** Executed only when the visitor explicitly expresses commercial interest or requests a technical consultation.

### 1.2. WhatsApp Business API Webhook Integration
* **Objective:** Enable bidirectional synchronization between the website chatbot and EngrLean's official WhatsApp Business number (`+20 100 000 0000`).
* **Component Blueprint:**
  * Implement `WhatsAppWebhookTool(AbstractTool)` to trigger WhatsApp templates when a user requests follow-up over mobile messaging.
  * Webhook listener to ingest incoming WhatsApp conversations into the unified RAG agent pipeline.

### 1.3. CRM & ERP Sync Connectors
* **Objective:** Persist qualified leads into EngrLean's internal business software systems.
* **Component Blueprint:**
  * Pluggable database adapters (`PostgresLeadStore`, `HubSpotCRMConnector`, `OdooConnector`).

---

## 2. Advanced Retrieval Engineering (RAG 2.0)

While dense vector similarity using `text-embedding-004` delivers robust semantic search, future phases will introduce:

### 2.1. Hybrid Search (Lexical BM25 + Semantic Dense)
* **Rationale:** Exact terminology matching is essential for specific engineering standard codes (e.g., ISO/IEC 27001, COBIT 2019, TIA-942 Tier IV standards, IEEE).
* **Implementation:**
  * Integrate BM25 sparse keyword indexing alongside ChromaDB dense embeddings.
  * Implement Reciprocal Rank Fusion (RRF) to merge score distributions.

### 2.2. Cross-Encoder Re-ranking (Flash Re-ranker)
* **Rationale:** Maximizes retrieval precision by taking the top 15 candidate chunks and scoring them with a cross-encoder model before passing only the top 4 highest-relevance chunks to Gemini 1.5 Flash.
* **Implementation:**
  * Hook into `RAGPipeline.retrieve_context()` to apply Cohere Re-rank or a local Flash re-ranker stage.

### 2.3. Dynamic Metadata Filtering by Corporate Pillar
* **Rationale:** Filter searches based on explicit pillar context (e.g., `#digital-transformation`, `#smart-systems`, `#software-integration`) to eliminate cross-pillar noise for technical inquiries.

---

## 3. Session State & Long-Term Memory

### 3.1. Persistent Chat History
* **Current State:** In-memory session state scoped to the Streamlit session.
* **Future Upgrade:**
  * Store multi-turn transcripts in a persistent datastore (PostgreSQL / SQLite).
  * Enable visitor session resumption across device switches using unique session tokens.

### 3.2. Analytics & Conversation Intelligence Dashboard
* **Objective:** Provide the executive team with insights into:
  * Most frequently requested engineering services.
  * Emerging customer interest trends (e.g., Smart Home adoption rates in Egypt and GCC).
  * Unanswered inquiries (gap analysis) to continually enrich `data/knowledge/`.

---

## 4. Headless REST API Architecture (FastAPI Transition)

To connect the RAG core directly with EngrLean's primary web portal (`https://engrlean.com/`):

### 4.1. Headless Endpoints
Create `src/api/` exposing FastAPI endpoints:
* `POST /api/v1/chat`: Streaming and non-streaming conversational responses.
* `POST /api/v1/ingest`: Secured endpoint for triggering knowledge base re-indexing via Webhook.
* `GET /api/v1/health`: Liveness and readiness probes for cloud orchestrators.

### 4.2. Containerization & Production Deployment
* **Dockerfile:** Multi-stage, lightweight Alpine/Debian Python image.
* **Cloud Target:** Deployable as a serverless container on Google Cloud Run, Railway, or AWS ECS behind Cloudflare SSL termination.

