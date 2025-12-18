# api/agente.py
"""
Endpoints API para el Agente Autónomo de Bienestar Laboral

Este módulo NO modifica los endpoints existentes.
Agrega nuevos endpoints específicos para la conversación con el agente.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from datetime import datetime

from backend.config.database import get_db
from backend.ia.iaCore import NLPAnalyzer
from backend.ia.iaAgent import AgenteAutonomo
from backend.core.coreModels import ConversacionAgente, MensajeAgente, InsightAgente

router = APIRouter(tags=["Agente"])

# Instancias globales
try:
    nlp_analyzer = NLPAnalyzer()
    agente = AgenteAutonomo(nlp_analyzer)
    print("[OK] Agente autonomo inicializado correctamente")
except Exception as e:
    print(f"[ERROR] Al inicializar agente: {str(e)}")
    import traceback
    print(traceback.format_exc())
    nlp_analyzer = None
    agente = None


# ============================================================
# MODELOS PYDANTIC PARA REQUESTS/RESPONSES
# ============================================================

class IniciarConversacionPayload(BaseModel):
    """Payload para iniciar conversación con el agente"""
    mensaje: str
    meta: Optional[dict] = None


class ResponderPayload(BaseModel):
    """Payload para responder en una conversación existente"""
    conversacion_id: int
    respuesta: str


class ActualizarInsightPayload(BaseModel):
    """Payload para actualizar estado de un insight"""
    estado: Optional[str] = None
    revisado_por: Optional[str] = None
    notas_rrhh: Optional[str] = None


# ============================================================
# ENDPOINTS
# ============================================================

@router.get("/agente/health/")
def health_check():
    """Health check del agente"""
    return {
        "status": "ok",
        "agente_loaded": agente is not None,
        "nlp_analyzer_loaded": nlp_analyzer is not None
    }


@router.get("/agente/insights/estadisticas/simple/")
def estadisticas_insights_simple(db: Session = Depends(get_db)):
    """Endpoint de prueba ultra simple para diagnosticar"""
    try:
        print("[DEBUG] Endpoint simple llamado")
        count = db.query(InsightAgente).count()
        print(f"[DEBUG] Count exitoso: {count}")
        return {"total": count, "status": "ok"}
    except Exception as e:
        print(f"[DEBUG ERROR] {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"total": 0, "status": "error", "message": str(e)}


@router.post("/agente/iniciar/")
def iniciar_conversacion(payload: IniciarConversacionPayload, db: Session = Depends(get_db)):
    """
    Inicia una conversación con el agente autónomo

    El agente analiza el mensaje inicial y decide si profundizar con preguntas guiadas.

    Returns:
        {
            "conversacion_id": int,
            "requiere_seguimiento": bool,
            "pregunta": str | None,
            "analisis_inicial": dict,
            "nivel_riesgo": str,
            "razon_seguimiento": str
        }
    """
    try:
        meta = payload.meta or {}
        mensaje = payload.mensaje

        # El agente decide si profundizar
        decision = agente.iniciar_conversacion(mensaje, meta)

        # Crear registro de conversación en BD
        conversacion = ConversacionAgente(
            mensaje_inicial=mensaje,
            analisis_inicial=decision["analisis_nlp"],
            departamento=meta.get("departamento"),
            equipo=meta.get("equipo"),
            categoria_principal=decision["categoria_principal"],
            nivel_riesgo_inicial=decision["nivel_riesgo"],
            nivel_riesgo_actual=decision["nivel_riesgo"],
            estado="activa" if decision["requiere_seguimiento"] else "cerrada",
            razon_seguimiento=decision["razon_seguimiento"]
        )
        db.add(conversacion)
        db.commit()
        db.refresh(conversacion)

        # Si hay pregunta del agente, guardar primer mensaje del agente
        if decision["requiere_seguimiento"] and decision["pregunta_agente"]:
            mensaje_agente = MensajeAgente(
                conversacion_id=conversacion.id,
                rol="agente",
                contenido=decision["pregunta_agente"],
                meta_info={"tipo": "primera_pregunta"}
            )
            db.add(mensaje_agente)
            db.commit()

        return {
            "conversacion_id": conversacion.id,
            "requiere_seguimiento": decision["requiere_seguimiento"],
            "pregunta": decision["pregunta_agente"],
            "analisis_inicial": decision["analisis_nlp"],
            "nivel_riesgo": decision["nivel_riesgo"],
            "razon_seguimiento": decision["razon_seguimiento"]
        }

    except Exception as e:
        print(f"[ERROR] EN /agente/iniciar/: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agente/responder/")
def responder_conversacion(payload: ResponderPayload, db: Session = Depends(get_db)):
    """
    Procesa la respuesta del empleado y decide siguiente acción

    Returns:
        {
            "accion": str,  # "profundizar", "cerrar"
            "pregunta": str | None,
            "nivel_riesgo": str,
            "insight_generado": dict | None
        }
    """
    try:
        conversacion_id = payload.conversacion_id
        respuesta_empleado = payload.respuesta

        # Obtener conversación
        conversacion = db.query(ConversacionAgente).filter(
            ConversacionAgente.id == conversacion_id
        ).first()

        if not conversacion:
            raise HTTPException(status_code=404, detail="Conversación no encontrada")

        if conversacion.estado != "activa":
            raise HTTPException(status_code=400, detail="Conversación ya cerrada")

        # Guardar respuesta del empleado
        mensaje_empleado = MensajeAgente(
            conversacion_id=conversacion_id,
            rol="empleado",
            contenido=respuesta_empleado
        )
        db.add(mensaje_empleado)
        db.commit()

        # Obtener mensajes previos
        mensajes_previos = db.query(MensajeAgente).filter(
            MensajeAgente.conversacion_id == conversacion_id
        ).order_by(MensajeAgente.created_at).all()

        mensajes_dict = [
            {"rol": m.rol, "contenido": m.contenido}
            for m in mensajes_previos
        ]

        # Recolectar todos los bloqueos detectados previamente
        bloqueos_acumulados = []
        for m in mensajes_previos:
            if m.rol == "agente" and m.meta_info and m.meta_info.get("bloqueo_detectado"):
                bloqueo = m.meta_info["bloqueo_detectado"]
                if bloqueo and bloqueo.get("hay_bloqueo"):
                    bloqueos_acumulados.append(bloqueo)

        # Contexto de conversación
        contexto = {
            "conversacion_id": conversacion.id,
            "nivel_riesgo": conversacion.nivel_riesgo_actual,
            "categoria_principal": conversacion.categoria_principal,
            "departamento": conversacion.departamento,
            "equipo": conversacion.equipo,
            "analisis_inicial": conversacion.analisis_inicial,
            "bloqueos_previos": bloqueos_acumulados
        }

        # El agente procesa la respuesta
        decision = agente.procesar_respuesta(
            respuesta_empleado,
            contexto,
            mensajes_dict
        )

        # Actualizar el mensaje del empleado con el análisis NLP
        mensaje_empleado.analisis = decision.get("analisis")

        # Actualizar nivel de riesgo
        conversacion.nivel_riesgo_actual = decision["nivel_riesgo_actualizado"]

        # Si hay pregunta del agente, guardarla
        if decision["accion"] == "profundizar" and decision["pregunta"]:
            mensaje_agente = MensajeAgente(
                conversacion_id=conversacion_id,
                rol="agente",
                contenido=decision["pregunta"],
                meta_info={
                    "bloqueo_detectado": decision.get("bloqueo_detectado")
                }
            )
            db.add(mensaje_agente)

        # Si se cierra la conversación
        if decision["accion"] == "cerrar":
            conversacion.estado = "cerrada"

            # Si se generó un insight, guardarlo
            if decision.get("insight"):
                print(f"[INSIGHT] Guardando insight generado: {decision['insight']['tipo']}")
                insight_data = decision["insight"]
                insight = InsightAgente(
                    conversacion_id=conversacion_id,
                    tipo=insight_data["tipo"],
                    categoria=insight_data["categoria"],
                    titulo=insight_data["titulo"],
                    descripcion=insight_data["descripcion"],
                    contexto_completo=insight_data["contexto_completo"],
                    recomendacion_rrhh=insight_data["recomendacion_rrhh"],
                    evidencias=insight_data.get("evidencias", []),
                    severidad=insight_data["severidad"],
                    departamento=conversacion.departamento,
                    equipo=conversacion.equipo,
                    estado="nuevo"
                )
                db.add(insight)
            else:
                print(f"[WARN]  No se generó insight para esta conversación")

        db.commit()

        return {
            "accion": decision["accion"],
            "pregunta": decision.get("pregunta"),
            "nivel_riesgo": decision["nivel_riesgo_actualizado"],
            "insight_generado": decision.get("insight"),
            "bloqueo_detectado": decision.get("bloqueo_detectado")
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] ERROR EN /agente/responder/: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agente/conversacion/{conversacion_id}/")
def obtener_conversacion(conversacion_id: int, db: Session = Depends(get_db)):
    """
    Obtiene el historial completo de una conversación

    Returns:
        {
            "conversacion": {...},
            "mensajes": [{...}],
            "insights": [{...}]
        }
    """
    try:
        conversacion = db.query(ConversacionAgente).filter(
            ConversacionAgente.id == conversacion_id
        ).first()

        if not conversacion:
            raise HTTPException(status_code=404, detail="Conversación no encontrada")

        mensajes = db.query(MensajeAgente).filter(
            MensajeAgente.conversacion_id == conversacion_id
        ).order_by(MensajeAgente.created_at).all()

        insights = db.query(InsightAgente).filter(
            InsightAgente.conversacion_id == conversacion_id
        ).all()

        return {
            "conversacion": {
                "id": conversacion.id,
                "mensaje_inicial": conversacion.mensaje_inicial,
                "analisis_inicial": conversacion.analisis_inicial,
                "departamento": conversacion.departamento,
                "equipo": conversacion.equipo,
                "categoria_principal": conversacion.categoria_principal,
                "nivel_riesgo_inicial": conversacion.nivel_riesgo_inicial,
                "nivel_riesgo_actual": conversacion.nivel_riesgo_actual,
                "estado": conversacion.estado,
                "razon_seguimiento": conversacion.razon_seguimiento,
                "created_at": str(conversacion.created_at),
                "updated_at": str(conversacion.updated_at)
            },
            "mensajes": [
                {
                    "id": m.id,
                    "rol": m.rol,
                    "contenido": m.contenido,
                    "analisis": m.analisis,
                    "meta_info": m.meta_info,
                    "created_at": str(m.created_at)
                }
                for m in mensajes
            ],
            "insights": [
                {
                    "id": i.id,
                    "tipo": i.tipo,
                    "titulo": i.titulo,
                    "descripcion": i.descripcion,
                    "severidad": i.severidad,
                    "estado": i.estado
                }
                for i in insights
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] ERROR EN /agente/conversacion/: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agente/insights/")
def obtener_insights(
    limite: int = 20,
    tipo: Optional[str] = None,
    severidad: Optional[str] = None,
    estado: Optional[str] = None,
    departamento: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Obtiene insights generados por el agente con filtros opcionales

    Query parameters:
        - limite: Número de resultados (default: 20)
        - tipo: Filtrar por tipo de insight
        - severidad: Filtrar por severidad
        - estado: Filtrar por estado (nuevo, revisado, etc)
        - departamento: Filtrar por departamento
    """
    try:
        query = db.query(InsightAgente)

        if tipo:
            query = query.filter(InsightAgente.tipo == tipo)
        if severidad:
            query = query.filter(InsightAgente.severidad == severidad)
        if estado:
            query = query.filter(InsightAgente.estado == estado)
        if departamento:
            query = query.filter(InsightAgente.departamento == departamento)

        insights = query.order_by(
            InsightAgente.created_at.desc()
        ).limit(limite).all()

        return {
            "insights": [
                {
                    "id": i.id,
                    "conversacion_id": i.conversacion_id,
                    "tipo": i.tipo,
                    "categoria": i.categoria,
                    "titulo": i.titulo,
                    "descripcion": i.descripcion,
                    "contexto_completo": i.contexto_completo,
                    "recomendacion_rrhh": i.recomendacion_rrhh,
                    "evidencias": i.evidencias,
                    "severidad": i.severidad,
                    "departamento": i.departamento,
                    "equipo": i.equipo,
                    "estado": i.estado,
                    "revisado_por": i.revisado_por,
                    "fecha_revision": str(i.fecha_revision) if i.fecha_revision else None,
                    "notas_rrhh": i.notas_rrhh,
                    "created_at": str(i.created_at),
                    "updated_at": str(i.updated_at)
                }
                for i in insights
            ],
            "total": len(insights)
        }

    except Exception as e:
        print(f"[ERROR] ERROR EN /agente/insights/: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agente/insights/estadisticas/")
def estadisticas_insights(db: Session = Depends(get_db)):
    """Obtiene estadísticas generales de insights"""
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    logger.info("=" * 60)
    logger.info("[STATS] ENDPOINT LLAMADO")
    logger.info("=" * 60)

    resultado_default = {
        "total": 0,
        "por_tipo": {},
        "por_severidad": {},
        "por_estado": {},
        "por_departamento": {}
    }

    try:
        # Contar total
        total = db.query(InsightAgente).count()
        logger.info(f"Total insights: {total}")

        if total == 0:
            logger.info("No hay insights, retornando vacio")
            return resultado_default

        resultado = {
            "total": total,
            "por_tipo": {},
            "por_severidad": {},
            "por_estado": {},
            "por_departamento": {}
        }

        # Por tipo
        tipos = db.query(InsightAgente.tipo, func.count(InsightAgente.id)).group_by(InsightAgente.tipo).all()
        for tipo, count in tipos:
            if tipo:
                resultado["por_tipo"][tipo] = count

        # Por severidad
        severidades = db.query(InsightAgente.severidad, func.count(InsightAgente.id)).group_by(InsightAgente.severidad).all()
        for sev, count in severidades:
            if sev:
                resultado["por_severidad"][sev] = count

        # Por estado
        estados = db.query(InsightAgente.estado, func.count(InsightAgente.id)).group_by(InsightAgente.estado).all()
        for est, count in estados:
            if est:
                resultado["por_estado"][est] = count

        # Por departamento
        departamentos = db.query(InsightAgente.departamento, func.count(InsightAgente.id)).filter(
            InsightAgente.departamento.isnot(None)
        ).group_by(InsightAgente.departamento).all()
        for dept, count in departamentos:
            if dept:
                resultado["por_departamento"][dept] = count

        logger.info(f"Resultado: {resultado}")
        return resultado

    except Exception as e:
        logger.error(f"ERROR: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return resultado_default


@router.patch("/agente/insights/{insight_id}/")
def actualizar_insight(
    insight_id: int,
    payload: ActualizarInsightPayload,
    db: Session = Depends(get_db)
):
    """
    Actualiza el estado y notas de un insight

    RRHH puede marcar insights como revisados, agregar notas, cambiar estado
    """
    try:
        insight = db.query(InsightAgente).filter(
            InsightAgente.id == insight_id
        ).first()

        if not insight:
            raise HTTPException(status_code=404, detail="Insight no encontrado")

        if payload.estado:
            insight.estado = payload.estado

        if payload.revisado_por:
            insight.revisado_por = payload.revisado_por
            if insight.estado == "nuevo":
                insight.estado = "revisado"
            if not insight.fecha_revision:
                insight.fecha_revision = datetime.now()

        if payload.notas_rrhh is not None:
            insight.notas_rrhh = payload.notas_rrhh

        db.commit()
        db.refresh(insight)

        return {
            "success": True,
            "insight": {
                "id": insight.id,
                "estado": insight.estado,
                "revisado_por": insight.revisado_por,
                "fecha_revision": str(insight.fecha_revision) if insight.fecha_revision else None,
                "notas_rrhh": insight.notas_rrhh
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] ERROR EN /agente/insights/{insight_id}/: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agente/conversaciones/")
def listar_conversaciones(
    limite: int = 20,
    estado: Optional[str] = None,
    nivel_riesgo: Optional[str] = None,
    departamento: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Lista conversaciones con filtros opcionales
    """
    try:
        query = db.query(ConversacionAgente)

        if estado:
            query = query.filter(ConversacionAgente.estado == estado)
        if nivel_riesgo:
            query = query.filter(ConversacionAgente.nivel_riesgo_actual == nivel_riesgo)
        if departamento:
            query = query.filter(ConversacionAgente.departamento == departamento)

        conversaciones = query.order_by(
            ConversacionAgente.created_at.desc()
        ).limit(limite).all()

        return {
            "conversaciones": [
                {
                    "id": c.id,
                    "mensaje_inicial": c.mensaje_inicial[:150] + "..." if len(c.mensaje_inicial) > 150 else c.mensaje_inicial,
                    "categoria_principal": c.categoria_principal,
                    "nivel_riesgo_actual": c.nivel_riesgo_actual,
                    "estado": c.estado,
                    "departamento": c.departamento,
                    "equipo": c.equipo,
                    "created_at": str(c.created_at),
                    "updated_at": str(c.updated_at)
                }
                for c in conversaciones
            ],
            "total": len(conversaciones)
        }

    except Exception as e:
        print(f"[ERROR] ERROR EN /agente/conversaciones/: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
