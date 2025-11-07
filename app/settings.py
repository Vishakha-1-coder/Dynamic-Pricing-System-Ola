# app/settings.py
import os
import math
import requests
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "").strip()

@dataclass
class FareRule:
    base: float
    per_km: float
    per_min: float

FARE_ECONOMY = FareRule(base=50, per_km=12, per_min=2)
FARE_PREMIUM = FareRule(base=90, per_km=20, per_min=3)

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.009
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlmb/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def maps_distance_duration(origin, destination):
    """Returns (distance_km, duration_min)."""
    if not GOOGLE_API_KEY:
        return None, None
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {"origins": origin, "destinations": destination, "key": GOOGLE_API_KEY, "units": "metric"}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    try:
        elem = data["rows"][0]["elements"][0]
        if elem.get("status") != "OK":
            return None, None
        dist = elem["distance"]["value"] / 1000
        dur = elem["duration"]["value"] / 60
        return dist, dur
    except Exception:
        return None, None

def estimate_base_cost(vehicle_type, distance_km, duration_min):
    rule = FARE_PREMIUM if vehicle_type.lower() == "premium" else FARE_ECONOMY
    return rule.base + rule.per_km * distance_km + rule.per_min * duration_min

def infer_time_bucket(hour):
    if 5 <= hour < 12: return "Morning"
    if 12 <= hour < 17: return "Afternoon"
    if 17 <= hour < 21: return "Evening"
    return "Night"
