import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title='AI-Powered Data Dashboard',
    page_icon='🤖',
    layout='wide',
    initial_sidebar_state='expanded'
)

# Custom CSS for modern styling
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
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: #f0f2f6;
        border-radius: 10px 10px 0 0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #667eea;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🤖 AI-Powered Data Dashboard</h1>', unsafe_allow_html=True)
st.markdown('---')

# Sidebar for file upload and settings
with st.sidebar:
    st.header('📁 Data Upload')
    uploaded_file = st.file_uploader('Upload your CSV file', type=['csv'], help='Upload a CSV file to analyze')
    
    if uploaded_file:
        st.success('✅ File uploaded successfully!')
        st.info(f'File: {uploaded_file.name}')

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    # Dataset overview metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric('📊 Total Rows', f'{len(df):,}')
    with col2:
        st.metric('📈 Total Columns', len(df.columns))
    with col3:
        st.metric('🔢 Numeric Columns', len(df.select_dtypes(include=np.number).columns))
    with col4:
        st.metric('📝 Text Columns', len(df.select_dtypes(include='object').columns))
    
    # Tabs for better organization
    tab1, tab2, tab3, tab4, tab5 = st.tabs(['📋 Data Overview', '🔧 Feature Engineering', '🤖 AI Models', '📊 Visualizations', '🔍 Insights'])

    # Data cleaning
    for col in df.select_dtypes(include=np.number).columns:
        df[col].fillna(df[col].mean(), inplace=True)
    for col in df.select_dtypes(include='object').columns:
        df[col].fillna(df[col].mode()[0], inplace=True)

    # Limit dataset size for performance
    max_rows = 10000
    if len(df) > max_rows:
        st.warning(f'📊 Dataset is large ({len(df):,} rows). Using random sample of {max_rows:,} rows for performance.')
        df_sample = df.sample(n=max_rows, random_state=42).reset_index(drop=True)
    else:
        df_sample = df.copy()

    with tab1:
        st.subheader('📋 Raw Data Preview')
        st.dataframe(df_sample.head(10), use_container_width=True)
        
        st.subheader('📊 Data Profile')
        profile_summary = pd.DataFrame({
            'Data Type': df_sample.dtypes.astype(str),
            'Non-null Count': df_sample.notnull().sum(),
            'Unique Values': df_sample.nunique(),
            'Missing Values': df_sample.isnull().sum(),
        })
        st.dataframe(profile_summary, use_container_width=True)
        
        # Key statistics
        if len(df_sample.select_dtypes(include=np.number).columns) > 0:
            st.subheader('📈 Statistical Summary')
            st.dataframe(df_sample.describe(), use_container_width=True)

    with tab2:
        st.subheader('🔧 Custom Feature Engineering')
        num_cols = df_sample.select_dtypes(include=np.number).columns.tolist()
        
        if len(num_cols) >= 2:
            with st.container():
                st.markdown('### Create New Features')
                col_left, col_right = st.columns(2)
                
                with col_left:
                    col1 = st.selectbox('First numeric column', num_cols, key='feat_col1')
                    operation = st.selectbox('Operation', ['Add (+)', 'Subtract (-)', 'Multiply (*)', 'Divide (/)'])
                
                with col_right:
                    col2 = st.selectbox('Second numeric column', [c for c in num_cols if c != col1], key='feat_col2')
                    new_feature_name = st.text_input('Feature name', value=f'{col1}_{operation[0]}_{col2}')
                
                if st.button('🚀 Create Feature', type='primary'):
                    try:
                        if operation == 'Add (+)':
                            df_sample[new_feature_name] = df_sample[col1] + df_sample[col2]
                        elif operation == 'Subtract (-)':
                            df_sample[new_feature_name] = df_sample[col1] - df_sample[col2]
                        elif operation == 'Multiply (*)':
                            df_sample[new_feature_name] = df_sample[col1] * df_sample[col2]
                        elif operation == 'Divide (/)':
                            df_sample[new_feature_name] = df_sample[col1] / df_sample[col2].replace(0, np.nan)
                            df_sample[new_feature_name].fillna(0, inplace=True)

                        st.success(f'✅ Feature "{new_feature_name}" created successfully!')
                        if new_feature_name not in num_cols:
                            num_cols.append(new_feature_name)
                    except Exception as e:
                        st.error(f'❌ Error creating feature: {e}')
        else:
            st.info('💡 Need at least 2 numeric columns for feature engineering.')

    with tab3:
        st.subheader('🤖 AI Model Training')
        
        col_model1, col_model2 = st.columns(2)
        
        with col_model1:
            target_col = st.selectbox('🎯 Target column', df_sample.columns)
        
        with col_model2:
            n_trees = st.slider('🌳 Number of trees', 5, 50, 20, help='Lower values = faster training')

        if target_col:
            feature_cols = st.multiselect(
                '🔧 Feature columns',
                [c for c in df_sample.columns if c != target_col],
                default=[c for c in df_sample.columns if c != target_col][:5]  # Limit default selection
            )

            if feature_cols and st.button('🚀 Train Model', type='primary'):
                with st.spinner('Training model...'):
                    X = df_sample[feature_cols].copy()
                    y = df_sample[target_col]

                    # Encode categorical features
                    for col in X.select_dtypes(include='object').columns:
                        X[col] = X[col].astype('category').cat.codes

                    # Detect classification vs regression
                    is_classification = False
                    if y.dtype == 'object' or str(y.dtype).startswith('category'):
                        is_classification = True
                        y = y.astype('category').cat.codes

                    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

                    if is_classification:
                        clf = RandomForestClassifier(n_estimators=n_trees, max_features='sqrt', random_state=42)
                        clf.fit(X_train, y_train)
                        y_pred = clf.predict(X_test)
                        acc = accuracy_score(y_test, y_pred)
                        
                        st.success('✅ Classification model trained!')
                        st.metric('🎯 Accuracy', f'{acc:.3f}')
                        
                        with st.expander('📊 Detailed Classification Report'):
                            st.text(classification_report(y_test, y_pred))
                    else:
                        reg = RandomForestRegressor(n_estimators=n_trees, max_features='sqrt', random_state=42)
                        reg.fit(X_train, y_train)
                        y_pred = reg.predict(X_test)
                        mse = mean_squared_error(y_test, y_pred)
                        
                        st.success('✅ Regression model trained!')
                        st.metric('📉 Mean Squared Error', f'{mse:.3f}')
                        
                        # Interactive plotly chart
                        fig = px.scatter(x=y_test, y=y_pred, 
                                       labels={'x': 'Actual', 'y': 'Predicted'},
                                       title='Actual vs Predicted Values')
                        fig.add_shape(type='line', x0=y_test.min(), y0=y_test.min(),
                                    x1=y_test.max(), y1=y_test.max(),
                                    line=dict(dash='dash', color='red'))
                        st.plotly_chart(fig, use_container_width=True)
            elif not feature_cols:
                st.warning('⚠️ Please select at least one feature column.')
        else:
            st.info('💡 Select a target column to start training.')

    with tab4:
        st.subheader('📊 Interactive Visualizations')
        
        all_columns = df_sample.columns.tolist()
        if all_columns:
            col_chart1, col_chart2, col_chart3 = st.columns(3)
            
            with col_chart1:
                x_axis = st.selectbox('📊 X-axis', all_columns, key='x_axis_chart')
            
            with col_chart2:
                y_axis = st.selectbox('📈 Y-axis', all_columns, 
                                    index=1 if len(all_columns) > 1 else 0, key='y_axis_chart')
            
            with col_chart3:
                chart_type = st.selectbox('📋 Chart type', ['Scatter Plot', 'Line Chart', 'Bar Chart', 'Box Plot'])

            if st.button('🎨 Generate Visualization', type='primary'):
                try:
                    if chart_type == 'Scatter Plot':
                        fig = px.scatter(df_sample, x=x_axis, y=y_axis, 
                                       title=f'{y_axis} vs {x_axis}',
                                       color_discrete_sequence=['#667eea'])
                    elif chart_type == 'Line Chart':
                        fig = px.line(df_sample, x=x_axis, y=y_axis,
                                    title=f'{y_axis} over {x_axis}')
                    elif chart_type == 'Bar Chart':
                        fig = px.bar(df_sample.head(20), x=x_axis, y=y_axis,
                                   title=f'{y_axis} by {x_axis} (Top 20)')
                    elif chart_type == 'Box Plot':
                        fig = px.box(df_sample, y=y_axis, title=f'Distribution of {y_axis}')
                    
                    fig.update_layout(template='plotly_white')
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"❌ Error generating chart: {e}")

    with tab5:
        st.subheader('🔍 Data Insights')
        
        if len(num_cols) > 1:
            # Correlation heatmap with plotly
            corr_matrix = df_sample[num_cols].corr()
            fig_corr = px.imshow(corr_matrix, 
                               text_auto=True, 
                               aspect='auto',
                               title='🔥 Correlation Heatmap',
                               color_continuous_scale='RdBu_r')
            fig_corr.update_layout(width=800, height=600)
            st.plotly_chart(fig_corr, use_container_width=True)
            
            # Top correlations
            st.subheader('🔗 Strongest Correlations')
            corr_pairs = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_pairs.append({
                        'Feature 1': corr_matrix.columns[i],
                        'Feature 2': corr_matrix.columns[j],
                        'Correlation': corr_matrix.iloc[i, j]
                    })
            
            corr_df = pd.DataFrame(corr_pairs)
            corr_df = corr_df.reindex(corr_df['Correlation'].abs().sort_values(ascending=False).index)
            st.dataframe(corr_df.head(10), use_container_width=True)
            
        else:
            st.info('💡 Need at least 2 numeric columns for correlation analysis.')
        
        # Data distribution
        if num_cols:
            st.subheader('📊 Data Distributions')
            selected_col = st.selectbox('Select column for distribution', num_cols)
            
            col_dist1, col_dist2 = st.columns(2)
            
            with col_dist1:
                fig_hist = px.histogram(df_sample, x=selected_col, 
                                      title=f'Distribution of {selected_col}',
                                      nbins=30)
                st.plotly_chart(fig_hist, use_container_width=True)
            
            with col_dist2:
                fig_box = px.box(df_sample, y=selected_col, 
                               title=f'Box Plot of {selected_col}')
                st.plotly_chart(fig_box, use_container_width=True)

else:
    # Welcome screen
    st.markdown("""
    <div style="text-align: center; padding: 3rem;">
        <h2>🚀 Welcome to the AI-Powered Data Dashboard</h2>
        <p style="font-size: 1.2rem; color: #666;">Upload a CSV file to start exploring your data with advanced AI analytics</p>
        <br>
        <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 10px; color: white; min-width: 200px;">
                <h3>📊 Data Analysis</h3>
                <p>Automated data profiling and insights</p>
            </div>
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 1.5rem; border-radius: 10px; color: white; min-width: 200px;">
                <h3>🤖 AI Models</h3>
                <p>Machine learning with one click</p>
            </div>
            <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 1.5rem; border-radius: 10px; color: white; min-width: 200px;">
                <h3>📈 Visualizations</h3>
                <p>Interactive charts and graphs</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)