import os
import tempfile
import time
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

TEST_MODE = False

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
    DATA_DIR = BASE_DIR / "data_mini2"
    MODEL_DIR = BASE_DIR / "models_mini2"
    
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
                    with st.spinner("AI 분석 중입니다..."):
                        time.sleep(2)
                        st.session_state.report_text = """### 미국 시장 예측 분석

미국 자동차 시장은 전 세계에서 가장 크고 영향력 있는 시장 중 하나입니다. 연간 판매량, 소비자 다양성, 기술 혁신에서 미국 시장은 주요 자동차 제조사들에게 중요한 역할을 합니다. 최근 몇 년 동안, 미국 시장의 자동차 소비 패턴은 친환경 차량의 선호도 증가, SUV와 픽업 트럭에 대한 높은 수요, 그리고 디지털 기술과 연결성을 중시하는 경향을 보였습니다.

### 최근 동향 요약

최근 뉴스에 따르면, "도요타, 25% 관세 부과시 영업이익 30% 감소 전망"과 같은 보도가 나왔고, "트럼프 무차별 관세속 한·중·일 만남 3국 FTA 및 경제통상 협력 확대"에 대한 논의가 있었습니다. 이러한 뉴스는 현재 글로벌 무역 환경이 매우 불확실하며, 높은 관세와 무역 전쟁이 전 세계 자동차 산업에 큰 부정적 영향을 미칠 수 있음을 시사합니다. 특히, 미국 내에서의 고관세는 자동차 제조사의 비용을 증가시키고 최종 소비자 가격에 영향을 미쳐 수요 감소로 이어질 수 있습니다.

### 선택된 시점 ±1분기 예측 분석

2025년 1분기를 중심으로 한 6개월 간의 현대 자동차의 미국 시장 수출 예측은 전반적인 감소세를 보여주고 있습니다. 예측된 수출량은 2024년 10월 59,286대에서 2025년 3월 58,093대로 점차 감소세를 나타내고 있으며, 이는 글로벌 무역 환경의 불확실성, 높은 관세 부과의 가능성, 그리고 미국 내 자동차 시장의 수요 변화에 대한 반응으로 해석할 수 있습니다. 특히, 고관세로 인한 비용 증가와 소비자 구매력 저하가 수출 감소에 주요한 영향을 미칠 것으로 예상됩니다.

### 전략적 제안

1. **관세 회피 전략 수립**: 현대는 관세 부담 최소화를 위해 미국 내 현지 생산을 확대하고, 북미 지역에서의 부품 조달 비중을 증가시킬 필요가 있습니다.
2. **제품 포트폴리오 다양화**: 미국 시장의 수요 변화에 유연하게 대응하기 위해, 현대는 친환경 차량과 SUV, 픽업 트럭 등 다양한 범위의 제품을 제공할 필요가 있습니다.
3. **디지털 마케팅 강화**: 온라인 판매 채널과 소셜미디어 마케팅을 강화하여 변화하는 소비자 구매 행태에 적응하고, 소비자와의 직접적인 소통을 늘릴 필요가 있습니다.
4. **경제적 불확실성에 대비한 유연한 가격 정책**: 고관세와 같은 경제적 요인으로 인한 비용 증가에도 불구하고, 소비자 수요를 유지하기 위해 가격 인상을 최소화하고 다양한 프로모션과 구매 유인책을 마련해야 합니다.
5. **국제 협력 및 로비 활동 강화**: 무역 환경과 관련된 정책의 변화에 적극적으로 대응하기 위해, 현대는 한국 및 기타 국제 기업들과의 협력을 강화하고, 미국 정부 및 관련 기관에 대한 로비 활동을 적극적으로 전개해야 합니다."""
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
            from markdown import markdown
            st.markdown("### 📄 AI 분석 보고서")

            # 마크다운 문법을 HTML로 변환
            report_html = markdown(st.session_state.report_text)

            # 변환된 HTML을 박스에 출력
            st.markdown(f"""
            <div style="
                background-color: #FAFAFA;
                border: 1px solid #D5DBDB;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                font-size: 16px;
            ">
                {report_html}
            </div>
            """, unsafe_allow_html=True)
            st.markdown("---")
            st.markdown("#### 📀 보고서를 PDF로 저장하기")
            
            def generate_pdf():
                import shutil

                # PDF 설정 (가로세로 A4, UTF-8 인코딩)
                pdf = FPDF('P', 'mm', 'A4')
                pdf.add_page()
                pdf.set_auto_page_break(auto=True, margin=20)
                pdf.set_left_margin(15)
                
                # 폰트 경로 설정
                FONT_DIR = "custom_fonts"
                FONT_REGULAR = os.path.join(FONT_DIR, "NanumGothic.ttf")
                FONT_BOLD = os.path.join(FONT_DIR, "NanumGothicBold.ttf")
                
                # 임시 폰트 처리
                try:
                    temp_dir = tempfile.gettempdir()
                    temp_files = []
                    for font_src, font_name in [(FONT_REGULAR, "NanumGothic.ttf"), 
                                            (FONT_BOLD, "NanumGothicBold.ttf")]:
                        temp_path = os.path.join(temp_dir, font_name)
                        if os.path.exists(temp_path): os.remove(temp_path)
                        shutil.copy(font_src, temp_path)
                        temp_files.append(temp_path)
                        
                    # 폰트 등록
                    pdf.add_font("NanumGothic", "", temp_files[0], uni=True)
                    pdf.add_font("NanumGothic", "B", temp_files[1], uni=True)
                except Exception as e:
                    st.error(f"폰트 로드 실패: {str(e)}")
                    return None

                # 텍스트 렌더링 함수 (글자 잘림 방지)
                def render_text(text, style="", size=11, is_bold=False):
                    text = text.replace("**", "").replace("##", "").strip()
                    if not text: 
                        pdf.ln(8)
                        return
                        
                    pdf.set_font("NanumGothic", "B" if is_bold else style, size)
                    
                    # 효율적인 줄바꿈 처리 (한글 최적화)
                    char_width = pdf.get_string_width("가")  # 한글 문자 너비 기준
                    max_chars = int((pdf.w - 2*pdf.l_margin) / char_width) - 3
                    
                    lines = []
                    current_line = ""
                    for word in text.split():
                        if pdf.get_string_width(current_line + word) < (pdf.w - 2*pdf.l_margin - 10):
                            current_line += word + " "
                        else:
                            lines.append(current_line)
                            current_line = word + " "
                    lines.append(current_line)
                    
                    for line in lines:
                        pdf.cell(0, 10, line.strip(), ln=True)
                    pdf.ln(5)

                # 본문 처리
                for line in st.session_state.report_text.split('\n'):
                    line = line.strip()
                    
                    # 1. 제목 처리 (#, ##)
                    if line.startswith("#"):
                        level = line.count("#")
                        title = line.replace("#", "").strip()
                        render_text(title, size=14-level*2, is_bold=True)
                        
                    # 2. 리스트 항목 (1., 2. 등)
                    elif re.match(r'^\d+\.', line):
                        pdf.set_font("NanumGothic", "B", 11)
                        num_part = re.match(r'^\d+\.', line).group()
                        pdf.cell(10, 10, num_part, ln=False)
                        
                        content = line[len(num_part):]
                        render_text(content, is_bold=True)
                        
                    # 3. 일반 텍스트
                    else:
                        render_text(line)

                return pdf.output(dest='S').encode('latin-1')

            st.download_button(
                label="📥 PDF 다운로드",
                data=generate_pdf(),
                file_name=f"{selected_label}_시장_분석_보고서.pdf",
                mime="application/pdf",
                key="pdf_download"
            )

