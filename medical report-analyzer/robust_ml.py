import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import cross_val_score
import pickle
import re
from data_manager import DataManager

class RobustMLSystem:
    def __init__(self):
        self.data_manager = DataManager()
        self.vectorizer = TfidfVectorizer(max_features=200, stop_words='english', ngram_range=(1,2))
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        
        # Models
        self.risk_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.diagnosis_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.anomaly_model = None
        
        self.is_trained = False
        self.load_models()
    
    def extract_comprehensive_features(self, text, health_metrics=None):
        features = {}
        
        # Text features
        if text:
            # Medical keywords
            medical_keywords = ['pain', 'fever', 'nausea', 'fatigue', 'headache', 'cough', 'diabetes', 'hypertension']
            for keyword in medical_keywords:
                features[f'has_{keyword}'] = 1 if keyword.lower() in text.lower() else 0
            
            # Numerical extractions
            features['bp_systolic'] = self._extract_number(text, r'(?:BP|Blood Pressure):\s*(\d+)/\d+')
            features['bp_diastolic'] = self._extract_number(text, r'(?:BP|Blood Pressure):\s*\d+/(\d+)')
            features['heart_rate'] = self._extract_number(text, r'(?:HR|Heart Rate):\s*(\d+)')
            features['temperature'] = self._extract_number(text, r'(?:Temperature|Temp):\s*(\d+\.?\d*)')
            features['glucose'] = self._extract_number(text, r'(?:Glucose|Blood Sugar):\s*(\d+\.?\d*)')
            features['age'] = self._extract_number(text, r'(?:Age):\s*(\d+)')
            
            # Text statistics
            features['word_count'] = len(text.split())
            features['sentence_count'] = len(text.split('.'))
        
        # Health metrics features
        if health_metrics:
            features.update(health_metrics)
            if 'height' in health_metrics and 'weight' in health_metrics:
                height_m = health_metrics['height'] / 100
                features['bmi'] = health_metrics['weight'] / (height_m ** 2)
        
        return features
    
    def _extract_number(self, text, pattern):
        match = re.search(pattern, text, re.IGNORECASE)
        return float(match.group(1)) if match else 0.0
    
    def store_and_analyze(self, user_id, data_type, raw_data, health_metrics=None, file_path=None):
        # Extract features
        features = self.extract_comprehensive_features(raw_data, health_metrics)
        
        # Store in database
        data_id = self.data_manager.store_user_data(
            user_id, data_type, raw_data, features, file_path, health_metrics
        )
        
        # Analyze if models are trained
        analysis_results = {}
        if self.is_trained:
            analysis_results = self.predict_comprehensive(features, raw_data)
            
            # Store analysis results
            self.data_manager.store_analysis_result(
                data_id, 'ml_prediction', analysis_results, 
                analysis_results.get('confidence', 0.0)
            )
        
        return {
            'data_id': data_id,
            'features': features,
            'analysis': analysis_results
        }
    
    def train_models(self, manual_labels=None):
        # Get all stored data
        training_data = self.data_manager.get_all_training_data()
        
        if len(training_data) < 5:
            return False
        
        # Prepare training data
        texts, features_list, labels = [], [], []
        for raw_data, extracted_features, results in training_data:
            if extracted_features:
                features = eval(extracted_features) if isinstance(extracted_features, str) else extracted_features
                features_list.append(list(features.values()))
                texts.append(raw_data)
                
                if results:
                    result_dict = eval(results) if isinstance(results, str) else results
                    labels.append(result_dict)
        
        if len(features_list) < 5:
            return False
        
        # Train models
        X_features = np.array(features_list)
        X_features = self.scaler.fit_transform(X_features)
        
        # Text vectorization
        if texts:
            X_text = self.vectorizer.fit_transform(texts)
            X_combined = np.hstack([X_features, X_text.toarray()])
        else:
            X_combined = X_features
        
        # Train risk prediction model
        if labels and all('risk_score' in label for label in labels):
            y_risk = [label['risk_score'] for label in labels]
            self.risk_model.fit(X_combined, y_risk)
        
        # Train diagnosis model
        if labels and all('diagnosis' in label for label in labels):
            diagnoses = [label['diagnosis'] for label in labels]
            if len(set(diagnoses)) > 1:
                y_diag = self.label_encoder.fit_transform(diagnoses)
                self.diagnosis_model.fit(X_combined, y_diag)
        
        self.is_trained = True
        self.save_models()
        return True
    
    def predict_comprehensive(self, features, text=""):
        if not self.is_trained:
            return {'error': 'Models not trained yet'}
        
        # Prepare features
        X_features = np.array([list(features.values())])
        X_features = self.scaler.transform(X_features)
        
        if text:
            X_text = self.vectorizer.transform([text])
            X_combined = np.hstack([X_features, X_text.toarray()])
        else:
            X_combined = X_features
        
        results = {}
        
        # Risk prediction
        try:
            risk_score = self.risk_model.predict(X_combined)[0]
            results['predicted_risk_score'] = max(0, min(10, risk_score))
        except:
            results['predicted_risk_score'] = 0.0
        
        # Diagnosis prediction
        try:
            diagnosis_pred = self.diagnosis_model.predict(X_combined)[0]
            diagnosis_proba = self.diagnosis_model.predict_proba(X_combined)[0]
            results['predicted_diagnosis'] = self.label_encoder.inverse_transform([diagnosis_pred])[0]
            results['confidence'] = max(diagnosis_proba)
        except:
            results['predicted_diagnosis'] = 'Unknown'
            results['confidence'] = 0.0
        
        # Health risk assessment
        results['health_risks'] = self._assess_health_risks(features)
        
        return results
    
    def _assess_health_risks(self, features):
        risks = []
        
        if features.get('bmi', 0) > 30:
            risks.append('Obesity Risk')
        if features.get('bp_systolic', 0) > 140:
            risks.append('Hypertension Risk')
        if features.get('glucose', 0) > 126:
            risks.append('Diabetes Risk')
        if features.get('age', 0) > 65:
            risks.append('Age-related Risk')
        
        return risks
    
    def save_models(self):
        models = {
            'risk_model': self.risk_model,
            'diagnosis_model': self.diagnosis_model,
            'vectorizer': self.vectorizer,
            'scaler': self.scaler,
            'label_encoder': self.label_encoder,
            'is_trained': self.is_trained
        }
        with open('robust_models.pkl', 'wb') as f:
            pickle.dump(models, f)
    
    def load_models(self):
        try:
            with open('robust_models.pkl', 'rb') as f:
                models = pickle.load(f)
                self.risk_model = models['risk_model']
                self.diagnosis_model = models['diagnosis_model']
                self.vectorizer = models['vectorizer']
                self.scaler = models['scaler']
                self.label_encoder = models['label_encoder']
                self.is_trained = models['is_trained']
        except:
            pass
    
    def get_user_analytics(self, user_id):
        user_data = self.data_manager.get_user_data(user_id)
        
        analytics = {
            'total_records': len(user_data),
            'data_types': {},
            'recent_trends': [],
            'risk_progression': []
        }
        
        for record in user_data:
            data_type = record[3]
            analytics['data_types'][data_type] = analytics['data_types'].get(data_type, 0) + 1
        
        return analytics