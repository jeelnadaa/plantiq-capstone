import re
import json
import logging
from typing import Dict, Any

log = logging.getLogger(__name__)

def analyze_and_route_query(user_query: str, ui_lang_hint: str = "en") -> Dict[str, Any]:
    """
    Uses an LLM pre-router to intelligently understand user intent, detect language
    (native Kannada, Kanglish, or English), and generate optimal English search keywords for RAG.
    Zero hardcoded keywords or regex limitations.
    """
    if not user_query or not user_query.strip():
        return {
            "detected_language": "english" if ui_lang_hint == "en" else "kannada",
            "input_script": "english" if ui_lang_hint == "en" else "kannada_script",
            "english_search_query": "",
            "is_greeting_or_location_only": True
        }

    # Fast check: If pure ASCII and obviously plain English words with no Kannada intent
    # We can still let LLM analyze for complex mixed queries
    from app.modules.rag.pipeline import query_llm

    prompt = f"""\
You are an intelligent language router for an agricultural AI system (PlantIQ) assisting coffee farmers.
Analyze the farmer's input query and return a valid JSON object.

Farmer's Message: "{user_query}"

Tasks:
1. "detected_language": "kannada" (if written in Kannada script OR Kanglish/transliterated Kannada) or "english".
2. "input_script": "kanglish" (if Kannada words written in Latin/English letters), "kannada_script" (if written in native Kannada ಲಿಪಿ), or "english".
3. "english_search_query": Translate and formulate concise English agricultural keywords optimized for semantic search in an agronomy vector database (e.g. 'ideal temperature rainfall soil pH elevation for coffee'). If the input is just a greeting/location, leave empty.
4. "is_greeting_or_location_only": true if the input is ONLY a location name (e.g. 'ಚಿಕ್ಕಬೆಗುರು', 'Chikmagalur'), a greeting ('hello', 'namaskara'), or a single vague word without a specific farming question; otherwise false.

Respond ONLY with valid JSON in this exact structure:
{{
  "detected_language": "kannada" | "english",
  "input_script": "kannada_script" | "kanglish" | "english",
  "english_search_query": "...",
  "is_greeting_or_location_only": true | false
}}
"""
    try:
        raw_resp = query_llm(prompt)
        # Extract JSON substring
        json_match = re.search(r'\{.*\}', raw_resp, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group(0))
            return {
                "detected_language": parsed.get("detected_language", "english"),
                "input_script": parsed.get("input_script", "english"),
                "english_search_query": parsed.get("english_search_query", user_query),
                "is_greeting_or_location_only": parsed.get("is_greeting_or_location_only", False)
            }
    except Exception as e:
        log.warning("LLM Pre-Router failed (%s), falling back to heuristics...", e)

    # Fallback heuristic if LLM call is unavailable
    has_kannada_unicode = bool(re.search(r'[\u0C80-\u0CFF]', user_query))
    return {
        "detected_language": "kannada" if (has_kannada_unicode or ui_lang_hint == "kn") else "english",
        "input_script": "kannada_script" if has_kannada_unicode else ("kanglish" if ui_lang_hint == "kn" else "english"),
        "english_search_query": user_query,
        "is_greeting_or_location_only": len(user_query.strip().split()) <= 1
    }

def detect_language_and_script(text: str, ui_lang_hint: str = "en") -> str:
    """Backward-compatible helper function."""
    routed = analyze_and_route_query(text, ui_lang_hint)
    return routed["input_script"]

def translate_query_for_rag_retrieval(query: str, detected_lang: str) -> str:
    """Backward-compatible helper function."""
    routed = analyze_and_route_query(query)
    search_q = routed.get("english_search_query", "").strip()
    return f"{query} {search_q}" if search_q else query
