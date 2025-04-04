import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from streamlit_option_menu import option_menu



# 데이터 로드 함수
@st.cache_data
def load_data(brand):
    try:
        df = pd.read_csv(f"data/{brand}_고객데이터_신규입력용.csv")
        df['제품 구매 날짜'] = pd.to_datetime(df['제품 구매 날짜'])
        df['구매월'] = df['제품 구매 날짜'].dt.to_period('M').astype(str)
        df['Cluster'] = df['Cluster'] + 1  # 클러스터 번호 1부터 시작하도록 조정
        return df
    except FileNotFoundError:
        st.error(f"{brand} 데이터 파일을 찾을 수 없습니다.")
        return pd.DataFrame()

# 생산량 추천 계산 함수
def calculate_production_recommendation(sales_trend, current_inventory, safety_stock=0.2):
    """
    sales_trend: 월별 판매량 시리즈 (최근 6개월 기준)
    current_inventory: 현재 재고량
    safety_stock: 안전 재고율 (기본값 20%)
    """
    avg_sales = sales_trend.mean()
    recommended_production = avg_sales * (1 + safety_stock) - current_inventory
    return max(0, recommended_production)

# 모델별 생산 우선순위 계산
def calculate_model_priority(df):
    model_stats = df.groupby('구매한 제품').agg({
        '거래 금액': 'mean',
        '제품구매빈도': 'mean',
        '제품 구매 날짜': 'count'
    }).rename(columns={'제품 구매 날짜': '판매량'})
    
    # 점수 계산 (표준화 후 가중평균)
    model_stats['수익성 점수'] = (model_stats['거래 금액'] / model_stats['거래 금액'].max()) * 0.4
    model_stats['충성도 점수'] = (model_stats['제품구매빈도'] / model_stats['제품구매빈도'].max()) * 0.3
    model_stats['인기 점수'] = (model_stats['판매량'] / model_stats['판매량'].max()) * 0.3
    
    model_stats['종합 점수'] = (model_stats['수익성 점수'] + 
                              model_stats['충성도 점수'] + 
                              model_stats['인기 점수'])
    
    return model_stats.sort_values('종합 점수', ascending=False)

# 메인 분석 함수
def run_all_eda():
    st.title("🚗 차량 생산량 최적화 분석 시스템")
    brand = st.session_state.get("brand", "현대")
    
    df = load_data(brand)
    
    if df.empty:
        st.warning("데이터를 불러오는 데 실패했습니다.")
    
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
        
        # 모델 선택 (멀티 선택 가능)
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
            value=(max_date - timedelta(days=365), max_date))  # 기본값 최근 6개월
        
        filtered_df = df[(df['구매한 제품'].isin(selected_models)) & 
                        (df['제품 구매 날짜'] >= date_range[0]) & 
                        (df['제품 구매 날짜'] <= date_range[1])]
        
        if filtered_df.empty:
            st.error("선택한 조건에 해당하는 데이터가 없습니다.")
            return
        
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
        
        # 최근 3개월 판매 통계
        st.subheader("최근 3개월 판매 통계")
        recent_months = monthly_sales.index[-3:]
        recent_sales = monthly_sales.loc[recent_months]
        
        col1, col2, col3 = st.columns(3)
        col1.metric("평균 판매량", f"{recent_sales.mean().mean():.1f}대")
        col2.metric("최대 판매량", f"{recent_sales.max().max()}대")
        col3.metric("최소 판매량", f"{recent_sales.min().min()}대")
        
        st.dataframe(recent_sales.style.format("{:.0f}대").background_gradient(cmap='Blues'))
        
    elif selected_analysis == "🌍 지역별 선호 모델":
        st.header(f"{brand} 지역별 선호 모델 분석")
        
        # 지역 선택
        regions = df['국가'].unique()
        selected_region = st.selectbox("지역 선택", regions)
        
        # 해당 지역 데이터 필터링
        region_df = df[df['국가'] == selected_region]
        
        # 모델별 판매량
        model_sales = region_df['구매한 제품'].value_counts().reset_index()
        model_sales.columns = ['모델', '판매량']
        
        # 상위 10개 모델 시각화
        top_models = model_sales.head(10)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"{selected_region} 인기 모델 Top 10")
            fig = px.bar(
                top_models,
                x='모델',
                y='판매량',
                color='모델',
                title=f"{selected_region} 인기 모델"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("판매 비율")
            fig = px.pie(
                top_models,
                names='모델',
                values='판매량',
                title=f"{selected_region} 모델별 판매 비율"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # 지역별 비교 분석
        st.subheader("지역별 모델 선호도 비교")
        
        # 비교할 지역 선택
        compare_regions = st.multiselect(
            "비교할 지역 선택",
            regions,
            default = list(dict.fromkeys([selected_region] + list(regions[:2]))))

    
        if compare_regions:
            compare_df = df[df['국가'].isin(compare_regions)]
            
            # 모델별 지역 판매량
            model_region_sales = compare_df.groupby(['구매한 제품', '국가']).size().unstack().fillna(0)
            
            # 상위 5개 모델만 표시
            top_5_models = model_region_sales.sum(axis=1).nlargest(5).index
            model_region_sales = model_region_sales.loc[top_5_models]
            
            st.dataframe(
                model_region_sales.style.background_gradient(cmap='Blues', axis=1)
            )
            
            # 히트맵 시각화
            fig = px.imshow(
                model_region_sales,
                labels=dict(x="지역", y="모델", color="판매량"),
                title="지역별 모델 선호도 비교"
            )
            st.plotly_chart(fig)
    
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
        
        # 선택한 클러스터의 모델 선호도
        cluster_preference = cluster_model.loc[selected_cluster].sort_values(ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"고객 유형 {selected_cluster} 선호 모델")
            fig = px.bar(
                cluster_preference.head(10),
                x=cluster_preference.head(10).index,
                y=cluster_preference.head(10).values,
                color=cluster_preference.head(10).index,
                title=f"고객 유형 {selected_cluster} Top 10 모델"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("모델 선호도 비율")
            fig = px.pie(
                cluster_preference.head(10),
                names=cluster_preference.head(10).index,
                values=cluster_preference.head(10).values,
                title=f"고객 유형 {selected_cluster} 모델 선호도"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # 모든 클러스터에 대한 모델 선호도 비교
        st.subheader("고객 유형별 모델 선호도 비교")
        
        # 비교할 모델 선택
        compare_models = st.multiselect(
            "비교할 모델 선택",
            df['구매한 제품'].unique(),
            default=df['구매한 제품'].value_counts().head(3).index.tolist()
        )
        
        if compare_models:
            model_cluster = df[df['구매한 제품'].isin(compare_models)]
            model_cluster = model_cluster.groupby(['구매한 제품', 'Cluster']).size().unstack().fillna(0)
            
            st.dataframe(
                model_cluster.style.background_gradient(cmap='Blues', axis=1)
            )
            
            # 클러스터별 모델 선호도 시각화
            fig = px.bar(
                model_cluster.T,
                barmode='group',
                title="고객 유형별 모델 선호도 비교"
            )
            st.plotly_chart(fig)
    
    elif selected_analysis == "🏭 생산량 추천 시스템":
        st.header(f"{brand} 생산량 추천 시스템")
        
        # 모델 선택
        selected_model = st.selectbox(
            "모델 선택",
            df['구매한 제품'].unique(),
            key='model_production_select'
        )
        
        # 최근 6개월 판매 데이터 
        recent_date = df['제품 구매 날짜'].max()
        six_months_ago = recent_date - timedelta(days=365)
        recent_sales = df[(df['구매한 제품'] == selected_model) & 
                         (df['제품 구매 날짜'] >= six_months_ago)]
        
        if recent_sales.empty:
            st.error("최근 1년 내 판매 데이터가 없습니다.")
            return
        
        # 월별 판매량 계산
        monthly_sales = recent_sales.groupby('구매월').size()
        
        # 현재 재고량 입력
        current_inventory = st.number_input(
            f"현재 {selected_model} 재고량 입력",
            min_value=0,
            value=5,
            step=5
        )
        
        # 안전 재고율 설정
        safety_stock = st.slider(
            "안전 재고율 설정 (%)",
            min_value=0,
            max_value=50,
            value=20,
            step=5
        ) / 100
        
        # 생산량 추천 계산
        recommended_production = calculate_production_recommendation(
            monthly_sales,
            current_inventory,
            safety_stock
        )
        
        st.subheader("생산량 추천 결과")
        
        col1, col2 = st.columns(2)
        col1.metric("최근 6개월 평균 판매량", f"{monthly_sales.mean():.1f}대/월")
        col2.metric("추천 생산량", f"{recommended_production:.0f}대")
        
        # 판매 추이 그래프
        st.subheader("최근 6개월 판매 추이")
        fig = px.line(
            x=monthly_sales.index,
            y=monthly_sales.values,
            title=f"{selected_model} 월별 판매량",
            labels={"x": "월", "y": "판매량"}
        )
        st.plotly_chart(fig)
        
        # 계절성 패턴 분석
        st.subheader("계절성 패턴 분석")
        
        # 월별 평균 판매량 계산 (전체 기간)
        df['구매월'] = df['제품 구매 날짜'].dt.month
        seasonal_pattern = df[df['구매한 제품'] == selected_model].groupby('구매월').size()
        
        fig = px.line(
            x=seasonal_pattern.index,
            y=seasonal_pattern.values,
            title=f"{selected_model} 월별 평균 판매 패턴 (전체 기간)",
            labels={"x": "월", "y": "평균 판매량"}
        )
        st.plotly_chart(fig)
    
    elif selected_analysis == "📊 모델별 생산 우선순위":
        st.header(f"{brand} 모델별 생산 우선순위")
        
        # 모델별 우선순위 계산
        model_priority = calculate_model_priority(df)
        
        st.subheader("모델별 종합 평가 점수")
        
        # 상위 10개 모델 표시
        top_models = model_priority.head(10)
        
        fig = px.bar(
            top_models,
            x=top_models.index,
            y='종합 점수',
            color='종합 점수',
            title="모델별 생산 우선순위 (종합 점수)"
        )
        st.plotly_chart(fig)
        
        # 상세 지표 비교
        st.subheader("모델별 상세 지표 비교")
        
        # 비교할 모델 선택
        compare_models = st.multiselect(
            "비교할 모델 선택",
            model_priority.index,
            default=model_priority.head(3).index.tolist()
        )
        
        if compare_models:
            compare_df = model_priority.loc[compare_models]
            
            # 지표 비교 바 차트
            fig = px.bar(
                compare_df,
                x=compare_df.index,
                y=['수익성 점수', '충성도 점수', '인기 점수'],
                barmode='group',
                title="모델별 평가 지표 비교"
            )
            st.plotly_chart(fig)
            
            # 현재 재고량 입력
            st.subheader("재고 현황 반영한 생산 우선순위")
            
            inventory_data = {}
            for model in compare_models:
                inventory_data[model] = st.number_input(
                    f"{model} 현재 재고량",
                    min_value=0,
                    value=10,
                    step=10,
                    key=f"inventory_{model}"
                )
            
            # 재고 회전율 계산
            inventory_df = pd.DataFrame({
                '모델': compare_models,
                '평균 판매량': [model_priority.loc[m, '판매량'] / len(df['구매월'].unique()) for m in compare_models],
                '현재 재고': [inventory_data[m] for m in compare_models],
                '종합 점수': [model_priority.loc[m, '종합 점수'] for m in compare_models]
            })
            
            inventory_df['재고 회전율'] = inventory_df['평균 판매량'] / inventory_df['현재 재고']
            inventory_df['생산 필요도'] = (inventory_df['종합 점수'] * (1 - inventory_df['재고 회전율']))
            
            st.dataframe(
                inventory_df.set_index('모델').style.background_gradient(cmap='Blues')
            )
            
            # 생산 필요도 시각화
            fig = px.bar(
                inventory_df,
                x='모델',
                y='생산 필요도',
                color='모델',
                title="재고 현황 반영한 생산 필요도"
            )
            st.plotly_chart(fig)

