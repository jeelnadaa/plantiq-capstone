from typing import Dict, Any, Optional

def build_chat_prompt(
    user_question: str,
    rag_context: str,
    attached_image_info: Optional[Dict[str, Any]] = None,
    env_data: Optional[Dict[str, Any]] = None,
    language: str = "en"
) -> str:
    """
    Builds a prompt for the chat assistant in English or Kannada.
    """
    env_section = ""
    if env_data and env_data.get("location_status") != "Disallowed / Unavailable":
        env_section = "\nCurrent Site Environment:\n"
        for k, v in env_data.items():
            env_section += f"- {k}: {v}\n"
    else:
        env_section = "\nLocation Status: Disallowed/Unavailable. (If location is missing, gently prompt farmer if they know their region's weather/temp/pH, but continue answering regardless).\n"

    image_section = ""
    if attached_image_info:
        image_section = f"\n[ATTACHED LEAF IMAGE DIAGNOSIS]\nDisease Detected: {attached_image_info.get('disease')}\nConfidence: {attached_image_info.get('confidence')}%\n"

    lang_instruction = ""
    if language == "kn":
        lang_instruction = "\nIMPORTANT: You must respond in Kannada (ಕನ್ನಡ). Use clear, respectful language suitable for a farmer."

    prompt = f"""\
You are PlantIQ Assistant, an expert AI agronomist specialized in coffee crops.
{image_section}
{env_section}
Knowledge Base Context:
{rag_context}

Farmer's Message: {user_question}

Instruction:
1. Answer the farmer's question directly, clearly, and concisely.
2. Use the Knowledge Base context where relevant.
3. If no location data is present, gently invite the farmer to share their location or local weather for more tailored advice, but do NOT refuse to answer.
{lang_instruction}"""

    return prompt
