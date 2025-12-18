# ia/iaAgent.py
"""
Agente Autónomo de Bienestar Laboral

Este módulo implementa la lógica de decisión del agente que decide:
- Si profundizar con preguntas guiadas
- Qué preguntas hacer según contexto
- Cuándo generar insights para RRHH
- Cuándo cerrar o escalar conversaciones

NO es un chatbot genérico. Es un sistema de detección de bloqueos organizacionales.
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional, Tuple
import logging
from datetime import datetime

from backend.ia.iaCore import NLPAnalyzer
from backend.ia.preProcesamiento import limpiarTextoBasico

logger = logging.getLogger("AgenteAutonomo")
logger.setLevel(logging.INFO)


# ============================================================
# 🔵 CONFIGURACIÓN DEL AGENTE
# ============================================================

class AgenteConfig:
    """Configuración del comportamiento del agente"""

    # Umbrales para decidir si profundizar
    UMBRAL_ESTRES_ALTO = 0.7  # Si sentimiento negativo >0.7
    UMBRAL_EMOCION_NEGATIVA = 0.75  # Si emoción negativa >0.75

    # Categorías que requieren seguimiento
    CATEGORIAS_CRITICAS = {
        "sobrecarga laboral",
        "liderazgo",
        "conflictos internos",
        "recursos insuficientes",
        "comunicación"
    }

    # Palabras clave de bloqueo
    KEYWORDS_BLOQUEO = [
        "nunca", "siempre", "meses", "nadie responde", "no responde",
        "no hace nada", "ignora", "sin respuesta", "esperando",
        "prometieron", "dijeron que", "nunca llegó", "no cumplieron"
    ]

    # Palabras clave de persistencia
    KEYWORDS_PERSISTENCIA = [
        "otra vez", "de nuevo", "sigue", "continúa", "todavía",
        "ya intenté", "ya hablé", "ya pedí", "hace meses", "hace tiempo"
    ]

    # Límites de conversación
    MAX_MENSAJES_AGENTE = 6  # Máximo 6 preguntas
    MIN_MENSAJES_PARA_INSIGHT = 2  # Mínimo 2 intercambios para generar insight

    # Niveles de riesgo
    RIESGO_BAJO = "bajo"
    RIESGO_MEDIO = "medio"
    RIESGO_ALTO = "alto"
    RIESGO_CRITICO = "critico"


# ============================================================
# 🔵 ESTRATEGIAS DE PREGUNTAS
# ============================================================

class EstrategiasPreguntas:
    """Generador de preguntas contextuales basadas en categorías"""

    @staticmethod
    def sobrecarga_laboral(contexto: dict) -> List[str]:
        return [
            "Oye, ¿has podido hablar con tu jefe sobre esto?",
            "¿Desde cuándo te sientes así con la carga de trabajo?",
            "¿Qué es lo que más te está pesando ahora mismo?",
            "¿Te han dado algún tipo de apoyo o ayuda?",
            "¿Has hablado antes con alguien de RRHH sobre esta situación?"
        ]

    @staticmethod
    def liderazgo(contexto: dict) -> List[str]:
        return [
            "¿Has podido platicar con tu jefe sobre esto?",
            "¿Tu líder te da feedback seguido o casi no?",
            "¿Desde cuándo está pasando esto?",
            "¿Tu jefe sabe cómo te sientes?",
            "¿Has intentado reportarlo con RRHH?",
            "Cuando intentas hablar con tu jefe, ¿qué pasa?"
        ]

    @staticmethod
    def recursos_insuficientes(contexto: dict) -> List[str]:
        return [
            "¿Ya pediste lo que necesitas?",
            "¿A quién se lo pediste?",
            "¿Te dijeron algo o te dejaron en visto?",
            "¿Cuánto tiempo llevas esperando?",
            "¿Esto te está frenando en tu trabajo?"
        ]

    @staticmethod
    def comunicacion(contexto: dict) -> List[str]:
        return [
            "¿Has intentado hablarlo directo con la persona?",
            "¿Cómo le has hecho para comunicarte? ¿Email, chat, presencial?",
            "¿Tu equipo o tu jefe saben de esto?",
            "¿Es la primera vez que pasa o ya es seguido?",
            "¿Te han respondido algo?"
        ]

    @staticmethod
    def conflictos_internos(contexto: dict) -> List[str]:
        return [
            "¿Has intentado hablarlo directamente con esa persona?",
            "¿Tu jefe sabe que esto está pasando?",
            "¿Desde cuándo viene este rollo?",
            "¿Te afecta en tu día a día en el trabajo?",
            "¿Has pedido ayuda a RRHH o a alguien más?"
        ]

    @staticmethod
    def equilibrio_vida_trabajo(contexto: dict) -> List[str]:
        return [
            "¿Es algo reciente o ya llevas tiempo sintiéndote así?",
            "¿Has hablado con tu jefe sobre ajustar horarios o algo?",
            "¿Qué es lo que más te tensiona?",
            "¿Has intentado poner límites o se complica por tu puesto?"
        ]

    @staticmethod
    def generica(contexto: dict) -> List[str]:
        """Preguntas genéricas para casos no categorizados"""
        return [
            "Oye, ¿ya intentaste hacer algo para resolverlo?",
            "¿Alguien más de tu equipo está pasando por algo parecido?",
            "¿Desde cuándo está pasando esto?",
            "¿Qué crees que te ayudaría más?",
            "¿Has podido platicarlo con alguien de tu equipo o con tu jefe?"
        ]


# ============================================================
# 🔵 DETECTOR DE BLOQUEOS
# ============================================================

class DetectorBloqueos:
    """Detecta bloqueos organizacionales en respuestas del empleado"""

    @staticmethod
    def detectar(respuesta: str, contexto_previo: List[dict]) -> dict:
        """
        Analiza respuesta para detectar bloqueos organizacionales

        Returns:
            {
                "hay_bloqueo": bool,
                "tipo": str,  # "liderazgo", "recursos", "proceso", "cultural"
                "descripcion": str,
                "severidad": str,
                "evidencia": str
            }
        """
        respuesta_lower = respuesta.lower()

        # Patrones de bloqueo de liderazgo
        if any(p in respuesta_lower for p in [
            "no responde", "nunca responde", "no tiene tiempo",
            "ignora", "no me hace caso", "no escucha"
        ]):
            return {
                "hay_bloqueo": True,
                "tipo": "liderazgo",
                "descripcion": "Liderazgo no accesible o no receptivo",
                "severidad": "alta",
                "evidencia": respuesta
            }

        # Patrones de bloqueo de recursos
        if any(p in respuesta_lower for p in [
            "nunca llegó", "nunca llegaron", "prometieron pero",
            "dijeron que sí pero", "no cumplieron", "sin respuesta"
        ]):
            return {
                "hay_bloqueo": True,
                "tipo": "recursos",
                "descripcion": "Recursos prometidos no entregados",
                "severidad": "media",
                "evidencia": respuesta
            }

        # Patrones de bloqueo de proceso
        if any(p in respuesta_lower for p in [
            "mucha burocracia", "proceso largo", "nadie se hace cargo",
            "me mandan de un lado a otro", "no saben quién"
        ]):
            return {
                "hay_bloqueo": True,
                "tipo": "proceso",
                "descripcion": "Procesos organizacionales ineficientes",
                "severidad": "media",
                "evidencia": respuesta
            }

        # Patrones de bloqueo cultural
        if any(p in respuesta_lower for p in [
            "así es aquí", "siempre ha sido así", "nadie hace nada",
            "todos se quejan", "es normal aquí", "todo el equipo"
        ]):
            return {
                "hay_bloqueo": True,
                "tipo": "cultural",
                "descripcion": "Problema sistémico o cultural",
                "severidad": "alta",
                "evidencia": respuesta
            }

        # Detectar persistencia sin bloqueo claro
        if any(p in respuesta_lower for p in [
            "hace meses", "hace tiempo", "sigue igual",
            "no cambia", "continúa", "todavía"
        ]):
            return {
                "hay_bloqueo": True,
                "tipo": "persistencia",
                "descripcion": "Problema persistente sin resolución",
                "severidad": "media",
                "evidencia": respuesta
            }

        return {
            "hay_bloqueo": False,
            "tipo": None,
            "descripcion": None,
            "severidad": "baja",
            "evidencia": None
        }


# ============================================================
# 🔵 GENERADOR DE INSIGHTS
# ============================================================

class GeneradorInsights:
    """Genera insights accionables para RRHH basados en conversaciones"""

    @staticmethod
    def generar(
        conversacion_completa: dict,
        analisis_inicial: dict,
        mensajes: List[dict],
        bloqueos_detectados: List[dict]
    ) -> Optional[dict]:
        """
        Genera insight si la conversación reveló información valiosa

        Returns:
            {
                "tipo": str,  # "problema_persistente", "accion_fallida", "bloqueo_organizacional"
                "categoria": str,
                "titulo": str,
                "descripcion": str,
                "contexto_completo": str,
                "recomendacion_rrhh": str,
                "severidad": str,
                "evidencias": List[str]
            }
        """
        print(f"🔍 GeneradorInsights.generar() - Mensajes: {len(mensajes)}, Bloqueos: {len(bloqueos_detectados)}")

        if len(mensajes) < AgenteConfig.MIN_MENSAJES_PARA_INSIGHT:
            print(f"⚠️  No se genera insight: Solo {len(mensajes)} mensajes (mínimo: {AgenteConfig.MIN_MENSAJES_PARA_INSIGHT})")
            return None

        # Extraer categoría principal
        categorias = analisis_inicial.get("categories", [])
        categoria_principal = categorias[0]["label"] if categorias else "sin categoría"

        # Si hay bloqueos detectados -> Insight de bloqueo organizacional
        if bloqueos_detectados:
            print(f"✅ Generando insight de bloqueo organizacional")
            bloqueo_principal = bloqueos_detectados[0]

            return {
                "tipo": "bloqueo_organizacional",
                "categoria": categoria_principal,
                "titulo": GeneradorInsights._generar_titulo_bloqueo(bloqueo_principal),
                "descripcion": GeneradorInsights._generar_descripcion_bloqueo(
                    bloqueo_principal,
                    conversacion_completa
                ),
                "contexto_completo": GeneradorInsights._resumir_conversacion(mensajes),
                "recomendacion_rrhh": GeneradorInsights._generar_recomendacion_bloqueo(
                    bloqueo_principal,
                    categoria_principal
                ),
                "severidad": bloqueo_principal["severidad"],
                "evidencias": [b["evidencia"] for b in bloqueos_detectados if b.get("evidencia")]
            }

        # Si detecta problema persistente
        if GeneradorInsights._es_problema_persistente(mensajes):
            print(f"✅ Generando insight de problema persistente")
            return {
                "tipo": "problema_persistente",
                "categoria": categoria_principal,
                "titulo": f"Problema persistente en {categoria_principal}",
                "descripcion": GeneradorInsights._generar_descripcion_persistente(
                    mensajes,
                    conversacion_completa
                ),
                "contexto_completo": GeneradorInsights._resumir_conversacion(mensajes),
                "recomendacion_rrhh": GeneradorInsights._generar_recomendacion_persistente(
                    categoria_principal
                ),
                "severidad": "media",
                "evidencias": [m["contenido"] for m in mensajes if m["rol"] == "empleado"]
            }

        # Si detecta acción fallida (RRHH prometió algo que no ocurrió)
        if GeneradorInsights._es_accion_fallida(mensajes):
            print(f"✅ Generando insight de acción fallida")
            return {
                "tipo": "accion_fallida",
                "categoria": categoria_principal,
                "titulo": "Seguimiento de RRHH sin concretar",
                "descripcion": GeneradorInsights._generar_descripcion_accion_fallida(mensajes),
                "contexto_completo": GeneradorInsights._resumir_conversacion(mensajes),
                "recomendacion_rrhh": "Revisar proceso de seguimiento y asegurar cumplimiento de compromisos",
                "severidad": "media",
                "evidencias": [m["contenido"] for m in mensajes if m["rol"] == "empleado"]
            }

        print(f"⚠️  No se generó insight: No se detectaron patrones de bloqueo, persistencia o acción fallida")
        return None

    @staticmethod
    def _generar_titulo_bloqueo(bloqueo: dict) -> str:
        tipo = bloqueo["tipo"]
        if tipo == "liderazgo":
            return "Bloqueo de liderazgo - Supervisor no accesible"
        elif tipo == "recursos":
            return "Recursos prometidos no entregados"
        elif tipo == "proceso":
            return "Procesos organizacionales ineficientes"
        elif tipo == "cultural":
            return "Problema sistémico o cultural identificado"
        else:
            return "Problema persistente sin resolución"

    @staticmethod
    def _generar_descripcion_bloqueo(bloqueo: dict, conversacion: dict) -> str:
        tipo = bloqueo["tipo"]
        dept = conversacion.get("departamento", "departamento no especificado")
        equipo = conversacion.get("equipo", "equipo no especificado")

        if tipo == "liderazgo":
            return (f"Empleado de {dept} ({equipo}) reporta que su supervisor no está disponible "
                   f"o no responde a solicitudes de reunión. {bloqueo['descripcion']}")
        elif tipo == "recursos":
            return (f"Empleado de {dept} solicitó recursos/herramientas que fueron prometidos "
                   f"pero nunca entregados. {bloqueo['descripcion']}")
        elif tipo == "proceso":
            return (f"Empleado de {dept} enfrenta procesos burocráticos o ineficientes que "
                   f"impiden resolver su problema. {bloqueo['descripcion']}")
        elif tipo == "cultural":
            return (f"Problema sistémico detectado en {dept}. El empleado indica que "
                   f"esto es generalizado en el equipo. {bloqueo['descripcion']}")
        else:
            return f"Problema persistente en {dept} sin resolución aparente."

    @staticmethod
    def _generar_recomendacion_bloqueo(bloqueo: dict, categoria: str) -> str:
        tipo = bloqueo["tipo"]

        if tipo == "liderazgo":
            return ("Intervención inmediata: (1) Reunión con el supervisor del área para "
                   "revisar accesibilidad y carga de trabajo, (2) Verificar si hay otros "
                   "empleados con el mismo problema, (3) Establecer canales alternativos "
                   "de comunicación")
        elif tipo == "recursos":
            return ("(1) Revisar el proceso de solicitud de recursos y dar seguimiento, "
                   "(2) Verificar por qué no se cumplió el compromiso, "
                   "(3) Asignar recursos pendientes con fecha límite específica")
        elif tipo == "proceso":
            return ("(1) Mapear el proceso que genera el bloqueo, "
                   "(2) Identificar cuellos de botella, "
                   "(3) Asignar responsable único para dar seguimiento")
        elif tipo == "cultural":
            return ("(1) Investigación más amplia en el departamento, "
                   "(2) Sesión de feedback con el equipo completo, "
                   "(3) Evaluar cambios estructurales o de liderazgo")
        else:
            return f"Seguimiento inmediato del caso de {categoria}"

    @staticmethod
    def _es_problema_persistente(mensajes: List[dict]) -> bool:
        """Detecta si el empleado menciona que el problema lleva tiempo"""
        keywords = ["hace meses", "hace tiempo", "sigue", "continúa", "todavía", "otra vez"]

        for msg in mensajes:
            if msg["rol"] == "empleado":
                contenido_lower = msg["contenido"].lower()
                if any(kw in contenido_lower for kw in keywords):
                    return True
        return False

    @staticmethod
    def _es_accion_fallida(mensajes: List[dict]) -> bool:
        """Detecta si RRHH prometió algo que no ocurrió"""
        keywords = ["rrhh", "recursos humanos", "dijeron que", "prometieron", "nunca llegó"]

        for msg in mensajes:
            if msg["rol"] == "empleado":
                contenido_lower = msg["contenido"].lower()
                if any(kw in contenido_lower for kw in keywords):
                    return True
        return False

    @staticmethod
    def _generar_descripcion_persistente(mensajes: List[dict], conversacion: dict) -> str:
        dept = conversacion.get("departamento", "departamento no especificado")
        return (f"Empleado de {dept} reporta problema que persiste en el tiempo. "
               f"Ha intentado resolverlo sin éxito. Requiere seguimiento e intervención.")

    @staticmethod
    def _generar_descripcion_accion_fallida(mensajes: List[dict]) -> str:
        return ("Empleado reporta que RRHH o liderazgo prometió acción de seguimiento "
               "que no se concretó. Genera frustración y desconfianza.")

    @staticmethod
    def _generar_recomendacion_persistente(categoria: str) -> str:
        return (f"(1) Seguimiento inmediato del caso de {categoria}, "
               f"(2) Verificar por qué el problema no se ha resuelto, "
               f"(3) Asignar responsable con fecha límite para dar respuesta")

    @staticmethod
    def _resumir_conversacion(mensajes: List[dict]) -> str:
        """Genera un resumen textual de la conversación"""
        resumen_lineas = []
        for i, msg in enumerate(mensajes, 1):
            rol = msg["rol"].capitalize()
            contenido = msg["contenido"][:150]  # Primeros 150 caracteres
            resumen_lineas.append(f"{i}. [{rol}] {contenido}")

        return "\n".join(resumen_lineas)


# ============================================================
# 🔵 AGENTE AUTÓNOMO PRINCIPAL
# ============================================================

class AgenteAutonomo:
    """
    Agente autónomo que decide cómo continuar conversaciones
    basándose en análisis NLP y detección de bloqueos
    """

    def __init__(self, nlp_analyzer: Optional[NLPAnalyzer] = None):
        """Inicializa con acceso al analizador NLP existente"""
        self.nlp = nlp_analyzer or NLPAnalyzer()
        self.cfg = AgenteConfig()
        self.estrategias = EstrategiasPreguntas()
        self.detector = DetectorBloqueos()
        self.generador_insights = GeneradorInsights()

    # --------------------------------------------------------
    # 🔶 INICIO DE CONVERSACIÓN
    # --------------------------------------------------------
    def iniciar_conversacion(
        self,
        mensaje_inicial: str,
        meta: Optional[dict] = None
    ) -> dict:
        """
        Analiza mensaje inicial y decide si activar conversación profunda

        Returns:
            {
                "requiere_seguimiento": bool,
                "analisis_nlp": dict,
                "pregunta_agente": str | None,
                "razon_seguimiento": str,
                "nivel_riesgo": str,
                "categoria_principal": str
            }
        """
        meta = meta or {}

        # Usar análisis NLP existente
        analisis = self.nlp.analyze_comment(mensaje_inicial, meta)

        # Extraer información clave
        stress_level = analisis["stress"]["level"]
        emotion = analisis["emotion"]["label"]
        emotion_score = analisis["emotion"]["score"]
        categorias = [cat["label"] for cat in analisis["categories"]]
        categoria_principal = categorias[0] if categorias else None
        sent_dist = analisis["stress"]["sentiment_dist"]

        # Determinar nivel de riesgo inicial
        nivel_riesgo = self._calcular_nivel_riesgo(
            stress_level,
            emotion,
            emotion_score,
            sent_dist,
            categorias
        )

        # Decidir si profundizar
        debe_profundizar, razon = self._debe_profundizar(
            stress_level,
            emotion,
            emotion_score,
            categorias,
            mensaje_inicial
        )

        if not debe_profundizar:
            return {
                "requiere_seguimiento": False,
                "analisis_nlp": analisis,
                "pregunta_agente": None,
                "razon_seguimiento": razon,
                "nivel_riesgo": nivel_riesgo,
                "categoria_principal": categoria_principal
            }

        # Generar primera pregunta según categoría
        primera_pregunta = self._generar_primera_pregunta(
            categoria_principal,
            categorias,
            mensaje_inicial
        )

        return {
            "requiere_seguimiento": True,
            "analisis_nlp": analisis,
            "pregunta_agente": primera_pregunta,
            "razon_seguimiento": razon,
            "nivel_riesgo": nivel_riesgo,
            "categoria_principal": categoria_principal
        }

    # --------------------------------------------------------
    # 🔶 PROCESAMIENTO DE RESPUESTA
    # --------------------------------------------------------
    def procesar_respuesta(
        self,
        respuesta_empleado: str,
        contexto_conversacion: dict,
        mensajes_previos: List[dict]
    ) -> dict:
        """
        Procesa respuesta del empleado y decide siguiente acción

        Args:
            respuesta_empleado: Respuesta del empleado
            contexto_conversacion: Dict con info de la conversación (nivel_riesgo, categoria, etc)
            mensajes_previos: Lista de mensajes previos [{rol, contenido}, ...]

        Returns:
            {
                "accion": str,  # "profundizar", "cerrar", "generar_insight"
                "pregunta": str | None,
                "analisis": dict,
                "bloqueo_detectado": dict | None,
                "nivel_riesgo_actualizado": str,
                "insight": dict | None
            }
        """
        # Analizar respuesta con NLP
        analisis = self.nlp.analyze_comment(respuesta_empleado)

        # Detectar bloqueos
        bloqueo = self.detector.detectar(respuesta_empleado, mensajes_previos)

        # Actualizar nivel de riesgo
        nivel_riesgo_actual = contexto_conversacion.get("nivel_riesgo", "medio")
        nivel_riesgo_nuevo = self._actualizar_nivel_riesgo(
            nivel_riesgo_actual,
            analisis,
            bloqueo
        )

        # Contar preguntas del agente
        num_preguntas = sum(1 for m in mensajes_previos if m["rol"] == "agente")

        # Recolectar todos los bloqueos (previos + actual)
        bloqueos_acumulados = contexto_conversacion.get("bloqueos_previos", [])
        if bloqueo["hay_bloqueo"]:
            bloqueos_acumulados.append(bloqueo)

        # Decidir si cerrar conversación
        if num_preguntas >= self.cfg.MAX_MENSAJES_AGENTE:
            # Llegamos al límite -> Generar insight y cerrar
            insight = self._generar_insight_final(
                contexto_conversacion,
                mensajes_previos,
                respuesta_empleado,
                analisis,
                bloqueos_acumulados
            )

            return {
                "accion": "cerrar",
                "pregunta": None,
                "analisis": analisis,
                "bloqueo_detectado": bloqueo if bloqueo["hay_bloqueo"] else None,
                "nivel_riesgo_actualizado": nivel_riesgo_nuevo,
                "insight": insight
            }

        # Verificar si el empleado quiere terminar
        if self._empleado_quiere_terminar(respuesta_empleado):
            insight = self._generar_insight_final(
                contexto_conversacion,
                mensajes_previos,
                respuesta_empleado,
                analisis,
                bloqueos_acumulados
            )

            return {
                "accion": "cerrar",
                "pregunta": None,
                "analisis": analisis,
                "bloqueo_detectado": bloqueo if bloqueo["hay_bloqueo"] else None,
                "nivel_riesgo_actualizado": nivel_riesgo_nuevo,
                "insight": insight
            }

        # Si hay bloqueo crítico -> Profundizar en el bloqueo
        if bloqueo["hay_bloqueo"] and bloqueo["severidad"] == "alta":
            pregunta = self._generar_pregunta_bloqueo(bloqueo, contexto_conversacion)

            return {
                "accion": "profundizar",
                "pregunta": pregunta,
                "analisis": analisis,
                "bloqueo_detectado": bloqueo,
                "nivel_riesgo_actualizado": nivel_riesgo_nuevo,
                "insight": None
            }

        # Continuar con pregunta según categoría
        categoria = contexto_conversacion.get("categoria_principal")
        pregunta_siguiente = self._generar_siguiente_pregunta(
            categoria,
            mensajes_previos,
            respuesta_empleado
        )

        # Si ya no hay más preguntas (retorna None), cerrar conversación
        if pregunta_siguiente is None:
            print(f"✅ Cerrando conversación: se agotaron las preguntas")
            insight = self._generar_insight_final(
                contexto_conversacion,
                mensajes_previos,
                respuesta_empleado,
                analisis,
                bloqueos_acumulados
            )

            return {
                "accion": "cerrar",
                "pregunta": None,
                "analisis": analisis,
                "bloqueo_detectado": bloqueo if bloqueo["hay_bloqueo"] else None,
                "nivel_riesgo_actualizado": nivel_riesgo_nuevo,
                "insight": insight
            }

        return {
            "accion": "profundizar",
            "pregunta": pregunta_siguiente,
            "analisis": analisis,
            "bloqueo_detectado": bloqueo if bloqueo["hay_bloqueo"] else None,
            "nivel_riesgo_actualizado": nivel_riesgo_nuevo,
            "insight": None
        }

    # --------------------------------------------------------
    # 🔶 MÉTODOS AUXILIARES
    # --------------------------------------------------------
    def _calcular_nivel_riesgo(
        self,
        stress_level: str,
        emotion: str,
        emotion_score: float,
        sent_dist: dict,
        categorias: List[str]
    ) -> str:
        """Calcula nivel de riesgo inicial"""

        # Estrés alto + emoción negativa fuerte = crítico
        if stress_level == "alto" and emotion in ["tristeza", "miedo", "enojo"] and emotion_score > 0.8:
            return self.cfg.RIESGO_CRITICO

        # Estrés alto + categoría crítica = alto
        if stress_level == "alto" and any(cat in self.cfg.CATEGORIAS_CRITICAS for cat in categorias):
            return self.cfg.RIESGO_ALTO

        # Estrés medio con emociones negativas = medio
        if stress_level == "medio" and sent_dist.get("negative", 0) > 0.5:
            return self.cfg.RIESGO_MEDIO

        # Estrés bajo = bajo
        if stress_level == "bajo":
            return self.cfg.RIESGO_BAJO

        return self.cfg.RIESGO_MEDIO

    def _debe_profundizar(
        self,
        stress_level: str,
        emotion: str,
        emotion_score: float,
        categorias: List[str],
        texto: str
    ) -> Tuple[bool, str]:
        """Decide si debe iniciar conversación profunda"""

        # Caso 1: Estrés alto
        if stress_level == "alto":
            return True, "Estrés alto detectado - requiere seguimiento"

        # Caso 2: Emoción muy negativa
        if emotion in ["tristeza", "miedo", "enojo"] and emotion_score > self.cfg.UMBRAL_EMOCION_NEGATIVA:
            return True, f"Emoción negativa intensa ({emotion}) detectada"

        # Caso 3: Categoría crítica detectada
        categorias_criticas_detectadas = [c for c in categorias if c in self.cfg.CATEGORIAS_CRITICAS]
        if categorias_criticas_detectadas:
            return True, f"Categoría crítica detectada: {categorias_criticas_detectadas[0]}"

        # Caso 4: Palabras clave de bloqueo o persistencia
        texto_lower = texto.lower()
        if any(kw in texto_lower for kw in self.cfg.KEYWORDS_BLOQUEO):
            return True, "Posible bloqueo organizacional detectado"

        if any(kw in texto_lower for kw in self.cfg.KEYWORDS_PERSISTENCIA):
            return True, "Problema persistente detectado"

        # No profundizar: comentario positivo o sin señales críticas
        return False, "Comentario no requiere seguimiento profundo"

    def _generar_primera_pregunta(
        self,
        categoria_principal: Optional[str],
        categorias: List[str],
        mensaje: str
    ) -> str:
        """Genera primera pregunta contextual"""

        if not categoria_principal:
            return self.estrategias.generica({})[0]

        # Mapear categoría a estrategia
        if categoria_principal == "sobrecarga laboral":
            return self.estrategias.sobrecarga_laboral({})[0]
        elif categoria_principal == "liderazgo":
            return self.estrategias.liderazgo({})[0]
        elif categoria_principal == "recursos insuficientes":
            return self.estrategias.recursos_insuficientes({})[0]
        elif categoria_principal == "comunicación":
            return self.estrategias.comunicacion({})[0]
        elif categoria_principal == "conflictos internos":
            return self.estrategias.conflictos_internos({})[0]
        elif categoria_principal == "equilibrio vida-trabajo":
            return self.estrategias.equilibrio_vida_trabajo({})[0]
        else:
            return self.estrategias.generica({})[0]

    def _generar_siguiente_pregunta(
        self,
        categoria: Optional[str],
        mensajes_previos: List[dict],
        ultima_respuesta: str
    ) -> Optional[str]:
        """Genera siguiente pregunta sin repetir. Retorna None si ya no hay preguntas nuevas."""

        # Obtener lista de preguntas para la categoría
        if categoria == "sobrecarga laboral":
            preguntas_disponibles = self.estrategias.sobrecarga_laboral({})
        elif categoria == "liderazgo":
            preguntas_disponibles = self.estrategias.liderazgo({})
        elif categoria == "recursos insuficientes":
            preguntas_disponibles = self.estrategias.recursos_insuficientes({})
        elif categoria == "comunicación":
            preguntas_disponibles = self.estrategias.comunicacion({})
        elif categoria == "conflictos internos":
            preguntas_disponibles = self.estrategias.conflictos_internos({})
        elif categoria == "equilibrio vida-trabajo":
            preguntas_disponibles = self.estrategias.equilibrio_vida_trabajo({})
        else:
            preguntas_disponibles = self.estrategias.generica({})

        # Filtrar preguntas ya usadas
        preguntas_usadas = [m["contenido"] for m in mensajes_previos if m["rol"] == "agente"]
        preguntas_nuevas = [p for p in preguntas_disponibles if p not in preguntas_usadas]

        if preguntas_nuevas:
            return preguntas_nuevas[0]

        # Si se agotaron las preguntas, hacer pregunta de cierre (solo una vez)
        pregunta_cierre = "¿Quieres agregar algo más sobre esto?"
        if pregunta_cierre not in preguntas_usadas:
            return pregunta_cierre

        # Si ya se hizo la pregunta de cierre, retornar None para cerrar
        return None

    def _generar_pregunta_bloqueo(self, bloqueo: dict, contexto: dict) -> str:
        """Genera pregunta específica para profundizar en bloqueo"""

        tipo = bloqueo["tipo"]

        if tipo == "liderazgo":
            return "¿Cuánto tiempo llevas intentando comunicarte sin que te hagan caso?"
        elif tipo == "recursos":
            return "¿Cuándo te prometieron eso y cuánto llevas esperando?"
        elif tipo == "proceso":
            return "¿Qué has hecho hasta ahora y en dónde se está trabando todo?"
        elif tipo == "cultural":
            return "¿Cuántas personas de tu equipo están pasando por lo mismo?"
        else:
            return "¿Qué has intentado para arreglarlo?"

    def _actualizar_nivel_riesgo(
        self,
        nivel_actual: str,
        analisis: dict,
        bloqueo: dict
    ) -> str:
        """Actualiza nivel de riesgo según nueva información"""

        # Si hay bloqueo de alta severidad -> Aumentar a alto o crítico
        if bloqueo["hay_bloqueo"] and bloqueo["severidad"] == "alta":
            if nivel_actual in ["bajo", "medio"]:
                return self.cfg.RIESGO_ALTO
            else:
                return self.cfg.RIESGO_CRITICO

        # Si el sentimiento es muy negativo -> Aumentar riesgo
        sent_dist = analisis["stress"]["sentiment_dist"]
        if sent_dist.get("negative", 0) > 0.7 and nivel_actual != self.cfg.RIESGO_CRITICO:
            if nivel_actual == self.cfg.RIESGO_BAJO:
                return self.cfg.RIESGO_MEDIO
            elif nivel_actual == self.cfg.RIESGO_MEDIO:
                return self.cfg.RIESGO_ALTO

        return nivel_actual

    def _empleado_quiere_terminar(self, respuesta: str) -> bool:
        """Detecta si empleado quiere finalizar conversación"""
        respuesta_lower = respuesta.lower().strip()

        terminos_fin = [
            "no", "nada", "nada más", "no gracias", "gracias",
            "eso es todo", "es todo", "no tengo más", "ya está"
        ]

        # Si la respuesta es muy corta y coincide con términos de fin
        if len(respuesta.split()) <= 3:
            if any(term in respuesta_lower for term in terminos_fin):
                return True

        return False

    def _generar_insight_final(
        self,
        contexto_conversacion: dict,
        mensajes_previos: List[dict],
        ultima_respuesta: str,
        ultimo_analisis: dict,
        bloqueos_detectados: List[dict]
    ) -> Optional[dict]:
        """Genera insight final basado en toda la conversación"""

        # Construir lista completa de mensajes
        mensajes_completos = mensajes_previos + [{
            "rol": "empleado",
            "contenido": ultima_respuesta
        }]

        # Obtener análisis inicial del contexto
        analisis_inicial = contexto_conversacion.get("analisis_inicial", {})

        # Generar insight
        insight = self.generador_insights.generar(
            conversacion_completa=contexto_conversacion,
            analisis_inicial=analisis_inicial,
            mensajes=mensajes_completos,
            bloqueos_detectados=bloqueos_detectados
        )

        return insight
