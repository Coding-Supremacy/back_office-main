import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from streamlit_option_menu import option_menu
import numpy as np

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
    # 클러스터 기본 정보
    cluster_info = {
        "Cluster": [1, 2, 3, 4, 5],
        "특징": [
            "남성, 중장년층, VIP 집중",
            "성별균형, 젊은층, 이탈 가능성 높음",
            "성별균형, 고령층, 이탈 가능성 높음",
            "성별균형, 고령층, 안정적 고객군",
            "성별균형, 젊은층, 안정적 고객군"
        ],
        "고객 비율(%)": [15, 25, 20, 20, 20]  # 예시 비율 (실제 데이터에 맞게 조정 필요)
    }
    
    # 클러스터별 선호 모델 계산 (상위 3개)
    cluster_model_preference = df.groupby(['Cluster', '구매한 제품']).size().groupby(level=0).nlargest(3)
    
    # 각 클러스터별 선호 모델 문자열 생성
    preferred_models = {}
    for cluster in cluster_info["Cluster"]:
        try:
            models = cluster_model_preference[cluster].index.get_level_values(1).tolist()
            preferred_models[cluster] = ", ".join(models[:3])  # 상위 3개 모델만 표시
        except KeyError:
            preferred_models[cluster] = "데이터 없음"
    
    # 데이터프레임에 선호 모델 컬럼 추가
    cluster_info["선호 모델"] = [preferred_models[c] for c in cluster_info["Cluster"]]
    
    # 데이터프레임 생성
    cluster_df = pd.DataFrame(cluster_info)
    
    # 클러스터 번호를 인덱스로 설정
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
                over_performing.append(f"- {model}: 지역 평균보다 {diff:.1f}% 높음")
    
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
        
        # 전체 클러스터 정보 표시
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
            unique_preferences.append(f"- {model}: 일반 고객 대비 {diff:.1f}% 더 높은 선호도를 보여줌")
    
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
        "비교할 모델 선택 (기본값은 선택중인 고객 유형별 판매량 상위 3개 모델입니다.)",
        df['구매한 제품'].unique(),
        default=df['구매한 제품'].value_counts().head(3).index.tolist()
    )
    
    if compare_models:
        model_cluster = df[df['구매한 제품'].isin(compare_models)]
        model_cluster = model_cluster.groupby(['구매한 제품', 'Cluster']).size().unstack().fillna(0)
        
        # 정수형으로 포매팅하여 출력
        st.dataframe(
            model_cluster.style.format("{:.0f}")  # 소수점 없이 정수로 표시
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
                    # 최소 판매량이 0인 경우 (inf 방지)
                    insight = f"- {model}: 유형 {best_cluster}에서만 {max_sales}건 판매 (유형 {worst_cluster}에서는 판매 없음)"
                else:
                    ratio = max_sales / min_sales
                    if ratio > 3:  # 3배 이상 차이나는 경우
                        insight = f"- {model}: 유형 {best_cluster}에서 유형 {worst_cluster}보다 {ratio:.1f}배 더 선호"
                    else:
                        continue  # 3배 미만 차이는 인사이트에서 제외
                
                insights.append(insight)

        if insights:
            st.markdown("#### 📌 고객 유형별 선호도 차이가 큰 모델:\n" + "\n".join(insights))
        else:
            st.info("선택한 모델들의 고객 유형별 선호도 차이가 크지 않습니다.")

# 생산량 추천 시스템 분석 및 인사이트 생성
def analyze_production_recommendation(df, selected_model, current_inventory, safety_stock):
    st.subheader("🏭 생산량 추천 시스템 분석 결과")
    
    # 최근 1년 판매 데이터
    recent_date = df['제품 구매 날짜'].max()
    one_year_ago = recent_date - timedelta(days=365)
    recent_sales = df[(df['구매한 제품'] == selected_model) & 
                     (df['제품 구매 날짜'] >= one_year_ago)]
    
    if recent_sales.empty:
        st.error("최근 1년 내 판매 데이터가 없습니다.")
        return
    
    # 월별 판매량 계산
    monthly_sales = recent_sales.groupby('구매월').size()
    
    # 생산량 추천 계산
    recommended_production = calculate_production_recommendation(
        monthly_sales,
        current_inventory,
        safety_stock
    )
    
    st.markdown("### 📊 생산량 추천 결과")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("최근 12개월 평균 판매량", f"{monthly_sales.mean():.1f}대/월")
    col2.metric("현재 재고량", f"{current_inventory}대")
    col3.metric("추천 생산량", f"{recommended_production:.0f}대")
    
    # 판매 추이 그래프
    st.markdown("### 📈 최근 12개월 판매 추이")
    fig = px.line(
        x=monthly_sales.index,
        y=monthly_sales.values,
        title=f"{selected_model} 월별 판매량",
        labels={"x": "월", "y": "판매량"}
    )
    st.plotly_chart(fig)
    
    # 생산 추천 인사이트
    st.markdown("### 🔍 생산 계획 인사이트")
    
    inventory_coverage = current_inventory / monthly_sales.mean() if monthly_sales.mean() > 0 else float('inf')
    
    if inventory_coverage < 1:
        st.error(f"⚠️ 위험: 현재 재고가 평균 월 판매량의 {inventory_coverage:.1f}개월 분량밖에 안됩니다. 즉시 생산 필요!")
    elif inventory_coverage < 2:
        st.warning(f"⚠️ 주의: 현재 재고가 평균 월 판매량의 {inventory_coverage:.1f}개월 분량입니다. 생산 계획 수립 필요.")
    else:
        st.success(f"✅ 안정적: 현재 재고가 평균 월 판매량의 {inventory_coverage:.1f}개월 분량입니다.")
    
    # 계절성 패턴 분석
    st.markdown("### 📅 계절성 패턴 분석 (전체 기간)")
    
    seasonal_pattern = df[df['구매한 제품'] == selected_model].groupby('구매월_num').size()
    
    fig = px.line(
        x=seasonal_pattern.index,
        y=seasonal_pattern.values,
        title=f"{selected_model} 월별 평균 판매 패턴",
        labels={"x": "월", "y": "평균 판매량"}
    )
    st.plotly_chart(fig)
    
    # 계절성 인사이트
    peak_month = int(seasonal_pattern.idxmax())
    low_month = int(seasonal_pattern.idxmin())
    peak_sales = int(seasonal_pattern.max())
    low_sales = seasonal_pattern.min()
    seasonality_ratio = peak_sales / low_sales if low_sales != 0 else float('inf')
    # 생산 계획 범위 계산
    start_month = max(1, peak_month - 2)
    end_month = max(1, peak_month - 1)

    if start_month == end_month:
        production_month_text = f"{start_month}월"
    else:
        production_month_text = f"{start_month}~{end_month}월"

    st.markdown(f"""
    #### 🔍 계절성 주요 인사이트
    - **최고 판매월**: {peak_month}월 (평균 {peak_sales:.1f}대)
    - **최저 판매월**: {low_month}월 (평균 {low_sales:.1f}대)
    - **계절성 차이**: {seasonality_ratio:.1f}배 차이
    
    💡 **생산 계획 제안**: {peak_month}월 수요 대비를 위해 **{production_month_text}**에 생산량 증대 필요
""")

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
        
        # 지표 비교 차트
        fig = px.bar(
            compare_df,
            x=compare_df.index,
            y=['수익성 점수', '충성도 점수', '인기 점수'],
            barmode='group',
            title="모델별 평가 지표 비교",
            labels={'value': '점수', 'variable': '지표'}
        )
        st.plotly_chart(fig)
        
        # 강점 분석
        insights = []
        for model in compare_models:
            strengths = []
            if compare_df.loc[model, '수익성 점수'] > 0.7:
                strengths.append("고수익")
            if compare_df.loc[model, '충성도 점수'] > 0.7:
                strengths.append("충성도 높음")
            if compare_df.loc[model, '인기 점수'] > 0.7:
                strengths.append("인기 급상승")
                
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
                st.warning(f"{model}: 재고 부족 (현재 {weeks:.1f}주 분) → **긴급 생산 필요**")
            elif weeks > 8:
                st.info(f"{model}: 재고 과다 (현재 {weeks:.1f}주 분) → 생산 감소 검토")
            else:
                st.success(f"{model}: 재고 적정 (현재 {weeks:.1f}주 분)")

# 메인 분석 함수
def run_all_eda():
    st.title("🚗 차량 생산량 최적화 분석 with 인사이트")
    brand = st.session_state.get("brand", "현대")
    
    df = load_data(brand)
    
    if df.empty:
        st.warning("데이터를 불러오는 데 실패했습니다.")
        return
    
    # 최신 데이터 업데이트 알림
    latest_date = df['제품 구매 날짜'].max().strftime('%Y-%m-%d')
    st.sidebar.success(f"최신 데이터 업데이트: {latest_date} (총 {len(df)}건)")
    
    # 분석 메뉴 선택
    selected_analysis = option_menu(
        menu_title=None,
        options=[
            "📈 모델별 판매 트렌드",
            "🌍 지역별 선호 모델", 
            "👥 고객 유형별 모델 선호도",
            "🏭 생산량 추천 시스템",
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
        selected_region = st.selectbox("지역 선택", regions)
        
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
    
    elif selected_analysis == "🏭 생산량 추천 시스템":
        st.header(f"{brand} 생산량 추천 시스템")
        
        # 모델 선택
        selected_model = st.selectbox(
            "모델 선택",
            df['구매한 제품'].unique(),
            key='model_production_select'
        )
        
        # 현재 재고량 입력
        current_inventory = st.number_input(
            f"현재 {selected_model} 재고량 입력",
            min_value=0,
            value=5,
            step=1
        )
        
        # 안전 재고율 설정
        safety_stock = st.slider(
            "안전 재고율 설정 (%)",
            min_value=0,
            max_value=50,
            value=20,
            step=5
        ) / 100
        
        analyze_production_recommendation(df, selected_model, current_inventory, safety_stock)
    
    elif selected_analysis == "📊 모델별 생산 우선순위":
        st.header(f"{brand} 모델별 생산 우선순위")
        
        # 모델별 우선순위 계산
        model_priority = calculate_model_priority(df)
        
        analyze_model_priority(df, model_priority)
