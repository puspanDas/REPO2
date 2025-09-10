from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import PyPDF2
import docx
from werkzeug.utils import secure_filename
import re
from datetime import datetime
import json
from models import MedicalMLModels
from robust_ml import RobustMLSystem
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize ML models
ml_models = MedicalMLModels()
robust_ml = RobustMLSystem()

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'doc'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def extract_text_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def analyze_medical_report(text):
    analysis = {
        'patient_info': extract_patient_info(text),
        'vital_signs': extract_vital_signs(text),
        'medications': extract_medications(text),
        'diagnoses': extract_diagnoses(text),
        'lab_results': extract_lab_results(text),
        'recommendations': extract_recommendations(text),
        'risk_factors': identify_risk_factors(text),
        'summary': generate_summary(text),
        'ml_predictions': {
            'predicted_risk_score': ml_models.predict_risk_score(text),
            'predicted_diagnosis': ml_models.predict_diagnosis(text)
        },
        'robust_analysis': robust_ml.predict_comprehensive(robust_ml.extract_comprehensive_features(text), text)
    }
    return analysis

def extract_patient_info(text):
    info = {}
    
    # Extract name
    name_pattern = r'(?:Patient|Name|Patient Name):\s*([A-Za-z\s]+)'
    name_match = re.search(name_pattern, text, re.IGNORECASE)
    if name_match:
        info['name'] = name_match.group(1).strip()
    
    # Extract age
    age_pattern = r'(?:Age|Years):\s*(\d+)'
    age_match = re.search(age_pattern, text, re.IGNORECASE)
    if age_match:
        info['age'] = age_match.group(1)
    
    # Extract gender
    gender_pattern = r'(?:Gender|Sex):\s*(Male|Female|M|F)'
    gender_match = re.search(gender_pattern, text, re.IGNORECASE)
    if gender_match:
        info['gender'] = gender_match.group(1)
    
    return info

def extract_vital_signs(text):
    vitals = {}
    
    # Blood pressure
    bp_pattern = r'(?:BP|Blood Pressure):\s*(\d+/\d+)'
    bp_match = re.search(bp_pattern, text, re.IGNORECASE)
    if bp_match:
        vitals['blood_pressure'] = bp_match.group(1)
    
    # Heart rate
    hr_pattern = r'(?:HR|Heart Rate|Pulse):\s*(\d+)'
    hr_match = re.search(hr_pattern, text, re.IGNORECASE)
    if hr_match:
        vitals['heart_rate'] = hr_match.group(1)
    
    # Temperature
    temp_pattern = r'(?:Temperature|Temp):\s*(\d+\.?\d*)'
    temp_match = re.search(temp_pattern, text, re.IGNORECASE)
    if temp_match:
        vitals['temperature'] = temp_match.group(1)
    
    return vitals

def extract_medications(text):
    medications = []
    med_patterns = [
        r'(?:Medication|Medicine|Drug):\s*([A-Za-z\s]+)',
        r'(?:Prescribed|Taking):\s*([A-Za-z\s]+)',
        r'(?:Rx|RX):\s*([A-Za-z\s]+)'
    ]
    
    for pattern in med_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        medications.extend(matches)
    
    return list(set(medications))

def extract_diagnoses(text):
    diagnoses = []
    diag_patterns = [
        r'(?:Diagnosis|Diagnosed with):\s*([A-Za-z\s]+)',
        r'(?:Condition|Disease):\s*([A-Za-z\s]+)',
        r'(?:ICD|ICD-10):\s*([A-Za-z0-9\s\.]+)'
    ]
    
    for pattern in diag_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        diagnoses.extend(matches)
    
    return list(set(diagnoses))

def extract_lab_results(text):
    results = {}
    
    # Common lab values
    lab_patterns = {
        'glucose': r'(?:Glucose|Blood Sugar):\s*(\d+\.?\d*)',
        'cholesterol': r'(?:Cholesterol|Total Cholesterol):\s*(\d+\.?\d*)',
        'hemoglobin': r'(?:Hemoglobin|Hb|HGB):\s*(\d+\.?\d*)',
        'white_blood_cells': r'(?:WBC|White Blood Cells):\s*(\d+\.?\d*)',
        'creatinine': r'(?:Creatinine):\s*(\d+\.?\d*)'
    }
    
    for lab, pattern in lab_patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            results[lab] = match.group(1)
    
    return results

def extract_recommendations(text):
    recommendations = []
    rec_patterns = [
        r'(?:Recommendation|Recommend|Advised):\s*([^\.]+)',
        r'(?:Follow up|Follow-up):\s*([^\.]+)',
        r'(?:Treatment|Therapy):\s*([^\.]+)'
    ]
    
    for pattern in rec_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        recommendations.extend(matches)
    
    return recommendations

def identify_risk_factors(text):
    risk_factors = []
    risk_keywords = [
        'hypertension', 'diabetes', 'obesity', 'smoking', 'alcohol',
        'family history', 'high cholesterol', 'heart disease', 'stroke'
    ]
    
    text_lower = text.lower()
    for keyword in risk_keywords:
        if keyword in text_lower:
            risk_factors.append(keyword.title())
    
    return risk_factors

def generate_summary(text):
    word_count = len(text.split())
    return {
        'word_count': word_count,
        'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'status': 'Analysis Complete'
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file selected'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'})
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Extract text based on file type
        try:
            if filename.lower().endswith('.pdf'):
                text = extract_text_from_pdf(file_path)
            elif filename.lower().endswith('.docx'):
                text = extract_text_from_docx(file_path)
            elif filename.lower().endswith('.txt'):
                text = extract_text_from_txt(file_path)
            else:
                return jsonify({'error': 'Unsupported file type'})
            
            # Store data and analyze
            user_id = request.remote_addr  # Simple user identification
            robust_result = robust_ml.store_and_analyze(user_id, 'file_upload', text, file_path=filename)
            
            # Analyze the medical report
            analysis = analyze_medical_report(text)
            analysis['robust_analysis'] = robust_result['analysis']
            
            # Clean up uploaded file
            os.remove(file_path)
            
            return jsonify({
                'success': True,
                'filename': filename,
                'analysis': analysis
            })
            
        except Exception as e:
            return jsonify({'error': f'Error processing file: {str(e)}'})
    
    return jsonify({'error': 'Invalid file type'})

@app.route('/analyze-text', methods=['POST'])
def analyze_text():
    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'No text provided'})
    
    # Store and analyze with robust ML
    user_id = request.remote_addr
    robust_result = robust_ml.store_and_analyze(user_id, 'text_input', text)
    
    analysis = analyze_medical_report(text)
    analysis['robust_analysis'] = robust_result['analysis']
    
    return jsonify({
        'success': True,
        'analysis': analysis
    })

@app.route('/train-model', methods=['POST'])
def train_model():
    data = request.get_json()
    text = data.get('text', '')
    risk_score = data.get('risk_score', 0)
    diagnosis = data.get('diagnosis', '')
    
    if not text or not diagnosis:
        return jsonify({'error': 'Text and diagnosis required'})
    
    ml_models.add_training_data(text, risk_score, diagnosis)
    success = ml_models.train_models()
    
    return jsonify({
        'success': success,
        'stats': ml_models.get_training_stats()
    })

@app.route('/model-stats', methods=['GET'])
def model_stats():
    return jsonify(ml_models.get_training_stats())

@app.route('/calculate-health-metrics', methods=['POST'])
def calculate_health_metrics():
    data = request.get_json()
    height = float(data.get('height', 0))  # in cm
    weight = float(data.get('weight', 0))  # in kg
    systolic = int(data.get('systolic', 0))
    diastolic = int(data.get('diastolic', 0))
    blood_sugar = float(data.get('blood_sugar', 0))  # mg/dL
    
    # Store health metrics
    user_id = request.remote_addr
    health_metrics = {
        'height': height, 'weight': weight, 'systolic': systolic,
        'diastolic': diastolic, 'blood_sugar': blood_sugar
    }
    robust_result = robust_ml.store_and_analyze(user_id, 'health_metrics', '', health_metrics)
    
    # Calculate BMI
    height_m = height / 100
    bmi = weight / (height_m ** 2)
    
    # BMI Categories
    if bmi < 18.5:
        bmi_category = "Underweight"
        bmi_risk = "Low"
    elif bmi < 25:
        bmi_category = "Normal"
        bmi_risk = "Low"
    elif bmi < 30:
        bmi_category = "Overweight"
        bmi_risk = "Medium"
    else:
        bmi_category = "Obese"
        bmi_risk = "High"
    
    # Blood Pressure Risk
    if systolic < 120 and diastolic < 80:
        bp_category = "Normal"
        bp_risk = "Low"
    elif systolic < 130 and diastolic < 80:
        bp_category = "Elevated"
        bp_risk = "Low"
    elif systolic < 140 or diastolic < 90:
        bp_category = "Stage 1 Hypertension"
        bp_risk = "Medium"
    else:
        bp_category = "Stage 2 Hypertension"
        bp_risk = "High"
    
    # Blood Sugar Risk
    if blood_sugar < 100:
        bs_category = "Normal"
        bs_risk = "Low"
    elif blood_sugar < 126:
        bs_category = "Prediabetes"
        bs_risk = "Medium"
    else:
        bs_category = "Diabetes"
        bs_risk = "High"
    
    # Overall Risk Score (0-10)
    risk_scores = {"Low": 1, "Medium": 5, "High": 9}
    overall_risk = (risk_scores[bmi_risk] + risk_scores[bp_risk] + risk_scores[bs_risk]) / 3
    
    result = {
        'bmi': round(bmi, 1),
        'bmi_category': bmi_category,
        'bmi_risk': bmi_risk,
        'bp_category': bp_category,
        'bp_risk': bp_risk,
        'bs_category': bs_category,
        'bs_risk': bs_risk,
        'overall_risk_score': round(overall_risk, 1),
        'recommendations': get_health_recommendations(bmi_risk, bp_risk, bs_risk),
        'robust_analysis': robust_result['analysis']
    }
    
    return jsonify(result)

@app.route('/train-robust-model', methods=['POST'])
def train_robust_model():
    data = request.get_json()
    user_id = request.remote_addr
    
    # Manual training data
    text = data.get('text', '')
    risk_score = float(data.get('risk_score', 0))
    diagnosis = data.get('diagnosis', '')
    
    # Store as training data
    features = robust_ml.extract_comprehensive_features(text)
    data_id = robust_ml.data_manager.store_user_data(
        user_id, 'manual_training', text, features
    )
    
    # Store manual labels
    robust_ml.data_manager.store_analysis_result(
        data_id, 'manual_training', 
        {'risk_score': risk_score, 'diagnosis': diagnosis}
    )
    
    # Retrain models
    success = robust_ml.train_models()
    
    return jsonify({
        'success': success,
        'message': 'Model training completed' if success else 'Need more training data'
    })

@app.route('/user-analytics/<user_id>', methods=['GET'])
def get_user_analytics(user_id):
    analytics = robust_ml.get_user_analytics(user_id)
    return jsonify(analytics)

def get_health_recommendations(bmi_risk, bp_risk, bs_risk):
    recommendations = []
    if bmi_risk == "High":
        recommendations.append("Consider weight management program")
    if bp_risk in ["Medium", "High"]:
        recommendations.append("Monitor blood pressure regularly")
    if bs_risk in ["Medium", "High"]:
        recommendations.append("Consult doctor about blood sugar levels")
    if not recommendations:
        recommendations.append("Maintain current healthy lifestyle")
    return recommendations

if __name__ == '__main__':
    app.run(debug=True)