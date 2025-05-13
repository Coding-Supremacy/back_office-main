
import streamlit as st
import os
import pandas as pd
import plotly.express as px
import plotly.colors as pc
from streamlit_option_menu import option_menu
from streamlit_autorefresh import st_autorefresh
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import datetime
from email.mime.image import MIMEImage
import time
from project_1.ui_mini1.vehicle_recommendations_data import (
    brand_recommendations,
    vehicle_recommendations
)

# Mode développeur (True: production, False: mode développeur)
prod = True
prod_email = "marurun@naver.com"
brand = st.session_state.get("brand", "Hyundai")

def generate_marketing_strategies(country_df):
    strategies = {}
    clusters = sorted(country_df['고객유형'].unique())
    
    # Analyse par genre (colonne originale coréenne '성별')
    gender_dist = country_df.groupby(['고객유형', '성별']).size().unstack(fill_value=0)
    gender_pct = gender_dist.div(gender_dist.sum(axis=1), axis=0) * 100
    
    # Analyse par âge (colonne originale '연령')
    age_stats = country_df.groupby('고객유형')['연령'].agg(['mean', 'std'])
    
    # Analyse des transactions (colonne originale '거래 금액')
    transaction_stats = country_df.groupby('고객유형')['거래 금액'].mean()
    
    # Fréquence d'achat (colonne originale '제품구매빈도')
    freq_stats = country_df.groupby('고객유형')['제품구매빈도'].mean()

    for cluster in clusters:
        strategy_parts = []
        male_pct = gender_pct.loc[cluster, '남']
        female_pct = gender_pct.loc[cluster, '여']
        
        if male_pct >= 60:
            strategy_parts.append("• Promotion spéciale pour les modèles sportifs!")
        elif female_pct >= 60:
            strategy_parts.append("• Avantages pour véhicules familiaux sécuritaires")
        else:
            strategy_parts.append("• Options diversifiées pour tous les goûts")

        avg_age = age_stats.loc[cluster, 'mean']
        if avg_age < 35:
            strategy_parts.append("Modèles tendance avec technologies connectées")
        elif avg_age >= 45:
            strategy_parts.append("Modèles axés sur le confort avec rabais spéciaux")
        
        avg_transaction = transaction_stats.loc[cluster]
        transaction_median = transaction_stats.median()
        if avg_transaction >= transaction_median * 1.2:
            strategy_parts.append("Service concierge VIP pour modèles premium")
        
        avg_freq = freq_stats.loc[cluster]
        freq_median = freq_stats.median()
        if avg_freq >= freq_median * 1.5:
            strategy_parts.append("Avantages fidélité et entretien")

        strategies[cluster] = "<br>• ".join(strategy_parts)
    
    return strategies, brand_recommendations

def send_email(customer_name, customer_email, message, cluster=None, marketing_strategies=None, brand_recommendations=None, purchased_model=None):
    if not prod:
        original_email = customer_email
        customer_email = prod_email
        message = f"[MODE DÉVELOPPEUR] Destinataire original : {original_email}<br><br>{message}"
    
    brand = st.session_state.get("brand", "Hyundai")
    
    if brand == "Hyundai":
        primary_color = "#005bac"
        logo_alt = "Logo Hyundai"
        logo_cid = "hyundai_logo"
        brand_name = "Hyundai Motors"
        logo_path = "main/project_1/img/hyundai_logo.jpg"
    else:
        primary_color = "#c10b30"
        logo_alt = "Logo Kia"
        logo_cid = "kia_logo"
        brand_name = "Kia Motors"
        logo_path = "main/project_1/img/kia_logo.png"
    
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    EMAIL_ADDRESS = "vhzkflfltm6@gmail.com"
    EMAIL_PASSWORD = "cnvc dpea ldyv pfgq"
    
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = customer_email
    msg['Subject'] = f"Recommandations personnalisées de véhicules pour {customer_name}" if prod else f"[TEST] Recommandations pour {customer_name}"

    modeles_recommandes = []
    if cluster and brand_recommendations and brand in brand_recommendations:
        cluster_key = cluster - 1 if brand == "Hyundai" else cluster
        if cluster_key in brand_recommendations[brand]:
            if purchased_model:
                modeles_recommandes = [modele for modele in brand_recommendations[brand][cluster_key] 
                                    if modele != purchased_model]
            else:
                modeles_recommandes = brand_recommendations[brand][cluster_key]
    
    contenu_strategie = ""
    if cluster and marketing_strategies and cluster in marketing_strategies:
        contenu_strategie += f"""
        <div style="margin-bottom: 20px;">
            <h3 style="margin-top: 0; margin-bottom: 15px; color: {primary_color}; font-size: 18px;">Vos recommandations</h3>
            <div style="font-size: 15px; line-height: 1.6;">
                {marketing_strategies[cluster].replace('<br>• ', '<br>• ')}
            </div>
        </div>
        """

    if modeles_recommandes:
        models_html = "<h3 style='margin-bottom: 15px; color: {}; font-size: 18px;'>Modèles recommandés</h3><ul style='padding-left: 20px; margin-top: 0;'>".format(primary_color)
        models_html += "".join([f"<li style='margin-bottom: 8px;'>{modele}</li>" for modele in modeles_recommandes])
        models_html += "</ul>"
        contenu_strategie += f"""
        <div style="margin: 25px 0 20px 0;">
            {models_html}
        </div>
        """

    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 30px;">
        <table style="width: 100%; max-width: 800px; margin: auto; background: white; padding: 30px; 
                    border-radius: 15px; box-shadow: 0px 5px 15px rgba(0,0,0,0.1);">
            <tr>
                <td style="text-align: center; padding: 20px; background: {primary_color}; color: white; 
                        border-top-left-radius: 15px; border-top-right-radius: 15px;">
                    <h1 style="margin: 0;">🚗 Offres personnalisées {brand_name} 🚗</h1>
                </td>
            </tr>
            <tr>
                <td style="padding: 30px;">
                    <div style="text-align: center; margin-bottom: 25px;">
                        <img src="cid:{logo_cid}" alt="{logo_alt}" style="width: 100%; max-width: 300px; border-radius: 8px;">
                    </div>
                    <p style="font-size: 18px; text-align: center; margin-bottom: 25px;">Bonjour <strong>{customer_name}</strong>,</p>
                    <div style="background: #f8f9fa; padding: 25px; border-radius: 10px; margin-top: 20px; border: 1px solid #e0e0e0;">
                        {contenu_strategie}
                        <div style="font-size: 15px; line-height: 1.7; padding-top: 15px; border-top: 1px solid #e0e0e0; margin-top: 20px;">
                            {message}
                        </div>
                    </div>
                    <div style="text-align: center; margin-top: 30px;">
                        <a href="https://www.{'hyundai' if brand == 'Hyundai' else 'kia'}.com" 
                            style="display: inline-block; background: {primary_color}; color: white; padding: 14px 28px; 
                                text-decoration: none; border-radius: 6px; font-size: 16px; font-weight: 600;">
                            Voir les offres
                        </a>
                    </div>
                </td>
            </tr>
            <tr>
                <td style="padding: 20px 15px 15px 15px; font-size: 13px; text-align: center; color: #777; border-top: 1px solid #eee;">
                    ※ Ceci est un message automatisé. Contactez le service client pour toute question.
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    msg.attach(MIMEText(html_body, 'html'))
    try:
        with open(logo_path, 'rb') as img_file:
            img = MIMEImage(img_file.read())
            img.add_header('Content-ID', f'<{logo_cid}>')
            msg.attach(img)
    except Exception as e:
        st.error(f"Échec de l'ajout du logo : {str(e)}")

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, customer_email, msg.as_string())
        server.quit()
    except Exception as e:
        st.error(f"Échec de l'envoi du courriel : {str(e)}")

# Actualisation automatique chaque 10 secondes
st_autorefresh(interval=10000, limit=None, key=f"actualisation_{time.time()}")

def generate_gender_insights(gender_pct):
    insights = ["**📊 Analyse par genre**"]
    max_male = gender_pct['남'].idxmax()
    max_female = gender_pct['여'].idxmax()
    equilibre = (gender_pct['남'] - gender_pct['여']).abs().idxmin()
    
    insights.append(f"- Plus haut ratio masculin : Type {max_male} ({gender_pct.loc[max_male, '남']:.1f}%)")
    insights.append(f"- Plus haut ratio féminin : Type {max_female} ({gender_pct.loc[max_female, '여']:.1f}%)")
    insights.append(f"- Plus équilibré : Type {equilibre} (Homme {gender_pct.loc[equilibre, '남']:.1f}% / Femme {gender_pct.loc[equilibre, '여']:.1f}%)")
    
    marketing = ["**🎯 Suggestions marketing**"]
    dominant_male = gender_pct[gender_pct['남'] >= 60].index.tolist()
    if dominant_male:
        marketing.append(f"- Types {', '.join(map(str, dominant_male))}: Promotions ciblant les hommes (modèles sportifs)")
    
    return "\n".join(insights + [""] + marketing)

def generate_age_insights(age_stats):
    insights = ["**📊 Analyse par âge**"]
    plus_jeune = age_stats['mean'].idxmin()
    plus_age = age_stats['mean'].idxmax()
    
    insights.append(f"- Clients les plus jeunes : Type {plus_jeune} (Moy. {age_stats.loc[plus_jeune, 'mean']:.1f} ans)")
    insights.append(f"- Clients les plus âgés : Type {plus_age} (Moy. {age_stats.loc[plus_age, 'mean']:.1f} ans)")
    
    marketing = ["**🎯 Suggestions marketing**"]
    types_jeunes = age_stats[age_stats['mean'] < 40].index.tolist()
    if types_jeunes:
        marketing.append(f"- Types {', '.join(map(str, types_jeunes))}: Campagnes sur les réseaux sociaux, designs tendance")
    
    return "\n".join(insights + [""] + marketing)

def run_eda_es():
    brand = st.session_state.get("brand", "Hyundai")
    country = st.session_state.get("country", "")
    
    selected_analysis = option_menu(
        menu_title=None,
        options=[
            "👥 Répartition par genre",
            "👵 Répartition par âge", 
            "💰 Montant des transactions",
            "🛒 Fréquence d'achat",
            "🚘 Analyse des modèles",
            "🏷️ Segments clients",
            "📝 Rapport complet"
        ],
        icons=["gender-male", "person", "cash", "cart", "car", "tags", "file-text"],
        menu_icon="bar-chart",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#f9f9f9"},
            "icon": {"color": "#2E86C1", "font-size": "18px"},
            "nav-link": {"font-size": "16px", "text-align": "center", "margin": "0px", "padding": "10px"},
            "nav-link-selected": {"background-color": "#2E86C1", "color": "white"},
        }
    )

    csv_path = os.path.abspath(f"data/{brand}_고객데이터_신규입력용.csv")
    
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        country_df = df[df['국가'] == country].copy()
        country_df['고객유형'] = country_df['Cluster'] + 1
        
        if selected_analysis == "👥 Répartition par genre":
            st.title(f"{brand} - Analyse du marché {country}")
            st.header("Répartition par genre et type de client")
            
            gender_dist = country_df.groupby(['고객유형', '성별']).size().unstack(fill_value=0)
            fig = px.bar(gender_dist, barmode='group',
                        title='Répartition par genre',
                        labels={'value':'Nombre', '고객유형':'Type de client'},
                        color_discrete_map={'남':'#3498db', '여':'#e74c3c'})
            st.plotly_chart(fig)
            
            st.markdown(generate_gender_insights(gender_dist.div(gender_dist.sum(axis=1), axis=0)*100))
            
        elif selected_analysis == "👵 Répartition par âge":
            st.header("Analyse par âge")
            fig = px.box(country_df, x='고객유형', y='연령', 
                        title='Répartition par âge')
            st.plotly_chart(fig)
            
            age_stats = country_df.groupby('고객유형')['연령'].agg(['mean', 'std']).round(1)
            st.markdown(generate_age_insights(age_stats))
            
        # Sections d'analyse supplémentaires...
        
        elif selected_analysis == "📝 Rapport complet":
            st.header("Rapport complet d'analyse client")
            strategies_marketing, _ = generate_marketing_strategies(country_df)
            
            if not prod:
                st.warning(f"⚠️ Mode développeur actif (Courriels envoyés à {prod_email})")
            
            # Génération des sections du rapport...
            
            # Fonctionnalité d'envoi de courriels
            type_selectionne = st.selectbox("Sélectionnez un type de client", sorted(country_df['고객유형'].unique()))
            contenu_courriel = st.text_area("Contenu du courriel", 
                                       f"Cher client,\n\nNous avons des offres spéciales pour vous...")
            
            if st.button("Envoyer les promotions"):
                with st.spinner("Envoi en cours..."):
                    # Logique d'envoi de courriels
                    pass

if __name__ == "__main__":
    run_eda_es()