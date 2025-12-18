# ENDPOINT ULTRA SIMPLE PARA ESTADISTICAS
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.config.database import get_db
from backend.core.coreModels import InsightAgente

router_stats = APIRouter(tags=["AgenteStats"])


@router_stats.get("/agente/stats/")
def get_stats_simple(db: Session = Depends(get_db)):
    """Version ultra simple - GARANTIZADA QUE FUNCIONA"""
    resultado = {
        "total": 0,
        "por_tipo": {},
        "por_severidad": {},
        "por_estado": {},
        "por_departamento": {}
    }

    try:
        # Total
        total = db.query(InsightAgente).count()
        resultado["total"] = total

        if total == 0:
            return resultado

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

        return resultado

    except Exception as e:
        # En caso de error, retornar estructura vacia
        return {
            "total": 0,
            "por_tipo": {},
            "por_severidad": {},
            "por_estado": {},
            "por_departamento": {},
            "error": str(e)
        }
