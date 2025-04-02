import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
import numpy as np
import platform
from matplotlib import font_manager, rc
import io
import random
from bs4 import BeautifulSoup
import plotly.express as px
from fpdf import FPDF
from datetime import datetime
import base64
import os
import tempfile
import shutil



# 폰트 설정
plt.rcParams['axes.unicode_minus'] = False

if platform.system() == 'Darwin':
    rc('font', family='AppleGothic')
elif platform.system() == 'Windows':
    path = "c:/Windows/Fonts/malgun.ttf"
    font_name = font_manager.FontProperties(fname=path).get_name()
    rc('font', family=font_name)
else:
    print('Unknown system... sorry~~~~')

@st.cache_data
def fontRegistered():
    font_dirs = [os.getcwd() + '../custom_fonts']
    font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
    for font_file in font_files:
        font_manager.fontManager.addfont(font_file)
    font_manager._load_fontmanager(try_read_cache=False)



@st.cache_data
def load_data():
    # 현재 파일(trend.py)의 위치를 기준으로 상대 경로 생성
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 현재 파일이 있는 디렉토리
    data_path = os.path.join(BASE_DIR, 'data_mini2/', '수출 주요 국가 차량 판매량 순위_정리 완료2.csv')
    
    # 파일 존재 여부 확인
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"데이터 파일을 찾을 수 없습니다: {data_path}")
    
    return pd.read_csv(data_path, encoding='utf-8')

data = load_data()

# 대륙별 국가 매핑
continent_mapping = {
    'Asia': ['China', 'India', 'Japan', 'South Korea', 'Thailand'],
    'Europe': ['Germany', 'France', 'UK', 'Italy', 'Spain'],
    'Africa': ['South Africa', 'Egypt', 'Nigeria', 'Morocco', 'Algeria'],
    'North America': ['USA', 'Canada', 'Mexico'],
    'South America': ['Brazil', 'Argentina', 'Chile', 'Colombia', 'Peru'],
    'Oceania': ['Australia', 'New Zealand', 'Fiji']
}

# HTML 태그 제거 함수
def clean_html(text):
    if not text:
        return ""
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text()

# 네이버 뉴스 API 함수
def fetch_news(query):
    client_id = st.secrets["X-Naver-Client-Id"]
    client_secret = st.secrets["X-Naver-Client-Secret"]
    url = "https://openapi.naver.com/v1/search/news.json"
    
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }
    params = {
        "query": query,
        "display": 5,
        "start": 1,
        "sort": "date"
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"뉴스를 가져오는 중 오류가 발생했습니다: {e}")
        return None

# 브랜드별 경쟁 전략 매핑
def get_brand_strategy(target_brand):
    brand_strategies = {
        "Toyota": {
            "color": "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)",
            "전략": [
                "✅ 신뢰성 이미지 대비 가격 경쟁력 강조",
                "✅ 하이브리드 기술 비교 광고 집행",
                "✅ 5년 무상 정비 프로모션"
            ],
            "주력_모델": ["RAV4", "Corolla", "Hilux"]
        },
        "Volkswagen": {
            "color": "linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%)",
            "전략": [
                "✅ 유럽풍 디자인 대비 현지화 사양 강조",
                "✅ 전기차 크로스오버 모델 집중 홍보",
                "✅ 디젤 게이트 이후 신뢰성 회복 캠페인"
            ],
            "주력_모델": ["Golf", "Tiguan", "ID.4"]
        }
    }
    return brand_strategies.get(target_brand, {
        "color": "linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%)",
        "전략": [
            f"✅ {target_brand} 강점 분석 후 차별화 전략",
            "✅ 현지 소비자 선호도 조사 실시",
            "✅ 경쟁사 대비 비교표 제공"
        ],
        "주력_모델": ["N/A"]
    })

# 모델별 경쟁 차량 및 전략 매핑
def get_competitive_strategy(target_model):
    hyundai_models = ["아반떼", "코나", "투싼", "싼타페", "그랜저", 
                     "아이오닉 5", "넥쏘", "포터", "캐스퍼", "스타리아"]
    kia_models = ["K5", "K8", "셀토스", "스포티지", "쏘렌토", 
                 "EV6", "니로", "모하비", "레이", "카니발"]
    
    competitive_models = {
        "Toyota Hilux": {
            "color": "linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%)",
            "현대차": ["싼타크루즈", "포터", "넥쏘"],
            "기아차": ["바이론", "모하비", "EV9"],
            "전략": [
                "✅ 디젤 엔진 성능 강조",
                "✅ 현지 오프로드 테스트 영상",
                "✅ 건설/농업용 패키지 할인"
            ]
        },
        "Tesla Model Y": {
            "color": "linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)",
            "현대차": ["아이오닉 5", "코나 일렉트릭", "넥쏘"],
            "기아차": ["EV6", "니로 EV", "EV9"],
            "전략": [
                "✅ 초고속 충전 인프라 강조",
                "✅ 7년 무상 배터리 보증",
                "✅ 전기차 보조금 최적화"
            ]
        }
    }
    
    if target_model in competitive_models:
        return competitive_models[target_model]
    
    return {
        "color": "linear-gradient(135deg, #d4fc79 0%, #96e6a1 100%)",
        "현대차": random.sample(hyundai_models, 3),
        "기아차": random.sample(kia_models, 3),
        "전략": [
            f"✅ 현대차 {random.choice(['가격', '디자인', '연비', '안전'])} 경쟁력",
            f"✅ 기아차 {random.choice(['기술', '편의사양', '공간성', '디자인'])} 우위",
            "✅ 지역 맞춤형 프로모션"
        ]
    }

# 공통 뉴스 쿼리 생성 함수
def get_news_query(region, column=None, value=None):
    if region in continent_mapping:
        base_query = region + " 자동차 수출 시장"
    else:
        for continent, countries in continent_mapping.items():
            if region in countries:
                base_query = continent + " 자동차 수출 시장"
                break
        else:
            base_query = region + " 자동차 수출 시장"
    
    if column == '파워트레인' and value:
        return f"{region} {value} 자동차 수출"
    return base_query

def create_pdf_report(selected_region, selected_year, selected_column, analysis_data):
    class KoreanPDF(FPDF):
        def __init__(self):
            super().__init__()
            
            
            try:
                # 원본 폰트 경로 (Streamlit Cloud 배포 경로)
                FONT_PATH_ORIG = "main_project/project_2/fonts/NanumGothic.ttf"
                TEMP_FONT_PATH = os.path.join(tempfile.gettempdir(), "NanumGothic.ttf")
                
                # 임시 폴더에 폰트 복사 (권한 문제 해결)
                if os.path.exists(FONT_PATH_ORIG):
                    shutil.copyfile(FONT_PATH_ORIG, TEMP_FONT_PATH)
                    
                    # 폰트 등록
                    self.add_font("NanumGothic", "", TEMP_FONT_PATH, uni=True)
                    self.add_font("NanumGothic", "B", TEMP_FONT_PATH, uni=True)
                    self.title_font = "NanumGothic"
                    print(f"폰트 로드 성공: {TEMP_FONT_PATH}")
                else:
                    print(f"⚠️ 원본 폰트 없음: {FONT_PATH_ORIG}")
            except Exception as e:
                print(f"❌ 폰트 로드 실패: {str(e)}")

    pdf = KoreanPDF()
    pdf.add_page()
    
    # 폰트 설정 (나눔고딕 -> 실패 시 기본 폰트)
    try:
        pdf.set_font("NanumGothic", "B", 24)
    except:
        try:
            pdf.set_font("Malgun", "B", 24)
        except:
            pdf.set_font("helvetica", "B", 24)
    
    # 제목 페이지 디자인
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 40, txt="현대기아차 글로벌 시장 분석 리포트", ln=1, align='C')
    
    pdf.set_font(pdf.title_font, "", 16)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 20, txt=f"대상 지역: {selected_region}", ln=1, align='C')
    pdf.cell(0, 10, txt=f"분석 연도: {selected_year}", ln=1, align='C')
    pdf.cell(0, 20, txt=f"분석 기준: {selected_column}", ln=1, align='C')
    
    # 회사 로고 추가 (예시)
    try:
        pdf.image("hyundai_kia_logo.png", x=80, y=pdf.get_y(), w=50)
    except:
        pass
    
    pdf.add_page()
    
    # 1. 분석 개요 섹션 - 대륙 찾기 로직 수정
    pdf.set_font(pdf.title_font, "B", 18)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, txt="1. 분석 개요", ln=1)
    pdf.set_font(pdf.title_font, "", 12)
    pdf.set_text_color(0, 0, 0)
    
    # 대륙 찾기 (에러 처리 강화)
    continent = None
    for k, v in continent_mapping.items():
        if selected_region in v:
            continent = k
            break
    
    if continent:
        region_type = "대륙"
        overview_text = f"""
        본 리포트는 {continent} {region_type}의 주요 자동차 시장 중 {selected_region}에서의 
        현대기아차 경쟁 현황을 {selected_column} 기준으로 분석한 자료입니다.
        """
    else:
        overview_text = f"""
        본 리포트는 {selected_region} 지역에서의 현대기아차 경쟁 현황을 
        {selected_column} 기준으로 분석한 자료입니다.
        """
    
    overview_text += f"""
    
    {selected_year}년 기준 현대기아차의 시장 점유율, 경쟁사 대비 강점/약점, 
    현지 시장 특성에 기반한 전략적 제안을 포함하고 있습니다.
    
    분석 대상: {selected_region} 시장에서 판매된 모든 차량
    데이터 기준: {selected_year}년 전체 판매 데이터
    """
    
    pdf.multi_cell(0, 10, txt=overview_text)
    pdf.ln(10)
    
    # 2. 시장 현황 분석 섹션 (더 전문적인 내용)
    pdf.set_font(pdf.title_font, "B", 18)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, txt="2. 시장 현황 분석", ln=1)
    pdf.set_font(pdf.title_font, "", 12)
    pdf.set_text_color(0, 0, 0)
    
    if selected_column == '브랜드':
        top_brands = analysis_data.nlargest(5, '판매량')
        pdf.multi_cell(0, 10, txt=f"{selected_region} 시장 Top 5 브랜드 현황:")
        pdf.ln(5)
        
        # 표 생성
        col_widths = [60, 40, 40, 50]
        pdf.set_font(pdf.title_font, "B", 12)
        pdf.cell(col_widths[0], 10, txt="브랜드", border=1)
        pdf.cell(col_widths[1], 10, txt="판매량", border=1)
        pdf.cell(col_widths[2], 10, txt="점유율", border=1)
        pdf.cell(col_widths[3], 10, txt="전년대비", border=1)
        pdf.ln()
        
        pdf.set_font(pdf.title_font, "", 12)
        for idx, row in top_brands.iterrows():
            # 전년도 데이터 비교 (간단한 예시)
            prev_year = int(selected_year) - 1
            prev_data = data[(data['국가명'] == selected_region) & 
                           (data['연도'] == prev_year) &
                           (data['브랜드'] == row['브랜드'])]
            prev_sales = prev_data['판매량'].sum() if not prev_data.empty else 0
            change = ((row['판매량'] - prev_sales) / prev_sales * 100) if prev_sales > 0 else 100
            
            pdf.cell(col_widths[0], 10, txt=row['브랜드'], border=1)
            pdf.cell(col_widths[1], 10, txt=f"{row['판매량']:,}대", border=1)
            pdf.cell(col_widths[2], 10, txt=f"{row['판매량']/analysis_data['판매량'].sum()*100:.1f}%", border=1)
            pdf.cell(col_widths[3], 10, txt=f"{change:+.1f}%", border=1)
            pdf.ln()
            
    elif selected_column == '모델명':
        top_models = analysis_data.nlargest(5, '판매량')
        pdf.multi_cell(0, 10, txt=f"{selected_region} 시장 인기 모델 Top 5:")
        pdf.ln(5)
        
        # 표 생성
        col_widths = [60, 40, 40, 50]
        pdf.set_font(pdf.title_font, "B", 12)
        pdf.cell(col_widths[0], 10, txt="모델명", border=1)
        pdf.cell(col_widths[1], 10, txt="판매량", border=1)
        pdf.cell(col_widths[2], 10, txt="점유율", border=1)
        pdf.cell(col_widths[3], 10, txt="브랜드", border=1)
        pdf.ln()
        
        pdf.set_font(pdf.title_font, "", 12)
        for idx, row in top_models.iterrows():
            brand = region_year_data[region_year_data['모델명'] == row['모델명']]['브랜드'].values[0]
            
            pdf.cell(col_widths[0], 10, txt=row['모델명'], border=1)
            pdf.cell(col_widths[1], 10, txt=f"{row['판매량']:,}대", border=1)
            pdf.cell(col_widths[2], 10, txt=f"{row['판매량']/analysis_data['판매량'].sum()*100:.1f}%", border=1)
            pdf.cell(col_widths[3], 10, txt=brand, border=1)
            pdf.ln()
            
    elif selected_column == '파워트레인':
        top_powertrains = analysis_data.nlargest(5, '판매량')
        pdf.multi_cell(0, 10, txt=f"{selected_region} 시장 파워트레인별 판매 현황:")
        pdf.ln(5)
        
        # 표 생성
        col_widths = [60, 50, 40, 50]
        pdf.set_font(pdf.title_font, "B", 12)
        pdf.cell(col_widths[0], 10, txt="파워트레인", border=1)
        pdf.cell(col_widths[1], 10, txt="판매량", border=1)
        pdf.cell(col_widths[2], 10, txt="점유율", border=1)
        pdf.cell(col_widths[3], 10, txt="추세", border=1)
        pdf.ln()
        
        pdf.set_font(pdf.title_font, "", 12)
        for idx, row in top_powertrains.iterrows():
            # 간단한 추세 분석 (예시)
            if row['파워트레인'] == '전기':
                trend = "급증 ▲▲"
            elif row['파워트레인'] == '하이브리드':
                trend = "증가 ▲"
            elif row['파워트레인'] == '디젤':
                trend = "감소 ▼"
            else:
                trend = "안정적 -"
            
            pdf.cell(col_widths[0], 10, txt=row['파워트레인'], border=1)
            pdf.cell(col_widths[1], 10, txt=f"{row['판매량']:,}대", border=1)
            pdf.cell(col_widths[2], 10, txt=f"{row['판매량']/analysis_data['판매량'].sum()*100:.1f}%", border=1)
            pdf.cell(col_widths[3], 10, txt=trend, border=1)
            pdf.ln()
    
    pdf.ln(10)
    
    # 3. 경쟁 분석 섹션 (더 전문적인 내용)
    pdf.set_font(pdf.title_font, "B", 18)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, txt="3. 경쟁 분석", ln=1)
    pdf.set_font(pdf.title_font, "", 12)
    pdf.set_text_color(0, 0, 0)
    
    if selected_column == '브랜드':
        top_brand = analysis_data.loc[analysis_data['판매량'].idxmax()]
        strategy = get_brand_strategy(top_brand['브랜드'])
        
        pdf.multi_cell(0, 10, txt=f"1위 브랜드: {top_brand['브랜드']} ({top_brand['판매량']:,}대, 점유율 {top_brand['판매량']/analysis_data['판매량'].sum()*100:.1f}%)")
        pdf.ln(5)
        
        pdf.multi_cell(0, 10, txt=f"현대기아차 대비 {top_brand['브랜드']}의 주요 강점:")
        for tactic in strategy['전략']:
            pdf.cell(10)
            pdf.multi_cell(0, 10, txt=f"• {tactic.replace('✅', '').strip()}")
        
    elif selected_column == '모델명':
        top_model = analysis_data.loc[analysis_data['판매량'].idxmax()]
        strategy = get_competitive_strategy(top_model['모델명'])
        
        pdf.multi_cell(0, 10, txt=f"1위 모델: {top_model['모델명']} ({top_model['판매량']:,}대, 점유율 {top_model['판매량']/analysis_data['판매량'].sum()*100:.1f}%)")
        pdf.ln(5)
        
        pdf.multi_cell(0, 10, txt=f"경쟁 모델 {top_model['모델명']}에 대한 대응 전략:")
        for tactic in strategy['전략']:
            pdf.cell(10)
            pdf.multi_cell(0, 10, txt=f"• {tactic.replace('✅', '').strip()}")
        
    elif selected_column == '파워트레인':
        top_powertrain = analysis_data.loc[analysis_data['판매량'].idxmax()]
        
        pdf.multi_cell(0, 10, txt=f"가장 인기 있는 파워트레인: {top_powertrain['파워트레인']} ({top_powertrain['판매량']:,}대, 점유율 {top_powertrain['판매량']/analysis_data['판매량'].sum()*100:.1f}%)")
        pdf.ln(5)
        
        if top_powertrain['파워트레인'] == '전기':
            pdf.multi_cell(0, 10, txt="전기차 시장 전망:")
            pdf.multi_cell(0, 10, txt="• 글로벌 친환경 차량 수요 증가에 따른 성장 지속 전망")
            pdf.multi_cell(0, 10, txt="• 충전 인프라 확충이 시장 확대의 핵심 요인")
        elif top_powertrain['파워트레인'] == '하이브리드':
            pdf.multi_cell(0, 10, txt="하이브리드 시장 전망:")
            pdf.multi_cell(0, 10, txt="• 전기차 전환기 과도기 기술로 지속적 수요 예상")
            pdf.multi_cell(0, 10, txt="• 도심형 차량 중심으로 선호도 유지")
    
    pdf.ln(10)
    
    # 4. 전략 제안 섹션 (더 실무적인 내용)
    pdf.set_font(pdf.title_font, "B", 18)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, txt="4. 전략적 제안", ln=1)
    pdf.set_font(pdf.title_font, "", 12)
    pdf.set_text_color(0, 0, 0)
    
    recommendations = {
        "가격 전략": [
            f"{selected_region} 시장 소득 수준에 맞춘 가격 조정",
            "경쟁사 대비 가격 경쟁력 강화 패키지 제공",
            "할부/리스 옵션 다양화"
        ],
        "마케팅 전략": [
            "현지 문화에 맞는 광고 캠페인 개발",
            "디지털 플랫폼을 통한 타겟 마케팅 강화",
            "인플루언서/유튜버 협업 확대"
        ],
        "제품 전략": [
            "현지 도로 사양/기후에 맞춘 사양 조정",
            "인기 옵션 패키지 재구성",
            "경쟁사 대비 차별화된 기술 강조"
        ],
        "서비스 전략": [
            "A/S 네트워크 확충 및 서비스 품질 향상",
            "보증 기간 연장 또는 특별 멤버십 제공",
            "24시간 긴급 출동 서비스 도입"
        ]
    }
    
    for category, items in recommendations.items():
        pdf.set_font(pdf.title_font, "B", 14)
        pdf.cell(0, 10, txt=category, ln=1)
        pdf.set_font(pdf.title_font, "", 12)
        for item in items:
            pdf.cell(10)
            pdf.multi_cell(0, 10, txt=f"• {item}")
        pdf.ln(3)
    
    # 리포트 푸터
    pdf.set_font(pdf.title_font, "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, txt=f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=1, align='C')
    pdf.cell(0, 10, txt="© 2023 현대기아차 글로벌 전략팀. All Rights Reserved.", ln=1, align='C')
    
    # UTF-8 인코딩으로 출력
    try:
        return pdf.output(dest='S').encode('latin-1')
    except Exception as e:
        st.error(f"PDF 생성 오류: {str(e)}")
        return None

# 차트 생성 함수
def create_plotly_chart(data, x_col, y_col, title, color_sequence=None):
    if color_sequence is None:
        color_sequence = px.colors.qualitative.Pastel
        
    fig = px.bar(data, x=x_col, y=y_col, 
                title=title,
                color=x_col,
                color_discrete_sequence=color_sequence,
                text=y_col)
    
    fig.update_traces(texttemplate='%{text:,}', textposition='outside')
    fig.update_layout(
        showlegend=False,
        font=dict(size=18),
        title=dict(font=dict(size=24)),
        xaxis_title=dict(font=dict(size=20)),
        yaxis_title=dict(font=dict(size=16)),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=60, b=20),
        hovermode="x unified"
    )
    fig.update_yaxes(title_text="판매량")
    fig.update_xaxes(tickangle=45 if len(data) > 5 else 0, tickfont=dict(size=20))
    return fig

def run_trend():

    # --------------------------------------
    # UI 시작
    st.header("🚗 현대기아차 글로벌 수출 분석 대시보드")

    # 필터 컨테이너
    filter_container = st.container()
    with filter_container:
        cols = st.columns(4)  # 리포트 버튼을 위해 4열로 변경
        with cols[0]:
            selected_region = st.selectbox('지역 선택', data['국가명'].unique())
        with cols[1]:
            selected_year = st.selectbox('연도 선택', data['연도'].unique())
        with cols[2]:
            selected_column = st.selectbox('분석 기준', ['브랜드', '모델명', '파워트레인'])
        with cols[3]:
            st.markdown("<br>", unsafe_allow_html=True)
            generate_report = st.button("📄 분석 리포트 생성")

    # 데이터 필터링
    region_year_data = data[(data['국가명'] == selected_region) & (data['연도'] == selected_year)]

    # 리포트 생성 처리
    if generate_report:
        if region_year_data.empty:
            st.warning("리포트를 생성할 데이터가 없습니다. 다른 필터를 선택해 주세요.")
        else:
            with st.spinner("리포트 생성 중..."):
                if selected_column == '브랜드':
                    analysis_data = region_year_data.groupby('브랜드')['판매량'].sum().reset_index()
                elif selected_column == '모델명':
                    analysis_data = region_year_data.groupby('모델명')['판매량'].sum().reset_index()
                elif selected_column == '파워트레인':
                    analysis_data = region_year_data.groupby('파워트레인')['판매량'].sum().reset_index()
                
                pdf = create_pdf_report(selected_region, selected_year, selected_column, analysis_data)
                
                
                
                b64 = base64.b64encode(pdf).decode()
                href = f'<a href="data:application/octet-stream;base64,{b64}" download="현대기아차_{selected_region}_수출분석.pdf">📥 리포트 다운로드</a>'
                st.markdown(href, unsafe_allow_html=True)
                st.success("리포트 생성이 완료되었습니다. 위 링크를 클릭하여 다운로드하세요.")

    # 메인 컨텐츠
    st.title(f"{selected_region} 지역 {selected_year}년 {selected_column}별 분석")

    if selected_column == '브랜드':
        brand_sales = region_year_data.groupby('브랜드')['판매량'].sum().reset_index()
        
        if brand_sales.empty:
            st.warning("해당 지역과 연도에 데이터가 없습니다.")
        else:
            # 판매량 차트
            fig = create_plotly_chart(brand_sales, '브랜드', '판매량', 
                                    f"{selected_region} 지역 브랜드별 판매량")
            st.plotly_chart(fig, use_container_width=True)
            
            # 브랜드 전략 섹션
            st.subheader("📊 브랜드 경쟁 분석")
            top_brand = brand_sales.loc[brand_sales['판매량'].idxmax()]
            strategy = get_brand_strategy(top_brand['브랜드'])
            
            with st.container():
                cols = st.columns([1, 3])
                with cols[0]:
                    st.metric("🏆 최다 판매 브랜드", top_brand['브랜드'])
                with cols[1]:
                    st.metric("📈 판매량", f"{top_brand['판매량']:,}대")
            
            # 브랜드 전략 카드
            with st.expander(f"🌟 {top_brand['브랜드']} 대응 전략", expanded=True):
                st.markdown(f"""
                <div style="
                    background: {strategy['color']};
                    padding: 20px;
                    border-radius: 15px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                    margin: 10px 0;
                ">
                    <h3 style="color: #2c3e50; margin-top: 0;">{top_brand['브랜드']} 경쟁 전략</h3>
                    <ul style="color: #34495e;">
                        {''.join([f'<li>{tactic}</li>' for tactic in strategy['전략']])}
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("#### 🛠️ 세부 실행 계획")
                cols = st.columns(2)
                with cols[0]:
                    st.info("**현대차 추천 모델**\n\n" + "\n".join([f"- {m}" for m in get_competitive_strategy(strategy["주력_모델"][0])["현대차"]]))
                with cols[1]:
                    st.success("**기아차 추천 모델**\n\n" + "\n".join([f"- {m}" for m in get_competitive_strategy(strategy["주력_모델"][0])["기아차"]]))

            # 뉴스 섹션
            st.markdown("---")
            st.subheader("📰 관련 최신 뉴스")
            query = get_news_query(selected_region)
            news_data = fetch_news(query)
            
            if news_data and 'items' in news_data:
                cols = st.columns(2)
                for i, item in enumerate(news_data['items'][:2]):
                    with cols[i]:
                        st.markdown(f"""
                        <a href="{item['link']}" target="_blank" style="text-decoration: none;">
                            <div style="
                                background: linear-gradient(135deg, #fdfcfb 0%, #e2d1c3 100%);
                                padding: 15px;
                                border-radius: 12px;
                                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                                margin: 10px 0;
                                height: 150px;
                                overflow: hidden;
                                transition: transform 0.3s ease;
                                cursor: pointer;
                            ">
                                <h4 style="color: #2c3e50; margin-top: 0;">{clean_html(item['title'])[:50]}...</h4>
                                <p style="color: #7f8c8d;">{clean_html(item['description'])[:100]}...</p>
                                <div style="color: #3498db; text-decoration: none;">더보기 →</div>
                            </div>
                        </a>
                        """, unsafe_allow_html=True)

    elif selected_column == '모델명':
        model_sales = region_year_data.groupby('모델명')['판매량'].sum().reset_index()
        
        if model_sales.empty:
            st.warning("해당 지역과 연도에 데이터가 없습니다.")
        else:
            # 판매량 차트
            fig = create_plotly_chart(model_sales, '모델명', '판매량', 
                                    f"{selected_region} 지역 모델별 판매량",
                                    px.colors.qualitative.Pastel2)
            st.plotly_chart(fig, use_container_width=True)
            
            # 모델 전략 섹션
            st.subheader("📊 모델 경쟁 분석")
            top_model = model_sales.loc[model_sales['판매량'].idxmax()]
            strategy = get_competitive_strategy(top_model['모델명'])
            
            with st.container():
                cols = st.columns([1, 3])
                with cols[0]:
                    st.metric("🏆 최다 판매 모델", top_model['모델명'])
                with cols[1]:
                    st.metric("📈 판매량", f"{top_model['판매량']:,}대")
            
            # 모델 전략 카드
            with st.expander(f"🌟 {top_model['모델명']} 대응 전략", expanded=True):
                st.markdown(f"""
                <div style="
                    background: {strategy['color']};
                    padding: 20px;
                    border-radius: 15px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                    margin: 10px 0;
                ">
                    <h3 style="color: #2c3e50; margin-top: 0;">{top_model['모델명']} 경쟁 전략</h3>
                    <div style="display: flex;">
                        <div style="flex: 1; padding-right: 15px;">
                            <h4 style="color: #2c3e50;">현대차 추천</h4>
                            <ul style="color: #34495e;">
                                {''.join([f'<li>{model}</li>' for model in strategy["현대차"]])}
                            </ul>
                        </div>
                        <div style="flex: 1;">
                            <h4 style="color: #2c3e50;">기아차 추천</h4>
                            <ul style="color: #34495e;">
                                {''.join([f'<li>{model}</li>' for model in strategy["기아차"]])}
                            </ul>
                        </div>
                    </div>
                    <h4 style="color: #2c3e50;">마케팅 전략</h4>
                    <ul style="color: #34495e;">
                        {''.join([f'<li>{tactic}</li>' for tactic in strategy["전략"]])}
                    </ul>
                </div>
                """, unsafe_allow_html=True)

            # 뉴스 섹션
            st.markdown("---")
            st.subheader("📰 관련 최신 뉴스")
            query = get_news_query(selected_region)
            news_data = fetch_news(query)
            
            if news_data and 'items' in news_data:
                cols = st.columns(2)
                for i, item in enumerate(news_data['items'][:2]):
                    with cols[i]:
                        st.markdown(f"""
                        <a href="{item['link']}" target="_blank" style="text-decoration: none;">
                            <div style="
                                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                                padding: 15px;
                                border-radius: 12px;
                                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                                margin: 10px 0;
                                height: 150px;
                                overflow: hidden;
                                cursor: pointer;
                            ">
                                <h4 style="color: #2c3e50; margin-top: 0;">{clean_html(item['title'])[:50]}...</h4>
                                <p style="color: #7f8c8d;">{clean_html(item['description'])[:100]}...</p>
                                <div style="color: #3498db; text-decoration: none;">더보기 →</div>
                            </div>
                        </a>
                        """, unsafe_allow_html=True)

    elif selected_column == '파워트레인':
        powertrain_sales = region_year_data.groupby('파워트레인')['판매량'].sum().reset_index()
        
        if powertrain_sales.empty:
            st.warning("해당 지역과 연도에 데이터가 없습니다.")
        else:
            # 판매량 차트
            fig = create_plotly_chart(powertrain_sales, '파워트레인', '판매량', 
                                    f"{selected_region} 지역 파워트레인별 판매량",
                                    px.colors.qualitative.Set3)
            st.plotly_chart(fig, use_container_width=True)
            
            # 파워트레인 전략 섹션
            st.subheader("⚡ 파워트레인 분석")
            top_powertrain = powertrain_sales.loc[powertrain_sales['판매량'].idxmax()]
            
            with st.container():
                cols = st.columns([1, 3])
                with cols[0]:
                    st.metric("🏆 최다 판매", top_powertrain['파워트레인'])
                with cols[1]:
                    st.metric("📈 판매량", f"{top_powertrain['판매량']:,}대")
            
            # 파워트레인 전략 카드
            powertrain_colors = {
                "가솔린": "linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%)",
                "디젤": "linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%)",
                "하이브리드": "linear-gradient(135deg, #d4fc79 0%, #96e6a1 100%)",
                "전기": "linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)"
            }
            
            powertrain_strategies = {
                "가솔린": [
                    "✅ ECO 모드 성능 강조",
                    "✅ 휘발유 차량 유지비 절감 프로모션",
                    "✅ 고출력 모델 마케팅 강화"
                ],
                "디젤": [
                    "✅ 토크 성능을 강조한 오프로드 테스트",
                    "✅ 상업용 차량 특별 할부 조건",
                    "✅ DPF 관리 무상 점검 이벤트"
                ],
                "하이브리드": [
                    "✅ 연비 비교 광고 집행",
                    "✅ 장기 보증 패키지 제공",
                    "✅ 환경보호 이미지 강화"
                ],
                "전기": [
                    "✅ 충전 인프라 할인 혜택",
                    "✅ 배터리 성능 보증 기간 확대",
                    "✅ 친환경 세금 감면 지원"
                ]
            }
            
            with st.expander(f"🌟 {top_powertrain['파워트레인']} 파워트레인 전략", expanded=True):
                bg_color = powertrain_colors.get(top_powertrain['파워트레인'], "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)")
                st.markdown(f"""
                <div style="
                    background: {bg_color};
                    padding: 20px;
                    border-radius: 15px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                    margin: 10px 0;
                ">
                    <h3 style="color: #2c3e50; margin-top: 0;">{top_powertrain['파워트레인']} 전략</h3>
                    <ul style="color: #34495e;">
                        {''.join([f'<li>{tactic}</li>' for tactic in powertrain_strategies.get(top_powertrain['파워트레인'], ["✅ 기술 신뢰성 홍보"])])}
                    </ul>
                </div>
                """, unsafe_allow_html=True)

            # 뉴스 섹션
            st.markdown("---")
            st.subheader("📰 관련 최신 뉴스")
            query = get_news_query(selected_region, '파워트레인', top_powertrain['파워트레인'])
            news_data = fetch_news(query)
            
            if news_data and 'items' in news_data:
                cols = st.columns(2)
                for i, item in enumerate(news_data['items'][:2]):
                    with cols[i]:
                        st.markdown(f"""
                        <a href="{item['link']}" target="_blank" style="text-decoration: none;">
                            <div style="
                                background: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%);
                                padding: 15px;
                                border-radius: 12px;
                                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                                margin: 10px 0;
                                height: 150px;
                                overflow: hidden;
                                cursor: pointer;
                            ">
                                <h4 style="color: #2c3e50; margin-top: 0;">{clean_html(item['title'])[:50]}...</h4>
                                <p style="color: #7f8c8d;">{clean_html(item['description'])[:100]}...</p>
                                <div style="color: #3498db; text-decoration: none;">더보기 →</div>
                            </div>
                        </a>
                        """, unsafe_allow_html=True)

    st.markdown("---") 

    # 세션 상태 초기화
    if 'show_data' not in st.session_state:
        st.session_state.show_data = False
    if 'page' not in st.session_state:
        st.session_state.page = 1  # 기본값 1로 설정

    # 🔹 원본 데이터 보기 버튼
    if st.button('🔍 원본데이터 보기'):
        st.session_state.show_data = not st.session_state.show_data

    # 🔹 데이터 표시 영역
    if st.session_state.show_data:
        st.subheader("📁 원본 데이터")
        
        # 페이지네이션 설정
        page_size = 7
        total_pages = max(1, (len(data) // page_size) + (1 if len(data) % page_size else 0))
        
        # 페이지 이동 버튼
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button('◀ 이전', disabled=(st.session_state.page <= 1)):
                st.session_state.page -= 1
                st.rerun()  # 변경 즉시 화면 갱신
        
        with col2:
            st.write(f"페이지 {st.session_state.page}/{total_pages}")
        
        with col3:
            if st.button('다음 ▶', disabled=(st.session_state.page >= total_pages)):
                st.session_state.page += 1
                st.rerun()  # 변경 즉시 화면 갱신
        
        # 데이터 표시
        start_idx = (st.session_state.page - 1) * page_size
        end_idx = min(start_idx + page_size, len(data))
        st.dataframe(data.iloc[start_idx:end_idx], height=300)
        
        # 데이터 요약
        with st.expander("📊 데이터 요약 정보 보기"):
            st.write(f"• 총 행 수: {len(data)}")
            st.write("• 컬럼 구조:")
            st.json({col: str(dtype) for col, dtype in data.dtypes.items()})