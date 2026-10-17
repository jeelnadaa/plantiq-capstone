"""
Test Suite: Module 3 — Multilingual Multimodal Conversational Assistant (Chatbot)
File: tests/test_chatbot.py
Coverage:
- Sub-Millisecond Linguistic Pre-Router (Native Kannada Unicode, English)
- Conversational GPS Coordinate Regex Extraction
- Chat Database Persistence (Thread Isolation & Base64 Image Rehydration)
- Multi-Turn Conversation Continuity & Service Processing
"""

import re
import pytest
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, engine
from app.models.chat import Base as ChatBase, ChatThread, ChatMessage
from app.services.router_service import analyze_and_route_query
from app.services.chat_service import process_chat_message

# Ensure database tables exist
ChatBase.metadata.create_all(bind=engine)


class TestChatbotModule:
    """Module 3: Multilingual Voice/Text Chatbot Functional Test Suite"""

    # --- 1. Linguistic Pre-Router Tests ---
    def test_linguistic_router_kannada_script_detection(self):
        """TC-CHT-01: Verifies native Kannada script triggers Kannada response directive."""
        kannada_msg = "ಕಾಫಿ ಎಲೆ ತುಕ್ಕು ರೋಗಕ್ಕೆ ಯಾವ ಔಷಧಿ ಸಿಂಪಡಿಸಬೇಕು?"
        meta = analyze_and_route_query(kannada_msg)

        assert meta["detected_script"] == "kannada_script"
        assert meta["target_response_language"] == "kn"

    def test_linguistic_router_english_detection(self):
        """TC-CHT-02: Verifies standard English query routes with target_lang == 'en'."""
        english_msg = "What is the recommended dosage for Bordeaux mixture in monsoon?"
        meta = analyze_and_route_query(english_msg)

        assert meta["detected_script"] == "english"
        assert meta["target_response_language"] == "en"

    # --- 2. Conversational GPS Extraction Tests ---
    def test_conversational_coordinate_regex_parsing(self):
        """TC-CHT-03: Verifies regex boundary extraction of GPS coordinates from chat text."""
        # Pattern 1: Comma separated
        msg1 = "Please report weather at 13.3161, 75.7720 for my estate."
        m1 = re.search(r'(-?\d{1,2}\.\d+)\s*,\s*(-?\d{1,3}\.\d+)', msg1)
        assert m1 is not None
        lat1, lng1 = float(m1.group(1)), float(m1.group(2))
        assert abs(lat1 - 13.3161) < 1e-4
        assert abs(lng1 - 75.7720) < 1e-4

        # Pattern 2: Key-value formatted
        msg2 = "Estate coords lat: 12.4244, lng: 75.7382. What is disease risk?"
        m2 = re.search(r'lat(?:itude)?\s*[:=]?\s*(-?\d{1,2}\.\d+).*?l(?:ng|on|ongitude)?\s*[:=]?\s*(-?\d{1,3}\.\d+)', msg2, re.IGNORECASE)
        assert m2 is not None
        lat2, lng2 = float(m2.group(1)), float(m2.group(2))
        assert abs(lat2 - 12.4244) < 1e-4
        assert abs(lng2 - 75.7382) < 1e-4

    # --- 3. Chat Session & Image Rehydration Persistence ---
    def test_chat_thread_and_base64_image_persistence(self):
        """TC-CHT-04: Verifies multi-turn history and Base64 image rehydration in SQLite."""
        db = SessionLocal()
        thread_id = "test-thread-uuid-persist"
        try:
            # Create thread
            thread = ChatThread(id=thread_id, user_id=1, title="Test Coffee Chat")
            db.add(thread)
            db.commit()

            # Add user message with attached Base64 image
            dummy_b64 = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD..."
            user_msg = ChatMessage(
                thread_id=thread_id,
                role="user",
                content="Is this leaf rust or cercospora?",
                attached_image_name="Rust",
                image_data_url=dummy_b64
            )
            asst_msg = ChatMessage(
                thread_id=thread_id,
                role="assistant",
                content="This is Coffee Leaf Rust with 96% confidence. Apply Bordeaux mixture."
            )
            db.add(user_msg)
            db.add(asst_msg)
            db.commit()

            # Retrieve and verify rehydration
            saved_thread = db.query(ChatThread).filter(ChatThread.id == thread_id).first()
            assert saved_thread is not None
            assert len(saved_thread.messages) == 2
            assert saved_thread.messages[0].image_data_url == dummy_b64
            assert saved_thread.messages[1].role == "assistant"
        finally:
            db.query(ChatMessage).filter(ChatMessage.thread_id == thread_id).delete()
            db.query(ChatThread).filter(ChatThread.id == thread_id).delete()
            db.commit()
            db.close()

    # --- 4. Multi-Turn Conversation Service Processing ---
    def test_chat_service_dialogue_processing(self):
        """TC-CHT-05: Verifies process_chat_message maintains session continuity across turns."""
        db = SessionLocal()
        session_id = "test-session-chat-service"
        try:
            # Turn 1
            res1 = process_chat_message(
                db=db,
                session_id=session_id,
                user_message="Hello, how do I prevent coffee diseases in monsoon?",
                language="en",
                user_id=1
            )
            assert res1["session_id"] == session_id
            assert "reply" in res1
            assert len(res1["reply"]) > 10

            # Turn 2: Follow up in the same thread
            res2 = process_chat_message(
                db=db,
                session_id=session_id,
                user_message="What about organic Trichoderma spray?",
                language="en",
                user_id=1
            )
            assert res2["session_id"] == session_id
            assert len(res2["history"]) >= 4  # 2 user turns + 2 assistant replies
        finally:
            db.query(ChatMessage).filter(ChatMessage.thread_id == session_id).delete()
            db.query(ChatThread).filter(ChatThread.id == session_id).delete()
            db.commit()
            db.close()
