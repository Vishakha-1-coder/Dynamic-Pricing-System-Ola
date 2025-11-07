# app/app.py
import os
from datetime import datetime
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from .settings import (
    maps_distance_duration, estimate_base_cost, infer_time_bucket, GOOGLE_API_KEY
)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODEL_PATH = os.path.join(ROOT, "model", "dynamic_pricing_pipeline.joblib")

app = FastAPI(title="Dynamic Pricing API", version="1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://vishakha-pricing-ai.netlify.app",  # your Netlify frontend
        "http://localhost:5500"                     # optional for local testing
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


_model = None

@app.on_event("startup")
def load_model():
    global _model
    if not os.path.exists(MODEL_PATH):
        raise RuntimeError(f"Model not found at {MODEL_PATH}.")
    _model = joblib.load(MODEL_PATH)
    print("✅ Model loaded successfully.")

class RideRequest(BaseModel):
    origin: str = Field(..., example="CST Station, Mumbai")
    destination: str = Field(..., example="BKC, Mumbai")
    vehicle_type: str = "Economy"
    number_of_riders: int = 60
    number_of_drivers: int = 25
    number_of_past_rides: int = 10
    average_ratings: float = 4.3
    location_category: str = "Urban"
    customer_loyalty_status: str = "Regular"
    time_of_booking: str | None = None

@app.get("/health")
def health():
    return {"status": "ok", "google_api_key": bool(GOOGLE_API_KEY)}

@app.post("/predict")
def predict_fare(req: RideRequest):
    distance_km, duration_min = maps_distance_duration(req.origin, req.destination)
    if distance_km is None or duration_min is None:
        distance_km, duration_min = 5.0, 15.0  # fallback
    base_cost = estimate_base_cost(req.vehicle_type, distance_km, duration_min)
    time_bucket = req.time_of_booking or infer_time_bucket(datetime.now().hour)

    df = pd.DataFrame([{
        "Number_of_Riders": req.number_of_riders,
        "Number_of_Drivers": req.number_of_drivers,
        "Number_of_Past_Rides": req.number_of_past_rides,
        "Average_Ratings": req.average_ratings,
        "Expected_Ride_Duration": duration_min,
        "Historical_Cost_of_Ride": base_cost,
        "Location_Category": req.location_category,
        "Customer_Loyalty_Status": req.customer_loyalty_status,
        "Time_of_Booking": time_bucket,
        "Vehicle_Type": req.vehicle_type
    }])
    try:
        price = _model.predict(df)[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "origin": req.origin,
        "destination": req.destination,
        "distance_km": round(distance_km, 2),
        "duration_min": round(duration_min, 1),
        "base_cost": round(base_cost, 2),
        "predicted_dynamic_price": round(float(price), 2)
    }
