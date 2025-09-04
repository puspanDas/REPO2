import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.express as px
import json

# Backend URL
BACKEND_URL = "http://localhost:5000"

# Page config
st.set_page_config(
    page_title='AI-Powered Data Dashboard',
    page_icon='🤖',
    layout='wide',
    initial_sidebar_state='expanded'
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🤖 AI-Powered Data Dashboard (with Backend)</h1>', unsafe_allow_html=True)

# Check backend health
try:
    health = requests.get(f"{BACKEND_URL}/health", timeout=2)
    if health.status_code == 200:
        st.success("✅ Backend connected")
    else:
        st.error("❌ Backend not responding")
except:
    st.error("❌ Backend not available. Start backend with: python backend.py")

# Sidebar
with st.sidebar:
    st.header('📁 Data Upload')
    uploaded_file = st.file_uploader('Upload CSV file', type=['csv'])
    
    if uploaded_file and st.button('📤 Upload to Backend'):
        try:
            files = {'file': uploaded_file}
            response = requests.post(f"{BACKEND_URL}/upload", files=files)
            
            if response.status_code == 200:
                data = response.json()
                st.success('✅ File uploaded to backend!')
                st.session_state['data_info'] = data
            else:
                st.error('❌ Upload failed')
        except Exception as e:
            st.error(f'❌ Error: {e}')

# Main content
if 'data_info' in st.session_state:
    data_info = st.session_state['data_info']
    
    # Dataset metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric('📊 Total Rows', f"{data_info['rows']:,}")
    with col2:
        st.metric('📈 Total Columns', data_info['columns'])
    with col3:
        st.metric('🔢 Numeric Columns', len(data_info['numeric_columns']))
    with col4:
        st.metric('📝 Text Columns', data_info['columns'] - len(data_info['numeric_columns']))
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(['📋 Data Profile', '🤖 AI Training', '🔍 Correlations', '🎯 Predictions'])
    
    with tab1:
        st.subheader('📊 Data Profile')
        if st.button('🔄 Get Profile from Backend'):
            try:
                response = requests.get(f"{BACKEND_URL}/profile")
                if response.status_code == 200:
                    profile = response.json()['profile']
                    
                    # Display profile
                    profile_df = pd.DataFrame({
                        'Column': list(profile['dtypes'].keys()),
                        'Data Type': list(profile['dtypes'].values()),
                        'Missing Values': [profile['missing_values'][col] for col in profile['dtypes'].keys()],
                        'Unique Values': [profile['unique_values'][col] for col in profile['dtypes'].keys()]
                    })
                    st.dataframe(profile_df, use_container_width=True)
                else:
                    st.error('❌ Failed to get profile')
            except Exception as e:
                st.error(f'❌ Error: {e}')
    
    with tab2:
        st.subheader('🤖 AI Model Training')
        
        col_left, col_right = st.columns(2)
        
        with col_left:
            target_col = st.selectbox('🎯 Target Column', data_info['column_names'])
            n_trees = st.slider('🌳 Number of Trees', 5, 50, 20)
        
        with col_right:
            feature_cols = st.multiselect(
                '🔧 Feature Columns',
                [col for col in data_info['column_names'] if col != target_col],
                default=[col for col in data_info['column_names'] if col != target_col][:3]
            )
        
        if st.button('🚀 Train Model on Backend', type='primary'):
            if feature_cols:
                try:
                    payload = {
                        'target_column': target_col,
                        'feature_columns': feature_cols,
                        'n_trees': n_trees
                    }
                    
                    with st.spinner('Training model on backend...'):
                        response = requests.post(f"{BACKEND_URL}/train", json=payload)
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f'✅ {result["model_type"].title()} model trained!')
                        st.metric(f'📊 {result["metric"].upper()}', f'{result["score"]:.3f}')
                        st.session_state['model_trained'] = True
                    else:
                        st.error('❌ Training failed')
                except Exception as e:
                    st.error(f'❌ Error: {e}')
            else:
                st.warning('⚠️ Select feature columns')
    
    with tab3:
        st.subheader('🔍 Correlation Analysis')
        if st.button('📊 Get Correlations from Backend'):
            try:
                response = requests.get(f"{BACKEND_URL}/correlations")
                if response.status_code == 200:
                    data = response.json()
                    correlations = data['correlations']
                    
                    # Display top correlations
                    corr_df = pd.DataFrame(correlations)
                    st.dataframe(corr_df, use_container_width=True)
                    
                    # Correlation heatmap
                    if len(data_info['numeric_columns']) > 1:
                        matrix = pd.DataFrame(data['matrix'])
                        fig = px.imshow(matrix, text_auto=True, title='🔥 Correlation Heatmap')
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error('❌ Failed to get correlations')
            except Exception as e:
                st.error(f'❌ Error: {e}')
    
    with tab4:
        st.subheader('🎯 Make Predictions')
        if st.session_state.get('model_trained', False):
            st.write('Adjust feature values using sliders:')
            
            # Get data ranges for sliders
            if st.button('📊 Get Data Ranges'):
                try:
                    response = requests.get(f"{BACKEND_URL}/profile")
                    if response.status_code == 200:
                        st.session_state['data_ranges'] = response.json()['profile']
                except Exception as e:
                    st.error(f'❌ Error getting ranges: {e}')
            
            # Create range sliders for features
            feature_values = {}
            if 'data_ranges' in st.session_state:
                profile = st.session_state['data_ranges']
                
                # Use numeric ranges if available
                if 'numeric_ranges' in profile:
                    for col in list(profile['numeric_ranges'].keys())[:5]:  # Limit to 5 columns
                        ranges = profile['numeric_ranges'][col]
                        min_val = ranges['min']
                        max_val = ranges['max']
                        default_val = ranges['mean']
                        
                        feature_values[col] = st.slider(
                            f'📊 {col}',
                            min_value=float(min_val),
                            max_value=float(max_val),
                            value=float(default_val),
                            step=(max_val - min_val) / 100
                        )
                else:
                    # Fallback to basic sliders
                    for col in data_info['numeric_columns'][:3]:
                        feature_values[col] = st.slider(
                            f'📊 {col}',
                            min_value=0.0,
                            max_value=100.0,
                            value=50.0,
                            step=0.1
                        )
            else:
                st.info('💡 Click "Get Data Ranges" first to see sliders')
            
            if feature_values and st.button('🔮 Predict'):
                try:
                    payload = {'features': feature_values}
                    response = requests.post(f"{BACKEND_URL}/predict", json=payload)
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f'🎯 Prediction: {result["prediction"]:.3f}')
                        
                        # Show input values used
                        with st.expander('📋 Input Values Used'):
                            for key, value in feature_values.items():
                                st.write(f'• {key}: {value:.2f}')
                    else:
                        st.error('❌ Prediction failed')
                except Exception as e:
                    st.error(f'❌ Error: {e}')
        else:
            st.info('💡 Train a model first to make predictions')

else:
    # Welcome screen
    st.markdown("""
    <div style="text-align: center; padding: 3rem;">
        <h2>🚀 Welcome to the AI-Powered Data Dashboard</h2>
        <p style="font-size: 1.2rem; color: #666;">Upload a CSV file and interact with the Flask backend</p>
        <br>
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 10px; color: white;">
            <h3>🔧 Backend Features</h3>
            <p>• Data upload and profiling</p>
            <p>• AI model training</p>
            <p>• Correlation analysis</p>
            <p>• Real-time predictions</p>
        </div>
    </div>
    """, unsafe_allow_html=True)