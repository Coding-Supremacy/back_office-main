import streamlit as st
import requests

# API 엔드포인트 설정
api_url = "https://www.vinaudit.com/vehicle-market-value-api"  # 실제 엔드포인트가 아닐 수 있음

# 사용자 입력 받기
st.title("중고차 시장 가치 조회")
make_model_trim = st.text_input("차량 모델 (예: 2016 Mazda MX-5 Miata Club)")
mileage = st.number_input("주행 거리")

# API 호출
if st.button("조회 시작"):
    params = {
        "make_model_trim": make_model_trim,
        "mileage": mileage
    }
    
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()  # 상태 코드가 200이 아니면 예외 발생
        
        # API 응답 처리
        data = response.json()
        st.write(data)
    except requests.exceptions.RequestException as e:
        st.error(f"API 요청 실패: {e}")