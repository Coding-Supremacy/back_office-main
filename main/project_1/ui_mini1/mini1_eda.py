import streamlit as st
import os
import pandas as pd
import plotly.express as px
import plotly.colors as pc
from streamlit_option_menu import option_menu
from streamlit_autorefresh import st_autorefresh
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import datetime
from email.mime.image import MIMEImage
#클러스터별 차량추천
brand_recommendations = {
    '현대': {
        0: ['Avante (CN7 N)', 'NEXO (FE)', 'Santa-Fe ™'],
        1: ['G80 (RG3)', 'G90 (HI)', 'IONIQ 6 (CE)'],
        2: ['G70 (IK)', 'i30 (PD)', 'Avante (CN7 HEV)'],
        3: ['Avante (CN7 N)', 'Tucson (NX4 PHEV)', 'Grandeur (GN7 HEV)'],
        4: ['IONIQ (AE EV)', 'NEXO (FE)', 'Tucson (NX4 PHEV)'],
        5: ['Santa-Fe ™', 'G70 (IK)', 'Grandeur (GN7 HEV)'],
        6: ['i30 (PD)', 'Avante (CN7 N)', 'Avante (CN7 HEV)'],
        7: ['IONIQ 6 (CE)', 'NEXO (FE)', 'G90 (RS4)']
    },
    '기아': {
        0: ['Forte', 'KX1', 'KX3', 'Rio (pride)', 'Seltos', 'Sonet', 'Syros', 'Zhipao', 'Carnival'],
        1: ['EV6', 'EV9', 'K4', 'K8', 'KX5', 'KX7', 'Sorento', 'Sportage', 'Telluride'],
        2: ['Cerato', 'EV5', 'EV6', 'G70 (IK)', 'K3', 'K5', 'Optima / K5'],
        3: ['C\'eed', 'C\'eed CUV', 'Cerato', 'Forte', 'K2', 'K3', 'KX3', 'Pegas', 'Rio (pride)', 'Seltos', 'Sonet', 'Sportage', 'Syros'],
        4: ['Carens MPV', 'Carnival', 'EV5', 'EV6', 'EV9', 'K4', 'KX5', 'Sorento', 'Telluride'],
        5: ['C\'eed', 'K2', 'Optima / K5', 'Pegas', 'Carnival']
    }
}

# 클러스터별 차량 추천 이유
vehicle_recommendations = {'현대':{
    "Avante (CN7 N)": {
        0: "젊은 연령대와 높은 거래 금액을 자랑하는 고객님께 딱 맞는 트렌디한 선택입니다. \n 최신형 세단으로 스타일과 실용성 두 마리 토끼를 잡을 수 있는 완벽한 선택입니다. \n 이 차량으로 한 단계 더 업그레이드된 라이프스타일을 경험해 보세요.",
        1: "VIP 고객님에게 어울리는 고급스러움을 제공하는 차량입니다. \n  고급 세단으로서 품격 있는 스타일을 완성해 드립니다. \n 더욱 럭셔리한 운전을 즐기세요.",
        2: "가격 대비 성능 최고! Avante (CN7 N)은 경제적이면서도 뛰어난 성능을 자랑하는 차량입니다.",
        3: "젊은 고객님, 스타일과 친환경성을 모두 고려한 Avante (CN7 N)!\n  최신 기술과 뛰어난 성능, 이 차량은 바로 고객님의 라이프스타일에 맞는 완벽한 파트너입니다.",
        4: "이 차량은 친환경차 선호도가 높은 고객님께도 안성맞춤!\n  가격 대비 성능이 뛰어나며 실용성도 고려한 Avante (CN7 N)을 추천 드립니다.",
        5: "신뢰할 수 있는 차량, Avante (CN7 N)!\n  현금 거래 비율이 높은 고객님께는 안정감과 실용성까지 제공하는 세련된 선택이 될 거예요.",
        6: "젊은 고객님들에게 더 없이 좋은 가격 대비 성능의 Avante (CN7 N)!\n  실용적이면서도 트렌디한 선택을 원하신다면 이 차가 바로 정답입니다.",
        7: "친환경차를 선호하시는 고객님에게 더할 나위 없이 좋은 전기차 옵션까지 고려한 Avante (CN7 N),\n  이 차와 함께라면 환경을 생각하는 운전이 가능해요."
    },
    "NEXO (FE)": {
        0: "환경보호에 관심을 가지기 시작하신 고객님께 완벽한 선택, 수소차 NEXO! \n 연령대가 젊고 환경을 생각하는 여러분께 딱 맞는 차량입니다. 지속 가능한 미래를 위한 선택을 하세요.",
        1: "친환경차 선호도가 높은 VIP 고객님께 완벽한 고급스러움과 친환경을 동시에 만족시킬 수 있는 차량, NEXO!\n  고급스러우면서도 환경을 생각하는 똑똑한 선택입니다.",
        4: "친환경차에 대한 관심이 높은 고객님께 맞춤 추천!\n  NEXO는 연료비 절감과 친환경적 요소를 모두 고려한 차량으로, 미래를 향한 현명한 선택입니다.",
        7: "친환경을 생각하는 고객님께 완벽한 선택, 수소차 NEXO!\n  완벽한 친환경차로, 여러분의 선택이 더욱 빛날 것입니다. 고급스러움과 친환경을 동시에 갖춘 NEXO를 만나보세요."
    },
    "Santa-Fe ™": {
        0: "가족 단위 고객님께 완벽한 공간과 실용성을 제공하는 Santa-Fe!\n  넓고 다용도로 사용 가능한 SUV, 장거리 여행에도 완벽한 선택입니다.\n  여러분의 생활을 더욱 편리하고 즐겁게 만들어 드려요!",
        5: "편안한 승차감과 넉넉한 공간을 자랑하는 Santa-Fe!\n  나이가 많고 현금 거래 비율이 높은 고객님께 실용적이고 신뢰할 수 있는 선택입니다. \n 가족과 함께 편안한 여행을 떠나세요!"
    },
    "G80 (RG3)": {
        1: "고급스러운 세단을 원하신다면 G80 (RG3)!\n  VIP 고객님께 딱 맞는 차량으로, 품격과 스타일을 모두 갖춘 선택입니다.\n  차 한 대로 고급스러움을 완성해 보세요."
    },
    "G90 (HI)": {
        1: "한 단계 더 높은 품격을 원하시는 고객님께 G90!\n  프리미엄 세단의 대명사로, 고급스러움과 편안함을 동시에 제공하는 차량입니다.\n  최상의 편안함을 원하신다면 G90을 선택하세요.",
        7: "거래 금액이 매우 높고, 친환경차를 선호하시는 고객님께 딱 맞는 고급 전기차, G90!\n  프리미엄 이미지를 더한 친환경차로, 완벽한 선택입니다."
    },
    "IONIQ 6 (CE)": {
        1: "친환경차에 대한 관심이 늘고 있는 고객님께, 고급 전기차 IONIQ 6! \n 고급스러운 외관과 첨단 기술을 갖춘 차량으로, 친환경을 고려하면서도 세련된 스타일을 제공합니다.",
        7: "친환경을 생각하는 고객님께 더욱 특별한 IONIQ 6! \n 고급스러움과 친환경성을 동시에 갖춘 전기차로, 미래 지향적인 선택이 될 것입니다."
    },
    "i30 (PD)": {
        2: "가격이 저렴하고 실용적인 소형차, i30! \n 연령대가 높고 거래 금액이 적은 고객님께 부담 없는 유지비와 실용성을 제공하는 완벽한 선택입니다.",
        6: "저렴한 가격으로 실용성을 고려한 i30! \n 거래 금액과 구매 빈도가 낮은 고객님께 실용적이고 경제적인 소형차를 추천드립니다."
    },
    "Tucson (NX4 PHEV)": {
        3: "환경을 고려한 플러그인 하이브리드 SUV, Tucson!\n  친환경차 비율이 높은 고객님께 적합한 선택으로, 실용적인 공간과 뛰어난 연비를 자랑합니다.",
        4: "연료 효율성을 중시하는 고객님께 맞춤 추천!\n  Tucson은 플러그인 하이브리드로, 경제적인 연비와 친환경성을 모두 고려한 차량입니다."
    },
    "Grandeur (GN7 HEV)": {
        3: "고객님께 적합한 차량, Grandeur HEV! \n 실용적이고 연비가 뛰어난 하이브리드 세단으로, 경제적인 선택이면서도 고급스러운 느낌을 제공합니다.",
        5: "연비가 뛰어난 하이브리드 세단, Grandeur! \n 거래 금액이 적은 고객님께 적합하며, 실용적이고 신뢰할 수 있는 선택입니다."
    },
    "IONIQ (AE EV)": {
        4: "친환경차에 관심많은 고객님께 가격대가 적당한 전기차인 IONIQ을 추천합니다. \n IONIQ은 연료비가 적고 실용적인 전기차로 적합합니다."
    },
    "G70 (IK)": {
        2: "고객님께 고급스러움을 더할 수 있는 G70!\n  가격대가 적당하면서도 고급스러움을 갖춘 차량으로, 차별화된 경험을 선사합니다.",
        5: "고급스러운 느낌의 세단을 선호하는 고객님께, G70! \n 거래 금액이 적더라도 품격을 높여 줄 차량입니다."
    },
    "Avante (CN7 HEV)": {
        2:"가격 대비 뛰어난 성능을 자랑하는 Avante (CN7 HEV)! 뛰어난 연비와 친환경적인 장점으로 실용적인 선택이 될 것입니다.\n경제적이면서도 환경을 고려한 현명한 선택을 하세요.",
        6:"젊은 고객님들에게 더 없이 좋은 가격 대비 성능의 Avante (CN7 N)! 좋은 연비로 실용적이면서도 트렌디한 선택을 원하신다면 이 차가 바로 정답입니다."
    }
},
'기아': {
    "C'eed": {
        3: "중형 세단 선호 고객님께 잘 어울리는 실용적인 차량입니다.\n경제적이고 꾸준한 운전에 적합합니다.",
        5: "처음 차량 구매를 고민하는 중장년층 고객님께 합리적인 선택이 될 수 있는 차량입니다."
    },
    "C'eed CUV": {
        0: "젊은 고객층의 개성과 실용성을 모두 만족시키는 CUV 모델입니다.\n중형 차량을 선호하는 고객님께 추천드립니다.",
        3: "비친환경 성향이 강한 고객님께 가성비 좋은 중형 CUV 모델로 추천드립니다."
    },
    "Carens MPV": {
        1: "SUV와 다목적 차량을 선호하는 VIP 고객님께 가족 단위 이동에 적합한 차량입니다.",
        4: "중장년층 고객님께 넓은 공간과 실용성을 제공하는 차량으로 추천드립니다."
    },
    "Carnival": {
        0: "젊은 연령대지만 대형 차량을 선호하는 고객님께 맞는 패밀리카입니다.",
        4: "SUV 성향의 중장년 고객님께 여유로운 공간과 활용도를 제공하는 차량입니다."
    },
    "Cerato": {
        2: "젊고 세단을 선호하는 VIP 고객층에게 실용적이면서 세련된 디자인의 차량입니다.",
        3: "비친환경 성향이 강한 고객님께 합리적인 가격대의 중형 세단으로 추천합니다."
    },
    "EV5": {
        2: "중간 수준의 친환경 성향을 가진 젊은 VIP 고객님께 전기 SUV EV5를 추천드립니다.",
        4: "전기차에 관심 있는 중장년 고객님께 실속 있는 선택이 될 수 있습니다."
    },
    "EV6": {
        1: "친환경 성향이 일부 있는 SUV 선호 고객님께 고급 전기 SUV EV6를 추천드립니다.",
        2: "젊은 VIP 고객님의 라이프스타일에 맞는 미래 지향적 선택입니다."
    },
    "EV9": {
        1: "SUV를 선호하면서도 고급 친환경차에 관심 있는 VIP 고객님께 적합한 플래그십 전기차입니다.",
        4: "중장년층의 SUV 친환경 트렌드를 만족시키는 고급 전기 SUV입니다."
    },
    "Forte": {
        0: "실속을 중요시하는 젊은 고객님께 추천되는 가성비 좋은 차량입니다.",
        3: "중형 세단 중심의 일반 고객층에게 실용성과 효율성을 제공합니다."
    },
    "K2": {
        3: "경제적인 세단을 원하는 젊은 고객님께 추천드립니다.\n기초적인 운송 수단으로 훌륭합니다.",
        5: "처음 차량을 구매하려는 중장년층 고객님께 부담 없는 선택지입니다."
    },
    "K3": {
        2: "젊고 실용적인 고객층에게 적합한 세단입니다.\n디자인과 기능을 모두 만족시킵니다.",
        3: "중형 세단 위주의 일반 고객에게 적합한 차량입니다."
    },
    "K4": {
        1: "고급 세단 성향의 중장년층 VIP 고객님께 스타일과 실용성을 제공하는 모델입니다.",
        4: "SUV 선호지만 세단도 고려하는 고객님께 고급 중형 세단으로 추천드립니다."
    },
    "K5": {
        2: "세련된 디자인과 중형 세단 선호 고객님께 잘 어울리는 차량입니다.",
        5: "고민 중인 고객님께 실용성과 품격을 동시에 제공하는 선택입니다."
    },
    "KX1": {
        0: "젊은 고객님들께 적합한 콤팩트 SUV입니다.\n도심 주행과 스타일을 모두 만족합니다."
    },
    "KX3": {
        0: "중형 SUV를 선호하는 젊은 고객에게 적합한 차량입니다.",
        3: "SUV의 실용성과 세련된 감각을 동시에 고려한 고객층에 맞습니다."
    },
    "KX5": {
        1: "SUV 중심의 VIP 고객님께 적절한 중형 SUV 선택지입니다.",
        4: "중장년층 SUV 선호 고객님께 좋은 선택이 될 수 있습니다."
    },
    "KX7": {
        1: "중장년층 VIP SUV 고객에게 대형 SUV로서의 품격을 제공합니다."
    },
    "Optima / K5": {
        2: "중형 세단의 대표 주자로 젊은 VIP 고객님께 추천드립니다.\n디자인과 기능 모두 만족!",
        5: "세단 선호 성향의 중장년층 신규 고객에게도 안정적인 선택입니다."
    },
    "Pegas": {
        3: "비용 효율성과 실용성을 중시하는 고객님께 맞는 소형 세단입니다.",
        5: "가벼운 운전과 낮은 유지비를 원하는 중장년 고객님께 추천드립니다."
    },
    "Rio (pride)": {
        0: "경제성을 최우선으로 하는 젊은 고객님께 맞는 차량입니다.",
        3: "도심형 운전에 적합하며 유지비 부담이 적은 선택지입니다."
    },
    "Seltos": {
        0: "트렌디한 디자인을 선호하는 젊은 층에게 어울리는 소형 SUV입니다.",
        3: "꾸준한 SUV 사용을 원하는 일반 고객에게 적합합니다."
    },
    "Sonet": {
        0: "도심형 SUV로 젊은 고객님께 안성맞춤입니다.\n작지만 강한 실용성을 제공합니다.",
        3: "SUV 스타일을 원하지만 부담 없는 크기를 원하는 고객께 추천드립니다."
    },
    "Sorento": {
        1: "SUV를 선호하는 중장년층 VIP 고객님께 적합한 패밀리카입니다.",
        4: "공간과 실용성을 중시하는 SUV 중심 고객님께 알맞은 대형 SUV입니다."
    },
    "Sportage": {
        1: "중장년층 SUV 중심 고객에게 잘 어울리는 인기 모델입니다.",
        4: "SUV를 실용적으로 활용하시는 고객님께 추천되는 차량입니다."
    },
    "Syros": {
        0: "젊고 개성 강한 고객님께 맞는 유니크한 선택지입니다.",
        3: "차별화된 디자인을 추구하는 중형차 선호 고객님께 어울립니다."
    },
    "Telluride": {
        1: "프리미엄 SUV를 찾는 중장년층 고객에게 최적의 선택입니다.\n넓은 공간과 고급감을 모두 갖춘 대형 SUV입니다.",
        4: "가족 단위 고객님께 편안함과 스타일을 제공하는 고급 SUV입니다."
    },
    "Zhipao": {
        0: "젊은 고객층에게 새로운 스타일과 가성비를 제공하는 실속형 차량입니다."
    }
}
}

#기본 차량 추천 이유
basic_recommendations = {
    '현대': {
        "Avante (CN7 N)": "Avante (CN7 N)은 뛰어난 성능과 스타일을 자랑하는 최신형 세단입니다. 실용성과 세련된 디자인을 갖춘 완벽한 선택입니다.",
        "NEXO (FE)": "NEXO는 친환경적인 수소차로, 연료비 절감과 환경을 생각하는 고객에게 안성맞춤입니다. 고급스러움과 친환경성을 동시에 제공합니다.",
        "Santa-Fe ™": "Santa-Fe는 넓고 다용도로 사용 가능한 공간을 자랑하는 SUV로, 가족 단위 여행에 적합합니다. 실용성과 편안함을 제공합니다.",
        "G80 (RG3)": "G80은 고급스러운 세단으로 품격 있는 운전 경험을 제공합니다. VIP 고객님에게 어울리는 차량입니다.",
        "G90 (HI)": "G90은 프리미엄 세단으로, 고급스러움과 편안함을 제공합니다. 모든 세부 사항이 완벽하게 설계되어 있어 최고의 만족감을 선사합니다.",
        "IONIQ 6 (CE)": "IONIQ 6는 첨단 기술과 세련된 디자인을 갖춘 전기차입니다. 친환경적인 드라이빙을 원하시는 고객님께 적합합니다.",
        "i30 (PD)": "i30은 실용적이고 경제적인 소형차로, 유지비가 적고 부담 없는 선택입니다. 특히 첫 차로 적합한 모델입니다.",
        "Tucson (NX4 PHEV)": "Tucson은 플러그인 하이브리드 SUV로, 환경을 고려하면서도 강력한 성능을 제공합니다. 연비 효율성이 뛰어난 차량입니다.",
        "Grandeur (GN7 HEV)": "Grandeur는 고급스러움과 실용성을 동시에 제공합니다. 하이브리드 모델로 연비가 뛰어나고, 가격대비 좋은 선택입니다.",
        "IONIQ (AE EV)": "IONIQ는 전기차로 연료비 절감과 친환경적인 운전이 가능합니다. 가격대비 성능이 뛰어난 모델입니다.",
        "G70 (IK)": "G70은 고급 세단으로, 가격대가 적당하면서도 고급스러운 느낌을 줄 수 있는 차량입니다. 세련된 디자인을 갖추고 있습니다.",
        "Palisade (LX2)": "Palisade는 넓고 고급스러운 3열 SUV로, 대가족이나 넉넉한 공간을 필요로 하는 고객님께 적합합니다. 높은 품질의 승차감을 제공합니다.",
        "Santa-Fe (MX5 PHEV)": "Santa-Fe PHEV는 플러그인 하이브리드 SUV로, 친환경을 고려하면서도 넓은 공간과 뛰어난 성능을 자랑하는 선택입니다.",
        "G90 (RS4)": "G90 RS4는 프리미엄 브랜드의 대표 모델로, 최고급 세단에 걸맞은 품격과 편안함을 제공합니다. 세부 사항까지 완벽한 선택입니다.",
        "Avante (CN7 HEV)": "친환경차 선호도가 높은 고객님께 Avante (CN7 HEV)! 하이브리드 모델로 연비 효율성을 자랑하며, 친환경적인 선택을 제공합니다."
    },
    '기아': {
        "K3": "K3는 세련된 디자인과 실용성을 겸비한 준중형 세단으로, 합리적인 가격대비 뛰어난 성능을 제공합니다.",
        "Pegas": "Pegas는 경제성과 실용성을 중시하는 고객을 위한 컴팩트 세단으로, 도심 주행에 최적화된 모델입니다.",
        "K5": "K5는 스포티한 디자인과 역동적인 주행 성능을 갖춘 중형 세단으로, 젊은 감각을 원하는 분들께 추천합니다.",
        "Rio(pride)": "Rio(Pride)는 컴팩트한 사이즈와 경제적인 운영 비용이 장점인 소형차로, 첫 차로 적합합니다.",
        "EV6": "EV6는 기아의 최신 전기차 기술이 집약된 크로스오버 SUV로, 혁신적인 디자인과 뛰어난 주행 거리가 특징입니다.",
        "KX7": "KX7는 넓은 실내 공간과 다양한 편의 사양을 갖춘 중대형 SUV로, 가족 여행에 적합합니다.",
        "C'eed CUV": "C'eed CUV는 유럽형 디자인과 실용성을 결합한 크로스오버로, 도시와 어우러지는 세련된 스타일을 자랑합니다.",
        "K4": "K4는 중형 세단의 편안함과 준중형의 경제성을 겸비한 모델로, 실용적인 선택을 원하는 분들께 적합합니다.",
        "Telluride": "Telluride는 미국 시장을 겨냥한 대형 SUV로, 웅장한 디자인과 풍부한 사양이 특징입니다.",
        "KX5": "KX5는 중형 SUV 시장에서 인기 있는 모델로, 균형 잡힌 성능과 스타일을 제공합니다.",
        "Seltos": "Seltos는 젊고 활동적인 라이프스타일에 맞는 소형 SUV로, 개성 있는 디자인과 다양한 컬러 옵션이 매력적입니다.",
        "Sorento": "Sorento는 프리미엄 감성과 실용성을 모두 갖춘 중대형 SUV로, 고급스러운 주행 경험을 제공합니다.",
        "Carnival": "Carnival은 뛰어난 실내 공간과 편의성을 자랑하는 대형 MPV로, 가족 단위 고객에게 최적화된 모델입니다.",
        "K2": "K2는 컴팩트한 사이즈와 경제적인 운영 비용이 장점인 소형 세단으로, 도심 주행에 적합합니다.",
        "KX3": "KX3는 개성 있는 디자인과 다양한 컬러 옵션으로 젊은 층에게 어필하는 소형 SUV입니다.",
        "Forte": "Forte는 실용성과 스타일을 겸비한 준중형 세단으로, 합리적인 가격대비 다양한 사양을 제공합니다.",
        "Carnival (CKD)": "Carnival (CKD)는 현지 조립 방식으로 제공되는 대형 MPV로, 원본 모델과 동일한 품질을 유지합니다.",
        "Carens MPV": "Carens MPV는 다목적 가족용 차량으로, 유연한 좌석 구성과 넉넉한 적재 공간이 특징입니다.",
        "Sonet": "Sonet은 인도 시장을 겨냥한 소형 SUV로, 콤팩트한 사이즈와 강렬한 디자인이 매력적입니다.",
        "Sportage": "Sportage는 기아의 대표 중형 SUV로, 세련된 디자인과 첨단 안전 사양을 자랑합니다.",
        "C'eed": "C'eed는 유럽 시장을 겨냥한 해치백 모델로, 동적 주행 성능과 실용성을 두루 갖췄습니다.",
        "Syros": "Syros는 중국 시장 전략 모델로 추정되는 세단으로, 독특한 디자인이 특징입니다.",
        "Cerato": "Cerato는 K3의 글로벌 명칭으로, 전 세계적으로 사랑받는 준중형 세단입니다.",
        "KX1": "KX1은 소형 SUV 시장에서 인기 있는 모델로, 도시형 라이프스타일에 최적화되었습니다.",
        "EV5": "EV5는 기아의 중형 전기 SUV로, 실용성과 친환경 기술의 조화를 추구합니다.",
        "Zhipao": "Zhipao는 중국 시장을 겨냥한 전략 모델로, 현지 소비자 취향에 맞춰 개발되었습니다.",
        "EV9": "EV9은 기아의 플래그십 전기 SUV로, 고급스러움과 첨단 기술이 결합된 모델입니다."
    }
}

# 개발자 모드 설정 (True: 실제 운영, False: 개발자 모드)
prod = False  # 이 값을 True로 변경하면 실제 고객에게 발송
prod_email = "marurun@naver.com"  # 개발자 이메일
brand = st.session_state.get("brand", "현대")



#분석 결과를 기반으로 클러스터별 마케팅 전략 자동 생성
def generate_marketing_strategies(country_df):
    strategies = {}
    
    # 클러스터 목록
    clusters = sorted(country_df['고객유형'].unique())
    
    # 1. 성별 분석 기반 전략
    gender_dist = country_df.groupby(['고객유형', '성별']).size().unstack(fill_value=0)
    gender_pct = gender_dist.div(gender_dist.sum(axis=1), axis=0) * 100
    
    # 2. 연령 분석 기반 전략
    age_stats = country_df.groupby('고객유형')['연령'].agg(['mean', 'std'])
    
    # 3. 거래 금액 분석 기반 전략
    transaction_stats = country_df.groupby('고객유형')['거래 금액'].mean()
    
    # 4. 구매 빈도 분석 기반 전략
    freq_stats = country_df.groupby('고객유형')['제품구매빈도'].mean()
    

    
    
    for cluster in clusters:
        strategy_parts = []
        
        # 성별 기반 전략
        male_pct = gender_pct.loc[cluster, '남']
        female_pct = gender_pct.loc[cluster, '여']
        
        if male_pct >= 60:
            strategy_parts.append("남성 고객님이 선호하는 스포츠 디자인과 첨단 기술이 집약된 모델 특별 프로모션!")
        elif female_pct >= 60:
            strategy_parts.append("안전성과 실용성을 중시하는 고객님을 위한 패밀리 전용 차량 혜택을 제공합니다.")
        else:
            strategy_parts.append("누구나 만족할 수 있는 다양한 트림과 옵션 구성을 제안드립니다.")
        
        # 연령 기반 전략
        avg_age = age_stats.loc[cluster, 'mean']
        
        if avg_age < 35:
            strategy_parts.append("SNS에서도 화제가 된 최신 디자인과 스마트 기능 차량을 추천드립니다.")
        elif avg_age >= 45:
            strategy_parts.append("넉넉한 공간, 편의 사양, 안전 기능까지 갖춘 차량을 특별 할인가에 제공해드립니다.")
        else:
            strategy_parts.append("세대 구분 없이 인기 있는 모델로, 스타일과 실용성을 동시에 만족시켜드립니다.")
        
        # 거래 금액 기반 전략
        avg_transaction = transaction_stats.loc[cluster]
        transaction_median = transaction_stats.median()
        
        if avg_transaction >= transaction_median * 1.2:
            strategy_parts.append("프리미엄 모델 고객님 전용, 전담 컨설팅과 VIP 시승 혜택을 제공해드립니다.")
        elif avg_transaction <= transaction_median * 0.8:
            strategy_parts.append("실속 있는 가격과 높은 연비를 자랑하는 합리적 모델을 특별 할인과 함께 안내드립니다.")
        else:
            strategy_parts.append("안정적인 인기 모델을 합리적인 가격에 만나보세요.")
        
        # 구매 빈도 기반 전략
        avg_freq = freq_stats.loc[cluster]
        freq_median = freq_stats.median()
        
        if avg_freq >= freq_median * 1.5:
            strategy_parts.append("단골 고객님께 감사의 마음을 담아, 멤버십 전용 혜택과 정기 유지관리 쿠폰을 제공합니다.")
        elif avg_freq <= freq_median * 0.7:
            strategy_parts.append("차량 구매를 고민 중이신가요? 지금 가입 시 오랜만에 오신 고객님을 위한 특별 할인 혜택을 드립니다.")
        
        # 전략 조합
        strategies[cluster] = "<br>• ".join(strategy_parts)
    
    return strategies, brand_recommendations

def send_email(customer_name, customer_email, message, cluster=None, marketing_strategies=None, brand_recommendations=None, purchased_model=None):
    # 개발자 모드인 경우 모든 이메일을 개발자 이메일로 발송
    if not prod:
        original_email = customer_email  # 원래 고객 이메일 저장 (로그용)
        customer_email = prod_email  # 개발자 이메일로 변경
        message = f"[개발자 모드] 원래 수신자: {original_email}<br><br>{message}"
    
    # 브랜드별 테마 설정
    brand = st.session_state.get("brand", "현대")
    
    if brand == "현대":
        primary_color = "#005bac"  # 현대 블루
        logo_alt = "현대 로고"
        logo_cid = "hyundai_logo"
        brand_name = "현대자동차"
        logo_path = "main/project_1/img/hyundai_logo.jpg"
    else:  # 기아
        primary_color = "#c10b30"  # 기아 레드
        logo_alt = "기아 로고"
        logo_cid = "kia_logo"
        brand_name = "기아자동차"
        logo_path = "main/project_1/img/kia_logo.png"
    
    # SMTP 서버 설정
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    EMAIL_ADDRESS = "vhzkflfltm6@gmail.com"
    EMAIL_PASSWORD = "cnvc dpea ldyv pfgq" 
    
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = customer_email
    msg['Subject'] = f"{customer_name}님, 프로모션 안내" if prod else f"[테스트] {customer_name}님, 프로모션 안내"

    # 고객에게 추천할 모델 목록 생성 (구매한 모델 제외)
    recommended_models = []
    if cluster and brand_recommendations and brand in brand_recommendations:
        cluster_key = cluster - 1 if brand == "현대" else cluster  # 현대는 1-8, 기아는 0-5
        if cluster_key in brand_recommendations[brand]:
            if purchased_model:
                # 구매한 모델을 제외한 추천 모델 목록
                recommended_models = [model for model in brand_recommendations[brand][cluster_key] 
                                      if model != purchased_model]
            else:
                # 구매한 모델 정보가 없는 경우 전체 추천
                recommended_models = brand_recommendations[brand][cluster_key]
    
    # 마케팅 전략과 추천 모델을 하나의 박스로 통합
    strategy_box_content = ""

    if cluster and marketing_strategies and cluster in marketing_strategies:
        strategy_box_content += f"""
        <div style="margin-bottom: 20px;">
            <h3 style="margin-top: 0; margin-bottom: 15px; color: {primary_color}; font-size: 18px;">고객님을 위한 맞춤형 제안</h3>
            <div style="font-size: 15px; line-height: 1.6;">
                {marketing_strategies[cluster].replace('<br>• ', '<br>• ')}
            </div>
        </div>
        """

    # 추천 모델 목록 추가
    if recommended_models:
        models_html = "<h3 style='margin-bottom: 15px; color: {}; font-size: 18px;'>추천 모델</h3><ul style='padding-left: 20px; margin-top: 0;'>".format(primary_color)
        models_html += "".join([f"<li style='margin-bottom: 8px;'>{model}</li>" for model in recommended_models])
        models_html += "</ul>"
        
        strategy_box_content += f"""
        <div style="margin: 25px 0 20px 0;">
            {models_html}
        </div>
        """

    # 메인 메시지 박스
    main_message_box = f"""
    <div style="background: #f8f9fa; padding: 25px; border-radius: 10px; margin-top: 20px; border: 1px solid #e0e0e0;">
        {strategy_box_content}
        
        <div style="font-size: 15px; line-height: 1.7; padding-top: 15px; border-top: 1px solid #e0e0e0; margin-top: 20px;">
            {message}
        </div>
    </div>
    """

    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 30px;">
        <table style="width: 100%; max-width: 800px; margin: auto; background: white; padding: 30px; 
                    border-radius: 15px; box-shadow: 0px 5px 15px rgba(0,0,0,0.1);">
            <!-- 헤더 영역 (로고) -->
            <tr>
                <td style="text-align: center; padding: 20px; background: {primary_color}; color: white; 
                        border-top-left-radius: 15px; border-top-right-radius: 15px;">
                    <h1 style="margin: 0;">🚗 {brand_name} 프로모션 🚗</h1>
                </td>
            </tr>
            
            <!-- 본문 내용 -->
            <tr>
                <td style="padding: 30px;">
                    <!-- 브랜드 로고 -->
                    <div style="text-align: center; margin-bottom: 25px;">
                        <a href="https://www.{'hyundai' if brand == '현대' else 'kia'}.com" target="_blank">
                        <img src="cid:{logo_cid}"
                            alt="{logo_alt}" style="width: 100%; max-width: 300px; border-radius: 8px;">
                        </a>
                    </div>

                    <p style="font-size: 18px; text-align: center; margin-bottom: 25px;">안녕하세요, <strong>{customer_name}</strong>님!</p>

                    {main_message_box}
                    
                    <div style="text-align: center; margin-top: 30px;">
                        <a href="https://www.{'hyundai' if brand == '현대' else 'kia'}.com" 
                            style="display: inline-block; background: {primary_color}; color: white; padding: 14px 28px; 
                                text-decoration: none; border-radius: 6px; font-size: 16px; font-weight: 600;">
                            지금 확인하기
                        </a>
                    </div>
                </td>
            </tr>

            <!-- 푸터 (고객센터 안내) -->
            <tr>
                <td style="padding: 20px 15px 15px 15px; font-size: 13px; text-align: center; color: #777; border-top: 1px solid #eee;">
                    ※ 본 메일은 자동 발송되었으며, 문의는 고객센터를 이용해주세요.
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    # HTML 본문 첨부
    msg.attach(MIMEText(html_body, 'html'))

    # 로고 이미지 첨부
    try:
        with open(logo_path, 'rb') as img_file:
            img_data = img_file.read()
            img = MIMEImage(img_data)
            img.add_header('Content-ID', f'<{logo_cid}>')
            img.add_header('Content-Disposition', 'inline', filename=os.path.basename(logo_path))
            msg.attach(img)
    except Exception as e:
        st.error(f"로고 이미지 첨부 실패: {str(e)}")
        # 이미지 첨부 실패 시 대체 텍스트 사용
        html_body = html_body.replace(f'src="cid:{logo_cid}"', f'alt="{logo_alt}" style="display:none;"')
        msg = MIMEMultipart()  # 기존 메시지 재생성
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = customer_email
        msg['Subject'] = f"{customer_name}님, 프로모션 안내" if prod else f"[테스트] {customer_name}님, 프로모션 안내"
        msg.attach(MIMEText(html_body, 'html'))

    server = smtplib.SMTP('smtp.gmail.com', 587)  # Gmail SMTP 서버 사용
    server.starttls()
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    text = msg.as_string()
    server.sendmail(EMAIL_ADDRESS, customer_email, text)
    server.quit()
# 10초마다 자동 새로고침 (10000 밀리초)
st_autorefresh(interval=10000, limit=None, key="fizzbuzz")

# 인포 메시지를 세밀하게 표시하는 함수
def custom_info(message, bg_color, text_color="black"):
    st.markdown(
        f'<div style="background-color: {bg_color}; color: {text_color}; padding: 10px; border-radius: 4px; margin-bottom: 10px;">{message}</div>',
        unsafe_allow_html=True
    )

# 기본 스타일 설정
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
    body {
        font-family: 'Roboto', sans-serif;
        background: linear-gradient(135deg, #f0f4f8, #e8f5e9);
        padding: 20px;
    }
    .css-18e3th9, .css-1d391kg { background: none; }
    .reportview-container .main {
        background-color: rgba(255,255,255,0.9);
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    }
    h1 {
        font-size: 2.5em;
        font-weight: 700;
        text-align: center;
        color: #2E86C1;
        margin-bottom: 10px;
    }
    h4 {
        text-align: center;
        color: #555;
        margin-bottom: 30px;
        font-size: 1.1em;
    }
    hr { border: 1px solid #bbb; margin: 20px 0; }
    .nav-link {
        transition: background-color 0.3s ease, transform 0.3s ease;
        border-radius: 10px;
    }
    .nav-link:hover {
        background-color: #AED6F1 !important;
        transform: scale(1.05);
    }
    .analysis-text {
        background-color: #ffffff;
        border-left: 4px solid #2E86C1;
        padding: 20px;
        margin: 30px 0;
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        font-size: 1.1em;
        color: #333;
        line-height: 1.5;
    }
    .analysis-text:hover { background-color: #f7f9fa; }
    .option-menu .nav-link-selected { background-color: #2E86C1; color: white; }
    </style>
    """,
    unsafe_allow_html=True
)

# 클러스터 색상 매핑
cluster_color_map = {
    1: "#A8E6CF",  # 연두색
    2: "#FFF9B0",  # 연노랑
    3: "#AECBFA",  # 연파랑
    4: "#FFD3B6",  # 연주황
    5: "#D5AAFF",  # 연보라
    6: "#FFB3BA",  # 연핑크
    7: "#B5EAD7",  # 민트
    8: "#E2F0CB",  # 연연두
}
today = datetime.date.today().strftime("%Y-%m-%d")

# 인사이트 자동 생성 함수
def generate_gender_insights(gender_pct):
    insights = ["**📊 성별 분포 인사이트**"]
    
    max_male = gender_pct['남'].idxmax()
    max_female = gender_pct['여'].idxmax()
    balanced_cluster = (gender_pct['남'] - gender_pct['여']).abs().idxmin()

    male_dominant = gender_pct[gender_pct['남'] >= 60].index.tolist()
    female_dominant = gender_pct[gender_pct['여'] >= 60].index.tolist()
    balanced = list(set(gender_pct.index) - set(male_dominant) - set(female_dominant))

    insights.append(f"- 가장 남성 비율 높은 클러스터: {max_male}번 ({gender_pct.loc[max_male, '남']:.1f}%)")
    insights.append(f"- 가장 여성 비율 높은 클러스터: {max_female}번 ({gender_pct.loc[max_female, '여']:.1f}%)")
    insights.append(f"- 가장 균형 잡힌 클러스터: {balanced_cluster}번 (남성 {gender_pct.loc[balanced_cluster, '남']:.1f}% / 여성 {gender_pct.loc[balanced_cluster, '여']:.1f}%)")

    marketing = ["**🎯 마케팅 제안**"]
    if male_dominant:
        marketing.append(f"- 클러스터 {', '.join(map(str, male_dominant))}: 남성 타겟 프로모션 (스포츠 모델, 기술 기능 강조)")
    if female_dominant:
        marketing.append(f"- 클러스터 {', '.join(map(str, female_dominant))}: 여성 타겟 캠페인 (안전 기능, 가족 친화적 메시지)")
    if balanced:
        marketing.append(f"- 클러스터 {', '.join(map(str, balanced))}: 일반적인 마케팅 접근 (다양한 옵션 제공)")

    return "\n".join(insights + [""] + marketing)

def generate_age_insights(age_stats):
    insights = ["**📊 연령 분포 인사이트**"]
    
    youngest = age_stats['평균 연령'].idxmin()
    oldest = age_stats['평균 연령'].idxmax()
    diverse = age_stats['표준편차'].idxmax()
    
    young_clusters = age_stats[age_stats['평균 연령'] < 40].index.tolist()
    old_clusters = age_stats[age_stats['평균 연령'] >= 40].index.tolist()
    diverse_clusters = age_stats.sort_values('표준편차', ascending=False).head(2).index.tolist()

    insights.append(f"- 가장 젊은 클러스터: {youngest}번 (평균 {age_stats.loc[youngest, '평균 연령']}세)")
    insights.append(f"- 가장 연장자 클러스터: {oldest}번 (평균 {age_stats.loc[oldest, '평균 연령']}세)")
    insights.append(f"- 가장 다양한 연령대: {diverse}번 (표준편차 {age_stats.loc[diverse, '표준편차']}세)")

    marketing = ["**🎯 마케팅 제안**"]
    if young_clusters:
        marketing.append(f"- 클러스터 {', '.join(map(str, young_clusters))}: SNS 마케팅, 트렌디한 디자인/기술 강조")
    if old_clusters:
        marketing.append(f"- 클러스터 {', '.join(map(str, old_clusters))}: 안전/편의 기능, 할인 혜택 강조")
    if diverse_clusters:
        marketing.append(f"- 클러스터 {', '.join(map(str, diverse_clusters))}: 다양한 연령층 호소 가능한 메시지")

    return "\n".join(insights + [""] + marketing)

def generate_transaction_insights(transaction_stats):
    insights = ["**📊 거래 금액 인사이트**"]
    
    high_value = transaction_stats['평균 거래액'].idxmax()
    low_value = transaction_stats['평균 거래액'].idxmin()
    total_sales = transaction_stats['총 거래액'].sum()
    
    high_value_clusters = transaction_stats[transaction_stats['평균 거래액'] >= transaction_stats['평균 거래액'].quantile(0.75)].index.tolist()
    low_value_clusters = transaction_stats[transaction_stats['평균 거래액'] <= transaction_stats['평균 거래액'].quantile(0.25)].index.tolist()

    insights.append(f"- 최고 평균 거래액 클러스터: {high_value}번 ({transaction_stats.loc[high_value, '평균 거래액']:,.0f}원)")
    insights.append(f"- 최저 평균 거래액 클러스터: {low_value}번 ({transaction_stats.loc[low_value, '평균 거래액']:,.0f}원)")
    insights.append(f"- 총 거래액 ({today} 기준): {total_sales:,.0f}원")

    marketing = ["**🎯 마케팅 제안**"]
    if high_value_clusters:
        marketing.append(f"- 클러스터 {', '.join(map(str, high_value_clusters))}: 프리미엄 모델 추천, VIP 서비스 제공")
    if low_value_clusters:
        marketing.append(f"- 클러스터 {', '.join(map(str, low_value_clusters))}: 할인 프로모션, 저비용 모델 추천")

    return "\n".join(insights + [""] + marketing)

def generate_frequency_insights(freq_stats):
    insights = ["**📊 구매 빈도 인사이트**"]
    
    frequent = freq_stats['평균 구매 빈도'].idxmax()
    rare = freq_stats['평균 구매 빈도'].idxmin()
    
    frequent_clusters = freq_stats[freq_stats['평균 구매 빈도'] >= freq_stats['평균 구매 빈도'].quantile(0.75)].index.tolist()
    rare_clusters = freq_stats[freq_stats['평균 구매 빈도'] <= freq_stats['평균 구매 빈도'].quantile(0.25)].index.tolist()

    insights.append(f"- 최고 구매 빈도 클러스터: {frequent}번 (평균 {freq_stats.loc[frequent, '평균 구매 빈도']:.2f}회)")
    insights.append(f"- 최저 구매 빈도 클러스터: {rare}번 (평균 {freq_stats.loc[rare, '평균 구매 빈도']:.2f}회)")

    marketing = ["**🎯 마케팅 제안**"]
    if frequent_clusters:
        marketing.append(f"- 클러스터 {', '.join(map(str, frequent_clusters))}: 충성도 프로그램, 정기 구매 혜택")
    if rare_clusters:
        marketing.append(f"- 클러스터 {', '.join(map(str, rare_clusters))}: 재구매 유도 프로모션, 첫 구매 할인")

    return "\n".join(insights + [""] + marketing)

def generate_model_insights(model_cluster, selected_model):
    insights = [f"**📊 {selected_model} 모델 인사이트**"]
    
    main_cluster = model_cluster.idxmax()
    main_ratio = (model_cluster[main_cluster] / model_cluster.sum()) * 100
    
    top_clusters = model_cluster.nlargest(2).index.tolist()  # 상위 2개 클러스터
    other_clusters = list(set(model_cluster.index) - set(top_clusters))

    insights.append(f"- 주 구매 클러스터: {main_cluster}번 ({main_ratio:.1f}%)")
    insights.append(f"- 총 판매량: {model_cluster.sum()}대")

    marketing = ["**🎯 마케팅 제안**"]
    if top_clusters:
        marketing.append(f"- 클러스터 {', '.join(map(str, top_clusters))}: 해당 클러스터 특성에 맞는 맞춤형 프로모션")
    if other_clusters:
        marketing.append(f"- 클러스터 {', '.join(map(str, other_clusters))}: 판매 확장을 위한 타겟 마케팅 테스트")

    return "\n".join(insights + [""] + marketing)

def run_eda():
    brand = st.session_state.get("brand", "현대")
    country = st.session_state.get("country", "")

    # 분석 종류 선택 메뉴
    selected_analysis = option_menu(
        menu_title=None,
        options=[
            "👥 클러스터별 성별 분포",
            "👵 클러스터별 연령 분포",
            "💰 클러스터별 거래 금액",
            "🛒 클러스터별 구매 빈도",
            "🚘 모델별 구매 분석",
            "📝 종합 보고서 및 이메일 발송"
        ],
        icons=["", "", "", ""],
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

    csv_path = f"data/{brand}_고객데이터_신규입력용.csv"
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        country_df = df[df['국가'] == country].copy()
        country_df['Cluster_Display'] = country_df['Cluster'] + 1
        country_df.rename(columns={"Cluster_Display": "고객유형"}, inplace=True)
        
        if selected_analysis == "👥 클러스터별 성별 분포":
            st.subheader(f"{country} - 클러스터별 성별 분포")
            
            if {'Cluster', '성별'}.issubset(country_df.columns):
                # 성별 분포 계산
                gender_dist = country_df.groupby(['고객유형', '성별']).size().unstack(fill_value=0)
                gender_pct = gender_dist.div(gender_dist.sum(axis=1), axis=0) * 100
                
                # 바 차트
                bar_fig = px.bar(
                    gender_dist, barmode='group',
                    title=f'{country} 클러스터별 성별 분포',
                    labels={'value': '고객 수', '고객유형': '클러스터'},
                    color_discrete_map={'남': '#3498db', '여': '#e74c3c'}
                )
                st.plotly_chart(bar_fig)
                
                # 비율 표시
                st.subheader("클러스터별 성별 비율 (%)")
                st.dataframe(gender_pct.style.format("{:.1f}%").background_gradient(cmap='Blues'))
                
                # 인사이트 제공
                st.markdown(generate_gender_insights(gender_pct))
                
            else:
                st.error("필요한 컬럼이 데이터에 없습니다.")

        elif selected_analysis == "👵 클러스터별 연령 분포":
            st.subheader(f"{country} - 클러스터별 연령 분포 분석")
            
            if {'Cluster', '연령'}.issubset(country_df.columns):
                # 박스플롯
                box_fig = px.box(
                    country_df, x='고객유형', y='연령',
                    title=f'{country} 클러스터별 연령 분포',
                    color='고객유형'
                )
                st.plotly_chart(box_fig)
                
                # 히스토그램
                hist_fig = px.histogram(
                    country_df, x='연령', color='고객유형',
                    nbins=20, barmode='overlay', opacity=0.7,
                    title=f'{country} 클러스터별 연령 분포 히스토그램'
                )
                st.plotly_chart(hist_fig)
                
                # 연령 통계
                age_stats = country_df.groupby('고객유형')['연령'].agg(['mean', 'median', 'std']).round(1)
                age_stats.columns = ['평균 연령', '중앙값', '표준편차']
                
                st.subheader("클러스터별 연령 통계")
                st.dataframe(age_stats.style.format({
                    '평균 연령': '{:.1f}세',
                    '중앙값': '{:.1f}세',
                    '표준편차': '{:.1f}세'
                }).background_gradient(cmap='Blues'))
                
                # 인사이트 제공
                st.markdown(generate_age_insights(age_stats))
                
            else:
                st.error("필요한 컬럼이 데이터에 없습니다.")

        elif selected_analysis == "💰 클러스터별 거래 금액":
            st.subheader(f"{country} - 클러스터별 거래 금액 분석")
            
            if {'Cluster', '거래 금액'}.issubset(country_df.columns):
                # 박스플롯
                box_fig = px.box(
                    country_df, x='고객유형', y='거래 금액',
                    title=f'{country} 클러스터별 거래 금액 분포',
                    color='고객유형'
                )
                st.plotly_chart(box_fig)
                
                # 거래 금액 통계
                transaction_stats = country_df.groupby('고객유형')['거래 금액'].agg(['mean', 'median', 'sum']).round()
                transaction_stats.rename(columns={'mean': '평균 거래액', 'median': '중앙값', 'sum': '총 거래액'}, inplace=True)
                transaction_stats.columns = ['평균 거래액', '중앙값', '총 거래액']
                
                st.subheader("클러스터별 거래 금액 통계")
                st.dataframe(transaction_stats.style.format({
                    '평균 거래액': '{:,.0f}원',
                    '중앙값': '{:,.0f}원',
                    '총 거래액': '{:,.0f}원'
                }).background_gradient(cmap='Blues'))
                
                # 인사이트 제공
                st.markdown(generate_transaction_insights(transaction_stats))
                
            else:
                st.error("필요한 컬럼이 데이터에 없습니다.")

        elif selected_analysis == "🛒 클러스터별 구매 빈도":
            st.subheader(f"{country} - 클러스터별 구매 빈도 분석")
            
            if {'Cluster', '제품구매빈도'}.issubset(country_df.columns):
                # 박스플롯
                box_fig = px.box(
                    country_df, x='고객유형', y='제품구매빈도',
                    title=f'{country} 클러스터별 구매 빈도 분포',
                    color='고객유형'
                )
                st.plotly_chart(box_fig)
                
                # 구매 빈도 통계
                freq_stats = country_df.groupby('고객유형')['제품구매빈도'].agg(['mean', 'median']).round(2)
                freq_stats.columns = ['평균 구매 빈도', '중앙값']
                
                st.subheader("클러스터별 구매 빈도 통계")
                st.dataframe(freq_stats.style.format({
                    '평균 구매 빈도': '{:.2f}회',
                    '중앙값': '{:.2f}회'
                }).background_gradient(cmap='Blues'))
                
                # 인사이트 제공
                st.markdown(generate_frequency_insights(freq_stats))
                
            else:
                st.error("필요한 컬럼이 데이터에 없습니다.")

        elif selected_analysis == "🚘 모델별 구매 분석":
            st.subheader(f"{country} - 모델별 구매 분석")
            
            if {'구매한 제품', 'Cluster'}.issubset(country_df.columns):
                # 모델별 판매량
                model_sales = country_df['구매한 제품'].value_counts().reset_index().head(10)
                model_sales.columns = ['모델', '판매량']
                
                # 바 차트
                bar_fig = px.bar(
                    model_sales, x='모델', y='판매량',
                    title=f'{country} 모델별 Top10 판매량',
                    color='모델',
                    color_discrete_sequence=px.colors.sequential.Sunset
                )
                st.plotly_chart(bar_fig)
                
                # 모델 선택
                selected_model = st.selectbox(
                    "모델 선택",
                    country_df['구매한 제품'].unique(),
                    key='model_select'
                )
                
                # 선택 모델의 클러스터 분포
                model_cluster = country_df[country_df['구매한 제품'] == selected_model]['고객유형'].value_counts()
                
                # 파이 차트
                pie_fig = px.pie(
                    model_cluster, names=model_cluster.index, values=model_cluster.values,
                    title=f'{selected_model} 모델 구매 고객의 클러스터 분포',
                    color_discrete_sequence=px.colors.sequential.Sunset
                )
                st.plotly_chart(pie_fig)
                
                # 클러스터 분포 표시
                st.subheader(f"{selected_model} 모델 구매 고객 클러스터 분포")
                st.dataframe(model_cluster.to_frame('고객 수').style.format({"고객 수": "{:,}명"}))
                
                # 인사이트 제공
                st.markdown(generate_model_insights(model_cluster, selected_model))
                
            else:
                st.error("필요한 컬럼이 데이터에 없습니다.")
                
        elif selected_analysis == "📝 종합 보고서 및 이메일 발송":
            st.subheader(f"{country} - 종합 분석 보고서 및 클러스터별 마케팅 이메일 발송")
            marketing_strategies, brand_recommendations = generate_marketing_strategies(country_df)

            # 개발자 모드 상태 표시
            if not prod:
                st.warning(f"⚠️ 개발자 모드 활성화 (모든 이메일은 {prod_email}로 발송됩니다)")
            else:
                st.success("✅ 운영 모드 (실제 고객에게 이메일 발송)")
            
            # 종합 분석 보고서 생성
            st.markdown("### 📊 종합 분석 보고서")
            
            # 1. 기본 통계
            st.markdown("#### 1. 기본 통계")
            total_customers = len(country_df)
            clusters = country_df['고객유형'].nunique()
            avg_age = country_df['연령'].mean()
            avg_transaction = country_df['거래 금액'].mean()
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("총 고객 수", f"{total_customers:,}명")
            col2.metric("클러스터 수", clusters)
            col3.metric("평균 연령", f"{avg_age:.1f}세")
            col4.metric("평균 거래액", f"{avg_transaction:,.0f}원")
            
            # 2. 클러스터별 주요 특성 요약
            st.markdown("#### 2. 클러스터별 주요 특성")
            
            # 성별 분포
            gender_dist = country_df.groupby(['고객유형', '성별']).size().unstack(fill_value=0)
            gender_pct = gender_dist.div(gender_dist.sum(axis=1), axis=0) * 100
            
            # 연령 통계
            age_stats = country_df.groupby('고객유형')['연령'].agg(['mean', 'std']).round(1)
            age_stats.columns = ['평균 연령', '표준편차']
            
            # 거래 금액 통계
            transaction_stats = country_df.groupby('고객유형')['거래 금액'].agg(['mean', 'sum']).round()
            transaction_stats.columns = ['평균 거래액', '총 거래액']
            
            # 구매 빈도 통계
            freq_stats = country_df.groupby('고객유형')['제품구매빈도'].mean().round(2)
            
            # 모든 통계를 하나의 데이터프레임으로 결합
            summary_df = pd.concat([
                gender_pct,
                age_stats,
                transaction_stats,
                freq_stats.rename('평균 구매 빈도')
            ], axis=1)
            
            st.dataframe(summary_df.style.format({
                '남': '{:.1f}%',
                '여': '{:.1f}%',
                '평균 연령': '{:.1f}세',
                '표준편차': '{:.1f}세',
                '평균 거래액': '{:,.0f}원',
                '총 거래액': '{:,.0f}원',
                '평균 구매 빈도': '{:.2f}회'
            }).background_gradient(cmap='Blues'))
            
            # 3. 마케팅 전략 제안
            st.markdown("#### 3. 클러스터별 마케팅 전략 제안")
            marketing_strategies, brand_recommendations = generate_marketing_strategies(country_df)

            # 클러스터별 카드 생성
            clusters = sorted(marketing_strategies.keys())
            cols_per_row = 2  # 한 행에 표시할 카드 수

            for i in range(0, len(clusters), cols_per_row):
                cols = st.columns(cols_per_row)
                for j in range(cols_per_row):
                    if i + j < len(clusters):
                        cluster = clusters[i + j]
                        with cols[j]:
                            # 카드 스타일 적용
                            st.markdown(
                                f"""
                                <div style="
                                    padding: 15px;
                                    border-radius: 10px;
                                    border: 1px solid #e0e0e0;
                                    background-color: #ffffff;
                                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                                    margin-bottom: 20px;
                                ">
                                    <h4 style="
                                        color: #2E86C1;
                                        margin-top: 0;
                                        border-bottom: 2px solid #f0f0f0;
                                        padding-bottom: 8px;
                                    ">클러스터 {cluster}</h4>
                                    <div style="
                                        font-size: 0.95em;
                                        line-height: 1.6;
                                        color: #333;
                                    ">
                                        {marketing_strategies[cluster]}
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
            
            # 4. 이메일 발송 기능
            st.markdown("---")
            st.markdown("### ✉️ 클러스터별 타겟 이메일 발송")
            
            # 클러스터 선택
            selected_cluster = st.selectbox(
                "클러스터 선택",
                sorted(country_df['고객유형'].unique()),
                key='email_cluster'
            )
            
            # 해당 클러스터 고객 필터링
            cluster_customers = country_df[country_df['고객유형'] == selected_cluster]
            
            # 이메일 내용 작성
            st.markdown("#### 이메일 내용 작성")
            
            # 기본 메시지 템플릿
            template = f"""
            <p>{brand}자동차의 특별한 프로모션 소식을 전해드립니다!</p>
            
            <p>요즘 차량 구입 고민이 많으시죠? 고객님께 꼭 맞는 특별 혜택을 안내드립니다.:</p>
            
            <ul>
                • {marketing_strategies[selected_cluster]}
                <br>• 한정 기간 할인 프로모션
            </ul>
            
            <p>자세한 내용은 아래 링크를 확인해주세요. 감사합니다!</p>
            """
            
            email_subject = st.text_input(
                "이메일 제목",
                f"[{brand}자동차] 고객님을 위한 맞춤 특별 혜택!",
                key='email_subject'
            )
            
            email_content = st.text_area(
                "이메일 내용 (HTML 형식)",
                template,
                height=300,
                key='email_content'
            )
            
            # 미리보기
            if st.checkbox("이메일 미리보기"):
                st.markdown("### 이메일 미리보기")
                st.markdown(f"**제목**: {email_subject}")
                st.markdown(email_content, unsafe_allow_html=True)
            
            # 발송 대상 확인
            st.markdown("#### 발송 대상 고객")
            
            # 개발자 모드인 경우 이메일 주소를 개발자 이메일로 표시
            if not prod:
                display_data = cluster_customers[['이름', '성별', '연령', '거래 금액','구매한 제품']].copy()
                display_data['이메일'] = prod_email  # 개발자 이메일로 표시
                display_data = display_data[['이름', '이메일', '성별', '연령', '거래 금액','구매한 제품']]
                st.warning(f"개발자 모드: 실제 고객 대신 {prod_email}로 발송됩니다")
            else:
                display_data = cluster_customers[['이름', '이메일', '성별', '연령', '거래 금액','구매한 제품']]
            
            # 페이지네이션 설정
            # 페이지네이션 설정
            if 'page' not in st.session_state:
                st.session_state.page = 1

            page_size = 7
            total_pages = max(1, (len(display_data) - 1)) // page_size + 1

            # 컬럼 레이아웃 설정 (6:4 비율로 좌우 분할)
            col_left, col_right = st.columns([6, 4])

            with col_left:
                # 왼쪽 컬럼: 고객 데이터 프레임 + 페이지네이션
                st.markdown("#### 발송 대상 고객 리스트")
                
                # 페이지네이션 컨트롤
                pagination_col1, pagination_col2, pagination_col3 = st.columns([1, 2, 1])
                with pagination_col1:
                    if st.button('◀ 이전', disabled=(st.session_state.page <= 1), key='prev_page'):
                        st.session_state.page -= 1
                        st.rerun()
                with pagination_col2:
                    st.markdown(f"<div style='text-align: center;'>페이지 {st.session_state.page} / {total_pages}</div>", unsafe_allow_html=True)
                with pagination_col3:
                    if st.button('다음 ▶', disabled=(st.session_state.page >= total_pages), key='next_page'):
                        st.session_state.page += 1
                        st.rerun()
                
                # 데이터 표시
                start_idx = (st.session_state.page - 1) * page_size
                end_idx = min(start_idx + page_size, len(display_data))
                st.dataframe(display_data.iloc[start_idx:end_idx], height=300)
                st.caption(f"총 {len(cluster_customers)}명의 고객에게 발송됩니다." + 
                        (" (개발자 모드 - 실제 발송되지 않음)" if not prod else ""))

            with col_right:
                # 오른쪽 컬럼: 클러스터 추천 모델
                st.markdown("#### 클러스터 추천 모델")
                
                brand = st.session_state.get("brand", "현대")
                cluster_key = selected_cluster - 1 if brand == "현대" else selected_cluster
                
                if brand in brand_recommendations and cluster_key in brand_recommendations[brand]:
                    recommended_models = brand_recommendations[brand][cluster_key][:3]  # 최대 3개만 표시
                    
                    # 카드 형태로 추천 모델 표시
                    for i, model in enumerate(recommended_models, 1):
                        with st.expander(f"추천 모델 {i}: {model}", expanded=True):
                            # vehicle_recommendations에서 추천 이유 가져오기
                            recommendation_text = ""
                            
                            # 클러스터 키 조정 (현대: 1-8 → 0-7, 기아: 0-5 유지)
                            cluster_key_for_rec = selected_cluster - 1 if brand == "현대" else selected_cluster
                            
                            # 추천 이유 조회
                            if (brand in vehicle_recommendations and 
                                model in vehicle_recommendations[brand] and 
                                cluster_key_for_rec in vehicle_recommendations[brand][model]):
                                
                                # 줄바꿈 문자를 <br> 태그로 미리 변환
                                recommendation_text = vehicle_recommendations[brand][model][cluster_key_for_rec].replace('\n', '<br>')
                                
                            else:
                                # 추천 이유가 없는 경우 기본 문구
                                recommendation_text = f"{model} 모델은 {brand} {selected_cluster}번 클러스터 고객님들께 추천드립니다."
                            
                            # HTML로 표시 (이제 f-string 내에 백슬래시 없음)
                            st.markdown(f"""
                            <div style="padding: 10px; border-radius: 8px; background-color: #f8f9fa; margin-bottom: 10px;">
                                <p style="font-weight: bold; margin-bottom: 5px; color: #2E86C1; font-size: 1.1em;">{model}</p>
                                <div style="font-size: 0.9em; color: #555; line-height: 1.6;">
                                    {recommendation_text}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # 추가로 현재 클러스터에서 실제로 많이 팔린 모델도 함께 표시 (옵션)
                    if '구매한 제품' in country_df.columns:
                        st.markdown("---")
                        st.markdown("##### 이 클러스터의 실제 판매 모델 (Top 3)")
                        top_sold_models = country_df[country_df['고객유형'] == selected_cluster]['구매한 제품'].value_counts().head(3)
                        if not top_sold_models.empty:
                            st.dataframe(
                                top_sold_models.reset_index().rename(
                                    columns={'구매한 제품': '모델명', 'count': '판매량'}
                                ),
                                hide_index=True
                            )
                else:
                    st.warning(f"이 클러스터({selected_cluster})에 대한 추천 모델 데이터가 없습니다.")
            
            # 이메일 발송 버튼
            if st.button("이메일 발송", 
                        key="send_email_button",
                        help="클릭하면 선택한 클러스터 고객에게 이메일을 발송합니다",
                        # 버튼 스타일 적용
                        use_container_width=True,  # 컨테이너 너비에 맞춤
                        type="primary"):  # 주요 버튼 스타일 적용
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                success_count = 0
                fail_count = 0
                
                for i, (_, row) in enumerate(cluster_customers.iterrows()):
                    try:
                        send_email(
                            customer_name=row['이름'],
                            customer_email=row['이메일'],
                            message=email_content,
                            cluster=selected_cluster,
                            marketing_strategies=marketing_strategies,
                            brand_recommendations=brand_recommendations,  # 추가된 인자
                            purchased_model=row['구매한 제품']  # 추가된 인자
                        )
                        success_count += 1
                        
                        # 개발자 모드 알림
                        if not prod:
                            st.info(f"개발자 모드: {row['이름']} 고객 대신 {prod_email}로 테스트 이메일 발송됨")
                            
                    except Exception as e:
                        st.error(f"{row['이름']} 고객에게 이메일 발송 실패: {str(e)}")
                        fail_count += 1
                    
                    progress = (i + 1) / len(cluster_customers)
                    progress_bar.progress(progress)
                    status_text.text(f"진행 중: {i + 1}/{len(cluster_customers)} (성공: {success_count}, 실패: {fail_count})")
                
                progress_bar.empty()
                if fail_count == 0:
                    st.success(f"모든 이메일({success_count}건)이 성공적으로 발송되었습니다!")
                    if not prod:
                        st.warning("개발자 모드 활성화 상태 - 실제 고객 대신 개발자 이메일로 발송되었습니다")
                else:
                    st.warning(f"이메일 발송 완료 (성공: {success_count}건, 실패: {fail_count}건)")
                    
        else:
            st.error(f"CSV 파일을 찾을 수 없습니다: {csv_path}")