import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report
from sklearn.ensemble import RandomForestClassifier
import joblib

# ----------------------------
# 1. Load Dataset
# ----------------------------
df = pd.read_csv("data/crop_loss_dataset.csv")

# ----------------------------
# 2. Feature & Target
# ----------------------------
target = "spoilage_risk"
features = df.columns.drop(target)

X = df[features]
y = df[target]

# Columns
numeric_cols = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
categorical_cols = X.select_dtypes(include=['object']).columns.tolist()

# ----------------------------
# 3. Preprocessing
# ----------------------------
preprocessor = ColumnTransformer([
    ("num", StandardScaler(), numeric_cols),
    ("cat", OneHotEncoder(handle_unknown='ignore'), categorical_cols)
])

# ----------------------------
# 4. Model + Pipeline
# ----------------------------
rf = RandomForestClassifier(class_weight="balanced")

pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("rf", rf)
])

# Hyperparameters
params = {
    "rf__n_estimators": [150, 250],
    "rf__max_depth": [10, 15, None],
    "rf__min_samples_split": [2, 5],
}

grid = GridSearchCV(
    pipeline,
    param_grid=params,
    cv=4,
    scoring='f1_macro',
    n_jobs=-1
)

grid.fit(X, y)

print("\nBest Params:", grid.best_params_)
print("\nClassification Report:")
print(classification_report(y, grid.predict(X)))

# ----------------------------
# 5. Save Model
# ----------------------------
joblib.dump(grid.best_estimator_, "ml_models/spoilage/model.pkl")
print("\nSpoilage model saved!")

# ----------------------------
# 6. Export feature names
# ----------------------------
joblib.dump({
    "numeric": numeric_cols,
    "categorical": categorical_cols
}, "ml_models/spoilage/feature_meta.pkl")
print("Feature metadata saved!")
