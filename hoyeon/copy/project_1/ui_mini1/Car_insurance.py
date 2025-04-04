import streamlit as st
import pandas as pd
import joblib
from datetime import datetime
from pathlib import Path

# 보험사 및 모델 데이터 정의
launch_dates = {
    '현대': {
        'G70 (IK)': '2017-09',
        'NEXO (FE)': '2018-01',
        'Avante (CN7 N)': '2020-05',
        'G80 (RG3)': '2020-03',
        'Grandeur (GN7 HEV)': '2022-01',
        'Tucson (NX4 PHEV)': '2021-05',
        'Avante (CN7 HEV)': '2020-07',
        'IONIQ 6 (CE)': '2022-06',
        'G90 (HI)': '2022-03',
        'Santa-Fe (MX5 PHEV)': '2022-06'
    }
}

eco_friendly_models = {
    '현대': [
        'NEXO (FE)', 'Avante (CN7 HEV)', 'Grandeur (GN7 HEV)', 
        'Tucson (NX4 PHEV)', 'IONIQ 6 (CE)', 'Santa-Fe (MX5 PHEV)'
    ]
}

# 클러스터별 보험사 추천 (현대해상 + 1개 보험사)
insurance_recommendations = {
    0: ["현대해상", "삼성화재"],
    1: ["현대해상", "KB손해보험"],
    2: ["현대해상", "DB손해보험"],
    3: ["현대해상", "한화손해보험"],
    4: ["현대해상", "메리츠화재"],
    5: ["현대해상", "롯데손해보험"]
}

# 보험사 상세 정보 (강화된 버전)
insurance_companies = {
    "현대해상": {
        "logo": "hoyeon/hun_bo.png",
        "description": "현대자동차 공식 보험 파트너로 현대차 전용 특별 혜택 제공",
        "strengths": ["현대차 전용 최대 15% 할인", "전국 현대차 서비스센터 연계 AS", "24시간 긴급출동 서비스"],
        "contact": "1588-5656",
        "discounts": {
            "친환경차": 0.15,
            "무사고": 0.1,
            "신차": 0.05
        },
        "coverage_details": {
            "기본보장": ["대인배상 무한", "대물배상 2억원", "자기신체사고 1억원"],
            "특별보장": ["자차보험(전손/도난)", "긴급출동서비스", "렌터카 비용 지원"],
            "현대차특화": ["전용 서비스센터 할인", "부품 교체 지원", "보험료 분납 혜택"]
        }
    },
    "삼성화재": {
        "logo": "hoyeon/sam_bo.png",
        "description": "국내 최대 자동차 보험사로 안정적인 보장과 빠른 보상 처리",
        "strengths": ["전국망 사고처리 시스템", "다양한 할인혜택", "모바일 앱을 통한 편리한 청약/보상"],
        "contact": "1588-5114",
        "discounts": {
            "친환경차": 0.1,
            "무사고": 0.15,
            "신차": 0.03
        },
        "coverage_details": {
            "기본보장": ["대인배상 무한", "대물배상 3억원", "자기신체사고 8천만원"],
            "특별보장": ["자차종합보험", "긴급구조비용", "법률비용 지원"],
            "부가서비스": ["사고 예방 교육", "차량 점검 서비스", "보험료 감면 혜택"]
        }
    },
    "KB손해보험": {
        "logo": "hoyeon/kb_bo.png",
        "description": "KB금융그룹 계열사로 금융사 연계 혜택 제공",
        "strengths": ["KB금융 연계 최대 10% 추가 할인", "전국 지점망", "간편한 보상절차"],
        "contact": "1544-0114",
        "discounts": {
            "친환경차": 0.12,
            "무사고": 0.12,
            "신차": 0.04
        },
        "coverage_details": {
            "기본보장": ["대인배상 무한", "대물배상 2억5천만원", "자기신체사고 7천만원"],
            "특별보장": ["자차손해 면책금 감면", "사고처리 비용 지원", "의료비 추가 보장"],
            "금융연계": ["대출금 연계 보장", "카드 결제 할인", "적립금 혜택"]
        }
    },
    "DB손해보험": {
        "logo": "hoyeon/db_bo.png",
        "description": "디지털 보험 선도 기업으로 온라인 특약 다양",
        "strengths": ["온라인 최저가 보장", "할인율 경쟁력", "모바일 청약 편리성"],
        "contact": "1588-0100",
        "discounts": {
            "친환경차": 0.13,
            "무사고": 0.13,
            "신차": 0.05
        },
        "coverage_details": {
            "기본보장": ["대인배상 무한", "대물배상 2억원", "자기신체사고 6천만원"],
            "특별보장": ["자차통합보험", "긴급 수리비 지원", "차량 감가상각 보상"],
            "디지털특화": ["온라인 전용 할인", "AI 사고 접수", "실시간 보상 진행 현황"]
        }
    },
    "한화손해보험": {
        "logo": "hoyeon/han_bo.png",
        "description": "한화그룹 계열 보험사로 그룹사 연계 혜택 풍부",
        "strengths": ["그룹사 포인트 통합 활용", "보험료 할인 다양", "고객센터 평가 우수"],
        "contact": "1588-6363",
        "discounts": {
            "친환경차": 0.1,
            "무사고": 0.1,
            "신차": 0.05
        },
        "coverage_details": {
            "기본보장": ["대인배상 무한", "대물배상 2억원", "자기신체사고 9천만원"],
            "특별보장": ["자차면책금 감면", "사고조사 비용 지원", "의료비 추가 지급"],
            "그룹혜택": ["한화리조트 할인", "포인트 적립", "제휴사 할인"]
        }
    },
    "메리츠화재": {
        "logo": "hoyeon/mer_bo.png",
        "description": "자동차 보험 전문성 강점으로 보험료 할인율 높음",
        "strengths": ["보험료 할인율 경쟁력", "사고처리 빠름", "모바일 앱 편의성"],
        "contact": "1588-9600",
        "discounts": {
            "친환경차": 0.15,
            "무사고": 0.15,
            "신차": 0.07
        },
        "coverage_details": {
            "기본보장": ["대인배상 무한", "대물배상 2억원", "자기신체사고 5천만원"],
            "특별보장": ["자차종합보험", "긴급 출동 서비스", "렌터카 비용 지원"],
            "할인혜택": ["다중계약 할인", "장기무사고 할인", "온라인 가입 할인"]
        }
    },
    "롯데손해보험": {
        "logo": "hoyeon/lot_bo.png",
        "description": "롯데그룹 계열 보험사로 그룹사 포인트 연계",
        "strengths": ["롯데포인트 적립/사용", "할인 혜택 다양", "24시간 사고 접수"],
        "contact": "1588-8100",
        "discounts": {
            "친환경차": 0.1,
            "무사고": 0.1,
            "신차": 0.05
        },
        "coverage_details": {
            "기본보장": ["대인배상 무한", "대물배상 2억원", "자기신체사고 7천만원"],
            "특별보장": ["자차통합보험", "긴급 출동 서비스", "법률 상담 지원"],
            "포인트혜택": ["보험료 포인트 결제", "제휴사 할인", "포인트 추가 적립"]
        }
    }
}

# 보험 유형 상세 정보
insurance_type_details = {
    "친환경특화보험": {
        "description": "친환경 차량 전용 보험으로 배터리 및 충전 관련 사고를 특별히 보장",
        "price_range": "15~25만원",
        "base_price": 200000,
        "coverages": {
            "필수보장": [
                "대인배상 무한 (사망/상해)",
                "대물배상 2억원 (차량사고로 인한 타인 재산 피해)",
                "자기신체사고 1억원 (운전자 상해 보장)"
            ],
            "친환경특화보장": [
                "고전압 배터리 손상 보장 (사고, 화재, 침수 시)",
                "충전기 사고 보상 (충전 중 발생한 사고)",
                "전기차 전용 부품 교체 지원",
                "긴급 충전 서비스 (배터리 방전 시)"
            ],
            "추가서비스": [
                "친환경차 전용 서비스센터 할인",
                "배터리 성능 보증 연장 옵션",
                "환경부 인증 탄소배출 감축 포인트 적립"
            ]
        }
    },
    "프리미엄보험": {
        "description": "고급 차량 및 고객을 위한 종합 보장 패키지",
        "price_range": "20~30만원",
        "base_price": 250000,
        "coverages": {
            "필수보장": [
                "대인배상 무한 (사망/상해)",
                "대물배상 3억원 (고가 차량에 적합한 높은 보장한도)",
                "자기신체사고 1억원 (운전자 상해 보장)"
            ],
            "특별보장": [
                "자차종합보험 (전손/도난/추돌/횡돌 등 전면 보장)",
                "고급차 전용 부품 교체 지원 (OEM 부품 보장)",
                "VIP 긴급출동 서비스 (전문 기사 파견)",
                "전국 네트워크 로드 서비스"
            ],
            "부가서비스": [
                "전용 콜센터 (24시간 전문 상담원 연결)",
                "렌터카 업그레이드 옵션",
                "해외에서의 사고 지원 서비스"
            ]
        }
    },
    "표준보험": {
        "description": "일반 차량에 적합한 기본적인 보장을 제공하는 보험",
        "price_range": "10~20만원",
        "base_price": 150000,
        "coverages": {
            "필수보장": [
                "대인배상 무한 (사망/상해)",
                "대물배상 2억원 (차량사고로 인한 타인 재산 피해)",
                "자기신체사고 5천만원 (운전자 상해 보장)"
            ],
            "기본보장": [
                "자차손해보험 (전손/도난 시 보상)",
                "대물사고 면책금 감면 특약",
                "긴급 출동 서비스 (기본)"
            ],
            "선택보장": [
                "자동차 액세서리 보장 (추가 비용 발생 시)",
                "의료비 추가 지급 특약",
                "법률비용 지원 서비스"
            ]
        }
    }
}

def load_css():
    st.markdown("""
    <style>
        .main {
            background-color: #f8f9fa;
        }
        .stButton>button {
            background-color: #0d6efd;
            color: white;
            border-radius: 5px;
            padding: 0.5rem 1rem;
            border: none;
        }
        .stButton>button:hover {
            background-color: #0b5ed7;
            color: white;
        }
        .header {
            color: #0d6efd;
            padding: 1rem 0;
        }
        .highlight {
            background-color: #e7f1ff;
            padding: 0.5rem;
            border-radius: 5px;
            margin: 0.5rem 0;
        }
        .insurance-card {
            transition: transform 0.3s;
            height: 100%;
            padding: 1rem;
            border: 1px solid #dee2e6;
            border-radius: 10px;
            margin-bottom: 1rem;
        }
        .insurance-card:hover {
            transform: scale(1.02);
            box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
        }
        .eco-badge {
            background-color: #198754;
            color: white;
            padding: 0.25rem 0.5rem;
            border-radius: 20px;
            font-size: 0.8rem;
            display: inline-block;
            margin-left: 0.5rem;
        }
        .premium-badge {
            background-color: #6f42c1;
            color: white;
            padding: 0.25rem 0.5rem;
            border-radius: 20px;
            font-size: 0.8rem;
            display: inline-block;
            margin-left: 0.5rem;
        }
        .company-logo {
            max-height: 60px;
            margin-bottom: 1rem;
        }
        .coverage-item {
            padding: 0.5rem;
            margin: 0.25rem 0;
            border-left: 3px solid #0d6efd;
            background-color: #f8f9fa;
        }
        .coverage-category {
            font-weight: bold;
            color: #0d6efd;
            margin-top: 1rem;
        }
        .tab-content {
            padding: 1rem;
            border: 1px solid #dee2e6;
            border-top: none;
            border-radius: 0 0 10px 10px;
        }
    </style>
    """, unsafe_allow_html=True)

def load_models():
    """모델 로드 함수"""
    model_dir = Path(__file__).parent.parent / "models_mini1"
    segment_model_path = model_dir / "gb_model_hs.pkl"
    clustering_model_path = model_dir / "gb_pipeline_hc.pkl"

    if not segment_model_path.exists() or not clustering_model_path.exists():
        st.error("모델 파일을 찾을 수 없습니다.")
        st.stop()

    return joblib.load(segment_model_path), joblib.load(clustering_model_path)

def input_customer_info():
    """고객 정보 입력 폼"""
    st.title("📋 현대 고객 정보 입력")
    
    segment_model, clustering_model = load_models()
    
    with st.form(key="customer_form"):
        # 섹션 1: 기본 정보
        st.subheader("1. 기본 정보")
        col1, col2 = st.columns(2)
        
        with col1:
            gender = st.selectbox("성별", ["남", "여"], key="gender")
            birth_date = st.date_input("생년월일", 
                                    min_value=datetime(1900, 1, 1), 
                                    max_value=datetime.today().replace(year=datetime.today().year - 20),
                                    key="birth_date")
        
        with col2:
            car_type = st.selectbox("차량 유형", ["준중형 세단", "중형 세단", "대형 세단", "SUV"], key="car_type")
            selected_vehicle = st.selectbox("모델 선택", list(launch_dates['현대'].keys()), key="car_model")
    
        # 섹션 2: 구매 정보
        st.subheader("2. 구매 정보")
        col1, col2 = st.columns(2)
        
        with col1:
            transaction_amount = st.number_input("예산 (원)", min_value=10000000, step=1000000, format="%d", key="budget")
            purchase_frequency = st.number_input("구매 빈도", min_value=1, value=1, key="purchase_freq")
        
        with col2:
            transaction_method = st.selectbox("거래 방식", ["카드", "현금", "계좌이체"], key="payment_method")
            purchase_date = st.date_input("구매 예정일", key="purchase_date")
    
        # 섹션 3: 보험 정보
        st.subheader("3. 보험 정보")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            driving_exp = st.selectbox("운전 경력", ["1년 미만", "1~3년", "3~5년", "5년 이상"], key="driving_exp_select")
        
        with col2:
            accident_history = st.selectbox("최근 3년 사고 이력", ["무사고", "1건", "2건", "3건 이상"], key="accident_history_select")
        
        with col3:
            car_age = st.selectbox("차량 연식", ["신차", "1~3년", "3~5년", "5~7년", "7년 이상"], key="car_age_select")
        
        # 제출 버튼
        submitted = st.form_submit_button("보험 추천 받기", use_container_width=True)
        
        if submitted:
            # 연령 계산
            today = datetime.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            
            # 세그먼트 예측
            segment_input = pd.DataFrame([[transaction_method, launch_dates['현대'].get(selected_vehicle), 
                                        purchase_date, transaction_amount, purchase_frequency]],
                                      columns=['거래 방식', '제품 출시년월', '제품 구매 날짜', 
                                               '거래 금액', '제품 구매 빈도'])
            customer_segment = segment_model.predict(segment_input)[0]
            
            # 클러스터링 예측
            cluster_input = pd.DataFrame([[gender, car_type, transaction_method, 
                                         launch_dates['현대'].get(selected_vehicle),
                                         purchase_date, customer_segment,
                                         "여" if selected_vehicle in eco_friendly_models['현대'] else "부",
                                         age, transaction_amount, purchase_frequency]],
                                       columns=['성별', '차량구분', '거래 방식', '제품 출시년월',
                                               '제품 구매 날짜', '고객 세그먼트', '친환경차',
                                               '연령', '거래 금액', '제품 구매 빈도'])
            cluster_id = clustering_model.predict(cluster_input)[0]
            
            # 세션 상태 저장 (네임스페이스 적용)
            st.session_state.update({
                "car_insurance_step": 2,
                "car_insurance_cluster_id": cluster_id,
                "car_insurance_selected_vehicle": selected_vehicle,
                "car_insurance_driving_exp": driving_exp,
                "car_insurance_accident_history": accident_history,
                "car_insurance_car_age": car_age,
                "car_insurance_gender": gender,
                "car_insurance_birth_date": birth_date,
                "car_insurance_transaction_amount": transaction_amount,
                "car_insurance_purchase_frequency": purchase_frequency,
                "car_insurance_car_type": car_type,
                "car_insurance_transaction_method": transaction_method,
                "car_insurance_purchase_date": purchase_date,
                "car_insurance_age": age,
                "car_insurance_is_eco_friendly": selected_vehicle in eco_friendly_models['현대']
            })
            
            st.rerun()

def Car_insurance_recommendation():
    """보험 추천 정보 표시"""
    st.title("🚗 현대 맞춤형 자동차 보험 추천")
    
    # 세션에서 고객 정보 가져오기 (네임스페이스 적용)
    cluster_id = st.session_state.get("car_insurance_cluster_id", 0)
    selected_vehicle = st.session_state.get("car_insurance_selected_vehicle", "")
    is_eco_friendly = st.session_state.get("car_insurance_is_eco_friendly", False)
    driving_exp = st.session_state.get("car_insurance_driving_exp", "3~5년")
    accident_history = st.session_state.get("car_insurance_accident_history", "무사고")
    car_age = st.session_state.get("car_insurance_car_age", "신차")
    
    # 보험사 추천 섹션
    with st.container():
        st.write("")
        st.write("")
        st.subheader("🏆 추천 보험사")
        st.write("")
        
        recommended_insurances = insurance_recommendations.get(cluster_id, ["현대해상"])
        cols = st.columns(len(recommended_insurances))
        
        for idx, insurance in enumerate(recommended_insurances):
            with cols[idx]:
                info = insurance_companies.get(insurance, {})
                with st.container():
                    # 보험사 로고
                    st.image(info.get("logo", ""), use_container_width=True)
                    
                    # 보험사 이름
                    st.markdown(f"<h3 style='margin-top: 0.5rem;'>{insurance}</h3>", unsafe_allow_html=True)
                    
                    # 보험사 설명
                    st.markdown(f"<p style='color: #6c757d; font-size: 0.9rem;'>{info.get('description', '')}</p>", unsafe_allow_html=True)
                    
                    # 강점 목록
                    st.markdown("<p style='margin-bottom: 0.5rem;'><strong>주요 강점:</strong></p>", unsafe_allow_html=True)
                    for strength in info.get("strengths", []):
                        st.markdown(f"<p style='margin: 0.2rem 0; font-size: 0.9rem;'>✓ {strength}</p>", unsafe_allow_html=True)
                    
                    # 현대해상 특별 할인 강조
                    if insurance == "현대해상":
                        st.markdown('<div class="highlight" style="font-size: 0.9rem;">✅ 현대차 구매 고객 전용 특별 할인</div>', unsafe_allow_html=True)
                    
                    # 연락처
                    st.markdown(f"<p style='margin-top: 1rem; margin-bottom: 0;'><strong>문의:</strong> 📞 {info.get('contact', '')}</p>", unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)

    # 보험 유형 추천 섹션
    with st.container():
        st.subheader("🔍 추천 보험 유형")
        
        if is_eco_friendly:
            insurance_type = "친환경특화보험"
            eco_badge = '<span class="eco-badge">친환경차 특화</span>'
        elif cluster_id in [1, 3]:  # 프리미엄 고객
            insurance_type = "프리미엄보험"
            eco_badge = '<span class="premium-badge">프리미엄</span>'
        else:
            insurance_type = "표준보험"
            eco_badge = ''
        
        type_info = insurance_type_details.get(insurance_type, {})
        
        with st.container():
            st.markdown(f'<div class="card">', unsafe_allow_html=True)
            st.markdown(f"<h3 style='display: flex; align-items: center;'>{insurance_type}{eco_badge}</h3>", unsafe_allow_html=True)
            
            # 보험 설명
            st.markdown(f"<p>{type_info.get('description', '')}</p>", unsafe_allow_html=True)
            
            # 가격 정보
            st.markdown(f"<p><strong>월 예상 보험료:</strong> <span style='color: #0d6efd; font-weight: bold;'>{type_info.get('price_range', '')}</span></p>", unsafe_allow_html=True)
            
            # 보장 내용 탭
            tab1, tab2, tab3 = st.tabs(list(type_info.get("coverages", {}).keys()))
            
            for tab, (category, items) in zip([tab1, tab2, tab3], type_info.get("coverages", {}).items()):
                with tab:
                    st.markdown(f"<div class='coverage-category'>{category}</div>", unsafe_allow_html=True)
                    for item in items:
                        st.markdown(f"<div class='coverage-item'>• {item}</div>", unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

    # 보험료 계산 섹션
    with st.container():
        st.subheader("📊 보험료 예상 계산")
        
        # 가격 계산 로직
        def calculate_insurance_price(base_price):
            # 할인/할증 요소
            factors = {
                "driving_exp": {
                    "1년 미만": 1.2, "1~3년": 1.1, "3~5년": 1.0, "5년 이상": 0.9
                },
                "accident_history": {
                    "무사고": 0.85, "1건": 1.0, "2건": 1.2, "3건 이상": 1.5
                },
                "car_age": {
                    "신차": 1.1, "1~3년": 1.0, "3~5년": 0.95, 
                    "5~7년": 0.9, "7년 이상": 0.8
                }
            }
            
            price = base_price
            price *= factors["driving_exp"][driving_exp]
            price *= factors["accident_history"][accident_history]
            price *= factors["car_age"][car_age]
            
            return int(price)
        
        # 보험사별 가격 계산
        insurance_prices = {}
        for ins in recommended_insurances:
            ins_info = insurance_companies.get(ins, {})
            base_price = type_info.get("base_price", 150000)
            temp_price = calculate_insurance_price(base_price)
            
            # 할인 적용
            discounts = ins_info.get("discounts", {})
            if is_eco_friendly:
                temp_price *= (1 - discounts.get("친환경차", 0))
            if accident_history == "무사고":
                temp_price *= (1 - discounts.get("무사고", 0))
            if car_age == "신차":
                temp_price *= (1 - discounts.get("신차", 0))
            
            insurance_prices[ins] = int(temp_price)
        
        # 결과 표시
        min_price = min(insurance_prices.values())
        max_price = max(insurance_prices.values())
        
        st.markdown(f"""
        <div class="highlight">
            <h4 style='margin: 0; color: #0d6efd;'>월 예상 보험료 범위</h4>
            <p style='font-size: 1.5rem; font-weight: bold; margin: 0.5rem 0;'>
                {min_price:,}원 ~ {max_price:,}원
            </p>
            <p style='font-size: 0.9rem; margin: 0;'>* 고객 프로필과 차량 정보를 기반으로 한 예상 금액이며, 정확한 보험료는 보험사 심사 후 결정됩니다.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 보험사별 상세 정보
        st.markdown("---")
        st.subheader("🔍 보험사별 상세 보장 내용")
        
        for ins, price in insurance_prices.items():
            with st.expander(f"{ins} - 월 예상 보험료: {price:,}원", expanded=True):
                info = insurance_companies.get(ins, {})
                
                # 할인 정보
                discount_info = []
                ins_discounts = info.get("discounts", {})
                
                if is_eco_friendly and ins_discounts.get("친환경차", 0) > 0:
                    discount_info.append(f"친환경차 {ins_discounts['친환경차']*100:.0f}% 할인")
                if accident_history == "무사고" and ins_discounts.get("무사고", 0) > 0:
                    discount_info.append(f"무사고 {ins_discounts['무사고']*100:.0f}% 할인")
                if car_age == "신차" and ins_discounts.get("신차", 0) > 0:
                    discount_info.append(f"신차 {ins_discounts['신차']*100:.0f}% 할인")
                
                if discount_info:
                    st.markdown(f"<p><strong>적용된 할인:</strong> {', '.join(discount_info)}</p>", unsafe_allow_html=True)
                
                # 보장 내용 탭
                tabs = st.tabs(list(info.get("coverage_details", {}).keys()))
                
                for tab, (category, items) in zip(tabs, info.get("coverage_details", {}).items()):
                    with tab:
                        st.markdown(f"<div class='coverage-category'>{category}</div>", unsafe_allow_html=True)
                        for item in items:
                            st.markdown(f"<div class='coverage-item'>• {item}</div>", unsafe_allow_html=True)
                
                # 보험사 연락처
                st.markdown(f"<div style='margin-top: 1rem;'><strong>문의 전화:</strong> 📞 {info.get('contact', '')}</div>", unsafe_allow_html=True)

    # 다시 입력하기 버튼
    if st.button("다시 입력하기", use_container_width=True):
        st.session_state["car_insurance_step"] = 1
        st.rerun()

def run_car_customer_info():
    """메인 앱 실행 (네임스페이스 적용)"""
    load_css()
    
    # 네임스페이스를 사용한 세션 상태 초기화
    if "car_insurance_step" not in st.session_state:
        st.session_state["car_insurance_step"] = 1
    
    # 단계별 페이지 표시
    if st.session_state["car_insurance_step"] == 1:
        input_customer_info()
    elif st.session_state["car_insurance_step"] == 2:
        Car_insurance_recommendation()

if __name__ == "__main__":
    run_car_customer_info()
