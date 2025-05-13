데이터 및 분석 프로세스 (README.md 예시, 코드·로직·도식 포함)
아래는 PPTX 파일에서 실제 프로젝트 분석 프로세스와 주요 코드, 로직 흐름을 최대한 상세히 정리한 예시입니다.
실제 코드 일부와 함께, 전체 데이터 흐름을 한눈에 볼 수 있도록 도식(머신러닝 파이프라인/분석 플로우)도 포함하였습니다.

데이터 및 분석 프로세스
1. 데이터 수집 및 구성
실제 판매·수출 데이터: 현대·기아차 2023~2025년 실적(차종, 국가, 공장, 월별 등)

가상 고객 데이터: ChatGPT 활용, 국가별 이름·차종·친환경 여부·구매빈도 등 현실 반영

외부 데이터: 국가별 GDP, 기후대, 경쟁사 판매량 등

2. 데이터 전처리 및 통합
문자 → 숫자 변환: "5,388" → 5388

컬럼명 표준화: 브랜드별·연도별 다른 컬럼명을 한글로 통일

결측치 처리: NaN → 0 또는 최소값(min) 대체

연도 컬럼 추가 및 통합: 연도별/지역별/차종별 데이터를 하나의 데이터프레임으로 합침

범주형·수치형 분리 및 인코딩:

범주형: OneHotEncoder

수치형: StandardScaler

python
# 예시: 문자열 숫자 변환 및 컬럼 표준화
df['판매량'] = df['판매량'].str.replace(',', '').astype(int)
df.rename(columns={'Domestic': '내수용', 'Recreational Vehicle': '휴양용 차량'}, inplace=True)

# 결측치 처리
df.fillna(0, inplace=True)

# 범주형/수치형 분리 및 파이프라인
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer

categorical_features = ['성별', '차량구분', '거래방식', '제품출시년월', '제품구매날짜', '친환경차']
numeric_features = ['연령', '거래금액', '구매빈도', '고객세그먼트']

preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(), categorical_features),
        ('num', StandardScaler(), numeric_features)
    ])
3. 고객 세분화 및 추천 시스템
(1) 1차 RFM 기반 클러스터링
입력 피처: 거래방식, 출시년월, 구매날짜, 거래금액, 구매빈도

K-Means: K=4 (VIP, 일반, 신규, 이탈가능)

파이프라인: 범주형 OneHot, 수치형 StandardScaler

python
from sklearn.cluster import KMeans

# 전처리 후 K-Means
X = preprocessor.fit_transform(df)
kmeans = KMeans(n_clusters=4, random_state=42)
df['고객세그먼트'] = kmeans.fit_predict(X)
(2) 2차 고객 유형 클러스터링
입력 피처: 성별, 차량구분, 친환경차, 연령 등 추가

K-Means: Elbow Method로 K=6 선정

python
from sklearn.metrics import silhouette_score

# 최적 K 탐색 (엘보우 메소드)
wcss = []
for k in range(2, 11):
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(X)
    wcss.append(kmeans.inertia_)
# (wcss 그래프 시각화로 최적 K 선택)
(3) 신규 고객 유형 예측 (분류 모델)
입력 피처: 위 클러스터링과 동일

타겟: 클러스터 라벨

모델 비교: RandomForest, GradientBoosting, SVC → 현대: GradientBoosting(99.2%), 기아: RandomForest(100%)

python
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier

# 학습/테스트 분리
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 모델 학습
gb = GradientBoostingClassifier().fit(X_train, y_train)
rf = RandomForestClassifier().fit(X_train, y_train)

# 정확도 비교
print("GB:", gb.score(X_test, y_test), "RF:", rf.score(X_test, y_test))
4. 판매/수출/생산 예측 (시계열·다변량)
(1) Prophet 시계열 예측
데이터 변환: wide → long (월별 컬럼 melt), '날짜' → 'ds', '수출실적' → 'y'

계절성 설정: 월 단위 예측, daily/weekly seasonality 비활성화

python
from prophet import Prophet

# 데이터 melt 및 컬럼명 변경
df_long = pd.melt(df, id_vars=['국가', '연도'], value_vars=[f'{m}월' for m in range(1, 13)],
                  var_name='월', value_name='수출실적')
df_long['ds'] = pd.to_datetime(df_long['연도'].astype(str) + '-' + df_long['월'].str.replace('월', '') + '-01')
df_long.rename(columns={'수출실적': 'y'}, inplace=True)

# Prophet 모델
model = Prophet(daily_seasonality=False, weekly_seasonality=False)
model.fit(df_long[['ds', 'y']])
future = model.make_future_dataframe(periods=12, freq='M')
forecast = model.predict(future)
(2) LightGBM 다변량 예측
입력 피처: 수출량, 전월수출량(lag), 연도, 월, GDP, 국가명, 기후대, 차종구분, 차량구분

타겟: 다음달_수출량

python
import lightgbm as lgb

features = ['수출량', '전월_수출량', '연도', '월', 'GDP', '국가명', '기후대', '차종구분', '차량구분']
target = '다음달_수출량'

# 데이터 전처리 (OneHotEncoder, StandardScaler 적용)
X = preprocessor.fit_transform(df[features])
y = df[target]

# LightGBM 학습
train_data = lgb.Dataset(X, label=y)
params = {'objective': 'regression', 'metric': 'rmse'}
gbm = lgb.train(params, train_data, num_boost_round=100)
5. 실시간 대시보드 및 자동화
Streamlit 기반 대시보드: 브랜드/국가/고객유형별 실적, 추천, 예측 결과 실시간 시각화

자동화: 타겟 이메일/문자 발송, 실시간 보고서 생성, 마케팅 전략 자동 제안

6. 전체 분석 프로세스 도식 (머신러닝 파이프라인)
text
graph TD
    A[데이터 수집] --> B[전처리 및 통합]
    B --> C1[RFM 클러스터링]
    C1 --> C2[고객유형 클러스터링]
    C2 --> D[고객 유형 예측 모델]
    D --> E[차량 추천/마케팅 자동화]
    B --> F1[판매/수출 데이터 변환]
    F1 --> F2[Prophet 시계열 예측]
    F1 --> F3[LightGBM 다변량 예측]
    F2 --> G[실시간 대시보드]
    F3 --> G
    E --> G
7. 주요 분석·추천 로직 요약
고객 입력 → 예측 → 추천 → 저장/발송:

고객 정보 입력

클러스터/유형 예측

맞춤 차량·프로모션 추천

고객 데이터 저장 및 이메일/문자 자동 발송

판매/수출 예측 → 전략 제안:

Prophet/LightGBM 예측

계절성·트렌드 분석

생산/마케팅/재고 전략 자동 제시

8. (참고) PPTX 내 코드 포함 여부
PPTX 파일에는 실제 Python 코드 스니펫(전처리, 모델링, 예측 등)이 다수 포함되어 있습니다.

주요 파이프라인, 피처 엔지니어링, 모델 학습·예측 코드, Streamlit 자동화 코드 등이 슬라이드 내에 설명과 함께 삽입되어 있습니다.

추가로, 도식(머신러닝 파이프라인, 분석 흐름도)도 그림/텍스트 형태로 포함되어 있어 README에 mermaid 등으로 재구성하기 쉽습니다.
