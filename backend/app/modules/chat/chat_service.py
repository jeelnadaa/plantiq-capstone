import uuid
import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.modules.rag.vector_store import get_vector_store
from app.modules.rag.pipeline import query_llm
from app.modules.chat.prompts import build_chat_prompt
from app.modules.cnn.detector import get_detector
from app.modules.environment.mock_provider import get_env_service
from app.modules.chat.models import ChatThread, ChatMessage

def get_or_create_thread(
    db: Session,
    thread_id: Optional[str] = None,
    user_id: Optional[int] = None,
    title: str = "New Conversation"
) -> ChatThread:
    """Fetches an existing thread or creates a new persistent thread."""
    if thread_id:
        thread = db.query(ChatThread).filter(ChatThread.id == thread_id).first()
        if thread:
            if user_id and not thread.user_id:
                thread.user_id = user_id
                db.commit()
            return thread

    new_id = thread_id or str(uuid.uuid4())
    thread = ChatThread(
        id=new_id,
        user_id=user_id,
        title=title
    )
    db.add(thread)
    db.commit()
    db.refresh(thread)
    return thread

def get_user_chat_threads(db: Session, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """Returns all chat threads for a user (or recent anonymous threads)."""
    query = db.query(ChatThread)
    if user_id:
        query = query.filter(ChatThread.user_id == user_id)
    else:
        query = query.filter(ChatThread.user_id == None)

    threads = query.order_by(ChatThread.updated_at.desc()).limit(20).all()
    return [
        {
            "thread_id": t.id,
            "title": t.title,
            "updated_at": t.updated_at.isoformat(),
            "message_count": len(t.messages)
        }
        for t in threads
    ]

def get_thread_message_history(db: Session, thread_id: str) -> List[Dict[str, Any]]:
    """Fetches formatted message history for a specific thread."""
    thread = db.query(ChatThread).filter(ChatThread.id == thread_id).first()
    if not thread:
        return []

    res = []
    for m in thread.messages:
        sources = json.loads(m.sources_json or "[]")
        res.append({
            "role": m.role,
            "content": m.content,
            "sources": sources,
            "created_at": m.created_at.isoformat()
        })
    return res

def process_chat_message(
    db: Session,
    session_id: Optional[str],
    user_message: str,
    user_id: Optional[int] = None,
    language: str = "en",
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    image_bytes: Optional[bytes] = None,
    provider: str = "gemini"
) -> Dict[str, Any]:
    """Processes a user message in a chat thread and persists response to SQLite."""
    title = user_message[:35] + "..." if len(user_message) > 35 else user_message
    thread = get_or_create_thread(db, thread_id=session_id, user_id=user_id, title=title)

    attached_image_info = None
    if image_bytes:
        detector = get_detector()
        prediction = detector.predict(image_bytes)
        attached_image_info = prediction

    # Get environmental factors
    env_service = get_env_service()
    env_data = env_service.get_environmental_data(latitude, longitude)

    # RAG Retrieval
    store = get_vector_store()
    retrieval_query = user_message
    if attached_image_info:
        disease = attached_image_info.get("class", "")
        retrieval_query = f"{disease} {user_message}"

    chunks, scores = store.search(retrieval_query, top_k=3)
    rag_context = "\n\n".join([f"[{i+1}] {c.source} p.{c.page}: {c.text}" for i, c in enumerate(chunks)])
    sources = list(set([f"{c.source} (p.{c.page})" for c in chunks]))

    # Construct Prompt
    prompt = build_chat_prompt(
        user_question=user_message,
        rag_context=rag_context,
        attached_image_info=attached_image_info,
        env_data=env_data,
        language=language
    )

    # Query LLM
    assistant_reply = query_llm(prompt, provider=provider)

    # Save User & Assistant Messages to Database
    msg_user = ChatMessage(
        thread_id=thread.id,
        role="user",
        content=user_message
    )
    msg_assistant = ChatMessage(
        thread_id=thread.id,
        role="assistant",
        content=assistant_reply,
        sources_json=json.dumps(sources),
        env_data_json=json.dumps(env_data)
    )
    db.add(msg_user)
    db.add(msg_assistant)

    # Update thread title if first user message
    if len(thread.messages) <= 2:
        thread.title = title
    
    db.commit()

    return {
        "session_id": thread.id,
        "reply": assistant_reply,
        "sources": sources,
        "env_data": env_data,
        "attached_image_info": attached_image_info,
        "language": language
    }

def start_chat_from_cnn_handoff(
    db: Session,
    disease: str,
    confidence: float,
    distribution: Dict[str, float],
    env_data: Dict[str, Any],
    advisory: str,
    user_id: Optional[int] = None
) -> Dict[str, Any]:
    """Creates a new chat session pre-loaded with context from a CNN diagnostic scan."""
    thread_title = f"{disease} Scan Consultation"
    thread = get_or_create_thread(db, user_id=user_id, title=thread_title)

    init_summary = f"Diagnosis Handoff: {disease} ({confidence:.1f}% confidence)."
    assistant_intro = f"I've pre-loaded your leaf scan diagnosis for **{disease}** ({confidence:.1f}% confidence).\n\nInitial Advisory Summary:\n{advisory}\n\nWhat would you like to know more about regarding treatment or care?"

    msg_sys = ChatMessage(
        thread_id=thread.id,
        role="system",
        content=init_summary
    )
    msg_asst = ChatMessage(
        thread_id=thread.id,
        role="assistant",
        content=assistant_intro,
        sources_json="[]"
    )
    db.add(msg_sys)
    db.add(msg_asst)
    db.commit()

    return {
        "session_id": thread.id,
        "messages": get_thread_message_history(db, thread.id),
        "attached_image_info": {
            "class": disease,
            "confidence": confidence,
            "distribution": distribution
        }
    }
