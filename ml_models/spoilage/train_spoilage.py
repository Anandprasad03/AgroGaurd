import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib

# 1. Load Data
df = pd.read_csv("data/crop_loss_dataset.csv")

# 2. Features & Target
# We drop ID and Timestamp as they don't cause spoilage
X = df[["city", "temperature", "humidity", "rainfall"]]
y = df["spoilage_risk"]

# 3. Preprocessing
# Numeric: Temp, Humidity, Rain
# Categorical: City
numeric_features = ["temperature", "humidity", "rainfall"]
categorical_features = ["city"]

preprocessor = ColumnTransformer([
    ("num", StandardScaler(), numeric_features),
    ("cat", OneHotEncoder(handle_unknown='ignore'), categorical_features)
])

# 4. Pipeline
# We use RandomForest to handle the complex interactions
pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", RandomForestClassifier(n_estimators=100, random_state=42))
])

# 5. Train
print("Training on Real-World Structure...")
pipeline.fit(X, y)

# 6. Save Model
joblib.dump(pipeline, "ml_models/spoilage/model.pkl")
print("✅ Model Saved! Classification Report:")
print(classification_report(y, pipeline.predict(X)))