# ia/iaCore.py
from __future__ import annotations
from typing import Dict, Any, List, Iterable, Optional, Tuple
import logging

from transformers import pipeline, Pipeline
from backend.ia.configIA import IAConfig
from backend.ia.preProcesamiento import limpiarTextoBasico

logger = logging.getLogger("NLPAnalyzer")
if not logger.handlers:
    import sys
    h = logging.StreamHandler(sys.stdout)
    logger.addHandler(h)
logger.setLevel(logging.INFO)

def _trim(text: str, n: int) -> str:
    text = (text or "").strip()
    return text if len(text) <= n else text[:n].rsplit(" ", 1)[0]

def _meaningful(text: str) -> bool:
    return isinstance(text, str) and len(text.strip()) >= 3

class ModelRegistry:
    def __init__(self, cfg: IAConfig):
        self.cfg = cfg
        self._sentiment_pipe: Optional[Pipeline] = None
        self._emotion_pipe: Optional[Pipeline] = None
        self._zeroshot_pipe: Optional[Pipeline] = None
        self._summarizer_pipe: Optional[Pipeline] = None

    def sentiment(self) -> Pipeline:
        if self._sentiment_pipe is None:
            logger.info("Cargando modelo de Sentiment...")
            self._sentiment_pipe = pipeline("sentiment-analysis", model=self.cfg.sentiment_model, device=-1, truncation=True)
        return self._sentiment_pipe

    def emotion(self) -> Pipeline:
        if self._emotion_pipe is None:
            logger.info("Cargando modelo de Emotion...")
            # Sin top_k para obtener solo la etiqueta principal
            self._emotion_pipe = pipeline("text-classification", model=self.cfg.emotion_model, device=-1, truncation=True)
        return self._emotion_pipe

    def zeroshot(self) -> Pipeline:
        if self._zeroshot_pipe is None:
            logger.info("Cargando modelo Zero-shot...")
            self._zeroshot_pipe = pipeline("zero-shot-classification", model=self.cfg.zeroshot_model, device=-1, truncation=True)
        return self._zeroshot_pipe

    def summarizer(self) -> Pipeline:
        if self._summarizer_pipe is None:
            logger.info("Cargando modelo Summarization...")
            self._summarizer_pipe = pipeline("summarization", model=self.cfg.summarizer_model, device=-1, truncation=True)
        return self._summarizer_pipe

class NLPAnalyzer:
    def __init__(self, cfg: Optional[IAConfig] = None):
        self.cfg = cfg or IAConfig()
        self.m = ModelRegistry(self.cfg)

    def _emotion(self, text: str) -> Tuple[str, float]:
        if not _meaningful(text): return ("desconocida", 0.0)
        try:
            out = self.m.emotion()(_trim(text, self.cfg.max_len_models))
            # El modelo devuelve una lista con un diccionario
            if isinstance(out, list) and len(out) > 0:
                pred = out[0]
                if isinstance(pred, dict):
                    label = str(pred.get("label", "desconocida")).lower()
                    score = float(pred.get("score", 0.0))
                    return label, score
            return ("desconocida", 0.0)
        except Exception as e:
            logger.warning(f"Emotion fail: {e}")
            import traceback
            logger.warning(traceback.format_exc())
            return ("desconocida", 0.0)

    def _stress(self, text: str) -> Tuple[str, Dict[str,float]]:
        if not _meaningful(text): return ("bajo", {"positive":0.0,"neutral":1.0,"negative":0.0})
        try:
            out = self.m.sentiment()(_trim(text, self.cfg.max_len_models))
            if not isinstance(out, list) or len(out) == 0:
                return ("medio", {"positive":0.0,"neutral":1.0,"negative":0.0})

            label = str(out[0].get("label", "")).upper()
            score = float(out[0].get("score", 0.0))

            # Mapear etiquetas (el modelo devuelve NEG, POS, NEU)
            if label == "NEG" or "NEG" in label:
                sent = "negative"
            elif label == "POS" or "POS" in label:
                sent = "positive"
            elif label == "NEU" or "NEU" in label:
                sent = "neutral"
            else:
                sent = "neutral"

            level = self.cfg.stress_map.get(sent, "medio")
            dist = {"positive":0.0,"neutral":0.0,"negative":0.0}
            dist[sent] = score

            # refuerzo por palabras clave
            low = text.lower()
            if level != "alto" and any(k in low for k in self.cfg.stress_keywords["alto"]):
                level = "alto"
            elif level == "bajo" and any(k in low for k in self.cfg.stress_keywords["medio"]):
                level = "medio"

            return level, dist
        except Exception as e:
            logger.warning(f"Stress fail: {e}")
            import traceback
            logger.warning(traceback.format_exc())
            return ("medio", {"positive":0.0,"neutral":1.0,"negative":0.0})

    def _categories(self, text: str, top_k: int = 3) -> List[Tuple[str, float]]:
        if not _meaningful(text): return []
        try:
            out = self.m.zeroshot()(_trim(text, self.cfg.max_len_models), self.cfg.categorias, multi_label=True)
            pairs = [(lab, float(scr)) for lab, scr in zip(out["labels"], out["scores"]) if scr >= self.cfg.min_score_categoria]
            pairs.sort(key=lambda x: x[1], reverse=True)
            return pairs[:top_k]
        except Exception as e:
            logger.warning(f"Zero-shot fail: {e}")
            return []

    def _summary(self, text: str) -> str:
        if not _meaningful(text): return ""
        if len(text) <= 140: return text
        try:
            out = self.m.summarizer()(_trim(text, self.cfg.max_len_summary), max_length=80, min_length=25, do_sample=False)
            return out[0]["summary_text"].strip()
        except Exception as e:
            logger.warning(f"Summarize fail: {e}")
            return _trim(text, 160)

    def _generate_personalized_suggestion(self, stress_level: str, emotion: str, categories: List[str], text: str) -> str:
        """Genera sugerencias personalizadas basadas en múltiples factores"""

        text_lower = text.lower()

        # Análisis de palabras clave específicas
        menciona_jefe = any(word in text_lower for word in ["jefe", "líder", "manager", "supervisor", "gerente"])
        menciona_equipo = any(word in text_lower for word in ["equipo", "compañeros", "colaboradores", "grupo"])
        menciona_tiempo = any(word in text_lower for word in ["tiempo", "horas", "horario", "plazo", "urgente"])
        menciona_salario = any(word in text_lower for word in ["salario", "sueldo", "pago", "remuneración", "dinero"])
        menciona_herramientas = any(word in text_lower for word in ["herramientas", "software", "sistema", "tecnología", "recursos"])
        menciona_capacitacion = any(word in text_lower for word in ["capacitación", "formación", "entrenamiento", "aprender", "curso"])

        # CASOS DE ESTRÉS ALTO (Priorizar palabras clave sobre categorías)
        if stress_level == "alto":
            # PRIORIDAD 1: Casos críticos por palabras clave
            if menciona_salario:
                return "SENSIBLE: Reunión confidencial con RRHH para revisar compensación. Benchmarking salarial. Evaluar ajuste o plan de carrera."

            # PRIORIDAD 2: Problemas de comunicación con liderazgo
            if menciona_jefe and ("comunicación" in categories or "liderazgo" in categories):
                return "PRIORITARIO: Mediar comunicación con liderazgo directo. Establecer canales claros y frecuencia de feedback. Coaching para el líder."

            # PRIORIDAD 3: Conflictos de equipo
            if "conflictos internos" in categories or (menciona_equipo and any(word in text_lower for word in ["tensión", "conflicto", "problema", "pelea", "discusión"])):
                return "CRÍTICO: Intervención mediadora urgente. Sesión de team building. Evaluar separación temporal de equipos si es necesario."

            # PRIORIDAD 4: Necesidad de formación/capacitación
            if menciona_capacitacion or "formación/capacitación" in categories:
                return "PRIORITARIO: Ofrecer plan de desarrollo personalizado urgente. Cursos, mentoring o certificaciones. Invertir en crecimiento profesional."

            # PRIORIDAD 5: Herramientas y tecnología
            if menciona_herramientas or "tecnología/herramientas" in categories:
                return "ACCIÓN INMEDIATA: Evaluar y proveer herramientas necesarias. Consultar con IT/Procurement. Budget para equipamiento urgente."

            # PRIORIDAD 7: Balance vida-trabajo
            if menciona_tiempo and any(word in text_lower for word in ["familia", "horas", "horario", "descanso", "vida"]):
                return "URGENTE: Revisar horarios y expectativas. Implementar políticas de desconexión. Evaluar trabajo remoto/híbrido. Respetar horarios."

            # PRIORIDAD 9: Sobrecarga con mención temporal
            if (menciona_tiempo or "sobrecarga laboral" in categories) and any(word in text_lower for word in ["plazo", "urgente", "imposible", "mucho", "demasiado"]):
                return "URGENTE: Redistribuir tareas inmediatamente. Reunión 1:1 para revisar plazos y prioridades. Considerar apoyo temporal."

            # PRIORIDAD 10: Comunicación general
            if "comunicación" in categories:
                return "PRIORITARIO: Implementar reuniones 1:1 semanales. Crear canales de comunicación abiertos y seguros. Revisar dinámicas de equipo."

            # PRIORIDAD 11: Recursos insuficientes
            if "recursos insuficientes" in categories:
                return "ACCIÓN INMEDIATA: Reunión para identificar recursos faltantes (personal, herramientas, presupuesto). Plan de adquisición prioritario."

            # Caso genérico alto estrés
            if emotion in ["fear", "sadness"]:
                return "PRIORITARIO: Sesión 1:1 inmediata. Considerar apoyo psicológico (EAP). Identificar y eliminar factores estresantes. Seguimiento semanal."
            elif emotion in ["anger", "disgust"]:
                return "URGENTE: Reunión inmediata para escuchar preocupaciones. Tomar acción concreta en 48h. Plan de mejora documentado."
            else:
                return "ALTO ESTRÉS: Agendar reunión urgente. Identificar causas específicas. Plan de acción inmediato con seguimiento semanal."

        # CASOS DE ESTRÉS MEDIO
        elif stress_level == "medio":
            # PRIORIDAD 1: Formación/capacitación
            if "formación/capacitación" in categories or menciona_capacitacion:
                return "Ofrecer plan de desarrollo personalizado. Cursos, mentoring o certificaciones. Invertir en crecimiento profesional."

            # PRIORIDAD 2: Tecnología/herramientas
            if "tecnología/herramientas" in categories or menciona_herramientas:
                return "Evaluar upgrade de herramientas. Capacitación en sistemas actuales. Escuchar necesidades tecnológicas específicas."

            # PRIORIDAD 3: Procesos
            if "procesos" in categories:
                return "Revisar y simplificar procesos burocráticos. Sesión de mejora continua. Implementar sugerencias del equipo."

            # PRIORIDAD 4: Comunicación
            if "comunicación" in categories:
                return "Mejorar flujos de información. Reuniones de equipo más efectivas. Canales claros para dudas y feedback."

            # Caso genérico medio estrés
            if emotion in ["fear", "sadness"]:
                return "Monitorear de cerca. Check-in mensual. Identificar tendencias antes que escalen. Crear espacio de confianza."
            else:
                return "Seguimiento mensual. Abrir canales de feedback bidireccional. Prevenir escalamiento a alto estrés."

        # CASOS DE ESTRÉS BAJO (positivos)
        else:
            # Satisfacción general
            if "satisfacción general" in categories:
                return "¡Excelente! Documentar qué funciona bien. Replicar prácticas exitosas. Reconocimiento público del buen ambiente."

            # Motivación
            if "motivación" in categories:
                return "Aprovechar momentum positivo. Ofrecer nuevos retos o proyectos. Considerar para liderazgo o mentoría de otros."

            # Reconocimiento
            if "reconocimiento" in categories:
                if emotion in ["joy", "happiness"]:
                    return "Mantener cultura de reconocimiento. Celebrar logros públicamente. Sistema de rewards formal para reforzar."
                return "Continuar reconociendo contribuciones. Crear programa de reconocimiento peer-to-peer. Premiar excelencia."

            # Ambiente laboral
            if "ambiente laboral" in categories:
                return "Ambiente saludable. Mantener prácticas actuales. Entrevistar para identificar qué genera bienestar y replicarlo."

            # Liderazgo positivo
            if "liderazgo" in categories:
                return "Liderazgo efectivo detectado. Benchmark de buenas prácticas. Considerar para mentoría de otros líderes."

            # Caso genérico bajo estrés
            if emotion in ["joy", "happiness"]:
                return "Empleado satisfecho. Reforzar lo que funciona. Caso de estudio para buenas prácticas organizacionales."
            else:
                return "Situación estable. Mantener comunicación abierta. Seguimiento trimestral para mantener bienestar."

        # Fallback general
        return "Continuar seguimiento. Mantener canales de comunicación abiertos. Revisar en próxima evaluación."

    # ----------- API pública -----------
    def analyze_comment(self, text: str, meta: dict | None = None) -> Dict[str, Any]:
        meta = meta or {}
        txt = limpiarTextoBasico(text or "")
        if not _meaningful(txt):
            return {
                "emotion": {"label":"desconocida","score":0.0},
                "stress": {"level":"bajo","sentiment_dist":{"positive":0.0,"neutral":1.0,"negative":0.0}},
                "categories": [], "summary":"", "suggestion":"Comentario no informativo; solicita más detalle.",
                "meta": meta
            }
        emo_label, emo_score = self._emotion(txt)
        stress_level, dist = self._stress(txt)
        cats = self._categories(txt)
        summary = self._summary(txt)
        top_labels = [c for c,_ in cats]

        # Sistema de sugerencias personalizadas mejorado
        suggestion = self._generate_personalized_suggestion(stress_level, emo_label, top_labels, txt)

        meta_out = dict(meta)
        if "comentario" in meta_out and "comentario_original" not in meta_out:
            meta_out["comentario_original"] = meta_out.get("comentario", "")

        return {
            "emotion": {"label": emo_label, "score": emo_score},
            "stress": {"level": stress_level, "sentiment_dist": dist},
            "categories": [{"label": c, "score": s} for c, s in cats],
            "summary": summary,
            "suggestion": suggestion,
            "meta": meta_out
        }

    def batch_analyze(self, rows: Iterable[dict], text_key: str = "comentario", meta_keys: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        meta_keys = meta_keys or ["departamento","equipo","fecha","comentario"]
        out: List[Dict[str, Any]] = []
        for i, row in enumerate(rows):
            try:
                txt = str(row.get(text_key, "") or "")
                meta = {k: row.get(k) for k in meta_keys if k in row}
                out.append(self.analyze_comment(txt, meta))
            except Exception as e:
                logger.error(f"Fila {i} falló: {e}")
                out.append({
                    "emotion":{"label":"error","score":0.0},
                    "stress":{"level":"desconocido","sentiment_dist":{}},
                    "categories":[], "summary":"", "suggestion":"No se pudo analizar.",
                    "meta":{"row_index": i, "error": str(e)}
                })
        return out
