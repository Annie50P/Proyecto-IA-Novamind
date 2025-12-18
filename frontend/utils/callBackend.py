import requests
from typing import Optional, Dict, Any, List

BASE_URL = "http://127.0.0.1:8000"

def analizarComentarioIndividual(comentario: str, meta: Optional[Dict] = None) -> Dict[str, Any]:
    url = f"{BASE_URL}/analizar-comentario/"
    payload = {
        "comentario": comentario,
        "meta": meta or {}
    }
    response = requests.post(url, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()

def analizarLoteCSV(datos: List[Dict[str, Any]]) -> Dict[str, Any]:
    url = f"{BASE_URL}/analizar-lote/"
    payload = {"datos": datos}
    response = requests.post(url, json=payload, timeout=300)
    response.raise_for_status()
    return response.json()

def obtenerHistoricos(
    limit: int = 100,
    departamento: Optional[str] = None,
    equipo: Optional[str] = None,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
    stress_level: Optional[str] = None
) -> List[Dict[str, Any]]:
    url = f"{BASE_URL}/historicos/"
    params = {"limit": limit}
    if departamento:
        params["departamento"] = departamento
    if equipo:
        params["equipo"] = equipo
    if fecha_inicio:
        params["fecha_inicio"] = fecha_inicio
    if fecha_fin:
        params["fecha_fin"] = fecha_fin
    if stress_level:
        params["stress_level"] = stress_level

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()

def obtenerAlertas(nivel: str = "alto", limite: int = 20, departamento: Optional[str] = None) -> List[Dict[str, Any]]:
    url = f"{BASE_URL}/alertas/"
    params = {"nivel": nivel, "limite": limite}
    if departamento:
        params["departamento"] = departamento

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()

def obtenerEstadisticas(
    departamento: Optional[str] = None,
    equipo: Optional[str] = None,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None
) -> Dict[str, Any]:
    url = f"{BASE_URL}/estadisticas/"
    params = {}
    if departamento:
        params["departamento"] = departamento
    if equipo:
        params["equipo"] = equipo
    if fecha_inicio:
        params["fecha_inicio"] = fecha_inicio
    if fecha_fin:
        params["fecha_fin"] = fecha_fin

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()

def obtenerEstadisticasDepartamentos() -> Dict[str, Any]:
    url = f"{BASE_URL}/estadisticas/departamentos/"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()

def obtenerEstadisticasEquipos(departamento: Optional[str] = None) -> Dict[str, Any]:
    url = f"{BASE_URL}/estadisticas/equipos/"
    params = {}
    if departamento:
        params["departamento"] = departamento

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()

def obtenerTendencias(dias: int = 30, departamento: Optional[str] = None) -> Dict[str, Any]:
    url = f"{BASE_URL}/estadisticas/tendencias/"
    params = {"dias": dias}
    if departamento:
        params["departamento"] = departamento

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()

def obtenerPatrones() -> Dict[str, Any]:
    url = f"{BASE_URL}/alertas/patrones/"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()

def obtenerAlertasDepartamento(departamento: str) -> Dict[str, Any]:
    url = f"{BASE_URL}/alertas/departamento/{departamento}"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()

def obtenerTextoComentarios(departamento: Optional[str] = None, limit: int = 500) -> List[str]:
    url = f"{BASE_URL}/historicos/texto/"
    params = {"limit": limit}
    if departamento:
        params["departamento"] = departamento

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json().get("comentarios", [])

def obtenerDepartamentos() -> List[str]:
    url = f"{BASE_URL}/historicos/departamentos/"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json().get("departamentos", [])

def obtenerEquipos(departamento: Optional[str] = None) -> List[str]:
    url = f"{BASE_URL}/historicos/equipos/"
    params = {}
    if departamento:
        params["departamento"] = departamento

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json().get("equipos", [])

def verificarConexion() -> bool:
    try:
        url = f"{BASE_URL}/"
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except:
        return False

def login(usuario: str, password: str) -> Dict[str, Any]:
    url = f"{BASE_URL}/login/"
    payload = {"usuario": usuario, "password": password}
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()
    return response.json()


# ============================================================
# FUNCIONES DEL AGENTE AUTÓNOMO
# ============================================================

def iniciarConversacionAgente(mensaje: str, meta: Optional[Dict] = None) -> Dict[str, Any]:
    """Inicia conversación con el agente autónomo"""
    url = f"{BASE_URL}/agente/iniciar/"
    payload = {
        "mensaje": mensaje,
        "meta": meta or {}
    }
    response = requests.post(url, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()


def responderAgente(conversacion_id: int, respuesta: str) -> Dict[str, Any]:
    """Envía respuesta del empleado al agente"""
    url = f"{BASE_URL}/agente/responder/"
    payload = {
        "conversacion_id": conversacion_id,
        "respuesta": respuesta
    }
    response = requests.post(url, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()


def obtenerConversacionAgente(conversacion_id: int) -> Dict[str, Any]:
    """Obtiene historial completo de una conversación"""
    url = f"{BASE_URL}/agente/conversacion/{conversacion_id}/"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def obtenerInsights(
    limite: int = 20,
    tipo: Optional[str] = None,
    severidad: Optional[str] = None,
    estado: Optional[str] = None,
    departamento: Optional[str] = None
) -> Dict[str, Any]:
    """Obtiene insights generados por el agente"""
    url = f"{BASE_URL}/agente/insights/"
    params = {"limite": limite}
    if tipo:
        params["tipo"] = tipo
    if severidad:
        params["severidad"] = severidad
    if estado:
        params["estado"] = estado
    if departamento:
        params["departamento"] = departamento

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def obtenerEstadisticasInsights() -> Dict[str, Any]:
    """Obtiene estadísticas generales de insights"""
    url = f"{BASE_URL}/agente/stats/"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def actualizarInsight(
    insight_id: int,
    estado: Optional[str] = None,
    revisado_por: Optional[str] = None,
    notas_rrhh: Optional[str] = None
) -> Dict[str, Any]:
    """Actualiza estado y notas de un insight"""
    url = f"{BASE_URL}/agente/insights/{insight_id}/"
    payload = {}
    if estado:
        payload["estado"] = estado
    if revisado_por:
        payload["revisado_por"] = revisado_por
    if notas_rrhh is not None:
        payload["notas_rrhh"] = notas_rrhh

    response = requests.patch(url, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def listarConversacionesAgente(
    limite: int = 20,
    estado: Optional[str] = None,
    nivel_riesgo: Optional[str] = None,
    departamento: Optional[str] = None
) -> Dict[str, Any]:
    """Lista conversaciones del agente"""
    url = f"{BASE_URL}/agente/conversaciones/"
    params = {"limite": limite}
    if estado:
        params["estado"] = estado
    if nivel_riesgo:
        params["nivel_riesgo"] = nivel_riesgo
    if departamento:
        params["departamento"] = departamento

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()
