from typing import Dict, Any, Optional, List

def build_chat_prompt(
    user_question: str,
    rag_context: str,
    attached_image_info: Optional[Dict[str, Any]] = None,
    env_data: Optional[Dict[str, Any]] = None,
    language: str = "en",
    detected_lang: str = "english",
    history: Optional[List[Dict[str, str]]] = None
) -> str:
    """
    Builds a multi-turn conversation-aware agronomic prompt.
    """
    env_section = ""
    if env_data and env_data.get("location_status") != "Disallowed / Unavailable":
        env_section = "\nCurrent Site Environment Factors:\n"
        for k, v in env_data.items():
            env_section += f"- {k}: {v}\n"

    image_section = ""
    if attached_image_info:
        image_section = f"\n[ATTACHED LEAF IMAGE DIAGNOSIS]\nDisease Detected: {attached_image_info.get('disease')}\nConfidence: {attached_image_info.get('confidence')}%\n"

    history_section = ""
    if history and len(history) > 0:
        history_section = "\n[CONVERSATION HISTORY - PREVIOUS MESSAGES IN THIS CHAT]\n"
        for h in history[-8:]:  # Include last 8 conversational turns
            role_label = "Farmer" if h.get("role") == "user" else "PlantIQ Assistant"
            history_section += f"{role_label}: {h.get('content', '')}\n"

    is_kannada_intent = (detected_lang in ["kannada_script", "kanglish"] or language == "kn")

    if is_kannada_intent:
        lang_instruction = (
            "\nLANGUAGE DIRECTIVE (CRITICAL - MANDATORY):\n"
            "- The farmer's message is in Kannada or Kanglish (Kannada written using English alphabet).\n"
            "- You MUST write your entire answer in natural, fluent, respectful Kannada in Kannada script (ಕನ್ನಡ ಲಿಪಿ).\n"
            "- Technical, chemical, or fertilizer names can include English terms in parentheses (e.g., ಬೋರ್ಡೋ ಮಿಶ್ರಣ (Bordeaux mixture))."
        )
    else:
        lang_instruction = "\nLANGUAGE DIRECTIVE: Write your response in clear, concise, professional English."

    prompt = f"""\
You are PlantIQ Assistant, an expert AI agronomist specialized in South Indian coffee plantations (Arabica & Robusta in Chikmagalur, Coorg, Hassan, etc.).
{image_section}
{env_section}
Retrieved Knowledge Base Reference:
{rag_context}
{history_section}
Farmer's Current Message: "{user_question}"

CORE INSTRUCTIONS (STRICT RELEVANCE & CONVERSATIONAL MEMORY):
1. **Multi-Turn Context & Memory**: Use the Conversation History to understand pronouns, follow-ups, requests to translate, clarify, or expand on earlier messages (e.g., "convert the above response to english", "what about organic alternatives?", "why?").
2. **Relevance is Mandatory**: Answer ONLY what the farmer specifically asked about.
   - If the farmer asks to translate or explain a previous message, do so directly using the conversation history.
   - If the farmer asks about environmental conditions or growth requirements, explain ONLY those conditions. Do NOT dump unsolicited disease names, fungicides, or pesticide lists unless asked.
   - If the farmer sends only a location name, greeting, or short vague phrase (e.g. "ಚಿಕ್ಕಬೆಗುರು", "Hello"), give a warm 1-2 sentence greeting acknowledging their location and asking specifically what advice they need for their coffee crops.
3. **Precision & Structure**: Keep points clean with clear bullet points.
{lang_instruction}"""

    return prompt
