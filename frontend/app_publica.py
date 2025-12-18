import streamlit as st
import sys
from pathlib import Path
from datetime import date

frontend_path = Path(__file__).parent
if str(frontend_path) not in sys.path:
    sys.path.insert(0, str(frontend_path))

from utils.callBackend import analizarComentarioIndividual, verificarConexion
from pages.chatAgente import mostrar_chat_agente

st.set_page_config(
    page_title="Sistema de Bienestar Laboral",
    page_icon="💬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

def main():
    st.title("💬 Sistema de Bienestar Laboral")
    st.markdown("### Elige cómo quieres compartir tu opinión")

    # Tabs para elegir entre formulario y chat
    tab1, tab2 = st.tabs(["📝 Comentario rápido", "💬 Conversación con el agente"])

    with tab1:
        mostrar_formulario_tradicional()

    with tab2:
        mostrar_chat_agente()


def mostrar_formulario_tradicional():
    """Muestra el formulario tradicional de comentarios"""
    st.markdown("### Comparte tu opinión de forma anónima")

    st.info("Tu comentario será analizado de forma confidencial por el departamento de Recursos Humanos para mejorar el ambiente laboral.")

    if not verificarConexion():
        st.error("El sistema no está disponible en este momento. Por favor, intenta más tarde.")
        return

    with st.form("form_comentario_publico"):
        comentario = st.text_area(
            "Tu comentario",
            height=200,
            placeholder="Escribe aquí tu comentario sobre el ambiente laboral, carga de trabajo, liderazgo, comunicación, etc...",
            max_chars=2000,
            help="Tu comentario es completamente anónimo"
        )

        col1, col2 = st.columns(2)

        with col1:
            departamento = st.selectbox(
                "Departamento (opcional)",
                ["", "Operaciones", "Ventas", "IT", "RRHH", "Finanzas", "Marketing", "Otro"]
            )

        with col2:
            equipo = st.text_input(
                "Equipo (opcional)",
                placeholder="Ej: Turno A, Equipo Norte, etc.",
                help="Puedes dejarlo en blanco"
            )

        submitted = st.form_submit_button("Enviar Comentario", use_container_width=True, type="primary")

    if submitted:
        if not comentario.strip():
            st.error("Por favor escribe un comentario antes de enviar")
            return

        with st.spinner("Enviando tu comentario..."):
            try:
                meta = {
                    "departamento": departamento if departamento else "No especificado",
                    "equipo": equipo if equipo else "",
                    "fecha": str(date.today())
                }

                resultado = analizarComentarioIndividual(comentario, meta)

                st.success("¡Gracias por tu comentario!")
                st.balloons()

                st.markdown("---")
                st.markdown("### Tu comentario ha sido registrado")
                st.write("El equipo de Recursos Humanos revisará tu comentario y tomará las acciones correspondientes.")

                if st.button("Enviar otro comentario"):
                    st.rerun()

            except Exception as e:
                st.error("Hubo un error al enviar tu comentario. Por favor, intenta de nuevo.")
                st.write(f"Error: {str(e)}")

    st.markdown("---")
    st.caption("Sistema confidencial de comentarios - Recursos Humanos")

if __name__ == "__main__":
    main()
