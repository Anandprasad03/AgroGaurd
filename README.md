# 🌾 AgroGuard — Intelligent Crop Management & Logistics System

AgroGuard is an advanced AgriTech platform that bridges farm production and market logistics. It combines machine learning (spoilage prediction), time-series analysis (market price forecasting) and generative AI (conversational agronomist) to help farmers maximize yield value and minimize post-harvest losses.

Short summary:
- Predict spoilage risk for harvested crops
- Forecast near-term market prices to optimize sale timing
- Optimize transport schedules to preserve freshness
- Provide an AI agronomist for crop planning and soil advice

Repository: https://github.com/your-username/agroguard (replace with actual URL)


![Build Status](https://img.shields.io/badge/build-passing-brightgreen) ![Python Version](https://img.shields.io/badge/python-3.9%2B-blue) ![License](https://img.shields.io/badge/license-MIT-lightgrey)

(Replace with your CI / coverage badges and actual links.)

- Description
- Badges
- Features
- Tech Stack
- Project Structure
- Installation & Setup
  - Prerequisites
  - Clone
  - Backend
  - Environment Variables
  - Run Locally
  - Frontend
- Usage / Examples
- API Reference
- Screenshots
- Contributing
- License
- Acknowledgements

## 🚀 Key Features

1. Spoilage Prediction Engine
   - Files: predict.html / spoilage_api.py
   - Function: Predicts probability of produce spoilage using crop parameters (temperature, humidity, harvest time).
   - Tech: Scikit-learn classifier (trained on crop_loss_dataset.csv).

2. Market Price Forecasting
   - Files: price.html / price_api.py
   - Function: Forecasts market rates using historical price trends to help decide sell timing.
   - Tech: Regression / Time-series models.

3. Smart Logistics Optimizer
   - Files: logistics.html / logistics_api.py
   - Function: Computes optimal transport departure times to maximize freshness at market.

4. AI Agronomist Agent
   - Files: crop_planner.html / ai_agent_api.py
   - Function: Conversational AI that analyzes soil profiles and suggests crop rotations and schedules.
   - Tech: LLM integration (Groq / Google Gemini API).

5. Centralized Dashboard
   - Files: dashboard.html
   - Function: Visualizes soil health, financial projections, and spoilage risk using Chart.js.


## 🛠️ Tech Stack

- Frontend: HTML5, CSS3, Vanilla JavaScript (ES6+), Chart.js
- Backend API: Python (FastAPI recommended) or Flask
- ML: scikit-learn, pandas, numpy, joblib
- AI Integration: Groq API / Google Gemini (replace with your chosen provider and docs link)
- Deployment: Optional Docker, Vercel, or Render
- Data: project/data/ (training datasets)


## 📂 Project Structure

Preserved original tree (improved for readability):

```bash
project/
├── frontend/           # User Interface (HTML/JS/CSS)
│   ├── assets/         # Images and Global Styles
│   ├── js/             # API Connectors and Logic
│   └── *.html          # Web Pages
├── backend/            # API Endpoints
│   ├── *_api.py        # Feature-specific logic
│   └── main.py         # Server Entry Point
├── ml_models/          # Trained Models & Serialized Objects
│   ├── spoilage/       # Spoilage Classifiers
│   └── price/          # Price Regressors
├── data/               # Datasets for Training
└── docs/               # Architecture Diagrams & Planning
```

Notes:
- Keep trained models (serialized) in ml_models/ and do not commit large binary models to Git — use a model storage or Git LFS.
- Keep sample datasets in data/ or link to the full dataset location in docs/.

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.9+
- Git
- (Optional) Docker

### 1) Clone the repository
```bash
git clone https://github.com/your-username/agroguard.git
cd agroguard
```

### 2) Backend setup (recommended: FastAPI)
Create and activate a virtual environment, then install requirements:

```bash
python -m venv venv
# macOS / Linux
source venv/bin/activate
# Windows (PowerShell)
# .\venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

### 3) Environment variables
Create a `.env` file in the project root with required keys (example):

```env
GROQ_API_KEY=your_api_key_here
GEMINI_API_KEY=your_api_key_here
# Add other keys (e.g., DATABASE_URL) as needed
```

(If you use python-dotenv or similar, configure it in backend/main.py.)

### 4) Run the backend locally
```bash
# Example for uvicorn + FastAPI
uvicorn backend.main:app --reload
```

### 5) Frontend
The frontend is static HTML/JS. Options:
- Open `frontend/index.html` directly in your browser (file://).
- Recommended: serve with Live Server in VS Code or a lightweight HTTP server.

Example using Python's http.server (serve from `frontend/`):
```bash
cd frontend
python -m http.server 5500
# then open http://localhost:5500
```


## Environment Variables

Create a `.env` file at the project root containing keys used by the app. Example entries:

```env
GROQ_API_KEY=your_api_key_here
GEMINI_API_KEY=your_api_key_here
# Example: DATABASE_URL=sqlite:///./dev.db
# Example: SECRET_KEY=replace_this_with_a_secure_value
```

Load these variables using python-dotenv or your preferred method in backend/main.py before starting the app.

## Usage / Examples

Quick API example (assumes a spoilage prediction endpoint):

```bash
# Using curl to call the spoilage API
curl -X POST http://localhost:8000/api/spoilage/predict \
  -H "Content-Type: application/json" \
  -d '{"temperature": 10, "humidity": 85, "harvest_time": "2026-02-10T08:00:00"}'
```

Expected response (example):
```json
{
  "crop": "tomato",
  "spoilage_probability": 0.23,
  "recommended_action": "sell within 2 days or refrigerate"
}
```

Frontend: open dashboard and interact with tools (price forecast, logistics optimizer, AI agronomist) via the provided UI pages (e.g., `frontend/dashboard.html`).

## API Reference (brief)

Endpoints (examples — implement and document fully in docs/api.md):
- `POST /api/spoilage/predict` — predict spoilage probability (payload: temperature, humidity, harvest_time, crop_type)
- `POST /api/price/forecast` — forecast market prices (payload: crop_type, historical_range)
- `POST /api/logistics/optimize` — suggest transport times (payload: origin, destination, predicted_spoilage)
- `POST /api/ai/plan` — conversational agronomist (payload: soil_profile, user_questions)

Add a full OpenAPI/Swagger spec (FastAPI provides it at `/docs`) and link to docs/api.md.

## 📸 Screenshots & Architecture

Add screenshots to `docs/` and reference them here. Example:

- docs/screenshots/dashboard.png — Centralized Dashboard
- docs/screenshots/predict_tool.png — Spoilage Prediction Tool

(Place actual images and update paths.)


## Contributing

Contributions are welcome. Suggested workflow:
1. Fork the repo.
2. Create a feature branch: `git checkout -b feat/my-feature`.
3. Commit changes and push: `git push origin feat/my-feature`.
4. Open a pull request describing your change.

Please include tests for new ML pre-processing or API behavior. Add code style checks and follow the existing patterns. Add an issue before large changes so we can discuss design/approach.

## License

This project should include a LICENSE file. Example (MIT):

MIT License

Copyright (c) YEAR Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions: ...

(Replace with the actual license text or choose another license and add LICENSE file.)

## Acknowledgements

- Chart.js for visualization
- scikit-learn, pandas, numpy for ML
- Inspiration: various AgriTech projects and open datasets


## Support

For issues, open an issue on the repository. For feature requests or collaboration, contact the maintainers via the GitHub profile or add details in the issue tracker.