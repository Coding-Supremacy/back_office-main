import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from io import BytesIO

# ------------------------------
# 1. 데이터 로드 및 전처리
# ------------------------------
@st.cache_data
def load_data(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
        required_cols = ['연도', '국가명', '모델명', '판매량', '브랜드', '파워트레인']
        if not all(col in df.columns for col in required_cols):
            st.error(f"필수 컬럼 누락: {', '.join(required_cols)}")
            return None
        return df
    except Exception as e:
        st.error(f"파일 읽기 오류: {str(e)}")
        return None

# ------------------------------
# 2. 고급 분석 기능
# ------------------------------
def show_sales_trend(df, country, model):
    """시계열 판매 추이 분석"""
    filtered = df[(df['국가명'] == country) & (df['모델명'] == model)]
    if filtered.empty:
        st.warning("해당 조건에 맞는 데이터가 없습니다.")
        return
    
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(filtered['연도'], filtered['판매량'], marker='o', linewidth=2)
    ax.set_title(f"{country} - {model} 판매 추이", fontsize=14)
    ax.set_xlabel("연도")
    ax.set_ylabel("판매량 (대)")
    ax.grid(True, linestyle='--', alpha=0.6)
    st.pyplot(fig)

def show_powertrain_share(df, country, year):
    """파워트레인별 점유율 시각화"""
    filtered = df[(df['국가명'] == country) & (df['연도'] == year)]
    if filtered.empty:
        st.warning("데이터가 없습니다.")
        return
    
    pt_df = filtered.groupby('파워트레인')['판매량'].sum().reset_index()
    
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(pt_df['판매량'], 
           labels=pt_df['파워트레인'],
           autopct='%1.1f%%',
           startangle=90,
           wedgeprops={'width': 0.4})
    ax.set_title(f"{year}년 {country} 파워트레인 점유율", fontsize=12)
    st.pyplot(fig)

def calculate_competitiveness(df, brand, country):
    """브랜드 경쟁력 지수 계산 (가중 평균)"""
    filtered = df[(df['브랜드'] == brand) & (df['국가명'] == country)]
    if filtered.empty:
        return 0
    
    # 가중치: 연도 최신일수록 높은 가중치 (2025년=5, 2024년=4, ...)
    filtered['weight'] = filtered['연도'] - 2020
    total_sales = np.average(filtered['판매량'], weights=filtered['weight'])
    return round(total_sales / 1000, 2)  # 단위 조정

def predict_sales(df, country, model):
    """간단한 선형 회귀 예측"""
    filtered = df[(df['국가명'] == country) & (df['모델명'] == model)]
    if len(filtered) < 2:
        st.warning("예측을 위해 최소 2년 이상 데이터가 필요합니다.")
        return None
    
    X = filtered['연도'].values.reshape(-1, 1)
    y = filtered['판매량'].values
    
    model_lr = LinearRegression()
    model_lr.fit(X, y)
    next_year = filtered['연도'].max() + 1
    predicted = model_lr.predict([[next_year]])[0]
    
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.scatter(X, y, color='blue', label='실적')
    ax.plot(X, model_lr.predict(X), color='red', label='예측 추세선')
    ax.set_title(f"{model} 판매 예측 ({next_year}년)", fontsize=12)
    ax.set_xlabel("연도")
    ax.set_ylabel("판매량")
    ax.legend()
    st.pyplot(fig)
    
    return max(0, round(predicted))

# ------------------------------
# 3. 메인 애플리케이션
# ------------------------------
def main():
    st.set_page_config(
        page_title="고급 판매 분석 도구",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🚗 자동차 판매 고급 분석 도구")
    uploaded_file = st.file_uploader("CSV 파일 업로드", type=["csv"])
    
    if not uploaded_file:
        st.info("📌 예시 파일 형식: 연도,국가명,모델명,판매량,브랜드,파워트레인")
        return
    
    df = load_data(uploaded_file)
    if df is None:
        return
    
    # ------------------------------
    # 분석 패널
    # ------------------------------
    st.sidebar.header("분석 조건")
    country = st.sidebar.selectbox("국가 선택", sorted(df['국가명'].unique()))
    year = st.sidebar.selectbox("연도 선택", sorted(df['연도'].unique(), reverse=True))
    brand = st.sidebar.selectbox("브랜드 선택", sorted(df['브랜드'].unique()))
    
    tab1, tab2, tab3, tab4 = st.tabs(["대시보드", "시계열 분석", "경쟁력 지수", "데이터 탐색기"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("TOP 3 모델")
            top3 = df[(df['국가명'] == country) & (df['연도'] == year)]\
                   .nlargest(3, '판매량')[['모델명', '판매량', '브랜드']]
            st.dataframe(top3.style.format({'판매량': '{:,.0f}대'}))
        
        with col2:
            st.subheader("파워트레인 점유율")
            show_powertrain_share(df, country, year)
    
    with tab2:
        model = st.selectbox(
            "모델 선택", 
            df[df['국가명'] == country]['모델명'].unique())
        
        st.subheader("판매 추이 분석")
        show_sales_trend(df, country, model)
        
        st.subheader("내년 예측")
        predicted = predict_sales(df, country, model)
        if predicted:
            st.success(f"예상 판매량: {predicted:,.0f}대")
    
    with tab3:
        st.subheader("브랜드 경쟁력 지수")
        score = calculate_competitiveness(df, brand, country)
        st.metric(
            label=f"{brand} in {country}",
            value=score,
            help="최근 5년 판매량 가중 평균 (단위: 천 대)"
        )
        
        # 경쟁사 비교
        competitors = df[df['국가명'] == country]['브랜드'].unique()
        comp_df = pd.DataFrame({
            '브랜드': competitors,
            '경쟁력 지수': [calculate_competitiveness(df, b, country) for b in competitors]
        }).sort_values('경쟁력 지수', ascending=False)
        
        st.dataframe(
            comp_df.style.format({'경쟁력 지수': '{:.2f}'}),
            height=300
        )
    
    with tab4:
        st.subheader("원본 데이터 필터링")
        
        col1, col2 = st.columns(2)
        with col1:
            years = st.multiselect(
                "연도 필터",
                options=sorted(df['연도'].unique()),
                default=[year]
            )
        with col2:
            brands = st.multiselect(
                "브랜드 필터",
                options=sorted(df['브랜드'].unique()),
                default=[brand]
            )
        
        filtered = df[
            (df['국가명'] == country) &
            (df['연도'].isin(years)) &
            (df['브랜드'].isin(brands))
        ]
        
        st.dataframe(
            filtered.sort_values('판매량', ascending=False),
            height=400,
            use_container_width=True
        )
        
        # CSV 내보내기
        csv = filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="필터링 데이터 내보내기",
            data=csv,
            file_name=f"filtered_{country}.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()