import uuid
import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.modules.rag.vector_store import get_vector_store
from app.modules.rag.pipeline import query_llm
from app.modules.rag.language_router import analyze_and_route_query
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
    """Processes a user message in a chat thread with LLM Pre-Router intelligence."""
    title = user_message[:35] + "..." if len(user_message) > 35 else user_message
    thread = get_or_create_thread(db, thread_id=session_id, user_id=user_id, title=title)

    # 1. Intelligent LLM Pre-Router (Zero hardcoding: detects Kanglish, Kannada, English, and extracts search keywords)
    routed = analyze_and_route_query(user_message, ui_lang_hint=language)
    detected_lang = routed.get("input_script", "english")
    is_greeting_or_loc = routed.get("is_greeting_or_location_only", False)
    english_keywords = routed.get("english_search_query", user_message)

    attached_image_info = None
    if image_bytes:
        detector = get_detector()
        prediction = detector.predict(image_bytes)
        attached_image_info = prediction

    # 2. Get environmental factors
    env_service = get_env_service()
    env_data = env_service.get_environmental_data(latitude, longitude)

    # 3. RAG Retrieval (Only execute if asking a farming question or image is attached)
    rag_context = ""
    sources = []
    if not is_greeting_or_loc or attached_image_info:
        store = get_vector_store()
        retrieval_query = english_keywords or user_message
        if attached_image_info:
            disease = attached_image_info.get("class", "")
            retrieval_query = f"{disease} {retrieval_query}"

        chunks, scores = store.search(retrieval_query, top_k=3)
        rag_context = "\n\n".join([f"[{i+1}] {c.source} p.{c.page}: {c.text}" for i, c in enumerate(chunks)])
        sources = list(set([f"{c.source} (p.{c.page})" for c in chunks]))

    # 4. Extract existing message history for multi-turn conversational memory
    history = [
        {"role": m.role, "content": m.content}
        for m in thread.messages
    ]

    # Construct Prompt with Language Directives and Multi-Turn History
    prompt = build_chat_prompt(
        user_question=user_message,
        rag_context=rag_context,
        attached_image_info=attached_image_info,
        env_data=env_data,
        language=language,
        detected_lang=detected_lang,
        history=history
    )

    # 5. Query LLM
    assistant_reply = query_llm(prompt, provider=provider)

    # 6. Save User & Assistant Messages to Database
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
        "detected_language": detected_lang,
        "attached_image": attached_image_info
    }

def start_chat_from_cnn_handoff(
    db: Session,
    disease: str,
    confidence: float,
    advisory: str,
    user_id: Optional[int] = None,
    language: str = "en",
    distribution: Optional[Dict[str, Any]] = None,
    env_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Initializes a new persistent chat thread pre-seeded with scan context."""
    title = f"Scan: {disease} ({confidence:.0f}%)"
    thread = get_or_create_thread(db, user_id=user_id, title=title)

    init_msg = (
        f"ನಾನು ನಿಮ್ಮ ಕಾಫಿ ಎಲೆಯ ರೋಗ ಪರಿಶೋಧನೆಯನ್ನು ({disease}, {confidence:.0f}% ನಂಬಿಕೆ) ಪರಿಶೀಲಿಸಿದ್ದೇನೆ. "
        "ಚಿಕಿತ್ಸೆ ಅಥವಾ ಹೆಚ್ಚಿನ ವಿವರಗಳ ಬಗ್ಗೆ ನೀವು ಯಾವುದೇ ಪ್ರಶ್ನೆಯನ್ನು ಕೇಳಬಹುದು."
        if language == "kn" else
        f"I have received your coffee leaf diagnosis for {disease} ({confidence:.0f}% confidence). "
        "Feel free to ask any questions about treatment, fungicides, or crop care!"
    )

    msg_assistant = ChatMessage(
        thread_id=thread.id,
        role="assistant",
        content=init_msg
    )
    db.add(msg_assistant)
    db.commit()

    return {
        "session_id": thread.id,
        "messages": [
            {
                "role": "assistant",
                "content": init_msg,
                "sources": [],
                "created_at": msg_assistant.created_at.isoformat()
            }
        ]
    }
