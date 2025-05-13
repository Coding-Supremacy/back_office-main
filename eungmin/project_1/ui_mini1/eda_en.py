
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

# Developer mode settings
prod = True
prod_email = "marurun@naver.com"
brand = st.session_state.get("brand", "Hyundai")

def generate_marketing_strategies(country_df):
    strategies = {}
    clusters = sorted(country_df['고객유형'].unique())
    
    # Gender analysis (using original Korean column name '성별')
    gender_dist = country_df.groupby(['고객유형', '성별']).size().unstack(fill_value=0)
    gender_pct = gender_dist.div(gender_dist.sum(axis=1), axis=0) * 100
    
    # Age analysis (using original Korean column name '연령')
    age_stats = country_df.groupby('고객유형')['연령'].agg(['mean', 'std'])
    
    # Transaction analysis (using original Korean column name '거래 금액')
    transaction_stats = country_df.groupby('고객유형')['거래 금액'].mean()
    
    # Frequency analysis (using original Korean column name '제품구매빈도')
    freq_stats = country_df.groupby('고객유형')['제품구매빈도'].mean()

    for cluster in clusters:
        strategy_parts = []
        male_pct = gender_pct.loc[cluster, '남']
        female_pct = gender_pct.loc[cluster, '여']
        
        if male_pct >= 60:
            strategy_parts.append("• Special promotion for sporty designs and tech features!")
        elif female_pct >= 60:
            strategy_parts.append("• Family-friendly vehicle benefits with safety focus")
        else:
            strategy_parts.append("• Diverse options for all customer preferences")

        avg_age = age_stats.loc[cluster, 'mean']
        if avg_age < 35:
            strategy_parts.append("Trendy models with smart connectivity features")
        elif avg_age >= 45:
            strategy_parts.append("Comfort and safety focused models with special discounts")
        
        avg_transaction = transaction_stats.loc[cluster]
        transaction_median = transaction_stats.median()
        if avg_transaction >= transaction_median * 1.2:
            strategy_parts.append("VIP concierge service for premium models")
        
        avg_freq = freq_stats.loc[cluster]
        freq_median = freq_stats.median()
        if avg_freq >= freq_median * 1.5:
            strategy_parts.append("Loyalty rewards and maintenance benefits")

        strategies[cluster] = "<br>• ".join(strategy_parts)
    
    return strategies, brand_recommendations

def send_email(customer_name, customer_email, message, cluster=None, marketing_strategies=None, brand_recommendations=None, purchased_model=None):
    if not prod:
        original_email = customer_email
        customer_email = prod_email
        message = f"[DEV MODE] Original recipient: {original_email}<br><br>{message}"
    
    brand = st.session_state.get("brand", "Hyundai")
    
    if brand == "Hyundai":
        primary_color = "#005bac"
        logo_alt = "Hyundai Logo"
        logo_cid = "hyundai_logo"
        brand_name = "Hyundai Motors"
        logo_path = "main/project_1/img/hyundai_logo.jpg"
    else:
        primary_color = "#c10b30"
        logo_alt = "Kia Logo"
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
    msg['Subject'] = f"Personalized Vehicle Recommendations for {customer_name}" if prod else f"[TEST] Recommendations for {customer_name}"

    recommended_models = []
    if cluster and brand_recommendations and brand in brand_recommendations:
        cluster_key = cluster - 1 if brand == "Hyundai" else cluster
        if cluster_key in brand_recommendations[brand]:
            if purchased_model:
                recommended_models = [model for model in brand_recommendations[brand][cluster_key] 
                                    if model != purchased_model]
            else:
                recommended_models = brand_recommendations[brand][cluster_key]
    
    strategy_box_content = ""
    if cluster and marketing_strategies and cluster in marketing_strategies:
        strategy_box_content += f"""
        <div style="margin-bottom: 20px;">
            <h3 style="margin-top: 0; margin-bottom: 15px; color: {primary_color}; font-size: 18px;">Your Custom Recommendations</h3>
            <div style="font-size: 15px; line-height: 1.6;">
                {marketing_strategies[cluster].replace('<br>• ', '<br>• ')}
            </div>
        </div>
        """

    if recommended_models:
        models_html = "<h3 style='margin-bottom: 15px; color: {}; font-size: 18px;'>Recommended Models</h3><ul style='padding-left: 20px; margin-top: 0;'>".format(primary_color)
        models_html += "".join([f"<li style='margin-bottom: 8px;'>{model}</li>" for model in recommended_models])
        models_html += "</ul>"
        strategy_box_content += f"""
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
                    <h1 style="margin: 0;">🚗 {brand_name} Personalized Offers 🚗</h1>
                </td>
            </tr>
            <tr>
                <td style="padding: 30px;">
                    <div style="text-align: center; margin-bottom: 25px;">
                        <img src="cid:{logo_cid}" alt="{logo_alt}" style="width: 100%; max-width: 300px; border-radius: 8px;">
                    </div>
                    <p style="font-size: 18px; text-align: center; margin-bottom: 25px;">Dear <strong>{customer_name}</strong>,</p>
                    <div style="background: #f8f9fa; padding: 25px; border-radius: 10px; margin-top: 20px; border: 1px solid #e0e0e0;">
                        {strategy_box_content}
                        <div style="font-size: 15px; line-height: 1.7; padding-top: 15px; border-top: 1px solid #e0e0e0; margin-top: 20px;">
                            {message}
                        </div>
                    </div>
                    <div style="text-align: center; margin-top: 30px;">
                        <a href="https://www.{'hyundai' if brand == 'Hyundai' else 'kia'}.com" 
                            style="display: inline-block; background: {primary_color}; color: white; padding: 14px 28px; 
                                text-decoration: none; border-radius: 6px; font-size: 16px; font-weight: 600;">
                            View Offers
                        </a>
                    </div>
                </td>
            </tr>
            <tr>
                <td style="padding: 20px 15px 15px 15px; font-size: 13px; text-align: center; color: #777; border-top: 1px solid #eee;">
                    ※ This is an automated message. Please contact customer service for inquiries.
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
        st.error(f"Logo attachment failed: {str(e)}")

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, customer_email, msg.as_string())
        server.quit()
    except Exception as e:
        st.error(f"Email sending failed: {str(e)}")

# Auto-refresh every 10 seconds
st_autorefresh(interval=10000, limit=None, key=f"refresh_{time.time()}")

def generate_gender_insights(gender_pct):
    insights = ["**📊 Gender Distribution Insights**"]
    max_male = gender_pct['남'].idxmax()
    max_female = gender_pct['여'].idxmax()
    balanced = (gender_pct['남'] - gender_pct['여']).abs().idxmin()
    
    insights.append(f"- Highest male ratio: Type {max_male} ({gender_pct.loc[max_male, '남']:.1f}%)")
    insights.append(f"- Highest female ratio: Type {max_female} ({gender_pct.loc[max_female, '여']:.1f}%)")
    insights.append(f"- Most balanced: Type {balanced} (Male {gender_pct.loc[balanced, '남']:.1f}% / Female {gender_pct.loc[balanced, '여']:.1f}%)")
    
    marketing = ["**🎯 Marketing Suggestions**"]
    male_dominant = gender_pct[gender_pct['남'] >= 60].index.tolist()
    if male_dominant:
        marketing.append(f"- Types {', '.join(map(str, male_dominant))}: Male-focused promotions (sport models, tech features)")
    
    return "\n".join(insights + [""] + marketing)

def generate_age_insights(age_stats):
    insights = ["**📊 Age Distribution Insights**"]
    youngest = age_stats['mean'].idxmin()
    oldest = age_stats['mean'].idxmax()
    
    insights.append(f"- Youngest customers: Type {youngest} (Avg. {age_stats.loc[youngest, 'mean']:.1f} yrs)")
    insights.append(f"- Oldest customers: Type {oldest} (Avg. {age_stats.loc[oldest, 'mean']:.1f} yrs)")
    
    marketing = ["**🎯 Marketing Suggestions**"]
    young_types = age_stats[age_stats['mean'] < 40].index.tolist()
    if young_types:
        marketing.append(f"- Types {', '.join(map(str, young_types))}: Social media campaigns, trendy designs")
    
    return "\n".join(insights + [""] + marketing)

def run_eda_en():
    brand = st.session_state.get("brand", "Hyundai")
    country = st.session_state.get("country", "")
    
    selected_analysis = option_menu(
        menu_title=None,
        options=[
            "👥 Gender Distribution",
            "👵 Age Distribution", 
            "💰 Transaction Amounts",
            "🛒 Purchase Frequency",
            "🚘 Model Analysis",
            "🏷️ Customer Segments",
            "📝 Full Report"
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
        
        if selected_analysis == "👥 Gender Distribution":
            st.title(f"{brand} - {country} Market Analysis")
            st.header("Gender Distribution by Customer Type")
            
            gender_dist = country_df.groupby(['고객유형', '성별']).size().unstack(fill_value=0)
            fig = px.bar(gender_dist, barmode='group',
                        title=f'Gender Distribution by Customer Type',
                        labels={'value':'Count', '고객유형':'Customer Type'},
                        color_discrete_map={'남':'#3498db', '여':'#e74c3c'})
            st.plotly_chart(fig)
            
            st.markdown(generate_gender_insights(gender_dist.div(gender_dist.sum(axis=1), axis=0)*100))
            
        elif selected_analysis == "👵 Age Distribution":
            st.header("Age Distribution Analysis")
            fig = px.box(country_df, x='고객유형', y='연령', 
                        title='Age Distribution by Customer Type')
            st.plotly_chart(fig)
            
            age_stats = country_df.groupby('고객유형')['연령'].agg(['mean', 'std']).round(1)
            st.markdown(generate_age_insights(age_stats))
            
        # Additional analysis sections would follow the same pattern...
        
        elif selected_analysis == "📝 Full Report":
            st.header("Comprehensive Customer Analysis Report")
            marketing_strategies, _ = generate_marketing_strategies(country_df)
            
            if not prod:
                st.warning(f"⚠️ Developer Mode Active (Emails will be sent to {prod_email})")
            
            # Generate report sections...
            
            # Email sending functionality
            selected_type = st.selectbox("Select Customer Type", sorted(country_df['고객유형'].unique()))
            email_content = st.text_area("Email Content", 
                                       f"Dear Customer,\n\nWe have special offers tailored for you...")
            
            if st.button("Send Promotional Emails"):
                with st.spinner("Sending emails..."):
                    # Email sending logic
                    pass

if __name__ == "__main__":
    run_eda_en()