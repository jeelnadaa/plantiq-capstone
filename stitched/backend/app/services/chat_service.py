import uuid
import json
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.models.chat import ChatThread, ChatMessage
from app.services.router_service import analyze_and_route_query
from app.services.rag_service import get_rag_service
from app.services.env_service import get_env_service
from app.core.config import settings

def process_chat_message(
    db: Session,
    session_id: Optional[str],
    user_message: str,
    attached_image_name: Optional[str] = None,
    image_bytes: Optional[bytes] = None,
    image_data_url: Optional[str] = None,
    scan_metadata_json: Optional[str] = None,
    disease_context: Optional[str] = None,
    language: str = "en",
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    user_id: Optional[int] = None
) -> Dict[str, Any]:
    if not session_id:
        session_id = str(uuid.uuid4())
        initial_title = user_message[:35] + ("..." if len(user_message) > 35 else "")
        thread = ChatThread(id=session_id, user_id=user_id, title=initial_title)
        db.add(thread)
        db.commit()
    else:
        thread = db.query(ChatThread).filter(ChatThread.id == session_id).first()
        if not thread:
            thread = ChatThread(id=session_id, user_id=user_id, title=user_message[:35])
            db.add(thread)
            db.commit()

    history = [{"role": m.role, "content": m.content} for m in thread.messages]

    # 1. Parse Scan Metadata if passed from History or Scanner
    meta_disease_str = ""
    meta_advisory_str = ""
    meta_env_str = ""
    if scan_metadata_json:
        try:
            scan_meta = json.loads(scan_metadata_json)
            if scan_meta.get("disease"):
                if not disease_context:
                    disease_context = scan_meta["disease"]
                meta_disease_str = f"Disease Identified During Scan: {scan_meta['disease']} ({scan_meta.get('confidence', 95):.1f}% Confidence)"
            if scan_meta.get("advisory"):
                meta_advisory_str = f"\n- Initial Recommended Advisory at Scan Time: {scan_meta['advisory']}"
            if scan_meta.get("env_data") and isinstance(scan_meta["env_data"], dict):
                env_items = [f"  * {k}: {v}" for k, v in scan_meta["env_data"].items() if v and v != "Disallowed / Unavailable"]
                if env_items:
                    meta_env_str = "\n- Microclimate Environmental Conditions Logged During Scan:\n" + "\n".join(env_items)
        except Exception as e:
            print(f"[Chat Service] Scan metadata parse warning: {e}")

    # 2. Run CNN classification if fresh image bytes attached
    attached_image_info = None
    if image_bytes:
        try:
            from app.services.cnn_service import get_detector
            detector = get_detector()
            attached_image_info = detector.predict(image_bytes)
            if not disease_context and attached_image_info:
                disease_context = attached_image_info.get("class")
        except Exception as e:
            print(f"[Chat Service] CNN inference warning: {e}")

    # 3. Live Environmental context
    env_service = get_env_service()
    env_data = env_service.get_environmental_data(latitude, longitude)

    # 4. Linguistic Router
    route_meta = analyze_and_route_query(user_message)
    target_lang = route_meta.get("target_response_language", language)
    is_greeting_or_loc = route_meta.get("is_greeting_or_location_only", False)

    # 5. RAG Retrieval
    rag_service = get_rag_service()
    retrieved_docs = []
    if not is_greeting_or_loc or attached_image_info or disease_context or scan_metadata_json:
        query_kw = route_meta.get("search_query_english") or user_message
        if disease_context:
            query_kw = f"{disease_context} {query_kw}"
        retrieved_docs = rag_service.search(query_kw, top_k=2)

    lang_instruction = (
        "OUTPUT STRICTLY IN NATIVE KANNADA SCRIPT (ಕನ್ನಡ ಲಿಪಿ). Do NOT write Kannada in Latin alphabets."
        if target_lang == "kn" or route_meta.get("detected_script") in ["kannada_script", "kanglish"]
        else "OUTPUT IN CLEAR, CONCISE ENGLISH."
    )

    history_str = ""
    if history:
        history_lines = []
        for h in history[-8:]:
            label = "Farmer" if h["role"] == "user" else "PlantIQ Assistant"
            history_lines.append(f"{label}: {h['content']}")
        history_str = "\n[CONVERSATION HISTORY - PREVIOUS MESSAGES IN THIS THREAD]\n" + "\n".join(history_lines)

    env_str = ""
    if env_data and env_data.get("location_status") != "Disallowed / Unavailable":
        env_lines = [f"- {k}: {v}" for k, v in env_data.items()]
        env_str = "\n[Current Live Site Environmental Conditions]\n" + "\n".join(env_lines)

    # Build image and historical scan context
    image_diagnosis_block = ""
    if attached_image_info:
        cls_name = attached_image_info.get("class", "Cerscospora")
        if "cerscospora" in cls_name.lower() or "cercospora" in cls_name.lower():
            display_disease = "Cercospora Leaf Spot (Brown Eye Spot / Cercospora coffeicola)"
        elif "rust" in cls_name.lower():
            display_disease = "Coffee Leaf Rust (Hemileia vastatrix)"
        elif "phoma" in cls_name.lower():
            display_disease = "Phoma Leaf Spot (Phoma costarricensis)"
        elif "miner" in cls_name.lower():
            display_disease = "Coffee Leaf Miner (Leucoptera coffeella)"
        elif "healthy" in cls_name.lower():
            display_disease = "Healthy Coffee Leaf"
        else:
            display_disease = cls_name

        conf = attached_image_info.get("confidence", 95.0)
        image_diagnosis_block = f"""
[ATTACHED LEAF PHOTO - PLANTIQ COMPUTER VISION RESNET50 DIAGNOSIS]
- Disease Detected in Attached Photo: {display_disease}
- Model Confidence: {conf:.1f}%
- Diagnostic Assessment: The attached coffee leaf photo displays active symptoms characteristic of {display_disease}.
"""
    elif disease_context or attached_image_name:
        image_diagnosis_block = f"""
[ATTACHED LEAF PHOTO CONTEXT]
- Attached Leaf Diagnostic Context: {disease_context or attached_image_name}
"""

    if meta_disease_str or meta_advisory_str or meta_env_str:
        image_diagnosis_block += f"""
[HISTORICAL SCAN METADATA ATTACHED FROM FARMER'S PAST SCAN]
- {meta_disease_str}{meta_advisory_str}{meta_env_str}
"""

    docs_lines = [f"- {d['text']}" for d in retrieved_docs]
    docs_str = "\n".join(docs_lines) if docs_lines else "Standard South Indian coffee agronomic guidelines."

    prompt = f"""You are PlantIQ Assistant, an expert AI agronomist specialized in South Indian coffee plantations (Arabica & Robusta).
{lang_instruction}

{history_str}
{env_str}
{image_diagnosis_block}

[AGRONOMIC MANUAL KNOWLEDGE]
{docs_str}

Farmer's Current Message: "{user_message}"

CRITICAL INSTRUCTIONS:
1. If an attached leaf image or past scan metadata is provided above, YOU ALREADY HAVE THE VISUAL DIAGNOSIS AND ENVIRONMENTAL CONTEXT. NEVER state "I cannot process images" or "Please describe the symptoms".
2. If Historical Scan Metadata (past advisory, recorded microclimate factors like humidity/rainfall/temperature) is provided, incorporate this exact site history into your answers and recommendations!
3. Clearly identify the disease ({disease_context or (attached_image_info and attached_image_info.get('class')) or 'the attached leaf disease'}), describe its visual symptoms, and explain the exact agronomic causes and Central Coffee Research Institute (CCRI) chemical/organic management protocols.
4. Answer directly, concisely, and practically for a field grower.
"""

    reply = rag_service._call_llm(prompt)

    user_msg_record = ChatMessage(
        thread_id=session_id,
        role="user",
        content=user_message,
        attached_image_name=attached_image_name or (attached_image_info and attached_image_info.get("class")),
        image_data_url=image_data_url
    )
    asst_msg_record = ChatMessage(
        thread_id=session_id,
        role="assistant",
        content=reply
    )
    db.add(user_msg_record)
    db.add(asst_msg_record)
    db.commit()

    updated_history = history + [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": reply}
    ]

    return {
        "session_id": session_id,
        "reply": reply,
        "history": updated_history,
        "disease": disease_context or (attached_image_info and attached_image_info.get("class"))
    }
