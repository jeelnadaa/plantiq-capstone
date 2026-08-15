from typing import Dict, Any, List
from app.core.config import settings

def evaluate_confidence(cnn_confidence: float, rag_similarity: float) -> Dict[str, Any]:
    """
    Evaluates whether the prediction or retrieval confidence is below threshold.
    Returns evaluation status and recommended generation mode.
    """
    is_cnn_low = cnn_confidence < settings.CONFIDENCE_THRESHOLD_CNN
    is_rag_low = rag_similarity < settings.CONFIDENCE_THRESHOLD_RAG
    is_low_confidence = is_cnn_low or is_rag_low

    reasons = []
    if is_cnn_low:
        reasons.append(f"CNN diagnosis confidence is {cnn_confidence:.1f}% (below threshold {settings.CONFIDENCE_THRESHOLD_CNN:.0f}%)")
    if is_rag_low:
        reasons.append(f"Knowledge-base match similarity is {rag_similarity:.2f} (below threshold {settings.CONFIDENCE_THRESHOLD_RAG:.2f})")

    return {
        "is_low_confidence": is_low_confidence,
        "is_cnn_low": is_cnn_low,
        "is_rag_low": is_rag_low,
        "reasons": reasons,
        "mode": "blended" if is_low_confidence else "strict_rag"
    }

def construct_advisory_prompt(
    disease: str,
    cnn_confidence: float,
    env_data: Dict[str, Any],
    user_question: str | None,
    rag_context: str,
    confidence_eval: Dict[str, Any],
    language: str = "en",
    detected_lang: str = "english"
) -> str:
    """
    Constructs an LLM prompt. If confidence is low, uses a Blended Prompt format.
    Supports Kannada script, Kanglish, and English output directives.
    """
    env_str = ""
    if env_data:
        env_str = "\nLocation & Site Environmental Conditions:\n"
        for k, v in env_data.items():
            env_str += f"- {k}: {v}\n"

    lang_instruction = ""
    if detected_lang in ["kannada_script", "kanglish"] or language == "kn":
        lang_instruction = (
            "\nLANGUAGE DIRECTIVE (MANDATORY):\n"
            "- Provide the entire response in fluent, respectful Kannada written in native Kannada script (ಕನ್ನಡ ಲಿಪಿ).\n"
            "- Mention chemical or fertilizer names with English terms in parentheses where helpful (e.g., ಬೋರ್ಡೋ ಮಿಶ್ರಣ (Bordeaux Mixture 1%))."
        )
    else:
        lang_instruction = "\nLANGUAGE DIRECTIVE: Provide the response in clear, encouraging English suitable for coffee planters."

    if confidence_eval["is_low_confidence"]:
        # BLENDED PROMPT
        reasons_text = "; ".join(confidence_eval["reasons"])
        prompt = f"""\
You are an expert agronomist providing assistance to a coffee farmer.

[NOTICE - LOW CERTAINTY SAFEGUARD]
{reasons_text}
Because of potential uncertainty in the initial diagnosis or knowledge retrieval, please generate a BLENDED response combining retrieved knowledge base insights with your core pre-trained agricultural expertise.

Disease Diagnosis : {disease} (Confidence: {cnn_confidence:.1f}%)
{env_str}
Farmer's Specific Question: {user_question if user_question else "None provided"}

Retrieved Knowledge Base Context:
{rag_context}

Please structure your response with:
1. **Diagnosis & Caution Note**: Clearly state the diagnosis ({disease}) but advise verifying symptoms.
2. **Environmental Assessment**: How current site conditions affect disease progression.
3. **Immediate Action Steps**: Safe, effective organic/chemical treatments.
4. **General Preventive Advice**: Soil health, pruning, and shade management.
5. **Clear Guidance**: Concise, actionable steps spoken directly to the farmer.
{lang_instruction}"""
    else:
        # STRICT RAG PROMPT
        prompt = f"""\
You are an expert agronomist specializing in coffee crop health.

CNN Diagnosis : {disease} ({cnn_confidence:.1f}% confidence)
{env_str}
Farmer's Question: {user_question if user_question else "None"}

Retrieved Knowledge Base Context:
{rag_context}

Provide a comprehensive, authoritative advisory covering:
1. Disease symptoms and identification
2. How the current environmental conditions contribute to risk
3. Recommended immediate treatment options
4. Preventive measures and long-term agronomic care

Be direct, clear, and encouraging.
{lang_instruction}"""

    return prompt
