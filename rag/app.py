import os
import markdown
from flask import Flask, render_template, request, jsonify
import pipeline
import demo as demo_module

app = Flask(__name__)

# Initialize the vector store once on startup
store = pipeline.get_store()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/query", methods=["GET", "POST"])
def query():
    if request.method == "POST":
        user_query = request.json.get("query")
        provider = request.json.get("provider", "gemini")
        if not user_query:
            return jsonify({"error": "No query provided"}), 400
        
        results = pipeline.answer_question(user_query, store, provider)
        return jsonify([
            {
                "answer": r.answer,
                "confidence": r.confidence,
                "sources": r.sources
            } for r in results
        ])
    return render_template("query.html")

@app.route("/cnn")
def cnn():
    return render_template("cnn.html")

@app.route("/demo")
def demo_page():
    return render_template(
        "demo.html", 
        cnn_scenarios=demo_module.CNN_SCENARIOS,
        query_scenarios=demo_module.QUESTIONS
    )

@app.route("/run_demo", methods=["POST"])
def run_demo():
    data = request.json
    mode = data.get("mode") # "cnn" or "query"
    index = data.get("index") # int or "all"
    provider = data.get("provider", "gemini")
    
    results = []
    if mode == "cnn":
        scenario_indices = [index] if isinstance(index, int) else range(len(demo_module.CNN_SCENARIOS))
        for i in scenario_indices:
            res_list = demo_module.run_cnn_mode(store, i, silent=True, provider=provider)
            for res_obj in res_list:
                inp = res_obj["input"]
                res = res_obj["result"]
                serialized = {
                    "scenario_id": i,
                    "disease": inp.disease or "None (Healthy)",
                    "confidence": f"{inp.confidence*100:.1f}%",
                    "env": inp.env_data,
                    "question": inp.user_question,
                    "answer": res.answer,
                    "confidence_rag": res.confidence,
                    "sources": res.sources
                }
                results.append(serialized)
            
    elif mode == "query":
        question_indices = [index] if isinstance(index, int) else range(len(demo_module.QUESTIONS))
        for i in question_indices:
            res_list = demo_module.run_query_mode(store, i, silent=True, provider=provider)
            # res_list contains multiple results
            for result_obj in res_list:
                res = result_obj["result"]
                serialized = {
                    "scenario_id": i,
                    "question": result_obj["question"],
                    "answer": res.answer,
                    "confidence": res.confidence,
                    "sources": res.sources
                }
                results.append(serialized)
            
    return jsonify(results)

@app.route("/readme")
def readme():
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()
    html_content = markdown.markdown(content, extensions=['fenced_code', 'tables'])
    return render_template("readme.html", content=html_content)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
