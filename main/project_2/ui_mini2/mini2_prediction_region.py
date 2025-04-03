import os
import tempfile
from fpdf import FPDF
import streamlit as st
import pandas as pd
import pickle
import plotly.graph_objects as go
import requests
from prophet import Prophet
from openai import OpenAI
from streamlit_option_menu import option_menu
import datetime
import re
from pathlib import Path

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

TEST_MODE = True

def clean_text(text):
    # 유니코드 이모지 및 특수기호 제거
    return re.sub(r"[^\u0000-\uD7FF\uE000-\uFFFF]", "", text)

def load_model(channel, selected_market, model_dir):
    channel_key_map = {
        "현대": "hyundai",
        "기아": "kia"
    }
    channel_key = channel_key_map[channel]
    filename = f"{channel_key}_{selected_market}_model.pkl"
    model_path = os.path.join(model_dir, filename)

    if not os.path.exists(model_path):
        st.error(f"❌ 해당 모델 파일이 존재하지 않습니다: {filename}")
        return None

    with open(model_path, "rb") as f:
        model = pickle.load(f)
    return model

def load_sales_data(csv_path, selected_market):
    df = pd.read_csv(csv_path)
    df["ds"] = pd.to_datetime(df["ds"])
    df = df[df["국가"] == selected_market][["ds", "y"]].copy()
    return df

def create_forecast(model, periods=18, freq="ME"):
    future = model.make_future_dataframe(periods=periods, freq=freq)
    forecast = model.predict(future)
    return forecast

def plot_forecast(df_actual, forecast, selected_market):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=forecast["ds"], y=forecast["yhat"],
        mode='lines+markers', name='예측값', line=dict(color='blue')
    ))
    fig.add_trace(go.Scatter(
        x=df_actual["ds"], y=df_actual["y"],
        mode='lines', name='실제값', line=dict(color='orange', dash='dash')
    ))
    fig.add_trace(go.Scatter(
        x=forecast["ds"].tolist() + forecast["ds"][::-1].tolist(),
        y=forecast["yhat_upper"].tolist() + forecast["yhat_lower"][::-1].tolist(),
        fill='toself', fillcolor='rgba(0,100,80,0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip", showlegend=True, name='신뢰구간'
    ))
    fig.update_layout(
        title=f"[{selected_market}] 수출 실적 예측",
        xaxis_title="날짜",
        yaxis_title="수출량",
        legend=dict(x=0.01, y=0.99),
        template="plotly_white"
    )
    fig.update_xaxes(
        tickformat="%Y-%m", dtick="M1", tickangle=45,
        range=["2024-10-01", forecast["ds"].max().strftime("%Y-%m-%d")]
    )
    return fig

def fetch_news(query, display=5):
    headers = {
        "X-Naver-Client-Id": st.secrets["X-Naver-Client-Id"],
        "X-Naver-Client-Secret": st.secrets["X-Naver-Client-Secret"],
    }
    params = {"query": query, "display": display, "sort": "date"}
    url = "https://openapi.naver.com/v1/search/news.json"
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get("items", [])
    else:
        return []

def run_prediction_region():
    BASE_DIR = Path(__file__).resolve().parent.parent # Path 객체 반환
    DATA_DIR = BASE_DIR / "mini2_data"
    MODEL_DIR = BASE_DIR / "mini2_models"
    
    CSV_PATH_MAP = {
        "현대": DATA_DIR / "현대_시장구분별_수출실적.csv",
        "기아": DATA_DIR / "기아_시장구분별_수출실적.csv"
    }

    channel = st.session_state.get("brand", "현대")
    
    market_label_map = {
        "미국": "북미-미국", "캐나다": "북미-캐나다", "멕시코": "북미-멕시코",
        "동유럽": "동유럽", "서유럽": "서유럽", "아시아": "아시아",
        "중남미": "중남미", "중동·아프리카": "중동·아프리카"
    }
    selected_label = st.selectbox("국가를 선택하세요", list(market_label_map.keys()))
    selected_market = market_label_map[selected_label]

    st.title(f"{channel} - 국가별 수출실적 예측")
    st.markdown(f"""
### 수출 실적 예측 대시보드
이 페이지는 {channel}차의 **2021년~2025년 1월 까지의 국가별 수출 실적** 데이터를 기반으로,
**향후 18개월간 예측된 수출 추세**를 시각화하고,
**관련 뉴스 기사**를 통해 최근 이슈와 전망을 함께 제공합니다.
""")

    if selected_market:
        model = load_model(channel, selected_market, MODEL_DIR)
        if model is None:
            return
        forecast = create_forecast(model)
        df_actual = load_sales_data(CSV_PATH_MAP[channel], selected_market)
        st.plotly_chart(plot_forecast(df_actual, forecast, selected_market), use_container_width=True)

        # 뉴스 섹션 추가
        st.subheader(f"[{selected_label}] 관련 최신 뉴스")
        query = f"{selected_label} 자동차 수출"
        news_items = fetch_news(query)
        if news_items:
            cols = st.columns(len(news_items))
            for i, news in enumerate(news_items):
                with cols[i]:
                    title = news["title"].replace("<b>", "").replace("</b>", "")
                    description = news.get("description", "").replace("<b>", "").replace("</b>", "")
                    link = news["link"]
                    st.markdown(f"""
                    <div style="border:1px solid #ddd; border-radius:10px; padding:10px; text-align:center; height: 300px; display: flex; flex-direction: column; justify-content: space-between; overflow: hidden;">
                        <div style="flex-grow: 1;">
                            <a href="{link}" target="_blank" style="text-decoration:none;"><strong>{title}</strong></a>
                            <hr style="border: 0; height: 1px; background-color: #ccc; margin: 10px 0;">
                            <p style="font-size:14px; color:#555; margin-top:10px; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 6; -webkit-box-orient: vertical;">{description}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("뉴스 데이터를 불러올 수 없습니다.")

        st.markdown("#### 분석을 원하는 분기를 선택해주세요")
        quarter_options = {
            "2025년 1분기 (1~3월)": datetime.date(2025, 1, 1),
            "2025년 2분기 (4~6월)": datetime.date(2025, 4, 1),
            "2025년 3분기 (7~9월)": datetime.date(2025, 7, 1),
            "2025년 4분기 (10~12월)": datetime.date(2025, 10, 1),
            "2026년 1분기 (1~3월)": datetime.date(2026, 1, 1),
            "2026년 2분기 (4~6월)": datetime.date(2026, 4, 1)
        }
        selected_q_label = st.selectbox("분기를 선택하세요", list(quarter_options.keys()))
        selected_date = pd.to_datetime(quarter_options[selected_q_label])

        start_range = selected_date - pd.DateOffset(months=3)
        end_range = selected_date + pd.DateOffset(months=3)

        forecast_selected = forecast[(forecast["ds"] >= start_range) & (forecast["ds"] <= end_range)][["ds", "yhat", "yhat_lower", "yhat_upper"]].copy()
        forecast_selected["월"] = forecast_selected["ds"].apply(
            lambda d: (d + pd.DateOffset(days=1)).strftime("%Y년 %m월") if d.is_month_end else d.strftime("%Y년 %m월")
        )
        forecast_selected = forecast_selected.rename(columns={
            "yhat": "예측치", "yhat_lower": "하한", "yhat_upper": "상한"
        })
        highlight_months = pd.date_range(start=selected_date, periods=3, freq="MS").strftime("%Y년 %m월").tolist()

        def highlight_selected_quarter(row):
            if row["월"] in highlight_months:
                return ['background-color: #D5F5E3'] * len(row)
            else:
                return [''] * len(row)

        st.markdown(f"#### {selected_q_label} 예측 데이터")
        st.dataframe(
            forecast_selected[["월", "예측치", "하한", "상한"]].style
                .apply(highlight_selected_quarter, axis=1)
                .format({"예측치": "{:,.0f}", "하한": "{:,.0f}", "상한": "{:,.0f}"}),
            use_container_width=True, hide_index=True
        )

        st.subheader("AI 분석가의 시장 분석과 예측")
        if "report_text" not in st.session_state:
            st.session_state.report_text = None

        if st.button("AI 분석 실행"):
            if forecast_selected.empty:
                st.warning("예측 데이터가 충분하지 않아 AI 분석을 생성할 수 없습니다.")
                return

            forecast_start = forecast_selected["예측치"].iloc[0]
            forecast_end = forecast_selected["예측치"].iloc[-1]
            forecast_trend = "증가세" if forecast_end > forecast_start else "감소세"

            news_items = fetch_news(f"{selected_label} 자동차 수출")
            news_keywords = ", ".join([n["title"].replace("<b>", "").replace("</b>", "") for n in news_items[:3]])

            recent_actual = df_actual.sort_values("ds").tail(12)
            actual_trend_str = ", ".join([
                f"{row['ds'].strftime('%Y-%m')}: {int(row['y'])}" for _, row in recent_actual.iterrows()
            ])

            trend_data_str = ", ".join([
                f"{row['월']}: {int(row['예측치'])}" for _, row in forecast_selected.iterrows()
            ])

            prompt = f"""
당신은 자동차 수출 시장을 분석하는 전문 보고서 작성자입니다. 아래 정보를 바탕으로, [시장 분석 보고서]를 작성해주세요.
- 브랜드: {channel}
- 시장명: {selected_label}
- 최근 12개월간 실제 수출 실적: {actual_trend_str}
- 선택한 분기: {selected_q_label}
- ±1분기 예측 추세: {forecast_trend}  
- ±1분기 예측 수출량 추이: {trend_data_str}
- 최근 뉴스 키워드: {news_keywords}

보고서 형식은 다음과 같이 작성해주세요:

1. **{selected_label} 시장 예측 분석**  
{selected_label} 시장의 특징과 현재 상황을 분석합니다.

2. **최근 동향 요약**  
뉴스 키워드를 바탕으로 최근 이슈 및 자동차 수출과 관련된 주요 변화 사항을 서술합니다.  
해당 뉴스 키워드가 자동차 수출 시장에 긍정적 혹은 부정적인 영향을 줄지도 분석해주세요.

3. **선택된 시점 ±1분기 예측 분석**  
선택된 분기를 기준으로 총 6개월의 수출 예측 흐름을 분석해주세요.  
어떤 요인들이 영향을 미칠 것으로 보이며, 어떤 주의사항이나 기회가 있는지 설명해주세요.

4. **전략적 제안**  
자동차 제조업체 또는 관련 산업이 향후 어떻게 대응하면 좋을지 구체적이고 현실적인 전략을 제시해주세요.

보고서는 **전문적이지만 이해하기 쉽게**, **한글로** 작성해주세요.
"""
            try:
                if TEST_MODE:
                    st.session_state.report_text = "🧪 [테스트 모드] 실제 보고서 대신 이 문구가 출력됩니다.\nPDF 저장 및 레이아웃 확인용입니다."
                else:
                    with st.spinner("GPT-4 Turbo가 분석 중입니다..."):
                        response = client.chat.completions.create(
                            model="gpt-4-0125-preview",
                            messages=[
                                {"role": "system", "content": "당신은 자동차 수출 시장 전문 보고서를 작성하는 전문가입니다."},
                                {"role": "user", "content": prompt}
                            ]
                        )
                        st.session_state.report_text = response.choices[0].message.content.strip()
            except Exception as e:
                st.error(f"AI 분석 중 오류 발생: {e}")

        # 세션 상태에 보고서가 있다면 출력 및 PDF 저장 가능하도록
        if st.session_state.get("report_text"):
            st.markdown("### 📄 AI 분석 보고서")
            st.text_area("보고서 내용", st.session_state.report_text, height=400, label_visibility="collapsed")
            
            st.markdown("---")
            st.markdown("#### 📀 보고서를 PDF로 저장하기")
            
            def generate_pdf():
                import shutil

                pdf = FPDF()
                pdf.add_page()
                pdf.set_auto_page_break(auto=True, margin=15)

                FONT_PATH_ORIG = "main_project/project_2/fonts/NanumGothic.ttf"
                TEMP_FONT_PATH = os.path.join(tempfile.gettempdir(), "NanumGothic.ttf")

                # 임시 경로에 복사
                try:
                    shutil.copy(FONT_PATH_ORIG, TEMP_FONT_PATH)
                except Exception as e:
                    st.error(f"폰트 복사 중 오류 발생: {e}")
                    return None

                if os.path.exists(TEMP_FONT_PATH):
                    pdf.add_font("NanumGothic", "", TEMP_FONT_PATH, uni=True)
                    pdf.set_font("NanumGothic", size=10)
                else:
                    pdf.set_font("Arial", size=10)

                lines = clean_text(st.session_state.report_text).split('\n')
                for line in lines:
                    for i in range(0, len(line), 60):
                        pdf.cell(0, 10, line[i:i+60], ln=1)

                return pdf.output(dest='S').encode('latin-1')

            st.download_button(
                label="📥 PDF 다운로드",
                data=generate_pdf(),
                file_name=f"{selected_label}_시장_분석_보고서.pdf",
                mime="application/pdf",
                key="pdf_download"
            )
