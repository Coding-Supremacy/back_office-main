import streamlit as st
from pathlib import Path
import base64

def run_home_es():
    st.markdown("<h1 style='text-align: center;'>🚗 Sistema de Recomendación de Vehículos y Promociones Personalizadas</h1>", unsafe_allow_html=True)

    st.divider()

    # Breve introducción de la aplicación
    st.write("Esta aplicación utiliza inteligencia artificial para recomendar vehículos y analizar datos de clientes para ofrecer promociones personalizadas.")

    img_path = Path(__file__).parent.parent / "img" / "home2.png"

    # Leer archivo de imagen y codificar en base64
    with open(img_path, "rb") as file:
        contents = file.read()
        data_url = base64.b64encode(contents).decode("utf-8")

    # Mostrar imagen centrada usando HTML
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center;">
            <img src="data:image/png;base64,{data_url}" width="500">
        </div>
        """,
        unsafe_allow_html=True
    )

    # Diseño de 3 tarjetas para características principales
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("#### 📊 Análisis de Clientes")
        st.info("Analiza clientes y proporciona información basada en datos.")

    with col2:
        st.write("#### 🤖 Predicción con IA")
        st.success("Predice tipos de clientes utilizando modelos de aprendizaje automático.")

    with col3:
        st.write("#### ✉️ Envío de Promociones")
        st.warning("Envía automáticamente correos electrónicos personalizados basados en resultados de análisis.")