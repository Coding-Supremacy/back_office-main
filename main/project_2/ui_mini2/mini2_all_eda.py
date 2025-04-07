import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from streamlit_option_menu import option_menu
import numpy as np

from project_1.ui_mini1.vehicle_recommendations_data import brand_recommendations

# 브랜드별 클러스터 추천 모델 (전역 변수)
brand_recommendations = {
    '현대': {
        1: ['Avante (CN7 N)', "G70 (IK)", "Tucson (NX4 PHEV)"],
        2: ["IONIQ 6 (CE)", "Grandeur (GN7 HEV)", "NEXO (FE)"],
        3: ["IONIQ 6 (CE)", "Grandeur (GN7 HEV)", "Santa-Fe (MX5 PHEV)"],
        4: ['Avante (CN7 N)',"Tucson (NX4 PHEV)", "G90 (HI)"],
        5: ["IONIQ 6 (CE)", "Santa-Fe (MX5 PHEV)", "Tucson (NX4 PHEV)"],
        6: ["Avante (CN7 N)", "G70 (IK)", "Tucson (NX4 PHEV)"]
    },
    '기아': {
        1: ["K5", "Telluride", "Sportage"],
        2: ["EV9", "Sorento", "Carnival"],
        3: ["K5", "EV6", "Seltos"],
        4: ["K5", "Sportage", "K8"],
        5: ["Telluride", "EV9", "Sorento"],
        6: ["K5", "K3", "Sonet"]
    }
}

# 데이터 로드 및 전처리 함수
@st.cache_data
def load_data(brand):
    try:
        df = pd.read_csv(f"data/{brand}_고객데이터_신규입력용.csv")
        df['제품 구매 날짜'] = pd.to_datetime(df['제품 구매 날짜'])
        df['구매월'] = df['제품 구매 날짜'].dt.to_period('M').astype(str)
        df['구매월_num'] = df['제품 구매 날짜'].dt.month
        df['Cluster'] = df['Cluster'] + 1  # 클러스터 번호 1부터 시작
        df['구매한 제품'] = df['구매한 제품'].apply(preprocess_model_name)# 모델명 전처리 적용
        
        # 실시간 데이터 누적을 위한 가상 데이터 생성 (실제 시스템에서는 DB에서 최신 데이터 불러옴)
        today = datetime.now()
        new_data = []
        for _ in range(np.random.randint(5, 15)):  # 5~15개의 새 데이터 생성
            random_days = np.random.randint(1, 30)
            new_date = today - timedelta(days=random_days)
            random_model = np.random.choice(df['구매한 제품'].unique())
            random_region = np.random.choice(df['국가'].unique())
            random_cluster = np.random.choice(df['Cluster'].unique())
            
            new_data.append({
                '제품 구매 날짜': new_date,
                '구매한 제품': random_model,
                '국가': random_region,
                'Cluster': random_cluster,
                '거래 금액': np.random.randint(20000, 100000),
                '제품구매빈도': np.random.randint(1, 10)
            })
        
        new_df = pd.DataFrame(new_data)
        df = pd.concat([df, new_df], ignore_index=True)
        
        return df
    except FileNotFoundError:
        st.error(f"{brand} 데이터 파일을 찾을 수 없습니다.")
        return pd.DataFrame()
    
def preprocess_model_name(model_name):
    """모델명에서 괄호 앞의 기본 모델명만 추출"""
    if '(' in model_name:
        return model_name.split('(')[0].strip()
    return model_name

def create_cluster_info_df(df, brand):
    # 고객 세그먼트 매핑 정보
    segment_mapping = {
        "현대": {
            0: "VIP",
            1: "이탈가능",
            2: "신규",
            3: "일반"
        },
        "기아": {
            0: "VIP",
            1: "일반",
            2: "신규",
            3: "이탈가능"
        }
    }

    cluster_stats = []

    for cluster_num in sorted(df['Cluster'].unique()):
        cluster_data = df[df['Cluster'] == cluster_num]

        # ✅ 세그먼트명 변환
        if '고객 세그먼트' in cluster_data.columns:
            mapped_segment_names = (
                cluster_data['고객 세그먼트']
                .map(segment_mapping.get(brand, {}))
                .dropna()
            )
            if not mapped_segment_names.empty:
                dominant_segment = mapped_segment_names.value_counts().idxmax()
            else:
                dominant_segment = "세그먼트 미지정"
        else:
            dominant_segment = "세그먼트 없음"

        # 🔹 성별 분석
        if '성별' in cluster_data.columns:
            gender_dist = cluster_data['성별'].value_counts(normalize=True) * 100
            dominant_gender = gender_dist.idxmax() if not gender_dist.empty else None
            gender_ratio = f"{dominant_gender} {gender_dist.max():.0f}%" if dominant_gender else "성별 데이터 없음"
        else:
            gender_ratio = "성별 데이터 없음"

        # 🔹 연령대 분석
        if '연령' in cluster_data.columns:
            cluster_data = cluster_data.copy()
            cluster_data['연령대'] = cluster_data['연령'].apply(lambda x: '고연령층' if x >= 40 else '젊은세대')
            age_dist = cluster_data['연령대'].value_counts()
            if not age_dist.empty:
                dominant_age = age_dist.idxmax()
            else:
                dominant_age = "연령 데이터 없음"
        else:
            dominant_age = "연령 데이터 없음"

        # 🔹 특징 조합
        characteristics_parts = [dominant_segment]
        if gender_ratio != "성별 데이터 없음":
            characteristics_parts.append(gender_ratio)
        if dominant_age != "연령 데이터 없음":
            characteristics_parts.append(dominant_age)

        characteristics = ", ".join(characteristics_parts)

        # 🔹 선호 모델
        top_models = cluster_data['구매한 제품'].value_counts().nlargest(3)
        preferred_models = ", ".join(top_models.index.tolist()) if not top_models.empty else "데이터 없음"

        # 🔹 고객 비율
        customer_ratio = (len(cluster_data) / len(df)) * 100

        cluster_stats.append({
            "Cluster": cluster_num,
            "특징": characteristics,
            "고객 비율(%)": round(customer_ratio, 1),
            "선호 모델": preferred_models
        })

    cluster_df = pd.DataFrame(cluster_stats)
    cluster_df.set_index("Cluster", inplace=True)
    return cluster_df



# 생산량 추천 계산 함수
def calculate_production_recommendation(sales_trend, current_inventory, safety_stock=0.2):
    avg_sales = sales_trend.mean()
    recommended_production = avg_sales * (1 + safety_stock) - current_inventory
    return max(0, recommended_production)

# 모델별 생산 우선순위 계산
def calculate_model_priority(df):
    # 1. 기본 통계 계산
    model_stats = df.groupby('구매한 제품').agg({
        '거래 금액': 'mean',
        '제품 구매 날짜': 'count',
        '제품구매경로': lambda x: (x == '오프라인').mean() if '오프라인' in x.values else 0  # 오프라인 구매 비율
    }).rename(columns={'제품 구매 날짜': '판매량'}).fillna(0)

    # 2. 최근 3개월 판매 비중 계산
    recent_date = df['제품 구매 날짜'].max()
    recent_mask = df['제품 구매 날짜'] >= (recent_date - pd.DateOffset(months=3))
    recent_sales = df[recent_mask].groupby('구매한 제품').size()
    model_stats['최근_판매_비중'] = (recent_sales / model_stats['판매량']).fillna(0)

    # 3. 점수 계산 (가중치 적용 후 정수 변환)
    model_stats['수익성 점수'] = ((model_stats['거래 금액'] / model_stats['거래 금액'].max()) * 40).round().astype(int)

    model_stats['충성도 점수'] = (
        (model_stats['최근_판매_비중'].fillna(0) * 0.6 +
         model_stats['제품구매경로'] * 0.4) * 30
    ).round().astype(int)

    model_stats['인기 점수'] = ((model_stats['판매량'] / model_stats['판매량'].max()) * 30).round().astype(int)

    # 4. 종합 점수 계산 (100점 만점 기준)
    model_stats['종합 점수'] = model_stats[['수익성 점수', '충성도 점수', '인기 점수']].sum(axis=1)

    return model_stats.sort_values('종합 점수', ascending=False)


# 판매 트렌드 분석 및 인사이트 생성
def analyze_sales_trend(filtered_df, brand, selected_models):
    st.subheader("📊 판매 트렌드 분석 결과")
    
    # 월별 판매량 집계
    monthly_sales = filtered_df.groupby(['구매월', '구매한 제품']).size().unstack().fillna(0)
    
    # 판매 트렌드 시각화
    fig = px.line(
        monthly_sales, 
        x=monthly_sales.index, 
        y=selected_models,
        title=f"{brand} 모델별 월별 판매 추이",
        labels={"value": "판매량", "구매월": "월", "variable": "모델"}
    )
    st.plotly_chart(fig)
    
    # 판매 트렌드 인사이트
    st.markdown("### 🔍 판매 트렌드 주요 인사이트")
    
    # 모델별 성장률 계산 (최근 3개월 vs 이전 3개월)
    if len(monthly_sales) >= 6:
        recent_months = monthly_sales.index[-3:]
        previous_months = monthly_sales.index[-6:-3]
        
        growth_rates = {}
        for model in selected_models:
            recent_sales = monthly_sales.loc[recent_months, model].mean()
            previous_sales = monthly_sales.loc[previous_months, model].mean()
            growth_rate = ((recent_sales - previous_sales) / previous_sales * 100) if previous_sales != 0 else 0
            growth_rates[model] = growth_rate
        
        fastest_growing = max(growth_rates, key=growth_rates.get)
        fastest_declining = min(growth_rates, key=growth_rates.get)
        
        st.markdown(f"""
        - **가장 빠르게 성장하는 모델**: {fastest_growing} (성장률: {growth_rates[fastest_growing]:.1f}%)
        - **판매 감소 중인 모델**: {fastest_declining} (감소율: {abs(growth_rates[fastest_declining]):.1f}%)
        """)
        
        # 계절성 패턴 분석
        st.markdown("### 📅 계절성 패턴 분석")
        seasonal_df = filtered_df.groupby(['구매월_num', '구매한 제품']).size().unstack().fillna(0)
        
        fig_seasonal = px.line(
            seasonal_df,
            x=seasonal_df.index,
            y=selected_models,
            title="월별 계절성 패턴 (전체 기간)",
            labels={"value": "평균 판매량", "구매월_num": "월", "variable": "모델"}
        )
        st.plotly_chart(fig_seasonal)
        
        # 계절성 인사이트
        seasonal_insights = []
        for model in selected_models:
            peak_month = int(seasonal_df[model].idxmax())
            low_month = int(seasonal_df[model].idxmin())
            seasonal_insights.append(f"- {model}: 최고 판매월 {peak_month}월, 최저 판매월 {low_month}월")
        
        st.markdown("#### 🔍 계절성 주요 인사이트\n" + "\n".join(seasonal_insights))
    
    # 최근 3개월 판매 통계
    st.subheader("📈 최근 3개월 판매 통계")
    recent_months = monthly_sales.index[-3:] if len(monthly_sales) >= 3 else monthly_sales.index
    recent_sales = monthly_sales.loc[recent_months]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("평균 판매량", f"{recent_sales.mean().mean():.1f}대")
    col2.metric("최대 판매량", f"{recent_sales.max().max()}대")
    col3.metric("최소 판매량", f"{recent_sales.min().min()}대")
    
    st.dataframe(recent_sales.style.format("{:.0f}대").background_gradient(cmap='Blues'))
    
    # 판매 추세에 따른 생산 권장 사항
    st.markdown("### 🏭 생산 계획 권장 사항")
    for model in selected_models:
        model_sales = monthly_sales[model]
        if len(model_sales) >= 3:
            trend = (model_sales.iloc[-1] - model_sales.iloc[-3]) / 3  # 월평균 변화량
            if trend > 0:
                st.success(f"{model}: 판매량이 월평균 {trend:.1f}대 증가 중 → 생산량 점진적 증가 권장")
            elif trend < 0:
                st.warning(f"{model}: 판매량이 월평균 {abs(trend):.1f}대 감소 중 → 생산량 조정 필요")
            else:
                st.info(f"{model}: 판매량 안정적 → 현재 생산량 유지 권장")

# 지역별 선호 모델 분석 및 인사이트 생성
def analyze_regional_preference(region_df, selected_region, df):
    st.subheader("🌍 지역별 선호 모델 분석 결과")
    
    # 모델별 판매량
    model_sales = region_df['구매한 제품'].value_counts().reset_index()
    model_sales.columns = ['모델', '판매량']
    top_models = model_sales.head(10)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏆 인기 모델 Top 10")
        fig = px.bar(
            top_models,
            x='모델',
            y='판매량',
            color='모델',
            title=f"{selected_region} 인기 모델"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 판매 비율")
        fig = px.pie(
            top_models,
            names='모델',
            values='판매량',
            title=f"{selected_region} 모델별 판매 비율"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # 지역별 인사이트
    st.markdown("### 🔍 지역별 주요 인사이트")
    
    # 전체 평균과 비교
    total_avg_sales = df['구매한 제품'].value_counts(normalize=True)
    region_avg_sales = region_df['구매한 제품'].value_counts(normalize=True)
    
    over_performing = []
    for model in top_models['모델']:
        if model in total_avg_sales.index:
            diff = (region_avg_sales.get(model, 0) - total_avg_sales.get(model, 0)) * 100
            if diff > 5:  # 5% 이상 높은 경우
                over_performing.append(f"- {model}: 평균보다 {diff:.1f}% 높음")
    
    if over_performing:
        st.markdown(f"#### 📌 {selected_region}에서 특별히 잘 팔리는 모델:\n" + "\n".join(over_performing))
    else:
        st.info("이 지역의 모델 선호도는 전체 평균과 유사합니다.")
    
    # 지역별 비교 분석
    st.subheader("🌐 지역별 Top5 모델 선호도 비교")
    
    regions = df['국가'].unique()
    compare_regions = st.multiselect(
        "비교할 지역 선택",
        regions,
        default=list(dict.fromkeys([selected_region] + list(regions[:2]))))
    
    if compare_regions:
        compare_df = df[df['국가'].isin(compare_regions)]
        model_region_sales = compare_df.groupby(['구매한 제품', '국가']).size().unstack().fillna(0)
        
        # 상위 5개 모델만 표시
        top_5_models = model_region_sales.sum(axis=1).nlargest(5).index
        model_region_sales = model_region_sales.loc[top_5_models]
        def highlight_zero(val):
            color = 'red' if val == 0 else 'white'
            return f'background-color: {color}'
        st.dataframe(
            model_region_sales.style
                .applymap(highlight_zero)  # 0대는 빨간색 강조
                .background_gradient(cmap='Blues', axis=1)  # 그 외는 블루 그라데이션
                .format("{:.0f}대")  # 단위 표시
        )
        
        # 히트맵 시각화
        fig = px.imshow(
            model_region_sales,
            labels=dict(x="지역", y="모델", color="판매량"),
            title="지역별 Top5 모델 선호도 비교"
        )
        st.plotly_chart(fig)
        
        # 지역 비교 인사이트
        st.markdown("### 🔍 지역 비교 주요 인사이트")
        
        insights = []
        for model in top_5_models:
            if model in model_region_sales.index:  # 모델 존재 확인 추가
                best_region = model_region_sales.loc[model].idxmax()
                worst_region = model_region_sales.loc[model].idxmin()
                best_sales = model_region_sales.loc[model, best_region]
                worst_sales = model_region_sales.loc[model, worst_region]
                
                # 조건 완화: 0대 판매 또는 2배 이상 차이 시 인사이트 생성
                if worst_sales == 0:
                    insights.append(f"- {model}: {best_region}에서 단독 판매 (타지역 0대)")
                elif best_sales >= 2 * worst_sales:  # 2배 이상 차이 시
                    ratio = best_sales / worst_sales
                    insights.append(f"- {model}: {best_region}에서 {worst_region}보다 {ratio:.1f}배 더 많이 팔림")
        
        # 인사이트 표시 로직 변경
        if insights:
            st.markdown("#### 📌 지역별 차이가 큰 모델:")
            for insight in insights:
                st.markdown(insight)
        else:
            st.info("선택한 지역 간 모델 선호도 차이가 크지 않습니다.")

# 고객 유형별 모델 선호도 분석 및 인사이트 생성
def analyze_cluster_preference(cluster_model, selected_cluster, df, brand):
    st.subheader("👥 고객 유형별 모델 선호도 분석 결과")
    
    # 선택한 클러스터의 모델 선호도
    cluster_preference = cluster_model.loc[selected_cluster].sort_values(ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"### 🏆 고객 유형 {selected_cluster} 선호 모델 Top 10")
        fig = px.bar(
            cluster_preference.head(10),
            x=cluster_preference.head(10).index,
            y=cluster_preference.head(10).values,
            color=cluster_preference.head(10).index,
            title=f"고객 유형 {selected_cluster} Top 10 모델"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # 클러스터 정보 데이터프레임 생성
        cluster_df = create_cluster_info_df(df, brand)
        
        st.markdown("### 📊 고객 유형별 특징 및 선호 모델")
        
        # 전체 클러스터 정보 표시 (선택한 클러스터 강조)
        st.dataframe(
            cluster_df.style.apply(
                lambda x: ["background: #EAF2F8" if x.name == selected_cluster else "" for i in x], 
                axis=1
            )
        )
    
    # 고객 유형별 인사이트
    st.markdown("### 🔍 고객 유형별 주요 인사이트")
    
    # 전체 평균과 비교
    total_avg_sales = df['구매한 제품'].value_counts(normalize=True)
    cluster_avg_sales = df[df['Cluster'] == selected_cluster]['구매한 제품'].value_counts(normalize=True)
    
    unique_preferences = []
    for model in cluster_preference.head(5).index:
        diff = (cluster_avg_sales.get(model, 0) - total_avg_sales.get(model, 0)) * 100
        if diff > 5:  # 5% 이상 높은 경우
            unique_preferences.append(f"- {model}: 일반 고객 대비 {diff:.1f}% 더 높은 선호도")
    
    # 클러스터 특징 가져오기
    cluster_features = cluster_df.loc[selected_cluster, "특징"]
    
    col1, col2 = st.columns(2)
    with col1:
        if unique_preferences:
            st.markdown(f"""
            #### 📌 고객 유형 {selected_cluster} 특징:
            {cluster_features}
            
            #### 특별히 선호하는 모델:
            {cluster_df.loc[selected_cluster, "선호 모델"]}
            """)
        else:
            st.info(f"""
            이 고객 유형의 선호도는 전체 평균과 유사합니다.
            
            #### 고객 유형 {selected_cluster} 특징:
            {cluster_features}
            """)
    
    # 모든 클러스터에 대한 모델 선호도 비교
    st.subheader("👥 고객 유형별 모델 선호도 비교")
    
    compare_models = st.multiselect(
        "비교할 모델 선택",
        df['구매한 제품'].unique(),
        default=df['구매한 제품'].value_counts().head(3).index.tolist(),
        key=f"model_compare_{selected_cluster}"
    )
    
    if compare_models:
        model_cluster = df[df['구매한 제품'].isin(compare_models)]
        model_cluster = model_cluster.groupby(['구매한 제품', 'Cluster']).size().unstack().fillna(0)
        
        # 정수형으로 포매팅하여 출력
        st.dataframe(
            model_cluster.style.format("{:.0f}")
            .background_gradient(cmap='Blues', axis=1)
        )
        
        # 클러스터별 모델 선호도 시각화
        fig = px.bar(
            model_cluster.T,
            barmode='group',
            title="고객 유형별 모델 선호도 비교"
        )
        st.plotly_chart(fig)
        
        # 고객 유형 비교 인사이트
        st.markdown("### 🔍 고객 유형별 모델 선호도 인사이트")

        insights = []
        for model in compare_models:
            if model in model_cluster.index:
                best_cluster = model_cluster.loc[model].idxmax()
                worst_cluster = model_cluster.loc[model].idxmin()
                max_sales = model_cluster.loc[model, best_cluster]
                min_sales = model_cluster.loc[model, worst_cluster]
                
                if min_sales == 0:
                    insights.append(f"- {model}: 유형 {best_cluster}에서만 {max_sales}건 판매 (유형 {worst_cluster}에서는 판매 없음)")
                else:
                    ratio = max_sales / min_sales
                    if ratio > 3:
                        insights.append(f"- {model}: 유형 {best_cluster}에서 유형 {worst_cluster}보다 {ratio:.1f}배 더 선호")

        if insights:
            st.markdown("#### 📌 고객 유형별 선호도 차이가 큰 모델:\n" + "\n".join(insights))
        else:
            st.info("선택한 모델들의 고객 유형별 선호도 차이가 크지 않습니다.")

            # 클러스터별 추천 모델 표시 (수정된 부분)
    st.subheader("🎯 고객유형별 추천 모델 (Top 3)")
    
    recommendations = brand_recommendations.get(brand, {})
    if recommendations:
        # 현재 선택된 클러스터의 추천 모델만 표시
        if selected_cluster in recommendations:
            rec_models = recommendations[selected_cluster]
            
            cols = st.columns(3)
            for i, model in enumerate(rec_models):
                with cols[i]:
                    st.metric(f"{i+1}순위", model)
            
        # 데이터프레임으로 전체 요약 표시
        with st.subheader("📋 모든 고객유형별 추천 모델 보기"):
            rec_df = pd.DataFrame.from_dict(
                recommendations,
                orient='index',
                columns=['1순위', '2순위', '3순위']
            )
            st.dataframe(
                rec_df.style.apply(
                    lambda x: ["background: #EAF2F8" if x.name == selected_cluster else "" for i in x],
                    axis=1
                )
            )


def analyze_model_priority(df, model_priority):
    st.subheader("📊 모델별 생산 우선순위 분석 결과 (최신 충성도 지표 반영)")
    with st.expander("ℹ️ 생산 우선순위 계산 방법 (클릭하여 상세보기)", expanded=False):
        st.markdown("""
        ### 📝 모델 평가 지표 계산 공식
        
        각 모델은 **3가지 핵심 지표**로 평가되며, 가중치를 적용해 종합 점수를 계산합니다:
        
        <div style="background-color:#f5f5f5; padding:15px; border-radius:10px; margin-bottom:20px;">
        <b>종합 점수 = (수익성 점수 × 40%) + (충성도 점수 × 30%) + (인기 점수 × 30%)</b>
        </div>
        
        #### 1️⃣ 수익성 점수 (40% 가중치)
        - 계산식: <code>(모델 평균 거래 금액 ÷ 최고 평균 거래 금액) × 0.4</code>
        - 모델별 평균 매출액을 기준으로 비교
        - 고가 모델일수록 유리한 지표
        
        #### 2️⃣ 충성도 점수 (30% 가중치)
        - 일반적으로는 재구매율이나 고객 유지율을 활용해 충성도를 평가하지만, 이번 분석에서는 관련 이력 데이터가 제한적이므로 대체 지표를 적용
        - 최근 3개월 판매 비중과 오프라인 구매율을 결합하여, 지속적인 수요 유지 가능성과 고객 접점 강도를 함께 반영하였습니다.
        - 계산식: <code>(최근 3개월 판매 비중 × 60% + 오프라인 구매율 × 40%) × 0.3</code>
        - 최근성(60%): 해당 모델의 최근 3개월 판매량 비율
        - 오프라인 구매(40%): 대리점 방문 고객 비율
        - 안정적인 고객 기반을 보유한 모델 평가
        
        #### 3️⃣ 인기 점수 (30% 가중치)
        - 계산식: <code>(모델 총 판매량 ÷ 최다 판매 모델 판매량) × 0.3</code>
        - 전체 판매량을 기준으로 비교
        - 시장 점유율이 높은 모델 평가
        """, unsafe_allow_html=True)
        
        # 계산 예시 시각화
        example_model = model_priority.index[0]
        example_data = model_priority.loc[example_model]
        
        st.markdown(f"""
        ### 📊 예시: {example_model} 모델 점수 계산
        <div style="background-color:#e8f4f8; padding:15px; border-radius:10px;">
        - 평균 거래 금액: {example_data['거래 금액']:,.0f}원 (최대 대비 {example_data['거래 금액']/model_priority['거래 금액'].max():.0%}) → <b>수익성 점수: {example_data['수익성 점수']:.0f}</b><br>
        - 최근 3개월 판매: {example_data['최근_판매_비중']:.0%}, 오프라인 구매: {example_data['제품구매경로']:.0%} → <b>충성도 점수: {example_data['충성도 점수']:.0f}</b><br>
        - 총 판매량: {int(example_data['판매량'])}대 (최대 대비 {example_data['판매량']/model_priority['판매량'].max():.0%}) → <b>인기 점수: {example_data['인기 점수']:.0f}</b><br>
        <div style="border-top:1px solid #ddd; margin:10px 0;"></div>
        → <b>종합 점수: {example_data['종합 점수']:.2f}</b>
        </div>
        """, unsafe_allow_html=True)
    
    # --------------------------
    # 기존 분석 결과 표시 부분
    # --------------------------
    # 상위 10개 모델 시각화
    top_models = model_priority.head(10)
    fig = px.bar(
        top_models,
        x=top_models.index,
        y='종합 점수',
        color='종합 점수',
        title="모델별 생산 우선순위 (종합 점수)",
        hover_data=['최근_판매_비중', '제품구매경로'],
        labels={'최근_판매_비중': '최근 3개월 비중', '제품구매경로': '오프라인 구매율'}
    )
    st.plotly_chart(fig)
    
    # 인사이트 생성 로직
    top_model = top_models.index[0]
    bottom_model = top_models.index[-1]
    
    st.markdown(f"""
    ## 🏆 모델별 평가 결과
    
    ### 최우선 생산 모델 (TOP 1)
    <div style="background-color:#e8f4f8; padding:15px; border-radius:10px; margin-bottom:20px;">
    <b>{top_model}</b>
    <table style="width:100%; border-collapse:collapse; margin-top:10px;">
    <tr><td style="padding:5px; width:30%;">종합 점수</td><td style="padding:5px;">{top_models.loc[top_model, '종합 점수']:.0f}</td></tr>
    <tr><td style="padding:5px;">수익성 점수</td><td style="padding:5px;">{top_models.loc[top_model, '수익성 점수']:.0f}</td></tr>
    <tr><td style="padding:5px;">충성도 점수</td><td style="padding:5px;">{top_models.loc[top_model, '충성도 점수']:.0f}</td></tr>
    <tr><td style="padding:5px;">인기 점수</td><td style="padding:5px;">{top_models.loc[top_model, '인기 점수']:.0f}</td></tr>
    </table>
    </div>
    
    ### 생산 조정 필요 모델 (Bottom 1)
    <div style="background-color:#fff4f4; padding:15px; border-radius:10px;">
    <b>{bottom_model}</b>
    <table style="width:100%; border-collapse:collapse; margin-top:10px;">
    <tr><td style="padding:5px; width:30%;">종합 점수</td><td style="padding:5px;">{top_models.loc[bottom_model, '종합 점수']:.0f}</td></tr>
    <tr><td style="padding:5px;">수익성 점수</td><td style="padding:5px;">{top_models.loc[bottom_model, '수익성 점수']:.0f}</td></tr>
    <tr><td style="padding:5px;">충성도 점수</td><td style="padding:5px;">{top_models.loc[bottom_model, '충성도 점수']:.0f}</td></tr>
    <tr><td style="padding:5px;">인기 점수</td><td style="padding:5px;">{top_models.loc[bottom_model, '인기 점수']:.0f}</td></tr>
    </table>
    </div>
    """, unsafe_allow_html=True)
    
    # 모델 비교 섹션
    compare_models = st.multiselect(
        "비교할 모델 선택 (최대 5개)",
        model_priority.index,
        default=model_priority.head(3).index.tolist(),
        key="model_compare"
    )

    if compare_models:
        compare_df = model_priority.loc[compare_models]
        
        # 1. 누적 바 그래프 (종합 점수 구성 비교)
        fig_stacked = px.bar(
            compare_df,
            x=compare_df.index,
            y=['수익성 점수', '충성도 점수', '인기 점수'],
            title="모델별 생산 우선순위 점수 (누적)",
            labels={'value': '점수', 'variable': '지표'},
            color_discrete_map={
                '수익성 점수': '#3498DB',  # 파란색
                '충성도 점수': '#F39C12',  # 주황색
                '인기 점수': '#2ECC71'     # 초록색
            }
        )
        fig_stacked.update_layout(
            barmode='stack',  # 누적 모드
            xaxis_title='모델',
            yaxis_title='종합 점수',
            legend_title='지표 구성',
            hovermode='x unified'  # 호버 시 모든 지표 표시
        )
        
        # 2. 종합 점수 순위 (보조 차트)
        fig_rank = px.bar(
            compare_df.sort_values('종합 점수', ascending=False),
            x='종합 점수',
            y=compare_df.index,
            orientation='h',
            title="종합 점수 순위",
            color='종합 점수',
            color_continuous_scale='Blues'
        )
        fig_rank.update_layout(yaxis_title='모델')
        
        # 그래프 병렬 출력
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig_stacked, use_container_width=True)
        with col2:
            st.plotly_chart(fig_rank, use_container_width=True)
        
        # 3. 데이터 테이블 (점수 상세 내역)
        st.markdown("### 📊 점수 상세 내역")
        st.dataframe(
            compare_df[['수익성 점수', '충성도 점수', '인기 점수', '종합 점수']]
            .style.background_gradient(cmap='YlOrRd', subset=['종합 점수'])
        )
        
        # 강점 분석
        insights = []
        for model in compare_models:
            strengths = []
            if compare_df.loc[model, '수익성 점수'] > 0.7:
                strengths.append("고수익")
            if compare_df.loc[model, '충성도 점수'] > 0.7:
                strengths.append("충성도 높음")
            if compare_df.loc[model, '인기 점수'] > 0.7:
                strengths.append("인기 상품")
                
            if strengths:
                insights.append(f"- **{model}**: {', '.join(strengths)}")
        
        if insights:
            with st.expander("🔍 모델별 강점 상세 분석", expanded=True):
                st.markdown("\n".join(insights))
        
        # 재고 관리 섹션
        st.markdown("### 📦 재고 현황 반영 생산 계획")
        inventory_data = {
            model: st.number_input(
                f"현재 {model} 재고량을 입력하세요.",
                min_value=0,
                value=10,
                step=1,
                key=f"inventory_{model}"
            ) for model in compare_models
        }
        
        inventory_df = pd.DataFrame({
            '모델': compare_models,
            '주간 평균 판매량': [model_priority.loc[m, '판매량']/52 for m in compare_models],
            '현재 재고': [inventory_data[m] for m in compare_models],
            '재고 주수': [inventory_data[m]/(model_priority.loc[m, '판매량']/52) for m in compare_models]
        }).set_index('모델')
        
        st.dataframe(
            inventory_df.style.format("{:.1f}").background_gradient(
                subset=['재고 주수'], 
                cmap='RdYlGn',  # 녹색(안전) ~ 빨강(위험)
                vmin=2, vmax=8    # 2주 미만: 위험, 8주 이상: 과잉
            )
        )
        
        # 생산 권장사항
        st.markdown("#### 📌 생산 계획 권장")
        for model in compare_models:
            weeks = inventory_df.loc[model, '재고 주수']
            if weeks < 2:
                st.error(f"{model}: 재고 부족 (현재 {weeks:.1f}주 분) → **긴급 생산 필요**")
            elif weeks > 8:
                st.success(f"{model}: 재고 과다 (현재 {weeks:.1f}주 분) → 생산 감소 검토")
            else:
                st.warning(f"{model}: 재고 적정 (현재 {weeks:.1f}주 분)")

# 메인 분석 함수
def run_all_eda():
    st.title("🚗 글로벌 고객 데이터 분석 + 생산 우선순위 도출")
    brand = st.session_state.get("brand", "현대")
    
    df = load_data(brand)
    
    if df.empty:
        st.warning("데이터를 불러오는 데 실패했습니다.")
        return
    
    
    # 분석 메뉴 선택
    selected_analysis = option_menu(
        menu_title=None,
        options=[
            "📈 모델별 판매 트렌드",
            "🌍 지역별 선호 모델", 
            "👥 고객 유형별 모델 선호도",
            "📊 모델별 생산 우선순위"
        ],
        icons=["", "", "", "", ""],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#f9f9f9"},
            "icon": {"color": "#2E86C1", "font-size": "20px"},
            "nav-link": {"font-size": "16px", "text-align": "center", "margin": "0px", "padding": "10px"},
            "nav-link-selected": {"background-color": "#2E86C1", "color": "white"},
        }
    )
    
    if selected_analysis == "📈 모델별 판매 트렌드":
        st.header(f"{brand} 모델별 판매 트렌드 분석")
        
        # 모델 선택
        selected_models = st.multiselect(
            "분석할 모델 선택",
            df['구매한 제품'].unique(),
            default=df['구매한 제품'].value_counts().head(3).index.tolist()
        )
        
        if not selected_models:
            st.warning("최소 한 개 이상의 모델을 선택해주세요.")
            return
        
        # 기간 선택
        min_date = df['제품 구매 날짜'].min().to_pydatetime()
        max_date = df['제품 구매 날짜'].max().to_pydatetime()
        date_range = st.slider(
            "분석 기간 선택",
            min_value=min_date,
            max_value=max_date,
            value=(max_date - timedelta(days=365), max_date))
        
        filtered_df = df[(df['구매한 제품'].isin(selected_models)) & 
                        (df['제품 구매 날짜'] >= date_range[0]) & 
                        (df['제품 구매 날짜'] <= date_range[1])]
        
        if filtered_df.empty:
            st.error("선택한 조건에 해당하는 데이터가 없습니다.")
            return
        
        analyze_sales_trend(filtered_df, brand, selected_models)
    
    elif selected_analysis == "🌍 지역별 선호 모델":
        st.header(f"{brand} 지역별 선호 모델 분석")
        
        # 지역 선택
        regions = df['국가'].unique()
        selected_region = st.selectbox("지역 선택", sorted(regions))
        
        # 해당 지역 데이터 필터링
        region_df = df[df['국가'] == selected_region]
        
        analyze_regional_preference(region_df, selected_region, df)
    
    elif selected_analysis == "👥 고객 유형별 모델 선호도":
        st.header(f"{brand} 고객 유형별 모델 선호도 분석")
        
        # 클러스터별 모델 선호도
        cluster_model = df.groupby(['Cluster', '구매한 제품']).size().unstack().fillna(0)
        
        # 클러스터 선택
        selected_cluster = st.selectbox(
            "고객 유형 선택",
            sorted(cluster_model.index.unique()),
            key='cluster_select'
        )
        
        analyze_cluster_preference(cluster_model, selected_cluster, df, brand)
    
    elif selected_analysis == "📊 모델별 생산 우선순위":
        st.header(f"{brand} 모델별 생산 우선순위")
        
        # 모델별 우선순위 계산
        model_priority = calculate_model_priority(df)
        
        analyze_model_priority(df, model_priority)
