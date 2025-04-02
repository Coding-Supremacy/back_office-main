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

def send_email(customer_name, customer_email, message):
    # SMTP 서버 설정
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    EMAIL_ADDRESS = "vhzkflfltm6@gmail.com"
    EMAIL_PASSWORD = "cnvc dpea ldyv pfgq" 
    
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = customer_email
    msg['Subject'] = f"{customer_name}님, 프로모션 안내"

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



def run_eda():
    brand = st.session_state.get("brand", "현대")  # 기본값은 현대
    country = st.session_state.get("country", "")

    # 분석 종류 선택 메뉴
    selected_analysis = option_menu(
        menu_title=None,
        options=[
            "👥 클러스터별 성별 분포",
            "💰 클러스터별 거래 금액",
            "🛒 클러스터별 구매 빈도",
            "🚘 모델별 구매 분석"
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

    pastel_colors = pc.qualitative.Pastel
    csv_path = f"data/{brand}_고객데이터_신규입력용.csv"


    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        
        # 국가 필터링
        country_df = df[df['국가'] == country]
        
        if selected_analysis == "👥 클러스터별 성별 분포":
            st.subheader(f"{country} - 클러스터별 성별 분포")
            
            if {'Cluster', '성별'}.issubset(country_df.columns):
                # 클러스터별 성별 분포 계산
                gender_dist = country_df.groupby(['Cluster', '성별']).size().reset_index(name='인원수')
                
                # 클러스터 번호에 +1을 더한 새로운 열 생성
                gender_dist['Cluster_Display'] = gender_dist['Cluster'] + 1
                
                bar_fig = px.bar(
                    gender_dist,
                    x='Cluster_Display',
                    y='인원수',
                    color='성별',
                    title=f'{country} 클러스터별 성별 분포',
                    labels={'Cluster_Display': '클러스터', '인원수': '고객 수'},
                    barmode='group',
                    color_discrete_map={'남': '#3498db', '여': '#e74c3c'}
                )
                
                bar_fig.update_layout(
                    title={'text': f'{country} 클러스터별 성별 분포', 'x': 0.5},
                    xaxis=dict(title='클러스터 유형'),
                    yaxis=dict(title='고객 수'),
                    plot_bgcolor='#f4f4f9',
                    paper_bgcolor='#ffffff'
                )
                
                st.plotly_chart(bar_fig)
                
                # 클러스터별 성별 비율 계산
                cluster_totals = gender_dist.groupby('Cluster_Display')['인원수'].sum().reset_index()
                gender_dist = gender_dist.merge(cluster_totals, on='Cluster_Display', suffixes=('', '_total'))
                gender_dist['비율'] = (gender_dist['인원수'] / gender_dist['인원수_total'] * 100).round(1)
                
                # 비율 표시
                st.subheader("클러스터별 성별 비율")
                pivot_df = gender_dist.pivot(index='Cluster_Display', columns='성별', values='비율').fillna(0)
                st.dataframe(pivot_df.style.format("{:.1f}%").background_gradient(cmap='Blues'))
                
                # 인사이트 제공
                st.markdown("""
                **분석 인사이트:**
                - 각 클러스터의 성별 분포를 확인하여 타겟 마케팅 전략 수립
                - 특정 성별이 집중된 클러스터는 성별에 맞는 맞춤형 프로모션 가능
                - 성별 균형이 잘 맞는 클러스터는 일반적인 마케팅 접근 가능
                """)
                
            else:
                st.error("필요한 컬럼이 데이터에 없습니다.")

        elif selected_analysis == "💰 클러스터별 거래 금액":
            st.subheader(f"{country} - 클러스터별 거래 금액 분석")
            
            if {'Cluster', '거래 금액'}.issubset(country_df.columns):
                # 클러스터 번호에 +1을 더한 새로운 열 생성
                country_df['Cluster_Display'] = country_df['Cluster'] + 1
                
                # 박스플롯 생성
                box_fig = px.box(
                    country_df,
                    x='Cluster_Display',
                    y='거래 금액',
                    title=f'{country} 클러스터별 거래 금액 분포',
                    labels={'Cluster_Display': '클러스터', '거래 금액': '거래 금액'},
                    color='Cluster_Display',
                    color_discrete_sequence=pastel_colors
                )
                
                box_fig.update_layout(
                    title={'text': f'{country} 클러스터별 거래 금액 분포', 'x': 0.5},
                    xaxis=dict(title='클러스터 유형'),
                    yaxis=dict(title='거래 금액'),
                    plot_bgcolor='#f4f4f9',
                    paper_bgcolor='#ffffff',
                    showlegend=False
                )
                
                st.plotly_chart(box_fig)
                
                # 클러스터별 평균 거래 금액 계산
                avg_transaction = country_df.groupby('Cluster_Display')['거래 금액'].mean().reset_index()
                avg_transaction['거래 금액'] = avg_transaction['거래 금액'].round()
                
                # 평균 거래 금액 표시
                st.subheader("클러스터별 평균 거래 금액")
                st.dataframe(avg_transaction.style.format({"거래 금액": "{:,.0f}원"}).background_gradient(subset=['거래 금액'], cmap='Greens'))
                
                # 인사이트 제공
                st.markdown("""
                **분석 인사이트:**
                - 고액 거래 클러스터: 프리미엄 서비스, VIP 혜택 제공
                - 중간 거래 클러스터: 업셀링 기회 탐색, 추가 구매 유도
                - 저액 거래 클러스터: 진입 장벽 낮은 제품 추천, 할인 프로모션
                """)
                
            else:
                st.error("필요한 컬럼이 데이터에 없습니다.")

        elif selected_analysis == "🛒 클러스터별 구매 빈도":
            st.subheader(f"{country} - 클러스터별 구매 빈도 분석")
            
            if {'Cluster', '제품구매빈도'}.issubset(country_df.columns):
                # 클러스터 번호에 +1을 더한 새로운 열 생성
                country_df['Cluster_Display'] = country_df['Cluster'] + 1
                
                # 박스플롯 생성
                box_fig = px.box(
                    country_df,
                    x='Cluster_Display',
                    y='제품구매빈도',
                    title=f'{country} 클러스터별 구매 빈도 분포',
                    labels={'Cluster_Display': '클러스터', '제품구매빈도': '구매 빈도'},
                    color='Cluster_Display',
                    color_discrete_sequence=pastel_colors
                )
                
                box_fig.update_layout(
                    title={'text': f'{country} 클러스터별 구매 빈도 분포', 'x': 0.5},
                    xaxis=dict(title='클러스터 유형'),
                    yaxis=dict(title='구매 빈도'),
                    plot_bgcolor='#f4f4f9',
                    paper_bgcolor='#ffffff',
                    showlegend=False
                )
                
                st.plotly_chart(box_fig)
                
                # 클러스터별 평균 구매 빈도 계산
                avg_frequency = country_df.groupby('Cluster_Display')['제품구매빈도'].mean().reset_index()
                avg_frequency['제품구매빈도'] = avg_frequency['제품구매빈도'].round(2)
                
                # 평균 구매 빈도 표시
                st.subheader("클러스터별 평균 구매 빈도")
                st.dataframe(avg_frequency.style.format({"제품구매빈도": "{:.2f}회"}).background_gradient(subset=['제품구매빈도'], cmap='Oranges'))
                
                # 인사이트 제공
                st.markdown("""
                **분석 인사이트:**
                - 고빈도 구매 클러스터: 충성도 프로그램 강화, 정기 구매 혜택 제공
                - 중간 빈도 클러스터: 구매 주기 단축을 위한 리마인드 마케팅
                - 저빈도 클러스터: 재구매 유도 프로모션, 첫 구매 고객 대상 혜택
                """)
                
            else:
                st.error("필요한 컬럼이 데이터에 없습니다.")

        elif selected_analysis == "🚘 모델별 구매 분석":
            st.subheader(f"{country} - 모델별 구매 분석")
            
            if {'구매한제품', 'Cluster'}.issubset(country_df.columns):
                # 모델별 판매량 계산
                model_sales = country_df['구매한제품'].value_counts().reset_index()
                model_sales.columns = ['모델', '판매량']
                
                # 바 차트 생성
                bar_fig = px.bar(
                    model_sales,
                    x='모델',
                    y='판매량',
                    title=f'{country} 모델별 판매량',
                    labels={'모델': '차량 모델', '판매량': '판매량'},
                    color='모델',
                    color_discrete_sequence=pastel_colors
                )
                
                bar_fig.update_layout(
                    title={'text': f'{country} 모델별 판매량', 'x': 0.5},
                    xaxis=dict(title='차량 모델', tickangle=45),
                    yaxis=dict(title='판매량'),
                    plot_bgcolor='#f4f4f9',
                    paper_bgcolor='#ffffff',
                    showlegend=False
                )
                
                st.plotly_chart(bar_fig)
                
                # 모델 선택
                selected_model = st.selectbox(
                    "모델 선택",
                    country_df['구매한제품'].unique(),
                    key='model_select'
                )
                
                # 선택된 모델의 클러스터 분포 계산
                model_cluster = country_df[country_df['구매한제품'] == selected_model]['Cluster'].value_counts().reset_index()
                model_cluster.columns = ['Cluster', '고객 수']
                model_cluster['Cluster'] = model_cluster['Cluster'] + 1
                
                # 파이 차트 생성
                pie_fig = px.pie(
                    model_cluster,
                    names='Cluster',
                    values='고객 수',
                    title=f'{selected_model} 모델 구매 고객의 클러스터 분포',
                    color_discrete_sequence=pastel_colors
                )
                
                st.plotly_chart(pie_fig)
                
                # 모델별 클러스터 분포 표시
                st.subheader(f"{selected_model} 모델 구매 고객 클러스터 분포")
                st.dataframe(model_cluster.style.format({"고객 수": "{:,}명"}).background_gradient(subset=['고객 수'], cmap='Purples'))
                
                # 인사이트 제공
                st.markdown(f"""
                **{selected_model} 모델 분석 인사이트:**
                - 주 구매 클러스터: {model_cluster.iloc[0]['Cluster']}번 유형 ({model_cluster.iloc[0]['고객 수']}명)
                - 타겟 마케팅: 해당 클러스터 특성에 맞는 프로모션 개발
                - 잠재 고객: 다른 클러스터로의 판매 확장 가능성 탐색
                """)
                
            else:
                st.error("필요한 컬럼이 데이터에 없습니다.")
                
    else:
        st.error(f"CSV 파일을 찾을 수 없습니다: {csv_path}")
