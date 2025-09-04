import streamlit as st
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import ConfusionMatrixDisplay, RocCurveDisplay, PrecisionRecallDisplay

st.set_page_config(page_title="Disease Identification App", layout="wide")
st.title("Disease Identification with Selective Features & Detailed Evaluation")

# Load pretrained model if exists (optional)
MODEL_PATH = "disease_classifier.pkl"
try:
    clf_loaded = joblib.load(MODEL_PATH)
except FileNotFoundError:
    clf_loaded = None
    st.info("Pretrained model not found. Please train a model with your dataset.")

uploaded_file = st.file_uploader("Upload CSV dataset", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("Dataset Preview")
    st.dataframe(df.head(10))

    target_col = st.selectbox("Select target column", options=df.columns)
    features_all = [col for col in df.columns if col != target_col]

    selected_features = st.multiselect("Select features to use", features_all, default=features_all)

    drop_na = st.checkbox("Drop rows with missing values", value=True)

    clf_name = st.selectbox("Choose classifier", ["Logistic Regression", "SVM (linear)"])
    test_size = st.slider("Test set size", 0.1, 0.4, 0.2, 0.05)
    random_state = st.number_input("Random seed", min_value=0, value=42)
    C = st.number_input("Regularization C", 0.001, 10.0, 1.0, 0.1, format="%.3f")

    if st.button("Train & Evaluate Model"):
        if not selected_features:
            st.error("Please select at least one feature.")
            st.stop()

        X = df[selected_features].copy()
        y = df[target_col].copy()

        # Drop missing values if chosen
        if drop_na:
            mask = X.notna().all(axis=1) & y.notna()
            X = X.loc[mask]
            y = y.loc[mask]
            st.write(f"Rows after dropping missing values: {len(y)}")

        if X.empty or y.empty:
            st.error("No data available after removing missing values.")
            st.stop()

        # Convert target to int for classification
        try:
            y = y.astype(int)
        except Exception as e:
            st.error(f"Target column conversion to discrete integer classes failed: {e}")
            st.stop()

        # Convert non-numeric features to integers using label encoding
        for col in X.columns:
            if not np.issubdtype(X[col].dtype, np.number):
                st.warning(f"Feature '{col}' converted to numeric via label encoding.")
                X[col], _ = pd.factorize(X[col])

        # Confirm all features numeric
        if not all(np.issubdtype(X[col].dtype, np.number) for col in X.columns):
            st.error("All selected features must be numeric after conversion.")
            st.stop()

        # Stratified split for train/test
        vc = y.value_counts()
        stratify_arg = y if (y.nunique() > 1 and vc.min() >= 2) else None
        if stratify_arg is None:
            st.warning("Stratified split disabled due to insufficient class samples.")

        try:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state, stratify=stratify_arg
            )
        except Exception as e:
            st.warning(f"Stratified split failed ({e}), falling back to unstratified split.")
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state, stratify=None
            )

        # Build pipeline
        if clf_name == "Logistic Regression":
            model = Pipeline([
                ("scaler", StandardScaler()),
                ("clf", LogisticRegression(C=C, max_iter=1000))
            ])
        else:
            model = Pipeline([
                ("scaler", StandardScaler()),
                ("clf", SVC(C=C, kernel="linear", probability=True))
            ])

        # Train model
        model.fit(X_train, y_train)
        acc = model.score(X_test, y_test)
        st.write(f"Test set accuracy: {acc:.3f}")

        # Confusion matrix
        st.subheader("Confusion Matrix")
        fig_cm, ax_cm = plt.subplots(figsize=(5, 4))
        ConfusionMatrixDisplay.from_estimator(model, X_test, y_test, ax=ax_cm)
        st.pyplot(fig_cm)

        # ROC / PR curves only if binary classification
        num_classes = y.nunique()
        if num_classes == 2:
            st.subheader("ROC Curve")
            fig_roc, ax_roc = plt.subplots(figsize=(5, 4))
            try:
                RocCurveDisplay.from_estimator(model, X_test, y_test, ax=ax_roc, name=clf_name)
                st.pyplot(fig_roc)
            except Exception as e:
                st.warning(f"ROC curve plotting failed: {e}")

            st.subheader("Precision-Recall Curve")
            fig_pr, ax_pr = plt.subplots(figsize=(5, 4))
            try:
                PrecisionRecallDisplay.from_estimator(model, X_test, y_test, ax=ax_pr, name=clf_name)
                st.pyplot(fig_pr)
            except Exception as e:
                st.warning(f"Precision-Recall plotting failed: {e}")
        else:
            st.info(f"ROC and Precision-Recall curves are only available for binary classification problems. Your target has {num_classes} unique classes.")

else:
    st.info("Upload a CSV dataset to begin.")
