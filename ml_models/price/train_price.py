import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

# ----------------------------
# 1. Load Dataset
# ----------------------------
df = pd.read_csv("data/price_history.csv")

# Expected columns:
# date, crop, mandi, price
# You can easily adapt any dataset.

# ----------------------------
# 2. Feature Engineering
# ----------------------------
df["date"] = pd.to_datetime(df["date"])
df["day"] = df["date"].dt.day
df["month"] = df["date"].dt.month
df["year"] = df["date"].dt.year
df["day_of_year"] = df["date"].dt.dayofyear
df["week"] = df["date"].dt.isocalendar().week.astype(int)

# Drop original date
df = df.drop(columns=["date"])

# ----------------------------
# 3. Encode categorical
# ----------------------------
df = pd.get_dummies(df, columns=["crop", "mandi"], drop_first=True)

# ----------------------------
# 4. Split Features/Target
# ----------------------------
X = df.drop(columns=["price"])
y = df["price"]

numeric_cols = X.columns.tolist()

# ----------------------------
# 5. Pipeline
# ----------------------------
pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("rf", RandomForestRegressor())
])

params = {
    "rf__n_estimators": [200, 300],
    "rf__max_depth": [10, 15, None],
    "rf__min_samples_split": [2, 4]
}

grid = GridSearchCV(
    pipeline,
    param_grid=params,
    cv=4,
    scoring="neg_mean_absolute_error",
    n_jobs=-1
)

grid.fit(X, y)

pred = grid.predict(X)

print("\nMAE:", mean_absolute_error(y, pred))
print("R2 Score:", r2_score(y, pred))
print("Best Params:", grid.best_params_)

# ----------------------------
# 6. Save Model + Metadata
# ----------------------------
joblib.dump(grid.best_estimator_, "ml_models/price/price_model.pkl")
print("\nPrice model saved!")

joblib.dump(numeric_cols, "ml_models/price/feature_meta.pkl")
print("Feature metadata saved!")