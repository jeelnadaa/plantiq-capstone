"""
terminal_logger.py
==================
PlantIQ Real-Time Pipeline Progress & Diagnostics Terminal Logger.
Provides real-time terminal output tracking CNN inference, Microclimate checks,
3-Stage Hybrid RAG retrieval, LLM advisory synthesis, and Safety Guardrails.
"""

import time
import sys
from typing import Dict, Any, List, Optional

# ANSI Color Codes for Rich Terminal Output
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"
    
    # Foreground
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Bright Foreground
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

def _format_ms(ms: float) -> str:
    if ms >= 1000.0:
        return f"{ms / 1000.0:.2f}s"
    return f"{ms:.1f}ms"

class TerminalProgressTracker:
    """Tracks end-to-end multi-phase ML / RAG pipeline execution in real time."""
    
    @staticmethod
    def log_request_header(operation: str, filename: str = "", user_id: Any = None, language: str = "en"):
        print()
        print(f"{Colors.BRIGHT_GREEN}╔══════════════════════════════════════════════════════════════════════════════════════════╗{Colors.RESET}")
        print(f"{Colors.BRIGHT_GREEN}║{Colors.RESET}  {Colors.BOLD}🌿 PlantIQ Pipeline Operation:{Colors.RESET} {Colors.BRIGHT_WHITE}{operation:<52}{Colors.RESET}{Colors.BRIGHT_GREEN}║{Colors.RESET}")
        meta_info = f"File: {filename or 'Direct Data'} | Lang: {language.upper()} | User: {user_id or 'Guest Planter'}"
        print(f"{Colors.BRIGHT_GREEN}║{Colors.RESET}  {Colors.DIM}{meta_info:<79}{Colors.RESET}{Colors.BRIGHT_GREEN}║{Colors.RESET}")
        print(f"{Colors.BRIGHT_GREEN}╚══════════════════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}")

    @staticmethod
    def log_cache_status(hit: bool, hash_preview: str = ""):
        if hit:
            print(f"  {Colors.BRIGHT_CYAN}⚡ [Deduplication Cache]{Colors.RESET} {Colors.GREEN}HIT!{Colors.RESET} (SHA-256: {hash_preview[:12]}...) - Serving instant cached diagnosis.")
        else:
            print(f"  {Colors.DIM}⚡ [Deduplication Cache]{Colors.RESET} MISS (SHA-256: {hash_preview[:12]}...) - Proceeding with full AI execution pipeline.")

    # ──────────────────────────────────────────────────────────────────────────
    # CNN Leaf Pathology Inference Progress
    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def log_cnn_start(device_name: str):
        print(f"\n  {Colors.BOLD}{Colors.BRIGHT_CYAN}┌── [1/4] CNN Vision Classifier (ResNet-50) ──────────────────────────────────────────┐{Colors.RESET}")
        print(f"  {Colors.BRIGHT_CYAN}│{Colors.RESET} Hardware Target: {Colors.BOLD}{device_name.upper()}{Colors.RESET} (Weights loaded)")

    @staticmethod
    def log_cnn_step(step_idx: int, total_steps: int, description: str, duration_ms: Optional[float] = None):
        dur_str = f" [{_format_ms(duration_ms)}]" if duration_ms is not None else ""
        print(f"  {Colors.BRIGHT_CYAN}│{Colors.RESET}   [{step_idx}/{total_steps}] {description}{Colors.BRIGHT_YELLOW}{dur_str}{Colors.RESET}")

    @staticmethod
    def log_cnn_result(disease: str, confidence: float, distribution: Dict[str, float], total_ms: float):
        badge_color = Colors.BRIGHT_GREEN if confidence >= 75.0 else Colors.BRIGHT_YELLOW
        status_symbol = "✓" if confidence >= 75.0 else "!"
        print(f"  {Colors.BRIGHT_CYAN}│{Colors.RESET}   {badge_color}★ Diagnostic Result: {Colors.BOLD}{disease}{Colors.RESET} {badge_color}({confidence:.1f}% Confidence) [{status_symbol}]{Colors.RESET}")
        
        # Format distribution mini-bars
        dist_strs = []
        for cls_name, prob in sorted(distribution.items(), key=lambda x: x[1], reverse=True)[:3]:
            dist_strs.append(f"{cls_name}: {prob:.1f}%")
        print(f"  {Colors.BRIGHT_CYAN}│{Colors.RESET}   {Colors.DIM}Top probabilities: {', '.join(dist_strs)}{Colors.RESET}")
        print(f"  {Colors.BRIGHT_CYAN}└── [CNN Finished in {_format_ms(total_ms)}] ───────────────────────────────────────────────────┘{Colors.RESET}")

    # ──────────────────────────────────────────────────────────────────────────
    # Microclimate Weather Engine Progress
    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def log_microclimate(env_data: Optional[Dict[str, Any]]):
        if not env_data or env_data.get("location_status") == "Disallowed / Unavailable":
            print(f"\n  {Colors.DIM}🌦️  [Microclimate Engine] Geolocation inactive - Using regional South Indian baseline.{Colors.RESET}")
            return
            
        temp = env_data.get("temperature", "N/A")
        rh = env_data.get("humidity", "N/A")
        rain = env_data.get("rainfall_24h", "0.0mm")
        risk = env_data.get("incubation_risk", "Moderate")
        
        risk_color = Colors.BRIGHT_RED if "high" in str(risk).lower() else (Colors.BRIGHT_YELLOW if "mod" in str(risk).lower() else Colors.BRIGHT_GREEN)
        print(f"\n  {Colors.BOLD}{Colors.BRIGHT_BLUE}🌦️  [Microclimate Engine] Live Site Sensor Readings:{Colors.RESET}")
        print(f"     • Temp: {Colors.BOLD}{temp}{Colors.RESET} | Humidity: {Colors.BOLD}{rh}{Colors.RESET} | 24h Rain: {Colors.BOLD}{rain}{Colors.RESET}")
        print(f"     • Disease Incubation Risk: {risk_color}{Colors.BOLD}{risk}{Colors.RESET}")

    # ──────────────────────────────────────────────────────────────────────────
    # 3-Stage Hybrid RAG Knowledge Retrieval Progress
    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def log_rag_start(query_text: str, topic_filter: Optional[str] = None):
        print(f"\n  {Colors.BOLD}{Colors.BRIGHT_MAGENTA}┌── [2/4] 3-Stage Hybrid RAG Knowledge Retrieval ─────────────────────────────────────┐{Colors.RESET}")
        print(f"  {Colors.BRIGHT_MAGENTA}│{Colors.RESET} Query Enriched: {Colors.DIM}\"{query_text[:65]}...\"{Colors.RESET}")
        if topic_filter:
            print(f"  {Colors.BRIGHT_MAGENTA}│{Colors.RESET} Topic Filter  : {Colors.CYAN}{topic_filter}{Colors.RESET}")

    @staticmethod
    def log_rag_step(stage_num: int, stage_name: str, details: str, duration_ms: Optional[float] = None):
        dur_str = f" [{_format_ms(duration_ms)}]" if duration_ms is not None else ""
        print(f"  {Colors.BRIGHT_MAGENTA}│{Colors.RESET}   [{stage_num}/4] {stage_name}: {details}{Colors.BRIGHT_YELLOW}{dur_str}{Colors.RESET}")

    @staticmethod
    def log_rag_results(retrieved_docs: List[Dict[str, Any]], total_ms: float):
        print(f"  {Colors.BRIGHT_MAGENTA}│{Colors.RESET}   {Colors.BRIGHT_GREEN}Top Retrieved Agronomic Passages:{Colors.RESET}")
        for i, d in enumerate(retrieved_docs[:2], start=1):
            src = d.get("source", "CCRI Manual")
            page = d.get("metadata", {}).get("page", 1)
            score = d.get("score", 0.0)
            preview = d.get("text", "").replace("\n", " ")[:60]
            print(f"  {Colors.BRIGHT_MAGENTA}│{Colors.RESET}     #{i} {Colors.BOLD}[Score: {score:.3f}]{Colors.RESET} {src} (p.{page}) - \"{preview}...\"")
        print(f"  {Colors.BRIGHT_MAGENTA}└── [Hybrid RAG Retrieval Finished in {_format_ms(total_ms)}] ───────────────────────────────┘{Colors.RESET}")

    # ──────────────────────────────────────────────────────────────────────────
    # LLM Advisory Generation & Safety Guardrail Progress
    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def log_llm_start(provider: str, model_name: str, language: str):
        print(f"\n  {Colors.BOLD}{Colors.BRIGHT_YELLOW}┌── [3/4] Agronomic LLM Advisory Synthesis ───────────────────────────────────────────┐{Colors.RESET}")
        print(f"  {Colors.BRIGHT_YELLOW}│{Colors.RESET} LLM Engine: {Colors.BOLD}{provider}{Colors.RESET} ({model_name}) | Target Language: {Colors.BOLD}{language.upper()}{Colors.RESET}")
        print(f"  {Colors.BRIGHT_YELLOW}│{Colors.RESET} Generating authoritative CCRI-grounded prescription...", end="", flush=True)

    @staticmethod
    def log_llm_complete(duration_s: float, answer_preview: str):
        print(f" {Colors.BRIGHT_GREEN}DONE [{duration_s:.2f}s]{Colors.RESET}")
        preview_clean = answer_preview.replace("\n", " ").strip()[:80]
        print(f"  {Colors.BRIGHT_YELLOW}│{Colors.RESET} {Colors.DIM}Response snippet: \"{preview_clean}...\"{Colors.RESET}")

    @staticmethod
    def log_safety_audit(safety_audit: Optional[Dict[str, Any]]):
        if not safety_audit:
            return
        verified = safety_audit.get("verified", True)
        detected = safety_audit.get("detected_dosages", [])
        unverified = safety_audit.get("unverified_dosages", [])
        
        if verified:
            d_str = ", ".join(detected) if detected else "standard ratios"
            print(f"  {Colors.BRIGHT_YELLOW}│{Colors.RESET} 🛡️  {Colors.BRIGHT_GREEN}Safety Guardrail Passed:{Colors.RESET} All dosages strictly match CIBRC guidelines ({d_str})")
        else:
            print(f"  {Colors.BRIGHT_YELLOW}│{Colors.RESET} ⚠️  {Colors.BRIGHT_RED}Safety Flag:{Colors.RESET} Unverified field dosages: {', '.join(unverified)}")
        print(f"  {Colors.BRIGHT_YELLOW}└── [LLM Advisory Generation Complete] ───────────────────────────────────────────────┘{Colors.RESET}")

    # ──────────────────────────────────────────────────────────────────────────
    # Pipeline Summary Badge
    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def log_pipeline_complete(total_time_s: float, cached: bool = False, device: str = "cuda"):
        dev_badge = f"{Colors.BRIGHT_GREEN}GPU ACCELERATED ({device.upper()}){Colors.RESET}" if "cuda" in device.lower() else f"{Colors.YELLOW}CPU{Colors.RESET}"
        cache_badge = f"{Colors.CYAN}CACHED RESULT{Colors.RESET}" if cached else f"{Colors.GREEN}NEW DIAGNOSIS{Colors.RESET}"
        
        print(f"\n  {Colors.BRIGHT_GREEN}★ SUMMARY:{Colors.RESET} [{cache_badge}] in {Colors.BOLD}{total_time_s:.2f}s{Colors.RESET} | Hardware: {dev_badge}")
        print(f"  {Colors.BRIGHT_GREEN}─────────────────────────────────────────────────────────────────────────────────────────{Colors.RESET}\n")

    # ──────────────────────────────────────────────────────────────────────────
    # Multimodal Chat Progress Tracking
    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def log_chat_request(user_message: str, detected_lang: str, has_image: bool, thread_id: str):
        print(f"\n{Colors.BRIGHT_CYAN}╔══════════════════════════════════════════════════════════════════════════════════════════╗{Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}║{Colors.RESET}  {Colors.BOLD}💬 PlantIQ Chat Assistant Request{Colors.RESET}{Colors.BRIGHT_CYAN}{'':<54}║{Colors.RESET}")
        msg_preview = user_message[:70] + ("..." if len(user_message) > 70 else "")
        print(f"{Colors.BRIGHT_CYAN}║{Colors.RESET}  {Colors.BOLD}Query:{Colors.RESET} \"{msg_preview}\"{Colors.BRIGHT_CYAN}{'':<5}║{Colors.RESET}")
        details = f"Lang: {detected_lang.upper()} | Attached Leaf Image: {'Yes (ResNet50)' if has_image else 'No'} | Thread: {thread_id[:8]}..."
        print(f"{Colors.BRIGHT_CYAN}║{Colors.RESET}  {Colors.DIM}{details:<79}{Colors.RESET}{Colors.BRIGHT_CYAN}║{Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}╚══════════════════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}")

    # ──────────────────────────────────────────────────────────────────────────
    # Speech-to-Text Voice Progress Tracking
    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def log_voice_request(filename: str, audio_len_bytes: int, target_lang: str):
        print(f"\n{Colors.BRIGHT_YELLOW}╔══════════════════════════════════════════════════════════════════════════════════════════╗{Colors.RESET}")
        print(f"{Colors.BRIGHT_YELLOW}║{Colors.RESET}  {Colors.BOLD}🎙️ PlantIQ Speech-to-Text Transcription{Colors.RESET}{Colors.BRIGHT_YELLOW}{'':<47}║{Colors.RESET}")
        details = f"Audio: {filename} ({audio_len_bytes / 1024:.1f} KB) | Target Language: {target_lang.upper()}"
        print(f"{Colors.BRIGHT_YELLOW}║{Colors.RESET}  {Colors.DIM}{details:<79}{Colors.RESET}{Colors.BRIGHT_YELLOW}║{Colors.RESET}")
        print(f"{Colors.BRIGHT_YELLOW}╚══════════════════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}")

    @staticmethod
    def log_voice_step(provider: str, device: str, duration_ms: float, transcribed_text: str):
        print(f"  {Colors.BRIGHT_YELLOW}│{Colors.RESET} Provider: {Colors.BOLD}{provider}{Colors.RESET} ({device.upper()}) [{_format_ms(duration_ms)}]")
        print(f"  {Colors.BRIGHT_YELLOW}│{Colors.RESET} Transcribed: {Colors.BRIGHT_WHITE}\"{transcribed_text}\"{Colors.RESET}")
        print(f"  {Colors.BRIGHT_YELLOW}╚══════════════════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}\n")

tracker = TerminalProgressTracker()
