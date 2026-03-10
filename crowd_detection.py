"""
Module 1: Crowd Detection CNN
Simulates crowd analysis from rally images using computer vision techniques.
"""

import numpy as np
import json
from PIL import Image, ImageDraw
import random
import math

class CrowdDetectionCNN:
    """
    Simulated CNN-based crowd detection and density estimation system.
    In production, this would use a pre-trained ResNet/VGG model with
    crowd counting heads (CSRNet, MCNN, etc.)
    """

    def __init__(self):
        self.model_name = "CrowdCountNet-v2"
        self.resolution = (224, 224)
        self.density_classes = ["Sparse", "Moderate", "Dense", "Massive", "Overflow"]
        self.engagement_metrics = {}

    def simulate_crowd_features(self, rally_name: str, seed: int = None) -> dict:
        """Simulate feature extraction from crowd image"""
        if seed:
            random.seed(seed)
            np.random.seed(seed)

        # Simulated CNN feature extraction
        raw_count = random.randint(5000, 150000)
        density_score = random.uniform(0.3, 0.98)

        # Segment the crowd into zones
        zones = {
            "front_stage": random.uniform(0.85, 0.99),
            "center_field": random.uniform(0.65, 0.90),
            "back_area": random.uniform(0.30, 0.70),
            "overflow_zones": random.uniform(0.10, 0.50),
            "standing_areas": random.uniform(0.55, 0.85)
        }

        # Demographic estimation from visual cues (simulated)
        demographics = {
            "youth_18_30": random.uniform(0.18, 0.32),
            "middle_aged_31_50": random.uniform(0.28, 0.42),
            "senior_51_plus": random.uniform(0.20, 0.35),
            "visible_signs_flags": random.randint(200, 5000),
            "seated_vs_standing_ratio": random.uniform(0.2, 0.8)
        }

        # Engagement indicators
        engagement = {
            "cheer_events_detected": random.randint(5, 45),
            "wave_patterns": random.randint(2, 15),
            "crowd_movement_score": random.uniform(0.4, 0.95),
            "attention_focus_score": random.uniform(0.55, 0.98),
            "exit_rate_per_minute": random.uniform(0.001, 0.015)
        }

        idx = min(int(density_score * len(self.density_classes)), len(self.density_classes) - 1)
        density_class = self.density_classes[idx]

        # Attendance authenticity score
        authenticity = self._calculate_authenticity(raw_count, density_score, engagement)

        result = {
            "rally_name": rally_name,
            "model": self.model_name,
            "estimated_attendance": raw_count,
            "density_score": round(density_score, 4),
            "density_class": density_class,
            "zone_occupancy": zones,
            "demographic_breakdown": demographics,
            "engagement_metrics": engagement,
            "authenticity_score": round(authenticity, 4),
            "confidence": round(random.uniform(0.82, 0.97), 4),
            "processing_time_ms": round(random.uniform(120, 450), 1)
        }

        self.engagement_metrics = result
        return result

    def _calculate_authenticity(self, count: int, density: float, engagement: dict) -> float:
        """Calculate how genuine the crowd engagement appears"""
        base = min(count / 100000, 1.0) * 0.3
        density_contrib = density * 0.25
        cheer_norm = min(engagement["cheer_events_detected"] / 45, 1.0) * 0.25
        movement_contrib = engagement["crowd_movement_score"] * 0.20
        return min(base + density_contrib + cheer_norm + movement_contrib, 1.0)

    def generate_heatmap_data(self, rows: int = 20, cols: int = 30) -> list:
        """Generate crowd density heatmap grid data"""
        heatmap = []
        center_r, center_c = rows // 2, cols // 2
        for r in range(rows):
            row_data = []
            for c in range(cols):
                dist = math.sqrt((r - center_r)**2 + (c - center_c)**2)
                max_dist = math.sqrt(center_r**2 + center_c**2)
                base_density = max(0, 1 - (dist / max_dist) * 0.8)
                noise = random.uniform(-0.15, 0.15)
                row_data.append(round(min(max(base_density + noise, 0), 1), 3))
            heatmap.append(row_data)
        return heatmap

    def analyze_multiple_rallies(self, rally_list: list) -> list:
        """Analyze multiple rallies and return comparative data"""
        results = []
        for i, rally in enumerate(rally_list):
            result = self.simulate_crowd_features(rally, seed=i * 42 + 7)
            results.append(result)
        return results


if __name__ == "__main__":
    detector = CrowdDetectionCNN()
    rallies = ["Capital City Main Rally", "Eastern District Rally", "Northern Suburbs Event",
               "Grand Sports Stadium", "University Campus Rally"]
    results = detector.analyze_multiple_rallies(rallies)
    for r in results:
        print(f"Rally: {r['rally_name']}")
        print(f"  Attendance: {r['estimated_attendance']:,}")
        print(f"  Density: {r['density_class']} ({r['density_score']:.2f})")
        print(f"  Engagement Auth Score: {r['authenticity_score']:.2f}")
        print()
