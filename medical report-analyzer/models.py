import pickle
import os
import numpy as np
from sklearn.svm import SVC
from sklearn.linear_model import LinearRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
import json

class MedicalMLModels:
    def __init__(self):
        self.svm_model = SVC(kernel='linear', probability=True)
        self.lr_model = LinearRegression()
        self.vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        self.label_encoder = LabelEncoder()
        self.data_file = 'training_data.json'
        self.models_file = 'trained_models.pkl'
        self.training_data = self.load_training_data()
        self.load_models()
    
    def load_training_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                return json.load(f)
        return {'texts': [], 'risk_scores': [], 'diagnoses': []}
    
    def save_training_data(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.training_data, f)
    
    def load_models(self):
        if os.path.exists(self.models_file):
            with open(self.models_file, 'rb') as f:
                models = pickle.load(f)
                self.svm_model = models.get('svm')
                self.lr_model = models.get('lr')
                self.vectorizer = models.get('vectorizer')
                self.label_encoder = models.get('label_encoder')
    
    def save_models(self):
        models = {
            'svm': self.svm_model,
            'lr': self.lr_model,
            'vectorizer': self.vectorizer,
            'label_encoder': self.label_encoder
        }
        with open(self.models_file, 'wb') as f:
            pickle.dump(models, f)
    
    def add_training_data(self, text, risk_score, diagnosis):
        self.training_data['texts'].append(text)
        self.training_data['risk_scores'].append(float(risk_score))
        self.training_data['diagnoses'].append(diagnosis)
        self.save_training_data()
    
    def train_models(self):
        if len(self.training_data['texts']) < 2:
            return False
        
        # Prepare data
        texts = self.training_data['texts']
        risk_scores = np.array(self.training_data['risk_scores'])
        diagnoses = self.training_data['diagnoses']
        
        # Vectorize text
        X = self.vectorizer.fit_transform(texts)
        
        # Train Linear Regression for risk score prediction
        self.lr_model.fit(X, risk_scores)
        
        # Train SVM for diagnosis classification
        if len(set(diagnoses)) > 1:
            y_encoded = self.label_encoder.fit_transform(diagnoses)
            self.svm_model.fit(X, y_encoded)
        
        self.save_models()
        return True
    
    def predict_risk_score(self, text):
        try:
            X = self.vectorizer.transform([text])
            return float(self.lr_model.predict(X)[0])
        except:
            return 0.0
    
    def predict_diagnosis(self, text):
        try:
            X = self.vectorizer.transform([text])
            prediction = self.svm_model.predict(X)[0]
            return self.label_encoder.inverse_transform([prediction])[0]
        except:
            return "Unknown"
    
    def get_training_stats(self):
        return {
            'total_samples': len(self.training_data['texts']),
            'unique_diagnoses': len(set(self.training_data['diagnoses'])),
            'avg_risk_score': np.mean(self.training_data['risk_scores']) if self.training_data['risk_scores'] else 0
        }