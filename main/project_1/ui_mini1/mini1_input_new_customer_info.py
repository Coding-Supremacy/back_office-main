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


from project_1.ui_mini1 import mini1_promo_email

def get_abs_path(relative_path):
    """상대 경로를 절대 경로로 변환"""
    return Path(__file__).parent.parent / relative_path

# 모델과 출시 년월 데이터
launch_dates = {
    '현대':{
    'G70 (IK)': '2017-09',
    'Santa-Fe ™': '2018-01',
    'NEXO (FE)': '2018-01',
    'Avante (CN7 N)': '2020-05',
    'G80 (RG3)': '2020-03',
    'Grandeur (GN7 HEV)': '2022-01',
    'IONIQ (AE EV)': '2016-01',
    'i30 (PD)': '2017-03',
    'Palisade (LX2)': '2018-12',
    'Tucson (NX4 PHEV)': '2021-05',
    'Avante (CN7 HEV)': '2020-07',
    'IONIQ 6 (CE)': '2022-06',
    'G90 (HI)': '2022-03',
    'Santa-Fe (MX5 PHEV)': '2022-06',
    'G90 (RS4)': '2022-03'
},

    '기아' : {
    'K3': '2018-09',
    'Pegas': '2017-06',
    'Rio (pride)': '2017-06',
    'EV6': '2021-03',
    'KX7': '2017-03',  # 중국 전용 모델
    'K4': '2014-04',  # 중국 전략형 세단
    'K5': '2019-12',  # Optima와 동일
    'Telluride': '2019-01',
    'KX5': '2016-03',
    'Seltos': '2019-06',
    'Sorento': '2020-03',
    'Carnival': '2020-06',
    'K2': '2017-01',
    'KX3': '2015-03',
    'Forte': '2018-01',  # 국내 K3
    'Carens MPV': '2013-03',
    'Sonet': '2020-08',  # 인도 전략형 SUV
    'Sportage': '2021-06',
    "C'eed": '2018-06',  # 유럽형 해치백
    'Syros': '2021-08',  # 가상 또는 중국전용일 수 있음
    'Cerato': '2018-03',
    'KX1': '2018-09',
    'EV5': '2023-08',
    'Zhipao': '2020-07',  # 중국 전략형 모델로 추정
    'EV9': '2023-03',
    'K4': '2020-09'}
}

# 현대 친환경차 모델 목록
eco_friendly_models = {'현대': [
    'NEXO (FE)', 'Avante (CN7 HEV)', 'Grandeur (GN7 HEV)', 'IONIQ (AE EV)', 
    'Tucson (NX4 PHEV)', 'IONIQ 6 (CE)', 'Santa-Fe (MX5 PHEV)'
],
'기아':['EV6', 'EV5', 'EV9']}

# 클러스터별 차량 추천 모델 목록
brand_recommendations = {
    '현대': {
        0: ['Avante (CN7 N)', 'NEXO (FE)', 'Santa-Fe ™'],
        1: ['G80 (RG3)', 'G90 (HI)', 'IONIQ 6 (CE)'],
        2: ['G70 (IK)', 'i30 (PD)', 'Avante (CN7 HEV)'],
        3: ['Avante (CN7 N)', 'Tucson (NX4 PHEV)', 'Grandeur (GN7 HEV)'],
        4: ['IONIQ (AE EV)', 'NEXO (FE)', 'Tucson (NX4 PHEV)'],
        5: ['Santa-Fe ™', 'G70 (IK)', 'Grandeur (GN7 HEV)'],
        6: ['i30 (PD)', 'Avante (CN7 N)', 'Avante (CN7 HEV)'],
        7: ['IONIQ 6 (CE)', 'NEXO (FE)', 'G90 (RS4)']
    },
    '기아': {
        0: ['Forte', 'KX1', 'KX3', 'Rio (pride)', 'Seltos', 'Sonet', 'Syros', 'Zhipao', 'Carnival'],
        1: ['EV6', 'EV9', 'K4', 'K8', 'KX5', 'KX7', 'Sorento', 'Sportage', 'Telluride'],
        2: ['Cerato', 'EV5', 'EV6', 'G70 (IK)', 'K3', 'K5', 'Optima / K5'],
        3: ['C\'eed', 'C\'eed CUV', 'Cerato', 'Forte', 'K2', 'K3', 'KX3', 'Pegas', 'Rio (pride)', 'Seltos', 'Sonet', 'Sportage', 'Syros'],
        4: ['Carens MPV', 'Carnival', 'EV5', 'EV6', 'EV9', 'K4', 'KX5', 'Sorento', 'Telluride'],
        5: ['C\'eed', 'K2', 'Optima / K5', 'Pegas', 'Carnival']
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
    model_dir = Path(__file__).parent.parent / "models_mini1"

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
            'Avante (CN7 N)','NEXO (FE)','Santa-Fe ™'
        ]
    elif cluster_id == 1:
        recommended_vehicles = [
            'G80 (RG3)','G90 (HI)','IONIQ 6 (CE)'
        ]
    elif cluster_id == 2:
        recommended_vehicles = [
            'G70 (IK)','i30 (PD)','Avante (CN7 HEV)'
        ]
    elif cluster_id == 3:
        recommended_vehicles = [
            'Avante (CN7 N)','Tucson (NX4 PHEV)','Grandeur (GN7 HEV)'
        ]
    elif cluster_id == 4:
        recommended_vehicles = [
            'IONIQ (AE EV)','NEXO (FE)','Tucson (NX4 PHEV)'
        ]
    elif cluster_id == 5:
        recommended_vehicles = [
            'Santa-Fe ™','G70 (IK)','Grandeur (GN7 HEV)'
        ]
    elif cluster_id == 6:
        recommended_vehicles = [
            'i30 (PD)','Avante (CN7 N)','Avante (CN7 HEV)'
        ]
    elif cluster_id == 7:
        recommended_vehicles = [
            'IONIQ 6 (CE)','NEXO (FE)','G90 (RS4)'
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
    IMAGE_BASE_PATH = 'img/'
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
            "Santa-Fe ™": "Santa-Fe는 넓고 다용도로 사용 가능한 공간을 자랑하는 SUV로, 가족 단위 여행에 적합합니다. 실용성과 편안함을 제공합니다.",
            "G80 (RG3)": "G80은 고급스러운 세단으로 품격 있는 운전 경험을 제공합니다. VIP 고객님에게 어울리는 차량입니다.",
            "G90 (HI)": "G90은 프리미엄 세단으로, 고급스러움과 편안함을 제공합니다. 모든 세부 사항이 완벽하게 설계되어 있어 최고의 만족감을 선사합니다.",
            "IONIQ 6 (CE)": "IONIQ 6는 첨단 기술과 세련된 디자인을 갖춘 전기차입니다. 친환경적인 드라이빙을 원하시는 고객님께 적합합니다.",
            "i30 (PD)": "i30은 실용적이고 경제적인 소형차로, 유지비가 적고 부담 없는 선택입니다. 특히 첫 차로 적합한 모델입니다.",
            "Tucson (NX4 PHEV)": "Tucson은 플러그인 하이브리드 SUV로, 환경을 고려하면서도 강력한 성능을 제공합니다. 연비 효율성이 뛰어난 차량입니다.",
            "Grandeur (GN7 HEV)": "Grandeur는 고급스러움과 실용성을 동시에 제공합니다. 하이브리드 모델로 연비가 뛰어나고, 가격대비 좋은 선택입니다.",
            "IONIQ (AE EV)": "IONIQ는 전기차로 연료비 절감과 친환경적인 운전이 가능합니다. 가격대비 성능이 뛰어난 모델입니다.",
            "G70 (IK)": "G70은 고급 세단으로, 가격대가 적당하면서도 고급스러운 느낌을 줄 수 있는 차량입니다. 세련된 디자인을 갖추고 있습니다.",
            "Palisade (LX2)": "Palisade는 넓고 고급스러운 3열 SUV로, 대가족이나 넉넉한 공간을 필요로 하는 고객님께 적합합니다. 높은 품질의 승차감을 제공합니다.",
            "Santa-Fe (MX5 PHEV)": "Santa-Fe PHEV는 플러그인 하이브리드 SUV로, 친환경을 고려하면서도 넓은 공간과 뛰어난 성능을 자랑하는 선택입니다.",
            "G90 (RS4)": "G90 RS4는 프리미엄 브랜드의 대표 모델로, 최고급 세단에 걸맞은 품격과 편안함을 제공합니다. 세부 사항까지 완벽한 선택입니다.",
            "Avante (CN7 HEV)": "친환경차 선호도가 높은 고객님께 Avante (CN7 HEV)! 하이브리드 모델로 연비 효율성을 자랑하며, 친환경적인 선택을 제공합니다."
        },
        '기아': {
            "K3": "K3는 세련된 디자인과 실용성을 겸비한 준중형 세단으로, 합리적인 가격대비 뛰어난 성능을 제공합니다.",
            "Pegas": "Pegas는 경제성과 실용성을 중시하는 고객을 위한 컴팩트 세단으로, 도심 주행에 최적화된 모델입니다.",
            "K5": "K5는 스포티한 디자인과 역동적인 주행 성능을 갖춘 중형 세단으로, 젊은 감각을 원하는 분들께 추천합니다.",
            "Rio(pride)": "Rio(Pride)는 컴팩트한 사이즈와 경제적인 운영 비용이 장점인 소형차로, 첫 차로 적합합니다.",
            "EV6": "EV6는 기아의 최신 전기차 기술이 집약된 크로스오버 SUV로, 혁신적인 디자인과 뛰어난 주행 거리가 특징입니다.",
            "KX7": "KX7는 넓은 실내 공간과 다양한 편의 사양을 갖춘 중대형 SUV로, 가족 여행에 적합합니다.",
            "C'eed CUV": "C'eed CUV는 유럽형 디자인과 실용성을 결합한 크로스오버로, 도시와 어우러지는 세련된 스타일을 자랑합니다.",
            "K4": "K4는 중형 세단의 편안함과 준중형의 경제성을 겸비한 모델로, 실용적인 선택을 원하는 분들께 적합합니다.",
            "Telluride": "Telluride는 미국 시장을 겨냥한 대형 SUV로, 웅장한 디자인과 풍부한 사양이 특징입니다.",
            "KX5": "KX5는 중형 SUV 시장에서 인기 있는 모델로, 균형 잡힌 성능과 스타일을 제공합니다.",
            "Seltos": "Seltos는 젊고 활동적인 라이프스타일에 맞는 소형 SUV로, 개성 있는 디자인과 다양한 컬러 옵션이 매력적입니다.",
            "Sorento": "Sorento는 프리미엄 감성과 실용성을 모두 갖춘 중대형 SUV로, 고급스러운 주행 경험을 제공합니다.",
            "Carnival": "Carnival은 뛰어난 실내 공간과 편의성을 자랑하는 대형 MPV로, 가족 단위 고객에게 최적화된 모델입니다.",
            "K2": "K2는 컴팩트한 사이즈와 경제적인 운영 비용이 장점인 소형 세단으로, 도심 주행에 적합합니다.",
            "KX3": "KX3는 개성 있는 디자인과 다양한 컬러 옵션으로 젊은 층에게 어필하는 소형 SUV입니다.",
            "Forte": "Forte는 실용성과 스타일을 겸비한 준중형 세단으로, 합리적인 가격대비 다양한 사양을 제공합니다.",
            "Carnival (CKD)": "Carnival (CKD)는 현지 조립 방식으로 제공되는 대형 MPV로, 원본 모델과 동일한 품질을 유지합니다.",
            "Carens MPV": "Carens MPV는 다목적 가족용 차량으로, 유연한 좌석 구성과 넉넉한 적재 공간이 특징입니다.",
            "Sonet": "Sonet은 인도 시장을 겨냥한 소형 SUV로, 콤팩트한 사이즈와 강렬한 디자인이 매력적입니다.",
            "Sportage": "Sportage는 기아의 대표 중형 SUV로, 세련된 디자인과 첨단 안전 사양을 자랑합니다.",
            "C'eed": "C'eed는 유럽 시장을 겨냥한 해치백 모델로, 동적 주행 성능과 실용성을 두루 갖췄습니다.",
            "Syros": "Syros는 중국 시장 전략 모델로 추정되는 세단으로, 독특한 디자인이 특징입니다.",
            "Cerato": "Cerato는 K3의 글로벌 명칭으로, 전 세계적으로 사랑받는 준중형 세단입니다.",
            "KX1": "KX1은 소형 SUV 시장에서 인기 있는 모델로, 도시형 라이프스타일에 최적화되었습니다.",
            "EV5": "EV5는 기아의 중형 전기 SUV로, 실용성과 친환경 기술의 조화를 추구합니다.",
            "Zhipao": "Zhipao는 중국 시장을 겨냥한 전략 모델로, 현지 소비자 취향에 맞춰 개발되었습니다.",
            "EV9": "EV9은 기아의 플래그십 전기 SUV로, 고급스러움과 첨단 기술이 결합된 모델입니다."
        }
    }

    # 차량 링크 매핑
    vehicle_links = {"현대":{
        "Avante (CN7 N)": "https://www.hyundai.com/kr/ko/vehicles/avante",
        "NEXO (FE)": "https://www.hyundai.com/kr/ko/vehicles/nexo",
        "Santa-Fe ™": "https://www.hyundai.com/kr/ko/e/vehicles/santafe/intro",
        "G80 (RG3)": "https://www.genesis.com/kr/ko/models/luxury-sedan-genesis/g80-black/highlights.html",
        "G90 (HI)": "https://www.genesis.com/kr/ko/models/luxury-sedan-genesis/g90-black/highlights.html",
        "IONIQ 6 (CE)": "https://www.hyundai.com/kr/ko/e/vehicles/ioniq6/intro",
        "i30 (PD)": "https://www.hyundai-n.com/ko/models/n/i30-n.do",
        "Tucson (NX4 PHEV)": "https://www.hyundai.com/kr/ko/vehicles/tucson",
        "Grandeur (GN7 HEV)": "https://www.hyundai.com/kr/ko/vehicles/grandeur",
        "IONIQ (AE EV)": "https://www.hyundai.com/kr/ko/e/vehicles/ioniq9/intro",
        "G70 (IK)": "https://www.genesis.com/kr/ko/models/luxury-sedan-genesis/g70/highlights.html",
        "Palisade (LX2)": "https://www.hyundai.com/kr/ko/vehicles/palisade",
        "Santa-Fe (MX5 PHEV)": "https://www.hyundai.com/kr/ko/e/vehicles/santafe/intro",
        "G90 (RS4)": "https://www.genesis.com/kr/ko/models/luxury-sedan-genesis/g90-black/highlights.html",
        "Avante (CN7 HEV)": "https://www.hyundai.com/kr/ko/e/vehicles/avante-n/intro"
    },
    "기아":{}
    }
    # 차량 가격 매핑
    vehicle_prices = {
        '현대': {
            "Avante (CN7 N)": 19640000,
            "NEXO (FE)": 69500000,
            "Santa-Fe ™": 34920000,
            "G80 (RG3)": 82750000,
            "G90 (HI)": 129600000,
            "IONIQ 6 (CE)": 46950000,
            "i30 (PD)": 25560000,
            "Tucson (NX4 PHEV)": 27290000,
            "Grandeur (GN7 HEV)": 37110000,
            "IONIQ (AE EV)": 67150000,
            "G70 (IK)": 45240000,
            "Palisade (LX2)": 43830000,
            "Santa-Fe (MX5 PHEV)": 34920000,
            "G90 (RS4)": 135800000,
            "Avante (CN7 HEV)": 33090000
        },
        '기아': {
        "C'eed": 25720000,
        "K5": 35460000,
        "K8": 43730000,
        "EV6": 52600000,
        "Sorento": 38990000,
        "Sportage": 32220000,
        "Carnival": 38960000,
        "Seltos": 25720000,
        "Stinger": 49980000,
        "Niro EV": 49970000,
        "Mohave": 51440000,
        "Ray EV": 26930000,
        "Soul": 27846000,           # 27,846,000
        "K3": 22110000,
        "K9": 87650000,
        "Forte": 27986000,          # 27,986,000
        "KX5": 32220000,
        "KX7": 38990000,
        "KX3": 25720000,
        "Rio (pride)": 23450000,    # 23,450,000
        "Telluride": 49966000,      # 49,966,000
        "KX1": 25720000,
        "K4": 30786000,             # 30,786,000
        "K2": 22110000,
        "KX8": 38990000,
        "KX9": 43830000,
        "KX10": 43830000
        }
    }


    # 클러스터별 차량 추천 이유 매핑
    vehicle_recommendations = {'현대':{
        "Avante (CN7 N)": {
            0: "젊은 연령대와 높은 거래 금액을 자랑하는 고객님께 딱 맞는 트렌디한 선택입니다. \n 최신형 세단으로 스타일과 실용성 두 마리 토끼를 잡을 수 있는 완벽한 선택입니다. \n 이 차량으로 한 단계 더 업그레이드된 라이프스타일을 경험해 보세요.",
            1: "VIP 고객님에게 어울리는 고급스러움을 제공하는 차량입니다. \n  고급 세단으로서 품격 있는 스타일을 완성해 드립니다. \n 더욱 럭셔리한 운전을 즐기세요.",
            2: "가격 대비 성능 최고! Avante (CN7 N)은 경제적이면서도 뛰어난 성능을 자랑하는 차량입니다.",
            3: "젊은 고객님, 스타일과 친환경성을 모두 고려한 Avante (CN7 N)!\n  최신 기술과 뛰어난 성능, 이 차량은 바로 고객님의 라이프스타일에 맞는 완벽한 파트너입니다.",
            4: "이 차량은 친환경차 선호도가 높은 고객님께도 안성맞춤!\n  가격 대비 성능이 뛰어나며 실용성도 고려한 Avante (CN7 N)을 추천 드립니다.",
            5: "신뢰할 수 있는 차량, Avante (CN7 N)!\n  현금 거래 비율이 높은 고객님께는 안정감과 실용성까지 제공하는 세련된 선택이 될 거예요.",
            6: "젊은 고객님들에게 더 없이 좋은 가격 대비 성능의 Avante (CN7 N)!\n  실용적이면서도 트렌디한 선택을 원하신다면 이 차가 바로 정답입니다.",
            7: "친환경차를 선호하시는 고객님에게 더할 나위 없이 좋은 전기차 옵션까지 고려한 Avante (CN7 N),\n  이 차와 함께라면 환경을 생각하는 운전이 가능해요."
        },
        "NEXO (FE)": {
            0: "환경보호에 관심을 가지기 시작하신 고객님께 완벽한 선택, 수소차 NEXO! \n 연령대가 젊고 환경을 생각하는 여러분께 딱 맞는 차량입니다. 지속 가능한 미래를 위한 선택을 하세요.",
            1: "친환경차 선호도가 높은 VIP 고객님께 완벽한 고급스러움과 친환경을 동시에 만족시킬 수 있는 차량, NEXO!\n  고급스러우면서도 환경을 생각하는 똑똑한 선택입니다.",
            4: "친환경차에 대한 관심이 높은 고객님께 맞춤 추천!\n  NEXO는 연료비 절감과 친환경적 요소를 모두 고려한 차량으로, 미래를 향한 현명한 선택입니다.",
            7: "친환경을 생각하는 고객님께 완벽한 선택, 수소차 NEXO!\n  완벽한 친환경차로, 여러분의 선택이 더욱 빛날 것입니다. 고급스러움과 친환경을 동시에 갖춘 NEXO를 만나보세요."
        },
        "Santa-Fe ™": {
            0: "가족 단위 고객님께 완벽한 공간과 실용성을 제공하는 Santa-Fe!\n  넓고 다용도로 사용 가능한 SUV, 장거리 여행에도 완벽한 선택입니다.\n  여러분의 생활을 더욱 편리하고 즐겁게 만들어 드려요!",
            5: "편안한 승차감과 넉넉한 공간을 자랑하는 Santa-Fe!\n  나이가 많고 현금 거래 비율이 높은 고객님께 실용적이고 신뢰할 수 있는 선택입니다. \n 가족과 함께 편안한 여행을 떠나세요!"
        },
        "G80 (RG3)": {
            1: "고급스러운 세단을 원하신다면 G80 (RG3)!\n  VIP 고객님께 딱 맞는 차량으로, 품격과 스타일을 모두 갖춘 선택입니다.\n  차 한 대로 고급스러움을 완성해 보세요."
        },
        "G90 (HI)": {
            1: "한 단계 더 높은 품격을 원하시는 고객님께 G90!\n  프리미엄 세단의 대명사로, 고급스러움과 편안함을 동시에 제공하는 차량입니다.\n  최상의 편안함을 원하신다면 G90을 선택하세요.",
            7: "거래 금액이 매우 높고, 친환경차를 선호하시는 고객님께 딱 맞는 고급 전기차, G90!\n  프리미엄 이미지를 더한 친환경차로, 완벽한 선택입니다."
        },
        "IONIQ 6 (CE)": {
            1: "친환경차에 대한 관심이 늘고 있는 고객님께, 고급 전기차 IONIQ 6! \n 고급스러운 외관과 첨단 기술을 갖춘 차량으로, 친환경을 고려하면서도 세련된 스타일을 제공합니다.",
            7: "친환경을 생각하는 고객님께 더욱 특별한 IONIQ 6! \n 고급스러움과 친환경성을 동시에 갖춘 전기차로, 미래 지향적인 선택이 될 것입니다."
        },
        "i30 (PD)": {
            2: "가격이 저렴하고 실용적인 소형차, i30! \n 연령대가 높고 거래 금액이 적은 고객님께 부담 없는 유지비와 실용성을 제공하는 완벽한 선택입니다.",
            6: "저렴한 가격으로 실용성을 고려한 i30! \n 거래 금액과 구매 빈도가 낮은 고객님께 실용적이고 경제적인 소형차를 추천드립니다."
        },
        "Tucson (NX4 PHEV)": {
            3: "환경을 고려한 플러그인 하이브리드 SUV, Tucson!\n  친환경차 비율이 높은 고객님께 적합한 선택으로, 실용적인 공간과 뛰어난 연비를 자랑합니다.",
            4: "연료 효율성을 중시하는 고객님께 맞춤 추천!\n  Tucson은 플러그인 하이브리드로, 경제적인 연비와 친환경성을 모두 고려한 차량입니다."
        },
        "Grandeur (GN7 HEV)": {
            3: "고객님께 적합한 차량, Grandeur HEV! \n 실용적이고 연비가 뛰어난 하이브리드 세단으로, 경제적인 선택이면서도 고급스러운 느낌을 제공합니다.",
            5: "연비가 뛰어난 하이브리드 세단, Grandeur! \n 거래 금액이 적은 고객님께 적합하며, 실용적이고 신뢰할 수 있는 선택입니다."
        },
        "IONIQ (AE EV)": {
            4: "친환경차에 관심많은 고객님께 가격대가 적당한 전기차인 IONIQ을 추천합니다. \n IONIQ은 연료비가 적고 실용적인 전기차로 적합합니다."
        },
        "G70 (IK)": {
            2: "고객님께 고급스러움을 더할 수 있는 G70!\n  가격대가 적당하면서도 고급스러움을 갖춘 차량으로, 차별화된 경험을 선사합니다.",
            5: "고급스러운 느낌의 세단을 선호하는 고객님께, G70! \n 거래 금액이 적더라도 품격을 높여 줄 차량입니다."
        },
        "Avante (CN7 HEV)": {
            2:"가격 대비 뛰어난 성능을 자랑하는 Avante (CN7 HEV)! 뛰어난 연비와 친환경적인 장점으로 실용적인 선택이 될 것입니다.\n경제적이면서도 환경을 고려한 현명한 선택을 하세요.",
            6:"젊은 고객님들에게 더 없이 좋은 가격 대비 성능의 Avante (CN7 N)! 좋은 연비로 실용적이면서도 트렌디한 선택을 원하신다면 이 차가 바로 정답입니다."
        }
    },
    '기아': {
        "C'eed": {
            3: "중형 세단 선호 고객님께 잘 어울리는 실용적인 차량입니다.\n경제적이고 꾸준한 운전에 적합합니다.",
            5: "처음 차량 구매를 고민하는 중장년층 고객님께 합리적인 선택이 될 수 있는 차량입니다."
        },
        "C'eed CUV": {
            0: "젊은 고객층의 개성과 실용성을 모두 만족시키는 CUV 모델입니다.\n중형 차량을 선호하는 고객님께 추천드립니다.",
            3: "비친환경 성향이 강한 고객님께 가성비 좋은 중형 CUV 모델로 추천드립니다."
        },
        "Carens MPV": {
            1: "SUV와 다목적 차량을 선호하는 VIP 고객님께 가족 단위 이동에 적합한 차량입니다.",
            4: "중장년층 고객님께 넓은 공간과 실용성을 제공하는 차량으로 추천드립니다."
        },
        "Carnival": {
            0: "젊은 연령대지만 대형 차량을 선호하는 고객님께 맞는 패밀리카입니다.",
            4: "SUV 성향의 중장년 고객님께 여유로운 공간과 활용도를 제공하는 차량입니다."
        },
        "Cerato": {
            2: "젊고 세단을 선호하는 VIP 고객층에게 실용적이면서 세련된 디자인의 차량입니다.",
            3: "비친환경 성향이 강한 고객님께 합리적인 가격대의 중형 세단으로 추천합니다."
        },
        "EV5": {
            2: "중간 수준의 친환경 성향을 가진 젊은 VIP 고객님께 전기 SUV EV5를 추천드립니다.",
            4: "전기차에 관심 있는 중장년 고객님께 실속 있는 선택이 될 수 있습니다."
        },
        "EV6": {
            1: "친환경 성향이 일부 있는 SUV 선호 고객님께 고급 전기 SUV EV6를 추천드립니다.",
            2: "젊은 VIP 고객님의 라이프스타일에 맞는 미래 지향적 선택입니다."
        },
        "EV9": {
            1: "SUV를 선호하면서도 고급 친환경차에 관심 있는 VIP 고객님께 적합한 플래그십 전기차입니다.",
            4: "중장년층의 SUV 친환경 트렌드를 만족시키는 고급 전기 SUV입니다."
        },
        "Forte": {
            0: "실속을 중요시하는 젊은 고객님께 추천되는 가성비 좋은 차량입니다.",
            3: "중형 세단 중심의 일반 고객층에게 실용성과 효율성을 제공합니다."
        },
        "K2": {
            3: "경제적인 세단을 원하는 젊은 고객님께 추천드립니다.\n기초적인 운송 수단으로 훌륭합니다.",
            5: "처음 차량을 구매하려는 중장년층 고객님께 부담 없는 선택지입니다."
        },
        "K3": {
            2: "젊고 실용적인 고객층에게 적합한 세단입니다.\n디자인과 기능을 모두 만족시킵니다.",
            3: "중형 세단 위주의 일반 고객에게 적합한 차량입니다."
        },
        "K4": {
            1: "고급 세단 성향의 중장년층 VIP 고객님께 스타일과 실용성을 제공하는 모델입니다.",
            4: "SUV 선호지만 세단도 고려하는 고객님께 고급 중형 세단으로 추천드립니다."
        },
        "K5": {
            2: "세련된 디자인과 중형 세단 선호 고객님께 잘 어울리는 차량입니다.",
            5: "고민 중인 고객님께 실용성과 품격을 동시에 제공하는 선택입니다."
        },
        "KX1": {
            0: "젊은 고객님들께 적합한 콤팩트 SUV입니다.\n도심 주행과 스타일을 모두 만족합니다."
        },
        "KX3": {
            0: "중형 SUV를 선호하는 젊은 고객에게 적합한 차량입니다.",
            3: "SUV의 실용성과 세련된 감각을 동시에 고려한 고객층에 맞습니다."
        },
        "KX5": {
            1: "SUV 중심의 VIP 고객님께 적절한 중형 SUV 선택지입니다.",
            4: "중장년층 SUV 선호 고객님께 좋은 선택이 될 수 있습니다."
        },
        "KX7": {
            1: "중장년층 VIP SUV 고객에게 대형 SUV로서의 품격을 제공합니다."
        },
        "Optima / K5": {
            2: "중형 세단의 대표 주자로 젊은 VIP 고객님께 추천드립니다.\n디자인과 기능 모두 만족!",
            5: "세단 선호 성향의 중장년층 신규 고객에게도 안정적인 선택입니다."
        },
        "Pegas": {
            3: "비용 효율성과 실용성을 중시하는 고객님께 맞는 소형 세단입니다.",
            5: "가벼운 운전과 낮은 유지비를 원하는 중장년 고객님께 추천드립니다."
        },
        "Rio (pride)": {
            0: "경제성을 최우선으로 하는 젊은 고객님께 맞는 차량입니다.",
            3: "도심형 운전에 적합하며 유지비 부담이 적은 선택지입니다."
        },
        "Seltos": {
            0: "트렌디한 디자인을 선호하는 젊은 층에게 어울리는 소형 SUV입니다.",
            3: "꾸준한 SUV 사용을 원하는 일반 고객에게 적합합니다."
        },
        "Sonet": {
            0: "도심형 SUV로 젊은 고객님께 안성맞춤입니다.\n작지만 강한 실용성을 제공합니다.",
            3: "SUV 스타일을 원하지만 부담 없는 크기를 원하는 고객께 추천드립니다."
        },
        "Sorento": {
            1: "SUV를 선호하는 중장년층 VIP 고객님께 적합한 패밀리카입니다.",
            4: "공간과 실용성을 중시하는 SUV 중심 고객님께 알맞은 대형 SUV입니다."
        },
        "Sportage": {
            1: "중장년층 SUV 중심 고객에게 잘 어울리는 인기 모델입니다.",
            4: "SUV를 실용적으로 활용하시는 고객님께 추천되는 차량입니다."
        },
        "Syros": {
            0: "젊고 개성 강한 고객님께 맞는 유니크한 선택지입니다.",
            3: "차별화된 디자인을 추구하는 중형차 선호 고객님께 어울립니다."
        },
        "Telluride": {
            1: "프리미엄 SUV를 찾는 중장년층 고객에게 최적의 선택입니다.\n넓은 공간과 고급감을 모두 갖춘 대형 SUV입니다.",
            4: "가족 단위 고객님께 편안함과 스타일을 제공하는 고급 SUV입니다."
        },
        "Zhipao": {
            0: "젊은 고객층에게 새로운 스타일과 가성비를 제공하는 실속형 차량입니다."
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
        vehicle_image = vehicle_images.get(selected_vehicle, get_abs_path("img/default.png"))
        # 실제 파일 존재 여부 확인
        if not vehicle_image.exists():
            vehicle_image = get_abs_path("img/default.png")
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
            친환경차 = "True" if selected_vehicle in eco_friendly_models.get(st.session_state.get("brand", ""), []) else "False"
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

            file_path = Path(__file__).parent.parent / "data" / f"{brand}_고객데이터_신규입력용.csv"
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
                mini1_promo_email.send_welcome_email(이메일, 이름, 아이디, 가입일)
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
                mini1_promo_email.send_welcome_email(이메일, 이름, 아이디, 가입일)
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

