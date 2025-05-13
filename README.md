# 🚗 AI 기반 고객 맞춤형 자동차 추천 및 영업전략 자동화 시스템

현대·기아차 실제 판매 데이터를 활용하여 고객 세분화·차량 추천·판매 예측·실시간 리포트 및 마케팅 자동화까지 아우르는 실전형 데이터 분석/AI 플랫폼

## 📂 데이터 및 분석 프로세스

### 1. 📥 데이터 수집 및 구성
- **내부 실적 데이터**: 현대·기아차 2023~2025년 판매·수출 데이터 (차종/국가/공장/월별 포함)
- **가상 고객 데이터**: ChatGPT로 생성한 국가별 고객 프로필 (이름, 차량 선호, 구매 빈도 등)
- **외부 보조 데이터**: 국가별 GDP, 기후대, 경쟁사 판매량 등

### 2. 🔧 데이터 전처리 및 통합
```python
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer

categorical_features = ['성별', '차량구분', '거래방식', '제품출시년월', '제품구매날짜', '친환경차']
numeric_features = ['연령', '거래금액', '구매빈도', '고객세그먼트']

preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(), categorical_features),
        ('num', StandardScaler(), numeric_features)
    ])
```
## 👥 고객 세분화 및 추천 시스템
### ✅ (1차) RFM 기반 클러스터링
KMeans (K=4): VIP / 일반 / 신규 / 이탈 가능 고객 분류

입력 피처: 거래방식, 출시일, 구매일, 금액, 빈도 등

### ✅ (2차) 고객 유형 클러스터링
추가 입력: 성별, 차량유형, 친환경 여부, 연령 등

Elbow method 기반 최적 K 선택 (예: K=6)

### ✅ 신규 고객 유형 예측
``` python
# GradientBoosting/RandomForest 분류 모델
from sklearn.ensemble import GradientBoostingClassifier

gb_model = GradientBoostingClassifier()
gb_model.fit(X_train, y_train)
```
# 예측 정확도: 현대 99.2%, 기아 100%
📈 판매/수출/생산 예측
🔮 Prophet 시계열 예측
``` python
from prophet import Prophet

model = Prophet(daily_seasonality=False, weekly_seasonality=False)
model.fit(df_long[['ds', 'y']])
forecast = model.predict(model.make_future_dataframe(periods=12, freq='M'))
```

### 💡 LightGBM 다변량 예측
```python
import lightgbm as lgb

params = {'objective': 'regression', 'metric': 'rmse'}
train_data = lgb.Dataset(X, label=y)
gbm = lgb.train(params, train_data, num_boost_round=100)
```
### 📊 실시간 대시보드
Streamlit 기반 시각화

자동화: 이메일 발송, 보고서 생성, 마케팅 전략 제안

🔁 전체 파이프라인 아키텍처
``` graph TD
    A[데이터 수집] --> B[전처리]
    B --> C1[RFM 클러스터링]
    C1 --> C2[고객유형 클러스터링]
    C2 --> D[고객 유형 예측]
    D --> E[차량 추천]
    B --> F1[데이터 변환]
    F1 --> F2[Prophet 예측]
    F1 --> F3[LightGBM 예측]
    F2 --> G[대시보드]
    F3 --> G
    E --> G
```

### 🧠 핵심 로직 요약
고객 분석 흐름
고객 정보 입력 → 2. 클러스터링 → 3. 차량 추천 → 4. 결과 발송

판매 예측 흐름
다중 모델 예측 → 2. 트렌드 분석 → 3. 전략 자동화
