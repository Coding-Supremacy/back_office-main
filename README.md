# 🚗 AI 기반 고객 맞춤형 자동차 추천 및 영업전략 자동화 시스템

현대·기아차 실제 판매 데이터를 활용한 고객 세분화, 차량 추천, 판매 예측, 리포트 자동화까지 전 과정을 다루는 실전형 데이터 분석/AI 프로젝트입니다.

---

## 📁 데이터 구성

- **내부 판매 실적 데이터**  
  - 현대/기아차 차종별 · 국가별 · 월별 · 내수/수출/공장 데이터

- **가상 고객 데이터**  
  - ChatGPT 기반 국가별 고객 프로필 (이름, 선호, 구매 이력 등)

- **외부 보조 데이터**  
  - 국가별 GDP, 기후대, 경쟁사 판매량 등

---

## 🔄 데이터 전처리

- 문자열 숫자 변환 (`"5,388"` → `5388`)
- 컬럼명 통일 및 한글화 (`'Domestic'` → `'내수용'`)
- 결측치 처리 (`NaN` → `0`)
- 수치형/범주형 구분 후 전처리 파이프라인 적용

```python
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer

categorical_features = ['성별', '차량구분', '거래방식', '제품출시년월', '제품구매날짜', '친환경차']
numeric_features = ['연령', '거래금액', '구매빈도', '고객세그먼트']

preprocessor = ColumnTransformer([
    ('cat', OneHotEncoder(), categorical_features),
    ('num', StandardScaler(), numeric_features)
])
👥 고객 분석 및 추천
(1) RFM 기반 고객 클러스터링
KMeans (K=4): VIP, 일반, 신규, 이탈 가능 고객

입력: 거래일, 금액, 빈도 등

(2) 추가 고객 유형 클러스터링
성별, 차량유형, 친환경 여부, 연령 등 포함

Elbow method → 최적 K 도출

(3) 신규 고객 분류 모델
모델: GradientBoosting, RandomForest

정확도: 현대 99.2%, 기아 100%

📈 판매/수출 예측
Prophet 시계열 모델
python
복사
편집
from prophet import Prophet

model = Prophet()
model.fit(df_long[['ds', 'y']])
forecast = model.predict(model.make_future_dataframe(periods=12, freq='M'))
월별 실적 예측 (long format 필요)

계절성, 추세 반영 가능

LightGBM 다변량 모델
python
복사
편집
import lightgbm as lgb

params = {'objective': 'regression', 'metric': 'rmse'}
train_data = lgb.Dataset(X, label=y)
model = lgb.train(params, train_data, num_boost_round=100)
입력: GDP, 국가, 기후대, 이전 실적 등

타겟: 다음달 수출량 예측

📊 시각화 & 자동화
Streamlit 대시보드: 브랜드/국가/고객유형 기반 시각화 및 추천 결과 제공

자동화 기능:

보고서 생성

고객별 추천 차량 자동 발송

전략 요약 공유

🔁 전체 파이프라인 (요약)
mermaid
복사
편집
graph TD
A[데이터 수집] --> B[전처리]
B --> C1[RFM 클러스터링]
C1 --> C2[고객 유형 클러스터링]
C2 --> D[신규 고객 예측]
D --> E[차량 추천/전략 제안]
B --> F1[Prophet 예측]
B --> F2[LightGBM 예측]
F1 --> G[대시보드 시각화]
F2 --> G
E --> G
