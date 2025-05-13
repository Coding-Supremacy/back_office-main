import os
import time
import streamlit as st
import pandas as pd
import joblib
from datetime import datetime
from pathlib import Path
import base64
import requests

# US Auto Insurance Email Sending Module (assumed to be implemented separately)
import project_1.ui_mini1.mini1_promo_email as promo_email

def get_abs_path(relative_path):
    """Convert a relative path to an absolute path"""
    return Path(__file__).parent.parent / relative_path

# Vehicle models and launch dates for the US market (example: Ford models)
launch_dates = {
    'Ford': {
        'Fiesta': '2017-03',
        'Focus': '2018-06',
        'Fusion': '2019-04',
        'Mustang': '2020-05',
        'Explorer': '2021-07',
        'F-150': '2018-09'
    }
}

eco_friendly_models = {
    'Ford': [
        'Fusion', 'Focus'
    ]
}

# Recommended insurance companies by cluster (US market example)
insurance_recommendations = {
    0: ["GEICO", "State Farm"],
    1: ["GEICO", "Progressive"],
    2: ["GEICO", "Allstate"],
    3: ["GEICO", "USAA"],
    4: ["GEICO", "Liberty Mutual"],
    5: ["GEICO", "Travelers"]
}

# Detailed information of insurance companies (US market example)
insurance_companies = {
    "GEICO": {
        "logo": "hoyeon/ge.png",
        "description": "GEICO is one of the most recognized insurers in the US, known for competitive rates and an efficient claims process.",
        "strengths": ["Competitive rates", "Fast claims process", "Comprehensive coverage"],
        "contact": "1-800-861-8380",
        "discounts": {
            "eco_vehicle": 0.10,
            "no_accidents": 0.15,
            "new_car": 0.05
        },
        "coverage_details": {
            "Basic Coverage": [
                "Liability: up to USD$50,000", 
                "Property Damage: up to USD$50,000", 
                "Personal Injury: up to USD$25,000"
            ],
            "Additional Coverage": [
                "Collision Coverage", 
                "Comprehensive Coverage", 
                "24/7 Roadside Assistance"
            ],
            "Special Benefits": [
                "Safe Driver Discounts", 
                "24/7 Customer Service", 
                "Digital Claims Processing"
            ]
        }
    },
    "State Farm": {
        "logo": "hoyeon/sta.png",
        "description": "State Farm offers personalized insurance solutions with a wide network of agents and a strong focus on customer service.",
        "strengths": ["Extensive Agent Network", "Personalized Service", "Comprehensive Solutions"],
        "contact": "1-800-STATE-FARM",
        "discounts": {
            "eco_vehicle": 0.08,
            "no_accidents": 0.12,
            "new_car": 0.04
        },
        "coverage_details": {
            "Basic Coverage": [
                "Liability: up to USD$45,000", 
                "Property Damage Protection", 
                "Personal Injury Coverage"
            ],
            "Additional Coverage": [
                "Collision Coverage", 
                "Comprehensive Protection", 
                "Rental Reimbursement"
            ],
            "Special Benefits": [
                "Loyalty Discounts", 
                "Personalized Advice", 
                "Efficient Claims Handling"
            ]
        }
    },
    "Progressive": {
        "logo": "hoyeon/pro.png",
        "description": "Progressive is known for its innovative auto insurance solutions, offering digital tools and flexible coverage options.",
        "strengths": ["Digital Innovation", "Flexible Options", "Good Value"],
        "contact": "1-800-PROGRESSIVE",
        "discounts": {
            "eco_vehicle": 0.09,
            "no_accidents": 0.14,
            "new_car": 0.05
        },
        "coverage_details": {
            "Basic Coverage": [
                "Liability: up to USD$50,000", 
                "Accident Protection", 
                "Medical Coverage"
            ],
            "Additional Coverage": [
                "Collision Coverage", 
                "Full Coverage", 
                "Roadside Assistance"
            ],
            "Special Benefits": [
                "Multi-Policy Discounts", 
                "Advanced Digital Tools", 
                "Rewards for Safe Driving"
            ]
        }
    },
    "Allstate": {
        "logo": "hoyeon/allst.png",
        "description": "Allstate stands out for its dedicated customer service and comprehensive insurance solutions tailored to American drivers.",
        "strengths": ["Dedicated Customer Service", "Wide Coverage", "Exclusive Benefits"],
        "contact": "1-800-ALLSTATE",
        "discounts": {
            "eco_vehicle": 0.07,
            "no_accidents": 0.13,
            "new_car": 0.06
        },
        "coverage_details": {
            "Basic Coverage": [
                "Liability: up to USD$50,000", 
                "Property Damage Coverage", 
                "Personal Injury Protection"
            ],
            "Additional Coverage": [
                "Collision Coverage", 
                "Comprehensive Coverage", 
                "Rental Reimbursement"
            ],
            "Special Benefits": [
                "Safe Driving Discounts", 
                "Priority Service", 
                "Flexible Payment Plans"
            ]
        }
    },
    "USAA": {
        "logo": "hoyeon/usaa.png",
        "description": "USAA specializes in insurance for military members and their families, offering competitive coverage and excellent customer service.",
        "strengths": ["Competitive Rates for Military", "Exceptional Customer Service", "Efficient Claims Process"],
        "contact": "1-800-USAA-USA",
        "discounts": {
            "eco_vehicle": 0.08,
            "no_accidents": 0.16,
            "new_car": 0.05
        },
        "coverage_details": {
            "Basic Coverage": [
                "Liability: up to USD$55,000", 
                "Property Damage Coverage", 
                "Personal Injury Protection"
            ],
            "Additional Coverage": [
                "Collision Coverage", 
                "Comprehensive Coverage", 
                "24/7 Roadside Assistance"
            ],
            "Special Benefits": [
                "Special Military Discounts", 
                "Online Claims Management", 
                "Personalized Service"
            ]
        }
    },
    "Liberty Mutual": {
        "logo": "us/libertymutual.png",
        "description": "Liberty Mutual offers auto insurance with extensive coverage and personalized solutions, backed by a strong market reputation.",
        "strengths": ["Extensive Coverage", "Personalized Solutions", "Strong Reputation"],
        "contact": "1-800-LIBERTY",
        "discounts": {
            "eco_vehicle": 0.09,
            "no_accidents": 0.14,
            "new_car": 0.04
        },
        "coverage_details": {
            "Basic Coverage": [
                "Liability: up to USD$50,000", 
                "Property Damage Protection", 
                "Personal Injury Coverage"
            ],
            "Additional Coverage": [
                "Collision Coverage", 
                "Comprehensive Coverage", 
                "Rental Reimbursement"
            ],
            "Special Benefits": [
                "Multi-Policy Discounts", 
                "24/7 Customer Support", 
                "Flexible Coverage Options"
            ]
        }
    },
    "Travelers": {
        "logo": "us/travelers.png",
        "description": "Travelers is known for its robust auto insurance offerings, providing comprehensive protection and fast claims assistance.",
        "strengths": ["Comprehensive Protection", "Fast Claims Process", "Wide Service Network"],
        "contact": "1-800-TRAVELERS",
        "discounts": {
            "eco_vehicle": 0.10,
            "no_accidents": 0.12,
            "new_car": 0.05
        },
        "coverage_details": {
            "Basic Coverage": [
                "Liability: up to USD$50,000", 
                "Third-Party Property Damage", 
                "Injury Protection"
            ],
            "Additional Coverage": [
                "Collision Coverage", 
                "Full Coverage", 
                "24/7 Roadside Assistance"
            ],
            "Special Benefits": [
                "Safe Driving Discounts", 
                "24/7 Digital Support", 
                "Quick Claims Processing"
            ]
        }
    }
}

# Insurance type details in English (adapted for the US market)
insurance_type_details = {
    "Eco Insurance": {
        "description": "Insurance designed for eco-friendly vehicles in the US, with special coverage for green technologies.",
        "price_range": "USD$90 ~ USD$140",
        "base_price": 180,
        "coverages": {
            "Mandatory Coverage": [
                "Liability Coverage", 
                "Property Damage up to USD$50,000", 
                "Personal Injury Coverage up to USD$25,000"
            ],
            "Eco Coverage": [
                "Coverage for Electrical System Damage", 
                "Insurance for Charging Station Incidents", 
                "Support for Eco Component Replacement", 
                "Electric Charging Assistance"
            ],
            "Additional Services": [
                "Discounts at Eco-Friendly Service Centers", 
                "Extended Warranty on Electrical Systems", 
                "Incentive Program for Energy Efficiency"
            ]
        }
    },
    "Premium Insurance": {
        "description": "Comprehensive insurance package for high-end vehicles in the US, with exclusive options for discerning clients.",
        "price_range": "USD$140 ~ USD$220",
        "base_price": 240,
        "coverages": {
            "Mandatory Coverage": [
                "Liability Coverage", 
                "Property Damage up to USD$75,000", 
                "Personal Injury Coverage up to USD$30,000"
            ],
            "Special Coverage": [
                "Full Coverage", 
                "Support for OEM Parts Replacement", 
                "VIP Roadside Assistance", 
                "Priority Claims Handling"
            ],
            "Complementary Services": [
                "Dedicated 24/7 Support Line", 
                "Premium Replacement Vehicle", 
                "International Coverage"
            ]
        }
    },
    "Standard Insurance": {
        "description": "Basic insurance offering essential coverages for most vehicles in the US.",
        "price_range": "USD$70 ~ USD$120",
        "base_price": 130,
        "coverages": {
            "Mandatory Coverage": [
                "Liability Coverage", 
                "Property Damage up to USD$40,000", 
                "Personal Injury Coverage up to USD$20,000"
            ],
            "Basic Coverage": [
                "Partial Damage Insurance", 
                "Deductible Reduction", 
                "Roadside Assistance"
            ],
            "Optional Coverage": [
                "Accessory Coverage", 
                "Additional Medical Expense Coverage", 
                "Legal Support in Case of an Accident"
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
    """Load segmentation and clustering models"""
    model_dir = Path(__file__).parent.parent / "models_mini1"
    segment_model_path = model_dir / "gb_model_hs.pkl"
    clustering_model_path = model_dir / "gb_pipeline_hc.pkl"

    if not segment_model_path.exists() or not clustering_model_path.exists():
        st.error("Model files not found.")
        st.stop()

    return joblib.load(segment_model_path), joblib.load(clustering_model_path)

def input_customer_info():
    st.title("📋 Enter Customer Information")
    
    segment_model, clustering_model = load_models()
    
    with st.form(key="customer_form"):
        st.subheader("1. Basic Information")
        col1, col2 = st.columns(2)
        with col1:
            gender = st.selectbox("Gender", ["Male", "Female"], key="gender")
            birth_date = st.date_input("Birth Date", 
                                    min_value=datetime(1900, 1, 1), 
                                    max_value=datetime.today().replace(year=datetime.today().year - 20),
                                    key="birth_date")
        with col2:
            vehicle_type = st.selectbox("Vehicle Type", ["Compact Sedan", "Mid-size Sedan", "Full-size Sedan", "SUV"], key="vehicle_type")
            selected_model = st.selectbox("Select Model", list(launch_dates['Ford'].keys()), key="vehicle_model")
        
        st.subheader("2. Purchase Information")
        col1, col2 = st.columns(2)
        with col1:
            transaction_amount = st.number_input("Budget (USD)", min_value=10000, step=1000, format="%d", key="budget")
            purchase_frequency = st.number_input("Purchase Frequency", min_value=1, value=1, key="frequency")
        with col2:
            payment_method = st.selectbox("Payment Method", ["Card", "Cash", "Transfer"], key="payment_method")
            purchase_date = st.date_input("Planned Purchase Date", key="purchase_date")
        
        st.subheader("3. Insurance Information")
        col1, col2, col3 = st.columns(3)
        with col1:
            driving_experience = st.selectbox("Driving Experience", ["Less than 1 year", "1-3 years", "3-5 years", "More than 5 years"], key="experience")
        with col2:
            accident_history = st.selectbox("Accident History (last 3 years)", ["No accidents", "1 accident", "2 accidents", "3 or more accidents"], key="accidents")
        with col3:
            # Create a selectbox with Korean options for car age and map to English
            car_age_option = st.selectbox("Car Age", ["신차", "1-3년", "3-5년", "5-7년", "7년 이상"], key="car_age")
            car_age_mapping = {
                "신차": "New",
                "1-3년": "1-3 years",
                "3-5년": "3-5 years",
                "5-7년": "5-7 years",
                "7년 이상": "More than 7 years"
            }
            car_age = car_age_mapping.get(car_age_option, car_age_option)
        
        submitted = st.form_submit_button("Get Insurance Recommendation", use_container_width=True)
        
        if submitted:
            today = datetime.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            
            # Note: Although the UI is in English, the model expects column names in Korean.
            input_segment = pd.DataFrame(
                [[payment_method, launch_dates['Ford'].get(selected_model), 
                  purchase_date, transaction_amount, purchase_frequency]],
                columns=['거래 방식', '제품 출시년월', '제품 구매 날짜', '거래 금액', '제품 구매 빈도']
            )
            customer_segment = segment_model.predict(input_segment)[0]
            
            input_cluster = pd.DataFrame(
                [[gender, vehicle_type, payment_method, launch_dates['Ford'].get(selected_model),
                  purchase_date, customer_segment,
                  "Yes" if selected_model in eco_friendly_models['Ford'] else "No",
                  age, transaction_amount, purchase_frequency]],
                columns=['성별', '차량구분', '거래 방식', '제품 출시년월', 
                         '제품 구매 날짜', '고객 세그먼트', '친환경차',
                         '연령', '거래 금액', '제품 구매 빈도']
            )
            cluster_id = clustering_model.predict(input_cluster)[0]
            
            # Save session state (prefix "car_insurance_")
            st.session_state.update({
                "car_insurance_step": 2,
                "car_insurance_cluster_id": cluster_id,
                "car_insurance_selected_vehicle": selected_model,
                "car_insurance_experience": driving_experience,
                "car_insurance_accidents": accident_history,
                "car_insurance_car_age": car_age,
                "car_insurance_gender": gender,
                "car_insurance_birth_date": birth_date,
                "car_insurance_transaction_amount": transaction_amount,
                "car_insurance_purchase_frequency": purchase_frequency,
                "car_insurance_vehicle_type": vehicle_type,
                "car_insurance_payment_method": payment_method,
                "car_insurance_purchase_date": purchase_date,
                "car_insurance_age": age,
                "car_insurance_is_eco_friendly": selected_model in eco_friendly_models['Ford']
            })
            
            st.rerun()

def Car_insurance_recommendation():
    st.title("🚗 Personalized Auto Insurance Recommendation for the US")
    
    cluster_id = st.session_state.get("car_insurance_cluster_id", 0)
    selected_model = st.session_state.get("car_insurance_selected_vehicle", "")
    is_eco = st.session_state.get("car_insurance_is_eco_friendly", False)
    driving_experience = st.session_state.get("car_insurance_experience", "3-5 years")
    accident_history = st.session_state.get("car_insurance_accidents", "No accidents")
    car_age = st.session_state.get("car_insurance_car_age", "New")
    
    # Section: Recommended Insurance Companies
    with st.container():
        st.write("")
        st.write("")
        st.subheader("🏆 Recommended Insurance Companies")
        st.write("")
        
        recommended = insurance_recommendations.get(cluster_id, ["GEICO"])
        cols = st.columns(len(recommended))
        
        for idx, comp in enumerate(recommended):
            with cols[idx]:
                info = insurance_companies.get(comp, {})
                with st.container():
                    st.image(info.get("logo", ""), use_container_width=True)
                    st.markdown(f"<h3 style='margin-top: 0.5rem;'>{comp}</h3>", unsafe_allow_html=True)
                    st.markdown(f"<p style='color: #6c757d; font-size: 0.9rem;'>{info.get('description', '')}</p>", unsafe_allow_html=True)
                    st.markdown("<p style='margin-bottom: 0.5rem;'><strong>Key Strengths:</strong></p>", unsafe_allow_html=True)
                    for strength in info.get("strengths", []):
                        st.markdown(f"<p style='margin: 0.2rem 0; font-size: 0.9rem;'>✓ {strength}</p>", unsafe_allow_html=True)
                    if comp == "GEICO":
                        st.markdown('<div class="highlight" style="font-size: 0.9rem;">✅ Special discount for modern car owners</div>', unsafe_allow_html=True)
                    st.markdown(f"<p style='margin-top: 1rem; margin-bottom: 0;'><strong>Contact:</strong> 📞 {info.get('contact', '')}</p>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
    
    # Section: Recommended Insurance Type
    with st.container():
        st.subheader("🔍 Recommended Insurance Types")
        
        if is_eco:
            insurance_type = "Eco Insurance"
            eco_badge = '<span class="eco-badge">Eco</span>'
        elif cluster_id in [1, 3]:
            insurance_type = "Premium Insurance"
            eco_badge = '<span class="premium-badge">Premium</span>'
        else:
            insurance_type = "Standard Insurance"
            eco_badge = ''
        
        type_info = insurance_type_details.get(insurance_type, {})
        
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f"<h3 style='display: flex; align-items: center;'>{insurance_type}{eco_badge}</h3>", unsafe_allow_html=True)
            st.markdown(f"<p>{type_info.get('description', '')}</p>", unsafe_allow_html=True)
            st.markdown(f"<p><strong>Estimated Monthly Premium:</strong> <span style='color: #0d6efd; font-weight: bold;'>{type_info.get('price_range', '')}</span></p>", unsafe_allow_html=True)
            tab1, tab2, tab3 = st.tabs(list(type_info.get("coverages", {}).keys()))
            for tab, (category, items) in zip([tab1, tab2, tab3], type_info.get("coverages", {}).items()):
                with tab:
                    st.markdown(f"<div class='coverage-category'>{category}</div>", unsafe_allow_html=True)
                    for item in items:
                        st.markdown(f"<div class='coverage-item'>• {item}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    
    # Section: Estimated Premium Calculation
    with st.container():
        st.subheader("📊 Estimated Premium Calculation")
        
        def calculate_insurance_price(base_price):
            factors = {
                "experience": {
                    "Less than 1 year": 1.2, "1-3 years": 1.1, "3-5 years": 1.0, "More than 5 years": 0.9
                },
                "accidents": {
                    "No accidents": 0.85, "1 accident": 1.0, "2 accidents": 1.2, "3 or more accidents": 1.5
                },
                "car_age": {
                    "New": 1.1, "1-3 years": 1.0, "3-5 years": 0.95, "5-7 years": 0.9, "More than 7 years": 0.8
                }
            }
            price = base_price
            price *= factors["experience"][driving_experience]
            price *= factors["accidents"][accident_history]
            price *= factors["car_age"][car_age]
            return int(price)
        
        insurance_prices = {}
        for comp in recommended:
            info = insurance_companies.get(comp, {})
            base_price = type_info.get("base_price", 130)
            temp = calculate_insurance_price(base_price)
            discounts = info.get("discounts", {})
            if is_eco:
                temp *= (1 - discounts.get("eco_vehicle", 0))
            if accident_history == "No accidents":
                temp *= (1 - discounts.get("no_accidents", 0))
            if car_age == "New":
                temp *= (1 - discounts.get("new_car", 0))
            insurance_prices[comp] = int(temp)
        
        price_min = min(insurance_prices.values())
        price_max = max(insurance_prices.values())
        
        st.markdown(f"""
        <div class="highlight">
            <h4 style='margin: 0; color: #0d6efd;'>Estimated Monthly Premium Range</h4>
            <p style='font-size: 1.5rem; font-weight: bold; margin: 0.5rem 0;'>
                USD$ {price_min:,} ~ USD$ {price_max:,}
            </p>
            <p style='font-size: 0.9rem; margin: 0;'>* Estimate based on customer profile and vehicle information.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("🔍 Coverage Details by Company")
        
        for comp, price in insurance_prices.items():
            with st.expander(f"{comp} - Estimated Premium: USD$ {price:,}", expanded=True):
                info = insurance_companies.get(comp, {})
                applied_discounts = []
                comp_discounts = info.get("discounts", {})
                if is_eco and comp_discounts.get("eco_vehicle", 0) > 0:
                    applied_discounts.append(f"Eco discount {comp_discounts['eco_vehicle']*100:.0f}%")
                if accident_history == "No accidents" and comp_discounts.get("no_accidents", 0) > 0:
                    applied_discounts.append(f"No accident discount {comp_discounts['no_accidents']*100:.0f}%")
                if car_age == "New" and comp_discounts.get("new_car", 0) > 0:
                    applied_discounts.append(f"New car discount {comp_discounts['new_car']*100:.0f}%")
                if applied_discounts:
                    st.markdown(f"<p><strong>Applied Discounts:</strong> {', '.join(applied_discounts)}</p>", unsafe_allow_html=True)
                tabs = st.tabs(list(info.get("coverage_details", {}).keys()))
                for tab, (category, items) in zip(tabs, info.get("coverage_details", {}).items()):
                    with tab:
                        st.markdown(f"<div class='coverage-category'>{category}</div>", unsafe_allow_html=True)
                        for item in items:
                            st.markdown(f"<div class='coverage-item'>• {item}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='margin-top: 1rem;'><strong>Contact:</strong> 📞 {info.get('contact', '')}</div>", unsafe_allow_html=True)
    
    if st.button("Reset Entry", use_container_width=True):
        st.session_state["car_insurance_step"] = 1
        st.rerun()

def run_car_customer_us():
    load_css()
    
    if "car_insurance_step" not in st.session_state:
        st.session_state["car_insurance_step"] = 1
    
    if st.session_state["car_insurance_step"] == 1:
        input_customer_info()
    elif st.session_state["car_insurance_step"] == 2:
        Car_insurance_recommendation()

if __name__ == "__main__":
    run_car_customer_us()
