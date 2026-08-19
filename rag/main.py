"""
main.py — Coffee RAG System
============================
Usage
-----
  python main.py demo cnn              # run all CNN scenarios
  python main.py demo cnn 2            # run CNN scenario index 2
  python main.py demo query            # run all query scenarios
  python main.py demo query 1          # run query scenario index 1
  python main.py demo all              # run everything

  python main.py ask "your question"   # live plain question
  python main.py disease               # live CNN mode (edit values in main.py)

Index is loaded automatically from INDEX_FOLDER (.env).
If the index does not exist it is built from PDF_FOLDER and saved.
If the PDF folder is empty a warning is printed and Gemini answers on its own.
"""

import sys
import logging
import pipeline
import demo as demo_module

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")


def main():
    args = sys.argv[1:]

    if not args:
        print(__doc__)
        sys.exit(0)

    # Bootstrap: load or build the FAISS index once
    store = pipeline.get_store()

    cmd = args[0]

    # ── demo mode ──────────────────────────────────────────────────────────
    if cmd == "demo":
        sub = args[1] if len(args) > 1 else "all"
        idx = int(args[2]) if len(args) > 2 else None

        if sub in ("cnn", "all"):
            scenarios = (
                [idx] if idx is not None
                else range(len(demo_module.CNN_SCENARIOS))
            )
            for i in scenarios:
                demo_module.run_cnn_mode(store, i)

        if sub in ("query", "all"):
            scenarios = (
                [idx] if idx is not None
                else range(len(demo_module.QUESTIONS))
            )
            for i in scenarios:
                demo_module.run_query_mode(store, i)

        if sub not in ("cnn", "query", "all"):
            print(f"Unknown demo sub-command '{sub}'. Use: cnn | query | all")
            sys.exit(1)

    # ── live ask mode ───────────────────────────────────────────────────────
    elif cmd == "ask":
        if len(args) < 2:
            print('Usage: python main.py ask "your question"')
            sys.exit(1)
        question = " ".join(args[1:])
        print(f"\nQuestion: {question}")
        result = pipeline.answer_question(question, store)
        demo_module._print_result(result)

    # ── live disease mode ───────────────────────────────────────────────────
    elif cmd == "disease":
        # Replace with real CNN + sensor output in production
        inp = pipeline.DiseaseInput(
            disease="Coffee Leaf Rust (Hemileia vastatrix)",
            confidence=0.94,
            is_healthy=False,
            temperature_c=22.5, humidity_pct=87.0, rainfall_mm=180.0,
            soil_ph=5.8, soil_type="loamy", elevation_m=1200.0,
            user_question=None,
        )
        result = pipeline.disease_advisory(inp, store)
        print(f"\nDisease: {inp.disease}  ({inp.confidence*100:.0f}%)")
        demo_module._print_result(result)

    else:
        print(f"Unknown command '{cmd}'. Run without arguments to see help.")
        sys.exit(1)


if __name__ == "__main__":
    main()
