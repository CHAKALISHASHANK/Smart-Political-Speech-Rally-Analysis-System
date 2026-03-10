"""
Module 4 & 5: Flask API Backend
Serves all analysis modules via REST API endpoints.
Powers the Election Insights Dashboard and Analyst UI.
"""

import json
import random
import math
import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

# ── Import our analysis modules ───────────────────────────────────────────────
from crowd_detection import CrowdDetectionCNN
from speech_analyzer import SpeechSentimentAnalyzer, SAMPLE_SPEECHES
from impact_model import ImpactPredictionModel

# ── App setup ─────────────────────────────────────────────────────────────────
app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)

# ── Initialize models (trained once at startup) ───────────────────────────────
print("Initializing Political Analysis System...")
crowd_detector = CrowdDetectionCNN()
speech_analyzer = SpeechSentimentAnalyzer()
impact_predictor = ImpactPredictionModel()
print("Training ML impact model...")
impact_predictor.train()
print("All models ready!\n")

# ── Pre-computed demo data ────────────────────────────────────────────────────
DEMO_RALLIES = [
    {"name": "Capital City Grand Rally",       "city": "Washington DC",   "date": "2024-10-15"},
    {"name": "Eastern Heartland Rally",        "city": "Philadelphia",    "date": "2024-10-18"},
    {"name": "Northern Suburbs Tour Stop",     "city": "Detroit",         "date": "2024-10-22"},
    {"name": "Southern States Mega Rally",    "city": "Atlanta",         "date": "2024-10-25"},
    {"name": "Western Coastal Event",          "city": "Los Angeles",     "date": "2024-10-28"},
    {"name": "University Campus Rally",        "city": "Columbus",        "date": "2024-11-01"},
    {"name": "Industrial Belt Rally",          "city": "Pittsburgh",      "date": "2024-11-03"},
    {"name": "Final Mile Championship Rally",  "city": "Miami",           "date": "2024-11-05"},
]

DEMO_CONTEXTS = [
    {"days_to_election": 21, "incumbent": 1, "battleground_state": 1,
     "media_coverage_index": 0.88, "opponent_recent_approval": 46, "economic_approval": 51},
    {"days_to_election": 18, "incumbent": 1, "battleground_state": 0,
     "media_coverage_index": 0.72, "opponent_recent_approval": 48, "economic_approval": 49},
    {"days_to_election": 14, "incumbent": 1, "battleground_state": 1,
     "media_coverage_index": 0.91, "opponent_recent_approval": 44, "economic_approval": 53},
    {"days_to_election": 11, "incumbent": 0, "battleground_state": 1,
     "media_coverage_index": 0.85, "opponent_recent_approval": 50, "economic_approval": 47},
    {"days_to_election": 8,  "incumbent": 0, "battleground_state": 0,
     "media_coverage_index": 0.79, "opponent_recent_approval": 52, "economic_approval": 48},
    {"days_to_election": 4,  "incumbent": 0, "battleground_state": 1,
     "media_coverage_index": 0.95, "opponent_recent_approval": 45, "economic_approval": 52},
    {"days_to_election": 2,  "incumbent": 1, "battleground_state": 1,
     "media_coverage_index": 0.97, "opponent_recent_approval": 43, "economic_approval": 54},
    {"days_to_election": 0,  "incumbent": 1, "battleground_state": 1,
     "media_coverage_index": 1.00, "opponent_recent_approval": 44, "economic_approval": 55},
]

def _precompute_all_analyses():
    """Pre-compute full analysis for all demo rallies"""
    results = []
    speech_keys = list(SAMPLE_SPEECHES.keys())
    for i, rally in enumerate(DEMO_RALLIES):
        crowd = crowd_detector.simulate_crowd_features(rally["name"], seed=i * 13 + 5)
        speech_key = speech_keys[i % len(speech_keys)]
        speech_text = SAMPLE_SPEECHES[speech_key]
        speech = speech_analyzer.analyze_speech(
            speech_text, speech_key, rally["name"], rally["date"])
        context = DEMO_CONTEXTS[i]
        impact = impact_predictor.predict(crowd, speech, context)
        results.append({
            "rally": rally,
            "crowd": crowd,
            "speech": speech,
            "impact": impact,
            "context": context
        })
    return results

print("Pre-computing rally analyses...")
ALL_ANALYSES = _precompute_all_analyses()
print(f"Computed {len(ALL_ANALYSES)} rally analyses.\n")


# ══════════════════════════════════════════════════════════════════════════════
# API ROUTES
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

# ── Overview ──────────────────────────────────────────────────────────────────
@app.route("/api/overview")
def api_overview():
    """Dashboard summary statistics"""
    total_attendance = sum(a["crowd"]["estimated_attendance"] for a in ALL_ANALYSES)
    avg_sentiment = sum(a["speech"]["overall_sentiment"]["overall_polarity"]
                        for a in ALL_ANALYSES) / len(ALL_ANALYSES)
    avg_impact = sum(a["impact"]["impact_score"] for a in ALL_ANALYSES) / len(ALL_ANALYSES)
    top_rally  = max(ALL_ANALYSES, key=lambda x: x["impact"]["impact_score"])
    top_swing  = max(ALL_ANALYSES, key=lambda x: x["impact"]["vote_swing_probability"])

    return jsonify({
        "total_rallies": len(ALL_ANALYSES),
        "total_attendance": total_attendance,
        "avg_sentiment": round(avg_sentiment, 4),
        "avg_impact_score": round(avg_impact, 4),
        "top_rally": {
            "name": top_rally["rally"]["name"],
            "city": top_rally["rally"]["city"],
            "impact_score": top_rally["impact"]["impact_score"]
        },
        "highest_swing_rally": {
            "name": top_swing["rally"]["name"],
            "swing_prob": top_swing["impact"]["vote_swing_probability"]
        },
        "model_accuracy": impact_predictor.training_history
    })

# ── All Rallies ───────────────────────────────────────────────────────────────
@app.route("/api/rallies")
def api_rallies():
    """List all rally data with key metrics"""
    rallies = []
    for a in ALL_ANALYSES:
        rallies.append({
            "name": a["rally"]["name"],
            "city": a["rally"]["city"],
            "date": a["rally"]["date"],
            "attendance": a["crowd"]["estimated_attendance"],
            "density_class": a["crowd"]["density_class"],
            "sentiment_label": a["speech"]["overall_sentiment"]["label"],
            "sentiment_score": a["speech"]["overall_sentiment"]["overall_polarity"],
            "impact_score": a["impact"]["impact_score"],
            "impact_level": a["impact"]["impact_level"],
            "swing_probability": a["impact"]["vote_swing_probability"],
            "media_reach": a["impact"]["predictions"]["media_reach_millions"],
            "social_virality": a["impact"]["predictions"]["social_virality_score"],
            "fundraising_lift": a["impact"]["predictions"]["fundraising_lift_pct"],
            "persuasion_score": a["speech"]["persuasion_score"],
            "days_to_election": a["context"]["days_to_election"]
        })
    return jsonify(rallies)

# ── Rally Detail ──────────────────────────────────────────────────────────────
@app.route("/api/rally/<int:idx>")
def api_rally_detail(idx):
    """Detailed analysis for a specific rally"""
    if idx < 0 or idx >= len(ALL_ANALYSES):
        return jsonify({"error": "Rally not found"}), 404
    a = ALL_ANALYSES[idx]
    return jsonify({
        "rally": a["rally"],
        "crowd": a["crowd"],
        "speech": {
            **a["speech"],
            "sentence_analysis": a["speech"]["sentence_analysis"][:10]
        },
        "impact": a["impact"],
        "context": a["context"]
    })

# ── Crowd Analysis ────────────────────────────────────────────────────────────
@app.route("/api/crowd")
def api_crowd():
    """Crowd data for all rallies"""
    return jsonify([{
        "rally": a["rally"]["name"],
        "city": a["rally"]["city"],
        "attendance": a["crowd"]["estimated_attendance"],
        "density_score": a["crowd"]["density_score"],
        "density_class": a["crowd"]["density_class"],
        "authenticity": a["crowd"]["authenticity_score"],
        "engagement": a["crowd"]["engagement_metrics"],
        "zones": a["crowd"]["zone_occupancy"],
        "demographics": a["crowd"]["demographic_breakdown"],
        "heatmap": crowd_detector.generate_heatmap_data(15, 20)
    } for a in ALL_ANALYSES])

# ── Sentiment ─────────────────────────────────────────────────────────────────
@app.route("/api/sentiment")
def api_sentiment():
    """Sentiment data for all rallies"""
    return jsonify([{
        "rally": a["rally"]["name"],
        "date": a["rally"]["date"],
        "polarity": a["speech"]["overall_sentiment"]["overall_polarity"],
        "subjectivity": a["speech"]["overall_sentiment"]["subjectivity"],
        "label": a["speech"]["overall_sentiment"]["label"],
        "positive_ratio": a["speech"]["overall_sentiment"]["positive_ratio"],
        "negative_ratio": a["speech"]["overall_sentiment"]["negative_ratio"],
        "neutral_ratio": a["speech"]["overall_sentiment"]["neutral_ratio"],
        "persuasion_score": a["speech"]["persuasion_score"],
        "topics": a["speech"]["topics"],
        "rhetorical_devices": a["speech"]["rhetorical_devices"],
        "word_frequency": a["speech"]["word_frequency"][:15],
        "key_quotes": a["speech"]["key_quotes"],
        "emotional_arc": a["speech"]["emotional_arc"]
    } for a in ALL_ANALYSES])

# ── Impact ────────────────────────────────────────────────────────────────────
@app.route("/api/impact")
def api_impact():
    """ML impact predictions for all rallies"""
    return jsonify([{
        "rally": a["rally"]["name"],
        "city": a["rally"]["city"],
        "date": a["rally"]["date"],
        "impact_score": a["impact"]["impact_score"],
        "impact_level": a["impact"]["impact_level"],
        "swing_probability": a["impact"]["vote_swing_probability"],
        "predictions": a["impact"]["predictions"],
        "top_factors": a["impact"]["top_impact_factors"],
        "confidence": a["impact"]["model_confidence"],
        "days_to_election": a["context"]["days_to_election"]
    } for a in ALL_ANALYSES])

# ── Feature Importance ────────────────────────────────────────────────────────
@app.route("/api/feature_importance")
def api_feature_importance():
    """Model feature importances"""
    return jsonify(impact_predictor.get_feature_importance_chart())

# ── Timeline ──────────────────────────────────────────────────────────────────
@app.route("/api/timeline")
def api_timeline():
    """Chronological data for timeline chart"""
    timeline = []
    for a in ALL_ANALYSES:
        timeline.append({
            "date": a["rally"]["date"],
            "rally": a["rally"]["name"],
            "city": a["rally"]["city"],
            "attendance": a["crowd"]["estimated_attendance"],
            "impact_score": a["impact"]["impact_score"],
            "sentiment": a["speech"]["overall_sentiment"]["overall_polarity"],
            "swing_prob": a["impact"]["vote_swing_probability"],
            "media_reach": a["impact"]["predictions"]["media_reach_millions"],
            "days_to_election": a["context"]["days_to_election"]
        })
    timeline.sort(key=lambda x: x["date"])
    return jsonify(timeline)

# ── Live Analyze ──────────────────────────────────────────────────────────────
@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    """Live analysis endpoint for Analyst UI"""
    data = request.json or {}
    speech_text = data.get("speech_text", list(SAMPLE_SPEECHES.values())[0])
    speaker     = data.get("speaker", "Analyst Test Speaker")
    rally_name  = data.get("rally_name", "Custom Analysis Rally")
    attendance  = int(data.get("attendance", 50000))
    days_elec   = int(data.get("days_to_election", 30))
    battleground = int(data.get("battleground", 1))

    # Run full pipeline
    crowd = crowd_detector.simulate_crowd_features(rally_name, seed=random.randint(1, 999))
    crowd["estimated_attendance"] = attendance

    speech = speech_analyzer.analyze_speech(speech_text, speaker, rally_name,
                                            data.get("date", "2024-11-05"))

    context = {
        "days_to_election": days_elec,
        "incumbent": int(data.get("incumbent", 0)),
        "battleground_state": battleground,
        "media_coverage_index": random.uniform(0.5, 0.95),
        "opponent_recent_approval": int(data.get("opponent_approval", 48)),
        "economic_approval": int(data.get("economic_approval", 50))
    }

    impact = impact_predictor.predict(crowd, speech, context)

    return jsonify({
        "crowd": crowd,
        "speech": {
            **speech,
            "sentence_analysis": speech["sentence_analysis"][:8]
        },
        "impact": impact,
        "context": context
    })

# ── Heatmap Data ──────────────────────────────────────────────────────────────
@app.route("/api/heatmap/<int:rally_idx>")
def api_heatmap(rally_idx):
    """Get crowd heatmap for a specific rally"""
    if rally_idx < 0 or rally_idx >= len(ALL_ANALYSES):
        rally_idx = 0
    random.seed(rally_idx * 7)
    return jsonify({
        "rally": ALL_ANALYSES[rally_idx]["rally"]["name"],
        "heatmap": crowd_detector.generate_heatmap_data(20, 30)
    })

# ── Election Forecast ─────────────────────────────────────────────────────────
@app.route("/api/forecast")
def api_forecast():
    """Aggregate election forecast based on all rally data"""
    avg_impact  = sum(a["impact"]["impact_score"] for a in ALL_ANALYSES) / len(ALL_ANALYSES)
    avg_swing   = sum(a["impact"]["vote_swing_probability"] for a in ALL_ANALYSES) / len(ALL_ANALYSES)
    avg_sent    = sum(a["speech"]["overall_sentiment"]["overall_polarity"] for a in ALL_ANALYSES) / len(ALL_ANALYSES)
    total_reach = sum(a["impact"]["predictions"]["media_reach_millions"] for a in ALL_ANALYSES)

    # Progressive polling curve (simulated)
    poll_curve = []
    base_lead  = round(random.uniform(1.5, 4.5), 1)
    for i, a in enumerate(sorted(ALL_ANALYSES, key=lambda x: x["rally"]["date"])):
        poll_change = a["impact"]["impact_score"] * random.uniform(-0.5, 1.2) - 0.1
        base_lead   = max(-5, min(10, base_lead + poll_change))
        poll_curve.append({
            "date": a["rally"]["date"],
            "polling_lead": round(base_lead, 2),
            "margin_of_error": round(random.uniform(2.0, 3.5), 1)
        })

    return jsonify({
        "overall_momentum": round(avg_impact, 4),
        "avg_swing_probability": round(avg_swing, 4),
        "avg_sentiment": round(avg_sent, 4),
        "total_media_reach_millions": round(total_reach, 1),
        "forecast_confidence": round(random.uniform(0.72, 0.89), 4),
        "projected_win_probability": round(min(0.35 + avg_impact * 0.5 + avg_swing * 0.2, 0.95), 4),
        "polling_curve": poll_curve,
        "key_states": [
            {"state": "Pennsylvania",  "lean": "Toss-Up",     "swing_prob": round(random.uniform(0.45, 0.55), 3)},
            {"state": "Michigan",      "lean": "Lean D",      "swing_prob": round(random.uniform(0.52, 0.62), 3)},
            {"state": "Wisconsin",     "lean": "Toss-Up",     "swing_prob": round(random.uniform(0.47, 0.53), 3)},
            {"state": "Georgia",       "lean": "Lean R",      "swing_prob": round(random.uniform(0.40, 0.50), 3)},
            {"state": "Arizona",       "lean": "Toss-Up",     "swing_prob": round(random.uniform(0.45, 0.55), 3)},
            {"state": "Nevada",        "lean": "Lean D",      "swing_prob": round(random.uniform(0.51, 0.58), 3)},
        ]
    })


if __name__ == "__main__":
    print("Starting Political Analysis API server...")
    print("Dashboard: http://localhost:5000")
    print("API Base : http://localhost:5000/api/")
    app.run(debug=True, host="0.0.0.0", port=5000)
