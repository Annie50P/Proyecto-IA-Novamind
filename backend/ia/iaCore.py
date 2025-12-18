from __future__ import annotations
from typing import Dict, Any, List, Optional, Tuple
import logging

from transformers import pipeline, Pipeline
from backend.ia.configIA import IAConfig
from backend.ia.preProcesamiento import limpiarTextoBasico

# ======================================================
# CONFIGURACIÓN DE LOGS
# ======================================================
logger = logging.getLogger("NLPAnalyzer")
if not logger.handlers:
    import sys
    handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

# ======================================================
# MAPEO DE EMOCIONES (HUMANAS Y CLARAS)
# ======================================================
EMOTION_MAP = {
    "joy": "alegría",
    "happy": "alegría",
    "happiness": "alegría",

    "sadness": "tristeza",
    "anger": "enojo",
    "fear": "miedo",
    "disgust": "rechazo",
    "surprise": "sorpresa",

    # emociones compuestas / humanas
    "frustration": "frustración",
    "stress": "agotamiento",
    "anxiety": "ansiedad",
    "burnout": "agotamiento",
    "tired": "agotamiento",
}

DEFAULT_EMOTION = "neutral"

def map_emotion(label: str) -> str:
    label = (label or "").lower().strip()
    return EMOTION_MAP.get(label, DEFAULT_EMOTION)

def meaningful(text: str) -> bool:
    return isinstance(text, str) and len(text.strip()) >= 4

def trim(text: str, max_len: int) -> str:
    text = text.strip()
    return text if len(text) <= max_len else text[:max_len].rsplit(" ", 1)[0]

# ======================================================
# REGISTRO DE MODELOS
# ======================================================
class ModelRegistry:
    def __init__(self, cfg: IAConfig):
        self.cfg = cfg
        self._sentiment = None
        self._emotion = None
        self._zeroshot = None
        self._summary = None

    def sentiment(self):
        if self._sentiment is None:
            logger.info("Cargando modelo de Sentiment Analysis")
            self._sentiment = pipeline(
                "sentiment-analysis",
                model=self.cfg.sentiment_model,
                device=-1,
                truncation=True
            )
        return self._sentiment

    def emotion(self):
        if self._emotion is None:
            logger.info("Cargando modelo de Emotion Detection")
            self._emotion = pipeline(
                "text-classification",
                model=self.cfg.emotion_model,
                device=-1,
                truncation=True
            )
        return self._emotion

    def zeroshot(self):
        if self._zeroshot is None:
            logger.info("Cargando modelo Zero-Shot")
            self._zeroshot = pipeline(
                "zero-shot-classification",
                model=self.cfg.zeroshot_model,
                device=-1,
                truncation=True
            )
        return self._zeroshot

    def summarizer(self):
        if self._summary is None:
            logger.info("Cargando modelo de Summarization")
            self._summary = pipeline(
                "summarization",
                model=self.cfg.summarizer_model,
                device=-1,
                truncation=True
            )
        return self._summary

# ======================================================
# ANALIZADOR PRINCIPAL
# ======================================================
class NLPAnalyzer:
    def __init__(self, cfg: Optional[IAConfig] = None):
        self.cfg = cfg or IAConfig()
        self.models = ModelRegistry(self.cfg)

    # --------------------------------------------------
    # EMOCIÓN
    # --------------------------------------------------
    def _detect_emotion(self, text: str) -> Tuple[str, float]:
        if not meaningful(text):
            return DEFAULT_EMOTION, 0.0

        try:
            result = self.models.emotion()(trim(text, self.cfg.max_len_models))
            label = result[0]["label"]
            score = float(result[0]["score"])
            return map_emotion(label), score
        except Exception:
            return DEFAULT_EMOTION, 0.0

    # --------------------------------------------------
    # ESTRÉS
    # --------------------------------------------------
    def _detect_stress(self, text: str):
        try:
            result = self.models.sentiment()(trim(text, self.cfg.max_len_models))[0]
            label = result["label"].upper()
            score = float(result["score"])

            sentiment = "neutral"
            if "NEG" in label:
                sentiment = "negative"
            elif "POS" in label:
                sentiment = "positive"

            stress_level = self.cfg.stress_map.get(sentiment, "medio")
            dist = {"positive": 0, "neutral": 0, "negative": 0}
            dist[sentiment] = score

            return stress_level, dist
        except Exception:
            return "medio", {"positive": 0, "neutral": 1, "negative": 0}

    # --------------------------------------------------
    # CATEGORÍAS
    # --------------------------------------------------
    def _detect_categories(self, text: str) -> List[str]:
        try:
            result = self.models.zeroshot()(
                trim(text, self.cfg.max_len_models),
                self.cfg.categorias,
                multi_label=True
            )

            return [
                label for label, score in zip(result["labels"], result["scores"])
                if score >= self.cfg.min_score_categoria
            ]
        except Exception:
            return []

    # --------------------------------------------------
    # RESUMEN
    # --------------------------------------------------
    def _summarize(self, text: str) -> str:
        if len(text) <= 140:
            return text

        try:
            result = self.models.summarizer()(
                trim(text, self.cfg.max_len_summary),
                max_length=80,
                min_length=30,
                do_sample=False
            )
            return result[0]["summary_text"]
        except Exception:
            return text[:160]

    # --------------------------------------------------
    # SUGERENCIAS INTELIGENTES (CORE)
    # --------------------------------------------------
    def _generate_suggestion(
        self,
        stress: str,
        emotion: str,
        categories: List[str],
        text: str
    ) -> str:

        text = text.lower()

        # ----------- ALTO ESTRÉS -----------
        if stress == "alto":
            if emotion in ["agotamiento", "ansiedad"]:
                return (
                    "El colaborador muestra señales claras de sobrecarga emocional. "
                    "Se recomienda una intervención prioritaria, revisión de carga laboral "
                    "y ofrecer apoyo inmediato."
                )

            if emotion in ["enojo", "frustración"]:
                return (
                    "Existe una posible acumulación de tensión. "
                    "Se sugiere una reunión de escucha activa para abordar el conflicto "
                    "antes de que escale."
                )

            if emotion == "tristeza":
                return (
                    "Se detecta desmotivación o malestar emocional. "
                    "Recomendable brindar acompañamiento y reforzar el reconocimiento."
                )

            return (
                "Nivel de estrés alto detectado. "
                "Se recomienda seguimiento cercano y acciones correctivas."
            )

        # ----------- ESTRÉS MEDIO -----------
        if stress == "medio":
            if emotion in ["ansiedad", "frustración"]:
                return (
                    "El colaborador muestra señales de alerta moderadas. "
                    "Se recomienda revisar procesos, comunicación y expectativas."
                )

            if emotion == "agotamiento":
                return (
                    "Podría existir desgaste progresivo. "
                    "Es recomendable evaluar pausas activas y balance de tareas."
                )

            return (
                "Situación estable pero con señales a monitorear. "
                "Se sugiere seguimiento preventivo."
            )

        # ----------- ESTRÉS BAJO -----------
        if stress == "bajo":
            if emotion in ["alegría", "satisfacción"]:
                return (
                    "Comentario positivo detectado. "
                    "Se recomienda reforzar las prácticas que generan bienestar."
                )

            if emotion == "neutral":
                return (
                    "Comentario sin señales de riesgo. "
                    "Mantener comunicación abierta."
                )

            return (
                "Estado general estable. "
                "No se requieren acciones inmediatas."
            )

        return "Mantener observación general."

    # --------------------------------------------------
    # API PRINCIPAL
    # --------------------------------------------------
    def analyze_comment(self, text: str, meta: dict | None = None) -> Dict[str, Any]:
        meta = meta or {}
        clean_text = limpiarTextoBasico(text)

        if not meaningful(clean_text):
            return {
                "emotion": {"label": DEFAULT_EMOTION, "score": 0.0},
                "stress": {"level": "bajo", "sentiment_dist": {"positive": 0, "neutral": 1, "negative": 0}},
                "categories": [],
                "summary": "",
                "suggestion": "Comentario insuficiente para análisis.",
                "meta": meta
            }

        emotion, emo_score = self._detect_emotion(clean_text)
        stress, dist = self._detect_stress(clean_text)
        categories = self._detect_categories(clean_text)
        summary = self._summarize(clean_text)

        return {
            "emotion": {"label": emotion, "score": emo_score},
            "stress": {"level": stress, "sentiment_dist": dist},
            "categories": [{"label": c} for c in categories],
            "summary": summary,
            "suggestion": self._generate_suggestion(stress, emotion, categories, clean_text),
            "meta": meta
        }
