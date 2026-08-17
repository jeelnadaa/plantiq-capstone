"""
build_index.py
==============
Semantic Section Chunking & Ingestion Engine for PlantIQ RAG Service.
- Extracts text from CCRI agronomy PDFs.
- Splits by semantic sections/headings (200-400 tokens with 15-20% overlap).
- Tags each chunk with topic metadata and source references.
- Builds Dense Index (BAAI/bge-base-en-v1.5) in FAISS.
- Builds Sparse Lexical Index (BM25Okapi) for hybrid keyword search.
"""

import os
import re
import pickle
import numpy as np
import torch
import faiss
import fitz  # PyMuPDF
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

# Optimize CPU threads
torch.set_num_threads(max(1, min(8, os.cpu_count() or 4)))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(BASE_DIR, "knowledge_base")
INDEX_DIR = os.path.join(BASE_DIR, "index")
os.makedirs(INDEX_DIR, exist_ok=True)

EMBEDDING_MODEL_NAME = "BAAI/bge-base-en-v1.5"

def detect_topic(filename: str, text: str) -> str:
    combined = (filename + " " + text[:600]).lower()
    if "rust" in combined or "hemileia" in combined:
        return "leaf_rust"
    elif "cercospora" in combined or "leaf spot" in combined or "brown eye" in combined:
        return "cercospora_leaf_spot"
    elif "miner" in combined or "leucoptera" in combined:
        return "leaf_miner"
    elif "phoma" in combined or "stem" in combined or "blight" in combined or "dieback" in combined:
        return "phoma_blight"
    elif "fertilizer" in combined or "nutrient" in combined or "organomineral" in combined or "soil" in combined:
        return "nutrition_fertilizer"
    elif "pest" in combined or "arthropod" in combined or "borer" in combined:
        return "pest_management"
    elif "cultivation" in combined or "shade" in combined or "pruning" in combined:
        return "cultural_shade_management"
    else:
        return "coffee_agronomy"

def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\x20-\x7E\u0C80-\u0CFF]", " ", text)  # Keep ASCII + Kannada
    return text.strip()

def split_into_sentences(text: str) -> list[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]

def semantic_chunk_text(text: str, source: str, page_num: int, target_tokens: int = 300, overlap_tokens: int = 50) -> list[dict]:
    lines = text.split("\n")
    current_section = "General Section"
    sections = []
    current_buffer = []

    for line in lines:
        cleaned_line = line.strip()
        if not cleaned_line:
            continue
        
        # Semantic Heading Detection
        is_heading = (len(cleaned_line) < 80 and 
                      (cleaned_line.isupper() or 
                       re.match(r'^(#+|\d+\.|\b[A-Z][a-z]+(\s+[A-Z][a-z]+)*:)', cleaned_line) or
                       any(k in cleaned_line.lower() for k in [
                           "management", "control", "symptoms", "dosage", "fungicide", 
                           "treatment", "biology", "distribution", "epidemiology", "chemical", 
                           "organic", "shade", "spray schedule", "cultural practices"
                       ])))
        
        if is_heading and len(current_buffer) > 0:
            sections.append((current_section, " ".join(current_buffer)))
            current_section = cleaned_line
            current_buffer = []
        else:
            current_buffer.append(cleaned_line)

    if current_buffer:
        sections.append((current_section, " ".join(current_buffer)))

    chunks = []
    target_words = int(target_tokens * 0.75)   # ~225 words
    overlap_words = int(overlap_tokens * 0.75) # ~38 words

    for sec_title, sec_text in sections:
        sec_text = clean_text(sec_text)
        if not sec_text or len(sec_text) < 40:
            continue

        sentences = split_into_sentences(sec_text)
        current_chunk_words = []
        current_chunk_sentences = []

        for sent in sentences:
            sent_words = sent.split()
            if len(current_chunk_words) + len(sent_words) > target_words and current_chunk_words:
                chunk_text = f"[{sec_title}] " + " ".join(current_chunk_sentences)
                topic = detect_topic(source, chunk_text)
                chunks.append({
                    "text": chunk_text,
                    "source": source,
                    "page": page_num,
                    "section": sec_title,
                    "topic": topic
                })
                
                # Context overlap preservation (15-20%)
                retained_sentences = []
                retained_words_count = 0
                for s in reversed(current_chunk_sentences):
                    s_w = len(s.split())
                    if retained_words_count + s_w <= overlap_words:
                        retained_sentences.insert(0, s)
                        retained_words_count += s_w
                    else:
                        break
                current_chunk_sentences = retained_sentences + [sent]
                current_chunk_words = " ".join(current_chunk_sentences).split()
            else:
                current_chunk_sentences.append(sent)
                current_chunk_words.extend(sent_words)

        if current_chunk_sentences:
            chunk_text = f"[{sec_title}] " + " ".join(current_chunk_sentences)
            topic = detect_topic(source, chunk_text)
            chunks.append({
                "text": chunk_text,
                "source": source,
                "page": page_num,
                "section": sec_title,
                "topic": topic
            })

    return chunks

def build_knowledge_index():
    print("==================================================")
    print("[PlantIQ] RAG Index Ingestion & Vector Build")
    print(f"[*] PDF Knowledge Base: {PDF_DIR}")
    print(f"[*] Index Destination: {INDEX_DIR}")
    print("==================================================")

    if not os.path.exists(PDF_DIR):
        raise FileNotFoundError(f"Knowledge directory '{PDF_DIR}' not found!")

    pdf_files = [f for f in sorted(os.listdir(PDF_DIR)) if f.endswith(".pdf")]
    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in '{PDF_DIR}'!")

    all_chunks = []
    print(f"\n[1/4] Parsing {len(pdf_files)} PDFs with PyMuPDF...")
    for fname in pdf_files:
        fpath = os.path.join(PDF_DIR, fname)
        try:
            doc = fitz.open(fpath)
            pdf_chunks = []
            num_pages = len(doc)
            for p_idx, page in enumerate(doc):
                p_text = page.get_text("text")
                if p_text.strip():
                    chunks = semantic_chunk_text(p_text, fname, p_idx + 1)
                    pdf_chunks.extend(chunks)
            doc.close()
            print(f"  [+] {fname}: {len(pdf_chunks)} semantic chunks (Pages: {num_pages})")
            all_chunks.extend(pdf_chunks)
        except Exception as e:
            print(f"  [-] Error reading {fname}: {e}")

    print(f"\n[2/4] Total Semantic Chunks Created: {len(all_chunks)}")

    # 1. Build Dense FAISS Index with BGE
    print(f"\n[3/4] Generating Dense Embeddings using '{EMBEDDING_MODEL_NAME}'...")
    embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)
    chunk_texts = [c["text"] for c in all_chunks]
    embeddings = embedder.encode(
        chunk_texts, 
        batch_size=64, 
        show_progress_bar=True, 
        normalize_embeddings=True,
        convert_to_numpy=True
    ).astype(np.float32)

    dim = embeddings.shape[1]
    faiss_index = faiss.IndexFlatIP(dim)
    faiss_index.add(embeddings)
    print(f"  [+] FAISS Index FlatIP built: {faiss_index.ntotal} vectors (Dimension: {dim})")

    # 2. Build Sparse Lexical Index with BM25
    print("\n[4/4] Building BM25 Sparse Lexical Corpus Index...")
    def tokenize(t: str) -> list[str]:
        return [w.lower() for w in re.findall(r'\b\w+\b', t) if len(w) > 1]

    tokenized_corpus = [tokenize(t) for t in chunk_texts]
    bm25 = BM25Okapi(tokenized_corpus)
    print("  [+] BM25Okapi inverted index constructed successfully.")

    # Save to disk
    faiss_path = os.path.join(INDEX_DIR, "faiss_index.bin")
    faiss.write_index(faiss_index, faiss_path)

    chunks_pkl = os.path.join(INDEX_DIR, "chunks.pkl")
    with open(chunks_pkl, "wb") as f:
        pickle.dump(all_chunks, f)

    chunks_npy = os.path.join(INDEX_DIR, "chunks.npy")
    np.save(chunks_npy, np.array(all_chunks, dtype=object), allow_pickle=True)

    bm25_path = os.path.join(INDEX_DIR, "bm25_index.pkl")
    with open(bm25_path, "wb") as f:
        pickle.dump({"bm25": bm25, "tokenized_corpus": tokenized_corpus}, f)

    print("\n==================================================")
    print("SUCCESS: RAG Knowledge Base & Hybrid Index Rebuilt!")
    print(f"  - FAISS Vector Store: {faiss_path}")
    print(f"  - BM25 Lexical Index: {bm25_path}")
    print(f"  - Semantic Chunk Metas: {chunks_pkl}")
    print("==================================================")

if __name__ == "__main__":
    build_knowledge_index()
