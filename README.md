# SIRS — Secure Offline Intelligence Retrieval System

> A secure, offline-first AI-powered document retrieval and analysis platform built for defense intelligence operations. No internet connection required. All processing happens locally.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [Running the System](#running-the-system)
- [API Endpoints](#api-endpoints)
- [IEEE Compliance](#ieee-compliance)
- [Running Tests](#running-tests)
- [Features](#features)

---

## Overview

SIRS (Secure Offline Intelligence Retrieval System) is a B.Tech capstone project that implements an agentic RAG (Retrieval-Augmented Generation) pipeline for secure, offline document intelligence. Users can upload classified documents and query them using natural language — all processing runs locally with no external API calls.

Key properties:
- Fully **offline** — no data leaves the system
- **Agentic pipeline** — multi-step planning and tool execution
- **MCP (Model Context Protocol)** — structured tool communication
- **IEEE compliant** — validated against 5 IEEE software engineering standards

---

## Architecture

SIRS uses a modular six-layer backend architecture:

```
┌─────────────────────────────────────────┐
│           Layer 1: API Layer            │  FastAPI REST endpoints
├─────────────────────────────────────────┤
│          Layer 2: Agent Layer           │  Plan-based query controller
├─────────────────────────────────────────┤
│           Layer 3: MCP Layer            │  Tool communication protocol
├─────────────────────────────────────────┤
│          Layer 4: Tools Layer           │  Retrieval, upload, summarizer,
│                                         │  report, list, IEEE compliance
├─────────────────────────────────────────┤
│        Layer 5: Retrieval Layer         │  FAISS vector store + chunking
│                                         │  + SentenceTransformers embeddings
├─────────────────────────────────────────┤
│          Layer 6: LLM Layer             │  Ollama local inference (Phi4-Mini)
└─────────────────────────────────────────┘
```

---

## Tech Stack

### Backend
| Component | Technology |
|---|---|
| API Framework | FastAPI 0.115 |
| Vector Database | FAISS 1.9 |
| Embeddings | SentenceTransformers (all-MiniLM-L6-v2) |
| Local LLM | Ollama (Phi4-Mini) |
| PDF Parsing | PyPDF2 |
| DOCX Parsing | python-docx |
| Logging | Loguru |
| Testing | Pytest |

### Frontend
| Component | Technology |
|---|---|
| Framework | React 18 |
| Build Tool | Vite |
| Styling | Tailwind CSS |
| HTTP Client | Axios |

---

## Project Structure

```
SIRS/
├── backend/
│   ├── main.py                        # FastAPI app entry point
│   ├── config.py                      # Settings and environment config
│   ├── conftest.py                    # Pytest path configuration
│   ├── requirements.txt               # Python dependencies
│   │
│   ├── api/
│   │   └── routes.py                  # All REST API route definitions
│   │
│   ├── routes/
│   │   └── ieee_compliance_route.py   # IEEE compliance API endpoints
│   │
│   ├── agent/
│   │   └── agent_controller.py        # Plan-based RAG query controller
│   │
│   ├── mcp/
│   │   ├── protocol.py                # MCPMessage / MCPResponse schemas
│   │   ├── communication.py           # MCP bus for tool routing
│   │   └── tool_registry.py           # Tool registration decorators
│   │
│   ├── tools/
│   │   ├── retrieval_tool.py          # FAISS document retrieval
│   │   ├── upload_tool.py             # Document ingestion + IEEE scan
│   │   ├── summarizer_tool.py         # Document summarization
│   │   ├── report_tool.py             # Report generation
│   │   ├── list_tool.py               # Document listing
│   │   ├── ieee_compliance_tool.py    # IEEE standards checker (5 standards)
│   │   └── ieee_compliance_store.py   # Compliance result persistence
│   │
│   ├── retrieval/
│   │   ├── vector_store.py            # FAISS index management
│   │   ├── embeddings.py              # SentenceTransformers wrapper
│   │   └── chunking.py                # Text chunking strategies
│   │
│   ├── llm/
│   │   └── ollama_client.py           # Ollama HTTP client
│   │
│   ├── data/
│   │   ├── faiss_index/               # FAISS index files (auto-generated)
│   │   └── ieee_compliance_results.json  # Per-document compliance scores
│   │
│   ├── uploads/                       # Uploaded documents (auto-generated)
│   ├── logs/                          # Application logs (auto-generated)
│   │
│   └── tests/
│       └── test_ieee_compliance.py    # 15 IEEE compliance test cases
│
└── frontend/
    └── src/
        ├── pages/
        │   └── ChatPage.jsx           # Intelligence query interface
        ├── components/
        │   └── IEEEComplianceReport.jsx  # Compliance report display
        └── services/
            └── api.js                 # Backend API calls
```

---

## Setup Instructions

### Prerequisites

- Python 3.13
- Node.js 18+
- [Ollama](https://ollama.com) installed and running
- Git

### 1. Clone the repository

```bash
git clone https://github.com/abhinavpanuganti69/sirs-intelligence-retrieval.git
cd sirs-intelligence-retrieval
```

### 2. Backend setup

```bash
cd backend

# Create and activate virtual environment (Windows)
python -m venv venv
.\venv\Scripts\Activate.ps1

# If PowerShell blocks activation, run this first:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install dependencies
pip install -r requirements.txt
```

### 3. Pull the LLM model

```bash
ollama pull phi4-mini
```

### 4. Frontend setup

```bash
cd frontend
npm install
```

---

## Running the System

### Start backend (from `backend/` folder with venv activated)

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Start frontend (from `frontend/` folder)

```bash
npm run dev
```

### Access the system

| Service | URL |
|---|---|
| Frontend Dashboard | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Documentation | http://localhost:8000/docs |

---

## API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/health` | System health check |
| GET | `/api/v1/system/status` | Full system telemetry |
| POST | `/api/v1/query` | Submit an intelligence query |
| POST | `/api/v1/documents/upload` | Upload and index a document |
| GET | `/api/v1/documents` | List all indexed documents |
| DELETE | `/api/v1/documents/{doc_id}` | Delete a document |
| GET | `/api/v1/mcp/tools` | List registered MCP tools |
| GET | `/api/v1/mcp/log` | MCP audit log |
| GET | `/api/v1/settings` | System configuration |

### IEEE Compliance Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/compliance/check` | Run IEEE check on any text |
| GET | `/compliance/info` | List all 5 supported standards |
| GET | `/api/v1/documents/{doc_id}/compliance` | Get compliance report for a document |
| GET | `/api/v1/documents/compliance/all` | Get compliance scores for all documents |

### Query Response Format

Every `POST /api/v1/query` response includes a `compliance_report` field:

```json
{
  "answer": "...",
  "sources": [...],
  "compliance_report": {
    "overall_score_pct": 82.5,
    "overall_passed": true,
    "verdict": "COMPLIANT ✅",
    "standards": [
      { "id": "IEEE 12207", "passed": true,  "score_pct": 83.3 },
      { "id": "IEEE 830",   "passed": true,  "score_pct": 83.3 },
      { "id": "IEEE 829",   "passed": false, "score_pct": 50.0 },
      { "id": "IEEE 1016",  "passed": true,  "score_pct": 83.3 },
      { "id": "IEEE 730",   "passed": true,  "score_pct": 100.0 }
    ]
  }
}
```

---

## IEEE Compliance

SIRS includes a built-in IEEE compliance validation layer that runs automatically on every document upload and every query response.

### Supported Standards

| Standard | Name | What it validates |
|---|---|---|
| IEEE 12207 | Software Life Cycle Processes | Requirements, design, implementation, testing, deployment phases |
| IEEE 830 | Software Requirements Specifications | Functional/non-functional requirements, measurability, traceability |
| IEEE 829 | Software Test Documentation | Test plans, test cases, expected results, coverage |
| IEEE 1016 | Software Design Description | Architecture, interfaces, data design, design rationale |
| IEEE 730 | Software Quality Assurance | Quality metrics, review processes, defect tracking, security |

### How it works

1. When a document is uploaded, its full text is extracted and scanned against all 5 standards
2. Compliance scores are saved to `data/ieee_compliance_results.json` keyed by `doc_id`
3. When a query is answered, the RAG response is also checked and the report is returned alongside the answer
4. The frontend displays the compliance panel below every system response

---

## Running Tests

```bash
cd backend
python -m pytest tests/test_ieee_compliance.py -v
```

Expected output:

```
tests/test_ieee_compliance.py::test_tc01_ieee_12207_passes_on_rich_content PASSED
tests/test_ieee_compliance.py::test_tc02_ieee_830_passes_on_rich_content PASSED
tests/test_ieee_compliance.py::test_tc03_ieee_829_passes_on_rich_content PASSED
tests/test_ieee_compliance.py::test_tc04_ieee_1016_passes_on_rich_content PASSED
tests/test_ieee_compliance.py::test_tc05_ieee_730_passes_on_rich_content PASSED
tests/test_ieee_compliance.py::test_tc06_ieee_12207_fails_on_minimal_content PASSED
tests/test_ieee_compliance.py::test_tc07_ieee_830_fails_on_minimal_content PASSED
tests/test_ieee_compliance.py::test_tc08_ieee_829_fails_on_minimal_content PASSED
tests/test_ieee_compliance.py::test_tc09_empty_content_raises_value_error PASSED
tests/test_ieee_compliance.py::test_tc10_overall_report_fails_on_minimal_content PASSED
tests/test_ieee_compliance.py::test_tc11_full_report_has_five_standards PASSED
tests/test_ieee_compliance.py::test_tc12_to_dict_is_json_serializable PASSED
tests/test_ieee_compliance.py::test_tc13_check_compliance_public_function PASSED
tests/test_ieee_compliance.py::test_tc14_suggestions_given_for_failing_checks PASSED
tests/test_ieee_compliance.py::test_tc15_scores_are_within_valid_range PASSED

15 passed in 0.41s
```

---

## Features

- **Offline-first** — zero external API calls, all inference runs locally via Ollama
- **Agentic RAG pipeline** — multi-step planning with tool-use via MCP protocol
- **Multi-format ingestion** — supports PDF, DOCX, TXT, and Markdown
- **IEEE compliance layer** — validates documents and responses against 5 IEEE standards automatically
- **Defense-themed dashboard** — React frontend styled for DRDO/military intelligence context
- **Audit logging** — full MCP tool call trace per query
- **Document management** — upload, list, and delete documents with automatic FAISS re-indexing

---