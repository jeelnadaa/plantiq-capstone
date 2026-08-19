# Coffee RAG System

An intelligent Retrieval-Augmented Generation (RAG) system designed to provide expert agronomic advice for coffee crop disease management. The system identifies coffee leaf diseases and combines diagnosed data with environmental factors to generate actionable treatment and prevention plans.

---

## Development Overview

The project is structured into three primary modules that handle data processing, core RAG logic, and CLI interaction:

- **`main.py`**: The central entry point for the application. It provides a Command Line Interface (CLI) to run predefined demo scenarios, ask live questions, or simulate disease diagnostics.
- **`pipeline.py`**: The core "engine" of the RAG system. It handles:
    - **Configuration**: Loads settings and API keys from `.env`.
    - **PDF Ingestion**: Parses, cleans, and chunks agronomy documents from the `knowledge_base` folder.
    - **Vector Search**: Manages the FAISS index for high-speed retrieval of relevant knowledge chunks.
    - **LLM Integration**: Wraps the Google Gemini API to synthesize answers based on retrieved context.
    - **RAG Dual-Modes**:
        - **Mode 1 (Disease Advisory)**: Processes structured inputs (disease name, confidence, temperature, humidity, etc.) to give a holistic field advisory.
        - **Mode 2 (Q&A)**: Answers plain-text agronomic questions from farmers.
- **`demo.py`**: Contains simulation scenarios for both RAG modes to showcase the system's ability to handle various coffee diseases (e.g., Leaf Rust, Leaf Miner, Cercospora Blight) and farmer queries.

---

## Technological Stack

The system leverages a combination of cutting-edge open-source tools and high-performance licensed AI models.

### Open-Source Technologies
- **[FAISS](https://github.com/facebookresearch/faiss)**: A library for efficient similarity search and clustering of dense vectors.
- **[Sentence-Transformers](https://sbert.net/)**: Used for generating high-quality text embeddings (`all-MiniLM-L6-v2`).
- **[PyMuPDF (fitz)](https://pymupdf.readthedocs.io/) / [pdfplumber](https://github.com/jsvine/pdfplumber)**: Robust libraries for extracting and cleaning text from PDF documents.
- **[NumPy](https://numpy.org/)**: Foundation for numerical operations and vector handling.
- **[Python-Dotenv](https://github.com/theskumar/python-dotenv)**: For secure management of environment variables and API keys.

### Licensed / Managed Services
- **[Google Generative AI (Gemini)](https://ai.google.dev/)**: The Large Language Model (LLM) used for reasoning and professional response synthesis. This is a licensed/managed API service provided by Google.

---

## Usage

### Run All Demo Scenarios
```bash
# Run all demo scenarios (CNN diagnostics + plain queries)
python main.py demo all
```

### Specific Scenarios
```bash
# Just CNN/Disease scenarios
python main.py demo cnn          # runs all 4 disease scenarios
python main.py demo cnn 0        # specific scenario: Coffee Leaf Rust

# Just Plain Query scenarios
python main.py demo query        # runs all 3 question scenarios
```

### Live Use
```bash
# Ask a direct question
python main.py ask "How do I treat coffee leaf rust organically?"

# Run a simulated live disease diagnostic
python main.py disease
```

---

## How the Index Works

The system manages its knowledge base automatically. You don't need to manually build indexes.

1. **Check**: On startup, it looks for an existing FAISS index in the `index/` folder.
2. **Load**: If found, it loads the vector store into memory immediately.
3. **Build**: If the index is missing, it scans the `knowledge_base/` folder for PDFs, chunks them, generates embeddings, and saves a new index.
4. **Fallback**: If no PDFs are found, the system warns the user and falls back to Gemini's built-in knowledge to answer questions.
