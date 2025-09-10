from flask import Flask, request, jsonify
import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

app = Flask(__name__)

class ModelManager:
    def __init__(self):
        self.model = None
        self.features = None
        
    def train_model(self, csv_path):
        df = pd.read_csv(csv_path)
        X = df.drop('target', axis=1)
        y = df['target']
        self.features = X.columns.tolist()
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model = RandomForestClassifier(random_state=42)
        self.model.fit(X_train, y_train)
        
        accuracy = self.model.score(X_test, y_test)
        joblib.dump(self.model, "model.pkl")
        return accuracy
    
    def load_model(self):
        if os.path.exists("model.pkl"):
            self.model = joblib.load("model.pkl")
            return True
        return False
    
    def predict(self, data):
        if self.model is None:
            return None
        return self.model.predict([data])[0], self.model.predict_proba([data])[0]

manager = ModelManager()

@app.route('/train', methods=['POST'])
def train():
    csv_file = request.json.get('csv_path', 'diseases.csv')
    try:
        accuracy = manager.train_model(csv_file)
        return jsonify({"status": "success", "accuracy": accuracy})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/predict', methods=['POST'])
def predict():
    if manager.model is None and not manager.load_model():
        return jsonify({"status": "error", "message": "No model available"})
    
    data = request.json.get('data')
    try:
        prediction, probability = manager.predict(data)
        return jsonify({
            "prediction": int(prediction),
            "probability": probability.tolist(),
            "risk": "High" if prediction == 1 else "Low"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/status', methods=['GET'])
def status():
    model_exists = manager.model is not None or os.path.exists("model.pkl")
    return jsonify({"model_ready": model_exists})

if __name__ == '__main__':
    manager.load_model()
    app.run(debug=True, port=5000)