# 🌾 AgroGuard
> **AI-Driven Smart Farming & Crop Protection System**

![Project Status](https://img.shields.io/badge/Status-Active-success?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi)
![AI](https://img.shields.io/badge/AI-Gemini%201.5%20Flash-orange?style=flat-square&logo=google)
![License](https://img.shields.io/badge/License-MIT-lightgrey?style=flat-square)

---

## 📖 About The Project

**AgroGuard** is an innovative agricultural management platform designed to empower modern farmers with real-time insights and automated security. Acting as a digital sentinel for your farmland, AgroGuard leverages **Generative AI** and **Machine Learning** to monitor crop health, predict spoilage risks, and optimize soil usage.

The system provides actionable data to improve crop yields and ensure sustainable farming practices by providing a robust defense against environmental threats through early detection and intelligent alerting.

---

## ✨ Key Features

### 🤖 1. AI Crop Planner
* **Intelligent Rotation:** Generates optimal crop rotation plans based on soil type, season, and previous harvest.
* **Soil Health Analysis:** AI analyzes soil gaps and suggests nitrogen-fixing crops.
* **Sustainability Scoring:** Visualizes the long-term impact of planting decisions.

### 🛡️ 2. Spoilage Risk Predictor
* **Real-time Risk Assessment:** Calculates the probability of crop spoilage based on storage temperature, humidity, and time.
* **Dynamic Visualizations:** Interactive Radar and Doughnut charts to visualize risk factors.
* **Robust AI Fallback:** System continues to work with "Safe Mode" estimation even if the AI service is temporarily down.


### 📈 3. Market Price & Profit Predictor 
* **Price Forecasting:** Predicts next-month crop prices based on current market price, season, and region.
* **Trend Analysis:** Generates a 5-month price trend for better selling and storage decisions.
* **Profit Guidance:** Provides AI-based recommendations on whether farmers should sell now or store for higher returns.
* **Graphical Insights:** Interactive charts to visualize price movement and expected profit.

### 📊 4. Smart Dashboard
* **User-Friendly Interface:** Clean, responsive UI built with HTML5 & CSS3.
* **Data Visualization:** Integrated Chart.js for instant graphical feedback.



---

## 🛠️ Tech Stack

| Component | Technology |
| :--- | :--- |
| **Backend** | Python, FastAPI, Uvicorn |
| **AI Engine** | Google Gemini 3 Flash Preview (Generative AI) |
| **Frontend** | HTML5, CSS3, JavaScript |
| **Visualization** | Chart.js |
| **Data Processing** | Pandas, JSON |

---

## 📂 Project Structure

```bash
AgroGuard
├── backend/
│   ├── ai_agent_api.py       # AI Logic for Crop Planning
│   ├── spoilage_api.py       # AI Logic for Spoilage Prediction
│   └── main.py               # FastAPI Entry Point
├── data/                     # Static data resources
├── docs/                     # Design documents & wireframes
└── frontend/
    ├── assets/               # CSS, Images, Videos
    ├── crop_planner.html     # AI Rotation Interface
    ├── predict.html          # Spoilage Prediction Interface
    ├── index.html            # Landing Page
    └── about.html            # About the project

## 🚀 Getting Started

Follow these steps to set up the project locally.

### Prerequisites
* Python 3.9 or higher
* A Google Cloud API Key (for Gemini)

### Installation

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/Anandprasad03/AgroGuard.git](https://github.com/Anandprasad03/AgroGuard.git)
    cd AgroGuard
    ```

2.  **Install Dependencies**
    ```bash
    pip install fastapi uvicorn requests python-dotenv pydantic
    ```

3.  **Configure Environment**
    Create a `.env` file in the root directory `AgroGuard/` and add your API key:
    ```env
    GEMINI_API_KEY=your_google_api_key_here
    ```

4.  **Run the Backend**
    ```bash
    uvicorn backend.main:app --reload
    ```

5.  **Launch the App**
    Open `frontend/index.html` in your browser.

---

## 📸 Screenshots

| Landing Page | Crop Planner | Spoilage Predictor |
| :---: | :---: | :---: |
| <img src="docs/dashboard_wireframe.png" width="200" alt="Landing"> | <img src="frontend/assets/png's/soil-health.png" width="200" alt="Planner"> | <img src="frontend/assets/png's/sustainable.png" width="200" alt="Predictor"> |

---

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1.  **Fork** the Project
2.  **Create** your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  **Commit** your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  **Push** to the Branch (`git push origin feature/AmazingFeature`)
5.  **Open** a Pull Request

---

## 📞 Contact
**Email:** (gietuinnovatex@gmail.com)
**Project Link:** [https://github.com/Anandprasad03/AgroGuard](https://github.com/Anandprasad03/AgroGuard)


                                    Built with ❤️ for Farmers