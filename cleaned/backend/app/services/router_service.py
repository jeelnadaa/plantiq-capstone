import json
import re
from typing import Dict, Any
from app.core.config import settings

def analyze_and_route_query(user_query: str) -> Dict[str, Any]:
    trimmed = user_query.strip()
    if not trimmed:
        return {"detected_script": "english", "search_query_english": "", "is_greeting_or_location_only": True, "target_response_language": "en"}

    has_kannada_script = bool(re.search(r'[ಀ-೿]', trimmed))
    
    prompt = f"""You are a specialized linguistic pre-router for PlantIQ, an agronomic AI for South Indian coffee farmers.
Analyze the following farmer query:
Query: '{trimmed}'

Return ONLY a JSON object with:
1. "detected_script": "kannada_script" (if native Kannada script), "kanglish" (if Kannada written in Latin/English alphabets like 'Coffee beliyalu yaava gobbara beku?'), or "english".
2. "search_query_english": Concise English keywords to search an agronomy manual (e.g. "coffee rust fungicide dosage"). If it is a greeting or location, provide empty string "".
3. "is_greeting_or_location_only": true if query is just a location (e.g. 'Chikkamagaluru') or greeting, false if it contains an agronomic question.
4. "target_response_language": "kn" if detected_script is kannada_script or kanglish, else "en".

JSON:"""

    res_text = ""
    if settings.GEMINI_API_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-2.5-flash')
            resp = model.generate_content(prompt, generation_config={"temperature": 0.1, "response_mime_type": "application/json"})
            res_text = resp.text
        except Exception as e:
            print(f"[Cleaned Router] Gemini warning: {e}")

    if not res_text and settings.GROQ_API_KEY:
        try:
            from groq import Groq
            g_client = Groq(api_key=settings.GROQ_API_KEY)
            comp = g_client.chat.completions.create(
                model='llama-3.3-70b-versatile',
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            res_text = comp.choices[0].message.content
        except Exception as e:
            print(f"[Cleaned Router] Groq warning: {e}")

    try:
        clean_json = res_text.strip().replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_json)
        return {
            "detected_script": data.get("detected_script", "kannada_script" if has_kannada_script else "english"),
            "search_query_english": data.get("search_query_english", trimmed),
            "is_greeting_or_location_only": bool(data.get("is_greeting_or_location_only", False)),
            "target_response_language": data.get("target_response_language", "kn" if has_kannada_script else "en")
        }
    except Exception:
        return {
            "detected_script": "kannada_script" if has_kannada_script else "english",
            "search_query_english": trimmed,
            "is_greeting_or_location_only": False,
            "target_response_language": "kn" if has_kannada_script else "en"
        }
