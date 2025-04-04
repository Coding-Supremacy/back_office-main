import os
import time
import streamlit as st
import pandas as pd
import joblib
from datetime import datetime
import re
from pathlib import Path
import base64
import requests


def get_abs_path(relative_path):
    """상대 경로를 절대 경로로 변환"""
    return Path(__file__).parent.parent / relative_path

# 모델과 출시 년월 데이터
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
    },
    '기아': {
        'K3': '2018-09',
        'EV6': '2021-03',
        'K5': '2019-12',
        'Telluride': '2019-01',
        'Seltos': '2019-06',
        'Sorento': '2020-03',
        'Carnival': '2020-06',
        'Sportage': '2021-06',
        'EV9': '2023-03'
    }
}

# 친환경차 모델 목록
eco_friendly_models = {
    '현대': [
        'NEXO (FE)', 'Avante (CN7 HEV)', 'Grandeur (GN7 HEV)', 
        'Tucson (NX4 PHEV)', 'IONIQ 6 (CE)', 'Santa-Fe (MX5 PHEV)'
    ],
    '기아': ['EV6', 'EV9']
}

# 클러스터별 차량 추천 모델 목록
brand_recommendations = {
    '현대': {
        0: ['Avante (CN7 N)', "G70 (IK)", "Tucson (NX4 PHEV)"],
        1: ["IONIQ 6 (CE)", "Grandeur (GN7 HEV)", "NEXO (FE)"],
        2: ["IONIQ 6 (CE)", "Grandeur (GN7 HEV)", "Santa-Fe (MX5 PHEV)"],
        3: ['Avante (CN7 N)', "Tucson (NX4 PHEV)", "G90 (HI)"],
        4: ["IONIQ 6 (CE)", "Santa-Fe (MX5 PHEV)", "Tucson (NX4 PHEV)"],
        5: ["Avante (CN7 N)", "G70 (IK)", "Tucson (NX4 PHEV)"]
    },
    '기아': {
        0: ["K5", "Telluride", "Sportage"],
        1: ["EV9", "Sorento", "Carnival"],
        2: ["K5", "EV6", "Seltos"],
        3: ["K5", "Sportage", "Tucson(NX4)"],
        4: ["Telluride", "EV9", "Sorento"],
        5: ["K5", "K3", "Sonet"]
    }
}

# 차량 이미지 경로
IMAGE_BASE_PATH = 'img/'
vehicle_images = {
    model: get_abs_path(f"{IMAGE_BASE_PATH}{model}.png")
    for brand_models in launch_dates.values()
    for model in brand_models
}

# 차량 가격 매핑
vehicle_prices = {
    "현대": {
        "Avante (CN7 N)": 23500000,
        "NEXO (FE)": 72500000,
        "G80 (RG3)": 64500000,
        "G90 (HI)": 84500000,
        "IONIQ 6 (CE)": 57800000,
        "Tucson (NX4 PHEV)": 48900000,
        "Grandeur (GN7 HEV)": 51200000,
        "G70 (IK)": 42500000,
        "Santa-Fe (MX5 PHEV)": 63500000,
        "Avante (CN7 HEV)": 24750000
    },
    "기아": {
        "K3": 24500000,
        "K5": 39500000,
        "EV6": 68500000,
        "Telluride": 62500000,
        "Seltos": 31200000,
        "Sorento": 54500000,
        "Carnival": 54500000,
        "Sportage": 34500000,
        "EV9": 78900000,
        "Sonet": 21500000
    }
}

# 차량 링크 매핑
vehicle_links = {
    "현대": {
        "Avante (CN7 N)": "https://www.hyundai.com/kr/ko/vehicles/avante",
        "NEXO (FE)": "https://www.hyundai.com/kr/ko/vehicles/nexo",
        "G80 (RG3)": "https://www.genesis.com/kr/ko/models/luxury-sedan-genesis/g80-black/highlights.html",
        "G90 (HI)": "https://www.genesis.com/kr/ko/models/luxury-sedan-genesis/g90-black/highlights.html",
        "IONIQ 6 (CE)": "https://www.hyundai.com/kr/ko/e/vehicles/ioniq6/intro",
        "Tucson (NX4 PHEV)": "https://www.hyundai.com/kr/ko/vehicles/tucson",
        "Grandeur (GN7 HEV)": "https://www.hyundai.com/kr/ko/vehicles/grandeur",
        "G70 (IK)": "https://www.genesis.com/kr/ko/models/luxury-sedan-genesis/g70/highlights.html",
        "Santa-Fe (MX5 PHEV)": "https://www.hyundai.com/kr/ko/e/vehicles/santafe/intro",
        "Avante (CN7 HEV)": "https://www.hyundai.com/kr/ko/e/vehicles/avante-n/intro"
    },
    "기아": {
        "K3": "https://www.kia.com/kr/vehicles/k3/summary.html",
        "K5": "https://www.kia.com/kr/vehicles/k5/summary.html",
        "EV6": "https://www.kia.com/kr/vehicles/ev6/summary.html",
        "Telluride": "https://www.kia.com/us/en/telluride",
        "Seltos": "https://www.kia.com/kr/vehicles/seltos/summary.html",
        "Sorento": "https://www.kia.com/kr/vehicles/sorento/summary.html",
        "Carnival": "https://www.kia.com/kr/vehicles/carnival/summary.html",
        "Sportage": "https://www.kia.com/kr/vehicles/sportage/summary.html",
        "EV9": "https://www.kia.com/kr/vehicles/ev9/summary.html"
    }
}

# 보험사 정보
insurance_companies = {
    "삼성화재": {
        "logo": "https://www.samsungfire.com/resources/images/common/ci.png",
        "description": "국내 최대 자동차 보험사로 다양한 할인 혜택 제공",
        "strengths": ["신차보험 특화", "할인율 높음", "사고처리 빠름"],
        "contact": "1588-5114",
        "discounts": {
            "신차": 0.1,
            "무사고": 0.15,
            "친환경차": 0.05,
            "다중할인": 0.05
        }
    },
    "DB손해보험": {
        "logo": "https://www.idirect.co.kr/image/company/db_logo.png",
        "description": "친환경 차량 특화 보험상품 보유",
        "strengths": ["친환경차 특화", "보험료 할인 다양", "24시간 긴급출동"],
        "contact": "1588-5656",
        "discounts": {
            "신차": 0.05,
            "무사고": 0.1,
            "친환경차": 0.15,
            "다중할인": 0.03
        }
    },
    "현대해상": {
        "logo": "https://www.hi.co.kr/images/common/ci.png",
        "description": "현대자동차와 연계된 특화 보험상품",
        "strengths": ["현대차 특화", "렌터카 연계", "AS 지원"],
        "contact": "1588-5656",
        "discounts": {
            "신차": 0.07,
            "무사고": 0.12,
            "친환경차": 0.1,
            "다중할인": 0.04
        }
    },
    "KB손해보험": {
        "logo": "https://www.kbinsure.co.kr/resources/images/common/ci.png",
        "description": "전통의 안정적인 보험 서비스",
        "strengths": ["안정성 높음", "금융연계상품 다양", "고객만족도 높음"],
        "contact": "1544-0114",
        "discounts": {
            "신차": 0.05,
            "무사고": 0.1,
            "친환경차": 0.08,
            "다중할인": 0.03
        }
    },
    "메리츠화재": {
        "logo": "https://www.meritzfire.com/resources/images/common/ci.png",
        "description": "젊은 층을 위한 혁신적인 보험상품",
        "strengths": ["디지털 플랫폼 강점", "보험료 저렴", "청년할인"],
        "contact": "1588-9600",
        "discounts": {
            "신차": 0.08,
            "무사고": 0.12,
            "친환경차": 0.07,
            "다중할인": 0.04
        }
    }
}

# 클러스터별 보험 추천 매핑
insurance_recommendations = {
    0: ["삼성화재", "메리츠화재"],  # 합리적 선택을 중시하는 고객
    1: ["DB손해보험", "현대해상"],  # 프리미엄 고객
    2: ["DB손해보험", "KB손해보험"],  # 가족 중심 고객
    3: ["삼성화재", "KB손해보험"],  # 비즈니스 고객
    4: ["현대해상", "메리츠화재"],  # 젊은 고객
    5: ["메리츠화재", "KB손해보험"]  # 첫 차 구매 고객
}

# 보험 유형 설명
insurance_types = {
    "기본보험": {
        "coverage": ["대인배상 무한", "대물배상 1억원", "자기신체사고 3천만원"],
        "price_range": "월 5~10만원",
        "base_price": 80000
    },
    "표준보험": {
        "coverage": ["대인배상 무한", "대물배상 2억원", "자기신체사고 5천만원", "자차보험"],
        "price_range": "월 10~20만원",
        "base_price": 150000
    },
    "프리미엄보험": {
        "coverage": ["대인배상 무한", "대물배상 3억원", "자기신체사고 1억원", 
                    "자차보험", "긴급출동서비스", "렌터카 지원"],
        "price_range": "월 20~30만원",
        "base_price": 250000
    },
    "친환경특화보험": {
        "coverage": ["배터리 보장", "충전기 사고 보상", "대인배상 무한", 
                    "대물배상 2억원", "자기신체사고 5천만원"],
        "price_range": "월 15~25만원",
        "base_price": 200000
    }
}

# 클러스터별 차량 추천 이유 매핑 (개선된 버전)
vehicle_recommendations = {
    '현대': {
        "Avante (CN7 N)": {
            0: {
                "title": "🌟 합리적인 선택을 원하는 당신을 위한 Avante CN7 N",
                "specs": {
                    "엔진": "1.6L 가솔린",
                    "연비": "15.2km/L",
                    "출력": "123마력",
                    "트렁크": "475L",
                    "안전등급": "Euro NCAP 5성급"
                },
                "추천이유": [
                    "💰 **가성비 최고**: 동급 최저 유지비 (월 평균 12만원)",
                    "🛡️ **안전 최적화**: 6에어백 + 긴급제동 시스템 기본 탑재",
                    "🚗 **주차 편의**: 후방 카메라 & 후측방 경고 시스템",
                    "🔄 **할부 혜택**: 36개월 무이자 할부 가능"
                ],
                "고객유형": "40~50대 중년층, 첫 차 구매자, 가성비를 중시하는 분",
                "경쟁차종": "기아 K3, 토요타 코롤라 대비 10% 더 낮은 유지비",
                "추천트림": "Smart (가솔린 1.6)",
                "트림가격": "2,475만원",
                "추천옵션": "어반 세이프티 패키지",
                "옵션가격": "132만원",
                "총가격": "2,607만원"
            },
            # ... [이하 생략 - 기존 vehicle_recommendations 내용 유지] ...
        }
    }
}

def display_insurance_recommendation(cluster_id, selected_vehicle, brand):
    """보험 추천 정보 표시 함수"""
    st.title("🚗 맞춤형 자동차 보험 추천")
    
    # 보험사 추천
    recommended_insurances = insurance_recommendations.get(cluster_id, [])
    is_eco_friendly = selected_vehicle in eco_friendly_models.get(brand, [])
    
    st.subheader("🏆 고객님을 위한 최적의 보험사 추천")
    cols = st.columns(len(recommended_insurances))
    
    for idx, insurance in enumerate(recommended_insurances):
        with cols[idx]:
            info = insurance_companies.get(insurance, {})
            st.image(info.get("logo", ""), width=100)
            st.markdown(f"### {insurance}")
            st.markdown(f"**특징**: {info.get('description', '')}")
            
            # 강점 표시
            strengths = "\n".join([f"- {s}" for s in info.get("strengths", [])])
            st.markdown(f"**강점**:\n{strengths}")
            
            # 친환경 차량인 경우 특별 표시
            if is_eco_friendly and insurance == "DB손해보험":
                st.success("✅ 이 보험사는 친환경 차량에 특화된 상품이 있습니다!")
            
            st.markdown(f"**연락처**: {info.get('contact', '')}")
            st.button(f"{insurance} 상담 신청", key=f"ins_btn_{idx}")

    # 보험 유형 추천
    st.subheader("🔍 추천 보험 유형")
    
    if is_eco_friendly:
        insurance_type = "친환경특화보험"
    elif cluster_id in [1, 3]:  # 프리미엄 고객
        insurance_type = "프리미엄보험"
    elif cluster_id in [2, 4]:  # 가족/젊은 고객
        insurance_type = "표준보험"
    else:
        insurance_type = "기본보험"
    
    type_info = insurance_types.get(insurance_type, {})
    
    st.markdown(f"### {insurance_type} (추천)")
    st.markdown(f"**월 예상 보험료**: {type_info.get('price_range', '')}")
    
    # 보장 내용 표시
    coverages = "\n".join([f"- {c}" for c in type_info.get("coverage", [])])
    st.markdown(f"**주요 보장 내용**:\n{coverages}")
    
    # 보험료 계산기
    st.subheader("📊 보험료 예상 계산")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        driving_exp = st.selectbox("운전 경력", ["1년 미만", "1~3년", "3~5년", "5년 이상"], key="driving_exp")
    with col2:
        accident_history = st.selectbox("최근 3년간 사고 이력", ["무사고", "1건", "2건", "3건 이상"], key="accident_history")
    with col3:
        car_age = st.selectbox("차량 연식", ["신차", "1~3년", "3~5년", "5~7년", "7년 이상"], key="car_age")
    
    if st.button("보험료 예상 계산"):
        base_price = type_info.get("base_price", 100000)
        
        # 할인/할증 적용
        price_factors = {
            "driving_exp": {
                "1년 미만": 1.2,
                "1~3년": 1.1,
                "3~5년": 1.0,
                "5년 이상": 0.9
            },
            "accident_history": {
                "무사고": 0.85,
                "1건": 1.0,
                "2건": 1.2,
                "3건 이상": 1.5
            },
            "car_age": {
                "신차": 1.1,
                "1~3년": 1.0,
                "3~5년": 0.95,
                "5~7년": 0.9,
                "7년 이상": 0.8
            }
        }
        
        # 기본 가격에 각 요소 적용
        final_price = base_price
        final_price *= price_factors["driving_exp"][driving_exp]
        final_price *= price_factors["accident_history"][accident_history]
        final_price *= price_factors["car_age"][car_age]
        
        # 보험사별 할인 적용
        insurance_prices = {}
        for ins in recommended_insurances:
            ins_info = insurance_companies.get(ins, {})
            discounts = ins_info.get("discounts", {})
            temp_price = final_price
            
            # 할인 적용
            if is_eco_friendly:
                temp_price *= (1 - discounts.get("친환경차", 0))
            if accident_history == "무사고":
                temp_price *= (1 - discounts.get("무사고", 0))
            if car_age == "신차":
                temp_price *= (1 - discounts.get("신차", 0))
            
            # 다중 할인 추가
            temp_price *= (1 - discounts.get("다중할인", 0))
            
            insurance_prices[ins] = int(temp_price)
        
        # 결과 표시
        st.success(f"월 예상 보험료 범위: {min(insurance_prices.values()):,}원 ~ {max(insurance_prices.values()):,}원")
        
        # 보험사별 상세 가격 비교
        st.subheader("🔍 보험사별 예상 보험료 비교")
        for ins, price in insurance_prices.items():
            st.markdown(f"**{ins}**: {price:,}원")
            
            # 할인 정보 표시
            discount_info = []
            ins_discounts = insurance_companies.get(ins, {}).get("discounts", {})
            
            if is_eco_friendly and ins_discounts.get("친환경차", 0) > 0:
                discount_info.append(f"친환경차 {ins_discounts['친환경차']*100:.0f}% 할인")
            if accident_history == "무사고" and ins_discounts.get("무사고", 0) > 0:
                discount_info.append(f"무사고 {ins_discounts['무사고']*100:.0f}% 할인")
            if car_age == "신차" and ins_discounts.get("신차", 0) > 0:
                discount_info.append(f"신차 {ins_discounts['신차']*100:.0f}% 할인")
            if len(discount_info) > 1 and ins_discounts.get("다중할인", 0) > 0:
                discount_info.append(f"다중할인 {ins_discounts['다중할인']*100:.0f}% 추가")
            
            if discount_info:
                st.markdown(f"적용된 할인: {', '.join(discount_info)}")
            
            st.markdown("---")

def run_insurance_prediction():
    """보험 예측을 실행하는 함수"""
    if "Cluster" not in st.session_state or "selected_vehicle" not in st.session_state or "brand" not in st.session_state:
        st.warning("먼저 고객 정보 입력과 차량 선택을 완료해주세요.")
        return
    
    cluster_id = st.session_state["Cluster"]
    selected_vehicle = st.session_state["selected_vehicle"]
    brand = st.session_state["brand"]
    
    display_insurance_recommendation(cluster_id, selected_vehicle, brand)

def display_vehicle_recommendation(brand, model, cluster_id):
    """개선된 차량 추천 정보 표시 함수 - 시각적으로 매력적인 디자인"""
    recommendation = vehicle_recommendations.get(brand, {}).get(model, {}).get(cluster_id, {})
    
    if not recommendation:
        st.warning("이 차량에 대한 추천 정보가 없습니다.")
        return
    
    # 차량 이미지 표시 (가운데 정렬)
    vehicle_image = vehicle_images.get(model, get_abs_path("img/default.png"))
    if vehicle_image.exists():
        col1, col2, col3 = st.columns([1, 6, 1])
        with col2:
            st.image(str(vehicle_image), use_container_width=True)
    else:
        st.warning("차량 이미지를 불러올 수 없습니다.")
    
    # 타이틀 섹션 (카드 스타일)
    with st.container():
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #6e48aa 0%, #9d50bb 100%);
            padding: 20px;
            border-radius: 10px;
            color: white;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        ">
            <h2 style="color: white; text-align: center; margin: 0;">{recommendation.get('title', model)}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)  # 공백 추가
    
    # 2열 레이아웃: 사양과 추천 이유
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # 주요 사양 카드
        with st.expander("🚀 **주요 사양**", expanded=True):
            specs = recommendation.get("specs", {})
            for key, value in specs.items():
                st.markdown(f"""
                <div style="
                    background: #f8f9fa;
                    padding: 12px;
                    border-radius: 8px;
                    margin-bottom: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                ">
                    <strong>{key}</strong>: {value}
                </div>
                """, unsafe_allow_html=True)
        
        # 가격 정보 카드
        with st.expander("💰 **가격 정보**", expanded=True):
            st.markdown(f"""
            <div style="
                background: #f8f9fa;
                padding: 12px;
                border-radius: 8px;
                margin-bottom: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            ">
                <strong>추천 트림</strong>: {recommendation.get('추천트림', '정보 없음')}
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="
                background: #f8f9fa;
                padding: 12px;
                border-radius: 8px;
                margin-bottom: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            ">
                <strong>트림 가격</strong>: {recommendation.get('트림가격', '정보 없음')}
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="
                background: #f8f9fa;
                padding: 12px;
                border-radius: 8px;
                margin-bottom: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            ">
                <strong>추천 옵션</strong>: {recommendation.get('추천옵션', '정보 없음')} (+{recommendation.get('옵션가격', '0')})
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="
                background: #e9f7ef;
                padding: 12px;
                border-radius: 8px;
                margin-bottom: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                border-left: 4px solid #2ecc71;
            ">
                <strong>총 예상 가격</strong>: {recommendation.get('총가격', '정보 없음')}
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # 추천 이유 섹션 (아이콘과 함께)
        with st.expander("✨ **추천 이유**", expanded=True):
            reasons = recommendation.get("추천이유", [])
            for reason in reasons:
                # **텍스트** 를 <strong>텍스트</strong>로 바꿔주는 처리
                reason_html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', reason)
                st.markdown(f"""
                <div style="
                    background: #f0f8ff;
                    padding: 12px;
                    border-radius: 8px;
                    margin-bottom: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                    border-left: 4px solid #3498db;
                ">
                    {reason_html}
                </div>
                """, unsafe_allow_html=True)
        
        # 고객 유형 및 경쟁 차종
        with st.expander("🎯 **추천 고객 유형**", expanded=True):
            st.markdown(f"""
            <div style="
                background: #fff4e6;
                padding: 12px;
                border-radius: 8px;
                margin-bottom: 12px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                border-left: 4px solid #e67e22;
            ">
                {recommendation.get('고객유형', '정보 없음')}
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="
                background: #e8f4f8;
                padding: 12px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                border-left: 4px solid #2980b9;
            ">
                <strong>경쟁 차종 비교</strong>: {recommendation.get('경쟁차종', '정보 없음')}
            </div>
            """, unsafe_allow_html=True)
    
    # 차량 상세 정보 링크 (버튼 스타일)
    vehicle_link = vehicle_links.get(brand, {}).get(model, "#")
    st.markdown(f"""
    <div style="text-align: center; margin-top: 20px;">
        <a href="{vehicle_link}" target="_blank" style="
            display: inline-block;
            padding: 12px 24px;
            background: linear-gradient(135deg, #3498db 0%, #2c3e50 100%);
            color: white;
            text-decoration: none;
            border-radius: 30px;
            font-weight: bold;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
            🔗 {model} 공식 사이트에서 자세히 보기
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    # 구분선 추가
    st.markdown("---")

# 모델 로드 함수
def load_models(brand):
    model_dir = Path(__file__).parent.parent / "models_mini1"

    if brand == '현대':
        segment_model_path = model_dir / "gb_model_hs.pkl"
        clustering_model_path = model_dir / "gb_pipeline_hc.pkl"
    elif brand == '기아':
        segment_model_path = model_dir / "gb_model_ks.pkl"
        clustering_model_path = model_dir / "rf_pipeline_kc.pkl"

    if not segment_model_path.exists():
        raise FileNotFoundError(f"[❌ 경고] 세그먼트 모델이 존재하지 않습니다: {segment_model_path}")
    if not clustering_model_path.exists():
        raise FileNotFoundError(f"[❌ 경고] 클러스터링 모델이 존재하지 않습니다: {clustering_model_path}")

    segment_model = joblib.load(segment_model_path)
    clustering_model = joblib.load(clustering_model_path)
    return segment_model, clustering_model

def run_input_step1(brand):
    st.title(f'📋 {brand} 고객 정보 입력')
    segment_model, clustering_model = load_models(brand)
    
    st.info(f"""
            #### {brand} 고객 정보를 입력하고 예측 버튼을 눌러주세요.
            #### 모든 항목은 필수입니다.
            """)

    with st.form(key="customer_info_form"):
        col1, col2 = st.columns([1, 1])
        with col1:
            성별 = st.selectbox("성별 선택", ["남", "여"])
            
            today = datetime.today()
            year_20_years_ago = today.replace(year=today.year - 20)
            if year_20_years_ago.month == 2 and year_20_years_ago.day == 29:
                year_20_years_ago = year_20_years_ago.replace(day=28)
            
            생년월일 = st.date_input("생년월일 입력", min_value=datetime(1900, 1, 1), max_value=year_20_years_ago)
            if 생년월일:
                today = datetime.today()
                연령 = today.year - 생년월일.year - ((today.month, today.day) < (생년월일.month, 생년월일.day))
            
            거래금액 = st.number_input("고객 예산 입력", min_value=10000000, step=1000000)
            구매빈도 = st.number_input("제품 구매 빈도 입력", min_value=1, step=1, value=1)

        with col2:
            차량구분 = st.selectbox("희망 차량 구분 선택", ["준중형 세단", "중형 세단", "대형 세단", "SUV", "픽업트럭"])
            거래방식 = st.selectbox("거래 방식 선택", ["카드", "현금", "계좌이체"])
            구매한제품 = st.selectbox("구입 희망 모델 선택", list(launch_dates[brand].keys()))
            제품구매날짜 = st.date_input("제품 구매 날짜 입력")

        # 버튼 2개를 나란히 배치하기 위한 columns
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("예측하기")
        with col2:
            insurance_submitted = st.form_submit_button("보험 확인하기")

        if submitted:
            if not (성별 and 생년월일 and 거래금액 and 구매빈도 and 차량구분 and 거래방식 and 구매한제품 and 제품구매날짜):
                st.error("⚠️ 모든 항목을 입력해야 합니다!")
                st.stop()

            today = datetime.today()
            연령 = today.year - 생년월일.year - ((today.month, today.day) < (생년월일.month, 생년월일.day))

            # 세션 상태 저장
            st.session_state.update({
                "성별": 성별,
                "생년월일": 생년월일,
                "거래금액": 거래금액,
                "구매빈도": 구매빈도,
                "차량구분": 차량구분,
                "거래방식": 거래방식,
                "구매한제품": 구매한제품,
                "제품구매날짜": 제품구매날짜,
                "연령": 연령,
                "제품구매빈도": 구매빈도,
                "제품출시년월": launch_dates[brand].get(구매한제품),
                "친환경차": "여" if 구매한제품 in eco_friendly_models[brand] else "부"
            })

            # 1단계: 세그먼트 분류
            segment_input_data = pd.DataFrame([[거래방식, st.session_state["제품출시년월"], 제품구매날짜, 거래금액, 구매빈도]],
                                           columns=['거래 방식', '제품 출시년월', '제품 구매 날짜', '거래 금액', '제품 구매 빈도'])
            
            고객세그먼트 = segment_model.predict(segment_input_data)[0]
            st.session_state["고객세그먼트"] = 고객세그먼트

            # 2단계: 클러스터링 분류
            clustering_input_data = pd.DataFrame([[성별, 차량구분, 거래방식, st.session_state["제품출시년월"], 
                                                 제품구매날짜, 고객세그먼트, st.session_state["친환경차"], 
                                                 연령, 거래금액, 구매빈도]],
                                               columns=['성별', '차량구분', '거래 방식', '제품 출시년월', 
                                                       '제품 구매 날짜', '고객 세그먼트', '친환경차',
                                                       '연령', '거래 금액', '제품 구매 빈도'])
            
            cluster_id = clustering_model.predict(clustering_input_data)[0]
            st.session_state["Cluster"] = cluster_id

            st.session_state["step"] = 2
            st.session_state["recommended_vehicles"] = brand_recommendations[brand].get(cluster_id, [])
            st.rerun()
            
        if insurance_submitted:
            run_insurance_prediction()  # 보험 예측 함수 실행

def step2_vehicle_selection(brand):
    st.title(f"🚗 {brand} 추천 차량 선택")

    # 세션 상태에서 결과 값 가져오기
    st.subheader("📊 고객 분석 결과")
    customer_segment = st.session_state.get("고객세그먼트", "N/A")
    cluster_id = st.session_state.get("Cluster", "N/A")
    age = st.session_state.get("연령", "N/A")
    gender = st.session_state.get("성별", "N/A")
    transaction_amount = st.session_state.get("거래금액", "N/A")
    
    # 결과를 2열 레이아웃으로 표시
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(label="고객 세그먼트", value=f"세그먼트 {customer_segment}")
        st.metric(label="연령", value=f"{age}세")
        st.metric(label="거래 금액", value=f"{transaction_amount:,}원")
    
    with col2:
        st.metric(label="클러스터", value=f"클러스터 {cluster_id}")
        st.metric(label="성별", value=gender)
        st.metric(label="차량 유형", value=st.session_state.get("차량구분", "N/A"))
    
    st.markdown("---")  # 구분선
    
    # 추천 차량 목록
    recommended_vehicles = st.session_state.get("recommended_vehicles", [])
    구매한제품 = st.session_state.get("구매한제품", "")
    selected_vehicle = st.session_state.get("selected_vehicle", "")

    # 구매한 제품이 추천 리스트에 없으면 추가
    if 구매한제품 and 구매한제품 not in recommended_vehicles:
        recommended_vehicles.append(구매한제품)

    # 차량 선택
    default_vehicle = selected_vehicle or 구매한제품 or (recommended_vehicles[0] if recommended_vehicles else "")
    if default_vehicle in recommended_vehicles:
        default_index = recommended_vehicles.index(default_vehicle)
    else:
        default_index = 0

    selected_vehicle = st.selectbox(
        "구입 희망 차량을 선택하세요",
        recommended_vehicles,
        key="vehicle_select_box",
        index=default_index
    )

    if selected_vehicle:
        # 개선된 차량 추천 정보 표시
        display_vehicle_recommendation(brand, selected_vehicle, cluster_id)
    else:
        st.warning("추천 차량이 없습니다. 다시 예측을 시도해 주세요.")

    # 보험 확인 버튼 추가
    if st.button("보험 확인하기"):
        st.session_state["selected_vehicle"] = selected_vehicle
        run_insurance_prediction()
        return

    # 선택 완료 버튼
    if st.button("선택 완료"):
        vehicle_price = vehicle_prices.get(brand, {}).get(selected_vehicle, 0)
        st.session_state["거래금액"] = vehicle_price
        st.session_state["selected_vehicle"] = selected_vehicle
        st.success(f"{selected_vehicle} 선택 완료! 이제 고객 정보를 저장합니다.")
        st.session_state["step"] = 3
        st.rerun()

def step3_customer_data_storage():
    st.title("📝 고객 정보 입력 및 저장")

    with st.form(key="customer_info_form"):
        이름 = st.text_input("이름")
        휴대폰번호 = st.text_input("휴대폰 번호 입력", placeholder="필수입니다.")
        이메일 = st.text_input("이메일 입력", placeholder="필수입니다.")
        주소 = st.text_input("주소")
        아이디 = st.text_input("아이디")
        가입일 = st.date_input("가입일")

        submit_button = st.form_submit_button("고객정보 저장하기")

        if submit_button:
            # 유효성 검사
            휴대폰번호 = re.sub(r'[^0-9]', '', 휴대폰번호)
            has_error = False

            if not (이름 and 휴대폰번호 and 이메일 and 주소 and 아이디 and 가입일):
                st.error("⚠️ 모든 항목을 입력해야 합니다!")
                has_error = True

            if not re.fullmatch(r"\d{11}", 휴대폰번호):
                st.error("⚠️ 휴대폰 번호는 11자리 숫자여야 합니다. (예: 01012345678)")
                has_error = True

            if "@" not in 이메일 or "." not in 이메일:
                st.error("⚠️ 이메일 주소 형식이 올바르지 않습니다. '@'와 '.'을 포함해야 합니다.")
                has_error = True

            if has_error:
                st.stop()

            # 세션 상태 저장
            st.session_state.update({
                "name": 이름,
                "phone": 휴대폰번호,
                "email": 이메일,
                "address": 주소,
                "id": 아이디,
                "registration_date": 가입일
            })

            # 데이터 저장 로직
            save_customer_data()
            
            # 세션 초기화 및 다음 단계로
            st.session_state["step"] = 1
            time.sleep(2)
            st.rerun()

def save_customer_data():
    """고객 데이터 저장 함수"""
    brand = st.session_state.get("brand", "")
    
    # 필요한 정보 가져오기
    customer_data = {
        "이름": st.session_state.get("name", ""),
        "생년월일": st.session_state.get("생년월일", ""),
        "연령": st.session_state.get("연령", ""),
        "성별": st.session_state.get("성별", ""),
        "휴대폰번호": st.session_state.get("phone", ""),
        "이메일": st.session_state.get("email", ""),
        "주소": st.session_state.get("address", ""),
        "아이디": st.session_state.get("id", ""),
        "가입일": st.session_state.get("registration_date", ""),
        "차량구분": st.session_state.get("차량구분", ""),
        "구매한 제품": st.session_state.get("selected_vehicle", ""),
        "친환경차": "여" if st.session_state.get("selected_vehicle", "") in eco_friendly_models.get(brand, []) else "부",
        "제품 구매 날짜": st.session_state.get("제품구매날짜", ""),
        "거래 금액": st.session_state.get("거래금액", ""),
        "거래 방식": st.session_state.get("거래방식", ""),
        "제품 구매 빈도": st.session_state.get("제품구매빈도", ""),
        "제품 출시년월": st.session_state.get("제품출시년월", ""),
        "고객세그먼트": st.session_state.get("고객세그먼트", ""),
        "Cluster": st.session_state.get("Cluster", "")
    }

    # 데이터프레임 생성
    full_data = pd.DataFrame([customer_data])

    # 파일 저장 경로
    file_path = Path(__file__).parent.parent.parent.parent / "data" / f"{brand}_고객데이터_신규입력용.csv"
    os.makedirs(file_path.parent, exist_ok=True)
    
    # CSV 파일에 저장 (기존 파일이 있으면 추가, 없으면 새로 생성)
    full_data.to_csv(file_path, mode='a', header=not file_path.exists(), index=False, encoding='utf-8-sig')

    # 문자 발송
    send_sms_notification()

    # 이메일 발송
    if brand == '현대' or brand == '기아':
        promo_email.send_welcome_email(
            st.session_state.get("email", ""),
            st.session_state.get("name", ""),
            st.session_state.get("id", ""),
            st.session_state.get("registration_date", "")
        )
        st.success("이메일이 성공적으로 발송되었습니다.")

def send_sms_notification():
    """SMS 알림 발송 함수"""
    clicksend_username = st.secrets["CLICKSEND"]["CLICKSEND_USERNAME"]
    clicksend_api_key = st.secrets["CLICKSEND"]["CLICKSEND_API_KEY"]
    to_number = "+82" + st.session_state.get("phone", "")[1:]
    message_body = f"""안녕하세요, {st.session_state.get("name", "")}님! 
{st.session_state.get("brand", "")} 자동차에서 보내드리는 메시지입니다. 
멤버십 가입을 축하드리며, 다양한 혜택과 서비스를 경험해보세요!"""

    try:
        response = requests.post(
            "https://rest.clicksend.com/v3/sms/send",
            headers={
                "Authorization": f"Basic {base64.b64encode(f'{clicksend_username}:{clicksend_api_key}'.encode()).decode()}",
                "Content-Type": "application/json"
            },
            json={"messages": [{"source": "sdk", "body": message_body, "to": to_number}]}
        )
        st.success("문자가 성공적으로 발송되었습니다.")
    except Exception as e:
        st.error("문자 발송에 실패했습니다.")
        print("Error sending SMS:", e)

def run_input_customer_info():
    if "step" not in st.session_state:
        st.session_state["step"] = 1
    brand = st.session_state.get("brand", "현대")
    
    if st.session_state["step"] == 1:
        run_input_step1(brand)
    elif st.session_state["step"] == 2:
        step2_vehicle_selection(brand)
    elif st.session_state["step"] == 3:
        step3_customer_data_storage()

# 메인 실행 코드
if __name__ == "__main__":
    st.set_page_config(
        page_title="자동차 보험 추천 시스템",
        page_icon="🚗",
        layout="wide"
    )
    
    # 브랜드 선택 (세션 상태에 저장)
    if "brand" not in st.session_state:
        st.session_state["brand"] = "현대"
    
    # 사이드바에 브랜드 선택 옵션
    with st.sidebar:
        st.title("🚗 자동차 브랜드 선택")
        brand_option = st.radio(
            "브랜드를 선택하세요",
            ["현대", "기아"],
            index=0 if st.session_state["brand"] == "현대" else 1
        )
        
        if brand_option != st.session_state["brand"]:
            st.session_state["brand"] = brand_option
            st.session_state["step"] = 1
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 시스템 정보")
        st.markdown("이 시스템은 고객 프로필 분석을 통해 최적의 차량과 보험을 추천합니다.")
    
    # 메인 콘텐츠 실행
    run_input_customer_info()