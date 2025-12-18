from __future__ import annotations
from typing import Dict, Any, List, Optional, Tuple
import logging

from transformers import pipeline, Pipeline
from backend.ia.configIA import IAConfig
from backend.ia.preProcesamiento import limpiarTextoBasico

# ============================================================
# 馃敡 LOGGING
# ============================================================
logger = logging.getLogger("NLPAnalyzer")
if not logger.handlers:
    import sys
    handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

# ============================================================
# 馃 EMOCIONES BASE (NUNCA "OTRO")
# ============================================================

EMO_MAP = {
    "joy": "alegría",
    "happy": "alegría",
    "happiness": "alegría",
    "sadness": "tristeza",
    "anger": "enojo",
    "fear": "miedo",
    "disgust": "enojo",
    "surprise": "sorpresa",
    "neutral": "neutral"
}

EMOCIONES_VALIDAS = {
    "alegría", "satisfacción", "motivación", "calma",
    "tristeza", "frustración", "agotamiento",
    "ansiedad", "enojo", "miedo", "neutral"
}

# ============================================================
# 馃О HELPERS
# ============================================================

def _trim(text: str, n: int) -> str:
    return text if len(text) <= n else text[:n].rsplit(" ", 1)[0]

def _meaningful(text: str) -> bool:
    return isinstance(text, str) and len(text.strip()) >= 3

# ============================================================
# 馃 MODELOS
# ============================================================

class ModelRegistry:
    def __init__(self, cfg: IAConfig):
        self.cfg = cfg
        self._sentiment: Optional[Pipeline] = None
        self._emotion: Optional[Pipeline] = None
        self._zeroshot: Optional[Pipeline] = None
        self._summarizer: Optional[Pipeline] = None

    def sentiment(self):
        if not self._sentiment:
            self._sentiment = pipeline(
                "sentiment-analysis",
                model=self.cfg.sentiment_model,
                truncation=True
            )
        return self._sentiment

    def emotion(self):
        if not self._emotion:
            self._emotion = pipeline(
                "text-classification",
                model=self.cfg.emotion_model,
                truncation=True
            )
        return self._emotion

    def zeroshot(self):
        if not self._zeroshot:
            self._zeroshot = pipeline(
                "zero-shot-classification",
                model=self.cfg.zeroshot_model,
                truncation=True
            )
        return self._zeroshot

    def summarizer(self):
        if not self._summarizer:
            self._summarizer = pipeline(
                "summarization",
                model=self.cfg.summarizer_model,
                truncation=True
            )
        return self._summarizer

# ============================================================
# 馃敺 ANALIZADOR PRINCIPAL
# ============================================================

class NLPAnalyzer:
    def __init__(self, cfg: Optional[IAConfig] = None):
        self.cfg = cfg or IAConfig()
        self.m = ModelRegistry(self.cfg)

    # --------------------------------------------------------
    # 馃 EMOCI脫N FINAL (NUNCA "OTRO")
    # --------------------------------------------------------
    def _resolver_emocion_final(
        self,
        emocion_modelo: str,
        sentimiento: str,
        nivel_estres: str,
        texto: str
    ) -> str:

        emocion_modelo = emocion_modelo.lower()

        if emocion_modelo in EMO_MAP:
            base = EMO_MAP[emocion_modelo]
        else:
            base = "neutral"

        texto = texto.lower()

        if sentimiento == "negative":
            if nivel_estres == "alto":
                return "agotamiento" if "agot" in texto else "frustración"
            if nivel_estres == "medio":
                return "ansiedad"
            return "tristeza"

        if sentimiento == "neutral":
            if nivel_estres == "alto":
                return "ansiedad"
            return "neutral"

        if sentimiento == "positive":
            if "orgullo" in texto or "logro" in texto:
                return "satisfacción"
            if "motiva" in texto:
                return "motivación"
            return "alegría"

        return "neutral"

    # --------------------------------------------------------
    # 馃攳 EMOCI脫N
    # --------------------------------------------------------
    def _emotion(self, text: str) -> Tuple[str, float]:
        out = self.m.emotion()(_trim(text, self.cfg.max_len_models))
        pred = out[0]
        return pred["label"], float(pred["score"])

    # --------------------------------------------------------
    # 馃敟 ESTR脡S
    # --------------------------------------------------------
    def _stress(self, text: str):
        out = self.m.sentiment()(_trim(text, self.cfg.max_len_models))
        label = out[0]["label"].upper()
        score = out[0]["score"]

        if "NEG" in label:
            return "alto", {"negative": score}
        if "POS" in label:
            return "bajo", {"positive": score}
        return "medio", {"neutral": score}

    # --------------------------------------------------------
    # 馃 CATEGOR脥AS
    # --------------------------------------------------------
    def _categories(self, text: str):
        out = self.m.zeroshot()(
            _trim(text, self.cfg.max_len_models),
            self.cfg.categorias,
            multi_label=True
        )
        return [
            {"label": l, "score": float(s)}
            for l, s in zip(out["labels"], out["scores"])
            if s >= self.cfg.min_score_categoria
        ]

    # --------------------------------------------------------
    # 馃摑 RESUMEN
    # --------------------------------------------------------
    def _summary(self, text: str) -> str:
        if len(text) < 120:
            return text
        out = self.m.summarizer()(
            _trim(text, self.cfg.max_len_summary),
            max_length=80,
            min_length=25,
            do_sample=False
        )
        return out[0]["summary_text"]



    # ========================================================
    # 馃殌 API PRINCIPAL
    # ========================================================
    def analyze_comment(self, text: str, meta: dict | None = None) -> Dict[str, Any]:
        meta = meta or {}
        txt = limpiarTextoBasico(text)

        emo_raw, emo_score = self._emotion(txt)
        stress_level, dist = self._stress(txt)

        sentimiento = (
            "negative" if stress_level == "alto"
            else "positive" if stress_level == "bajo"
            else "neutral"
        )

        emocion_final = self._resolver_emocion_final(
            emo_raw, sentimiento, stress_level, txt
        )

        return {
            "emotion": {"label": emocion_final, "score": emo_score},
            "stress": {"level": stress_level, "sentiment_dist": dist},
            "categories": self._categories(txt),
            "summary": self._summary(txt),
            "suggestion": self._generate_suggestion(stress_level, emocion_final, txt),
            "meta": meta
        }

    # --------------------------------------------------------
    # 馃挕 SUGERENCIAS
    # --------------------------------------------------------
    def _generate_suggestion(self, stress: str, emotion: str, text: str) -> str:
        if stress == "alto":
            return "Se recomienda intervención inmediata de RRHH y revisión de carga laboral."
        if stress == "medio":
            return "Monitorear el caso y mejorar comunicación con el equipo."
        if emotion in ["alegría", "motivación"]:
            return "Reforzar prácticas positivas y reconocer el desempleo."
        return "Seguimiento general recomendado."