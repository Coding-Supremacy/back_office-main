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

def send_email(customer_name, customer_email, message, cluster=None, marketing_strategies=None):
    # SMTP 서버 설정
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    EMAIL_ADDRESS = "vhzkflfltm6@gmail.com"
    EMAIL_PASSWORD = "cnvc dpea ldyv pfgq" 
    
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = customer_email
    msg['Subject'] = f"{customer_name}님, 프로모션 안내"

    # 마케팅 전략이 제공된 경우 메시지에 추가
    strategy_message = ""
    if cluster and marketing_strategies and cluster in marketing_strategies:
        strategy_message = f"""
        <div style="background: #e8f4fc; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #005bac;">
            <h3 style="margin-top: 0; color: #005bac;">고객님을 위한 맞춤형 제안</h3>
            <p>{marketing_strategies[cluster]}</p>
        </div>
        """

    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 30px;">
        <table style="width: 100%; max-width: 800px; margin: auto; background: white; padding: 30px; 
                    border-radius: 15px; box-shadow: 0px 5px 15px rgba(0,0,0,0.1);">
            <!-- 헤더 영역 (로고) -->
            <tr>
                <td style="text-align: center; padding: 20px; background: #005bac; color: white; 
                        border-top-left-radius: 15px; border-top-right-radius: 15px;">
                    <h1 style="margin: 0;">🚗 현대자동차 프로모션 🚗</h1>
                </td>
            </tr>
            
            <!-- 본문 내용 -->
            <tr>
                <td style="padding: 30px; text-align: center;">
                    
                    <!-- 현대 로고 -->
                    <a href="https://www.hyundai.com" target="_blank">
                    <img src="cid:hyundai_logo"
                        alt="현대 로고" style="width: 100%; max-width: 500px; border-radius: 10px;">
                    </a>

                    <p style="font-size: 18px;">안녕하세요, <strong>{customer_name}</strong>님!</p>

                    {strategy_message}

                    <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; font-size: 16px; margin-top: 20px;">
                        {message}
                    </div>
                    
                    <a href="https://www.hyundai.com" 
                        style="display: inline-block; background: #005bac; color: white; padding: 15px 30px; 
                            text-decoration: none; border-radius: 8px; margin-top: 20px; font-size: 16px;">
                        지금 확인하기
                    </a>
                </td>
            </tr>

            <!-- 푸터 (고객센터 안내) -->
            <tr>
                <td style="padding: 15px; font-size: 14px; text-align: center; color: gray;">
                    ※ 본 메일은 자동 발송되었으며, 문의는 고객센터를 이용해주세요.
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    msg.attach(MIMEText(html_body, 'html'))

    server = smtplib.SMTP('smtp.gmail.com', 587)  # Gmail SMTP 서버 사용
    server.starttls()
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    text = msg.as_string()
    server.sendmail(EMAIL_ADDRESS, customer_email, text)
    server.quit()

# 10초마다 자동 새로고침 (10000 밀리초)
st_autorefresh(interval=10000, limit=None, key="fizzbuzz")

# 인포 메시지를 세밀하게 표시하는 함수
def custom_info(message, bg_color, text_color="black"):
    st.markdown(
        f'<div style="background-color: {bg_color}; color: {text_color}; padding: 10px; border-radius: 4px; margin-bottom: 10px;">{message}</div>',
        unsafe_allow_html=True
    )

# 기본 스타일 설정
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
    body {
        font-family: 'Roboto', sans-serif;
        background: linear-gradient(135deg, #f0f4f8, #e8f5e9);
        padding: 20px;
    }
    .css-18e3th9, .css-1d391kg { background: none; }
    .reportview-container .main {
        background-color: rgba(255,255,255,0.9);
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    }
    h1 {
        font-size: 2.5em;
        font-weight: 700;
        text-align: center;
        color: #2E86C1;
        margin-bottom: 10px;
    }
    h4 {
        text-align: center;
        color: #555;
        margin-bottom: 30px;
        font-size: 1.1em;
    }
    hr { border: 1px solid #bbb; margin: 20px 0; }
    .nav-link {
        transition: background-color 0.3s ease, transform 0.3s ease;
        border-radius: 10px;
    }
    .nav-link:hover {
        background-color: #AED6F1 !important;
        transform: scale(1.05);
    }
    .analysis-text {
        background-color: #ffffff;
        border-left: 4px solid #2E86C1;
        padding: 20px;
        margin: 30px 0;
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        font-size: 1.1em;
        color: #333;
        line-height: 1.5;
    }
    .analysis-text:hover { background-color: #f7f9fa; }
    .option-menu .nav-link-selected { background-color: #2E86C1; color: white; }
    </style>
    """,
    unsafe_allow_html=True
)

# 클러스터 색상 매핑
cluster_color_map = {
    1: "#A8E6CF",  # 연두색
    2: "#FFF9B0",  # 연노랑
    3: "#AECBFA",  # 연파랑
    4: "#FFD3B6",  # 연주황
    5: "#D5AAFF",  # 연보라
    6: "#FFB3BA",  # 연핑크
    7: "#B5EAD7",  # 민트
    8: "#E2F0CB",  # 연연두
}
today = datetime.date.today().strftime("%Y-%m-%d")

# 인사이트 자동 생성 함수
def generate_gender_insights(gender_pct):
    insights = ["**📊 성별 분포 인사이트**"]
    
    max_male = gender_pct['남'].idxmax()
    max_female = gender_pct['여'].idxmax()
    balanced_cluster = (gender_pct['남'] - gender_pct['여']).abs().idxmin()

    male_dominant = gender_pct[gender_pct['남'] >= 60].index.tolist()
    female_dominant = gender_pct[gender_pct['여'] >= 60].index.tolist()
    balanced = list(set(gender_pct.index) - set(male_dominant) - set(female_dominant))

    insights.append(f"- 가장 남성 비율 높은 클러스터: {max_male}번 ({gender_pct.loc[max_male, '남']:.1f}%)")
    insights.append(f"- 가장 여성 비율 높은 클러스터: {max_female}번 ({gender_pct.loc[max_female, '여']:.1f}%)")
    insights.append(f"- 가장 균형 잡힌 클러스터: {balanced_cluster}번 (남성 {gender_pct.loc[balanced_cluster, '남']:.1f}% / 여성 {gender_pct.loc[balanced_cluster, '여']:.1f}%)")

    marketing = ["**🎯 마케팅 제안**"]
    if male_dominant:
        marketing.append(f"- 클러스터 {', '.join(map(str, male_dominant))}: 남성 타겟 프로모션 (스포츠 모델, 기술 기능 강조)")
    if female_dominant:
        marketing.append(f"- 클러스터 {', '.join(map(str, female_dominant))}: 여성 타겟 캠페인 (안전 기능, 가족 친화적 메시지)")
    if balanced:
        marketing.append(f"- 클러스터 {', '.join(map(str, balanced))}: 일반적인 마케팅 접근 (다양한 옵션 제공)")

    return "\n".join(insights + [""] + marketing)

def generate_age_insights(age_stats):
    insights = ["**📊 연령 분포 인사이트**"]
    
    youngest = age_stats['평균 연령'].idxmin()
    oldest = age_stats['평균 연령'].idxmax()
    diverse = age_stats['표준편차'].idxmax()
    
    young_clusters = age_stats[age_stats['평균 연령'] < 40].index.tolist()
    old_clusters = age_stats[age_stats['평균 연령'] >= 40].index.tolist()
    diverse_clusters = age_stats.sort_values('표준편차', ascending=False).head(2).index.tolist()

    insights.append(f"- 가장 젊은 클러스터: {youngest}번 (평균 {age_stats.loc[youngest, '평균 연령']}세)")
    insights.append(f"- 가장 연장자 클러스터: {oldest}번 (평균 {age_stats.loc[oldest, '평균 연령']}세)")
    insights.append(f"- 가장 다양한 연령대: {diverse}번 (표준편차 {age_stats.loc[diverse, '표준편차']}세)")

    marketing = ["**🎯 마케팅 제안**"]
    if young_clusters:
        marketing.append(f"- 클러스터 {', '.join(map(str, young_clusters))}: SNS 마케팅, 트렌디한 디자인/기술 강조")
    if old_clusters:
        marketing.append(f"- 클러스터 {', '.join(map(str, old_clusters))}: 안전/편의 기능, 할인 혜택 강조")
    if diverse_clusters:
        marketing.append(f"- 클러스터 {', '.join(map(str, diverse_clusters))}: 다양한 연령층 호소 가능한 메시지")

    return "\n".join(insights + [""] + marketing)

def generate_transaction_insights(transaction_stats):
    insights = ["**📊 거래 금액 인사이트**"]
    
    high_value = transaction_stats['평균 거래액'].idxmax()
    low_value = transaction_stats['평균 거래액'].idxmin()
    total_sales = transaction_stats['총 거래액'].sum()
    
    high_value_clusters = transaction_stats[transaction_stats['평균 거래액'] >= transaction_stats['평균 거래액'].quantile(0.75)].index.tolist()
    low_value_clusters = transaction_stats[transaction_stats['평균 거래액'] <= transaction_stats['평균 거래액'].quantile(0.25)].index.tolist()

    insights.append(f"- 최고 평균 거래액 클러스터: {high_value}번 ({transaction_stats.loc[high_value, '평균 거래액']:,.0f}원)")
    insights.append(f"- 최저 평균 거래액 클러스터: {low_value}번 ({transaction_stats.loc[low_value, '평균 거래액']:,.0f}원)")
    insights.append(f"- 총 거래액 ({today} 기준): {total_sales:,.0f}원")

    marketing = ["**🎯 마케팅 제안**"]
    if high_value_clusters:
        marketing.append(f"- 클러스터 {', '.join(map(str, high_value_clusters))}: 프리미엄 모델 추천, VIP 서비스 제공")
    if low_value_clusters:
        marketing.append(f"- 클러스터 {', '.join(map(str, low_value_clusters))}: 할인 프로모션, 저비용 모델 추천")

    return "\n".join(insights + [""] + marketing)


def generate_frequency_insights(freq_stats):
    insights = ["**📊 구매 빈도 인사이트**"]
    
    frequent = freq_stats['평균 구매 빈도'].idxmax()
    rare = freq_stats['평균 구매 빈도'].idxmin()
    
    frequent_clusters = freq_stats[freq_stats['평균 구매 빈도'] >= freq_stats['평균 구매 빈도'].quantile(0.75)].index.tolist()
    rare_clusters = freq_stats[freq_stats['평균 구매 빈도'] <= freq_stats['평균 구매 빈도'].quantile(0.25)].index.tolist()

    insights.append(f"- 최고 구매 빈도 클러스터: {frequent}번 (평균 {freq_stats.loc[frequent, '평균 구매 빈도']:.2f}회)")
    insights.append(f"- 최저 구매 빈도 클러스터: {rare}번 (평균 {freq_stats.loc[rare, '평균 구매 빈도']:.2f}회)")

    marketing = ["**🎯 마케팅 제안**"]
    if frequent_clusters:
        marketing.append(f"- 클러스터 {', '.join(map(str, frequent_clusters))}: 충성도 프로그램, 정기 구매 혜택")
    if rare_clusters:
        marketing.append(f"- 클러스터 {', '.join(map(str, rare_clusters))}: 재구매 유도 프로모션, 첫 구매 할인")

    return "\n".join(insights + [""] + marketing)

def generate_model_insights(model_cluster, selected_model):
    insights = [f"**📊 {selected_model} 모델 인사이트**"]
    
    main_cluster = model_cluster.idxmax()
    main_ratio = (model_cluster[main_cluster] / model_cluster.sum()) * 100
    
    top_clusters = model_cluster.nlargest(2).index.tolist()  # 상위 2개 클러스터
    other_clusters = list(set(model_cluster.index) - set(top_clusters))

    insights.append(f"- 주 구매 클러스터: {main_cluster}번 ({main_ratio:.1f}%)")
    insights.append(f"- 총 판매량: {model_cluster.sum()}대")

    marketing = ["**🎯 마케팅 제안**"]
    if top_clusters:
        marketing.append(f"- 클러스터 {', '.join(map(str, top_clusters))}: 해당 클러스터 특성에 맞는 맞춤형 프로모션")
    if other_clusters:
        marketing.append(f"- 클러스터 {', '.join(map(str, other_clusters))}: 판매 확장을 위한 타겟 마케팅 테스트")

    return "\n".join(insights + [""] + marketing)

def run_eda():
    brand = st.session_state.get("brand", "현대")
    country = st.session_state.get("country", "")

    # 분석 종류 선택 메뉴
    selected_analysis = option_menu(
        menu_title=None,
        options=[
            "👥 클러스터별 성별 분포",
            "👵 클러스터별 연령 분포",
            "💰 클러스터별 거래 금액",
            "🛒 클러스터별 구매 빈도",
            "🚘 모델별 구매 분석",
            "📝 종합 보고서 및 이메일 발송"
        ],
        icons=["", "", "", ""],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#f9f9f9"},
            "icon": {"color": "#2E86C1", "font-size": "20px"},
            "nav-link": {"font-size": "16px", "text-align": "center", "margin": "0px", "padding": "10px"},
            "nav-link-selected": {"background-color": "#2E86C1", "color": "white"},
        }
    )

    csv_path = f"data/{brand}_고객데이터_신규입력용.csv"
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        country_df = df[df['국가'] == country].copy()
        country_df['Cluster_Display'] = country_df['Cluster'] + 1
        country_df.rename(columns={"Cluster_Display": "고객유형"}, inplace=True)
        
        if selected_analysis == "👥 클러스터별 성별 분포":
            st.subheader(f"{country} - 클러스터별 성별 분포")
            
            if {'Cluster', '성별'}.issubset(country_df.columns):
                # 성별 분포 계산
                gender_dist = country_df.groupby(['고객유형', '성별']).size().unstack(fill_value=0)
                gender_pct = gender_dist.div(gender_dist.sum(axis=1), axis=0) * 100
                
                # 바 차트
                bar_fig = px.bar(
                    gender_dist, barmode='group',
                    title=f'{country} 클러스터별 성별 분포',
                    labels={'value': '고객 수', '고객유형': '클러스터'},
                    color_discrete_map={'남': '#3498db', '여': '#e74c3c'}
                )
                st.plotly_chart(bar_fig)
                
                # 비율 표시
                st.subheader("클러스터별 성별 비율 (%)")
                st.dataframe(gender_pct.style.format("{:.1f}%").background_gradient(cmap='Blues'))
                
                # 인사이트 제공
                st.markdown(generate_gender_insights(gender_pct))
                
            else:
                st.error("필요한 컬럼이 데이터에 없습니다.")

        elif selected_analysis == "👵 클러스터별 연령 분포":
            st.subheader(f"{country} - 클러스터별 연령 분포 분석")
            
            if {'Cluster', '연령'}.issubset(country_df.columns):
                # 박스플롯
                box_fig = px.box(
                    country_df, x='고객유형', y='연령',
                    title=f'{country} 클러스터별 연령 분포',
                    color='고객유형'
                )
                st.plotly_chart(box_fig)
                
                # 히스토그램
                hist_fig = px.histogram(
                    country_df, x='연령', color='고객유형',
                    nbins=20, barmode='overlay', opacity=0.7,
                    title=f'{country} 클러스터별 연령 분포 히스토그램'
                )
                st.plotly_chart(hist_fig)
                
                # 연령 통계
                age_stats = country_df.groupby('고객유형')['연령'].agg(['mean', 'median', 'std']).round(1)
                age_stats.columns = ['평균 연령', '중앙값', '표준편차']
                
                st.subheader("클러스터별 연령 통계")
                st.dataframe(age_stats.style.format({
                    '평균 연령': '{:.1f}세',
                    '중앙값': '{:.1f}세',
                    '표준편차': '{:.1f}세'
                }).background_gradient(cmap='Blues'))
                
                # 인사이트 제공
                st.markdown(generate_age_insights(age_stats))
                
            else:
                st.error("필요한 컬럼이 데이터에 없습니다.")

        elif selected_analysis == "💰 클러스터별 거래 금액":
            st.subheader(f"{country} - 클러스터별 거래 금액 분석")
            
            if {'Cluster', '거래 금액'}.issubset(country_df.columns):
                # 박스플롯
                box_fig = px.box(
                    country_df, x='고객유형', y='거래 금액',
                    title=f'{country} 클러스터별 거래 금액 분포',
                    color='고객유형'
                )
                st.plotly_chart(box_fig)
                
                # 거래 금액 통계
                # 이 코드로 대체하면 기존 함수와 호환됨
                transaction_stats = country_df.groupby('고객유형')['거래 금액'].agg(['mean', 'median', 'sum']).round()
                transaction_stats.rename(columns={'mean': '평균 거래액', 'median': '중앙값', 'sum': '총 거래액'}, inplace=True)
                transaction_stats.columns = ['평균 거래액', '중앙값', '총 거래액']
                
                st.subheader("클러스터별 거래 금액 통계")
                st.dataframe(transaction_stats.style.format({
                    '평균 거래액': '{:,.0f}원',
                    '중앙값': '{:,.0f}원',
                    '총 거래액': '{:,.0f}원'
                }).background_gradient(cmap='Blues'))
                
                # 인사이트 제공
                st.markdown(generate_transaction_insights(transaction_stats))
                
            else:
                st.error("필요한 컬럼이 데이터에 없습니다.")

        elif selected_analysis == "🛒 클러스터별 구매 빈도":
            st.subheader(f"{country} - 클러스터별 구매 빈도 분석")
            
            if {'Cluster', '제품구매빈도'}.issubset(country_df.columns):
                # 박스플롯
                box_fig = px.box(
                    country_df, x='고객유형', y='제품구매빈도',
                    title=f'{country} 클러스터별 구매 빈도 분포',
                    color='고객유형'
                )
                st.plotly_chart(box_fig)
                
                # 구매 빈도 통계
                freq_stats = country_df.groupby('고객유형')['제품구매빈도'].agg(['mean', 'median']).round(2)
                freq_stats.columns = ['평균 구매 빈도', '중앙값']
                
                st.subheader("클러스터별 구매 빈도 통계")
                st.dataframe(freq_stats.style.format({
                    '평균 구매 빈도': '{:.2f}회',
                    '중앙값': '{:.2f}회'
                }).background_gradient(cmap='Blues'))
                
                # 인사이트 제공
                st.markdown(generate_frequency_insights(freq_stats))
                
            else:
                st.error("필요한 컬럼이 데이터에 없습니다.")

        elif selected_analysis == "🚘 모델별 구매 분석":
            st.subheader(f"{country} - 모델별 구매 분석")
            
            if {'구매한 제품', 'Cluster'}.issubset(country_df.columns):
                # 모델별 판매량
                model_sales = country_df['구매한 제품'].value_counts().reset_index()
                model_sales.columns = ['모델', '판매량']
                
                # 바 차트
                bar_fig = px.bar(
                    model_sales, x='모델', y='판매량',
                    title=f'{country} 모델별 판매량',
                    color='모델',  # 컬러 매핑을 위해 추가
                    color_discrete_sequence=px.colors.sequential.Sunset
                )
                st.plotly_chart(bar_fig)
                
                # 모델 선택
                selected_model = st.selectbox(
                    "모델 선택",
                    country_df['구매한 제품'].unique(),
                    key='model_select'
                )
                
                # 선택 모델의 클러스터 분포
                model_cluster = country_df[country_df['구매한 제품'] == selected_model]['고객유형'].value_counts()
                
                # 파이 차트
                pie_fig = px.pie(
                    model_cluster, names=model_cluster.index, values=model_cluster.values,
                    title=f'{selected_model} 모델 구매 고객의 클러스터 분포',
                    color_discrete_sequence=px.colors.sequential.Sunset
                )
                st.plotly_chart(pie_fig)
                
                # 클러스터 분포 표시
                st.subheader(f"{selected_model} 모델 구매 고객 클러스터 분포")
                st.dataframe(model_cluster.to_frame('고객 수').style.format({"고객 수": "{:,}명"}))
                
                # 인사이트 제공
                st.markdown(generate_model_insights(model_cluster, selected_model))
                
            else:
                st.error("필요한 컬럼이 데이터에 없습니다.")
                
        elif selected_analysis == "📝 종합 보고서 및 이메일 발송":
                    st.subheader(f"{country} - 종합 분석 보고서 및 클러스터별 마케팅 이메일 발송")
                    
                    # 종합 분석 보고서 생성
                    st.markdown("### 📊 종합 분석 보고서")
                    
                    # 1. 기본 통계
                    st.markdown("#### 1. 기본 통계")
                    total_customers = len(country_df)
                    clusters = country_df['고객유형'].nunique()
                    avg_age = country_df['연령'].mean()
                    avg_transaction = country_df['거래 금액'].mean()
                    
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("총 고객 수", f"{total_customers:,}명")
                    col2.metric("클러스터 수", clusters)
                    col3.metric("평균 연령", f"{avg_age:.1f}세")
                    col4.metric("평균 거래액", f"{avg_transaction:,.0f}원")
                    
                    # 2. 클러스터별 주요 특성 요약
                    st.markdown("#### 2. 클러스터별 주요 특성")
                    
                    # 성별 분포
                    gender_dist = country_df.groupby(['고객유형', '성별']).size().unstack(fill_value=0)
                    gender_pct = gender_dist.div(gender_dist.sum(axis=1), axis=0) * 100
                    
                    # 연령 통계
                    age_stats = country_df.groupby('고객유형')['연령'].agg(['mean', 'std']).round(1)
                    age_stats.columns = ['평균 연령', '표준편차']
                    
                    # 거래 금액 통계
                    transaction_stats = country_df.groupby('고객유형')['거래 금액'].agg(['mean', 'sum']).round()
                    transaction_stats.columns = ['평균 거래액', '총 거래액']
                    
                    # 구매 빈도 통계
                    freq_stats = country_df.groupby('고객유형')['제품구매빈도'].mean().round(2)
                    
                    # 모든 통계를 하나의 데이터프레임으로 결합
                    summary_df = pd.concat([
                        gender_pct,
                        age_stats,
                        transaction_stats,
                        freq_stats.rename('평균 구매 빈도')
                    ], axis=1)
                    
                    st.dataframe(summary_df.style.format({
                        '남': '{:.1f}%',
                        '여': '{:.1f}%',
                        '평균 연령': '{:.1f}세',
                        '표준편차': '{:.1f}세',
                        '평균 거래액': '{:,.0f}원',
                        '총 거래액': '{:,.0f}원',
                        '평균 구매 빈도': '{:.2f}회'
                    }).background_gradient(cmap='Blues'))
                    
                    # 3. 마케팅 전략 제안
                    st.markdown("#### 3. 클러스터별 마케팅 전략 제안")
                    # 클러스터별 마케팅
                    marketing_strategies = {
                        1: "프리미엄 모델 추천 및 VIP 서비스 제공",
                        2: "할인 프로모션 및 저비용 모델 강조",
                        3: "가족 패키지 및 대형차 모델 추천",
                        4: "첫 구매 고객 대상 특별 혜택 제공",
                        5: "충성도 프로그램 및 정기 구매 혜택",
                        6: "SNS 마케팅 및 트렌디한 디자인 강조",
                        7: "안전 기능 및 편의 사항 강조",
                        8: "다양한 연령층 호소 가능한 메시지"
                    }
                    
                    for cluster, strategy in marketing_strategies.items():
                        st.markdown(f"- **클러스터 {cluster}**: {strategy}")
                    
                    # 4. 이메일 발송 기능
                    st.markdown("---")
                    st.markdown("### ✉️ 클러스터별 타겟 이메일 발송")
                    
                    # 클러스터 선택
                    selected_cluster = st.selectbox(
                        "클러스터 선택",
                        sorted(country_df['고객유형'].unique()),
                        key='email_cluster'
                    )
                    
                    # 해당 클러스터 고객 필터링
                    cluster_customers = country_df[country_df['고객유형'] == selected_cluster]
                    
                    # 이메일 내용 작성
                    st.markdown("#### 이메일 내용 작성")
                    
                    # 기본 메시지 템플릿
                    template = f"""
                    <p>현대자동차의 특별한 프로모션 소식을 전해드립니다!</p>
                    
                    <p>고객님의 구매 패턴을 분석한 결과, 다음과 같은 맞춤형 제안을 준비했습니다:</p>
                    
                    <ul>
                        <li>{marketing_strategies[selected_cluster]}</li>
                        <li>한정 기간 할인 프로모션</li>
                    </ul>
                    
                    <p>자세한 내용은 아래 링크를 확인해주세요. 감사합니다!</p>
                    """
                    
                    email_subject = st.text_input(
                        "이메일 제목",
                        f"[현대자동차] 고객님을 위한 맞춤 특별 혜택!",
                        key='email_subject'
                    )
                    
                    email_content = st.text_area(
                        "이메일 내용 (HTML 형식)",
                        template,
                        height=300,
                        key='email_content'
                    )
                    
                    # 미리보기
                    if st.checkbox("이메일 미리보기"):
                        st.markdown("### 이메일 미리보기")
                        st.markdown(f"**제목**: {email_subject}")
                        st.markdown(email_content, unsafe_allow_html=True)
                    
                    # 발송 대상 확인
                    st.markdown("#### 발송 대상 고객")
                    cluster_customers_table = cluster_customers[['이름', '이메일', '성별', '연령', '거래 금액']]
                    # 페이지 상태 초기화
                    if 'page' not in st.session_state:
                        st.session_state.page = 1

                    # 페이지네이션 설정
                    page_size = 7
                    data = cluster_customers[['이름', '이메일', '성별', '연령', '거래 금액']]
                    total_pages = max(1, (len(data) - 1) // page_size + 1)

                    col1, col2, col3 = st.columns([1, 2, 1])

                    with col1:
                        if st.button('◀ 이전', disabled=(st.session_state.page <= 1)):
                            st.session_state.page -= 1
                            st.rerun()

                    with col2:
                        st.markdown(f"<div style='text-align: center;'>페이지 {st.session_state.page} / {total_pages}</div>", unsafe_allow_html=True)

                    with col3:
                        if st.button('다음 ▶', disabled=(st.session_state.page >= total_pages)):
                            st.session_state.page += 1
                            st.rerun()

                    start_idx = (st.session_state.page - 1) * page_size
                    end_idx = min(start_idx + page_size, len(data))

                    # 데이터 표시
                    st.dataframe(data.iloc[start_idx:end_idx], height=300)
                    st.caption(f"총 {len(cluster_customers)}명의 고객에게 발송됩니다.")
                    
                    # 이메일 발송 버튼
                    # 이메일 발송 버튼
                    if st.button("이메일 발송"):
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        success_count = 0
                        fail_count = 0
                        
                        for i, (_, row) in enumerate(cluster_customers.iterrows()):
                            try:
                                send_email(
                                    customer_name=row['이름'],
                                    customer_email=row['이메일'],
                                    message=email_content,
                                    cluster=selected_cluster,
                                    marketing_strategies=marketing_strategies
                                )
                                success_count += 1
                            except Exception as e:
                                st.error(f"{row['이름']} 고객에게 이메일 발송 실패: {str(e)}")
                                fail_count += 1
                            
                            progress = (i + 1) / len(cluster_customers)
                            progress_bar.progress(progress)
                            status_text.text(f"진행 중: {i + 1}/{len(cluster_customers)} (성공: {success_count}, 실패: {fail_count})")
                        
                        progress_bar.empty()
                        if fail_count == 0:
                            st.success(f"모든 이메일({success_count}건)이 성공적으로 발송되었습니다!")
                        else:
                            st.warning(f"이메일 발송 완료 (성공: {success_count}건, 실패: {fail_count}건)")
                        
        else:
            st.error(f"CSV 파일을 찾을 수 없습니다: {csv_path}")