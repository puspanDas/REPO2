# Healthcare MediaAnalytics Pro

A comprehensive medical report analysis system that extracts and analyzes key information from medical documents.

## Features

- **Multi-format Support**: Analyze PDF, DOCX, and TXT medical reports
- **Patient Information Extraction**: Automatically extract patient demographics
- **Vital Signs Analysis**: Parse and display vital signs data
- **Medication Tracking**: Identify prescribed medications
- **Diagnosis Detection**: Extract medical diagnoses and conditions
- **Lab Results Processing**: Parse laboratory test results
- **Risk Factor Identification**: Identify potential health risk factors
- **Recommendations Extraction**: Extract medical recommendations
- **Modern Web Interface**: User-friendly drag-and-drop interface

## Installation

1. **Clone or download the project**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Start the application**:
   ```bash
   python app.py
   ```

2. **Open your browser** and navigate to `http://localhost:5000`

3. **Upload a medical report** or paste text directly into the interface

4. **View the analysis results** including:
   - Patient information
   - Vital signs
   - Medications
   - Diagnoses
   - Lab results
   - Risk factors
   - Recommendations

## Supported File Formats

- **PDF**: Medical reports in PDF format
- **DOCX**: Microsoft Word documents
- **TXT**: Plain text files

## File Size Limit

Maximum file size: 16MB

## Security Features

- Secure file handling with filename sanitization
- Temporary file cleanup after processing
- File type validation

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **File Processing**: PyPDF2, python-docx
- **Text Analysis**: Regular expressions for medical data extraction

## Sample Medical Report Format

The system works best with structured medical reports containing:

```
Patient Name: John Doe
Age: 45
Gender: Male
BP: 120/80
HR: 72
Temperature: 98.6
Diagnosis: Hypertension
Medication: Lisinopril
Glucose: 95
Cholesterol: 180
Recommendation: Follow up in 3 months
```

## Development

To extend the system:

1. Add new extraction patterns in the analysis functions
2. Modify the HTML template for additional UI elements
3. Update the analysis logic for new medical data types

## License

This project is for educational and demonstration purposes.