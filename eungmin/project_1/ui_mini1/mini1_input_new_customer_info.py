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
import project_1.ui_mini1.mini1_promo_email as promo_email
from project_1.ui_mini1.vehicle_recommendations_data import (vehicle_recommendations, vehicle_prices, vehicle_links, launch_dates, eco_friendly_models, brand_recommendations, basic_recommendations)
    

def get_abs_path(relative_path):
    """상대 경로를 절대 경로로 변환"""
    return Path(__file__).parent.parent / relative_path






# 차량 이미지 경로
IMAGE_BASE_PATH = 'img/'
vehicle_images = {
    model: get_abs_path(f"{IMAGE_BASE_PATH}{model}.png")
    for brand_models in launch_dates.values()
    for model in brand_models
}





def display_vehicle_recommendation(brand, model, cluster_id):
    
    recommendation = vehicle_recommendations.get(brand, {}).get(model, {}).get(cluster_id, {})
    
    if not recommendation:
        basic_rec = basic_recommendations.get(brand, {}).get(model, {})
        print(type(basic_rec))
        
        if basic_rec:
            # 차량 이미지 표시
            vehicle_image = vehicle_images.get(model, get_abs_path("img/default.png"))
            if vehicle_image.exists():
                col1, col2, col3 = st.columns([1, 6, 1])
                with col2:
                    st.image(str(vehicle_image), use_container_width=True)
            else:
                st.warning("차량 이미지를 불러올 수 없습니다.")
            
            # 기본 설명을 화면에 표시
            st.markdown(f"""
            <div style="
                background: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            ">
                <h2 style="text-align: center; margin: 0;">{model}</h2>
            </div>
            """, unsafe_allow_html=True)
            
            # 가격 정보 표시
            with st.expander("💰 **가격 정보**", expanded=True):
                price_info = dict(basic_rec).get("가격", "정보 없음")
                st.markdown(f"""
                <div style="
                    background: #f8f9fa;
                    padding: 12px;
                    border-radius: 8px;
                    margin-bottom: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                ">
                    <strong>가격</strong>: {price_info}
                </div>
                """, unsafe_allow_html=True)
            
            # 주요 특징 표시
            with st.expander("📝 **주요 특징**", expanded=True):
                features = basic_rec.get("주요 특징", [])
                if features:
                    for feature in features:
                        st.markdown(f"""
                        <div style="
                            background: #f0f8ff;
                            padding: 12px;
                            border-radius: 8px;
                            margin-bottom: 8px;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                            border-left: 4px solid #3498db;
                        ">
                            {feature}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="
                        background: #f0f8ff;
                        padding: 12px;
                        border-radius: 8px;
                        margin-bottom: 8px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                        border-left: 4px solid #3498db;
                    ">
                        정보 없음
                    </div>
                    """, unsafe_allow_html=True)
            
            # 타겟 고객 유형 표시
            with st.expander("🎯 **추천 고객 유형**", expanded=True):
                customer_type = basic_rec.get("타겟 고객", "정보 없음")
                st.markdown(f"""
                <div style="
                    background: #fff4e6;
                    padding: 12px;
                    border-radius: 8px;
                    margin-bottom: 12px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                    border-left: 4px solid #e67e22;
                ">
                    {customer_type}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("차량 추천 설명이 없습니다.")
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
            reasons = recommendation.get("추천이유", "")
            print(reasons)
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

# 예측을 위한 입력값을 처리하는 함수
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
            st.write(f"추천 차량 목록: {st.session_state['recommended_vehicles']}")
            st.write(cluster_id)
            st.rerun()

def step2_vehicle_selection(brand):
    st.title(f"🚗 추천 차량 목록")


    customer_segment = st.session_state.get("고객세그먼트", "N/A")
    cluster_id = st.session_state.get("Cluster", "N/A")
    age = st.session_state.get("연령", "N/A")
    gender = st.session_state.get("성별", "N/A")
    transaction_amount = st.session_state.get("거래금액", "N/A")
    
    
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
    
    # CSV 파일에 저장 (기존 파일이 있으면 추가, 없으면 새로 생성
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