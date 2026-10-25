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

# Detect CUDA acceleration
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Optimize CPU threads if on CPU
if DEVICE == "cpu":
    torch.set_num_threads(max(1, min(8, os.cpu_count() or 4)))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(BASE_DIR, "knowledge_base")
INDEX_DIR = os.path.join(BASE_DIR, "index")
os.makedirs(INDEX_DIR, exist_ok=True)

EMBEDDING_MODEL_NAME = "BAAI/bge-base-en-v1.5"

# Common agricultural abbreviations that must not trigger sentence splits
AGRI_ABBREVIATIONS = [
    r"e\.g\.", r"i\.e\.", r"a\.i\.", r"sp\.", r"spp\.", r"var\.", r"cf\.",
    r"WP\.", r"EC\.", r"SC\.", r"SL\.", r"WG\.", r"pH\.", r"approx\.",
    r"vs\.", r"fig\.", r"tab\.", r"no\.", r"vol\.", r"ha\.", r"kg\.",
    r"gm\.", r"ml\.", r"ppm\.", r"wt\."
]

def detect_topic(filename: str, text: str) -> str:
    combined = (filename + " " + text[:800]).lower()
    if any(k in combined for k in ["rust", "hemileia", "pustule", "clr"]):
        return "leaf_rust"
    elif any(k in combined for k in ["cercospora", "leaf spot", "brown eye", "berry blotch", "coffeicola"]):
        return "cercospora_leaf_spot"
    elif any(k in combined for k in ["miner", "leucoptera", "serpentine", "blotch mine"]):
        return "leaf_miner"
    elif any(k in combined for k in ["phoma", "costaricensis", "dieback", "twig dieback", "tip blight", "stem blight"]):
        return "phoma_blight"
    elif any(k in combined for k in ["anthracnose", "colletotrichum", "black rot", "koleroga", "pellicularia"]):
        return "anthracnose_black_rot"
    elif any(k in combined for k in ["fertilizer", "nutrient", "organomineral", "soil", "npk", "urea", "potash", "zinc", "boron", "dolomite", "acidity"]):
        return "nutrition_fertilizer"
    elif any(k in combined for k in ["borer", "white stem borer", "shot hole", "mealybug", "scale", "arthropod", "pest"]):
        return "pest_management"
    elif any(k in combined for k in ["cultivation", "shade", "pruning", "dadap", "silver oak", "lopping", "two-tier", "drainage"]):
        return "cultural_shade_management"
    else:
        return "coffee_agronomy"

def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\x20-\x7E\u0C80-\u0CFF]", " ", text)  # Keep ASCII + Kannada
    return text.strip()

def split_into_sentences(text: str) -> list[str]:
    """
    Abbreviation-protected sentence splitting.
    Protects agricultural terms like 'a.i.', 'e.g.', 'pH 6.5', '50 WP.' from false splits.
    """
    # Replace dots in known abbreviations with safe marker
    protected_text = text
    token_map = {}
    for idx, abbr in enumerate(AGRI_ABBREVIATIONS):
        pattern = re.compile(rf"\b{abbr}", re.IGNORECASE)
        placeholder = f"__AGRI_ABBR_{idx}__"
        for match in pattern.finditer(protected_text):
            orig_match = match.group(0)
            token_map[placeholder] = orig_match
            protected_text = protected_text.replace(orig_match, placeholder)

    # Standard sentence boundary split
    raw_sentences = re.split(r'(?<=[.!?])\s+', protected_text)

    # Restore placeholders
    sentences = []
    for s in raw_sentences:
        s_restored = s
        for placeholder, orig in token_map.items():
            s_restored = s_restored.replace(placeholder, orig)
        s_restored = s_restored.strip()
        if s_restored:
            sentences.append(s_restored)
    return sentences

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
    print(f"[PlantIQ] RAG Index Ingestion & Vector Build (Device: {DEVICE.upper()})")
    print(f"[*] PDF Knowledge Base: {PDF_DIR}")
    print(f"[*] Index Destination: {INDEX_DIR}")
    print("==================================================")

    if not os.path.exists(PDF_DIR):
        raise FileNotFoundError(f"Knowledge directory '{PDF_DIR}' not found!")

    pdf_files = [f for f in sorted(os.listdir(PDF_DIR)) if f.endswith(".pdf")]
    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in '{PDF_DIR}'!")

    all_chunks = []
    print(f"\n[1/4] Parsing {len(pdf_files)} PDFs with PyMuPDF (Text & Tables)...")
    for fname in pdf_files:
        fpath = os.path.join(PDF_DIR, fname)
        try:
            doc = fitz.open(fpath)
            pdf_chunks = []
            num_pages = len(doc)
            for p_idx, page in enumerate(doc):
                page_num = p_idx + 1

                # 1. Check for tabular structures (e.g. spray schedule tables)
                try:
                    tabs = getattr(page, "find_tables", None)
                    if tabs:
                        found_tabs = tabs()
                        if found_tabs and getattr(found_tabs, "tables", None):
                            for t_idx, tab in enumerate(found_tabs.tables):
                                md_table = tab.to_markdown() if hasattr(tab, "to_markdown") else ""
                                if md_table and len(md_table.strip()) > 30:
                                    topic = detect_topic(fname, md_table)
                                    pdf_chunks.append({
                                        "text": f"[Schedule & Dosage Table] {md_table.strip()}",
                                        "source": fname,
                                        "page": page_num,
                                        "section": f"Tabular Schedule {t_idx + 1}",
                                        "topic": topic
                                    })
                except Exception as table_err:
                    pass

                # 2. Extract standard running text
                p_text = page.get_text("text")
                if p_text.strip():
                    chunks = semantic_chunk_text(p_text, fname, page_num)
                    pdf_chunks.extend(chunks)

            doc.close()
            print(f"  [+] {fname}: {len(pdf_chunks)} semantic chunks (Pages: {num_pages})")
            all_chunks.extend(pdf_chunks)
        except Exception as e:
            print(f"  [-] Error reading {fname}: {e}")

    print(f"\n[2/4] Total Semantic Chunks Created: {len(all_chunks)}")

    # 1. Build Dense FAISS Index with BGE
    print(f"\n[3/4] Generating Dense Embeddings using '{EMBEDDING_MODEL_NAME}' on {DEVICE.upper()}...")
    embedder = SentenceTransformer(EMBEDDING_MODEL_NAME, device=DEVICE)
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
