import uuid
from typing import Dict, Any, List, Optional
from app.modules.rag.vector_store import get_vector_store
from app.modules.rag.pipeline import query_llm
from app.modules.chat.prompts import build_chat_prompt
from app.modules.cnn.detector import get_detector
from app.modules.environment.mock_provider import get_env_service

# In-memory session store (can be persisted to DB)
_CHAT_SESSIONS: Dict[str, Dict[str, Any]] = {}

def get_or_create_session(session_id: Optional[str] = None) -> Dict[str, Any]:
    if not session_id or session_id not in _CHAT_SESSIONS:
        new_id = session_id or str(uuid.uuid4())
        _CHAT_SESSIONS[new_id] = {
            "session_id": new_id,
            "messages": [],
            "attached_image_info": None,
            "hand-off_context": None
        }
        return _CHAT_SESSIONS[new_id]
    return _CHAT_SESSIONS[session_id]

def process_chat_message(
    session_id: str,
    user_message: str,
    language: str = "en",
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    image_bytes: Optional[bytes] = None,
    provider: str = "gemini"
) -> Dict[str, Any]:
    session = get_or_create_session(session_id)
    
    # 1. Handle image attachment if provided directly in chat
    if image_bytes:
        detector = get_detector()
        prediction = detector.predict(image_bytes)
        session["attached_image_info"] = prediction

    # 2. Get environmental factors (allowed vs disallowed)
    env_service = get_env_service()
    env_data = env_service.get_environmental_data(latitude, longitude)

    # 3. RAG Retrieval
    store = get_vector_store()
    retrieval_query = user_message
    if session.get("attached_image_info"):
        disease = session["attached_image_info"].get("class", "")
        retrieval_query = f"{disease} {user_message}"

    chunks, scores = store.search(retrieval_query, top_k=3)
    rag_context = "\n\n".join([f"[{i+1}] {c.source} p.{c.page}: {c.text}" for i, c in enumerate(chunks)])
    sources = list(set([f"{c.source} (p.{c.page})" for c in chunks]))

    # 4. Construct Prompt
    prompt = build_chat_prompt(
        user_question=user_message,
        rag_context=rag_context,
        attached_image_info=session.get("attached_image_info"),
        env_data=env_data,
        language=language
    )

    # 5. Query LLM
    assistant_reply = query_llm(prompt, provider=provider)

    # 6. Save message history
    session["messages"].append({"role": "user", "content": user_message})
    session["messages"].append({
        "role": "assistant",
        "content": assistant_reply,
        "sources": sources,
        "env_data": env_data
    })

    return {
        "session_id": session["session_id"],
        "reply": assistant_reply,
        "sources": sources,
        "env_data": env_data,
        "attached_image_info": session.get("attached_image_info"),
        "language": language
    }

def start_chat_from_cnn_handoff(
    disease: str,
    confidence: float,
    distribution: Dict[str, float],
    env_data: Dict[str, Any],
    advisory: str
) -> Dict[str, Any]:
    """
    Creates a new chat session pre-loaded with context from a CNN diagnostic scan.
    """
    session_id = str(uuid.uuid4())
    session = get_or_create_session(session_id)
    
    session["attached_image_info"] = {
        "class": disease,
        "confidence": confidence,
        "distribution": distribution
    }
    
    # Add initial context system message to session history
    init_summary = f"Diagnosis Handoff: {disease} ({confidence:.1f}% confidence)."
    session["messages"].append({
        "role": "system",
        "content": init_summary
    })
    session["messages"].append({
        "role": "assistant",
        "content": f"I've pre-loaded your leaf scan diagnosis for **{disease}** ({confidence:.1f}% confidence).\n\nInitial Advisory Summary:\n{advisory}\n\nWhat would you like to know more about regarding treatment or care?",
        "sources": []
    })

    return {
        "session_id": session_id,
        "messages": session["messages"],
        "attached_image_info": session["attached_image_info"]
    }
