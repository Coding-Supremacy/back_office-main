import streamlit as st
from pathlib import Path
import base64

def run_home_en():
    st.markdown("<h1 style='text-align: center;'>🚗 Vehicle Recommendation & Personalized Promotion System</h1>", unsafe_allow_html=True)

    st.divider()

    # Brief app introduction
    st.write("This app uses artificial intelligence to recommend vehicles and analyze customer data to provide personalized promotions.")

    img_path = Path(__file__).parent.parent / "img" / "home2.png"

    # Read image file and base64 encode
    with open(img_path, "rb") as file:
        contents = file.read()
        data_url = base64.b64encode(contents).decode("utf-8")

    # Display centered image using HTML
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center;">
            <img src="data:image/png;base64,{data_url}" width="500">
        </div>
        """,
        unsafe_allow_html=True
    )

    # 3-card layout for main features
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("#### 📊 Customer Analysis")
        st.info("Analyze customers and provide insights based on data.")

    with col2:
        st.write("#### 🤖 AI Prediction")
        st.success("Predict customer types using machine learning models.")

    with col3:
        st.write("#### ✉️ Promotion Delivery")
        st.warning("Automatically send personalized emails based on analysis results.")