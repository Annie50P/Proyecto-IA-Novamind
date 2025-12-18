# pages/insightsAgente.py
"""
Panel de Insights del Agente Autonomo para RRHH
"""

import streamlit as st
import sys
from pathlib import Path
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


def mostrar_dashboard_insights():
    """Dashboard principal de insights - VERSION SIMPLE QUE FUNCIONA"""

    st.title("Insights del Agente Autonomo")
    st.markdown("### Descubrimientos sobre bloqueos y problemas organizacionales")

    try:
        # Obtener estadisticas
        stats = obtenerEstadisticasInsights()

        # KPIs principales
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Insights", stats.get("total", 0))

        with col2:
            nuevos = stats.get("por_estado", {}).get("nuevo", 0)
            st.metric("Nuevos", nuevos)

        with col3:
            criticos = stats.get("por_severidad", {}).get("critica", 0)
            st.metric("Criticos", criticos)

        with col4:
            bloqueos = stats.get("por_tipo", {}).get("bloqueo_organizacional", 0)
            st.metric("Bloqueos", bloqueos)

        # Mostrar datos en tablas simples
        if stats.get("total", 0) > 0:
            st.markdown("---")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Por Tipo:**")
                if stats.get("por_tipo"):
                    for tipo, count in stats["por_tipo"].items():
                        st.write(f"- {tipo}: {count}")

                st.markdown("**Por Severidad:**")
                if stats.get("por_severidad"):
                    for sev, count in stats["por_severidad"].items():
                        st.write(f"- {sev}: {count}")

            with col2:
                st.markdown("**Por Estado:**")
                if stats.get("por_estado"):
                    for estado, count in stats["por_estado"].items():
                        st.write(f"- {estado}: {count}")

                st.markdown("**Por Departamento:**")
                if stats.get("por_departamento"):
                    for dept, count in stats["por_departamento"].items():
                        st.write(f"- {dept}: {count}")
        else:
            st.info("No hay insights disponibles todavia")

    except Exception as e:
        st.error(f"Error al cargar estadisticas: {str(e)}")
        st.write("Detalles del error para debugging:")
        st.code(str(e))


def mostrar_lista_insights():
    """Muestra lista de insights - VERSION SIMPLE"""

    st.markdown("### Lista de Insights")

    # Filtros basicos
    col1, col2 = st.columns(2)

    with col1:
        filtro_estado = st.selectbox(
            "Estado",
            ["Todos", "Nuevo", "Revisado", "En Accion", "Resuelto"]
        )

    with col2:
        limite = st.number_input("Limite", min_value=5, max_value=50, value=10)

    params = {"limite": limite}
    if filtro_estado != "Todos":
        params["estado"] = filtro_estado.lower().replace(" ", "_")

    try:
        resultado = obtenerInsights(**params)
        insights = resultado.get("insights", [])

        if not insights:
            st.info("No se encontraron insights")
            return

        st.write(f"**{len(insights)} insights encontrados**")

        # Mostrar insights en formato simple
        for insight in insights:
            with st.expander(f"{insight['tipo']} - {insight['titulo']}"):

                # Info basica
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Severidad:** {insight['severidad']}")
                with col2:
                    st.write(f"**Estado:** {insight['estado']}")
                with col3:
                    st.write(f"**Categoria:** {insight['categoria']}")

                st.markdown("---")

                # Contexto
                if insight.get('departamento'):
                    st.write(f"**Departamento:** {insight['departamento']}")
                if insight.get('equipo'):
                    st.write(f"**Equipo:** {insight['equipo']}")

                st.markdown("---")

                # Descripcion
                st.markdown("**Descripcion:**")
                st.write(insight['descripcion'])

                # Conversacion
                st.markdown("**Conversacion:**")
                st.text_area("", value=insight['contexto_completo'], height=150, disabled=True, key=f"conv_{insight['id']}")

                # Recomendacion
                st.markdown("**Recomendacion para RRHH:**")
                st.write(insight['recomendacion_rrhh'])

                # Notas
                if insight.get('notas_rrhh'):
                    st.markdown("**Notas:**")
                    st.write(insight['notas_rrhh'])

                st.markdown("---")

                # Acciones
                col1, col2 = st.columns(2)

                with col1:
                    nuevo_estado = st.selectbox(
                        "Cambiar estado",
                        ["nuevo", "revisado", "en_accion", "resuelto"],
                        index=["nuevo", "revisado", "en_accion", "resuelto"].index(insight["estado"]),
                        key=f"estado_{insight['id']}"
                    )

                with col2:
                    if st.button("Actualizar", key=f"btn_{insight['id']}"):
                        try:
                            actualizarInsight(insight["id"], estado=nuevo_estado, revisado_por="RRHH")
                            st.success("Actualizado")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

    except Exception as e:
        st.error(f"Error al cargar insights: {str(e)}")


def mostrar_conversaciones_agente():
    """Muestra lista de conversaciones - VERSION SIMPLE"""

    st.markdown("### Conversaciones del Agente")

    limite = st.number_input("Limite", min_value=5, max_value=50, value=10, key="limite_conv")

    try:
        resultado = listarConversacionesAgente(limite=limite)
        conversaciones = resultado.get("conversaciones", [])

        if not conversaciones:
            st.info("No se encontraron conversaciones")
            return

        st.write(f"**{len(conversaciones)} conversaciones encontradas**")

        for conv in conversaciones:
            with st.expander(f"{conv['categoria_principal'] or 'Sin categoria'} - {conv['departamento'] or 'Sin dept'}"):
                st.write(f"**Mensaje inicial:** {conv['mensaje_inicial']}")
                st.write(f"**Estado:** {conv['estado']}")
                st.write(f"**Nivel de riesgo:** {conv['nivel_riesgo_actual']}")
                st.write(f"**Fecha:** {conv['created_at']}")

    except Exception as e:
        st.error(f"Error al cargar conversaciones: {str(e)}")


def mostrar_pagina_insights():
    """Pagina principal de insights para RRHH"""

    tab1, tab2, tab3 = st.tabs(["Dashboard", "Insights", "Conversaciones"])

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
        page_icon="📊",
        layout="wide"
    )
    mostrar_pagina_insights()
