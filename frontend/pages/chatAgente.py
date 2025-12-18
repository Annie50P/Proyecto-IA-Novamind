# pages/chatAgente.py
"""
Interfaz de chat pública para el Agente Autónomo de Bienestar Laboral

Esta página NO reemplaza el formulario de comentarios existente.
Es una opción adicional que permite conversaciones guiadas con el agente.
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import date

frontend_path = Path(__file__).parent.parent
if str(frontend_path) not in sys.path:
    sys.path.insert(0, str(frontend_path))

from utils.callBackend import iniciarConversacionAgente, responderAgente, verificarConexion


def mostrar_mensaje(rol: str, contenido: str, nivel_riesgo: str = None):
    """Muestra un mensaje en el chat con formato apropiado"""

    if rol == "empleado":
        with st.chat_message("user"):
            st.write(contenido)

    elif rol == "agente":
        with st.chat_message("assistant"):
            st.write(contenido)

            # Mostrar indicador de nivel de riesgo si está disponible
            if nivel_riesgo:
                if nivel_riesgo == "critico":
                    st.caption("🔴 Nivel de riesgo: Crítico")
                elif nivel_riesgo == "alto":
                    st.caption("🟠 Nivel de riesgo: Alto")
                elif nivel_riesgo == "medio":
                    st.caption("🟡 Nivel de riesgo: Medio")
                else:
                    st.caption("🟢 Nivel de riesgo: Bajo")


def mostrar_chat_agente():
    """Interfaz principal del chat con el agente"""

    st.title(" Agente de Bienestar Laboral")
    st.markdown("### Conversación confidencial y anónima")

    st.info(
        "Este agente te ayudará a explorar tu situación de manera más profunda "
        "para entender mejor cómo ayudarte. La conversación es completamente "
        "confidencial y anónima."
    )

    # Verificar conexión
    if not verificarConexion():
        st.error("El sistema no está disponible en este momento. Por favor, intenta más tarde.")
        return

    # Inicializar session state
    if "conversacion_activa" not in st.session_state:
        st.session_state.conversacion_activa = False
    if "conversacion_id" not in st.session_state:
        st.session_state.conversacion_id = None
    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []
    if "nivel_riesgo" not in st.session_state:
        st.session_state.nivel_riesgo = None
    if "conversacion_cerrada" not in st.session_state:
        st.session_state.conversacion_cerrada = False

    # Si no hay conversación activa, mostrar formulario inicial
    if not st.session_state.conversacion_activa:
        st.markdown("---")
        st.markdown("### Cuéntanos qué te preocupa")

        with st.form("form_mensaje_inicial"):
            mensaje_inicial = st.text_area(
                "Tu mensaje",
                height=150,
                placeholder="Ej: Me siento muy estresado con la carga de trabajo...",
                max_chars=2000,
                help="Comparte tu situación de forma libre"
            )

            st.markdown("**Contexto opcional (ayuda a generar mejores recomendaciones):**")
            col1, col2 = st.columns(2)

            with col1:
                departamento = st.selectbox(
                    "Departamento",
                    ["", "Operaciones", "Ventas", "IT", "RRHH", "Finanzas", "Marketing", "Otro"]
                )

            with col2:
                equipo = st.text_input(
                    "Equipo",
                    placeholder="Ej: Turno A, Equipo Norte, etc."
                )

            submitted = st.form_submit_button("Iniciar conversación", type="primary", use_container_width=True)

        if submitted:
            if not mensaje_inicial.strip():
                st.error("Por favor escribe un mensaje antes de enviar")
                return

            with st.spinner("Analizando tu mensaje..."):
                try:
                    meta = {
                        "departamento": departamento if departamento else "No especificado",
                        "equipo": equipo if equipo else "",
                        "fecha": str(date.today())
                    }

                    # Iniciar conversación con el agente
                    resultado = iniciarConversacionAgente(mensaje_inicial, meta)

                    # Guardar en session state
                    st.session_state.conversacion_id = resultado["conversacion_id"]
                    st.session_state.nivel_riesgo = resultado["nivel_riesgo"]

                    # Agregar mensaje inicial del empleado
                    st.session_state.mensajes.append({
                        "rol": "empleado",
                        "contenido": mensaje_inicial
                    })

                    # Si el agente requiere seguimiento
                    if resultado["requiere_seguimiento"] and resultado["pregunta"]:
                        st.session_state.conversacion_activa = True

                        # Agregar pregunta del agente
                        st.session_state.mensajes.append({
                            "rol": "agente",
                            "contenido": resultado["pregunta"]
                        })

                        st.rerun()

                    else:
                        # No requiere seguimiento - mostrar solo confirmación
                        st.success("¡Gracias por tu comentario!")
                        st.balloons()

                        st.info(
                            f"**Análisis:** {resultado['razon_seguimiento']}\n\n"
                            "Tu comentario ha sido registrado y el equipo de Recursos Humanos "
                            "lo revisará."
                        )

                        if st.button("Enviar otro comentario"):
                            st.rerun()

                except Exception as e:
                    st.error("Hubo un error al procesar tu mensaje. Por favor, intenta de nuevo.")
                    st.write(f"Error: {str(e)}")

    else:
        # Conversación activa - mostrar chat
        st.markdown("---")

        # Mostrar historial de mensajes
        for mensaje in st.session_state.mensajes:
            mostrar_mensaje(
                mensaje["rol"],
                mensaje["contenido"],
                st.session_state.nivel_riesgo if mensaje["rol"] == "agente" else None
            )

        # Si la conversación está cerrada, mostrar mensaje final
        if st.session_state.conversacion_cerrada:
            st.success("Gracias por compartir tu situación.")
            st.info(
                "La información que compartiste será analizada por el equipo de Recursos Humanos "
                "para tomar las acciones correspondientes. Tu conversación ha sido registrada de "
                "forma confidencial."
            )

            if st.button("Iniciar nueva conversación"):
                # Limpiar session state
                st.session_state.conversacion_activa = False
                st.session_state.conversacion_id = None
                st.session_state.mensajes = []
                st.session_state.nivel_riesgo = None
                st.session_state.conversacion_cerrada = False
                st.rerun()

            return

        # Campo para responder
        st.markdown("---")

        with st.form("form_respuesta", clear_on_submit=True):
            respuesta = st.text_area(
                "Tu respuesta",
                height=100,
                placeholder="Escribe tu respuesta aquí...",
                max_chars=1000,
                key="respuesta_input"
            )

            col1, col2 = st.columns([3, 1])

            with col1:
                enviar = st.form_submit_button("Enviar respuesta", type="primary", use_container_width=True)

            with col2:
                finalizar = st.form_submit_button("Finalizar", use_container_width=True)

        if enviar:
            if not respuesta.strip():
                st.error("Por favor escribe una respuesta antes de enviar")
                return

            with st.spinner("Procesando tu respuesta..."):
                try:
                    # Enviar respuesta al agente
                    resultado = responderAgente(st.session_state.conversacion_id, respuesta)

                    # Agregar respuesta del empleado
                    st.session_state.mensajes.append({
                        "rol": "empleado",
                        "contenido": respuesta
                    })

                    # Actualizar nivel de riesgo
                    st.session_state.nivel_riesgo = resultado["nivel_riesgo"]

                    # Si el agente profundiza
                    if resultado["accion"] == "profundizar" and resultado["pregunta"]:
                        # Agregar nueva pregunta del agente
                        st.session_state.mensajes.append({
                            "rol": "agente",
                            "contenido": resultado["pregunta"]
                        })

                        st.rerun()

                    # Si el agente cierra la conversación
                    elif resultado["accion"] == "cerrar":
                        st.session_state.conversacion_cerrada = True
                        st.rerun()

                except Exception as e:
                    st.error("Hubo un error al procesar tu respuesta. Por favor, intenta de nuevo.")
                    st.write(f"Error: {str(e)}")

        if finalizar:
            st.session_state.conversacion_cerrada = True
            st.rerun()

    # Footer
    st.markdown("---")
    st.caption("Sistema confidencial de bienestar laboral - Recursos Humanos")


# Función para integrar en app_publica.py
def main():
    """Función principal para ejecutar como página standalone"""
    st.set_page_config(
        page_title="Agente de Bienestar",
        page_icon="",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    mostrar_chat_agente()


if __name__ == "__main__":
    main()
