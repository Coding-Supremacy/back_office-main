import streamlit as st
import requests
import json
import joblib
import pandas as pd
import random
import time
import numpy as np
from typing import Tuple
from datetime import datetime
from lightgbm import LGBMRegressor
from sklearn.preprocessing import StandardScaler

# ------------------------------
# 1. 모델 및 데이터 로드
# ------------------------------
@st.cache_resource
def load_model_and_data():
    try:
        # 실제 데이터 로드 (파일 경로를 실제 환경에 맞게 수정)
        df = pd.read_csv("hoyeon/기아.csv")
        
        # 국가별 GDP 매핑 생성
        gdp_mapping = df[['국가명', 'GDP']].drop_duplicates().set_index('국가명')['GDP'].to_dict()
        
        # 월별 데이터를 long 형식으로 변환
        month_cols = [f"{i}월" for i in range(1, 13)]
        id_vars = ['국가명', '연도', '기후대', 'GDP', '차종', '차량 구분']
        df_long = pd.melt(df, id_vars=id_vars, value_vars=month_cols,
                          var_name='월', value_name='수출량')
        df_long['월'] = df_long['월'].str.replace('월', '').astype(int)
        df_long['날짜'] = pd.to_datetime(df_long['연도'].astype(str) + '-' + df_long['월'].astype(str) + '-01')
        df_long = df_long.sort_values(by=['국가명', '차종', '날짜'])
        
        # 전월 및 다음달 수출량 계산
        df_long['전월_수출량'] = df_long.groupby(['국가명', '차종'])['수출량'].shift(1)
        df_long['다음달_수출량'] = df_long.groupby(['국가명', '차종'])['수출량'].shift(-1)
        df_model = df_long.dropna(subset=['전월_수출량', '다음달_수출량']).copy()
        
        # 실제 모델 로드 (파일 경로가 올바른지 확인)
        try:
            model = joblib.load("hoyeon/lgbm_model.joblib")
            scaler = joblib.load("hoyeon/scaler.joblib")
            model_columns = joblib.load("hoyeon/model_columns.pkl")
        except Exception as load_err:
            st.warning("모델 파일 로드에 실패하여 예제 모델을 사용합니다.")
            model = LGBMRegressor()
            scaler = StandardScaler()
            model_columns = ['수출량', '전월_수출량', '연도', '월', 'GDP'] + \
                            [f"국가명_{c}" for c in df['국가명'].unique()] + \
                            [f"기후대_{c}" for c in df['기후대'].unique()] + \
                            [f"차종_{c}" for c in df['차종'].unique()] + \
                            [f"차량 구분_{c}" for c in df['차량 구분'].unique()]
        
        return model, scaler, model_columns, df, df_long, df_model, gdp_mapping
        
    except Exception as e:
        st.error(f"시스템 초기화 중 오류 발생: {str(e)}")
        st.stop()

model, scaler, model_columns, df, df_long, df_model, gdp_mapping = load_model_and_data()

# ------------------------------
# 2. 헬퍼 함수: 마케팅 메시지 생성 및 API 호출 (강화된 버전)
# ------------------------------
class MarketingMessageGenerator:
    """마케팅 메시지 생성 전문 클래스"""
    
    def __init__(self):
        self.templates = {
            "상승세": {
                "출시 홍보": [
                    "🚀 [국가]에서 급성장 중인 [차종]! 전년 대비 [증가율]% 증가로 [기후대] 시장 점유율 확대 중",
                    "📈 [국가]의 [차종] 수요 폭발! 지난해보다 [증가율]% 증가로 최적의 진출 타이밍"
                ],
                "할인 혜택 안내": [
                    "🔥 [국가] 한정! 인기 차종 [차종] 추가 할인 - 전년 대비 [증가율]% 증가로 인한 특별 프로모션",
                    "🎯 [기후대] 시장에서 [증가율]% 성장한 [차종]! 지금 구매 시 추가 혜택"
                ],
                "브랜드 인지도 향상": [
                    "🏆 [국가]에서 [증가율]% 성장한 [차종]! [기후대] 시장에서의 입증된 성공",
                    "✨ [차종]의 [국가] 진출 성공기 - 전년 대비 [증가율]% 판매 증가로 현지 시장 공략 중"
                ]
            },
            "하락세": {
                "출시 홍보": [
                    "🔄 [국가] 시장 재도전! 개선된 [차종]으로 [기후대] 소비자 마음 사로잡기",
                    "💪 [국가]의 [차종] 판매 회복 전략 - 새로운 마케팅으로 반등 준비"
                ],
                "할인 혜택 안내": [
                    "💎 [국가]에서 [차종] 특별 할인 - 판매 부진 극복을 위한 한정 기회",
                    "🛒 [기후대] 시장에서의 [차종] 가격 경쟁력 강화! 지금이 최적의 구매 시기"
                ],
                "브랜드 인지도 향상": [
                    "🌱 [국가]에서의 [차종] 재도약 - [기후대] 소비자 피드백 반영한 개선 모델",
                    "🔄 [차종]의 [국가] 시장 재편 - 현지 취향에 맞춘 업그레이드 진행 중"
                ]
            },
            "유지": {
                "출시 홍보": [
                    "🌟 [국가] 시장에서 꾸준한 인기! [차종]의 [기후대] 대응 능력 검증 완료",
                    "📌 [국가]의 안정적인 [차종] 수요 - [기후대] 조건에서의 신뢰성 입증"
                ],
                "할인 혜택 안내": [
                    "🔒 [국가]에서 꾸준한 판매 기록을 가진 [차종]! 이번 달 특별 할인 제공",
                    "🏅 [기후대] 시장에서 검증된 [차종]의 가치 - 한정 기간 프로모션"
                ],
                "브랜드 인지도 향상": [
                    "🏅 [국가] 시장에서의 안정적인 [차종] 인기 - [기후대] 환경 적응력 검증",
                    "📊 [차종]의 [국가] 시장 성과 - 꾸준한 판매로 현지 시장 공략 지속"
                ]
            }
        }
        self.emojis = ["🚀", "🌟", "✨", "💎", "🛒", "🎁", "🏆", "📢", "🌍", "❄️", "🔥"]
    
    def get_trend(self, current_sales: float, previous_sales: float) -> Tuple[str, float]:
        """수출량 변화 추세 계산 (5% 이상 차이일 경우 상승/하락 판단)"""
        if previous_sales == 0:
            return "유지", 0
        change_percent = ((current_sales - previous_sales) / previous_sales) * 100
        if change_percent > 5:
            return "상승세", change_percent
        elif change_percent < -5:
            return "하락세", change_percent
        else:
            return "유지", change_percent
    
    def generate_trend_message(self, country: str, climate: str, car_type: str, 
                             customer_type: str, marketing_goal: str,
                             current_sales: float, previous_sales: float) -> str:
        """수출량 변화에 따른 기본 마케팅 메시지 생성"""
        trend, percent = self.get_trend(current_sales, previous_sales)
        template_group = self.templates.get(trend, {}).get(marketing_goal, [
            "🎯 [국가]의 [고객유형] 고객님을 위한 [차종] 특별 제안"
        ])
        template = random.choice(template_group)
        replacements = {
            "[국가]": country,
            "[기후대]": climate,
            "[차종]": car_type,
            "[고객유형]": customer_type,
            "[증가율]": f"{abs(percent):.1f}"
        }
        for key, value in replacements.items():
            template = template.replace(key, str(value))
        return f"{random.choice(self.emojis)} {template}"

class APIManager:
    """강화된 API 연결 관리 클래스"""
    
    def __init__(self):
        self.api_url = "https://api-inference.huggingface.co/models/google/gemma-3-27b-it"
        self.api_key = ""  # 보안 주의
        self.max_retries = 3
        self.timeout = 30
    
    def query_api(self, prompt: str) -> Tuple[str, bool]:
        """개선된 API 호출 함수"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 전문적인 프롬프트 구성
        system_prompt = (
            "당신은 기아자동차의 마케팅 전문가입니다. "
            "주어진 조건에 맞는 자동차 마케팅 문구를 생성해주세요. "
            "반드시 다음 조건을 충족해야 합니다:\n"
            "- 100자 의 간결한 문장\n"
            "- 자동차 마케팅에 적합한 전문적인 내용\n"
            "- 이모지 1개 포함\n"
            "- 반복되는 단어 없음\n"
            "- 자연스러운 한국어\n\n"
            "생성 예시:\n"
            "❄️ 노르웨이의 추운 겨울을 위한 전기 SUV! 환경을 생각하는 당신을 위한 최적의 선택"
            "당신은 현대/기아차 마케팅 팀의 카피라이터입니다."
            "고급스러운 표현 사용 (현대차/기아차 스타일)"
            "고객의 마음을 사로잡는 매력적인 문구 생성\n"
            "반복 표현 피하기"
        )
        
        full_prompt = f"{system_prompt}\n\n요청: {prompt}\n생성된 문구:"
        
        payload = {
            "inputs": full_prompt,
            "parameters": {
                "max_new_tokens": 100,
                "temperature": 0.7,
                "top_k": 50,
                "top_p": 0.9,
                "repetition_penalty": 1.5,
                "do_sample": True,
                "return_full_text": False
            },
            "options": {
                "wait_for_model": True
            }
        }
        
        for attempt in range(self.max_retries):
            try:
                with st.spinner(f"AI 생성 중 (시도 {attempt + 1}/{self.max_retries})..."):
                    response = requests.post(
                        self.api_url,
                        headers=headers,
                        json=payload,
                        timeout=self.timeout
                    )
                
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list) and result:
                        generated = result[0].get('generated_text', '').strip()
                        # 품질 검증
                        if (len(generated) > 20 and 
                            not any(word*3 in generated for word in ["귀여운", "아기"]) and
                            any(emoji in generated for emoji in ["🚀", "🌟", "✨", "💎", "🛒", "🎁", "🏆", "📢"])):
                            return generated.split("\n")[0], True
                
                elif response.status_code == 503:  # 서비스 불가능
                    wait_time = 5 * (attempt + 1)
                    st.warning(f"모델 준비 중... {wait_time}초 후 재시도")
                    time.sleep(wait_time)
                    continue
                
                if attempt < self.max_retries - 1:
                    time.sleep(2 * (attempt + 1))
                    
            except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
                st.warning(f"API 연결 오류: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(3 * (attempt + 1))
                continue
        
        return "", False

# ------------------------------
# 3. Streamlit 애플리케이션 (UI 개선)
# ------------------------------
def main():
    st.set_page_config(
        page_title="기아 AI 마케팅 어시스턴트",
        page_icon="🚗",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS 스타일
    st.markdown("""
    <style>
        .main-title {
            color: #003366;
            text-align: center;
            margin-bottom: 30px;
        }
        .message-box {
            background-color: #f0f8ff;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            border-left: 5px solid #0066cc;
            font-size: 18px;
        }
        .warning-box {
            background-color: #fff3cd;
            border-radius: 8px;
            padding: 15px;
            margin: 15px 0;
            border-left: 5px solid #ffc107;
        }
        .trend-up { color: #28a745; font-weight: bold; }
        .trend-down { color: #dc3545; font-weight: bold; }
        .trend-neutral { color: #6c757d; font-weight: bold; }
        .stButton>button {
            background-color: #0066cc;
            color: white;
            font-weight: bold;
            border-radius: 5px;
            padding: 10px 24px;
        }
        .stSelectbox, .stTextInput {
            margin-bottom: 15px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 class="main-title">🚗 기아 AI 마케팅 메시지 생성 시스템</h1>', unsafe_allow_html=True)
    
    # 사이드바
    with st.sidebar:
        st.header("📌 사용 가이드")
        st.markdown("""
        1. 마케팅 조건 설정
        2. 생성 버튼 클릭
        3. 결과 확인 및 수정
        4. 필요시 메시지 다운로드
        """)
        st.markdown("---")
        st.markdown("**🔧 설정 옵션**")
        auto_emoji = st.checkbox("이모지 자동 추가", value=True)
        st.markdown("---")
        st.markdown("**📊 데이터 정보**")
        st.markdown(f"- 국가: {len(df['국가명'].unique())}개")
        st.markdown(f"- 차종: {len(df['차종'].unique())}종")
        st.markdown(f"- 기후대: {len(df['기후대'].unique())}종")
    
    # 입력 섹션
    with st.container():
        st.subheader("🔍 마케팅 조건 설정")
        
        col1, col2 = st.columns(2)
        with col1:
            selected_climate = st.selectbox(
                "기후대 선택*",
                sorted(df['기후대'].unique()),
                index=0,
                help="차량이 운영될 기후 조건을 선택하세요"
            )
            filtered_countries = sorted(df[df['기후대'] == selected_climate]['국가명'].unique())
            country = st.selectbox(
                "국가 선택*",
                filtered_countries,
                index=0,
                help="타겟 국가를 선택하세요"
            )
            vehicle_category = st.selectbox(
                "차량 구분 선택*",
                sorted(df['차량 구분'].unique()),
                index=0,
                help="차량 유형을 선택하세요"
            )
            
        with col2:
            filtered_vehicle_types = sorted(df[df['차량 구분'] == vehicle_category]['차종'].unique())
            vehicle_type = st.selectbox(
                "차종 선택*",
                filtered_vehicle_types,
                index=0,
                help="마케팅할 차종을 선택하세요"
            )
            customer_type = st.text_input(
                "고객 유형*", 
                "실용적인",
                help="예: 친환경적인, 젊은, 가족 지향적인, 프리미엄"
            )
            marketing_goal = st.selectbox(
                "마케팅 목적*",
                ["출시 홍보", "할인 혜택 안내", "브랜드 인지도 향상"],
                index=0,
                help="마케팅의 주요 목적을 선택하세요"
            )
            st.markdown("<small>* 필수 입력 항목</small>", unsafe_allow_html=True)
        
        submitted = st.button(
            "✨ AI 마케팅 메시지 생성",
            type="primary",
            use_container_width=True
        )
    
    # 메시지 생성 섹션
    if submitted:
        if not all([selected_climate, country, vehicle_category, vehicle_type, customer_type, marketing_goal]):
            st.error("모든 필수 항목(*)을 입력해주세요.")
            return
        
        message_generator = MarketingMessageGenerator()
        api_manager = APIManager()
        
        # 수출량 데이터 분석
        try:
            country_data = df_model[(df_model['국가명'] == country) & (df_model['차종'] == vehicle_type)]
            if not country_data.empty:
                country_data = country_data.sort_values('날짜', ascending=False)
                latest_data = country_data.iloc[0]
                previous_data = country_data.iloc[1] if len(country_data) > 1 else latest_data
                
                current_sales = latest_data['수출량']
                previous_sales = previous_data['수출량']
                gdp = gdp_mapping.get(country, "정보 없음")
                
                trend, percent = message_generator.get_trend(current_sales, previous_sales)
                
                st.subheader("📊 수출량 분석 결과")
                col1, col2, col3 = st.columns(3)
                with col1:
                    delta_text = f"{percent:.1f}% ({'증가' if trend=='상승세' else '감소' if trend=='하락세' else '유지'})"
                    st.metric("현재 수출량", f"{current_sales:,}대", delta=delta_text,
                              delta_color=("normal" if trend != "하락세" else "inverse"))
                with col2:
                    st.metric("국가 GDP", f"${gdp:,}" if isinstance(gdp, (int, float)) else gdp)
                with col3:
                    trend_display = {
                        "상승세": '<span class="trend-up">↑ 상승세</span>',
                        "하락세": '<span class="trend-down">↓ 하락세</span>',
                        "유지": '<span class="trend-neutral">→ 유지</span>'
                    }.get(trend, "")
                    st.markdown(f"**판매 추이:** {trend_display}", unsafe_allow_html=True)
            else:
                current_sales = 0
                previous_sales = 0
                st.warning("선택한 국가와 차종에 대한 수출량 데이터가 없습니다. 기본 메시지를 생성합니다.")
                gdp = gdp_mapping.get(country, "정보 없음")
                trend, percent = "유지", 0
        except Exception as e:
            st.error(f"수출량 분석 중 오류 발생: {str(e)}")
            current_sales, previous_sales, trend, percent = 0, 0, "유지", 0
            gdp = gdp_mapping.get(country, "정보 없음")
        
        # API 호출을 위한 프롬프트 구성
        prompt = (
            f"국가: {country} (GDP: {gdp if isinstance(gdp, (int, float)) else '정보 없음'})\n"
            f"기후대: {selected_climate}\n"
            f"차종: {vehicle_type} ({vehicle_category})\n"
            f"고객 유형: {customer_type}\n"
            f"마케팅 목적: {marketing_goal}\n"
            f"판매 추이: {trend} ({percent:.1f}% {'증가' if trend=='상승세' else '감소' if trend=='하락세' else '유지'})\n\n"
            f"위 조건에 맞는 자동차 마케팅 문구를 생성해주세요."
        )
        
        api_message, api_success = api_manager.query_api(prompt)
        
        # 결과 표시
        st.subheader("💡 생성된 마케팅 메시지")
        
        if api_success:
            st.markdown(
                f'<div class="message-box">{api_message}</div>',
                unsafe_allow_html=True
            )
            st.success("AI가 생성한 최적화된 마케팅 메시지입니다.")
        else:
            default_msg = message_generator.generate_trend_message(
                country, selected_climate, vehicle_type, 
                customer_type, marketing_goal,
                current_sales, previous_sales
            )
            st.markdown(
                f'<div class="message-box">{default_msg}</div>',
                unsafe_allow_html=True
            )
            st.markdown(
                '<div class="warning-box">'
                '⚠️ API 연결에 일시적 문제가 있어 고품질 기본 메시지를 제공합니다. '
                '잠시 후 다시 시도해주세요.'
                '</div>',
                unsafe_allow_html=True
            )
        
        # 추가 기능
        with st.expander("🛠️ 메시지 사용자 지정 및 다운로드", expanded=True):
            final_message = st.text_area(
                "메시지 수정",
                value=api_message if api_success else default_msg,
                height=120,
                key="message_editor"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✏️ 수정 내용 적용", use_container_width=True):
                    st.session_state.final_message = final_message
                    st.rerun()
            with col2:
                if st.download_button(
                    label="📥 메시지 다운로드",
                    data=final_message,
                    file_name=f"kia_marketing_{country}_{vehicle_type}.txt",
                    mime="text/plain",
                    use_container_width=True
                ):
                    st.toast("메시지가 다운로드되었습니다!")
            
            if "final_message" in st.session_state:
                st.markdown("**최종 메시지 미리보기:**")
                st.info(st.session_state.final_message)

