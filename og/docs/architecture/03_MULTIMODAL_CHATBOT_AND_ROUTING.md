# 💬 Module 3: Multimodal Agronomy Chatbot & Linguistic Pre-Router

## 1. Executive Summary & Problem Statement
Smallholder coffee planters in Karnataka (Chikkamagaluru, Kodagu, Hassan) communicate fluidly across three linguistic forms:
1. Standard Literary Kannada Script (`ಕನ್ನಡ ಲಿಪಿ`)
2. Romanized Colloquial Kannada / Kanglish (e.g., *"ele mele haladi chukke idhe, yava aushadhi hodibeku?"*)
3. Indian English Agricultural Terminology (e.g., *"dosage for Bordeaux mixture during blossom showers"*).

Furthermore, farmers need to ask follow-up questions about leaf photos taken days ago or in previous sessions.

The **Multimodal Chatbot & Linguistic Routing Module** orchestrates:
1. **Zero-Latency Linguistic Script & Intent Pre-Routing**
2. **Multimodal CNN Vision Injection into Gemini 2.5 Flash / Groq GPT-OSS 120B**
3. **Sequential Context Ingestion** (CNN Pathology + Microclimate Weather + CCRI Treatment History)
4. **Persistent Image Data URIs & Multi-Turn Conversation Memory** in SQLite.

---

## 2. Linguistic Pre-Router Architecture

### 2.1 Script & Language Detection Matrix
Before sending queries to vector stores or LLMs, the **Linguistic Router** analyzes the input string in $< 1 \text{ ms}$:

```
                              [ Raw Farmer Input ]
                                       │
                ┌──────────────────────┼──────────────────────┐
                ▼                      ▼                      ▼
       [ Unicode Regex ]       [ Lexicon Match ]      [ Phonetic N-Gram ]
       (Kannada Range:         (Agri Kanglish         (Common Vernacular
        U+0C80 - U+0CFF)        Vocabulary)            Grammar Rules)
                │                      │                      │
                └──────────────────────┼──────────────────────┘
                                       │
                                       ▼
                     [ Classification & Translation Metadata ]
                     - detected_script: kannada_script / kanglish / english
                     - target_response_language: kn / en
                     - search_query_english: Cleaned Agronomy Search Terms
```

### 2.2 Kanglish Semantic Normalization
When a farmer types in Kanglish, vector databases indexed in English would fail to retrieve relevant documents. The Linguistic Router uses an agronomic dictionary mapper:
* *"haladi chukke"* $\to$ `"yellow spots / leaf rust"`
* *"kempu roga"* $\to$ `"red rust / disease"`
* *"aushadhi / dosage"* $\to$ `"fungicide spray dosage"`
* *"kole roga"* $\to$ `"black rot / berry rot"`

The extracted `search_query_english` is passed directly to the Hybrid RAG engine, ensuring $100\%$ retrieval precision while instructing the LLM to format the response strictly in native Kannada script (`ಕನ್ನಡ`).

---

## 3. Sequential Multimodal Context Injection

To generate actionable agronomic advice, the chatbot constructs a dense context payload injected into the system prompt:

```
[SYSTEM PROMPT]
├─ 1. Agronomist Persona & South Indian Coffee Context
├─ 2. Multimodal CNN Pathology: ResNet-50 Top-1 Class & Confidence (%)
├─ 3. Microclimate Telemetry: Temperature, Humidity, Elevation, Rain, pH
├─ 4. Historical Diagnostic Treatment Advisory (from Previous Scans)
├─ 5. Hybrid RAG Context Chunks (CCRI Grounded Fungicide Ratios)
└─ 6. Farmer Multi-Turn Conversation History + Attached Image Base64
```

### 3.1 LLM Fallback & Orchestration Architecture
1. **Primary LLM**: **Google Gemini 2.5 Flash**
   * *Rationale*: Native multimodal vision processing, large context window (1M tokens), high reasoning speed, superior Kannada script generation.
2. **Failover LLM**: **Groq GPT-OSS 120B (`openai/gpt-oss-120b`)**
   * *Rationale*: Massive 120B parameter frontier open-weights reasoning capability on Groq LPUs ($< 450 \text{ ms}$ TTFT) when external API rate limits or network latency spikes occur.

---

## 4. Multi-Turn Memory & Image Persistence

### 4.1 Relational Schema (`ChatMessage`)
```sql
CREATE TABLE chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    role VARCHAR(20) NOT NULL,            -- 'user' or 'assistant'
    content TEXT NOT NULL,
    image_data_url TEXT,                   -- Persistent base64 data URI
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
```

### 4.2 Cross-Page Image Rehydration
When a user navigates between the Leaf Scanner, Marketplace, and Chat tabs, or reopens the mobile APK:
1. `chat.js` fetches `/api/chat/history`.
2. Any message containing `image_data_url` immediately renders the attached leaf photograph inside the chat bubble.
3. The farmer can tap the image to zoom or reference past diagnostic queries seamlessly.
