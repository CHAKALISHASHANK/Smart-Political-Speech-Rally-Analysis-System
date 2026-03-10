"""
Module 2: NLP Speech Sentiment Analyzer
Processes political speeches using NLP techniques including sentiment analysis,
topic modeling, rhetoric detection, and emotional arc tracking.
"""

import re
import json
import random
import math
from collections import Counter, defaultdict
from textblob import TextBlob


class SpeechSentimentAnalyzer:
    """
    Advanced NLP pipeline for political speech analysis.
    Performs sentence-level sentiment, topic extraction, rhetoric detection,
    persuasion scoring, and emotional trajectory mapping.
    """

    POLITICAL_TOPICS = {
        "economy": ["economy", "jobs", "taxes", "growth", "inflation", "workers",
                    "wages", "business", "trade", "economic", "fiscal", "budget", "debt"],
        "healthcare": ["health", "hospital", "medicine", "insurance", "care", "doctors",
                       "patients", "treatment", "affordable", "coverage", "medical"],
        "security": ["security", "military", "border", "defense", "police", "safety",
                     "crime", "terrorism", "threat", "protect", "law", "order", "army"],
        "education": ["education", "schools", "students", "teachers", "university",
                      "learning", "college", "academic", "tuition", "scholarship"],
        "environment": ["climate", "environment", "green", "clean", "pollution", "energy",
                        "renewable", "carbon", "sustainable", "nature", "conservation"],
        "unity": ["together", "unity", "nation", "people", "united", "community",
                  "strength", "common", "shared", "collective", "team", "us"],
        "opposition": ["opponent", "corrupt", "failure", "wrong", "mistake", "problem",
                       "crisis", "blame", "disaster", "incompetent", "weak"]
    }

    RHETORICAL_DEVICES = {
        "anaphora": r'\b(\w+)\b.{0,50}\b\1\b.{0,50}\b\1\b',
        "tricolon": r'(\w[\w\s]*),\s*(\w[\w\s]*),\s*and\s+(\w[\w\s]*)',
        "question": r'\?',
        "exclamation": r'!',
        "metaphor_indicators": ["like a", "as strong as", "is a", "are the", "we are"]
    }

    EMOTIONAL_KEYWORDS = {
        "hope": ["hope", "dream", "future", "better", "brighter", "promise", "vision"],
        "fear": ["danger", "threat", "risk", "crisis", "warning", "afraid", "worried"],
        "anger": ["angry", "outrage", "unacceptable", "enough", "demand", "fight", "enough"],
        "pride": ["proud", "great", "strong", "achievement", "success", "victory", "honor"],
        "compassion": ["children", "families", "suffering", "help", "care", "support", "together"]
    }

    def __init__(self):
        self.speeches_analyzed = []

    def preprocess_text(self, text: str) -> list:
        """Clean and tokenize speech into sentences"""
        text = re.sub(r'\s+', ' ', text).strip()
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if len(s.strip()) > 10]

    def analyze_sentence_sentiment(self, sentence: str) -> dict:
        """Get sentiment for a single sentence"""
        blob = TextBlob(sentence)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity

        label = "Positive" if polarity > 0.05 else "Negative" if polarity < -0.05 else "Neutral"
        return {
            "text": sentence[:100] + ("..." if len(sentence) > 100 else ""),
            "polarity": round(polarity, 4),
            "subjectivity": round(subjectivity, 4),
            "label": label,
            "intensity": round(abs(polarity), 4)
        }

    def extract_topics(self, text: str) -> dict:
        """Identify political topics mentioned in speech"""
        text_lower = text.lower()
        topic_scores = {}

        for topic, keywords in self.POLITICAL_TOPICS.items():
            count = sum(text_lower.count(kw) for kw in keywords)
            total_words = len(text_lower.split())
            score = min(count / max(total_words * 0.01, 1), 1.0)
            topic_scores[topic] = round(score, 4)

        return topic_scores

    def detect_rhetorical_devices(self, text: str) -> dict:
        """Count rhetorical devices used in the speech"""
        devices = {
            "questions": len(re.findall(r'\?', text)),
            "exclamations": len(re.findall(r'!', text)),
            "repetitions": len(re.findall(r'\b(\w{4,})\b(?=.*\b\1\b)', text, re.IGNORECASE)),
            "three_part_lists": len(re.findall(
                r'(\w[\w\s]{2,15}),\s*(\w[\w\s]{2,15}),\s*and\s+(\w[\w\s]{2,15})', text)),
            "metaphors": sum(1 for m in self.RHETORICAL_DEVICES["metaphor_indicators"]
                           if m.lower() in text.lower())
        }
        return devices

    def track_emotional_arc(self, sentences: list) -> list:
        """Track emotional progression throughout the speech"""
        arc = []
        window = max(1, len(sentences) // 20)  # 20 points along the speech

        for i in range(0, len(sentences), max(1, len(sentences) // 20)):
            chunk = sentences[i:i + window]
            chunk_text = " ".join(s["text"] for s in chunk)

            emotion_scores = {}
            for emotion, keywords in self.EMOTIONAL_KEYWORDS.items():
                score = sum(chunk_text.lower().count(kw) for kw in keywords)
                emotion_scores[emotion] = score

            dominant = max(emotion_scores, key=emotion_scores.get) if any(
                v > 0 for v in emotion_scores.values()) else "neutral"

            arc.append({
                "position": round(i / max(len(sentences), 1), 3),
                "dominant_emotion": dominant,
                "emotion_scores": emotion_scores,
                "avg_sentiment": round(sum(
                    s.get("polarity", 0) for s in chunk) / max(len(chunk), 1), 4)
            })

        return arc

    def calculate_persuasion_score(self, analysis: dict) -> float:
        """Calculate overall persuasion effectiveness score"""
        rhetoric = analysis["rhetorical_devices"]
        sentiment = analysis["overall_sentiment"]
        topics = analysis["topics"]

        # Scoring components
        rhetoric_score = min((
            rhetoric["questions"] * 0.5 +
            rhetoric["exclamations"] * 0.3 +
            rhetoric["three_part_lists"] * 1.5
        ) / 20, 1.0)

        diversity_score = len([t for t, s in topics.items() if s > 0.05]) / len(topics)
        sentiment_score = abs(sentiment["overall_polarity"]) * 0.7 + sentiment["consistency"] * 0.3

        return round((rhetoric_score * 0.3 + diversity_score * 0.35 + sentiment_score * 0.35), 4)

    def generate_key_quotes(self, sentences: list, top_n: int = 5) -> list:
        """Extract most impactful quotes from speech"""
        scored = []
        for s in sentences:
            sentence_text = s["text"]
            impact = (abs(s["polarity"]) * 0.4 +
                     s["subjectivity"] * 0.3 +
                     min(len(sentence_text) / 200, 1.0) * 0.3)
            scored.append((sentence_text, impact))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [{"quote": q[:200], "impact_score": round(s, 4)}
                for q, s in scored[:top_n]]

    def extract_word_frequency(self, text: str, top_n: int = 30) -> list:
        """Get most frequent meaningful words"""
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
                    'for', 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were',
                    'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
                    'will', 'would', 'could', 'should', 'may', 'might', 'shall', 'can',
                    'our', 'we', 'us', 'i', 'you', 'they', 'he', 'she', 'it', 'this',
                    'that', 'these', 'those', 'not', 'my', 'your', 'their', 'its'}

        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        filtered = [w for w in words if w not in stopwords]
        freq = Counter(filtered).most_common(top_n)
        return [{"word": w, "count": c} for w, c in freq]

    def analyze_speech(self, speech_text: str, speaker: str, rally_name: str,
                       date: str = "2024-01-01") -> dict:
        """Full pipeline: analyze a complete political speech"""
        sentences_raw = self.preprocess_text(speech_text)
        analyzed_sentences = [self.analyze_sentence_sentiment(s) for s in sentences_raw]

        positive = [s for s in analyzed_sentences if s["label"] == "Positive"]
        negative = [s for s in analyzed_sentences if s["label"] == "Negative"]
        neutral  = [s for s in analyzed_sentences if s["label"] == "Neutral"]

        all_polarities = [s["polarity"] for s in analyzed_sentences]
        overall_polarity = sum(all_polarities) / max(len(all_polarities), 1)
        std_dev = math.sqrt(sum((p - overall_polarity)**2 for p in all_polarities) /
                           max(len(all_polarities), 1))
        consistency = max(0, 1 - std_dev)

        topics = self.extract_topics(speech_text)
        rhetoric = self.detect_rhetorical_devices(speech_text)
        emotional_arc = self.track_emotional_arc(analyzed_sentences)
        word_freq = self.extract_word_frequency(speech_text)
        key_quotes = self.generate_key_quotes(analyzed_sentences)

        result = {
            "speaker": speaker,
            "rally_name": rally_name,
            "date": date,
            "word_count": len(speech_text.split()),
            "sentence_count": len(sentences_raw),
            "overall_sentiment": {
                "overall_polarity": round(overall_polarity, 4),
                "subjectivity": round(sum(s["subjectivity"] for s in analyzed_sentences) /
                                     max(len(analyzed_sentences), 1), 4),
                "label": "Positive" if overall_polarity > 0.02 else
                         "Negative" if overall_polarity < -0.02 else "Neutral",
                "consistency": round(consistency, 4),
                "positive_ratio": round(len(positive) / max(len(analyzed_sentences), 1), 4),
                "negative_ratio": round(len(negative) / max(len(analyzed_sentences), 1), 4),
                "neutral_ratio": round(len(neutral) / max(len(analyzed_sentences), 1), 4)
            },
            "topics": topics,
            "rhetorical_devices": rhetoric,
            "emotional_arc": emotional_arc,
            "word_frequency": word_freq,
            "key_quotes": key_quotes,
            "sentence_analysis": analyzed_sentences[:20]  # First 20 for API response
        }

        result["persuasion_score"] = self.calculate_persuasion_score(result)
        self.speeches_analyzed.append(result)
        return result


# ── Sample speeches for demonstration ────────────────────────────────────────
SAMPLE_SPEECHES = {
    "Leader A - Rally Speech": """
    My fellow citizens! Today we stand together at a defining moment for our great nation.
    The future belongs to those who believe in the power of our dreams. We will build stronger
    roads, better schools, and healthier communities. Our economy has never been stronger and
    it will continue to grow because of your hard work. We must protect our families, our jobs,
    and our way of life. The opposition has failed you. They had their chance and they chose
    corruption over progress. We choose hope. We choose strength. We choose the future!
    Together we will create millions of new jobs. Together we will fix our broken healthcare
    system. Together we will ensure every child gets a quality education. The time for change
    is now. The time for action is today. The time for victory is ours! I believe in you.
    I believe in this nation. And I know that together, there is absolutely nothing we cannot
    achieve. Our best days are not behind us - they are ahead of us, waiting for us to seize them.
    Thank you, God bless you, and God bless our great nation!
    """,

    "Leader B - Economic Speech": """
    We face serious economic challenges today. Inflation has hurt working families. Prices are
    too high and wages have not kept pace. This is unacceptable. The previous government made
    terrible decisions that have damaged our economy. But we have a plan. A real plan with
    real solutions. First, we will cut taxes for the middle class. Second, we will invest in
    infrastructure creating three million jobs. Third, we will renegotiate trade deals that
    hurt our workers. Our businesses deserve better. Our farmers deserve better. Our workers
    deserve better. I have met thousands of families struggling to pay their bills. I have
    seen the hardship in their eyes. This cannot continue. We will restore economic dignity
    to every American family. Healthcare costs are crushing people. Education debt is
    suffocating our young people. The climate crisis threatens our future. We will address
    all of these challenges with bold, progressive policies. The wealthy must pay their fair
    share. Corporations must invest in their communities. We will build an economy that works
    for everyone, not just those at the top.
    """,

    "Leader C - Unity Speech": """
    What unites us is far greater than what divides us. We are one people, one nation, one
    community bound together by shared values and common dreams. Yes, we have disagreements.
    Yes, we see things differently sometimes. But at the end of the day, every parent wants
    their children to be safe and have opportunities. Every worker wants to earn a fair wage.
    Every family wants good healthcare and quality schools. These are not partisan issues.
    These are human issues. Security for our families must be paramount. Our military is
    the finest in the world and we will keep it that way. We will secure our borders while
    remaining a beacon of hope for those fleeing persecution. Our environment must be protected
    for future generations. Clean air, clean water, and renewable energy are not luxuries -
    they are necessities. I call on all citizens, regardless of party, to join together in
    building the nation we all know is possible. United we are unstoppable. Divided we fall.
    The choice is clear. Let us choose unity. Let us choose progress together.
    """
}


if __name__ == "__main__":
    analyzer = SpeechSentimentAnalyzer()
    for title, speech in list(SAMPLE_SPEECHES.items())[:2]:
        result = analyzer.analyze_speech(speech, title, "Demo Rally 2024", "2024-01-01")
        print(f"\n{'='*60}")
        print(f"Speaker: {result['speaker']}")
        print(f"Words: {result['word_count']} | Sentences: {result['sentence_count']}")
        print(f"Overall Sentiment: {result['overall_sentiment']['label']} "
              f"({result['overall_sentiment']['overall_polarity']:.3f})")
        print(f"Persuasion Score: {result['persuasion_score']:.3f}")
        print(f"Top Topics: {sorted(result['topics'].items(), key=lambda x: -x[1])[:3]}")
