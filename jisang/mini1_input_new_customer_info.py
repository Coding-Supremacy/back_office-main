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

from ui import mini1_promo_email
from google.cloud import translate_v2 as translate


# 경로 헬퍼 함수
def get_abs_path(relative_path):
    """상대 경로를 절대 경로로 변환"""
    base_dir = Path(__file__).parent.parent  # project_1 폴더
    return str(base_dir / relative_path)


# 클러스터 ID에 대한 설명
cluster_description = {
    0: ("평균 연령대 34.65세", "거래 금액 높음, 친환경차 비율 13.04%"),
    1: ("평균 연령대 51.35세", "VIP 세그먼트, 거래 금액 높음, 친환경차 비율 9.30%"),
    2: ("평균 연령대 60세", "신규 세그먼트, 거래 금액 적음, 친환경차 비율 0%"),
    3: ("평균 연령대 34.51세", "일반 세그먼트, 거래 금액 적당, 친환경차 비율 20.51%"),
    4: ("평균 연령대 38.55세", "거래 금액 낮음, 제품 구매 빈도 낮음, 친환경차 비율 39.39%"),
    5: ("평균 연령대 61.95세", "거래 금액 낮음, 현금 거래 비율 높음, 친환경차 비율 13.95%"),
    6: ("평균 연령대 33.52세", "거래 금액 낮음, 제품 구매 빈도 낮음, 친환경차 비율 0%"),
    7: ("평균 연령대 44.94세", "거래 금액 매우 높음, 제품 구매 빈도 낮음, 친환경차 비율 100%")
}

# 모델과 출시 년월 데이터
launch_dates = {
    'G70 (IK)': '2017-09',
    'NEXO (FE)': '2018-01',
    'Avante (CN7 N)': '2020-05',
    'G80 (RG3)': '2020-03',
    'Grandeur (GN7 HEV)': '2022-01',
    'Tucson (NX4 PHEV)': '2021-05',
    'Avante (CN7 HEV)': '2020-07',
    'IONIQ 6 (CE)': '2022-06',
    'G90 (HI)': '2022-03',
    'Santa-Fe (MX5 PHEV)': '2022-06',
}

# 친환경차 모델 목록
eco_friendly_models = [
    'NEXO (FE)', 'Avante (CN7 HEV)', 'Grandeur (GN7 HEV)', 
    'Tucson (NX4 PHEV)', 'IONIQ 6 (CE)', 'Santa-Fe (MX5 PHEV)'
]

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

# 시구 추출 함수
def extract_sigu(address):
    # '광역시', '특별시', '도' 등을 포함한 시구만 추출
    match = re.search(r'([가-힣]+(?:광역시|특별시|도)? [가-힣]+(?:시|구))', address)
    if match:
        return match.group(0)
    else:
        return "시구 없음"



# 예측을 위한 입력값을 처리하는 함수
def run_input_step1():
    st.title('📋 고객 정보 입력')

    model_path = Path(__file__).parent.parent / "mini1_model" / "svm_model.pkl"
    model = joblib.load(model_path)

    st.info("""
            #### 고객 정보를 입력하고 예측 버튼을 눌러주세요.
            #### 모든 항목은 필수입니다.
            """)

    with st.form(key="customer_info_form"):
        col1, col2 = st.columns([1, 1])
        with col1:
            # 고객 정보 입력 항목들 (성별, 생일, 고객세그먼트, 거래금액 등)
            성별 = st.selectbox("성별 선택", ["남", "여"])

            # 현재 날짜에서 20년 전의 날짜를 구하기
            today = datetime.today()
            year_20_years_ago = today.replace(year=today.year - 20)

            # 만약 오늘이 2월 29일이라면, 20년 전 날짜가 존재하지 않을 수 있기 때문에, 월과 일을 조정합니다.
            if year_20_years_ago.month == 2 and year_20_years_ago.day == 29:
                year_20_years_ago = year_20_years_ago.replace(day=28)


            # 생년월일 입력 (1900년부터 20년 전 날짜까지 선택 가능)
            생년월일 = st.date_input("생년월일 입력", min_value=datetime(1900, 1, 1), max_value=year_20_years_ago)
            if 생년월일:
                today = datetime.today()
                연령 = today.year - 생년월일.year - ((today.month, today.day) < (생년월일.month, 생년월일.day))
            고객세그먼트 = st.selectbox("고객 세그먼트 선택", ["신규", "VIP", "일반", "이탈가능"], index=0)
            거래금액 = st.number_input("고객 예산 입력", min_value=10000000, step=1000000)
            구매빈도 = st.number_input("제품 구매 빈도 입력", min_value=1, step=1, value=1)



        with col2:
            차량구분 = st.selectbox("희망 차량 구분 선택", ["준중형 세단", "중형 세단", "대형 세단", "SUV", "픽업트럭"])
            거래방식 = st.selectbox("거래 방식 선택", ["카드", "현금", "계좌이체"])
            구매경로 = st.selectbox("구매 경로 선택", ["온라인", "오프라인"], index=1)
            구매한제품 = st.selectbox("구입 희망 모델 선택", list(launch_dates.keys()))
            제품구매날짜 = st.date_input("제품 구매 날짜 입력")

        submitted = st.form_submit_button("예측하기")
        if submitted:
            # 모든 항목을 입력해야 함
            if not (성별 and 거래금액 and 구매빈도 and 차량구분 and 거래방식 and 구매경로 and 구매한제품 and 제품구매날짜):
                st.error("⚠️ 모든 항목을 입력해야 합니다!")
                st.stop()

            # 생년월일로 연령 계산
            today = datetime.today()
            연령 = today.year - 생년월일.year - ((today.month, today.day) < (생년월일.month, 생년월일.day))

            # 세션 상태에 입력된 값을 저장
            st.session_state["성별"] = 성별
            st.session_state["생년월일"] = 생년월일
            st.session_state["고객세그먼트"] = 고객세그먼트
            st.session_state["거래금액"] = 거래금액
            st.session_state["구매빈도"] = 구매빈도
            st.session_state["차량구분"] = 차량구분
            st.session_state["거래방식"] = 거래방식
            st.session_state["구매경로"] = 구매경로
            st.session_state["구매한제품"] = 구매한제품
            st.session_state["제품구매날짜"] = 제품구매날짜
            st.session_state["연령"] = 연령
            st.session_state["제품구매빈도"] = 구매빈도
            st.session_state["제품구매경로"] = 구매경로
            st.session_state["제품출시년월"] = launch_dates.get(구매한제품)



            # 예측 데이터 준비
            input_data = pd.DataFrame([[연령, 거래금액, 구매빈도, 성별, 차량구분, 거래방식, launch_dates.get(구매한제품), 제품구매날짜, 고객세그먼트, "여" if 구매한제품 in eco_friendly_models else "부"]],
                                    columns=["연령", "거래 금액", "제품 구매 빈도", "성별", "차량구분", "거래 방식", "제품 출시년월", "제품 구매 날짜", "고객 세그먼트", "친환경차"])

            # 예측 실행
            prediction = model.predict(input_data)
            cluster_id = prediction[0]

            st.session_state["Cluster"] = cluster_id
            st.session_state["step"] = 2  # 차량 선택 단계로 넘어가기
            st.session_state["recommended_vehicles"] = get_recommended_vehicles(cluster_id)
            st.rerun()




# 차량 추천 (친환경차 여부 포함)
def get_recommended_vehicles(cluster_id):
    recommended_vehicles = []

    if cluster_id == 0:
        recommended_vehicles = [
            'Avante (CN7 N)','NEXO (FE)'
        ]
    elif cluster_id == 1:
        recommended_vehicles = [
            'G90 (HI)','IONIQ 6 (CE)'
        ]
    elif cluster_id == 2:
        recommended_vehicles = [
            'G70 (IK)','Avante (CN7 HEV)'
        ]
    elif cluster_id == 3:
        recommended_vehicles = [
            'Avante (CN7 N)','Tucson (NX4 PHEV)','Grandeur (GN7 HEV)'
        ]
    elif cluster_id == 4:
        recommended_vehicles = [
            'NEXO (FE)','Tucson (NX4 PHEV)'
        ]
    elif cluster_id == 5:
        recommended_vehicles = [
            'G70 (IK)','Grandeur (GN7 HEV)'
        ]
    elif cluster_id == 6:
        recommended_vehicles = [
            'Avante (CN7 N)','Avante (CN7 HEV)'
        ]
    elif cluster_id == 7:
        recommended_vehicles = [
            'IONIQ 6 (CE)','NEXO (FE)'
        ]
    return recommended_vehicles



# 2단계: 고객이 모델 선택 후 인적 사항 입력
def step2_vehicle_selection():
    st.title("🚗 추천 차량 선택")

    # 세션 상태에서 필요한 값 가져오기
    cluster_id = st.session_state.get("Cluster")
    recommended_vehicles = st.session_state.get("recommended_vehicles", [])
    customer_type, characteristics = cluster_description.get(cluster_id, ("알 수 없는 클러스터", "특징 정보 없음"))
    selected_vehicle = st.session_state.get("selected_vehicle", "")

    # 기본 경로를 정의
    IMAGE_BASE_PATH = 'mini1_img/'

    # 파일명만 따로 분리해서 관리
    vehicle_image_files = {
        'G70 (IK)': 'g70.png',
        'Santa-Fe ™': 'santafe.png',
        'NEXO (FE)': 'NEXO.png',
        'Avante (CN7 N)': 'Avante (CN7 N).png',
        'G80 (RG3)': 'g80.png',
        'Grandeur (GN7 HEV)': 'Grandeur.png',
        'IONIQ (AE EV)': 'IONIQ.png',
        'i30 (PD)': 'i30.png',
        'Palisade (LX2)': 'PALISADE.png',
        'Tucson (NX4 PHEV)': 'TUCSON.png',
        'Avante (CN7 HEV)': 'Avante.png',
        'IONIQ 6 (CE)': 'IONIQ6.png',
        'G90 (HI)': 'G90.jpg',
        'Santa-Fe (MX5 PHEV)': 'Santa-FePHEV.png',
        'G90 (RS4)': 'G90.jpg'
    }

    # 최종 딕셔너리 생성
    vehicle_images = {
        name: get_abs_path(IMAGE_BASE_PATH + filename)
        for name, filename in vehicle_image_files.items()
    }
    # 차량에 대한 기본적인 추천 멘트
    basic_recommendations = {
    "Avante (CN7 N)": "Avante (CN7 N)은 실용성과 세련된 디자인을 갖춘 최신형 준중형 세단입니다. 안정적인 주행과 뛰어난 연비 효율을 제공합니다.",
    "NEXO (FE)": "NEXO는 수소 연료 기반의 친환경 SUV로, 정숙하고 매끄러운 주행감을 제공하며, 미래지향적인 기술이 적용된 모델입니다.",
    "G80 (RG3)": "G80은 고급스러운 외관과 세련된 인테리어, 뛰어난 주행 성능을 갖춘 프리미엄 세단입니다.",
    "G90 (HI)": "G90은 정교한 설계와 탁월한 승차감을 제공하는 고급 세단으로, 품격 있는 드라이빙 경험을 원하는 분들께 적합합니다.",
    "IONIQ 6 (CE)": "IONIQ 6는 유려한 디자인과 최첨단 전기차 기술을 결합한 모델로, 효율적이고 조용한 주행이 특징입니다.",
    "Tucson (NX4 PHEV)": "Tucson PHEV는 플러그인 하이브리드 SUV로, 전기 모드와 엔진 모드를 자유롭게 전환하며 뛰어난 연비와 성능을 제공합니다.",
    "Grandeur (GN7 HEV)": "Grandeur HEV는 고급스러운 디자인과 효율적인 하이브리드 시스템을 갖춘 준대형 세단입니다.",
    "G70 (IK)": "G70은 스포티한 디자인과 민첩한 주행 성능을 갖춘 고급 중형 세단으로, 역동적인 드라이빙을 즐길 수 있습니다.",
    "Santa-Fe (MX5 PHEV)": "Santa-Fe PHEV는 전기와 엔진의 조화를 이루는 플러그인 하이브리드 SUV로, 효율성과 주행 편의성을 동시에 갖췄습니다.",
    "Avante (CN7 HEV)": "Avante HEV는 연비 효율이 뛰어난 하이브리드 세단으로, 실용성과 친환경 기술이 조화를 이루는 모델입니다."

    }

    # 차량 링크 매핑
    vehicle_links = {
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
    }

    # 차량 가격 매핑
    vehicle_prices = {
        "Avante (CN7 N)": "19640000","NEXO (FE)": "69500000","G80 (RG3)": "82750000","G90 (HI)": "129600000","IONIQ 6 (CE)": "46950000","Tucson (NX4 PHEV)": "27290000","Grandeur (GN7 HEV)": "37110000","G70 (IK)": "45240000","Santa-Fe (MX5 PHEV)": "34920000","Avante (CN7 HEV)": "33090000"
    }

    # 클러스터별 차량 추천 이유 매핑
    vehicle_recommendations = {
    "Avante (CN7)": {
        0: {
            "description": "1.6L 가솔린 엔진의 경제적 준중형 세단으로, 연비 15.2km/L의 효율성을 자랑합니다. 6에어백과 스마트스트림 엔진이 적용되어 안전성과 연비를 동시에 잡았으며, 475L의 넉넉한 트렁크 공간으로 가족용으로도 적합합니다.",
            "recommended_trim": "Smart (가솔린 1.6)",
            "trim_price": "2,475",
            "recommended_option": "어반 세이프티 패키지",
            "option_price": "132",
            "total_price": "2,607",
            "reason": "40~50대 중년층이 합리적인 가격대와 현대자동차의 안정적인 A/S 네트워크를 믿고 선택할 수 있는 가성비 모델. 저렴한 유지비와 보험료가 부담 없는 것이 장점입니다."
        },
        3: {
            "description": "고속도로 주행 최적화 세단으로, 하이웨이 드라이빙 어시스트(차선 유지/차간 거리 자동 조절)가 장거리 운전 피로도를 30% 이상 줄여줍니다. 1.6L 가솔린 엔진과 7단 DCT 변속기의 조합으로 고속 주행 시에도 연비 16.1km/L를 유지합니다.",
            "recommended_trim": "Modern (가솔린 1.6)",
            "trim_price": "2,350",
            "recommended_option": "하이웨이 드라이빙 어시스트",
            "option_price": "90",
            "total_price": "2,440",
            "reason": "주말마다 고향을 오가거나 자녀 대학 통학을 위해 월 1,500km 이상 장거리 운전하는 50대 중장년층에게 최적. 고속도로 주행 시 안정성과 연비 효율성을 동시에 충족합니다."
        },
        5: {
            "description": "첫 구매자를 위한 안정적인 세단으로, 후방 카메라와 긴급 제동 시스템이 기본 적용되어 초보 운전자의 주차 및 도심 주행을 지원합니다. 10.25인치 내비게이션과 애플 카플레이 연동으로 편의성을 높였습니다.",
            "recommended_trim": "Modern (가솔린 1.6)",
            "trim_price": "2,350",
            "recommended_option": "라이트 에디션",
            "option_price": "65",
            "total_price": "2,415",
            "reason": "40대 중반~50대 초반의 첫 차 구매자들이 부담 없이 선택할 수 있는 진입 장벽 완화 모델. 할부 금융 상품과 5년 무상 A/S가 결합되어 신규 고객 유입에 효과적입니다."
        }
    },
    "G70 (IK)": {
        0: {
            "description": "2.0L 가솔린 터보 엔진(245마력)을 탑재한 소형 럭셔리 세단. 전자식 컨트롤 댐퍼와 19인치 알로이 휠로 주행 안정성을 높였으며, 퀼팅 난나카 가죽 시트와 12.3인치 클러스터로 고급스러움을 강조했습니다.",
            "recommended_trim": "Premium (2.0T)",
            "trim_price": "4,250",
            "recommended_option": "베이직 플러스 패키지",
            "option_price": "95",
            "total_price": "4,345",
            "reason": "50대 이상 중년 남성층이 BMW 3시리즈 대신 합리적인 가격으로 프리미엄 브랜드 체험을 원할 때 선택. 제네시스 전용 콜 서비스와 발코니가 있는 전시장이 고객의 프리미엄 니즈를 충족시킵니다."
        },
        5: {
            "description": "첫 프리미엄 차량 구매자를 위한 모델로, 2.0L 터보 엔진의 기본 성능은 유지하되 내장재 등 비필수 사양을 간소화했습니다. 주차 보조 패키지(후측방 모니터링/자동 주차)가 도심 생활 편의성을 높입니다.",
            "recommended_trim": "Standard (2.0T)",
            "trim_price": "3,980",
            "recommended_option": "주차 보조 패키지",
            "option_price": "70",
            "total_price": "4,050",
            "reason": "45~55세 연령대에서 첫 프리미엄 차량 구매를 고려하는 신규 고객을 위한 전략적 모델. 3년 무상 유지보스와 1:1 전담 상담원 서비스가 구매 결정을 유도합니다."
        }
    },
    "IONIQ 6 (CE)": {
        1: {
            "description": "AWD 고성능 전기차로 320kW 듀얼 모터 적용 시 0-100km/h 가속 5.1초 가능. 20인치 휠과 스포츠 서스펜션, 가상 엔진 사운드 시스템으로 주행 재미를 극대화했습니다. 400V 초고속 충전 시 18분 충전으로 351km 주행 가능.",
            "recommended_trim": "Premium (AWD)",
            "trim_price": "6,450",
            "recommended_option": "퍼포먼스 패키지",
            "option_price": "290",
            "total_price": "6,740",
            "reason": "30대 젊은 남성층이 테슬라 모델 3 퍼포먼스 대안으로 선택. 레이싱 게임 연동 기능과 N 퍼포먼스 튜닝 파츠 호환성을 강점으로 어필합니다."
        },
        2: {
            "description": "우드 그레인 대시보드와 리사이클드 PET 소재 시트가 적용된 친환경 럭셔리 모델. 공기 청정 모드와 마사지 시트로 여성 운전자의 피로를 줄여주며, 18인치 에어로 휀로 연비 효율성(6.2km/kWh)을 극대화했습니다.",
            "recommended_trim": "Exclusive (RWD)",
            "trim_price": "5,780",
            "recommended_option": "럭셔리 인테리어 패키지",
            "option_price": "240",
            "total_price": "6,020",
            "reason": "50대 이상 여성 고객이 메르세데스 EQS의 고가 부담을 줄이면서도 프리미엄 인테리어를 원할 때 적합. 현대카드 마일리지 5% 적립 프로모션과 결합해 마케팅 효과가 높습니다."
        },
        4: {
            "description": "에어로 다이내믹 디자인으로 Cd 0.21의 초저항 계수를 구현한 전기차. RWD 사양으로 524km의 장거리 주행이 가능하며, 스포츠 서스펜션으로 코너링 안정성을 높였습니다. V2L 기능으로 캠핑 시 전기 사용이 가능합니다.",
            "recommended_trim": "Exclusive (RWD)",
            "trim_price": "5,780",
            "recommended_option": "스포츠 서스펜션",
            "option_price": "120",
            "total_price": "5,900",
            "reason": "20~30대 젊은 층이 디자인과 실용성을 동시에 추구할 때 선택. 인스타그램 친화적인 컬러 옵션(디지털 티 그린)과 SNS 인증 이벤트 패키지가 판매 촉진 요소입니다."
        }
    },
    "Grandeur (GN7 HEV)": {
        1: {
            "description": "1.6L 하이브리드 시스템으로 연비 17.8km/L를 구현한 럭셔리 세단. 열선 스티어링 휠과 통풍 시트가 포함된 VIP 윈터 패키지로 한파 대비를 완벽하게 했으며, 12.3인치 오버헤드 디스플레이로 후석 만족도를 높였습니다.",
            "recommended_trim": "Inspiration (HEV)",
            "trim_price": "5,120",
            "recommended_option": "VIP 윈터 패키지",
            "option_price": "210",
            "total_price": "5,330",
            "reason": "55~65세 기업 임원층이 전기차 충전 인프라 불편을 피하면서도 환경 규제 대응을 위해 선택. 리스 상품과 결합 시 세금 혜택이 30% 이상 높아지는 점이 장점입니다."
        },
        2: {
            "description": "최상위 하이브리드 세단으로, 12스피커의 렉시컨 사운드 시스템과 공기 청정 기능이 탑재된 프레스티지 트림. 헬스 케어 패키지(생체 신호 모니터링/피로도 감지)로 장시간 운전 시 건강을 관리할 수 있습니다.",
            "recommended_trim": "Prestige (HEV)",
            "trim_price": "5,890",
            "recommended_option": "헬스 케어 패키지",
            "option_price": "370",
            "total_price": "6,260",
            "reason": "건강과 웰빙을 중시하는 50대 여성 고객층이 선호. 병원 방문용 차량으로 적합하며, 1년 무제한 건강 검진 쿠폰 제공이 구매 결정에 영향을 줍니다."
        }
    },
    "Tucson (NX4 PHEV)": {
        0: {
            "description": "플러그인 하이브리드 SUV로, 44.5km의 전기 주행 거리와 가솔린 모드 연비 16.4km/L를 동시에 확보. 에코 코스팅 시스템이 신호등 구간에서 에너지 회수 효율을 25% 높여줍니다. 589L의 대용량 트렁크로 캠핑 용품 수납이 용이합니다.",
            "recommended_trim": "Standard (PHEV)",
            "trim_price": "4,890",
            "recommended_option": "에코 코스팅 시스템",
            "option_price": "80",
            "total_price": "4,970",
            "reason": "45~55세 중년 남성층이 기존 가솔린 SUV에서 연비 부담을 해소하기 위해 전환하는 모델. 주말 레저 활동(골프/등산) 시 장비 운반용으로도 적합합니다."
        },
        3: {
            "description": "장거리 주행 최적화 PHEV로, 13.8kWh 대용량 배터리와 2.0L 가솔린 엔진의 조합이 최대 720km의 종합 주행 거리를 제공. 컴포트 플러스 패키지(통풍 시트/어드밴스드 크루즈 컨트롤)로 장시간 운전 피로를 최소화했습니다.",
            "recommended_trim": "Premium (PHEV)",
            "trim_price": "5,120",
            "recommended_option": "컴포트 플러스",
            "option_price": "140",
            "total_price": "5,260",
            "reason": "월 2,000km 이상 장거리 출퇴근을 하는 50대 중반 고객을 타깃. 회사 차량 인센티브와 결합 시 PHEV의 세제 혜택이 일반 하이브리드 대비 15% 더 유리합니다."
        },
        5: {
            "description": "신용카드 할부에 최적화된 PHEV 모델로, 스마트 키 시스템(핸드폰 디지털 키/원격 시동)이 기본 적용되었습니다. 5년 무상 충전권(1,000kWh) 제공으로 초기 운영 비용을 절감할 수 있습니다.",
            "recommended_trim": "Standard (PHEV)",
            "trim_price": "4,890",
            "recommended_option": "스마트 키 시스템",
            "option_price": "60",
            "total_price": "4,950",
            "reason": "40대 후반 신규 PHEV 구매자들의 진입 장벽을 낮추기 위한 모델. 현대카드 36개월 무이자 할부와 결합 시 월 137,000원대의 부담 없는 구매가 가능합니다."
        }
    },
    "Santa-Fe (MX5 PHEV)": {
        2: {
            "description": "7인승 PHEV SUV로, 2.5L 가솔린 엔진과 66.9km의 전기 주행 거리를 결합. 캡틴 시트 패키지(2열 통풍 시트/릴렉션 모드)로 대가족 이동 시 편의성을 제공하며, 3열 공간에 어린이 카시트 고정 장치가 기본 장착되었습니다.",
            "recommended_trim": "Calligraphy (PHEV)",
            "trim_price": "6,350",
            "recommended_option": "캡틴 시트 패키지",
            "option_price": "250",
            "total_price": "6,600",
            "reason": "다자녀(3명 이상) 가정의 30대 후반~40대 여성 고객이 미니밴 대체용으로 선택. 어린이 승하차 보조 시스템과 결합 시 육아 부담을 40% 이상 줄여줍니다."
        },
        4: {
            "description": "53km 전기주행 가능 PHEV 모델로, 스타일 패키지(20인치 휠/듀얼 머플러)로 디자인을 강화했습니다. 2열 폴딩 테이블과 12V 전원 포트 4개가 적용되어 젊은 가족의 캠핑/피크닉需求에 대응합니다.",
            "recommended_trim": "Premium (PHEV)",
            "trim_price": "5,890",
            "recommended_option": "스타일 패키지",
            "option_price": "150",
            "total_price": "6,040",
            "reason": "친환경 차량을 원하지만 전기차 충전 인프라가 부족한 지방 거주 30대 부부에게 적합. 전기 모드로 일상 이동 시 연료비를 70% 이상 절감할 수 있는 점을 강조합니다."
        }
    },
    "NEXO (FE)": {
        1: {
            "description": "수소전기차 플래그십 모델로, 6.33kg의 수소 충전으로 666km 주행이 가능합니다. 테크 패키지(AR HUD/리모트 스마트 파킹)가 적용되었으며, 공기 청정 시스템이 실내 미세먼지를 99.9% 제거합니다.",
            "recommended_trim": "Premium",
            "trim_price": "7,250",
            "recommended_option": "테크 패키지",
            "option_price": "320",
            "total_price": "7,570",
            "reason": "미래 기술을 선도하는 IT 업계 종사자(25~35세)가 선택. 정부 보조금(4,250만원)과 수소 충전 무료 쿠폰(3년) 제공으로 실구매 가격을 5,000만원대로 낮출 수 있습니다."
        }
    },
    "G90 (HI)": {
        3: {
            "description": "3.5L 가솔린 터보 엔진(380마력)을 탑재한 플래그십 럭셔리 세단. 리무진 패키지(전동식 뒷좌석/25스피커 뱅앤올룹슨 오디오)가 적용되었으며, 전용 스마트폰 앱으로 뒷좌석 환경(온도/조명/마사지)을 제어할 수 있습니다.",
            "recommended_trim": "Prestige (3.5T)",
            "trim_price": "8,450",
            "recommended_option": "리무진 패키지",
            "option_price": "490",
            "total_price": "8,940",
            "reason": "고빈도 비즈니스 이동이 많은 50대 이상 기업 대표층을 타깃. 전용 기사 교육 프로그램과 24시간 VIP 콜 서비스가 제공되어 '이동형 오피스'로 최적화되었습니다."
        }
    }
}



    st.info("고객님의 성향에 맞춘 추천차량 목록입니다.")

    # 고객이 선택한 구입 희망 모델
    구매한제품 = st.session_state.get("구매한제품", "")

    # 추천 차량 목록에 고객이 고른 모델이 없으면 추가
    if 구매한제품 and 구매한제품 not in recommended_vehicles:
        recommended_vehicles.append(구매한제품)
    
    if recommended_vehicles:
        # 차량 선택
        selected_vehicle = st.selectbox("구입 희망 차량을 선택하세요", recommended_vehicles, key="vehicle_select_box", index=recommended_vehicles.index(st.session_state.get("selected_vehicle", recommended_vehicles[0])))
        
        if selected_vehicle:
            # 차량 이미지 가져오기
            vehicle_image = vehicle_images.get(selected_vehicle, "img/default.png")
            # 차량 링크 가져오기
            vehicle_link = vehicle_links.get(selected_vehicle, "#")
            # 차량 설명 가져오기
            vehicle_description = vehicle_recommendations.get(selected_vehicle, {}).get(cluster_id, basic_recommendations.get(selected_vehicle, "차량에 대한 정보가 없습니다."))
            # 차량 가격 가져오기
            vehicle_price = vehicle_prices.get(selected_vehicle, "가격 정보 없음")
            
            # 이미지 출력과 링크 추가
            
            st.image(vehicle_image, use_container_width=True)
            st.text(vehicle_description)
            st.markdown(f"[차량 상세정보 확인하기]({vehicle_link})", unsafe_allow_html=True)
            st.text(f"가격: {vehicle_price}원")

        else:
            st.warning("추천 차량이 없습니다. 다시 예측을 시도해 주세요.")

        #차량 가격을 구매한금액
        
        # 차량 선택 완료 버튼
        submit_button = st.button("선택 완료")
        if submit_button:
            st.session_state["거래금액"] = vehicle_price #최종 선택 차량의 가격을 거래금액으로 저장
            st.session_state["selected_vehicle"] = selected_vehicle
            st.success(f"{selected_vehicle} 선택 완료! 이제 고객 정보를 저장합니다.")
            st.session_state["step"] = 3  # 고객 정보 저장 단계로 이동
            # 화면 새로고침
            st.rerun()
            


def step3_customer_data_storage():
    st.title("📝 고객 정보 입력 및 저장")

    # 고객 정보 입력 폼
    with st.form(key="customer_info_form"):
        이름 = st.text_input("이름")
        # 📌 **휴대폰 번호 입력 및 즉시 검증**
        휴대폰번호 = st.text_input("휴대폰 번호 입력", placeholder="필수입니다.", key="phone_input")
        # 하이픈을 포함한 휴대폰 번호 포맷팅
        휴대폰번호 = re.sub(r'[^0-9]', '', 휴대폰번호)  # 숫자만 추출
        if 휴대폰번호 and not re.fullmatch(r"\d{11}", 휴대폰번호):
            st.session_state["phone_error"] = True
        else:
            st.session_state["phone_error"] = False
        # 오류 메시지 표시
        if st.session_state["phone_error"]:
            st.error("⚠️ 휴대폰 번호는 11자리 숫자여야 합니다. (예: 01012345678)")
        이메일 = st.text_input("이메일 입력", placeholder="필수입니다.", key="email_input")
        
        if 이메일 and ("@" not in 이메일 or "." not in 이메일):
            st.session_state["email_error"] = True
        else:
            st.session_state["email_error"] = False
        # 오류 메시지 표시
        if st.session_state["email_error"]:
            st.error("⚠️ 이메일 주소 형식이 올바르지 않습니다. '@'와 '.'을 포함해야 합니다.")

        주소 = st.text_input("주소")
        아이디 = st.text_input("아이디")
        가입일 = st.date_input("가입일")

        # 고객 정보 저장하기 버튼
        submit_button = st.form_submit_button("고객정보 저장하기")

        if submit_button:
            if not (이름 and 휴대폰번호 and 이메일 and 주소 and 아이디 and 가입일):
                st.error("⚠️ 모든 항목을 입력해야 합니다!")
                st.stop()

            # 입력된 고객 정보 세션 상태에 저장
            st.session_state["name"] = 이름
            st.session_state["phone"] = 휴대폰번호
            st.session_state["email"] = 이메일
            st.session_state["address"] = 주소
            st.session_state["id"] = 아이디
            st.session_state["registration_date"] = 가입일

            # 세션 상태에서 다른 필요한 값 가져오기
            연령 = st.session_state.get("연령", "")
            생년월일 = st.session_state.get("생년월일", "")
            성별 = st.session_state.get("성별", "")
            고객세그먼트 = st.session_state.get("고객세그먼트", "")
            selected_vehicle = st.session_state.get("selected_vehicle", "")
            차량구분 = st.session_state.get("차량구분", "")
            친환경차 = "여" if selected_vehicle in eco_friendly_models else "부"
            구매한제품 = selected_vehicle
            제품구매날짜 = st.session_state.get("제품구매날짜", "")
            거래금액 = st.session_state.get("거래금액", "")
            거래방식 = st.session_state.get("거래방식", "")
            구매빈도 = st.session_state.get("제품구매빈도", "")
            제품구매경로 = st.session_state.get("제품구매경로", "")
            제품출시년월 = launch_dates.get(selected_vehicle, "")
            Cluster = st.session_state.get("Cluster", "")
            연령 = st.session_state.get("연령", "")
            구매빈도= st.session_state.get("구매빈도", "")
            제품출시년월= st.session_state.get("제품출시년월", "")

            # 주소에서 시구 추출
            시구 = extract_sigu(주소)

            # 고객 정보 저장
            full_data = pd.DataFrame([[이름, 생년월일, 연령, 성별, 휴대폰번호, 이메일, 주소, 아이디, 가입일, 고객세그먼트, 
                                       차량구분, 구매한제품, 친환경차, 제품구매날짜, 거래금액, 거래방식, 구매빈도, 제품구매경로, 제품출시년월, Cluster, 시구]],
                                    columns=["이름", "생년월일", "연령", "성별", "휴대폰번호", "이메일", "주소", "아이디", "가입일", 
                                             "고객 세그먼트", "차량구분", "구매한 제품", "친환경차", "제품 구매 날짜", "거래 금액", 
                                             "거래 방식", "제품 구매 빈도", "제품 구매 경로", "제품 출시년월", "Cluster", "시구"])

            # 1. 절대 경로로 변환 (프로젝트 루트 기준)
            file_path = Path(__file__).parent.parent / "data_mini1" / "클러스터링고객데이터_5.csv"

            # 2. 디렉토리 생성 (없을 경우)
            os.makedirs(file_path.parent, exist_ok=True)  # exist_ok=True: 이미 있으면 무시

            # 3. 파일 존재 여부 확인 (안전한 방법)
            file_exists = file_path.exists()

            # 4. CSV 저장 (인코딩 명시)
            full_data.to_csv(file_path, mode='a', header=not file_exists, index=False, encoding='utf-8-sig')


            # 문자 발송
            clicksend_username = st.secrets["CLICKSEND"]["CLICKSEND_USERNAME"]
            clicksend_api_key = st.secrets["CLICKSEND"]["CLICKSEND_API_KEY"]
            to_number = "+82" + 휴대폰번호[1:]  # 국내 번호 형식으로 변환
            message_body = f"안녕하세요, {이름}님! 현대 자동차에서 보내드리는 메시지입니다. 멤버십 가입을 축하드리며, 다양한 혜택과 서비스를 경험해보세요!"

            # ClickSend API 호출 (문자 발송)
            url = "https://rest.clicksend.com/v3/sms/send"
            auth_header = f"Basic {base64.b64encode(f'{clicksend_username}:{clicksend_api_key}'.encode()).decode()}"

            headers = {"Authorization": auth_header, "Content-Type": "application/json"}

            data = {"messages": [{"source": "sdk", "body": message_body, "to": to_number}]}

            try:
                response = requests.post(url, headers=headers, json=data)
                st.success("문자가 성공적으로 발송되었습니다.")
            except Exception as e:
                st.error("문자 발송에 실패했습니다.")
                print("Error sending SMS:", e)

            # 이메일 발송
            mini1_promo_email.send_welcome_email(이메일, 이름, 아이디, 가입일)
            st.success("이메일이 성공적으로 발송되었습니다.")


            # 📌 이메일 전송 로그 저장
            log_entry = pd.DataFrame([[이메일, 이름, Cluster, datetime.now().strftime("%Y-%m-%d %H:%M:%S")]],
                                    columns=["이메일", "이름", "클러스터 ID", "전송 시간"])

            # 📌 CSV 파일 경로
            log_file_path = r'main_project\project_1\data_mini1\이메일_전송_로그.csv'

            # 📌 파일이 없으면 새로 생성
            if not os.path.exists(log_file_path):
                log_entry.to_csv(log_file_path, mode='w', header=True, index=False)  # 새로운 파일 생성
                print(f"📄 새 이메일 전송 로그 파일 생성됨: {log_file_path}")
            else:
                log_entry.to_csv(log_file_path, mode='a', header=False, index=False)  # 기존 파일에 추가

            print("✅ 이메일 전송 로그 저장 완료!")
            st.session_state["step"] = 1
            time.sleep(2)
            st.rerun()