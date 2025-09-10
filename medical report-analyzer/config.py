import os

class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'healthcare-analytics-secret-key-2024'
    
    # File upload configuration
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'doc'}
    
    # Analysis configuration
    ANALYSIS_PATTERNS = {
        'patient_name': [
            r'(?:Patient|Name|Patient Name):\s*([A-Za-z\s]+)',
            r'Name:\s*([A-Za-z\s]+)',
        ],
        'age': [
            r'(?:Age|Years):\s*(\d+)',
            r'Age:\s*(\d+)',
        ],
        'gender': [
            r'(?:Gender|Sex):\s*(Male|Female|M|F)',
        ],
        'blood_pressure': [
            r'(?:BP|Blood Pressure):\s*(\d+/\d+)',
            r'Blood Pressure:\s*(\d+/\d+)',
        ],
        'heart_rate': [
            r'(?:HR|Heart Rate|Pulse):\s*(\d+)',
        ],
        'temperature': [
            r'(?:Temperature|Temp):\s*(\d+\.?\d*)',
        ]
    }
    
    # Medical keywords for risk factor identification
    RISK_KEYWORDS = [
        'hypertension', 'diabetes', 'obesity', 'smoking', 'alcohol',
        'family history', 'high cholesterol', 'heart disease', 'stroke',
        'cancer', 'kidney disease', 'liver disease', 'depression',
        'anxiety', 'asthma', 'copd', 'arthritis'
    ]
    
    # Lab test normal ranges (for reference)
    LAB_RANGES = {
        'glucose': {'normal': (70, 100), 'unit': 'mg/dL'},
        'cholesterol': {'normal': (0, 200), 'unit': 'mg/dL'},
        'hemoglobin': {'normal': (12.0, 15.5), 'unit': 'g/dL'},
        'white_blood_cells': {'normal': (4500, 11000), 'unit': '/μL'},
        'creatinine': {'normal': (0.6, 1.2), 'unit': 'mg/dL'}
    }