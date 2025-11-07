# scripts/train_model.py
import os
from pathlib import Path
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

# paths
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "dynamic_pricing_processed.csv"
MODEL_DIR = ROOT / "model"
MODEL_DIR.mkdir(exist_ok=True, parents=True)
MODEL_PATH = MODEL_DIR / "dynamic_pricing_pipeline.joblib"

def main():
    assert DATA.exists(), f"Missing file: {DATA}"
    df = pd.read_csv(DATA)

    target = "adjusted_ride_cost"
    if target not in df.columns:
        raise ValueError("Column 'adjusted_ride_cost' missing. Ensure Phase-3 processing done.")

    # numeric + categorical features
    numeric_features = [
        "Number_of_Riders",
        "Number_of_Drivers",
        "Number_of_Past_Rides",
        "Average_Ratings",
        "Expected_Ride_Duration",
        "Historical_Cost_of_Ride"
    ]
    categorical_features = [
        "Location_Category",
        "Customer_Loyalty_Status",
        "Time_of_Booking",
        "Vehicle_Type"
    ]

    X = df[numeric_features + categorical_features]
    y = df[target]

    # split
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # preprocessors
    num_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])
    cat_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore"))
    ])

    preprocessor = ColumnTransformer([
        ("num", num_pipe, numeric_features),
        ("cat", cat_pipe, categorical_features)
    ])

    # model
    model = RandomForestRegressor(
        n_estimators=400,
        random_state=42,
        n_jobs=-1
    )

    # full pipeline
    pipe = Pipeline([
        ("preprocessor", preprocessor),
        ("model", model)
    ])

    # train
    pipe.fit(X_train, y_train)
    y_pred = pipe.predict(X_val)

    mae = mean_absolute_error(y_val, y_pred)
    r2 = r2_score(y_val, y_pred)

    print(f"✅ Model trained successfully!")
    print(f"MAE: {mae:.2f}")
    print(f"R²:  {r2:.3f}")

    joblib.dump(pipe, MODEL_PATH)
    print(f"💾 Saved pipeline → {MODEL_PATH}")

if __name__ == "__main__":
    main()
