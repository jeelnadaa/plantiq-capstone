"""
demo.py
=======
Simulates both RAG modes with hard-coded sample data.
Imported and run by main.py — not meant to be executed directly.

  Mode 1 (CNN):    Three disease scenarios the CNN might return.
  Mode 2 (Query):  Three plain farmer questions.
"""

from pipeline import DiseaseInput, VectorStore, disease_advisory, answer_question

# ── Mode 1 scenarios ──────────────────────────────────────────────────────────

CNN_SCENARIOS = [
    DiseaseInput(
        disease="Coffee Leaf Rust (Hemileia vastatrix)",
        confidence=0.94,
        is_healthy=False,
        env_data={
            "Temperature (°C)": 22.5,
            "Humidity (%)": 87.0,
            "Rainfall (mm)": 180.0,
            "Soil pH": 5.8,
            "Soil Type": "loamy",
            "Elevation (m)": 1200.0
        },
        user_question="Which fungicide is safe to use near a stream?",
    ),
    DiseaseInput(
        disease="Coffee Leaf Miner (Leucoptera coffeella)",
        confidence=0.91,
        is_healthy=False,
        env_data={
            "Temperature (°C)": 28.0,
            "Humidity (%)": 60.0,
            "Wind Speed (km/h)": 12.5,
            "UV Index": 8,
            "Soil Type": "sandy loam"
        },
        user_question=None,
    ),
    DiseaseInput(
        disease="Cercospora Blight (Cercospora coffeicola)",
        confidence=0.86,
        is_healthy=False,
        env_data={},  # SENSOR FAILURE SIMULATION: Empty environmental data
        user_question="My soil test shows low nitrogen — what fertilizer should I use?",
    ),
    DiseaseInput(
        disease="",
        confidence=0.99,
        is_healthy=True,
        env_data={
            "Temperature (°C)": 21.0,
            "Humidity (%)": 75.0
        },
    ),
    DiseaseInput(
        disease="Coffee Berry Disease (Colletotrichum kahawae)",
        confidence=0.88,
        is_healthy=False,
        env_data={
            "Temperature (°C)": 19.5,
            "Humidity (%)": 92.0,
            "Atmospheric Pressure": "Moderate",
            "Shade Level": "High"
        },
        user_question=None, # Testing Default Advisory Mode
    ),
]

# ── Mode 2 scenarios ──────────────────────────────────────────────────────────

QUESTIONS = [
    "How do I treat coffee leaf rust organically?",
    "What is the best fertilizer for coffee plants at pH 5.5?",
    "How can I prevent coffee berry disease from spreading?",
]


# ── Runner (called from main.py) ──────────────────────────────────────────────

def run_cnn_mode(store: VectorStore, scenario_index: int = 0, silent: bool = False, provider: str = "gemini"):
    """Run one CNN scenario through the disease advisory pipeline."""
    inp = CNN_SCENARIOS[scenario_index]
    if not silent:
        _print_header(f"MODE 1 — CNN Disease Advisory  (scenario {scenario_index})")
        print(f"  Disease    : {inp.disease or 'None (healthy)'}")
        print(f"  Confidence : {inp.confidence*100:.0f}%")
        if inp.env_data:
            print("  Env Data   :")
            for k, v in inp.env_data.items():
                print(f"    • {k}: {v}")
        else:
            print("  Env Data   : (None provided)")
        print(f"  Question   : {inp.user_question or '(none)'}")
    
    result = disease_advisory(inp, store, provider)
    
    if not silent:
        _print_result(result)
    return [{"input": inp, "result": result}]


def run_query_mode(store: VectorStore, question_index: int = 0, silent: bool = False, provider: str = "gemini"):
    """Run one plain question through the Q&A pipeline."""
    question = QUESTIONS[question_index]
    if not silent:
        _print_header(f"MODE 2 — Farmer Question  (scenario {question_index})")
        print(f"  Q: {question}")
    
    results = answer_question(question, store, provider)
    
    if not silent:
        for r in results:
            _print_result(r)
    return [{"question": question, "result": r} for r in results]


# ── Private helpers ───────────────────────────────────────────────────────────

def _print_header(title: str):
    print("\n" + "=" * 65)
    print(f"  {title}")
    print("=" * 65)


def _print_result(result):
    print()
    print(result.answer)
    if result.sources:
        print("\n--- Sources ---")
        for s in result.sources:
            print(f"  • {s}")
    print()
