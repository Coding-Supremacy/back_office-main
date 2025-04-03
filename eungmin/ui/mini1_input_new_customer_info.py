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

import ui.mini1_promo_email

def get_abs_path(relative_path):
    """상대 경로를 절대 경로로 변환"""
    return Path(__file__).parent.parent / relative_path

# 모델과 출시 년월 데이터
launch_dates = {
    '현대':{
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

    '기아' : {
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

# 현대 친환경차 모델 목록
eco_friendly_models = {'현대': [
    'NEXO (FE)', 'Avante (CN7 HEV)', 'Grandeur (GN7 HEV)', 
    'Tucson (NX4 PHEV)', 'IONIQ 6 (CE)', 'Santa-Fe (MX5 PHEV)'
],
'기아':['EV6', 'EV9']}

# 클러스터별 차량 추천 모델 목록
brand_recommendations = {
    '현대': {
        0: ['Avante (CN7 N)', "G70 (IK)", "Tucson (NX4 PHEV)"],
        1: ["IONIQ 6 (CE)", "Grandeur (GN7 HEV)", "NEXO (FE)"],
        2: ["IONIQ 6 (CE)", "Grandeur (GN7 HEV)", "Santa-Fe (MX5 PHEV)"],
        3: ['Avante (CN7 N)',"Tucson (NX4 PHEV)", "G90 (HI)"],
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

# 예측을 위한 입력값을 처리하는 함수
def run_input_customer_info():
    if "step" not in st.session_state:
        st.session_state["step"] = 1  # 첫 번째 단계로 시작
    if st.session_state["step"] == 1:
        run_input_step1()  # 고객 정보 입력
    elif st.session_state["step"] == 2:
        step2_vehicle_selection()  # 차량 선택
    elif st.session_state["step"] == 3:
        step3_customer_data_storage()  # 고객 정보 저장

#모델 로드 함수
def load_models(brand):
    model_dir = Path(__file__).parent.parent / "mini1_model"

    # 디버깅용 출력
    print(f"📌 모델 디렉토리 확인: {model_dir.resolve()}")
    print(f"📌 디렉토리 존재 여부: {model_dir.exists()}")

    if brand == '현대':
        segment_model_path = model_dir / "gb_model_hs.pkl"
        clustering_model_path = model_dir / "gb_pipeline_hc.pkl"
    elif brand == '기아':
        segment_model_path = model_dir / "gb_model_ks.pkl"
        clustering_model_path = model_dir / "rf_pipeline_kc.pkl"

    # 모델 파일 존재 여부 확인
    print(f"📁 Segment 모델 경로: {segment_model_path}")
    print(f"📁 Clustering 모델 경로: {clustering_model_path}")
    print(f"✅ Segment 모델 존재?: {segment_model_path.exists()}")
    print(f"✅ Clustering 모델 존재?: {clustering_model_path.exists()}")

    # 예외 발생 전에 명확하게 알려주기
    if not segment_model_path.exists():
        raise FileNotFoundError(f"[❌ 경고] 세그먼트 모델이 존재하지 않습니다: {segment_model_path}")
    if not clustering_model_path.exists():
        raise FileNotFoundError(f"[❌ 경고] 클러스터링 모델이 존재하지 않습니다: {clustering_model_path}")

    segment_model = joblib.load(segment_model_path)
    clustering_model = joblib.load(clustering_model_path)
    return segment_model, clustering_model

# 예측을 위한 입력값을 처리하는 함수
def run_input_customer_info():
    # app.py에서 브랜드 선택을 처리하므로 step 0은 필요 없음
    if "step" not in st.session_state:
        st.session_state["step"] = 1  # 브랜드 선택 후 바로 고객 정보 입력 단계로
    # app.py에서 브랜드 선택을 이미 했으므로, brand는 session_state에서 가져옴
    brand = st.session_state.get("brand", "현대")  # 기본값은 현대
    
    if st.session_state["step"] == 1:
        run_input_step1(brand)  # 브랜드 정보를 인자로 전달
    elif st.session_state["step"] == 2:
        step2_vehicle_selection(brand)  # 브랜드 정보를 인자로 전달
    elif st.session_state["step"] == 3:
        step3_customer_data_storage()

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

        submitted = st.form_submit_button("예측하기")
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




# 차량 추천 (친환경차 여부 포함)
def get_recommended_vehicles(cluster_id):
    recommended_vehicles = []

    if cluster_id == 0:
        recommended_vehicles = [
            'Avante (CN7 N)', "G70 (IK)", "Tucson (NX4 PHEV)"
        ]
    elif cluster_id == 1:
        recommended_vehicles = [
            "IONIQ 6 (CE)", "Grandeur (GN7 HEV)", "NEXO (FE)"
        ]
    elif cluster_id == 2:
        recommended_vehicles = [
            "IONIQ 6 (CE)", "Grandeur (GN7 HEV)", "Santa-Fe (MX5 PHEV)"
        ]
    elif cluster_id == 3:
        recommended_vehicles = [
            'Avante (CN7 N)',"Tucson (NX4 PHEV)", "G90 (HI)"
        ]
    elif cluster_id == 4:
        recommended_vehicles = [
            "IONIQ 6 (CE)", "Santa-Fe (MX5 PHEV)", "Tucson (NX4 PHEV)"
        ]
    elif cluster_id == 5:
        recommended_vehicles = [
            "Avante (CN7 N)", "G70 (IK)", "Tucson (NX4 PHEV)"
        ]
    return recommended_vehicles

# 2단계: 고객이 모델 선택 후 인적 사항 입력
def step2_vehicle_selection(brand):
    st.title(f"🚗 {brand}추천 차량 선택")

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
    cluster_id = st.session_state.get("Cluster")
    recommended_vehicles = st.session_state.get("recommended_vehicles", [])
    구매한제품 = st.session_state.get("구매한제품", "")
    selected_vehicle = st.session_state.get("selected_vehicle", "")

    # 구매한 제품이 추천 리스트에 없으면 추가
    if 구매한제품 and 구매한제품 not in recommended_vehicles:
        recommended_vehicles.append(구매한제품)

    # 기본 경로를 정의
    IMAGE_BASE_PATH = 'mini2_img/'
    # 최종 딕셔너리 생성
    vehicle_images = {
        model: get_abs_path(f"{IMAGE_BASE_PATH}{model}.png")
        for brand_models in launch_dates.values()
        for model in brand_models
    }
    # 차량에 대한 기본적인 추천 멘트
    basic_recommendations = {
        '현대': {
            "Avante (CN7 N)": "Avante (CN7 N)은 뛰어난 성능과 스타일을 자랑하는 최신형 세단입니다. 실용성과 세련된 디자인을 갖춘 완벽한 선택입니다.",
            "NEXO (FE)": "NEXO는 친환경적인 수소차로, 연료비 절감과 환경을 생각하는 고객에게 안성맞춤입니다. 고급스러움과 친환경성을 동시에 제공합니다.",
            "G80 (RG3)": "G80은 고급스러운 세단으로 품격 있는 운전 경험을 제공합니다. VIP 고객님에게 어울리는 차량입니다.",
            "G90 (HI)": "G90은 프리미엄 세단으로, 고급스러움과 편안함을 제공합니다. 모든 세부 사항이 완벽하게 설계되어 있어 최고의 만족감을 선사합니다.",
            "IONIQ 6 (CE)": "IONIQ 6는 첨단 기술과 세련된 디자인을 갖춘 전기차입니다. 친환경적인 드라이빙을 원하시는 고객님께 적합합니다.",
            "Tucson (NX4 PHEV)": "Tucson은 플러그인 하이브리드 SUV로, 환경을 고려하면서도 강력한 성능을 제공합니다. 연비 효율성이 뛰어난 차량입니다.",
            "Grandeur (GN7 HEV)": "Grandeur는 고급스러움과 실용성을 동시에 제공합니다. 하이브리드 모델로 연비가 뛰어나고, 가격대비 좋은 선택입니다.",
            "G70 (IK)": "G70은 고급 세단으로, 가격대가 적당하면서도 고급스러운 느낌을 줄 수 있는 차량입니다. 세련된 디자인을 갖추고 있습니다.",
            "Santa-Fe (MX5 PHEV)": "Santa-Fe PHEV는 플러그인 하이브리드 SUV로, 친환경을 고려하면서도 넓은 공간과 뛰어난 성능을 자랑하는 선택입니다.",
            "Avante (CN7 HEV)": "친환경차 선호도가 높은 고객님께 Avante (CN7 HEV)! 하이브리드 모델로 연비 효율성을 자랑하며, 친환경적인 선택을 제공합니다."
        },
        '기아': {
            "K3": "K3는 세련된 디자인과 실용성을 겸비한 준중형 세단으로, 합리적인 가격대비 뛰어난 성능을 제공합니다.",
            "K5": "K5는 스포티한 디자인과 역동적인 주행 성능을 갖춘 중형 세단으로, 젊은 감각을 원하는 분들께 추천합니다.",
            "EV6": "EV6는 기아의 최신 전기차 기술이 집약된 크로스오버 SUV로, 혁신적인 디자인과 뛰어난 주행 거리가 특징입니다.",
            "Telluride": "Telluride는 미국 시장을 겨냥한 대형 SUV로, 웅장한 디자인과 풍부한 사양이 특징입니다.",
            "Seltos": "Seltos는 젊고 활동적인 라이프스타일에 맞는 소형 SUV로, 개성 있는 디자인과 다양한 컬러 옵션이 매력적입니다.",
            "Sorento": "Sorento는 프리미엄 감성과 실용성을 모두 갖춘 중대형 SUV로, 고급스러운 주행 경험을 제공합니다.",
            "Carnival": "Carnival은 뛰어난 실내 공간과 편의성을 자랑하는 대형 MPV로, 가족 단위 고객에게 최적화된 모델입니다.",
            "Sportage": "Sportage는 기아의 대표 중형 SUV로, 세련된 디자인과 첨단 안전 사양을 자랑합니다.",
            "EV9": "EV9은 기아의 플래그십 전기 SUV로, 고급스러움과 첨단 기술이 결합된 모델입니다."
        }
    }

    # 차량 링크 매핑
    vehicle_links = {"현대":{
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
    "기아":{}
    }
    # 차량 가격 매핑
    vehicle_prices = {
        '현대': {
            "Avante (CN7 N)": 19640000,
            "NEXO (FE)": 69500000,
            "G80 (RG3)": 82750000,
            "G90 (HI)": 129600000,
            "IONIQ 6 (CE)": 46950000,
            "Tucson (NX4 PHEV)": 27290000,
            "Grandeur (GN7 HEV)": 37110000,
            "G70 (IK)": 45240000,
            "Santa-Fe (MX5 PHEV)": 34920000,
            "Avante (CN7 HEV)": 33090000
        },
        '기아': {
        "EV9": 77000000,
        "K5": 35460000,
        "EV6": 52600000,
        "Sorento": 38990000,
        "Sportage": 32220000,
        "Carnival": 38960000,
        "Seltos": 25720000,
        "K3": 22110000,
        "Telluride": 49966000,
        }
    }


    # 클러스터별 차량 추천 이유 매핑
    vehicle_recommendations = {'현대':{
        "Avante (CN7 N)": {
            0: {
            "설명": "1.6L 가솔린 엔진의 경제적 준중형 세단으로, 연비 15.2km/L의 효율성을 자랑합니다. 6에어백과 스마트스트림 엔진이 적용되어 안전성과 연비를 동시에 잡았으며, 475L의 넉넉한 트렁크 공간으로 가족용으로도 적합합니다.",
            "추천트림": "Smart (가솔린 1.6)",
            "트림가격": "2,475",
            "추천옵션": "어반 세이프티 패키지",
            "옵션가격": "132",
            "총가격": "2,607",
            "추천이유": "40~50대 중년층이 합리적인 가격대와 현대자동차의 안정적인 A/S 네트워크를 믿고 선택할 수 있는 가성비 모델. 저렴한 유지비와 보험료가 부담 없는 것이 장점입니다."
        },
        3: {
            "설명": "고속도로 주행 최적화 세단으로, 하이웨이 드라이빙 어시스트(차선 유지/차간 거리 자동 조절)가 장거리 운전 피로도를 30% 이상 줄여줍니다. 1.6L 가솔린 엔진과 7단 DCT 변속기의 조합으로 고속 주행 시에도 연비 16.1km/L를 유지합니다.",
            "추천트림": "Modern (가솔린 1.6)",
            "트림가격": "2,350",
            "추천옵션": "하이웨이 드라이빙 어시스트",
            "옵션가격": "90",
            "총가격": "2,440",
            "추천이유": "주말마다 고향을 오가거나 자녀 대학 통학을 위해 월 1,500km 이상 장거리 운전하는 50대 중장년층에게 최적. 고속도로 주행 시 안정성과 연비 효율성을 동시에 충족합니다."
        },
        5: {
            "설명": "첫 구매자를 위한 안정적인 세단으로, 후방 카메라와 긴급 제동 시스템이 기본 적용되어 초보 운전자의 주차 및 도심 주행을 지원합니다. 10.25인치 내비게이션과 애플 카플레이 연동으로 편의성을 높였습니다.",
            "추천트림": "Modern (가솔린 1.6)",
            "트림가격": "2,350",
            "추천옵션": "라이트 에디션",
            "옵션가격": "65",
            "총가격": "2,415",
            "추천이유": "40대 중반~50대 초반의 첫 차 구매자들이 부담 없이 선택할 수 있는 진입 장벽 완화 모델. 할부 금융 상품과 5년 무상 A/S가 결합되어 신규 고객 유입에 효과적입니다."
        }
        },
        "G70 (IK)": {
        0: {
            "설명": "2.0L 가솔린 터보 엔진(245마력)을 탑재한 소형 럭셔리 세단. 전자식 컨트롤 댐퍼와 19인치 알로이 휠로 주행 안정성을 높였으며, 퀼팅 난나카 가죽 시트와 12.3인치 클러스터로 고급스러움을 강조했습니다.",
            "추천트림": "Premium (2.0T)",
            "트림가격": "4,250",
            "추천옵션": "베이직 플러스 패키지",
            "옵션가격": "95",
            "총가격": "4,345",
            "추천이유": "50대 이상 중년 남성층이 BMW 3시리즈 대신 합리적인 가격으로 프리미엄 브랜드 체험을 원할 때 선택. 제네시스 전용 콜 서비스와 발코니가 있는 전시장이 고객의 프리미엄 니즈를 충족시킵니다."
        },
        5: {
            "설명": "첫 프리미엄 차량 구매자를 위한 모델로, 2.0L 터보 엔진의 기본 성능은 유지하되 내장재 등 비필수 사양을 간소화했습니다. 주차 보조 패키지(후측방 모니터링/자동 주차)가 도심 생활 편의성을 높입니다.",
            "추천트림": "Standard (2.0T)",
            "트림가격": "3,980",
            "추천옵션": "주차 보조 패키지",
            "옵션가격": "70",
            "총가격": "4,050",
            "추천이유": "45~55세 연령대에서 첫 프리미엄 차량 구매를 고려하는 신규 고객을 위한 전략적 모델. 3년 무상 유지보스와 1:1 전담 상담원 서비스가 구매 결정을 유도합니다."
        }
        },
        "IONIQ 6 (CE)": {
        1: {
            "설명": "AWD 고성능 전기차로 320kW 듀얼 모터 적용 시 0-100km/h 가속 5.1초 가능. 20인치 휠과 스포츠 서스펜션, 가상 엔진 사운드 시스템으로 주행 재미를 극대화했습니다. 400V 초고속 충전 시 18분 충전으로 351km 주행 가능.",
            "추천트림": "Premium (AWD)",
            "트림가격": "6,450",
            "추천옵션": "퍼포먼스 패키지",
            "옵션가격": "290",
            "총가격": "6,740",
            "추천이유": "30대 젊은 남성층이 테슬라 모델 3 퍼포먼스 대안으로 선택. 레이싱 게임 연동 기능과 N 퍼포먼스 튜닝 파츠 호환성을 강점으로 어필합니다."
        },
        2: {
            "설명": "우드 그레인 대시보드와 리사이클드 PET 소재 시트가 적용된 친환경 럭셔리 모델. 공기 청정 모드와 마사지 시트로 여성 운전자의 피로를 줄여주며, 18인치 에어로 휀로 연비 효율성(6.2km/kWh)을 극대화했습니다.",
            "추천트림": "Exclusive (RWD)",
            "트림가격": "5,780",
            "추천옵션": "럭셔리 인테리어 패키지",
            "옵션가격": "240",
            "총가격": "6,020",
            "추천이유": "50대 이상 여성 고객이 메르세데스 EQS의 고가 부담을 줄이면서도 프리미엄 인테리어를 원할 때 적합. 현대카드 마일리지 5% 적립 프로모션과 결합해 마케팅 효과가 높습니다."
        },
        4: {
            "설명": "에어로 다이내믹 디자인으로 Cd 0.21의 초저항 계수를 구현한 전기차. RWD 사양으로 524km의 장거리 주행이 가능하며, 스포츠 서스펜션으로 코너링 안정성을 높였습니다. V2L 기능으로 캠핑 시 전기 사용이 가능합니다.",
            "추천트림": "Exclusive (RWD)",
            "트림가격": "5,780",
            "추천옵션": "스포츠 서스펜션",
            "옵션가격": "120",
            "총가격": "5,900",
            "추천이유": "20~30대 젊은 층이 디자인과 실용성을 동시에 추구할 때 선택. 인스타그램 친화적인 컬러 옵션(디지털 티 그린)과 SNS 인증 이벤트 패키지가 판매 촉진 요소입니다."
        }
        },
        "Grandeur (GN7 HEV)": {
        1: {
            "설명": "1.6L 하이브리드 시스템으로 연비 17.8km/L를 구현한 럭셔리 세단. 열선 스티어링 휠과 통풍 시트가 포함된 VIP 윈터 패키지로 한파 대비를 완벽하게 했으며, 12.3인치 오버헤드 디스플레이로 후석 만족도를 높였습니다.",
            "추천트림": "Inspiration (HEV)",
            "트림가격": "5,120",
            "추천옵션": "VIP 윈터 패키지",
            "옵션가격": "210",
            "총가격": "5,330",
            "추천이유": "55~65세 기업 임원층이 전기차 충전 인프라 불편을 피하면서도 환경 규제 대응을 위해 선택. 리스 상품과 결합 시 세금 혜택이 30% 이상 높아지는 점이 장점입니다."
        },
        2: {
            "설명": "최상위 하이브리드 세단으로, 12스피커의 렉시컨 사운드 시스템과 공기 청정 기능이 탑재된 프레스티지 트림. 헬스 케어 패키지(생체 신호 모니터링/피로도 감지)로 장시간 운전 시 건강을 관리할 수 있습니다.",
            "추천트림": "Prestige (HEV)",
            "트림가격": "5,890",
            "추천옵션": "헬스 케어 패키지",
            "옵션가격": "370",
            "총가격": "6,260",
            "추천이유": "건강과 웰빙을 중시하는 50대 여성 고객층이 선호. 병원 방문용 차량으로 적합하며, 1년 무제한 건강 검진 쿠폰 제공이 구매 결정에 영향을 줍니다."
        }
        },
        "Tucson (NX4 PHEV)": {
        0: {
            "설명": "플러그인 하이브리드 SUV로, 44.5km의 전기 주행 거리와 가솔린 모드 연비 16.4km/L를 동시에 확보. 에코 코스팅 시스템이 신호등 구간에서 에너지 회수 효율을 25% 높여줍니다. 589L의 대용량 트렁크로 캠핑 용품 수납이 용이합니다.",
            "추천트림": "Standard (PHEV)",
            "트림가격": "4,890",
            "추천옵션": "에코 코스팅 시스템",
            "옵션가격": "80",
            "총가격": "4,970",
            "추천이유": "45~55세 중년 남성층이 기존 가솔린 SUV에서 연비 부담을 해소하기 위해 전환하는 모델. 주말 레저 활동(골프/등산) 시 장비 운반용으로도 적합합니다."
        },
        3: {
            "설명": "장거리 주행 최적화 PHEV로, 13.8kWh 대용량 배터리와 2.0L 가솔린 엔진의 조합이 최대 720km의 종합 주행 거리를 제공. 컴포트 플러스 패키지(통풍 시트/어드밴스드 크루즈 컨트롤)로 장시간 운전 피로를 최소화했습니다.",
            "추천트림": "Premium (PHEV)",
            "트림가격": "5,120",
            "추천옵션": "컴포트 플러스",
            "옵션가격": "140",
            "총가격": "5,260",
            "추천이유": "월 2,000km 이상 장거리 출퇴근을 하는 50대 중반 고객을 타깃. 회사 차량 인센티브와 결합 시 PHEV의 세제 혜택이 일반 하이브리드 대비 15% 더 유리합니다."
        },
        5: {
            "설명": "신용카드 할부에 최적화된 PHEV 모델로, 스마트 키 시스템(핸드폰 디지털 키/원격 시동)이 기본 적용되었습니다. 5년 무상 충전권(1,000kWh) 제공으로 초기 운영 비용을 절감할 수 있습니다.",
            "추천트림": "Standard (PHEV)",
            "트림가격": "4,890",
            "추천옵션": "스마트 키 시스템",
            "옵션가격": "60",
            "총가격": "4,950",
            "추천이유": "40대 후반 신규 PHEV 구매자들의 진입 장벽을 낮추기 위한 모델. 현대카드 36개월 무이자 할부와 결합 시 월 137,000원대의 부담 없는 구매가 가능합니다."
        },
        4: {
            "설명": "44.5km 전기주행 가능 PHEV SUV로, 가솔린 모드 연비 16.4km/L의 효율성을 자랑합니다. 589L 대용량 트렁크와 V2L 기능으로 캠핑/레저 활동에 최적화되었으며, 10.25인치 디지털 클러스터와 애플 카플레이 연동으로 편의성을 높였습니다.",
            "추천트림": "Premium (PHEV)",
            "트림가격": "5,120",
            "추천옵션": "스타일 패키지 (20인치 휠 + LED 라이트 그릴)",
            "옵션가격": "150",
            "총가격": "5,270",
            "추천이유": "30대 젊은 고빈도 구매자들이 현금으로 구매 시 경제성을 중시하면서도 친환경 성향을 충족할 수 있는 모델. 주말 레저 활동(캠핑, 골프)과 일상 통근을 동시에 해결하는 실용적인 SUV로, 5년 무상 충전권(1,000kWh) 프로모션으로 초기 유지비 부담 완화."
        }
        },
        "Santa-Fe (MX5 PHEV)": {
        2: {
            "설명": "7인승 PHEV SUV로, 2.5L 가솔린 엔진과 66.9km의 전기 주행 거리를 결합. 캡틴 시트 패키지(2열 통풍 시트/릴렉션 모드)로 대가족 이동 시 편의성을 제공하며, 3열 공간에 어린이 카시트 고정 장치가 기본 장착되었습니다.",
            "추천트림": "Calligraphy (PHEV)",
            "트림가격": "6,350",
            "추천옵션": "캡틴 시트 패키지",
            "옵션가격": "250",
            "총가격": "6,600",
            "추천이유": "다자녀(3명 이상) 가정의 30대 후반~40대 여성 고객이 미니밴 대체용으로 선택. 어린이 승하차 보조 시스템과 결합 시 육아 부담을 40% 이상 줄여줍니다."
        },
        4: {
            "설명": "53km 전기주행 가능 PHEV 모델로, 스타일 패키지(20인치 휠/듀얼 머플러)로 디자인을 강화했습니다. 2열 폴딩 테이블과 12V 전원 포트 4개가 적용되어 젊은 가족의 캠핑/피크닉需求에 대응합니다.",
            "추천트림": "Premium (PHEV)",
            "트림가격": "5,890",
            "추천옵션": "스타일 패키지",
            "옵션가격": "150",
            "총가격": "6,040",
            "추천이유": "친환경 차량을 원하지만 전기차 충전 인프라가 부족한 지방 거주 30대 부부에게 적합. 전기 모드로 일상 이동 시 연료비를 70% 이상 절감할 수 있는 점을 강조합니다."
        }
        },
        "NEXO (FE)": {
        1: {
            "설명": "수소전기차 플래그십 모델로, 6.33kg의 수소 충전으로 666km 주행이 가능합니다. 테크 패키지(AR HUD/리모트 스마트 파킹)가 적용되었으며, 공기 청정 시스템이 실내 미세먼지를 99.9% 제거합니다.",
            "추천트림": "Premium",
            "트림가격": "7,250",
            "추천옵션": "테크 패키지",
            "옵션가격": "320",
            "총가격": "7,570",
            "추천이유": "미래 기술을 선도하는 IT 업계 종사자(25~35세)가 선택. 정부 보조금(4,250만원)과 수소 충전 무료 쿠폰(3년) 제공으로 실구매 가격을 5,000만원대로 낮출 수 있습니다."
        }
        },
        "G90 (HI)": {
        3: {
            "설명": "3.5L 가솔린 터보 엔진(380마력)을 탑재한 플래그십 럭셔리 세단. 리무진 패키지(전동식 뒷좌석/25스피커 뱅앤올룹슨 오디오)가 적용되었으며, 전용 스마트폰 앱으로 뒷좌석 환경(온도/조명/마사지)을 제어할 수 있습니다.",
            "추천트림": "Prestige (3.5T)",
            "트림가격": "8,450",
            "추천옵션": "리무진 패키지",
            "옵션가격": "490",
            "총가격": "8,940",
            "추천이유": "고빈도 비즈니스 이동이 많은 50대 이상 기업 대표층을 타깃. 전용 기사 교육 프로그램과 24시간 VIP 콜 서비스가 제공되어 '이동형 오피스'로 최적화되었습니다."
        }
        }
    },
    '기아': {
        "K5": {
        0: {
            "설명": "2.5L 터보 가솔린 엔진으로 290마력의 강력한 출력을 자랑하는 스포츠 세단. GT 라인 전용 19인치 알로이 휠과 애그레시브 프론트 그릴로 젊은 감성을 완벽히 표현하였습니다. 8단 자동변속기와 스포츠 서스펜션의 조합으로 코너링 안정성과 가속 성능(0-100km/h 6.2초)을 동시에 확보했습니다. 실내에는 GT 전용 레드 스티치 가죽 시트와 메탈 페달로 스포티함을 극대화하였으며, 12.3인치 디지털 계기판이 운전의 즐거움을 더합니다.",
            "추천트림": "2.5T GT",
            "트림가격": "4,120",
            "추천옵션": "스포츠 패키지(스포츠 배기사운드, 전자식 컨트롤 서스펜션)",
            "옵션가격": "220",
            "총가격": "4,340",
            "추천이유": "30대 중반 남성층이 주말 드라이브나 고속도로 주행에서 스포티한 주행 감각을 즐기기에 최적화된 모델입니다. 동급 최고 수준의 290마력 출력과 GT 라인 전용 디자인으로 개성을 강조할 수 있으며, 기아의 10년/10만km 파워트레인 보증으로 장기적인 안심 사용이 가능합니다. 특히 주말 레저 활동이 많은 고객에게 적합하며, 연간 15,000km 이상 주행하는 경우에도 안정적인 성능을 유지합니다."
        },
        2: {
            "설명": "1.6L 하이브리드 시스템으로 도심 연비 18.2km/L를 구현한 고효율 프리미엄 세단. 10.25인치 풀 디지털 클러스터와 헤드업 디스플레이로 모든 운전 정보를 직관적으로 확인할 수 있습니다. 어드밴스드 드라이빙 어시스트(차선유지, 스마트 크루즈 컨트롤)가 기본 적용되어 장거리 운전 피로도를 획기적으로 줄였습니다. 우드 그레인 인테리어와 모카 브라운 컬러의 나파 가죽 시트로 고급스러운 실내 분위기를 연출하였으며, 공기 청정 시스템이 탑재되어 쾌적한 실내 환경을 유지합니다.",
            "추천트림": "HEV 프레스티지",
            "트림가격": "3,950",
            "추천옵션": "테크 패키지(서라운드 뷰 모니터, 현대적 디자인 휠)",
            "옵션가격": "180",
            "총가격": "4,130",
            "추천이유": "환경 가치를 중요하게 생각하는 30대 여성 VIP 고객을 위한 최고급 세단입니다. 전기모터 지원으로 정숙성이 뛰어나 도심 주행에 적합하며, 우아한 디자인과 프리미엄 인테리어가 감성적인 만족도를 높입니다. 기아의 하이브리드 시스템은 5년/10만km 배터리 보증으로 신뢰성을 확보했으며, 월 평균 15만원 이상의 유지비 절감 효과가 기대됩니다. 특히 주말 가족 외출이 잦은 고객에게 적합하며, 어린이 승차 시 안전성을 고려한 다양한 기능이 탑재되었습니다."
        },
        3: {
            "설명": "2.5L 터보 가솔린 엔진과 8단 자동변속기의 완벽한 조합으로 0-100km/h 가속 6.6초를 구현한 고성능 모델. 스포츠 서스펜션과 브렘보 브레이크 시스템이 안정적인 고속 주행을 보장합니다. 12.3인치 3D 클러스터와 Nappa 가죽 시트, 통풍 시트 등 프리미엄 사양이 기본 적용되었습니다. 액티브 사운드 디자인으로 엔진음을 최적화해 운전 재미를 극대화했으며, GT 모드 선택 시 계기판이 레이싱 카 스타일로 변환됩니다.",
            "추천트림": "2.5T 프리미엄",
            "트림가격": "4,350",
            "추천옵션": "퍼포먼스 패키지(스포츠 LSD, 전자식 서스펜션 컨트롤)",
            "옵션가격": "240",
            "총가격": "4,590",
            "추천이유": "고성능 세단을 원하는 30대 초반 남성층을 위한 최적의 선택입니다. 290마력의 강력한 출력과 정밀한 핸들링 성능으로 주말 트랙 데이 참가에도 적합합니다. 3가지 주행 모드(일반, 스포츠, 스마트)를 통해 다양한 도로 조건에 맞춰 차량 성격을 변경할 수 있으며, 5년 무상 A/S와 10년 파워트레인 보증으로 유지비 부담을 최소화했습니다. 특히 연간 25,000km 이상 주행하는 고객에게 경제적입니다."
        },
        5: {
            "설명": "1.6L 터보 가솔린 엔진으로 180마력의 적정한 출력을 제공하는 실용적인 모델. 후방 카메라와 후측방 경고 시스템이 기본 적용되어 초보 운전자의 주차 편의성을 극대화했습니다. 10.25인치 내비게이션과 애플 카플레이 연동으로 도심 주행 시 편의성을 높였습니다. 480L의 넉넉한 트렁크 공간과 2열 레그룸 980mm로 가족용으로도 적합하며, 실내 공간 활용도를 높인 다양한 수납공간이 마련되어 있습니다.",
            "추천트림": "1.6T 디럭스",
            "트림가격": "2,950",
            "추천옵션": "라이트 에디션(LED 실내등, 오토 라이트 컨트롤)",
            "옵션가격": "75",
            "총가격": "3,025",
            "추천이유": "50대 중반의 첫 세단 구매자를 위한 가장 안정적인 선택입니다. 기아의 검증된 1.6L 터보 엔진으로 유지비가 저렴하며(월 평균 12만원), 보험료가 동급 대비 15% 저렴한 것이 장점입니다. 36개월 무이자 할부와 5년 무상 방문정비 서비스로 구매 부담을 크게 줄였으며, 중고차 시장에서 3년차 잔존가율 68%로 높은 편입니다. 특히 도심 주행 비율이 높은 중장년 고객에게 최적화되었습니다."
        }
        },
        "Telluride": {
        0: {
            "설명": "3.8L V6 가솔린 엔진의 대형 SUV로 291마력의 강력한 토크를 자랑하는 오프로드 모델. 20인치 초대형 알로이 휠과 풀타임 AWD 시스템이 모든 도로 조건에서 안정적인 주행을 보장합니다. 8인승 넉넉한 실내 공간과 1,597L까지 확장되는 트렁크는 캠핑이나 레저 활동에 최적화되었습니다. 10.25인치 헤드업 디스플레이와 360도 어라운드 뷰로 대형차의 주차 편의성을 높였으며, 2열/3열 모두 통풍 시트가 적용되어 여름철 장거리 이동 시 편안함을 극대화했습니다.",
            "추천트림": "3.8 프레스티지 AWD",
            "트림가격": "6,250",
            "추천옵션": "오프로드 패키지(전자식 차동제한장치, 언더가드)",
            "옵션가격": "380",
            "총가격": "6,630",
            "추천이유": "30대 후반의 레저 활동을 즐기는 고소득층에게 특화된 모델입니다. 주말마다 가족과 함께하는 오프로드 주행이나 캠핑에 최적의 성능을 발휘하며, 기아의 대형 SUV 최초로 5년/10만km 무상 유지보수 서비스를 제공합니다. 특히 월 2회 이상의 주말 레저 활동을 즐기는 고객에게 적합하며, 다양한 액티비티 장비 수납이 가능한 대용량 적재 공간이 특징입니다. 연간 20,000km 이상 주행해도 안정적인 성능을 유지하는 내구성을 자랑합니다."
        },
        4: {
            "설명": "3.8L V6 가솔린 엔진에 익스클루시브 전용 메탈릭 페인트와 20인치 다크 크롬 휠이 적용된 최고급 SUV. 퀼팅 납파 가죽 시트와 합판 인테리어로 럭셔리함을 극대화하였으며, 2열 캡틴 시트에 통풍/마사지 기능이 적용되어 비즈니스 이동 시 최상의 편안함을 제공합니다. 14.6인치 후석 엔터테인먼트 시스템과 12스피커 하만카돈 사운드로 극장 같은 오디오 경험을 구현했으며, 전동식 도어 커튼과 차양막이 프라이버시를 보장합니다.",
            "추천트림": "익스클루시브",
            "트림가격": "6,450",
            "추천옵션": "럭셔리 패키지(에어 서스펜션, 전동식 도어 커튼)",
            "옵션가격": "280",
            "총가격": "6,730",
            "추천이유": "50대 중후반의 고소득 비즈니스 임원들에게 특별히 추천하는 최고급 SUV입니다. 제네시스 GV80 대비 15% 가격 경쟁력이 있으며, VIP 고객 전용 콜센터와 출장 정비 서비스가 제공됩니다. 특히 주중에는 비즈니스 미팅용으로, 주말에는 가족용으로 다목적 사용이 가능합니다. 중고차 시장에서 3년차 잔존가율 75%를 유지하며, 연간 30,000km 이상의 장거리 주행에도 변함없는 승차감을 제공합니다."
        }
        },
        "Sportage": {
        0: {
            "설명": "1.6L 터보 가솔린 엔진과 7단 DCT의 조합으로 연비 13.5km/L를 구현한 준중형 SUV. 12.3인치 클러스터와 빌트인 캠으로 첨단 기술을 강조했으며, 어반 세이프티 패키지가 기본 적용되어 도심 주행 안전성을 높였습니다. 10.25인치 와이드 디스플레이와 BOSE 프리미엄 사운드 시스템이 탑재되었으며, 2열 폴딩 테이블과 12V 전원 포트 4개로 실용성을 극대화했습니다.",
            "추천트림": "1.6T 프레스티지",
            "트림가격": "3,450",
            "추천옵션": "테크 패키지(서라운드 뷰 모니터, 현대적 디자인 휠)",
            "옵션가격": "210",
            "총가격": "3,660",
            "추천이유": "첫 SUV 구매를 고려하는 30대 초반 고객을 위한 최적의 선택입니다. 컴팩트한 사이즈(4,660mm)와 우수한 시야각이 주차 및 좁은 골목 주행에 유리하며, 기아의 최신 커넥티드 카 기술이 모두 적용되었습니다. 5년 무상 A/S와 10년 파워트레인 보증으로 장기적인 안심 사용이 가능하며, 특히 도심 생활 비율이 높은 젊은 커플에게 적합합니다."
        },
        3: {
            "설명": "1.6L 터보 가솔린 엔진에 20인치 알로이 휠과 패널 선루프가 적용된 디자인 특화 모델. 2열 폴딩 테이블과 12V 전원 포트 4개가 캠핑에 최적화되었으며, 인스타그램 필터 연동 기능이 특징입니다. 12.3인치 커스텀 디스플레이와 15스피커 하만카돈 사운드 시스템으로 프리미엄 경험을 제공하며, GT 라인 전용 디자인 요소로 개성을 강조했습니다.",
            "추천트림": "디자인 프리미엄",
            "트림가격": "3,950",
            "추천옵션": "스타일 패키지(외장 스타일링 키트, 내장 무드 라이트)",
            "옵션가격": "150",
            "총가격": "4,100",
            "추천이유": "디자인을 중시하는 20~30대 젊은 고객층에게 특별히 추천하는 모델입니다. SNS에 공유할 수 있는 독특한 디자인 요소가 다수 적용되었으며, 인스타그램 필터 연동 기능으로 차량과 함께하는 라이프스타일을 표현하기에 적합합니다. 특히 주말마다 캠핑이나 드라이브를 즐기는 고객에게 최적화되었으며, 중고차 시장에서도 디자인 프리미엄이 유지되는 특징이 있습니다."
        }
        },
        "EV9": {
        1: {
            "설명": "99.8kWh 대용량 배터리로 501km의 장거리 주행이 가능한 기아의 플래그십 전기 SUV. 2열 캡틴 시트에 통풍/마사지/레그레스트 기능이 완비되어 비즈니스 이동 시 최고의 편안함을 제공합니다. 12.3인치 클러스터와 14.6인치 인포테인먼트 시스템의 연동으로 모든 정보를 한눈에 확인할 수 있으며, 우드 그레인 대시보드와 리사이클드 PET 소재 시트로 친환경 프리미엄을 실현했습니다. 800V 초고속 충전 시스템으로 18분 충전에 475km 주행이 가능해 장거리 이동 시 불편함이 없습니다.",
            "추천트림": "롱레인지 RWD",
            "트림가격": "7,890",
            "추천옵션": "VIP 패키지(에어 서스펜션, 전동식 도어 커튼)",
            "옵션가격": "520",
            "총가격": "8,410",
            "추천이유": "환경 가치를 중요하게 생각하는 50대 VIP 고객을 위한 최고급 전기 SUV입니다. 기업의 ESG 경영理念과 맞아 기업용 차량으로도 적합하며, 전용 콜센터와 24시간 긴급 출동 서비스가 제공됩니다. 특히 주중에는 비즈니스 미팅용으로, 주말에는 가족 여행용으로 다목적 사용이 가능합니다. 연간 40,000km 이상 주행하는 고객도 전기차 특유의 저유지비(월 평균 8만원) 혜택을 누릴 수 있으며, 기아카드와 연계해 충전비 10% 할인 혜택을 제공합니다."
        },
        4: {
            "설명": "6인승 프리미엄 전기 SUV로 2열 독립 시트와 전동 레그레스트가 적용된 최고급 모델. 27인치 와이드 디스플레이와 18스피커 메르세데스-벤츠 사운드 시스템으로 극장 같은 멀티미디어 경험을 제공합니다. 2열 ottoman 기능이 적용된 VIP 시트는 장시간 비즈니스 이동 시 최상의 편안함을 보장하며, 전용 냉장고와 와인 셀러가 탑재되어 있습니다. 800V 초고속 충전과 V2L 기능으로 캠핑 시 전기 사용이 가능합니다.",
            "추천트림": "익스클루시브 6인승",
            "트림가격": "8,250",
            "추천옵션": "VIP 컴포트(2열 ottoman 기능, 전용 냉장고)",
            "옵션가격": "480",
            "총가격": "8,730",
            "추천이유": "50대 고소득층이 원하는 최상위급 전기 SUV입니다. 제네시스 GV80 전기차 대비 20% 더 넓은 실내 공간을 자랑하며, 5년 무상 충전 서비스(기아차 충전소)가 제공됩니다. 특히 해외 출장이 잦은 고위 임원들에게 적합하며, 공항 픽업 서비스와 전용 콘시어지가 포함된 VIP 멤버십을 적용할 수 있습니다. 중고차 시장에서 3년차 잔존가율 80%를 유지하는 프리미엄 모델입니다."
        }
        },
        "Sorento": {
        1: {
            "설명": "PHEV 모델로 66km의 전기주행 거리와 가솔린 모드 연비 15.3km/L를 동시에 확보한 대형 SUV. 나파 가죽 시트와 합판 대시보드가 적용된 프리미엄 인테리어를 자랑하며, 컴포트 플러스 패키지(통풍 시트/어드밴스드 크루즈 컨트롤)로 장시간 운전 피로를 최소화했습니다. 12.3인치 파노라마 클러스터와 헤드업 디스플레이가 운전 편의성을 높였으며, 3열 전동 접이식 기능으로 공간 활용도가 뛰어납니다.",
            "추천트림": "PHEV 프리미엄",
            "트림가격": "5,950",
            "추천옵션": "럭셔리 인테리어 패키지(합판 대시보드, 나파 가죽 시트)",
            "옵션가격": "280",
            "총가격": "6,230",
            "추천이유": "환경 성향을 가진 50대 VIP 고객에게 적합한 대형 SUV입니다. 회사 차량 인센티브와 결합 시 PHEV의 세제 혜택이 일반 하이브리드 대비 20% 더 유리하며, 월 2,000km 이상 장거리 출퇴근을 하는 경우 연료비를 월 평균 25만원 절감할 수 있습니다. 특히 7인승이 필요한 가족 단위 고객에게 적합하며, 어린이 승하차 보조 시스템이 육아 부모에게 편리합니다."
        },
        4: {
            "설명": "하이브리드 시스템을 적용한 친환경 SUV로 2.5L 가솔린 엔진과 전기모터의 조합으로 연비 16.7km/L를 구현했습니다. 캡틴 시트 패키지로 2열 승차감을 극대화하였으며, 12.3인치 클러스터와 헤드업 디스플레이로 고급스러운 운전 환경을 제공합니다. 공기 청정 모드와 마사지 시트로 장거리 운전 피로를 줄여주며, 19인치 에어로 휀로 연비 효율성을 극대화했습니다.",
            "추천트림": "HEV 프레스티지",
            "트림가격": "5,450",
            "추천옵션": "테크 패키지(12.3인치 클러스터, 헤드업 디스플레이)",
            "옵션가격": "220",
            "총가격": "5,670",
            "추천이유": "친환경 대형 SUV를 원하는 50대 고객에게 최적의 선택입니다. 디젤 엔진 대비 30% 이상의 연료비 절감 효과가 있으며, 기아의 10년/20만km 하이브리드 시스템 보증으로 장기적인 안심 사용이 가능합니다. 특히 주말마다 가족과 장거리 여행을 즐기는 고객에게 적합하며, 3열을 접을 경우 605L의 대용량 트렁크 공간을 활용할 수 있습니다."
        }
        },
        "Carnival": {
        1: {
            "설명": "11인승 대형 MPV로 2열 회전 시트와 3열 전동 접이식 기능이 적용된 가족 친화적 모델. 12.3인치 듀얼 디스플레이와 후석 전용 공기청정기로 대가족의 편의성을 극대화했습니다. VIP 패키지(통풍/마사지 시트)로 장시간 운전 피로도를 감소시켰으며, 2열 오토마틱 슬라이딩 도어가 장보기 등 일상 생활에도 편리합니다. 3열까지 전 좌석 USB 충전 포트가 마련되어 있습니다.",
            "추천트림": "리무지엄",
            "트림가격": "5,450",
            "추천옵션": "VIP 패키지(통풍/마사지 시트, 2열 ottoman 기능)",
            "옵션가격": "290",
            "총가격": "5,740",
            "추천이유": "다자녀 가정의 40~50대 여성 고객이 미니밴 대체용으로 선택하기에 최적입니다. 어린이 승하차 보조 시스템과 결합 시 육아 부담을 50% 이상 줄여주며, 2열 회전 기능으로 차량 내에서의 가족 활동 공간을 확보할 수 있습니다. 특히 유아용 카시트 3개를 동시에 설치할 수 있는 넓은 2열 공간이 특징이며, 5년 무상 정기점검 서비스가 제공됩니다."
        }
        },
        "EV6": {
        2: {
            "설명": "AWD 고성능 전기차로 320kW 듀얼 모터 적용 시 0-100km/h 가속 5.1초 가능한 스포츠 모델. 20인치 휠과 스포츠 서스펜션, 가상 엔진 사운드 시스템으로 주행 재미를 극대화했습니다. 우드 그레인 대시보드와 리사이클드 PET 소재 시트가 적용된 친환경 럭셔리 인테리어를 자랑하며, 800V 초고속 충전 시 18분 충전으로 475km 주행이 가능합니다. GT 모드 선택 시 계기판이 레이싱 카 스타일로 변환됩니다.",
            "추천트림": "GT-Line AWD",
            "트림가격": "6,850",
            "추천옵션": "프리미엄 인테리어(우드 그레인 대시보드, 리사이클드 PET 시트)",
            "옵션가격": "320",
            "총가격": "7,170",
            "추천이유": "30대 젊은 여성 VIP 고객이 테슬라 모델 Y 대안으로 선택하기에 적합한 프리미엄 전기차입니다. 레이싱 게임 연동 기능과 GT 모드 전용 디스플레이가 강점이며, 기아카드 포인트 5% 적립 프로모션과 결합해 마케팅 효과가 높습니다. 특히 인스타그램에 공유하기에 적합한 유토피아 그레이 컬러 옵션이 제공되며, 연간 30,000km 이상 주행해도 충전비가 월 평균 10만원 이내로 저렴합니다."
        }
        },
        "Seltos": {
        2: {
            "설명": "1.6L 터보 엔진의 소형 SUV로 177마력 출력과 18.1km/L의 우수한 연비를 동시에 구현했습니다. 10.25인치 와이드 디스플레이와 BOSE 프리미엄 사운드 시스템이 적용되었으며, 빌트인 캠으로 주행 영상을 쉽게 촬영할 수 있습니다. 2열 폴딩 테이블과 12V 전원 포트 4개가 캠핑에 최적화되었으며, 인스타그램 필터 연동 기능으로 SNS 공유에 적합합니다.",
            "추천트림": "1.6T 프레스티지",
            "트림가격": "3,120",
            "추천옵션": "프리미엄 사운드(BOSE 8스피커 시스템, 앰프)",
            "옵션가격": "150",
            "총가격": "3,270",
            "추천이유": "첫 SUV를 원하는 20~30대 젊은 여성 VIP 고객에게 추천하는 모델입니다. 컴팩트한 사이즈(4,380mm)와 우수한 시야각이 도심 주행에 적합하며, 인스타그램 필터 연동 기능으로 차량과 함께하는 라이프스타일을 표현하기에 적합합니다. 특히 주말마다 캠핑이나 드라이브를 즐기는 고객에게 최적화되었으며, 36개월 무이자 할부로 부담 없이 구매할 수 있습니다."
        }
        },
        "Tucson(NX4)": {
        3: {
            "설명": "2.5L 가솔린 엔진에 8단 자동변속기의 조합으로 고속 주행 시 안정감을 제공하는 중형 SUV. 하이웨이 드라이빙 어시스트(차선 유지/차간 거리 자동 조절)가 장거리 운전 피로도를 30% 이상 줄여줍니다. 12.3인치 파노라마 클러스터와 10.25인치 내비게이션으로 운전 편의성을 높였으며, 2열 폴딩 테이블과 12V 전원 포트 4개가 캠핑에 최적화되었습니다.",
            "추천트림": "2.5 프리미엄",
            "트림가격": "3,950",
            "추천옵션": "스포츠 패키지(20인치 휠, 스포츠 서스펜션)",
            "옵션가격": "170",
            "총가격": "4,120",
            "추천이유": "SUV를 원하지만 세단의 우아함을 유지하고 싶은 30대 남성층에게 적합한 모델입니다. 고속도로 주행 시 안정성과 연비 효율성(15.8km/L)을 동시에 충족하며, 주말마다 고향을 오가거나 자녀 대학 통학을 위해 월 1,500km 이상 장거리 운전하는 경우에 최적입니다. 특히 5년 무상 A/S와 10년 파워트레인 보증으로 장기적인 안심 사용이 가능합니다."
        }
        },
        "K3": {
        5: {
            "설명": "1.6L 가솔린 엔진의 컴팩트 세단으로 연비 15.3km/L의 경제성을 자랑하는 실용적인 모델. 10.25인치 내비게이션과 후방카메라가 기본 적용되어 초보 운전자도 쉽게 적응할 수 있습니다. 6에어백과 긴급 제동 시스템이 안전성을 높였으며, 475L의 트렁크 공간으로 가족용으로도 적합합니다. 36개월 무이자 할부와 5년 무상 A/S가 결합되어 부담 없는 구매가 가능합니다.",
            "추천트림": "1.6 프레스티지",
            "트림가격": "2,450",
            "추천옵션": "스마트 패키지(LED 실내등, 오토 라이트 컨트롤)",
            "옵션가격": "80",
            "총가격": "2,530",
            "추천이유": "저예산으로 신뢰성 있는 차량을 원하는 50대 중장년 고객에게 최적의 선택입니다. 기아자동차의 안정적인 A/S 네트워크를 믿고 선택할 수 있으며, 보험료가 동급 대비 20% 저렴합니다. 특히 도심 생활 비율이 높은 고객에게 적합하며, 중고차 시장에서 3년차 잔존가율 70%를 유지해 추후 판매 시에도 손실이 적습니다. 첫 차 구매자들을 위한 다양한 금융 혜택이 제공됩니다."
        }
        },
        "Sonet": {
        5: {
            "설명": "1.2L 가솔린 엔진의 초소형 SUV로 4m 미만의 컴팩트한 전장(3,995mm)으로 좁은 골목 주행과 주차에 최적화되었습니다. 10.25인치 터치스크린과 애플 카플레이 연동으로 편의성을 높였으며, 후방 카메라와 긴급 제동 시스템이 초보 운전자를 배려했습니다. 1열 통풍 시트와 공기 청정 시스템이 여름철 쾌적한 실내 환경을 유지하며, 2열 폴딩 기능으로 수납 공간을灵活하게 활용할 수 있습니다.",
            "추천트림": "1.2 스마트",
            "트림가격": "2,150",
            "추천옵션": "어반 패키지(주차 보조 시스템, LED 실내등)",
            "옵션가격": "60",
            "총가격": "2,210",
            "추천이유": "도심 생활을 주로 하는 50대 중장년 고객에게 적합한 초소형 SUV입니다. 주차 공간이 협소한 아파트에 거주하는 고객이나, 주로 단거리 이동 위주로 사용하는 고객에게 최적화되었습니다. 보험료가 월 평균 5만원대로 매우 저렴하며, 연비 16.5km/L로 유지비 부담이 적습니다. 특히 첫 SUV를 구매하는 중장년 고객에게 추천하며, 5년 무상 방문정비 서비스로 관리 부담을 덜었습니다."
        }
    }
    }
}

    st.info("고객님의 성향에 맞춘 추천차량 목록입니다.")

    # selected_vehicle 기본값 설정
    default_vehicle = selected_vehicle or 구매한제품 or recommended_vehicles[0]
    if default_vehicle in recommended_vehicles:
        default_index = recommended_vehicles.index(default_vehicle)
    else:
        default_index = 0
        # 차량 선택
    selected_vehicle = st.selectbox(
        "구입 희망 차량을 선택하세요",
        recommended_vehicles,
        key="vehicle_select_box",
        index=default_index
    )
    if selected_vehicle:
        # 이미지, 설명, 링크, 가격 처리
        vehicle_image = vehicle_images.get(selected_vehicle, get_abs_path("mini2_img/default.png"))
        # 실제 파일 존재 여부 확인
        if not vehicle_image.exists():
            vehicle_image = get_abs_path("mini2_img/default.png")
        vehicle_link = vehicle_links.get(selected_vehicle, "#")
        vehicle_cluster_recommendations = vehicle_recommendations.get(brand, {})
        vehicle_recommend = vehicle_cluster_recommendations.get(selected_vehicle, {})
        cluster_recommend = vehicle_recommend.get(cluster_id, "")

        if cluster_recommend:
            vehicle_description = cluster_recommend
        else:
            vehicle_description = basic_recommendations.get(brand, {}).get(selected_vehicle, "차량에 대한 정보가 없습니다.")

        vehicle_price = vehicle_prices.get(brand, {}).get(selected_vehicle, "가격 정보 없음")

        # 표시
        st.image(vehicle_image, use_container_width=True)
        st.text(vehicle_description)
        st.markdown(f"[차량 상세정보 확인하기]({vehicle_link})", unsafe_allow_html=True)
        st.text(f"가격: {vehicle_price:,}원")

    else:
        st.warning("추천 차량이 없습니다. 다시 예측을 시도해 주세요.")

    # 선택 완료 버튼
    if st.button("선택 완료"):
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
            # 하이픈 제거 및 숫자만
            휴대폰번호 = re.sub(r'[^0-9]', '', 휴대폰번호)

            # --- 유효성 검사 ---
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

            # --- 유효성 통과 후 고객 정보 저장 ---
            st.session_state["name"] = 이름
            st.session_state["phone"] = 휴대폰번호
            st.session_state["email"] = 이메일
            st.session_state["address"] = 주소
            st.session_state["id"] = 아이디
            st.session_state["registration_date"] = 가입일

            # 필요한 정보 가져오기
            연령 = st.session_state.get("연령", "")
            country = st.session_state.get("country", "")
            생년월일 = st.session_state.get("생년월일", "")
            성별 = st.session_state.get("성별", "")
            고객세그먼트 = st.session_state.get("고객세그먼트", "")
            selected_vehicle = st.session_state.get("selected_vehicle", "")
            차량구분 = st.session_state.get("차량구분", "")
            친환경차 = "여" if selected_vehicle in eco_friendly_models.get(st.session_state.get("brand", ""), []) else "부"
            제품구매날짜 = st.session_state.get("제품구매날짜", "")
            거래금액 = st.session_state.get("거래금액", "")
            거래방식 = st.session_state.get("거래방식", "")
            구매빈도 = st.session_state.get("제품구매빈도", "")
            제품구매경로 = st.session_state.get("제품구매경로", "")
            제품출시년월 = st.session_state.get("제품출시년월", "")
            Cluster = st.session_state.get("Cluster", "")
            brand = st.session_state.get("brand", "")

            full_data = pd.DataFrame([[
                이름, 생년월일, 연령, 성별, 휴대폰번호, 이메일, 주소, 아이디, 가입일,
                차량구분, selected_vehicle, 친환경차, 제품구매날짜,
                거래금액, 거래방식, 구매빈도, 제품구매경로, 제품출시년월,country,고객세그먼트,Cluster
            ]], columns=[
                "이름", "생년월일", "연령", "성별", "휴대폰번호", "이메일", "주소", "아이디", "가입일",
                "차량구분", "구매한 제품", "친환경차", "제품 구매 날짜",
                "거래 금액", "거래 방식", "제품 구매 빈도", "제품 구매 경로", "제품 출시년월","국가","고객세그먼트","Cluster"
            ])

            file_path = Path(__file__).parent.parent.parent.parent / "data" / f"{brand}_고객데이터_신규입력용.csv"
            os.makedirs(file_path.parent, exist_ok=True)
            full_data.to_csv(file_path, mode='a', header=not file_path.exists(), index=False, encoding='utf-8-sig')

            # 문자 발송
            clicksend_username = st.secrets["CLICKSEND"]["CLICKSEND_USERNAME"]
            clicksend_api_key = st.secrets["CLICKSEND"]["CLICKSEND_API_KEY"]
            to_number = "+82" + 휴대폰번호[1:]
            message_body = f"안녕하세요, {이름}님! {brand} 자동차에서 보내드리는 메시지입니다. 멤버십 가입을 축하드리며, 다양한 혜택과 서비스를 경험해보세요!"

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

            # 현대 회원가입 이메일 발송
            if brand == '현대':
                # 이메일 발송
                ui.mini1_promo_email.send_welcome_email(이메일, 이름, 아이디, 가입일)
                st.success("이메일이 성공적으로 발송되었습니다.")

                # 이메일 전송 로그 저장
                log_entry = pd.DataFrame([[이메일, 이름, Cluster, datetime.now().strftime("%Y-%m-%d %H:%M:%S")]],
                                        columns=["이메일", "이름", "클러스터 ID", "전송 시간"])
                log_file_path = Path("data/현대_이메일_전송_로그.csv")
                os.makedirs(log_file_path.parent, exist_ok=True)
                log_entry.to_csv(log_file_path, mode='a', header=not log_file_path.exists(), index=False, encoding='utf-8-sig')

                print("✅ 이메일 전송 로그 저장 완료!")
                # 기아 회원가입 이메일 발송
            elif brand == '기아' :
                # 이메일 발송
                ui.mini1_promo_email.send_welcome_email(이메일, 이름, 아이디, 가입일)
                st.success("이메일이 성공적으로 발송되었습니다.")

                # 이메일 전송 로그 저장
                log_entry = pd.DataFrame([[이메일, 이름, Cluster, datetime.now().strftime("%Y-%m-%d %H:%M:%S")]],
                                        columns=["이메일", "이름", "클러스터 ID", "전송 시간"])
                log_file_path = Path("data/기아_이메일_전송_로그.csv")
                os.makedirs(log_file_path.parent, exist_ok=True)
                log_entry.to_csv(log_file_path, mode='a', header=not log_file_path.exists(), index=False, encoding='utf-8-sig')

                print("✅ 이메일 전송 로그 저장 완료!")
            st.session_state["step"] = 1
            time.sleep(2)
            st.rerun()