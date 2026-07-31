from flask import Flask, request, jsonify, render_template
import os
import markdown
from utils import get_model, predict_image, evaluate_npy_dataset
from utils import get_model, predict_image, evaluate_npy_dataset

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16 Megabyte max size

# Load model globally when starting server
model = get_model(weights_path='best_resnet50_coffee.pth')

@app.route('/')
def index():
    return render_template('index.html', title="Analyze")

@app.route('/evaluate_page')
def evaluate_page():
    return render_template('evaluate.html', title="Model Statistics")

@app.route('/readme')
def readme_page():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    readme_path = os.path.join(current_dir, 'README.md')
    content = ""
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
    
    html_content = markdown.markdown(content, extensions=['fenced_code', 'tables'])
    return render_template('readme.html', title="Documentation", readme_html=html_content)

@app.route('/predict', methods=['POST'])
def predict():
    if 'files[]' not in request.files:
        return jsonify({"error": "No files part in the request"}), 400
        
    files = request.files.getlist('files[]')
    if not files or files[0].filename == '':
        return jsonify({"error": "No selected files"}), 400
        
    results = []
    
    for file in files:
        if file:
            try:
                # Read bytes
                img_bytes = file.read()
                # Predict
                prediction = predict_image(model, img_bytes)
                results.append({
                    "filename": file.filename,
                    "prediction": prediction
                })
            except Exception as e:
                results.append({
                    "filename": file.filename,
                    "error": str(e)
                })
                
    return jsonify({"results": results})

@app.route('/evaluate', methods=['GET'])
def evaluate():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    metrics = evaluate_npy_dataset(model, current_dir)
    return jsonify(metrics)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
