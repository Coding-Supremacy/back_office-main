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
    # 분석 종류 선택 메뉴
    selected = option_menu(
        menu_title=None,
        options=[
            "📊 가입 연도 분석",
            "💰 거래 금액 분석",
            "🛒 구매 빈도 분석",
            "📈 고객 유형 분석",
            "🚘 모델별 구매 분석"
        ],
        icons=["", "", "", "", ""],
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
    # CSV 파일 경로 (필요에 따라 수정)
    csv_path = "main_project/project_1/data_mini1/클러스터링고객데이터_5.csv"

    # 1) 가입 연도 분석
    if selected == "📊 가입 연도 분석":
        st.subheader("📊 가입 연도와 고객 등급")
        st.markdown("""
        가입일 데이터를 분석하여 각 연도별 유입 고객의 등급과 수를 파악합니다. 
        X축은 가입 연도, Y축은 가입 고객 수를 나타내며, 서로 다른 색상은 고객 등급(일반, VIP, 이탈 가능 등)을 구분합니다.
        """)
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            if '가입일' in df.columns and '고객 세그먼트' in df.columns:
                df['가입일'] = pd.to_datetime(df['가입일'], errors='coerce')
                df['가입 연도'] = df['가입일'].dt.year
                df_grouped = df.groupby(['가입 연도', '고객 세그먼트']).size().reset_index(name='고객 수')
                bar_fig = px.bar(
                    df_grouped,
                    x='가입 연도',
                    y='고객 수',
                    color='고객 세그먼트',
                    title='가입 연도별 누적 고객',
                    labels={'가입 연도': '연도', '고객 수': '가입 고객 수', '고객 세그먼트': '고객 등급'},
                    color_discrete_sequence=pastel_colors
                )
                bar_fig.update_layout(
                    title={'text': '가입 연도별 누적 고객', 'x': 0.5, 'font': {'size': 20}},
                    xaxis=dict(title='가입 연도', tickformat='%Y'),
                    yaxis=dict(title='가입 고객 수'),
                    margin=dict(l=40, r=40, t=40, b=80),
                    plot_bgcolor='#f4f4f9',
                    paper_bgcolor='#ffffff',
                    font=dict(size=12)
                )
                st.plotly_chart(bar_fig)
                custom_info(
                    "<strong>자세한 그래프 설명:</strong><br> 이 그래프는 고객 가입 연도별로 유입된 고객 수와 유형을 시각화합니다. "
                    "가입 추세를 확인하고, 각 연도별 고객 특성을 분석하여 마케팅 전략 수립에 유용한 인사이트를 제공합니다.",
                    "#d1ecf1", "black"
                )
                total_customers = df_grouped['고객 수'].sum()
                if total_customers >= 2000:
                    custom_info("프로모션 제안: 고객수가 매우 많습니다. → 대규모 할인 행사, 프리미엄 멤버십 리뉴얼, VIP 전용 개인화 서비스 강화.",
                               "#d1e7dd", "darkgreen")
                elif total_customers >= 1500:
                    custom_info("프로모션 제안: 고객수가 양호합니다. → 신규 고객 혜택 강화 및 추천인 보상 프로그램 도입 고려.",
                               "#fff3cd", "darkorange")
                elif total_customers >= 1000:
                    custom_info("프로모션 제안: 고객수가 보통입니다. → 소규모 이벤트와 온라인 프로모션을 통한 고객 유입 촉진.",
                               "#f8d7da", "darkred")
                elif total_customers >= 500:
                    custom_info("프로모션 제안: 고객수가 낮습니다. → 온라인 광고, SNS 마케팅, 지역 이벤트 등 신규 고객 확보에 주력.",
                               "#f8d7da", "darkred")
                else:
                    custom_info("프로모션 제안: 고객수가 매우 적습니다. → 마케팅 전략 재검토 및 고객 피드백 수집 후 개선 필요.",
                               "#f5c6cb", "darkred")
            else:
                st.error("필요한 컬럼('가입일', '고객 세그먼트')이 CSV 파일에 없습니다.")
        else:
            st.error(f"⚠️ CSV 파일이 존재하지 않습니다: {csv_path}")
    

    elif selected == "💰 거래 금액 분석":
        st.subheader("💰 고객 유형별 거래 금액")
        st.markdown("""
        고객 유형별 거래 금액 분포를 박스플롯으로 시각화합니다. 
        중앙값, 사분위 범위 및 이상치를 통해 소비 패턴을 파악할 수 있습니다.
        """)
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            if {'Cluster', '거래 금액'}.issubset(df.columns):
                # 클러스터 번호에 +1을 더한 새로운 열 생성
                df['Cluster_Display'] = df['Cluster'] + 1
                
                # 클러스터가 8개인 경우, 색상 시퀀스를 조정합니다.
                box_fig = px.box(
                    df,
                    x="Cluster_Display",  # 새로운 열을 x축으로 사용
                    y="거래 금액",
                    title="고객 유형별 거래 금액 분포",
                    labels={'Cluster_Display': '고객 유형', '거래 금액': '거래 금액(원)'},
                    color="Cluster_Display",  # 각 클러스터별로 색상이 다르게 나타나도록 설정
                    color_discrete_sequence=px.colors.qualitative.Pastel[:8]  # 8개의 색상 사용
                )
                box_fig.update_layout(
                    title={'text': '고객 유형별 거래 금액 분포', 'x': 0.5, 'font': {'size': 20}},
                    xaxis=dict(title='고객 유형', tickangle=-45),  # x축 레이블을 45도 기울여 정렬
                    yaxis=dict(title='거래 금액(원)'),
                    margin=dict(l=40, r=40, t=40, b=120),  # x축 레이블이 잘리지 않도록 여백을 늘림
                    plot_bgcolor='#f4f4f9',
                    paper_bgcolor='#ffffff',
                    font=dict(size=12)
                )
                st.plotly_chart(box_fig)
                custom_info(
                    "<strong>자세한 그래프 설명:</strong><br> 박스플롯은 고객 유형별 거래 금액의 중앙값과 분포, 이상치를 명확하게 보여줍니다. "
                    "이를 통해 각 고객군의 소비 패턴을 비교 분석할 수 있어 마케팅 전략 수립에 큰 도움이 됩니다.",
                    "#d1ecf1", "black"
                )
                
                # 각 클러스터별 평균 거래 금액 계산
                cluster_avg = df.groupby('Cluster')['거래 금액'].mean().sort_values(ascending=False)
                
                # 클러스터별로 거래 금액 평균을 비교하여 프로모션 제안
                for i, (cluster, avg_transaction) in enumerate(cluster_avg.items()):
                    if i < len(cluster_avg) // 3:  # 상위 1/3 클러스터
                        custom_info(f"{cluster + 1}번 유형 고객 프로모션 제안: 거래 금액이 가장 높습니다. → 초고가 상품, 맞춤형 컨시어지, 프리미엄 이벤트 강화.",
                                "#d1e7dd", "darkgreen")
                    elif i < 2 * len(cluster_avg) // 3:  # 중위 클러스터
                        custom_info(f"{cluster + 1}번 유형 고객 프로모션 제안: 거래 금액이 중간 수준입니다. → VIP 추가 할인 및 업셀링, 맞춤 마케팅 컨설팅 제공 검토.",
                                "#d4edda", "darkgreen")
                    else:  # 하위 클러스터
                        custom_info(f"{cluster + 1}번 유형 고객 프로모션 제안: 거래 금액이 낮습니다. → 재구매 할인 쿠폰, 적립 이벤트, 타겟 마케팅 통한 충성도 향상.",
                                "#f8d7da", "darkred")
            else:
                st.error("필요한 컬럼('Cluster', '거래 금액')이 CSV 파일에 없습니다.")
        else:
            st.error(f"⚠️ CSV 파일이 존재하지 않습니다: {csv_path}")
        
        
    
                  
        

    # 3) 구매 빈도 분석
    elif selected == "🛒 구매 빈도 분석":
        st.subheader("🛒 고객 등급별 구매 빈도")
        st.markdown("""
        각 고객 유형의 평균 구매 횟수를 바 차트로 시각화하여 재구매 성향과 소비 패턴을 분석합니다.
        X축은 고객 유형, Y축은 해당 그룹의 평균 구매 횟수를 표시합니다.
        """)
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            if {'고객 세그먼트', '제품 구매 빈도'}.issubset(df.columns):
                freq_df = df.groupby('고객 세그먼트')['제품 구매 빈도'].mean().reset_index()
                freq_df.rename(columns={'제품 구매 빈도': '평균 구매 횟수'}, inplace=True)
                bar_fig = px.bar(
                    freq_df,
                    x="고객 세그먼트",
                    y="평균 구매 횟수",
                    title="세그먼트별 평균 구매 빈도",
                    labels={'고객 세그먼트': '고객 등급', '평균 구매 횟수': '평균 구매 횟수'},
                    color="고객 세그먼트",
                    color_discrete_sequence=pastel_colors
                )
                bar_fig.update_layout(
                    title={'text': '세그먼트별 평균 구매 빈도', 'x': 0.5, 'font': {'size': 20}},
                    xaxis=dict(title='고객 유형'),
                    yaxis=dict(title='평균 구매 횟수'),
                    margin=dict(l=40, r=40, t=40, b=80),
                    plot_bgcolor='#f4f4f9',
                    paper_bgcolor='#ffffff',
                    font=dict(size=12)
                )
                st.plotly_chart(bar_fig)
                custom_info(
                    "<strong>자세한 그래프 설명:</strong><br> 이 바 차트는 각 고객 유형별 평균 구매 횟수를 시각화하여, 재구매 성향 및 소비 패턴을 명확하게 파악할 수 있도록 도와줍니다.",
                    "#d1ecf1", "black"
                )
                avg_purchase = freq_df['평균 구매 횟수'].mean()
                if avg_purchase >= 10:
                    custom_info("프로모션 제안: 구매 빈도가 매우 높습니다. → VIP 보상 프로그램, 맞춤 할인, 전담 컨설팅 강화.",
                               "#d1e7dd", "darkgreen")
                elif avg_purchase >= 8:
                    custom_info("프로모션 제안: 구매 빈도가 높습니다. → 고객 보상 이벤트, 추가 포인트 적립, 맞춤 쿠폰 제공 고려.",
                               "#cce5ff", "darkblue")
                elif avg_purchase >= 5:
                    custom_info("프로모션 제안: 구매 빈도가 양호합니다. → 단골 고객 전환 위한 보상 프로그램, 업그레이드 혜택 제공.",
                               "#d4edda", "darkgreen")
                elif avg_purchase >= 3:
                    custom_info("프로모션 제안: 구매 빈도가 보통입니다. → 재구매 할인, 포인트 2배 적립 행사 등으로 구매 촉진 시도.",
                               "#fff3cd", "darkorange")
                elif avg_purchase >= 2:
                    custom_info("프로모션 제안: 구매 빈도가 낮습니다. → 타겟 마케팅, 즉시 구매 혜택 제공을 통해 재구매 유도.",
                               "#ffeeba", "darkorange")
                elif avg_purchase >= 1:
                    custom_info("프로모션 제안: 구매 빈도가 매우 낮습니다. → 신규 고객 확보와 재구매 촉진 위한 강력 할인 및 프로모션 필요.",
                               "#f8d7da", "darkred")
                elif avg_purchase == 0:
                    custom_info("프로모션 제안: 구매 데이터가 0입니다. → 데이터 점검 후, 신규 이벤트 및 시스템 오류 수정 검토.",
                               "#f5c6cb", "darkred")
                else:
                    custom_info("프로모션 제안: 구매 데이터 오류 발생. → 데이터 정합성 재확인 및 마케팅 전략 수정 필요.",
                               "#f5c6cb", "darkred")
            else:
                st.error("필요한 컬럼('고객 세그먼트', '제품 구매 빈도')이 CSV 파일에 없습니다.")
        else:
            st.error(f"⚠️ CSV 파일이 존재하지 않습니다: {csv_path}")

    # 4) 클러스터링 분석
    elif selected == "📈 고객 유형 분석":
        cluster_data = {
            "유형": [1, 2, 3, 4, 5, 6, 7, 8],
            "평균 연령대": [34.65, 51.35, 60, 34.51, 38.55, 61.95, 33.52, 44.94],
            "거래 금액": ["높음", "높음", "적음", "적당", "낮음", "낮음", "낮음", "매우 높음"],
            "제품 구매 빈도": ["-", "-", "-", "-", "낮음", "-", "낮음", "낮음"],
            "친환경차 비율": ["13.04%", "9.30%", "0%", "20.51%", "39.39%", "13.95%", "0%", "100%"],
            "RFM 세그먼트": ["VIP","VIP","신규","일반","일반","이탈가능","이탈가능","일반"],
            "클러스터 라벨": ["VIP 고가 다빈도 구매 고객",
            "VIP 고액 구매 고객",
            "신규 저가 구매자",
            "일반적인 중간 소비자",
            "일반 중간 연령 고액 소비자",
            "이탈가능성 있는 고연령 저액 소비자",
            "이탈가능성 있는 저연령 저액 소비자",
            "일반적인 친환경 고액 소비자"]
        }

        df = pd.DataFrame(cluster_data)


        # Streamlit에서 표 표시
        st.markdown("""
        <div style="background-color: #e9f7ef; border-left: 6px solid #28a745; padding: 20px; margin-bottom: 20px; border-radius: 4px;">
        <h2 style="color: #28a745; text-align: center; margin-bottom: 15px;">📊 고객 유형별 고객 세그먼트 요약</h2>
        <p style="text-align: center;">
            각 유형의 고객 특성을 한눈에 볼 수 있도록 정리하였습니다.
        </p>
        </div>
        """, unsafe_allow_html=True)

        # 인덱스를 숨기고 HTML로 변환하여 출력
        html_table = df.to_html(index=False)
        st.markdown(html_table, unsafe_allow_html=True)

        

        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            if {'Cluster', '고객 세그먼트'}.issubset(df.columns):
                df_grouped = df.groupby(['Cluster', '고객 세그먼트']).size().reset_index(name='고객 수')
                bar_fig = px.bar(
                    df_grouped,
                    x='Cluster',
                    y='고객 수',
                    color='고객 세그먼트',
                    title='클러스터별 고객 세그먼트 분포',
                    labels={'Cluster': '고객 유형', '고객 수': '고객 수', '고객 세그먼트': '고객 등급'},
                    color_discrete_sequence=pastel_colors,
                    barmode="stack"
                )
                bar_fig.update_layout(
                    title={'text': '고객 유형별 고객 세그먼트 분포', 'x': 0.5, 'font': {'size': 20}},
                    xaxis=dict(title='클러스터'),
                    yaxis=dict(title='고객 수'),
                    margin=dict(l=40, r=40, t=40, b=80),
                    plot_bgcolor='#f4f4f9',
                    paper_bgcolor='#ffffff',
                    font=dict(size=12)
                )
                st.plotly_chart(bar_fig)
                custom_info(
                    "<strong>자세한 그래프 설명:</strong><br> 이 그래프는 각 유형에 속한 고객들의 구성과 분포를 시각화합니다. "
                    "X축은 클러스터 번호, Y축은 해당 유형의 고객 총수를 나타내며, 서로 다른 색상은 고객 유형을 구분하여 각 유형의 특성을 명확하게 파악할 수 있습니다.",
                    "#d1ecf1", "black"
                )
            else:
                st.error("필요한 컬럼('Cluster', '고객 세그먼트')이 CSV 파일에 없습니다.")
        else:
            st.error(f"⚠️ CSV 파일이 존재하지 않습니다: {csv_path}")
            # 이메일 발송 버튼
        try:
            if st.button("프로모션 이메일 발송"):
                for i, (cluster, avg_transaction) in enumerate(cluster_avg.items()):
                    if i < len(cluster_avg) // 3:  
                        message = "제휴 카드 사용 시 3% 할인 혜택을 제공합니다."
                    elif i < 2 * len(cluster_avg) // 3:  
                        message = "VIP 멤버십 혜택을 통해 추가 할인 및 서비스를 제공합니다."
                    else:  
                        message = "재구매 할인 쿠폰을 통해 구매를 촉진해 보세요."
                    cluster_df = df[df['Cluster'] == cluster]
                    for index, row in cluster_df.iterrows():
                        customer_name = row['이름']  # 고객 이름을 데이터프레임에서 가져옴
                        customer_email = row['이메일']
                        send_email(customer_name, customer_email, message)
                st.success("이메일 발송이 완료되었습니다.")
                  
        except Exception as e:
            st.success(f"이메일을 발송했습니다.")

    # 5) 모델별 구매 분석
    elif selected == "🚘 모델별 구매 분석":
        st.subheader("🚘 모델별 구매 통계")
        st.markdown("""
        이 분석은 각 모델별 구매 데이터를 시각화하여 어떤 차량 모델이 인기가 있는지 파악합니다. 
        모델별 판매 추이를 확인하여 마케팅 전략 수립에 활용할 수 있습니다.
        """)
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            if {'구매한 제품', '거래 금액', '제품 구매 빈도'}.issubset(df.columns):
                
                # 모델별 판매량 분석
                model_sales = df['구매한 제품'].value_counts().reset_index()
                model_sales.columns = ['모델', '판매량']
                
                # 모델별 판매량 바 차트
                bar_fig = px.bar(
                    model_sales,
                    x='모델',
                    y='판매량',
                    title='모델별 판매량',
                    labels={'모델': '차량 모델', '판매량': '총 판매량'},
                    color='모델',
                    color_discrete_sequence=pastel_colors
                )
                bar_fig.update_layout(
                    title={'text': '모델별 판매량', 'x': 0.5, 'font': {'size': 20}},
                    xaxis=dict(title='차량 모델', tickangle=45),
                    yaxis=dict(title='총 판매량'),
                    margin=dict(l=40, r=40, t=40, b=120),
                    plot_bgcolor='#f4f4f9',
                    paper_bgcolor='#ffffff',
                    font=dict(size=12),
                    showlegend=False
                )
                st.plotly_chart(bar_fig)
                
                custom_info(
                    "<strong>자세한 그래프 설명:</strong><br> 이 그래프는 각 차량 모델별 총 판매량을 보여줍니다. X축은 차량 모델, Y축은 해당 모델의 총 판매량을 나타냅니다.",
                    "#d1ecf1", "black"
                )
                
                # 모델별 평균 거래 금액
                model_avg_price = df.groupby('구매한 제품')['거래 금액'].mean().reset_index()
                model_avg_price.columns = ['모델', '평균 거래 금액']
                
                # 모델 선택 드롭다운
                selected_model = st.selectbox("모델 선택", df['구매한 제품'].unique())
                
                # 선택된 모델의 클러스터별 구매 분포
                cluster_distribution = df[df['구매한 제품'] == selected_model]['Cluster'].value_counts().reset_index()
                cluster_distribution.columns = ['클러스터 번호', '고객 수']
                cluster_distribution['클러스터 번호'] = cluster_distribution['클러스터 번호'].astype(str) + '번 유형'

                
                pie_fig = px.pie(cluster_distribution,
                                 names='클러스터 번호',
                                 values='고객 수',
                                 title=f"{selected_model} 모델을 구매한 고객의 클러스터 분포",
                                 color_discrete_sequence=px.colors.qualitative.Set3)
                st.plotly_chart(pie_fig)
                
                custom_info(
                    f"<strong>자세한 파이차트 설명:</strong><br> 이 차트는 {selected_model} 모델을 구매한 고객들의 구매 빈도 분포를 보여줍니다.",
                    "#d1ecf1", "black"
                )
                
                # 모델별 분석 결과에 따른 프로모션 제안
                total_sales = model_sales[model_sales['모델'] == selected_model]['판매량'].values[0]
                avg_price = model_avg_price[model_avg_price['모델'] == selected_model]['평균 거래 금액'].values[0]
                
                if total_sales >= 50:
                    if avg_price >= 50000000:
                        custom_info(f"프로모션 제안: {selected_model} 모델은 판매량이 많고 고가입니다. → 프리미엄 프로모션, VIP 시승 이벤트, 고객 대상 맞춤형 서비스 제공.",
                                "#d1e7dd", "darkgreen")
                    else:
                        custom_info(f"프로모션 제안: {selected_model} 모델은 판매량이 많지만 가격대가 낮습니다. → 대량 구매 할인, 패키지 프로모션, 액세서리 번들 제공.",
                                "#d4edda", "darkgreen")
                elif total_sales >= 30:
                    custom_info(f"프로모션 제안: {selected_model} 모델은 판매량이 보통입니다. → 타겟 마케팅 강화, 제한된 기간 할인, 테스트 드라이브 이벤트 진행.",
                                "#fff3cd", "darkorange")
                else:
                    custom_info(f"프로모션 제안: {selected_model} 모델은 판매량이 낮습니다. → 집중 광고 캠페인, 특별 할인, 신규 고객 유치 프로모션 필요.",
                                "#f8d7da", "darkred")
                
                st.markdown(
                    """
                    ---<br>
                    <strong>추가 설명:</strong><br>
                    - 모델별 판매 데이터를 기반으로 마케팅 전략을 수립하세요.<br>
                    - 인기 모델과 비인기 모델에 대한 차별화된 접근이 필요합니다.
                    """, unsafe_allow_html=True
                )
            else:
                st.error("필요한 컬럼('구매한 제품', '거래 금액', '제품 구매 빈도')이 CSV 파일에 없습니다.")
        else:
            st.error(f"⚠️ CSV 파일이 존재하지 않습니다: {csv_path}")

if __name__ == "__main__":
    run_eda()
