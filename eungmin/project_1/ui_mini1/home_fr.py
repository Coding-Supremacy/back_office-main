import streamlit as st
from pathlib import Path
import base64

def run_home_fr():
    st.markdown("<h1 style='text-align: center;'>🚗 Système de Recommandation de Véhicules & Promotions Personnalisées</h1>", unsafe_allow_html=True)

    st.divider()

    # Brève introduction de l'application
    st.write("Cette application utilise l'intelligence artificielle pour recommander des véhicules et analyser les données clients pour fournir des promotions personnalisées.")

    img_path = Path(__file__).parent.parent / "img" / "home2.png"

    # Lire le fichier image et encoder en base64
    with open(img_path, "rb") as file:
        contents = file.read()
        data_url = base64.b64encode(contents).decode("utf-8")

    # Afficher l'image centrée en utilisant HTML
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center;">
            <img src="data:image/png;base64,{data_url}" width="500">
        </div>
        """,
        unsafe_allow_html=True
    )

    # Mise en page à 3 cartes pour les principales fonctionnalités
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("#### 📊 Analyse Client")
        st.info("Analysez les clients et fournissez des informations basées sur les données.")

    with col2:
        st.write("#### 🤖 Prédiction IA")
        st.success("Prédisez les types de clients à l'aide de modèles d'apprentissage automatique.")

    with col3:
        st.write("#### ✉️ Livraison de Promotion")
        st.warning("Envoyez automatiquement des e-mails personnalisés basés sur les résultats d'analyse.")