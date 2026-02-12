import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
import joblib

# 1. Load Data
df = pd.read_csv("data/price_history.csv")

# 2. Feature Engineering
df["Date"] = pd.to_datetime(df["Date"])
df["Month"] = df["Date"].dt.month
df["Year"] = df["Date"].dt.year
# Drop Date (model can't read dates directly) and Target
X = df.drop(columns=["Date", "Market_Price"]) 
y = df["Market_Price"]

# 3. Define Preprocessor
numeric_features = ["Supply_Tonnes", "Transport_Cost_Per_Km", "Fuel_Price", "Month", "Year"]
categorical_features = ["Crop", "Location"]

preprocessor = ColumnTransformer([
    ("num", StandardScaler(), numeric_features),
    ("cat", OneHotEncoder(handle_unknown='ignore'), categorical_features)
])

# 4. Pipeline
model = Pipeline([
    ("preprocessor", preprocessor),
    ("regressor", RandomForestRegressor(n_estimators=100, random_state=42))
])

# 5. Train
print("Training Price Model...")
model.fit(X, y)

# 6. Save
joblib.dump(model, "ml_models/price/price_model.pkl")
print("✅ Price model saved to ml_models/price/price_model.pkl")