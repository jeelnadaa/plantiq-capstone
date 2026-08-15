import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import google.generativeai as genai
from groq import Groq
from app.core.config import settings
from app.modules.rag.vector_store import get_vector_store, Chunk
from app.modules.rag.blender import evaluate_confidence, construct_advisory_prompt
from app.modules.rag.language_router import detect_language_and_script, translate_query_for_rag_retrieval

log = logging.getLogger(__name__)

@dataclass
class AdvisoryResult:
    answer: str
    cnn_confidence: float
    rag_confidence: float
    is_blended: bool
    reasons: List[str]
    sources: List[str]

def query_llm(prompt: str, provider: str = "gemini") -> str:
    """Invokes LLM provider (Gemini with Groq fallback)."""
    if provider == "groq" or not settings.GEMINI_API_KEY:
        return _query_groq(prompt)
    return _query_gemini(prompt)

def _query_gemini(prompt: str) -> str:
    if not settings.GEMINI_API_KEY:
        return _query_groq(prompt)
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel(settings.GEMINI_MODEL)
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        log.error("Gemini API call failed: %s. Falling back to Groq...", e)
        return _query_groq(prompt)

def _query_groq(prompt: str) -> str:
    if not settings.GROQ_API_KEY:
        return "I'm currently operating offline without an API key. Please configure GEMINI_API_KEY or GROQ_API_KEY."
    try:
        client = Groq(api_key=settings.GROQ_API_KEY)
        completion = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        log.error("Groq API call failed: %s", e)
        return f"Unable to reach LLM services at this moment: {e}"

def generate_disease_advisory(
    disease: str,
    cnn_confidence: float,
    is_healthy: bool,
    env_data: Dict[str, Any] = None,
    user_question: Optional[str] = None,
    language: str = "en",
    provider: str = "gemini"
) -> AdvisoryResult:
    """Runs the full CNN -> RAG -> LLM flow with confidence-aware blending and language routing."""
    if env_data is None:
        env_data = {}

    detected_lang = "english"
    if user_question:
        detected_lang = detect_language_and_script(user_question, ui_lang_hint=language)
    elif language == "kn":
        detected_lang = "kannada_script"

    if is_healthy or disease == "Healthy":
        healthy_msg = (
            "ಉತ್ತಮ ಉದ್ಯಾನವನ! ನಿಮ್ಮ ಕಾಫಿ ಎಲೆ ಆರೋಗ್ಯಕರವಾಗಿದೆ ಮತ್ತು ಯಾವುದೇ ರೋಗದ ಲಕ್ಷಣಗಳು ಕಂಡುಬಂದಿಲ್ಲ. ನಿಯಮಿತ ನೀರಾವರಿ, ಕಳೆ ನಿಯಂತ್ರಣ ಮತ್ತು ಮಣ್ಣಿನ ನಿರ್ವಹಣೆಯನ್ನು ಮುಂದುವರಿಸಿ." 
            if (detected_lang in ["kannada_script", "kanglish"] or language == "kn") else
            "Great news! Your coffee leaf appears healthy and free of detected diseases. Maintain normal irrigation, weed control, and soil management."
        )
        return AdvisoryResult(
            answer=healthy_msg,
            cnn_confidence=cnn_confidence,
            rag_confidence=1.0,
            is_blended=False,
            reasons=[],
            sources=[]
        )

    # 1. Perform FAISS vector retrieval with English normalized search terms
    store = get_vector_store()
    search_query = f"{disease} treatment coffee symptoms prevention"
    if user_question:
        translated_q = translate_query_for_rag_retrieval(user_question, detected_lang)
        search_query = f"{disease} {translated_q}"
    if env_data:
        search_query += " " + " ".join(str(v) for v in env_data.values())

    chunks, scores = store.search(search_query, top_k=5)
    best_rag_score = scores[0] if scores else 0.0
    sources = list(set([f"{c.source} (p.{c.page})" for c in chunks]))

    # Format RAG context
    formatted_context = "\n\n".join(
        [f"[{i+1}] {c.source} p.{c.page}\n{c.text}" for i, c in enumerate(chunks)]
    ) if chunks else "No specific document context found in local knowledge base."

    # 2. Evaluate confidence thresholds
    eval_res = evaluate_confidence(cnn_confidence, best_rag_score)

    # 3. Construct prompt with language directives
    prompt = construct_advisory_prompt(
        disease=disease,
        cnn_confidence=cnn_confidence,
        env_data=env_data,
        user_question=user_question,
        rag_context=formatted_context,
        confidence_eval=eval_res,
        language=language,
        detected_lang=detected_lang
    )

    # 4. Generate response via LLM
    answer = query_llm(prompt, provider=provider)

    return AdvisoryResult(
        answer=answer,
        cnn_confidence=cnn_confidence,
        rag_confidence=best_rag_score,
        is_blended=eval_res["is_low_confidence"],
        reasons=eval_res["reasons"],
        sources=sources
    )
