import pandas as pd
import numpy as np
import random
from datetime import datetime

# ----------------------------
# CONFIGURATION
# ----------------------------
CITIES = [
    "Gunupur", "Bhubaneswar", "Cuttack", "Rourkela", "Sambalpur", "Titlagarh", 
    "Ganjam", "Baripada", "Balasore", "Bhadrak", "Puri", "Rayagada", "Khurda", 
    "Sundargarh", "Jharsuguda", "Koraput", "Jaleswar", "Nuapada", "Bisoi", 
    "Balangir", "Dhenkanal", "Deoghar", "Nayagarh", "Paradip", "Gopalpur", 
    "Soro", "Banki", "Talcher", "Joda", "Angul"
]

def determine_risk(temp, humidity, rain):
    """
    Logic derived from your real data:
    Your data shows Temp ~30C + Hum ~20% = 'Medium'
    We will extrapolate 'High' and 'Low' from this baseline.
    """
    score = 0
    
    # Temperature Impact
    if temp > 35: score += 3
    elif temp > 28: score += 1  # Your baseline
    
    # Humidity Impact
    if humidity > 70: score += 3
    elif humidity > 40: score += 1
    
    # Rain Impact
    if rain > 5: score += 2
    
    if score >= 4: return "High"
    if score >= 1: return "Medium" # Matches your provided data
    return "Low"

# ----------------------------
# GENERATE DATA
# ----------------------------
data = []
for i in range(10000):
    city = random.choice(CITIES)
    
    # Simulate realistic sensor readings based on your baseline
    temp = round(np.random.normal(30, 5), 2)  # Mean 30, matching your data
    humidity = round(np.random.normal(30, 15), 0) # Mean 30, matching your data
    rainfall = 0.0
    
    # Occasional rain event
    if random.random() > 0.8:
        rainfall = round(np.random.exponential(10), 2)
        humidity += 20 # Rain spikes humidity
        
    risk = determine_risk(temp, humidity, rainfall)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    data.append([i+1, city, temp, humidity, rainfall, risk, timestamp])

# ----------------------------
# SAVE
# ----------------------------
df = pd.DataFrame(data, columns=["id", "city", "temperature", "humidity", "rainfall", "spoilage_risk", "recorded_at"])
df.to_csv("data/crop_loss_dataset.csv", index=False)
print(f"Generated 10,000 lines matching your 'City/Sensor' format.")