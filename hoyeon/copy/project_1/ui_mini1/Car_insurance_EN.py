import streamlit as st
import pandas as pd
import joblib
from datetime import datetime
from pathlib import Path

# 보험사 및 모델 데이터 정의
launch_dates = {
    '현대': {
        'G70 (IK)': '2017-09',
        'NEXO (FE)': '2018-01',
        'Avante (CN7 N)': '2020-05',
        'G80 (RG3)': '2020-03',
        'Grandeur (GN7 HEV)': '2022-01',
        'Tucson (NX4 PHEV)': '2021-05',
        'Avante (CN7 HEV)': '2020-07',
        'IONIQ 6 (CE)': '2022-06',
        'G90 (HI)': '2022-03',
        'Santa-Fe (MX5 PHEV)': '2022-06'
    }
}

eco_friendly_models = {
    '현대': [
        'NEXO (FE)', 'Avante (CN7 HEV)', 'Grandeur (GN7 HEV)', 
        'Tucson (NX4 PHEV)', 'IONIQ 6 (CE)', 'Santa-Fe (MX5 PHEV)'
    ]
}

# 클러스터별 보험사 추천 (State Farm + 1개 보험사)
insurance_recommendations = {
    0: ["State Farm", "Geico"],
    1: ["State Farm", "Progressive"],
    2: ["State Farm", "Allstate"],
    3: ["State Farm", "USAA"],
    4: ["State Farm", "Liberty Mutual"],
    5: ["State Farm", "Farmers Insurance"]
}

# 보험사 상세 정보 (미국 시장에 맞게 수정)
insurance_companies = {
    "State Farm": {
        "logo": "hoyeon/hun_bo.png",
        "description": "America's largest auto insurer with nationwide coverage and reliable service",
        "strengths": ["Nationwide agent network", "Multiple discount programs", "24/7 customer service"],
        "contact": "1-800-STATE-FARM",
        "discounts": {
            "친환경차": 0.15,
            "무사고": 0.1,
            "신차": 0.05
        },
        "coverage_details": {
            "Basic Coverage": ["Bodily injury: $300,000 per accident", "Property damage: $100,000", "Personal injury: $50,000"],
            "Special Coverage": ["Comprehensive collision", "Emergency roadside assistance", "Rental car reimbursement"],
            "Discounts": ["Multi-policy discount", "Safe driver discount", "New car discount"]
        }
    },
    "Geico": {
        "logo": "hoyeon/sam_bo.png",
        "description": "Known for affordable rates with quick quotes and convenient digital services",
        "strengths": ["Competitive pricing", "User-friendly mobile app", "Fast claims processing"],
        "contact": "1-800-947-AUTO",
        "discounts": {
            "친환경차": 0.1,
            "무사고": 0.15,
            "신차": 0.03
        },
        "coverage_details": {
            "Basic Coverage": ["Bodily injury: $250,000 per accident", "Property damage: $50,000", "Personal injury: $25,000"],
            "Special Coverage": ["Mechanical breakdown insurance", "Emergency road service", "Rideshare coverage"],
            "Discounts": ["Multi-vehicle discount", "Good student discount", "Military discount"]
        }
    },
    "Progressive": {
        "logo": "hoyeon/kb_bo.png",
        "description": "Innovative insurer offering Name Your Price® tool and usage-based options",
        "strengths": ["Customizable rates", "Snapshot driving program", "Online discounts"],
        "contact": "1-800-PROGRESSIVE",
        "discounts": {
            "친환경차": 0.12,
            "무사고": 0.12,
            "신차": 0.04
        },
        "coverage_details": {
            "Basic Coverage": ["Bodily injury: $300,000 per accident", "Property damage: $100,000", "Personal injury: $50,000"],
            "Special Coverage": ["Loan/lease payoff", "Custom parts/equipment", "Pet injury coverage"],
            "Discounts": ["Multi-policy discount", "Continuous insurance discount", "Online quote discount"]
        }
    },
    "Allstate": {
        "logo": "hoyeon/db_bo.png",
        "description": "Rewards safe drivers with Drivewise program and accident forgiveness",
        "strengths": ["Safe driving incentives", "Excellent customer service", "Comprehensive coverage options"],
        "contact": "1-800-ALLSTATE",
        "discounts": {
            "친환경차": 0.13,
            "무사고": 0.13,
            "신차": 0.05
        },
        "coverage_details": {
            "Basic Coverage": ["Bodily injury: $250,000 per accident", "Property damage: $50,000", "Personal injury: $25,000"],
            "Special Coverage": ["New car replacement", "Accident forgiveness", "Rental reimbursement"],
            "Discounts": ["Early signing discount", "Esmart discount", "Responsible payer discount"]
        }
    },
    "USAA": {
        "logo": "hoyeon/han_bo.png",
        "description": "Exclusive coverage for military members with exceptional satisfaction ratings",
        "strengths": ["Military-only discounts", "Superior claims service", "Competitive rates"],
        "contact": "1-800-531-USAA",
        "discounts": {
            "친환경차": 0.1,
            "무사고": 0.1,
            "신차": 0.05
        },
        "coverage_details": {
            "Basic Coverage": ["Bodily injury: $300,000 per accident", "Property damage: $100,000", "Personal injury: $50,000"],
            "Special Coverage": ["Deployment discounts", "Military vehicle coverage", "Overseas coverage"],
            "Discounts": ["Garaging discount", "Family discount", "Length of membership discount"]
        }
    },
    "Liberty Mutual": {
        "logo": "hoyeon/mer_bo.png",
        "description": "Offers customized coverage options and accident forgiveness",
        "strengths": ["Better car replacement", "Diverse discount options", "New car replacement"],
        "contact": "1-800-290-7933",
        "discounts": {
            "친환경차": 0.15,
            "무사고": 0.15,
            "신차": 0.07
        },
        "coverage_details": {
            "Basic Coverage": ["Bodily injury: $250,000 per accident", "Property damage: $50,000", "Personal injury: $25,000"],
            "Special Coverage": ["Rideshare coverage", "New car replacement", "Accident forgiveness"],
            "Discounts": ["Multi-policy discount", "Safe driver discount", "Online purchase discount"]
        }
    },
    "Farmers Insurance": {
        "logo": "hoyeon/lot_bo.png",
        "description": "Agent-focused service with diverse coverage options and accident forgiveness",
        "strengths": ["Local agent support", "Accident forgiveness", "New car replacement"],
        "contact": "1-888-327-6335",
        "discounts": {
            "친환경차": 0.1,
            "무사고": 0.1,
            "신차": 0.05
        },
        "coverage_details": {
            "Basic Coverage": ["Bodily injury: $250,000 per accident", "Property damage: $50,000", "Personal injury: $25,000"],
            "Special Coverage": ["Rideshare coverage", "Sound system coverage", "Personal umbrella policy"],
            "Discounts": ["Multi-car discount", "Pay-in-full discount", "Good student discount"]
        }
    }
}

# 보험 유형 상세 정보 (미국 달러 기준으로 수정)
insurance_type_details = {
    "Eco-Friendly Special": {
        "description": "Specialized coverage for hybrid/electric vehicles with battery and charging protection",
        "price_range": "$150-$250/month",
        "base_price": 200,
        "coverages": {
            "Required Coverage": [
                "Bodily injury: $300,000 per accident",
                "Property damage: $100,000",
                "Personal injury: $50,000"
            ],
            "Eco-Specific Coverage": [
                "High-voltage battery damage protection",
                "Charging equipment coverage",
                "EV-specific part replacement",
                "Emergency charging service"
            ],
            "Additional Services": [
                "EV-certified repair shops",
                "Battery performance guarantee",
                "Green driving rewards"
            ]
        }
    },
    "Premium Coverage": {
        "description": "Comprehensive protection package for luxury vehicles and premium customers",
        "price_range": "$200-$300/month",
        "base_price": 250,
        "coverages": {
            "Required Coverage": [
                "Bodily injury: $500,000 per accident",
                "Property damage: $250,000",
                "Personal injury: $100,000"
            ],
            "Premium Benefits": [
                "Full collision coverage",
                "OEM parts guarantee",
                "VIP roadside assistance",
                "Nationwide concierge service"
            ],
            "Value-Added Services": [
                "Dedicated claims specialist",
                "Rental car upgrades",
                "International coverage"
            ]
        }
    },
    "Standard Coverage": {
        "description": "Basic protection suitable for most vehicles at affordable rates",
        "price_range": "$100-$200/month",
        "base_price": 150,
        "coverages": {
            "Required Coverage": [
                "Bodily injury: $250,000 per accident",
                "Property damage: $50,000",
                "Personal injury: $25,000"
            ],
            "Basic Protection": [
                "Comprehensive coverage",
                "Deductible waiver",
                "Basic roadside assistance"
            ],
            "Optional Add-ons": [
                "Custom equipment coverage",
                "Medical payments",
                "Legal assistance"
            ]
        }
    }
}

def load_css():
    st.markdown("""
    <style>
        .main {
            background-color: #f8f9fa;
        }
        .stButton>button {
            background-color: #0d6efd;
            color: white;
            border-radius: 5px;
            padding: 0.5rem 1rem;
            border: none;
        }
        .stButton>button:hover {
            background-color: #0b5ed7;
            color: white;
        }
        .header {
            color: #0d6efd;
            padding: 1rem 0;
        }
        .highlight {
            background-color: #e7f1ff;
            padding: 0.5rem;
            border-radius: 5px;
            margin: 0.5rem 0;
        }
        .insurance-card {
            transition: transform 0.3s;
            height: 100%;
            padding: 1rem;
            border: 1px solid #dee2e6;
            border-radius: 10px;
            margin-bottom: 1rem;
        }
        .insurance-card:hover {
            transform: scale(1.02);
            box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
        }
        .eco-badge {
            background-color: #198754;
            color: white;
            padding: 0.25rem 0.5rem;
            border-radius: 20px;
            font-size: 0.8rem;
            display: inline-block;
            margin-left: 0.5rem;
        }
        .premium-badge {
            background-color: #6f42c1;
            color: white;
            padding: 0.25rem 0.5rem;
            border-radius: 20px;
            font-size: 0.8rem;
            display: inline-block;
            margin-left: 0.5rem;
        }
        .company-logo {
            max-height: 60px;
            margin-bottom: 1rem;
        }
        .coverage-item {
            padding: 0.5rem;
            margin: 0.25rem 0;
            border-left: 3px solid #0d6efd;
            background-color: #f8f9fa;
        }
        .coverage-category {
            font-weight: bold;
            color: #0d6efd;
            margin-top: 1rem;
        }
        .tab-content {
            padding: 1rem;
            border: 1px solid #dee2e6;
            border-top: none;
            border-radius: 0 0 10px 10px;
        }
    </style>
    """, unsafe_allow_html=True)

def load_models():
    """모델 로드 함수"""
    model_dir = Path(__file__).parent.parent / "models_mini1"
    segment_model_path = model_dir / "gb_model_hs.pkl"
    clustering_model_path = model_dir / "gb_pipeline_hc.pkl"

    if not segment_model_path.exists() or not clustering_model_path.exists():
        st.error("모델 파일을 찾을 수 없습니다.")
        st.stop()

    return joblib.load(segment_model_path), joblib.load(clustering_model_path)

def input_customer_info():
    """고객 정보 입력 폼"""
    st.title("📋 Hyundai Customer Information")
    
    segment_model, clustering_model = load_models()
    
    with st.form(key="customer_form"):
        # Section 1: Basic Information
        st.subheader("1. Basic Information")
        col1, col2 = st.columns(2)
        
        with col1:
            gender = st.selectbox("Gender", ["Male", "Female"], key="gender")
            birth_date = st.date_input("Date of Birth", 
                                    min_value=datetime(1900, 1, 1), 
                                    max_value=datetime.today().replace(year=datetime.today().year - 20),
                                    key="birth_date")
        
        with col2:
            car_type = st.selectbox("Vehicle Type", ["Compact Sedan", "Midsize Sedan", "Full-size Sedan", "SUV"], key="car_type")
            selected_vehicle = st.selectbox("Model Selection", list(launch_dates['현대'].keys()), key="car_model")
    
        # Section 2: Purchase Information
        st.subheader("2. Purchase Information")
        col1, col2 = st.columns(2)
        
        with col1:
            transaction_amount = st.number_input("Budget ($)", min_value=10000, step=1000, format="%d", key="budget")
            purchase_frequency = st.number_input("Purchase Frequency", min_value=1, value=1, key="purchase_freq")
        
        with col2:
            transaction_method = st.selectbox("Payment Method", ["Credit Card", "Cash", "Bank Transfer"], key="payment_method")
            purchase_date = st.date_input("Purchase Date", key="purchase_date")
    
        # Section 3: Insurance Information
        st.subheader("3. Insurance Information")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            driving_exp = st.selectbox("Driving Experience", ["Under 1 year", "1-3 years", "3-5 years", "5+ years"], key="driving_exp_select")
        
        with col2:
            accident_history = st.selectbox("Accident History (3 years)", ["No accidents", "1 accident", "2 accidents", "3+ accidents"], key="accident_history_select")
        
        with col3:
            car_age = st.selectbox("Vehicle Age", ["New car", "1-3 years", "3-5 years", "5-7 years", "7+ years"], key="car_age_select")
        
        # Submit Button
        submitted = st.form_submit_button("Get Insurance Recommendations", use_container_width=True)
        
        if submitted:
            # Age Calculation
            today = datetime.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            
            # Segment Prediction
            segment_input = pd.DataFrame([[transaction_method, launch_dates['현대'].get(selected_vehicle), 
                                        purchase_date, transaction_amount, purchase_frequency]],
                                      columns=['거래 방식', '제품 출시년월', '제품 구매 날짜', 
                                              '거래 금액', '제품 구매 빈도'])
            customer_segment = segment_model.predict(segment_input)[0]
            
            # Clustering Prediction
            cluster_input = pd.DataFrame([[gender, car_type, transaction_method, 
                                         launch_dates['현대'].get(selected_vehicle),
                                         purchase_date, customer_segment,
                                         "Yes" if selected_vehicle in eco_friendly_models['현대'] else "No",
                                         age, transaction_amount, purchase_frequency]],
                                       columns=['성별', '차량구분', '거래 방식', '제품 출시년월',
                                               '제품 구매 날짜', '고객 세그먼트', '친환경차',
                                               '연령', '거래 금액', '제품 구매 빈도'])
            cluster_id = clustering_model.predict(cluster_input)[0]
            
            # Save session state
            st.session_state.update({
                "step": 2,
                "cluster_id": cluster_id,
                "selected_vehicle": selected_vehicle,
                "driving_exp_session": driving_exp,
                "accident_history_session": accident_history,
                "car_age_session": car_age,
                "gender_session": gender,
                "birth_date_session": birth_date,
                "transaction_amount_session": transaction_amount,
                "purchase_frequency_session": purchase_frequency,
                "car_type_session": car_type,
                "transaction_method_session": transaction_method,
                "purchase_date_session": purchase_date,
                "age_session": age,
                "is_eco_friendly": selected_vehicle in eco_friendly_models['현대']
            })
            
            st.rerun()

def Car_insurance_recommendation():
    """보험 추천 정보 표시"""
    st.title("🚗 Personalized Hyundai Auto Insurance")
    
    # Get customer info from session
    cluster_id = st.session_state.get("cluster_id", 0)
    selected_vehicle = st.session_state.get("selected_vehicle", "")
    is_eco_friendly = st.session_state.get("is_eco_friendly", False)
    driving_exp = st.session_state.get("driving_exp_session", "3-5 years")
    accident_history = st.session_state.get("accident_history_session", "No accidents")
    car_age = st.session_state.get("car_age_session", "New car")
    
    # Insurance Company Recommendations
    with st.container():
        st.write("")
        st.write("")
        st.subheader("🏆 Recommended Insurers")
        st.write("")
        
        recommended_insurances = insurance_recommendations.get(cluster_id, ["State Farm"])
        cols = st.columns(len(recommended_insurances))
        
        for idx, insurance in enumerate(recommended_insurances):
            with cols[idx]:
                info = insurance_companies.get(insurance, {})
                with st.container():
                    
                    # Insurance Company Logo
                    st.image(info.get("logo", ""), use_container_width=True)
                    
                    # Company Name
                    st.markdown(f"<h3 style='margin-top: 0.5rem;'>{insurance}</h3>", unsafe_allow_html=True)
                    
                    # Company Description
                    st.markdown(f"<p style='color: #6c757d; font-size: 0.9rem;'>{info.get('description', '')}</p>", unsafe_allow_html=True)
                    
                    # Strengths List
                    st.markdown("<p style='margin-bottom: 0.5rem;'><strong>Key Strengths:</strong></p>", unsafe_allow_html=True)
                    for strength in info.get("strengths", []):
                        st.markdown(f"<p style='margin: 0.2rem 0; font-size: 0.9rem;'>✓ {strength}</p>", unsafe_allow_html=True)
                    
                    # Hyundai Special Discount
                    if insurance == "State Farm":
                        st.markdown('<div class="highlight" style="font-size: 0.9rem;">✅ Special Hyundai owner discounts</div>', unsafe_allow_html=True)
                    
                    # Contact Info
                    st.markdown(f"<p style='margin-top: 1rem; margin-bottom: 0;'><strong>Contact:</strong> 📞 {info.get('contact', '')}</p>", unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)

    # Recommended Insurance Type
    with st.container():
        st.subheader("🔍 Recommended Insurance Type")
        
        if is_eco_friendly:
            insurance_type = "Eco-Friendly Special"
            eco_badge = '<span class="eco-badge">Eco Special</span>'
        elif cluster_id in [1, 3]:  # Premium customers
            insurance_type = "Premium Coverage"
            eco_badge = '<span class="premium-badge">Premium</span>'
        else:
            insurance_type = "Standard Coverage"
            eco_badge = ''
        
        type_info = insurance_type_details.get(insurance_type, {})
        
        with st.container():
            st.markdown(f'<div class="card">', unsafe_allow_html=True)
            st.markdown(f"<h3 style='display: flex; align-items: center;'>{insurance_type}{eco_badge}</h3>", unsafe_allow_html=True)
            
            # Insurance Description
            st.markdown(f"<p>{type_info.get('description', '')}</p>", unsafe_allow_html=True)
            
            # Price Info
            st.markdown(f"<p><strong>Estimated Monthly Premium:</strong> <span style='color: #0d6efd; font-weight: bold;'>{type_info.get('price_range', '')}</span></p>", unsafe_allow_html=True)
            
            # Coverage Tabs
            tab1, tab2, tab3 = st.tabs(list(type_info.get("coverages", {}).keys()))
            
            for tab, (category, items) in zip([tab1, tab2, tab3], type_info.get("coverages", {}).items()):
                with tab:
                    st.markdown(f"<div class='coverage-category'>{category}</div>", unsafe_allow_html=True)
                    for item in items:
                        st.markdown(f"<div class='coverage-item'>• {item}</div>", unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

    # Premium Calculation
    with st.container():
        st.subheader("📊 Premium Estimate")
        
        # Price Calculation Logic
        def calculate_insurance_price(base_price):
            # Discount/Surcharge Factors
            factors = {
                "driving_exp": {
                    "Under 1 year": 1.2, "1-3 years": 1.1, "3-5 years": 1.0, "5+ years": 0.9
                },
                "accident_history": {
                    "No accidents": 0.85, "1 accident": 1.0, "2 accidents": 1.2, "3+ accidents": 1.5
                },
                "car_age": {
                    "New car": 1.1, "1-3 years": 1.0, "3-5 years": 0.95, 
                    "5-7 years": 0.9, "7+ years": 0.8
                }
            }
            
            price = base_price
            price *= factors["driving_exp"][driving_exp]
            price *= factors["accident_history"][accident_history]
            price *= factors["car_age"][car_age]
            
            return int(price)
        
        # Calculate Prices for Each Insurer
        insurance_prices = {}
        for ins in recommended_insurances:
            ins_info = insurance_companies.get(ins, {})
            base_price = type_info.get("base_price", 150)
            temp_price = calculate_insurance_price(base_price)
            
            # Apply Discounts
            discounts = ins_info.get("discounts", {})
            if is_eco_friendly:
                temp_price *= (1 - discounts.get("친환경차", 0))
            if accident_history == "No accidents":
                temp_price *= (1 - discounts.get("무사고", 0))
            if car_age == "New car":
                temp_price *= (1 - discounts.get("신차", 0))
            
            insurance_prices[ins] = int(temp_price)
        
        # Display Results
        min_price = min(insurance_prices.values())
        max_price = max(insurance_prices.values())
        
        st.markdown(f"""
        <div class="highlight">
            <h4 style='margin: 0; color: #0d6efd;'>Estimated Monthly Premium Range</h4>
            <p style='font-size: 1.5rem; font-weight: bold; margin: 0.5rem 0;'>
                ${min_price:,} ~ ${max_price:,}
            </p>
            <p style='font-size: 0.9rem; margin: 0;'>* Based on your profile and vehicle information. Final premium determined by insurer.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Detailed Coverage by Insurer
        st.markdown("---")
        st.subheader("🔍 Detailed Coverage by Insurer")
        
        for ins, price in insurance_prices.items():
            with st.expander(f"{ins} - Estimated Monthly Premium: ${price:,}", expanded=True):
                info = insurance_companies.get(ins, {})
                
                # Discount Information
                discount_info = []
                ins_discounts = info.get("discounts", {})
                
                if is_eco_friendly and ins_discounts.get("친환경차", 0) > 0:
                    discount_info.append(f"Eco vehicle {ins_discounts['친환경차']*100:.0f}% discount")
                if accident_history == "No accidents" and ins_discounts.get("무사고", 0) > 0:
                    discount_info.append(f"Accident-free {ins_discounts['무사고']*100:.0f}% discount")
                if car_age == "New car" and ins_discounts.get("신차", 0) > 0:
                    discount_info.append(f"New car {ins_discounts['신차']*100:.0f}% discount")
                
                if discount_info:
                    st.markdown(f"<p><strong>Applied Discounts:</strong> {', '.join(discount_info)}</p>", unsafe_allow_html=True)
                
                # Coverage Details Tabs
                tabs = st.tabs(list(info.get("coverage_details", {}).keys()))
                
                for tab, (category, items) in zip(tabs, info.get("coverage_details", {}).items()):
                    with tab:
                        st.markdown(f"<div class='coverage-category'>{category}</div>", unsafe_allow_html=True)
                        for item in items:
                            st.markdown(f"<div class='coverage-item'>• {item}</div>", unsafe_allow_html=True)
                
                # Insurer Contact
                st.markdown(f"<div style='margin-top: 1rem;'><strong>Contact:</strong> 📞 {info.get('contact', '')}</div>", unsafe_allow_html=True)

    # Reset Button
    if st.button("Start Over", use_container_width=True):
        st.session_state["step"] = 1
        st.rerun()

def run_car_customer_EN():
    """메인 앱 실행"""
    load_css()
    
    # Initialize session state
    if "step" not in st.session_state:
        st.session_state["step"] = 1
    
    # Show appropriate page based on step
    if st.session_state["step"] == 1:
        input_customer_info()
    elif st.session_state["step"] == 2:
        Car_insurance_recommendation()

if __name__ == "__main__":
    run_car_customer_EN()