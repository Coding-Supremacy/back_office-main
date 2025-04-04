import streamlit as st
import pandas as pd
import joblib
from datetime import datetime
from pathlib import Path

# Hyundai 모델 및 출시 정보 (멕시코 대상은 동일)
launch_dates = {
    'Hyundai': {
        'G70 (IK)': '2017-09',
        'NEXO (FE)': '2018-01',
        'Elantra (CN7 N)': '2020-05',
        'G80 (RG3)': '2020-03',
        'Grandeur (GN7 HEV)': '2022-01',
        'Tucson (NX4 PHEV)': '2021-05',
        'Elantra (CN7 HEV)': '2020-07',
        'IONIQ 6 (CE)': '2022-06',
        'G90 (HI)': '2022-03',
        'Santa-Fe (MX5 PHEV)': '2022-06'
    }
}

eco_friendly_models = {
    'Hyundai': [
        'NEXO (FE)', 'Elantra (CN7 HEV)', 'Grandeur (GN7 HEV)', 
        'Tucson (NX4 PHEV)', 'IONIQ 6 (CE)', 'Santa-Fe (MX5 PHEV)'
    ]
}

# 클러스터 기반 보험사 추천 (AXA Seguros를 기본 파트너로)
insurance_recommendations = {
    0: ["AXA Seguros", "GNP Seguros"],
    1: ["AXA Seguros", "Qualitas"],
    2: ["AXA Seguros", "MAPFRE"],
    3: ["AXA Seguros", "HDI Seguros"],
    4: ["AXA Seguros", "Liberty Seguros"],
    5: ["AXA Seguros", "GNP Seguros"]
}

# 멕시코 보험사 상세 정보
insurance_companies = {
    "AXA Seguros": {
        "logo": "hoyeon\db_bo.png",
        "description": "Leading insurer in Mexico with innovative auto insurance solutions and a nationwide network.",
        "strengths": ["Exclusive Hyundai discounts", "Rapid claims process", "24/7 roadside assistance"],
        "contact": "01-800-AXA-1234",
        "discounts": {
            "eco": 0.15,
            "no_accidents": 0.1,
            "new_car": 0.05
        },
        "coverage_details": {
            "Basic Coverage": ["Third-party liability: MXN 1M", "Accident benefits", "Direct compensation"],
            "Special Coverage": ["OEM parts guarantee", "Waiver of depreciation", "Rental car coverage"],
            "Discounts": ["Multi-policy discount", "Claims-free discount", "Seasonal discount"]
        }
    },
    "GNP Seguros": {
        "logo": "hoyeon\db_bo.png",
        "description": "One of Mexico's largest insurers known for personalized service and comprehensive coverage.",
        "strengths": ["Usage-based insurance", "Eco-friendly vehicle discounts", "Bilingual customer service"],
        "contact": "01-800-GNP-5678",
        "discounts": {
            "eco": 0.1,
            "no_accidents": 0.15,
            "new_car": 0.03
        },
        "coverage_details": {
            "Basic Coverage": ["Third-party liability: MXN 1M", "Accident benefits", "Uninsured motorist coverage"],
            "Special Coverage": ["Electric vehicle accessories", "Roadside assistance", "Deductible waiver"],
            "Discounts": ["Telematics discount", "Multi-vehicle discount", "Loyalty discount"]
        }
    },
    "Qualitas": {
        "logo": "hoyeon\db_bo.png",
        "description": "Specialist in auto insurance with a focus on customer satisfaction and efficient claims processing.",
        "strengths": ["Digital claim submission", "Hybrid/Electric discounts", "Extensive service network"],
        "contact": "01-800-QUAL-9101",
        "discounts": {
            "eco": 0.12,
            "no_accidents": 0.12,
            "new_car": 0.04
        },
        "coverage_details": {
            "Basic Coverage": ["Third-party liability: MXN 1M", "Accident benefits", "Direct compensation"],
            "Special Coverage": ["New vehicle protection", "Depreciation waiver", "Enhanced rental coverage"],
            "Discounts": ["Safe driving discount", "Bundle discount", "Seasonal promotion"]
        }
    },
    "MAPFRE": {
        "logo": "mexico/mapfre.png",
        "description": "International insurer with a strong presence in Mexico offering tailored auto insurance solutions.",
        "strengths": ["Comprehensive coverage options", "Fast claims service", "Strong partner network"],
        "contact": "01-800-MAP-2345",
        "discounts": {
            "eco": 0.13,
            "no_accidents": 0.13,
            "new_car": 0.05
        },
        "coverage_details": {
            "Basic Coverage": ["Third-party liability: MXN 1M", "Accident benefits", "Uninsured motorist coverage"],
            "Special Coverage": ["Original parts protection", "Loss of use", "Pet injury coverage"],
            "Discounts": ["Safe driving rewards", "Multi-car discount", "Affiliation discount"]
        }
    },
    "HDI Seguros": {
        "logo": "mexico/hdi.png",
        "description": "A trusted insurer in Mexico known for flexible payment options and excellent customer support.",
        "strengths": ["Flexible plans", "Exclusive dealership partnerships", "24/7 claim support"],
        "contact": "01-800-HDI-3456",
        "discounts": {
            "eco": 0.1,
            "no_accidents": 0.1,
            "new_car": 0.05
        },
        "coverage_details": {
            "Basic Coverage": ["Third-party liability: MXN 1M", "Accident benefits", "Direct compensation"],
            "Special Coverage": ["Waiver of depreciation", "Transportation replacement", "Key replacement"],
            "Discounts": ["No-claim bonus", "Professional association discount", "Seasonal discount"]
        }
    },
    "Liberty Seguros": {
        "logo": "mexico/liberty.png",
        "description": "A reliable insurer in Mexico offering competitive rates and flexible coverage options.",
        "strengths": ["Competitive pricing", "Flexible payment plans", "Efficient claims processing"],
        "contact": "01-800-LIB-7890",
        "discounts": {
            "eco": 0.15,
            "no_accidents": 0.15,
            "new_car": 0.07
        },
        "coverage_details": {
            "Basic Coverage": ["Third-party liability: MXN 1M", "Accident benefits", "Direct compensation"],
            "Special Coverage": ["New car replacement", "Roadside assistance", "Deductible waiver"],
            "Discounts": ["Multi-policy discount", "Loyalty discount", "Seasonal promotion"]
        }
    }
}

# 멕시코 보험 유형 세부 정보
insurance_type_details = {
    "Eco-Friendly Plus": {
        "description": "Special coverage for hybrid/electric vehicles with Mexico-specific protections.",
        "price_range": "MXN 2,000 - MXN 3,500/month",
        "base_price": 2500,
        "coverages": {
            "Mandatory Coverage": [
                "Third-party liability: MXN 1M",
                "Accident benefits",
                "Direct compensation"
            ],
            "Eco-Specific Protections": [
                "Battery coverage",
                "Charging equipment protection",
                "Green rebate eligibility",
                "Roadside assistance"
            ],
            "Additional Benefits": [
                "Depreciation waiver",
                "Enhanced rental coverage",
                "Eco-driving rewards"
            ]
        }
    },
    "Premium Protection": {
        "description": "Comprehensive coverage with premium benefits for luxury vehicles in Mexico.",
        "price_range": "MXN 3,000 - MXN 5,000/month",
        "base_price": 4000,
        "coverages": {
            "Mandatory Coverage": [
                "Third-party liability: MXN 1M",
                "Enhanced accident benefits",
                "Direct compensation"
            ],
            "Premium Benefits": [
                "New car replacement (2 years)",
                "Original parts guarantee",
                "Concierge claims service",
                "Nationwide roadside assistance"
            ],
            "Luxury Services": [
                "Dedicated claims specialist",
                "Rental car upgrades",
                "Trip interruption coverage"
            ]
        }
    },
    "Standard Protection": {
        "description": "Basic auto insurance meeting Mexico's regulatory requirements.",
        "price_range": "MXN 1,500 - MXN 2,500/month",
        "base_price": 2000,
        "coverages": {
            "Mandatory Coverage": [
                "Third-party liability: MXN 500,000",
                "Basic accident benefits",
                "Direct compensation"
            ],
            "Standard Protections": [
                "Collision coverage",
                "Comprehensive coverage",
                "Basic rental coverage"
            ],
            "Optional Add-ons": [
                "Increased liability limits",
                "Enhanced accident benefits",
                "Roadside assistance"
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
    """Load machine learning models"""
    model_dir = Path(__file__).parent.parent / "models_mini1"
    segment_model_path = model_dir / "gb_model_hs.pkl"
    clustering_model_path = model_dir / "gb_pipeline_hc.pkl"

    if not segment_model_path.exists() or not clustering_model_path.exists():
        st.error("Model files not found.")
        st.stop()

    return joblib.load(segment_model_path), joblib.load(clustering_model_path)

def input_customer_info():
    """Customer information input form"""
    st.title("📋 Hyundai Mexico Customer Information")
    
    segment_model, clustering_model = load_models()
    
    with st.form(key="customer_form"):
        # Section 1: Basic Information
        st.subheader("1. Basic Information")
        col1, col2 = st.columns(2)
        
        with col1:
            gender = st.selectbox("Gender", ["Male", "Female", "Other"], key="gender")
            birth_date = st.date_input("Date of Birth", 
                                    min_value=datetime(1900, 1, 1), 
                                    max_value=datetime.today().replace(year=datetime.today().year - 18),
                                    key="birth_date")
        
        with col2:
            car_type = st.selectbox("Vehicle Type", ["Compact Sedan", "Midsize Sedan", "Full-size Sedan", "SUV", "Truck"], key="car_type")
            selected_vehicle = st.selectbox("Model Selection", list(launch_dates['Hyundai'].keys()), key="car_model")
    
        # Section 2: Purchase Information
        st.subheader("2. Purchase Information")
        col1, col2 = st.columns(2)
        
        with col1:
            transaction_amount = st.number_input("Budget (MXN)", min_value=10000, step=1000, format="%d", key="budget")
            purchase_frequency = st.number_input("Purchase Frequency", min_value=1, value=1, key="purchase_freq")
        
        with col2:
            transaction_method = st.selectbox("Payment Method", ["Credit Card", "Cash", "Bank Transfer", "Lease"], key="payment_method")
            purchase_date = st.date_input("Purchase Date", key="purchase_date")
    
        # Section 3: Insurance Information
        st.subheader("3. Insurance Information")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            driving_exp = st.selectbox("Driving Experience", ["Under 1 year", "1-3 years", "3-5 years", "5-10 years", "10+ years"], key="driving_exp_select")
        
        with col2:
            accident_history = st.selectbox("Accident History (6 years)", ["No accidents", "1 at-fault", "2+ at-fault", "Not-at-fault only"], key="accident_history_select")
        
        with col3:
            car_age = st.selectbox("Vehicle Age", ["Brand new", "1 year old", "2-3 years old", "4-5 years old", "6+ years old"], key="car_age_select")
        
        # Submit Button
        submitted = st.form_submit_button("Get Insurance Recommendations", use_container_width=True)
        
        if submitted:
            # Age Calculation
            today = datetime.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            
            # Segment Prediction using Korean column names expected by the model
            segment_input = pd.DataFrame(
                [[transaction_method, launch_dates['Hyundai'].get(selected_vehicle), 
                  purchase_date, transaction_amount, purchase_frequency]],
                columns=['거래 방식', '제품 출시년월', '제품 구매 날짜', '거래 금액', '제품 구매 빈도']
            )
            customer_segment = segment_model.predict(segment_input)[0]
            
            # Map gender to Korean (Male->남, Female->여, Other->기타)
            gender_map = {"Male": "남", "Female": "여", "Other": "기타"}
            gender_kor = gender_map.get(gender, gender)
            
            # Clustering Prediction using Korean column names expected by the model
            cluster_input = pd.DataFrame(
                [[gender_kor, car_type, transaction_method, 
                  launch_dates['Hyundai'].get(selected_vehicle),
                  purchase_date, customer_segment,
                  "여" if selected_vehicle in eco_friendly_models['Hyundai'] else "부",
                  age, transaction_amount, purchase_frequency]],
                columns=['성별', '차량구분', '거래 방식', '제품 출시년월',
                         '제품 구매 날짜', '고객 세그먼트', '친환경차',
                         '연령', '거래 금액', '제품 구매 빈도']
            )
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
                "is_eco_friendly": selected_vehicle in eco_friendly_models['Hyundai']
            })
            
            st.rerun()

def Car_insurance_recommendation():
    """Display insurance recommendations"""
    st.title("🚗 Personalized Hyundai Mexico Auto Insurance")
    
    # Get customer info from session
    cluster_id = st.session_state.get("cluster_id", 0)
    selected_vehicle = st.session_state.get("selected_vehicle", "")
    is_eco_friendly = st.session_state.get("is_eco_friendly", False)
    driving_exp = st.session_state.get("driving_exp_session", "3-5 years")
    accident_history = st.session_state.get("accident_history_session", "No accidents")
    car_age = st.session_state.get("car_age_session", "Brand new")
    
    # Insurance Company Recommendations
    with st.container():
        st.write("")
        st.write("")
        st.subheader("🏆 Recommended Mexican Insurers")
        st.write("")
        
        recommended_insurances = insurance_recommendations.get(cluster_id, ["AXA Seguros"])
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
                    
                    # Hyundai Special Discount (AXA Seguros가 기본 파트너)
                    if insurance == "AXA Seguros":
                        st.markdown('<div class="highlight" style="font-size: 0.9rem;">✅ Preferred Hyundai Mexico partner discounts</div>', unsafe_allow_html=True)
                    
                    # Contact Info
                    st.markdown(f"<p style='margin-top: 1rem; margin-bottom: 0;'><strong>Contact:</strong> 📞 {info.get('contact', '')}</p>", unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)

    # Recommended Insurance Type
    with st.container():
        st.subheader("🔍 Recommended Insurance Type")
        
        if is_eco_friendly:
            insurance_type = "Eco-Friendly Plus"
            eco_badge = '<span class="eco-badge">Eco Special</span>'
        elif cluster_id in [1, 3]:  # Premium customers
            insurance_type = "Premium Protection"
            eco_badge = '<span class="premium-badge">Premium</span>'
        else:
            insurance_type = "Standard Protection"
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
            # Mexico-specific rating factors
            factors = {
                "driving_exp": {
                    "Under 1 year": 1.5, 
                    "1-3 years": 1.2, 
                    "3-5 years": 1.0, 
                    "5-10 years": 0.9, 
                    "10+ years": 0.8
                },
                "accident_history": {
                    "No accidents": 0.8, 
                    "Not-at-fault only": 0.9, 
                    "1 at-fault": 1.3, 
                    "2+ at-fault": 1.8
                },
                "car_age": {
                    "Brand new": 1.2, 
                    "1 year old": 1.1, 
                    "2-3 years old": 1.0, 
                    "4-5 years old": 0.95, 
                    "6+ years old": 0.85
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
            base_price = type_info.get("base_price", 2000)
            temp_price = calculate_insurance_price(base_price)
            
            # Apply Mexico-specific discounts
            discounts = ins_info.get("discounts", {})
            if is_eco_friendly:
                temp_price *= (1 - discounts.get("eco", 0))
            if accident_history == "No accidents":
                temp_price *= (1 - discounts.get("no_accidents", 0))
            if car_age in ["Brand new", "1 year old"]:
                temp_price *= (1 - discounts.get("new_car", 0))
            
            insurance_prices[ins] = int(temp_price)
        
        # Display Results
        min_price = min(insurance_prices.values())
        max_price = max(insurance_prices.values())
        
        st.markdown(f"""
        <div class="highlight">
            <h4 style='margin: 0; color: #0d6efd;'>Estimated Monthly Premium Range</h4>
            <p style='font-size: 1.5rem; font-weight: bold; margin: 0.5rem 0;'>
                MXN {min_price:,} - MXN {max_price:,}
            </p>
            <p style='font-size: 0.9rem; margin: 0;'>* Based on your profile and local requirements. Final premium subject to insurer approval.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Detailed Coverage by Insurer
        st.markdown("---")
        st.subheader("🔍 Detailed Coverage by Insurer")
        
        for ins, price in insurance_prices.items():
            with st.expander(f"{ins} - Estimated Monthly Premium: MXN {price:,}", expanded=True):
                info = insurance_companies.get(ins, {})
                
                # Discount Information
                discount_info = []
                ins_discounts = info.get("discounts", {})
                
                if is_eco_friendly and ins_discounts.get("eco", 0) > 0:
                    discount_info.append(f"Eco vehicle {ins_discounts['eco']*100:.0f}% discount")
                if accident_history == "No accidents" and ins_discounts.get("no_accidents", 0) > 0:
                    discount_info.append(f"Accident-free {ins_discounts['no_accidents']*100:.0f}% discount")
                if car_age in ["Brand new", "1 year old"] and ins_discounts.get("new_car", 0) > 0:
                    discount_info.append(f"New vehicle {ins_discounts['new_car']*100:.0f}% discount")
                
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

def run_car_customer_Me():
    """Main app execution"""
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
    run_car_customer_Me()
