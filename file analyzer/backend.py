from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, accuracy_score
import io
import base64

app = Flask(__name__)
CORS(app)

# Global storage for data
data_store = {}

@app.route('/upload', methods=['POST'])
def upload_data():
    try:
        file = request.files['file']
        df = pd.read_csv(file)
        
        # Store data
        data_store['df'] = df
        
        return jsonify({
            'status': 'success',
            'rows': len(df),
            'columns': len(df.columns),
            'column_names': df.columns.tolist(),
            'numeric_columns': df.select_dtypes(include=np.number).columns.tolist()
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/profile', methods=['GET'])
def get_profile():
    if 'df' not in data_store:
        return jsonify({'status': 'error', 'message': 'No data uploaded'}), 400
    
    df = data_store['df']
    
    # Get numeric column ranges
    numeric_ranges = {}
    for col in df.select_dtypes(include=np.number).columns:
        numeric_ranges[col] = {
            'min': float(df[col].min()),
            'max': float(df[col].max()),
            'mean': float(df[col].mean())
        }
    
    profile = {
        'shape': df.shape,
        'dtypes': df.dtypes.astype(str).to_dict(),
        'missing_values': df.isnull().sum().to_dict(),
        'unique_values': df.nunique().to_dict(),
        'numeric_ranges': numeric_ranges
    }
    
    return jsonify({'status': 'success', 'profile': profile})

@app.route('/train', methods=['POST'])
def train_model():
    if 'df' not in data_store:
        return jsonify({'status': 'error', 'message': 'No data uploaded'}), 400
    
    try:
        data = request.json
        df = data_store['df']
        
        target_col = data['target_column']
        feature_cols = data['feature_columns']
        n_trees = data.get('n_trees', 20)
        
        X = df[feature_cols].copy()
        y = df[target_col]
        
        # Encode categorical features
        for col in X.select_dtypes(include='object').columns:
            X[col] = X[col].astype('category').cat.codes
        
        # Detect classification vs regression
        is_classification = y.dtype == 'object' or str(y.dtype).startswith('category')
        if is_classification:
            y = y.astype('category').cat.codes
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        if is_classification:
            model = RandomForestClassifier(n_estimators=n_trees, random_state=42)
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            score = accuracy_score(y_test, y_pred)
            metric_name = 'accuracy'
        else:
            model = RandomForestRegressor(n_estimators=n_trees, random_state=42)
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            score = mean_squared_error(y_test, y_pred)
            metric_name = 'mse'
        
        # Store model
        data_store['model'] = model
        data_store['model_type'] = 'classification' if is_classification else 'regression'
        
        return jsonify({
            'status': 'success',
            'model_type': 'classification' if is_classification else 'regression',
            'score': float(score),
            'metric': metric_name,
            'predictions': y_pred.tolist()[:10]  # First 10 predictions
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/correlations', methods=['GET'])
def get_correlations():
    if 'df' not in data_store:
        return jsonify({'status': 'error', 'message': 'No data uploaded'}), 400
    
    df = data_store['df']
    numeric_cols = df.select_dtypes(include=np.number).columns
    
    if len(numeric_cols) < 2:
        return jsonify({'status': 'error', 'message': 'Need at least 2 numeric columns'}), 400
    
    corr_matrix = df[numeric_cols].corr()
    
    # Get top correlations
    correlations = []
    for i in range(len(corr_matrix.columns)):
        for j in range(i+1, len(corr_matrix.columns)):
            correlations.append({
                'feature1': corr_matrix.columns[i],
                'feature2': corr_matrix.columns[j],
                'correlation': float(corr_matrix.iloc[i, j])
            })
    
    # Sort by absolute correlation
    correlations.sort(key=lambda x: abs(x['correlation']), reverse=True)
    
    return jsonify({
        'status': 'success',
        'correlations': correlations[:10],
        'matrix': corr_matrix.to_dict()
    })

@app.route('/predict', methods=['POST'])
def predict():
    if 'model' not in data_store:
        return jsonify({'status': 'error', 'message': 'No model trained'}), 400
    
    try:
        data = request.json
        input_data = pd.DataFrame([data['features']])
        
        # Encode categorical features (same as training)
        for col in input_data.select_dtypes(include='object').columns:
            input_data[col] = input_data[col].astype('category').cat.codes
        
        model = data_store['model']
        prediction = model.predict(input_data)[0]
        
        return jsonify({
            'status': 'success',
            'prediction': float(prediction),
            'model_type': data_store['model_type']
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Backend is running'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)