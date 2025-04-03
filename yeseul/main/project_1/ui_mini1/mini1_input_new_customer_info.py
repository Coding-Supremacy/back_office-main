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

from project_1.ui_mini1.vehicle_recommendations_data import (
    launch_dates,
    eco_friendly_models,
    brand_recommendations,
    basic_recommendations,
    vehicle_links,
    vehicle_prices,
    vehicle_recommendations
)

def get_abs_path(relative_path):
    """상대 경로를 절대 경로로 변환"""
    return Path(__file__).parent.parent / relative_path







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
        vehicle_link = vehicle_links.get(brand, {}).get(selected_vehicle, "#")
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

            # 이메일 발송
            mini1_promo_email.send_welcome_email(이메일, 이름, 아이디, 가입일)
            st.success("이메일이 성공적으로 발송되었습니다.")

            # 이메일 전송 로그 저장
            log_entry = pd.DataFrame([[이메일, 이름, Cluster, datetime.now().strftime("%Y-%m-%d %H:%M:%S")]],
                                     columns=["이메일", "이름", "클러스터 ID", "전송 시간"])
            log_file_path = Path("data/이메일_전송_로그.csv")
            os.makedirs(log_file_path.parent, exist_ok=True)
            log_entry.to_csv(log_file_path, mode='a', header=not log_file_path.exists(), index=False, encoding='utf-8-sig')

            print("✅ 이메일 전송 로그 저장 완료!")
            st.session_state["step"] = 1
            time.sleep(2)
            st.rerun()
