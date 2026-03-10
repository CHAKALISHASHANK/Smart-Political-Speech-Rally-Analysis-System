# 🗳️ Smart Political Speech & Rally Analysis System

> An end-to-end AI-powered platform for analyzing political rallies through crowd detection, speech sentiment analysis, and election impact prediction.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Project Structure](#project-structure)
- [AI Modules](#ai-modules)
- [Dashboard Pages](#dashboard-pages)
- [API Endpoints](#api-endpoints)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Technologies Used](#technologies-used)
- [Screenshots](#screenshots)

---

## 🌐 Overview

The **Smart Political Speech & Rally Analysis System** is a full-stack AI application that leverages computer vision, natural language processing, and machine learning to provide deep insights into political rallies. It ingests rally names, speech content, and contextual data to deliver real-time crowd analysis, sentiment scoring, election impact prediction, and an election forecast — all through an interactive web dashboard.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🧠 **CNN Crowd Detection** | Estimates crowd attendance, density class, zone occupancy, demographics, and engagement authenticity |
| 📝 **NLP Speech Analysis** | Performs sentence-level sentiment, topic extraction, rhetoric detection, persuasion scoring, and emotional arc mapping |
| 📈 **ML Impact Prediction** | Predicts vote swing probability, media reach, social virality, fundraising potential, and approval change |
| 🗺️ **Election Forecast** | Generates state-level election probability maps based on composite rally performance |
| 🎛️ **Analyst Studio** | Live analysis UI for analysts to input custom data and get real-time AI predictions |
| 📊 **Interactive Dashboard** | Beautiful multi-page frontend with charts, heatmaps, timelines, and word clouds |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Web Frontend (HTML/CSS/JS)          │
│   Dashboard │ Crowd │ Sentiment │ Impact │ Forecast  │
└──────────────────────┬──────────────────────────────┘
                       │  REST API (JSON)
┌──────────────────────▼──────────────────────────────┐
│              Flask Backend (app.py)                  │
│   /api/overview  /api/crowd  /api/sentiment          │
│   /api/impact    /api/forecast  /api/analyze         │
└──────┬───────────────┬────────────────┬─────────────┘
       │               │                │
┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
│  Module 1   │ │  Module 2   │ │  Module 3   │
│  Crowd CNN  │ │ NLP Speech  │ │ ML Impact   │
│  Detection  │ │  Analyzer   │ │  Predictor  │
└─────────────┘ └─────────────┘ └─────────────┘
```

---

## 📁 Project Structure

```
ptoject 2/
│
├── app.py                  # Flask backend — API routes & model orchestration
├── crowd_detection.py      # Module 1: CNN-based crowd analysis
├── speech_analyzer.py      # Module 2: NLP speech sentiment pipeline
├── impact_model.py         # Module 3: ML impact prediction models
├── requirements.txt        # Python dependencies
│
└── static/
    ├── index.html          # Single-page frontend dashboard
    ├── style.css           # Dashboard styling
    └── app.js              # Frontend logic, charts, and API calls
```

---

## 🤖 AI Modules

### Module 1 — Crowd Detection CNN (`crowd_detection.py`)

Simulates a production CNN (e.g., CSRNet / MCNN architecture) for crowd counting and density estimation.

**Outputs:**
- Estimated attendance count
- Density class: `Sparse` → `Overflow`
- Zone occupancy (front stage, center, back, overflow, standing)
- Demographic breakdown (youth, middle-aged, seniors)
- Engagement metrics (cheer events, wave patterns, crowd movement)
- Authenticity score & confidence
- Crowd density heatmap (20×30 grid)

---

### Module 2 — NLP Speech Sentiment Analyzer (`speech_analyzer.py`)

A full NLP pipeline built on TextBlob for political speech understanding.

**Capabilities:**
- Sentence-level sentiment scoring (polarity & subjectivity)
- Political topic extraction (economy, healthcare, security, etc.)
- Rhetorical device detection (anaphora, antithesis, alliteration, etc.)
- Emotional arc tracking across the speech timeline
- Persuasion effectiveness scoring
- Key quote extraction
- Word frequency analysis (top 30 meaningful words)

---

### Module 3 — Impact Prediction Model (`impact_model.py`)

An ensemble ML system trained on synthetic political science data.

**Models:**
- `RandomForestRegressor` — predicts rally impact score (0–1)
- `GradientBoostingClassifier` — classifies voter swing probability

**Predicts:**
- Overall impact score & level (Low / Moderate / High / Transformative)
- Vote swing probability
- Media reach (millions)
- Social media virality score
- Fundraising potential ($)
- Approval rating change (%)
- Feature importance rankings

---

## 🖥️ Dashboard Pages

| Page | Description |
|---|---|
| **Overview** | High-level KPIs: total rallies, average attendance, sentiment score, impact score |
| **Crowd Detection** | Per-rally crowd stats, zone occupancy, heatmaps, demographic charts |
| **Speech Sentiment** | Sentiment distribution, emotional arc, topic breakdown, persuasion score, word cloud |
| **Impact Prediction** | ML predictions per rally — vote swing, media reach, fundraising, approval change |
| **Election Forecast** | State-level electoral map with predicted win probabilities |
| **Analyst Studio** | Real-time custom analysis — input any speech + crowd data for live AI scoring |

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serve the frontend dashboard |
| `GET` | `/api/overview` | Dashboard summary statistics |
| `GET` | `/api/rallies` | List of all rallies with key metrics |
| `GET` | `/api/rally/<idx>` | Detailed analysis for a specific rally |
| `GET` | `/api/crowd` | Crowd analysis data for all rallies |
| `GET` | `/api/sentiment` | Sentiment data for all rallies |
| `GET` | `/api/impact` | ML impact predictions for all rallies |
| `GET` | `/api/feature-importance` | Model feature importance scores |
| `GET` | `/api/timeline` | Chronological data for timeline charts |
| `GET` | `/api/heatmap/<rally_idx>` | Crowd heatmap grid for a specific rally |
| `GET` | `/api/forecast` | Election forecast data |
| `POST` | `/api/analyze` | Live analysis — accepts custom speech + crowd data |

---

## ⚙️ Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Steps

1. **Clone or download the project**

   ```bash
   git clone <repository-url>
   cd "ptoject 2"
   ```

2. **Create and activate a virtual environment** (recommended)

   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # macOS / Linux
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Download NLTK data** (required by TextBlob)

   ```python
   python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')"
   ```

---

## 🚀 Running the Application

```bash
python app.py
```

On startup, the system will:
1. Initialize all three AI modules
2. Train the ML impact prediction model (~2000 synthetic samples)
3. Pre-compute analyses for all 8 demo rallies
4. Start the Flask development server

Then open your browser and navigate to:

```
http://localhost:5000
```

---

## 🛠️ Technologies Used

### Backend
| Library | Version | Purpose |
|---|---|---|
| Flask | 2.3.3 | Web framework & REST API |
| Flask-CORS | 4.0.0 | Cross-origin resource sharing |
| scikit-learn | 1.3.0 | Random Forest & Gradient Boosting models |
| TextBlob | 0.17.1 | NLP sentiment analysis |
| NLTK | 3.8.1 | Natural language processing utilities |
| NumPy | 1.24.3 | Numerical computations |
| Pandas | 2.0.3 | Data manipulation |
| Pillow | 10.0.0 | Image processing |
| SciPy | 1.11.1 | Scientific computing |
| Matplotlib | 3.7.2 | Data visualization |
| Seaborn | 0.12.2 | Statistical visualization |
| Plotly | 5.15.0 | Interactive charts |
| WordCloud | 1.9.2 | Word frequency visualization |
| Joblib | 1.3.2 | Model serialization |

### Frontend
- **HTML5** — Semantic structure
- **CSS3** — Custom responsive styling
- **Vanilla JavaScript** — Dashboard logic, chart rendering, API calls

---

## 📸 Screenshots

> Launch the app and visit [http://localhost:5000](http://localhost:5000) to explore all dashboard pages interactively.

---

## 📌 Notes

- The ML models are trained on **synthetic data** generated using political science-inspired rules. In a production deployment, real historical rally and election data would replace the synthetic dataset.
- The CNN crowd detection is **simulated** — in production, a pre-trained deep learning model (CSRNet, MCNN, etc.) with real image input would be used.
- All analyses are **pre-computed at startup** for the 8 demo rallies to ensure fast dashboard load times.

---

## 👨‍💻 Author

**Shashank Chakali**  
Smart Political Speech & Rally Analysis System — 2024

---

*Built with ❤️ using Python, Flask, and modern AI/ML techniques.*
