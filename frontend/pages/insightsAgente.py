# pages/insightsAgente.py
"""
Panel de Insights del Agente Autónomo para RRHH

Este panel muestra los insights únicos generados por el agente que NO se obtienen
de comentarios estáticos: bloqueos organizacionales, acciones fallidas, problemas persistentes.
"""

import streamlit as st
import sys
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

frontend_path = Path(__file__).parent.parent
if str(frontend_path) not in sys.path:
    sys.path.insert(0, str(frontend_path))

from utils.callBackend import (
    obtenerInsights,
    obtenerEstadisticasInsights,
    actualizarInsight,
    obtenerConversacionAgente,
    listarConversacionesAgente
)


def mostrar_badge_severidad(severidad: str):
    """Muestra badge de severidad con color apropiado"""
    if severidad == "critica":
        st.markdown("🔴 **Crítica**")
    elif severidad == "alta":
        st.markdown("🟠 **Alta**")
    elif severidad == "media":
        st.markdown("🟡 **Media**")
    else:
        st.markdown("🟢 **Baja**")


def mostrar_badge_tipo(tipo: str):
    """Muestra badge de tipo de insight"""
    if tipo == "bloqueo_organizacional":
        return "🚧 Bloqueo Organizacional"
    elif tipo == "problema_persistente":
        return "🔁 Problema Persistente"
    elif tipo == "accion_fallida":
        return "❌ Acción Fallida"
    else:
        return tipo


def mostrar_badge_estado(estado: str):
    """Muestra badge de estado con color"""
    if estado == "nuevo":
        st.markdown("🆕 **Nuevo**")
    elif estado == "revisado":
        st.markdown("👀 **Revisado**")
    elif estado == "en_accion":
        st.markdown("⚙️ **En Acción**")
    elif estado == "resuelto":
        st.markdown("✅ **Resuelto**")


def mostrar_dashboard_insights():
    """Dashboard principal de insights"""

    st.title("🔍 Insights del Agente Autónomo")
    st.markdown("### Descubrimientos únicos sobre bloqueos y problemas organizacionales")

    st.info(
        "Estos insights son generados automáticamente por el agente durante conversaciones profundas. "
        "Revelan información que NO se obtiene de comentarios estáticos: por qué los problemas persisten, "
        "qué acciones no funcionaron, y dónde hay bloqueos organizacionales."
    )

    try:
        # Obtener estadísticas
        stats = obtenerEstadisticasInsights()

        # KPIs principales
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Insights", stats.get("total", 0))

        with col2:
            nuevos = stats.get("por_estado", {}).get("nuevo", 0)
            st.metric("Nuevos (sin revisar)", nuevos, delta=None)

        with col3:
            criticos = stats.get("por_severidad", {}).get("critica", 0)
            st.metric("Críticos", criticos, delta=None, delta_color="inverse")

        with col4:
            bloqueos = stats.get("por_tipo", {}).get("bloqueo_organizacional", 0)
            st.metric("Bloqueos Organizacionales", bloqueos)

        st.markdown("---")

        # Gráficos de distribución
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Distribución por Tipo")
            if stats.get("por_tipo"):
                tipos_data = stats["por_tipo"]
                tipos_labels = {
                    "bloqueo_organizacional": "Bloqueo Organizacional",
                    "problema_persistente": "Problema Persistente",
                    "accion_fallida": "Acción Fallida"
                }
                df_tipos = pd.DataFrame([
                    {"tipo": tipos_labels.get(k, k), "cantidad": v}
                    for k, v in tipos_data.items()
                ])
                fig = px.pie(df_tipos, values="cantidad", names="tipo", color_discrete_sequence=px.colors.qualitative.Set2)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No hay insights disponibles todavía")

        with col2:
            st.markdown("#### Distribución por Severidad")
            if stats.get("por_severidad"):
                sev_data = stats["por_severidad"]
                sev_order = ["baja", "media", "alta", "critica"]
                sev_colors = {"baja": "#90EE90", "media": "#FFD700", "alta": "#FF8C00", "critica": "#DC143C"}

                df_sev = pd.DataFrame([
                    {"severidad": k.capitalize(), "cantidad": v}
                    for k, v in sev_data.items()
                ])
                df_sev["orden"] = df_sev["severidad"].str.lower().map({s: i for i, s in enumerate(sev_order)})
                df_sev = df_sev.sort_values("orden")

                fig = px.bar(df_sev, x="severidad", y="cantidad", color="severidad",
                            color_discrete_map={k.capitalize(): v for k, v in sev_colors.items()})
                st.plotly_chart(fig, use_container_width=True)

        # Distribución por departamento
        if stats.get("por_departamento"):
            st.markdown("#### Insights por Departamento")
            df_dept = pd.DataFrame([
                {"departamento": k, "cantidad": v}
                for k, v in stats["por_departamento"].items()
            ]).sort_values("cantidad", ascending=False)

            fig = px.bar(df_dept, x="departamento", y="cantidad", color="cantidad",
                        color_continuous_scale="Reds")
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error al cargar estadísticas: {str(e)}")

    st.markdown("---")


def mostrar_lista_insights():
    """Muestra lista filtrable de insights"""

    st.markdown("### 📋 Lista de Insights")

    # Filtros
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        filtro_tipo = st.selectbox(
            "Tipo",
            ["Todos", "Bloqueo Organizacional", "Problema Persistente", "Acción Fallida"]
        )

    with col2:
        filtro_severidad = st.selectbox(
            "Severidad",
            ["Todas", "Crítica", "Alta", "Media", "Baja"]
        )

    with col3:
        filtro_estado = st.selectbox(
            "Estado",
            ["Todos", "Nuevo", "Revisado", "En Acción", "Resuelto"]
        )

    with col4:
        limite = st.number_input("Límite", min_value=5, max_value=100, value=20)

    # Construir parámetros de filtro
    tipo_map = {
        "Bloqueo Organizacional": "bloqueo_organizacional",
        "Problema Persistente": "problema_persistente",
        "Acción Fallida": "accion_fallida"
    }

    params = {"limite": limite}
    if filtro_tipo != "Todos":
        params["tipo"] = tipo_map[filtro_tipo]
    if filtro_severidad != "Todas":
        params["severidad"] = filtro_severidad.lower()
    if filtro_estado != "Todos":
        params["estado"] = filtro_estado.lower()

    try:
        # Obtener insights
        resultado = obtenerInsights(**params)
        insights = resultado.get("insights", [])

        if not insights:
            st.info("No se encontraron insights con los filtros seleccionados")
            return

        st.write(f"**{len(insights)} insights encontrados**")

        # Mostrar cada insight
        for insight in insights:
            with st.expander(
                f"{mostrar_badge_tipo(insight['tipo'])} - {insight['titulo']}"
            ):
                mostrar_detalle_insight(insight)

    except Exception as e:
        st.error(f"Error al cargar insights: {str(e)}")


def mostrar_detalle_insight(insight: dict):
    """Muestra detalle completo de un insight"""

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Severidad:**")
        mostrar_badge_severidad(insight["severidad"])

    with col2:
        st.markdown("**Estado:**")
        mostrar_badge_estado(insight["estado"])

    with col3:
        st.markdown("**Categoría:**")
        st.write(insight["categoria"])

    st.markdown("---")

    # Información del contexto
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**Departamento:** {insight.get('departamento') or 'No especificado'}")
    with col2:
        st.markdown(f"**Equipo:** {insight.get('equipo') or 'No especificado'}")
    with col3:
        fecha = insight.get("created_at", "")
        if fecha:
            fecha_dt = datetime.fromisoformat(fecha.replace("Z", "+00:00"))
            st.markdown(f"**Fecha:** {fecha_dt.strftime('%Y-%m-%d %H:%M')}")

    st.markdown("---")

    # Descripción
    st.markdown("**📝 Descripción:**")
    st.write(insight["descripcion"])

    # Contexto completo de la conversación
    st.markdown("**💬 Conversación completa:**")
    with st.container():
        st.text(insight["contexto_completo"])

    # Evidencias
    if insight.get("evidencias") and len(insight["evidencias"]) > 0:
        st.markdown("**📌 Evidencias:**")
        with st.container():
            for i, evidencia in enumerate(insight["evidencias"], 1):
                st.markdown(f"{i}. *\"{evidencia}\"*")

    # Recomendación para RRHH
    st.markdown("**💡 Recomendación para RRHH:**")
    st.success(insight["recomendacion_rrhh"])

    # Notas de RRHH
    if insight.get("notas_rrhh"):
        st.markdown("**📝 Notas de RRHH:**")
        st.info(insight["notas_rrhh"])

    if insight.get("revisado_por"):
        st.caption(f"Revisado por: {insight['revisado_por']} el {insight.get('fecha_revision', 'N/A')}")

    st.markdown("---")

    # Acciones
    st.markdown("**Acciones:**")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Ver conversación completa", key=f"ver_conv_{insight['id']}"):
            st.session_state.ver_conversacion_id = insight["conversacion_id"]

    with col2:
        nuevo_estado = st.selectbox(
            "Cambiar estado",
            ["nuevo", "revisado", "en_accion", "resuelto"],
            index=["nuevo", "revisado", "en_accion", "resuelto"].index(insight["estado"]),
            key=f"estado_{insight['id']}"
        )

    with col3:
        if st.button("Actualizar", key=f"actualizar_{insight['id']}"):
            try:
                usuario_rrhh = st.session_state.get("usuario", "RRHH")
                actualizarInsight(
                    insight["id"],
                    estado=nuevo_estado,
                    revisado_por=usuario_rrhh
                )
                st.success("Insight actualizado")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")

    # Agregar notas
    st.markdown("---")
    st.markdown("**➕ Notas internas:**")
    notas = st.text_area(
        "Agregar o editar notas",
        value=insight.get("notas_rrhh", ""),
        key=f"notas_{insight['id']}",
        height=100
    )
    if st.button("Guardar notas", key=f"guardar_notas_{insight['id']}"):
        try:
            actualizarInsight(insight["id"], notas_rrhh=notas)
            st.success("Notas guardadas")
            st.rerun()
        except Exception as e:
            st.error(f"Error: {str(e)}")


def mostrar_conversaciones_agente():
    """Muestra lista de conversaciones del agente"""

    st.markdown("### 💬 Conversaciones del Agente")

    # Filtros
    col1, col2, col3 = st.columns(3)

    with col1:
        filtro_estado = st.selectbox(
            "Estado conversación",
            ["Todas", "Activa", "Cerrada"],
            key="filtro_conv_estado"
        )

    with col2:
        filtro_riesgo = st.selectbox(
            "Nivel de riesgo",
            ["Todos", "Crítico", "Alto", "Medio", "Bajo"],
            key="filtro_conv_riesgo"
        )

    with col3:
        limite_conv = st.number_input("Límite", min_value=5, max_value=50, value=20, key="limite_conv")

    params = {"limite": limite_conv}
    if filtro_estado != "Todas":
        params["estado"] = filtro_estado.lower()
    if filtro_riesgo != "Todos":
        params["nivel_riesgo"] = filtro_riesgo.lower()

    try:
        resultado = listarConversacionesAgente(**params)
        conversaciones = resultado.get("conversaciones", [])

        if not conversaciones:
            st.info("No se encontraron conversaciones")
            return

        st.write(f"**{len(conversaciones)} conversaciones encontradas**")

        # Mostrar conversaciones
        for conv in conversaciones:
            nivel_riesgo_emoji = {
                "critico": "🔴",
                "alto": "🟠",
                "medio": "🟡",
                "bajo": "🟢"
            }

            with st.expander(
                f"{nivel_riesgo_emoji.get(conv['nivel_riesgo_actual'], '⚪')} "
                f"{conv['categoria_principal'] or 'Sin categoría'} - "
                f"{conv['departamento'] or 'Depto N/A'}"
            ):
                st.markdown(f"**Mensaje inicial:** {conv['mensaje_inicial']}")
                st.markdown(f"**Estado:** {conv['estado']}")
                st.markdown(f"**Nivel de riesgo:** {conv['nivel_riesgo_actual']}")
                st.markdown(f"**Fecha:** {conv['created_at']}")

                if st.button("Ver detalles completos", key=f"detalle_conv_{conv['id']}"):
                    with st.spinner("Cargando conversación..."):
                        try:
                            detalle = obtenerConversacionAgente(conv['id'])
                            st.json(detalle)
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

    except Exception as e:
        st.error(f"Error al cargar conversaciones: {str(e)}")


# Función principal para integrar en app_rrhh
def mostrar_pagina_insights():
    """Página principal de insights para RRHH"""

    # Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📋 Insights", "💬 Conversaciones"])

    with tab1:
        mostrar_dashboard_insights()

    with tab2:
        mostrar_lista_insights()

    with tab3:
        mostrar_conversaciones_agente()


# Para testing standalone
if __name__ == "__main__":
    st.set_page_config(
        page_title="Insights del Agente",
        page_icon="🔍",
        layout="wide"
    )
    mostrar_pagina_insights()
