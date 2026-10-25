"""
test_voice_toggles.py
=====================
Unit and integration tests verifying granular .env toggle controls for:
1. Master Local STT toggle (ENABLE_LOCAL_STT)
2. Granular English Local STT toggle (ENABLE_LOCAL_ENGLISH_STT)
3. Granular Kannada Local STT toggle (ENABLE_LOCAL_KANNADA_STT)
"""

import io
from unittest.mock import patch, MagicMock
from app.core.config import settings
from app.services.voice_service import transcribe_audio

DUMMY_WAV = b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80>\x00\x00\x00}\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00"

class TestVoiceSTTToggles:
    def test_settings_properties_logic(self):
        """TC-STT-01: Verifies is_local_kannada_stt_enabled and is_local_english_stt_enabled boolean logic."""
        orig_master = settings.ENABLE_LOCAL_STT
        orig_en = settings.ENABLE_LOCAL_ENGLISH_STT
        orig_kn = settings.ENABLE_LOCAL_KANNADA_STT

        try:
            # Case 1: All enabled
            settings.ENABLE_LOCAL_STT = True
            settings.ENABLE_LOCAL_ENGLISH_STT = True
            settings.ENABLE_LOCAL_KANNADA_STT = True
            assert settings.is_local_english_stt_enabled is True
            assert settings.is_local_kannada_stt_enabled is True

            # Case 2: English disabled, Kannada enabled
            settings.ENABLE_LOCAL_ENGLISH_STT = False
            settings.ENABLE_LOCAL_KANNADA_STT = True
            assert settings.is_local_english_stt_enabled is False
            assert settings.is_local_kannada_stt_enabled is True

            # Case 3: Kannada disabled, English enabled
            settings.ENABLE_LOCAL_ENGLISH_STT = True
            settings.ENABLE_LOCAL_KANNADA_STT = False
            assert settings.is_local_english_stt_enabled is True
            assert settings.is_local_kannada_stt_enabled is False

            # Case 4: Master toggle disabled (both should become False regardless of granular settings)
            settings.ENABLE_LOCAL_STT = False
            settings.ENABLE_LOCAL_ENGLISH_STT = True
            settings.ENABLE_LOCAL_KANNADA_STT = True
            assert settings.is_local_english_stt_enabled is False
            assert settings.is_local_kannada_stt_enabled is False

        finally:
            settings.ENABLE_LOCAL_STT = orig_master
            settings.ENABLE_LOCAL_ENGLISH_STT = orig_en
            settings.ENABLE_LOCAL_KANNADA_STT = orig_kn

    @patch("app.services.voice_service.LocalEnglishSTTManager")
    @patch("app.services.voice_service.IndicConformerSTTManager")
    def test_english_local_disabled_bypasses_model(self, mock_indic, mock_english):
        """TC-STT-02: Verifies that when ENABLE_LOCAL_ENGLISH_STT is False, LocalEnglishSTTManager is never instantiated."""
        orig_en = settings.ENABLE_LOCAL_ENGLISH_STT
        orig_master = settings.ENABLE_LOCAL_STT
        try:
            settings.ENABLE_LOCAL_STT = True
            settings.ENABLE_LOCAL_ENGLISH_STT = False

            with patch("groq.Groq") as mock_groq_class:
                mock_client = MagicMock()
                mock_client.audio.transcriptions.create.return_value = MagicMock(text="Cloud English Fallback Text")
                mock_groq_class.return_value = mock_client

                res = transcribe_audio(DUMMY_WAV, "sample.wav", target_lang="en")

                # Local English STT manager should NOT have been called
                mock_english.get_instance.assert_not_called()
                assert res.get("provider") == "groq-whisper"
                assert res.get("text") == "Cloud English Fallback Text"
        finally:
            settings.ENABLE_LOCAL_ENGLISH_STT = orig_en
            settings.ENABLE_LOCAL_STT = orig_master

    @patch("app.services.voice_service.LocalEnglishSTTManager")
    @patch("app.services.voice_service.IndicConformerSTTManager")
    def test_kannada_local_disabled_bypasses_model(self, mock_indic, mock_english):
        """TC-STT-03: Verifies that when ENABLE_LOCAL_KANNADA_STT is False, IndicConformerSTTManager is never instantiated."""
        orig_kn = settings.ENABLE_LOCAL_KANNADA_STT
        orig_master = settings.ENABLE_LOCAL_STT
        try:
            settings.ENABLE_LOCAL_STT = True
            settings.ENABLE_LOCAL_KANNADA_STT = False

            with patch("groq.Groq") as mock_groq_class:
                mock_client = MagicMock()
                mock_client.audio.transcriptions.create.return_value = MagicMock(text="ಕ್ಲೌಡ್ ಕನ್ನಡ ಪಠ್ಯ")
                mock_groq_class.return_value = mock_client

                res = transcribe_audio(DUMMY_WAV, "sample.wav", target_lang="kn")

                # Local IndicConformer STT manager should NOT have been called
                mock_indic.get_instance.assert_not_called()
                assert res.get("provider") == "groq-whisper"
                assert res.get("text") == "ಕ್ಲೌಡ್ ಕನ್ನಡ ಪಠ್ಯ"
        finally:
            settings.ENABLE_LOCAL_KANNADA_STT = orig_kn
            settings.ENABLE_LOCAL_STT = orig_master

    @patch("app.services.voice_service.LocalEnglishSTTManager")
    @patch("app.services.voice_service.IndicConformerSTTManager")
    def test_master_local_disabled_bypasses_both_models(self, mock_indic, mock_english):
        """TC-STT-04: Verifies that when ENABLE_LOCAL_STT is False, neither English nor Kannada local models are instantiated."""
        orig_master = settings.ENABLE_LOCAL_STT
        try:
            settings.ENABLE_LOCAL_STT = False

            with patch("groq.Groq") as mock_groq_class:
                mock_client = MagicMock()
                mock_client.audio.transcriptions.create.return_value = MagicMock(text="Direct Cloud Bypass")
                mock_groq_class.return_value = mock_client

                # Test English
                res_en = transcribe_audio(DUMMY_WAV, "test_en.wav", target_lang="en")
                mock_english.get_instance.assert_not_called()
                assert res_en.get("provider") == "groq-whisper"

                # Test Kannada
                res_kn = transcribe_audio(DUMMY_WAV, "test_kn.wav", target_lang="kn")
                mock_indic.get_instance.assert_not_called()
                assert res_kn.get("provider") == "groq-whisper"
        finally:
            settings.ENABLE_LOCAL_STT = orig_master
