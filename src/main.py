"""
Archivo Principal (main.py): Orquesta la ejecución del prototipo
y levanta la interfaz visual ligera para la prueba de concepto.
"""

import streamlit as st
from connector import DataConnector
from engine import CentinelaEngine

def main():
    st.title("Centinela - Auditoría Inteligente de Huella Digital")
    st.write("Prototipo de prueba para el Hito 2 - PTIA")

    user_email = st.text_input("Ingresa tu correo para auditar:", "usuario@example.com")

    if st.button("Empezar Caso"):
        with st.spinner("Analizando fuentes de riesgo y generando expediente..."):
            # 1. Recolectar datos
            connector = DataConnector(user_email)
            breach = connector.fetch_breach_data()
            activity = connector.fetch_activity_logs()
            photos = connector.fetch_photo_metadata()

            raw_data = {"breach": breach, "logs": activity, "photos": photos}

            engine = CentinelaEngine()
            report = engine.generate_case_report(raw_data)

            st.success("¡Caso analizado con éxito!")
            st.subheader(f"Expediente: {report['case_id']}")

            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="Puntuación de Seguridad", value=f"{report['score']}/100", delta=report["status"])
            with col2:
                st.write("**Resumen de hallazgos:**")
                st.json(report["summary_counts"])

            st.markdown("---")
            st.info(f"**Recomendación del Agente:** {report['recommendation']}")

if __name__ == "__main__":
    main()