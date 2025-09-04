import pandas as pd
import joblib
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

# Load dataset
df = pd.read_csv("diseases.csv")
TARGET_COL = "target"

# Separate features and target, ensure target is int for classification
X = df.drop(columns=[TARGET_COL])
y = df[TARGET_COL].astype(int)

# Use only numeric features for training
X = X.select_dtypes(include=["number"])

# Stratify only if every class has at least 2 samples
vc = y.value_counts()
stratify_arg = y if (y.nunique() > 1 and vc.min() >= 2) else None

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=stratify_arg
)

# Create pipeline with scaler and logistic regression
clf = Pipeline([
    ("scaler", StandardScaler()),
    ("clf", LogisticRegression(max_iter=1000))
])

# Train model
clf.fit(X_train, y_train)

# Save the trained model
joblib.dump(clf, "disease_classifier.pkl")
print("Model trained and saved to 'disease_classifier.pkl'.")
