import os
import time
import streamlit as st
import pandas as pd
import joblib
from datetime import datetime
from pathlib import Path
import base64
import requests

# 캐나다 보험 이메일 발송 모듈 (별도 구현했다고 가정)
import project_1.ui_mini1.mini1_promo_email as promo_email

def get_abs_path(relative_path):
    """상대 경로를 절대 경로로 변환"""
    return Path(__file__).parent.parent / relative_path

# 차량 모델 및 출시 년월 데이터 (캐나다 시장용, Ford 모델 예시)
launch_dates = {
    'Ford': {
        'Focus': '2018-01',
        'Fusion': '2019-05',
        'Mustang': '2020-03',
        'Explorer': '2021-06',
        'Edge': '2019-09',
        'Escape': '2020-11'
    }
}

eco_friendly_models = {
    'Ford': [
        'Fusion', 'Escape'
    ]
}

# 클러스터별 보험사 추천 (캐나다 시장용 예시)
insurance_recommendations = {
    0: ["Intact Insurance", "Desjardins Insurance"],
    1: ["Intact Insurance", "Aviva Canada"],
    2: ["Intact Insurance", "The Co-operators"],
    3: ["Intact Insurance", "RSA Canada"],
    4: ["Intact Insurance", "Economical Insurance"],
    5: ["Intact Insurance", "Allstate Canada"]
}

# 보험사 상세 정보 (캐나다 시장용 예시)
insurance_companies = {
    "Intact Insurance": {
        "logo": "hoyeon/in.png",
        "description": "Intact Insurance is one of Canada's leading auto insurers, known for comprehensive coverage and excellent customer service.",
        "strengths": ["Wide network of service providers", "Efficient claims process", "Flexible coverage options"],
        "contact": "1-800-123-INTACT",
        "discounts": {
            "vehiculo_ecologico": 0.10,
            "sin_accidentes": 0.15,
            "auto_nuevo": 0.05
        },
        "coverage_details": {
            "Cobertura Básica": [
                "Responsabilidad civil: hasta CAD$50,000", 
                "Daños a terceros: hasta CAD$50,000", 
                "Lesiones personales: hasta CAD$25,000"
            ],
            "Cobertura Adicional": [
                "Seguro contra colisión", 
                "Seguro a todo riesgo", 
                "Asistencia en carretera 24/7"
            ],
            "Beneficios Especiales": [
                "Descuentos en talleres afiliados", 
                "Cobertura de auto de reemplazo", 
                "Planes de pago flexibles"
            ]
        }
    },
    "Desjardins Insurance": {
        "logo": "hoyeon/de.png",
        "description": "Desjardins Insurance offers personalized auto insurance solutions, providing extensive coverage and exceptional claims support across Canada.",
        "strengths": ["Personalized service", "Strong local presence", "Quick claim resolution"],
        "contact": "1-800-456-DESJ",
        "discounts": {
            "vehiculo_ecologico": 0.12,
            "sin_accidentes": 0.10,
            "auto_nuevo": 0.04
        },
        "coverage_details": {
            "Cobertura Básica": [
                "Responsabilidad civil: hasta CAD$45,000", 
                "Beneficios por accidentes", 
                "Protección para conductores sin seguro"
            ],
            "Cobertura Adicional": [
                "Seguro contra colisión", 
                "Seguro a todo riesgo", 
                "Reembolso por alquiler de vehículo"
            ],
            "Beneficios Especiales": [
                "Descuentos por fidelidad", 
                "Atención personalizada en línea", 
                "Gestión rápida de reclamaciones"
            ]
        }
    },
    "Aviva Canada": {
        "logo": "hoyeon/aviva.png",
        "description": "Aviva Canada is a reputable provider of auto insurance, offering innovative coverage options and robust customer support.",
        "strengths": ["Innovative policies", "Competitive rates", "Strong digital tools"],
        "contact": "1-800-789-AVIVA",
        "discounts": {
            "vehiculo_ecologico": 0.08,
            "sin_accidentes": 0.12,
            "auto_nuevo": 0.03
        },
        "coverage_details": {
            "Cobertura Básica": [
                "Responsabilidad civil: hasta CAD$50,000", 
                "Pagos médicos", 
                "Beneficios por accidentes"
            ],
            "Cobertura Adicional": [
                "Seguro contra colisión", 
                "Seguro a todo riesgo", 
                "Cobertura de pérdida de uso"
            ],
            "Beneficios Especiales": [
                "Descuentos por pólizas múltiples", 
                "Asistencia en carretera 24/7", 
                "Accident forgiveness"
            ]
        }
    },
    "The Co-operators": {
        "logo": "hoyeon/in.png",
        "description": "The Co-operators offers a wide range of auto insurance products designed to meet diverse needs with competitive pricing.",
        "strengths": ["Community-focused", "Wide range of options", "Strong financial stability"],
        "contact": "1-800-321-COOP",
        "discounts": {
            "vehiculo_ecologico": 0.09,
            "sin_accidentes": 0.14,
            "auto_nuevo": 0.06
        },
        "coverage_details": {
            "Cobertura Básica": [
                "Responsabilidad civil: hasta CAD$40,000", 
                "Protección contra accidentes", 
                "Cobertura para terceros"
            ],
            "Cobertura Adicional": [
                "Seguro contra colisión", 
                "Seguro a todo riesgo", 
                "Asistencia en carretera"
            ],
            "Beneficios Especiales": [
                "Descuentos grupales", 
                "Planes de pago flexibles", 
                "Procesamiento digital de reclamos"
            ]
        }
    },
    "RSA Canada": {
        "logo": "canada/rsa.png",
        "description": "RSA Canada is known for its comprehensive auto insurance solutions, providing extensive coverage options and reliable support.",
        "strengths": ["Extensive coverage", "Reliable claims support", "Competitive pricing"],
        "contact": "1-800-654-RSA",
        "discounts": {
            "vehiculo_ecologico": 0.07,
            "sin_accidentes": 0.13,
            "auto_nuevo": 0.05
        },
        "coverage_details": {
            "Cobertura Básica": [
                "Responsabilidad civil: hasta CAD$50,000", 
                "Cobertura médica", 
                "Beneficios en caso de accidente"
            ],
            "Cobertura Adicional": [
                "Seguro contra colisión", 
                "Seguro a todo riesgo", 
                "Reembolso por coche de alquiler"
            ],
            "Beneficios Especiales": [
                "Descuentos por telemetría", 
                "Ajustes de cobertura flexibles", 
                "Soporte 24/7"
            ]
        }
    },
    "Economical Insurance": {
        "logo": "hoyeon/eco.png",
        "description": "Economical Insurance provides cost-effective auto insurance with a focus on value and customer satisfaction.",
        "strengths": ["Affordable rates", "Comprehensive options", "Fast claim processing"],
        "contact": "1-800-987-ECO",
        "discounts": {
            "vehiculo_ecologico": 0.11,
            "sin_accidentes": 0.09,
            "auto_nuevo": 0.04
        },
        "coverage_details": {
            "Cobertura Básica": [
                "Responsabilidad civil: hasta CAD$40,000", 
                "Protección contra lesiones", 
                "Beneficios por accidentes"
            ],
            "Cobertura Adicional": [
                "Seguro contra colisión", 
                "Seguro a todo riesgo", 
                "Asistencia en carretera"
            ],
            "Beneficios Especiales": [
                "Descuento por conducción segura", 
                "Bonificación por no siniestros", 
                "Planes de pago flexibles"
            ]
        }
    },
    "Allstate Canada": {
        "logo": "hoyeon/all.png",
        "description": "Allstate Canada delivers reliable auto insurance with personalized service and a broad spectrum of coverage options.",
        "strengths": ["Personalized service", "Strong claims handling", "Multiple discount options"],
        "contact": "1-800-555-ALL",
        "discounts": {
            "vehiculo_ecologico": 0.10,
            "sin_accidentes": 0.11,
            "auto_nuevo": 0.05
        },
        "coverage_details": {
            "Cobertura Básica": [
                "Responsabilidad civil: hasta CAD$45,000", 
                "Beneficios médicos", 
                "Protección contra accidentes"
            ],
            "Cobertura Adicional": [
                "Seguro contra colisión", 
                "Seguro a todo riesgo", 
                "Reembolso por alquiler de vehículo"
            ],
            "Beneficios Especiales": [
                "Descuento por múltiples pólizas", 
                "Recompensas por fidelidad", 
                "Atención al cliente 24/7"
            ]
        }
    }
}

# Detalles de tipo de seguro en español (adaptado para Canadá)
insurance_type_details = {
    "Seguro Ecológico": {
        "description": "Seguro diseñado para vehículos ecológicos en Canadá, con cobertura especial para tecnologías verdes.",
        "price_range": "CAD$100 ~ CAD$150",
        "base_price": 200,
        "coverages": {
            "Cobertura Obligatoria": [
                "Cobertura de responsabilidad civil", 
                "Daños a terceros hasta CAD$50,000", 
                "Cobertura de lesiones personales hasta CAD$25,000"
            ],
            "Cobertura Ecológica": [
                "Cobertura para daños en sistemas eléctricos", 
                "Seguro para incidentes en cargadores", 
                "Soporte en reemplazo de componentes ecológicos", 
                "Servicio de asistencia para carga eléctrica"
            ],
            "Servicios Adicionales": [
                "Descuentos en centros de servicio ecológicos", 
                "Extensión de garantía para sistemas eléctricos", 
                "Programa de puntos por eficiencia energética"
            ]
        }
    },
    "Seguro Premium": {
        "description": "Paquete integral de seguro para vehículos de alta gama en Canadá, con opciones exclusivas para clientes exigentes.",
        "price_range": "CAD$150 ~ CAD$250",
        "base_price": 250,
        "coverages": {
            "Cobertura Obligatoria": [
                "Cobertura de responsabilidad civil", 
                "Daños a terceros hasta CAD$75,000", 
                "Cobertura de lesiones personales hasta CAD$30,000"
            ],
            "Cobertura Especial": [
                "Seguro a todo riesgo", 
                "Soporte para piezas originales", 
                "Servicio VIP de asistencia en carretera", 
                "Atención prioritaria en reclamaciones"
            ],
            "Servicios Complementarios": [
                "Línea de atención exclusiva 24/7", 
                "Vehículo de reemplazo mejorado", 
                "Cobertura internacional"
            ]
        }
    },
    "Seguro Estándar": {
        "description": "Seguro básico que ofrece coberturas esenciales para la mayoría de vehículos en Canadá.",
        "price_range": "CAD$80 ~ CAD$130",
        "base_price": 150,
        "coverages": {
            "Cobertura Obligatoria": [
                "Cobertura de responsabilidad civil", 
                "Daños a terceros hasta CAD$40,000", 
                "Cobertura de lesiones personales hasta CAD$20,000"
            ],
            "Cobertura Básica": [
                "Seguro contra daños parciales", 
                "Reducción de deducible", 
                "Servicio de asistencia en carretera"
            ],
            "Cobertura Opcional": [
                "Cobertura para accesorios", 
                "Pago adicional en gastos médicos", 
                "Soporte legal en caso de accidente"
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
    """Función para cargar los modelos de segmentación y clustering"""
    model_dir = Path(__file__).parent.parent / "models_mini1"
    segment_model_path = model_dir / "gb_model_hs.pkl"
    clustering_model_path = model_dir / "gb_pipeline_hc.pkl"

    if not segment_model_path.exists() or not clustering_model_path.exists():
        st.error("No se pudieron encontrar los archivos de modelo.")
        st.stop()

    return joblib.load(segment_model_path), joblib.load(clustering_model_path)

def input_customer_info():
    st.title("📋 Ingrese la información del cliente")
    
    segment_model, clustering_model = load_models()
    
    with st.form(key="customer_form"):
        st.subheader("1. Información Básica")
        col1, col2 = st.columns(2)
        with col1:
            sexo = st.selectbox("Sexo", ["Masculino", "Femenino"], key="sexo")
            fecha_nacimiento = st.date_input("Fecha de Nacimiento", 
                                    min_value=datetime(1900, 1, 1), 
                                    max_value=datetime.today().replace(year=datetime.today().year - 20),
                                    key="fecha_nacimiento")
        with col2:
            tipo_vehiculo = st.selectbox("Tipo de vehículo", ["Sedán compacto", "Sedán mediano", "Sedán grande", "SUV"], key="tipo_vehiculo")
            modelo_seleccionado = st.selectbox("Seleccione el modelo", list(launch_dates['Ford'].keys()), key="modelo_auto")
        
        st.subheader("2. Información de Compra")
        col1, col2 = st.columns(2)
        with col1:
            monto_transaccion = st.number_input("Presupuesto (CAD)", min_value=10000, step=1000, format="%d", key="presupuesto")
            frecuencia_compra = st.number_input("Frecuencia de compra", min_value=1, value=1, key="frecuencia")
        with col2:
            metodo_transaccion = st.selectbox("Método de pago", ["Tarjeta", "Efectivo", "Transferencia"], key="metodo_pago")
            fecha_compra = st.date_input("Fecha prevista de compra", key="fecha_compra")
        
        st.subheader("3. Información de Seguro")
        col1, col2, col3 = st.columns(3)
        with col1:
            experiencia_conduccion = st.selectbox("Experiencia de conducción", ["Menos de 1 año", "1-3 años", "3-5 años", "Más de 5 años"], key="experiencia")
        with col2:
            historial_accidentes = st.selectbox("Historial de accidentes (últimos 3 años)", ["Sin accidentes", "1 accidente", "2 accidentes", "3 o más accidentes"], key="accidentes")
        with col3:
            antiguedad_auto = st.selectbox("Antigüedad del vehículo", ["Nuevo", "1-3 años", "3-5 años", "5-7 años", "Más de 7 años"], key="antiguedad")
        
        submitted = st.form_submit_button("Obtener recomendación de seguro", use_container_width=True)
        
        if submitted:
            today = datetime.today()
            edad = today.year - fecha_nacimiento.year - ((today.month, today.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
            
            # Nota: Aunque la interfaz está en español, el modelo espera los nombres de columna en coreano.
            input_segmento = pd.DataFrame(
                [[metodo_transaccion, launch_dates['Ford'].get(modelo_seleccionado), 
                  fecha_compra, monto_transaccion, frecuencia_compra]],
                columns=['거래 방식', '제품 출시년월', '제품 구매 날짜', '거래 금액', '제품 구매 빈도']
            )
            segmento_cliente = segment_model.predict(input_segmento)[0]
            
            input_cluster = pd.DataFrame(
                [[sexo, tipo_vehiculo, metodo_transaccion, launch_dates['Ford'].get(modelo_seleccionado),
                  fecha_compra, segmento_cliente,
                  "Sí" if modelo_seleccionado in eco_friendly_models['Ford'] else "No",
                  edad, monto_transaccion, frecuencia_compra]],
                columns=['성별', '차량구분', '거래 방식', '제품 출시년월', 
                         '제품 구매 날짜', '고객 세그먼트', '친환경차',
                         '연령', '거래 금액', '제품 구매 빈도']
            )
            cluster_id = clustering_model.predict(input_cluster)[0]
            
            # Guardar estado de sesión (prefijo "car_insurance_")
            st.session_state.update({
                "car_insurance_step": 2,
                "car_insurance_cluster_id": cluster_id,
                "car_insurance_selected_vehicle": modelo_seleccionado,
                "car_insurance_experiencia": experiencia_conduccion,
                "car_insurance_accidentes": historial_accidentes,
                "car_insurance_antiguedad": antiguedad_auto,
                "car_insurance_sexo": sexo,
                "car_insurance_fecha_nacimiento": fecha_nacimiento,
                "car_insurance_transaction_amount": monto_transaccion,
                "car_insurance_purchase_frequency": frecuencia_compra,
                "car_insurance_car_type": tipo_vehiculo,
                "car_insurance_transaction_method": metodo_transaccion,
                "car_insurance_purchase_date": fecha_compra,
                "car_insurance_age": edad,
                "car_insurance_is_eco_friendly": modelo_seleccionado in eco_friendly_models['Ford']
            })
            
            st.rerun()

def Car_insurance_recommendation():
    st.title("🚗 Recomendación personalizada de seguros para autos en Canadá")
    
    cluster_id = st.session_state.get("car_insurance_cluster_id", 0)
    modelo_seleccionado = st.session_state.get("car_insurance_selected_vehicle", "")
    es_eco = st.session_state.get("car_insurance_is_eco_friendly", False)
    experiencia = st.session_state.get("car_insurance_experiencia", "3-5 años")
    historial = st.session_state.get("car_insurance_accidentes", "Sin accidentes")
    antiguedad = st.session_state.get("car_insurance_antiguedad", "Nuevo")
    
    # Sección: Compañías de seguros recomendadas
    with st.container():
        st.write("")
        st.write("")
        st.subheader("🏆 Compañías de seguros recomendadas")
        st.write("")
        
        recomendados = insurance_recommendations.get(cluster_id, ["Intact Insurance"])
        cols = st.columns(len(recomendados))
        
        for idx, comp in enumerate(recomendados):
            with cols[idx]:
                info = insurance_companies.get(comp, {})
                with st.container():
                    st.image(info.get("logo", ""), use_container_width=True)
                    st.markdown(f"<h3 style='margin-top: 0.5rem;'>{comp}</h3>", unsafe_allow_html=True)
                    st.markdown(f"<p style='color: #6c757d; font-size: 0.9rem;'>{info.get('description', '')}</p>", unsafe_allow_html=True)
                    st.markdown("<p style='margin-bottom: 0.5rem;'><strong>Puntos fuertes:</strong></p>", unsafe_allow_html=True)
                    for strength in info.get("strengths", []):
                        st.markdown(f"<p style='margin: 0.2rem 0; font-size: 0.9rem;'>✓ {strength}</p>", unsafe_allow_html=True)
                    if comp == "Intact Insurance":
                        st.markdown('<div class="highlight" style="font-size: 0.9rem;">✅ Descuento especial para clientes de autos modernos</div>', unsafe_allow_html=True)
                    st.markdown(f"<p style='margin-top: 1rem; margin-bottom: 0;'><strong>Contacto:</strong> 📞 {info.get('contact', '')}</p>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
    
    # Sección: Tipo de seguro recomendado
    with st.container():
        st.subheader("🔍 Tipos de seguro recomendados")
        
        if es_eco:
            tipo_seguro = "Seguro Ecológico"
            eco_badge = '<span class="eco-badge">Ecológico</span>'
        elif cluster_id in [1, 3]:
            tipo_seguro = "Seguro Premium"
            eco_badge = '<span class="premium-badge">Premium</span>'
        else:
            tipo_seguro = "Seguro Estándar"
            eco_badge = ''
        
        tipo_info = insurance_type_details.get(tipo_seguro, {})
        
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f"<h3 style='display: flex; align-items: center;'>{tipo_seguro}{eco_badge}</h3>", unsafe_allow_html=True)
            st.markdown(f"<p>{tipo_info.get('description', '')}</p>", unsafe_allow_html=True)
            st.markdown(f"<p><strong>Prima mensual estimada:</strong> <span style='color: #0d6efd; font-weight: bold;'>{tipo_info.get('price_range', '')}</span></p>", unsafe_allow_html=True)
            tab1, tab2, tab3 = st.tabs(list(tipo_info.get("coverages", {}).keys()))
            for tab, (categoria, items) in zip([tab1, tab2, tab3], tipo_info.get("coverages", {}).items()):
                with tab:
                    st.markdown(f"<div class='coverage-category'>{categoria}</div>", unsafe_allow_html=True)
                    for item in items:
                        st.markdown(f"<div class='coverage-item'>• {item}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    
    # Sección: Cálculo estimado de la prima
    with st.container():
        st.subheader("📊 Cálculo estimado de la prima")
        
        def calcular_precio_seguro(precio_base):
            factores = {
                "experiencia": {
                    "Menos de 1 año": 1.2, "1-3 años": 1.1, "3-5 años": 1.0, "Más de 5 años": 0.9
                },
                "accidentes": {
                    "Sin accidentes": 0.85, "1 accidente": 1.0, "2 accidentes": 1.2, "3 o más accidentes": 1.5
                },
                "antiguedad": {
                    "Nuevo": 1.1, "1-3 años": 1.0, "3-5 años": 0.95, "5-7 años": 0.9, "Más de 7 años": 0.8
                }
            }
            precio = precio_base
            precio *= factores["experiencia"][experiencia]
            precio *= factores["accidentes"][historial]
            precio *= factores["antiguedad"][antiguedad]
            return int(precio)
        
        precios_seguros = {}
        for comp in recomendados:
            info = insurance_companies.get(comp, {})
            precio_base = tipo_info.get("base_price", 150)
            temp = calcular_precio_seguro(precio_base)
            descuentos = info.get("discounts", {})
            if es_eco:
                temp *= (1 - descuentos.get("vehiculo_ecologico", 0))
            if historial == "Sin accidentes":
                temp *= (1 - descuentos.get("sin_accidentes", 0))
            if antiguedad == "Nuevo":
                temp *= (1 - descuentos.get("auto_nuevo", 0))
            precios_seguros[comp] = int(temp)
        
        precio_min = min(precios_seguros.values())
        precio_max = max(precios_seguros.values())
        
        st.markdown(f"""
        <div class="highlight">
            <h4 style='margin: 0; color: #0d6efd;'>Rango estimado de la prima mensual</h4>
            <p style='font-size: 1.5rem; font-weight: bold; margin: 0.5rem 0;'>
                CAD$ {precio_min:,} ~ CAD$ {precio_max:,}
            </p>
            <p style='font-size: 0.9rem; margin: 0;'>* Estimación basada en el perfil del cliente y la información del vehículo.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("🔍 Detalles de cobertura por compañía")
        
        for comp, precio in precios_seguros.items():
            with st.expander(f"{comp} - Prima estimada: CAD$ {precio:,}", expanded=True):
                info = insurance_companies.get(comp, {})
                descuentos_aplicados = []
                ins_descuentos = info.get("discounts", {})
                if es_eco and ins_descuentos.get("vehiculo_ecologico", 0) > 0:
                    descuentos_aplicados.append(f"Descuento ecológico {ins_descuentos['vehiculo_ecologico']*100:.0f}%")
                if historial == "Sin accidentes" and ins_descuentos.get("sin_accidentes", 0) > 0:
                    descuentos_aplicados.append(f"Descuento por sin accidentes {ins_descuentos['sin_accidentes']*100:.0f}%")
                if antiguedad == "Nuevo" and ins_descuentos.get("auto_nuevo", 0) > 0:
                    descuentos_aplicados.append(f"Descuento por auto nuevo {ins_descuentos['auto_nuevo']*100:.0f}%")
                if descuentos_aplicados:
                    st.markdown(f"<p><strong>Descuentos aplicados:</strong> {', '.join(descuentos_aplicados)}</p>", unsafe_allow_html=True)
                tabs = st.tabs(list(info.get("coverage_details", {}).keys()))
                for tab, (categoria, items) in zip(tabs, info.get("coverage_details", {}).items()):
                    with tab:
                        st.markdown(f"<div class='coverage-category'>{categoria}</div>", unsafe_allow_html=True)
                        for item in items:
                            st.markdown(f"<div class='coverage-item'>• {item}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='margin-top: 1rem;'><strong>Teléfono de contacto:</strong> 📞 {info.get('contact', '')}</div>", unsafe_allow_html=True)
    
    if st.button("Reiniciar entrada", use_container_width=True):
        st.session_state["car_insurance_step"] = 1
        st.rerun()

def run_car_customer_ca():
    load_css()
    
    if "car_insurance_step" not in st.session_state:
        st.session_state["car_insurance_step"] = 1
    
    if st.session_state["car_insurance_step"] == 1:
        input_customer_info()
    elif st.session_state["car_insurance_step"] == 2:
        Car_insurance_recommendation()

if __name__ == "__main__":
    run_car_customer_ca()
