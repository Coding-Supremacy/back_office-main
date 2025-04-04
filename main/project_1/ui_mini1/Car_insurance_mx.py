import os
import time
import streamlit as st
import pandas as pd
import joblib
from datetime import datetime
from pathlib import Path
import base64
import requests

# 보험 이메일 발송 모듈 (별도 구현했다고 가정)
import project_1.ui_mini1.mini1_promo_email as promo_email

def get_abs_path(relative_path):
    """상대 경로를 절대 경로로 변환"""
    return Path(__file__).parent.parent / relative_path

# 모델과 출시 년월 데이터 (자동차 관련은 그대로 사용)
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

# 클러스터별 보험사 추천 (멕시코 시장용 예시)
insurance_recommendations = {
    0: ["AXA Seguros", "GNP Seguros"],
    1: ["AXA Seguros", "Qualitas"],
    2: ["AXA Seguros", "Mapfre México"],
    3: ["AXA Seguros", "HDI Seguros"],
    4: ["AXA Seguros", "Chubb México"],
    5: ["AXA Seguros", "Zurich México"]
}

# 보험사 상세 정보 (멕시코 시장용 예시)
insurance_companies = {
    "AXA Seguros": {
        "logo": "hoyeon/axa.png",
        "description": "AXA Seguros es líder en seguros de autos en México, ofreciendo cobertura integral y atención personalizada.",
        "strengths": ["Descuentos exclusivos para autos modernos", "Red nacional de servicios", "Atención 24/7"],
        "contact": "01-800-123-4567",
        "discounts": {
            "vehiculo_ecologico": 0.15,
            "sin_accidentes": 0.10,
            "auto_nuevo": 0.05
        },
        "coverage_details": {
            "Cobertura Básica": ["Responsabilidad Civil Ilimitada", "Daños a terceros hasta 2 millones MXN", "Cobertura de lesiones personales hasta 1 millón MXN"],
            "Cobertura Adicional": ["Seguro contra robo y colisión", "Asistencia en carretera", "Reembolso de gastos por alquiler de auto"],
            "Beneficios Especiales": ["Descuentos en talleres AXA", "Atención preferencial en centros autorizados", "Plan de pagos flexible"]
        }
    },
    "GNP Seguros": {
        "logo": "hoyeon/gnp.png",
        "description": "GNP Seguros ofrece soluciones confiables y rápidas en seguros de autos con una amplia red de atención en todo México.",
        "strengths": ["Amplia red de talleres", "Proceso de reclamaciones eficiente", "Beneficios para clientes sin accidentes"],
        "contact": "01-800-234-5678",
        "discounts": {
            "vehiculo_ecologico": 0.10,
            "sin_accidentes": 0.15,
            "auto_nuevo": 0.03
        },
        "coverage_details": {
            "Cobertura Básica": ["Responsabilidad Civil Ilimitada", "Daños a terceros hasta 3 millones MXN", "Cobertura de lesiones personales hasta 800,000 MXN"],
            "Cobertura Adicional": ["Seguro a todo riesgo", "Asistencia legal", "Servicio de grúa 24/7"],
            "Beneficios Especiales": ["Descuentos en seguros múltiples", "Programa de recompensas por sin accidentes", "Atención personalizada vía app móvil"]
        }
    },
    "Qualitas": {
        "logo": "hoyeon/qa.png",
        "description": "Qualitas es una de las aseguradoras más reconocidas en México, destacándose por su innovación y servicio al cliente.",
        "strengths": ["Ofertas personalizadas", "Tecnología avanzada en reclamaciones", "Atención rápida y eficiente"],
        "contact": "01-800-345-6789",
        "discounts": {
            "vehiculo_ecologico": 0.12,
            "sin_accidentes": 0.12,
            "auto_nuevo": 0.04
        },
        "coverage_details": {
            "Cobertura Básica": ["Responsabilidad Civil Ilimitada", "Daños a terceros hasta 2.5 millones MXN", "Cobertura de lesiones personales hasta 700,000 MXN"],
            "Cobertura Adicional": ["Reducción de deducible", "Reembolso de gastos médicos", "Asistencia vial"],
            "Beneficios Especiales": ["Beneficios financieros en conjunto", "Descuentos en gasolina", "Plan de ahorro en seguros"]
        }
    },
    "Mapfre México": {
        "logo": "hoyeon/mapf.png",
        "description": "Mapfre México ofrece seguros con cobertura amplia y servicios digitales para una experiencia sin complicaciones.",
        "strengths": ["Cobertura digital completa", "Atención en línea 24/7", "Red de talleres de confianza"],
        "contact": "01-800-456-7890",
        "discounts": {
            "vehiculo_ecologico": 0.13,
            "sin_accidentes": 0.13,
            "auto_nuevo": 0.05
        },
        "coverage_details": {
            "Cobertura Básica": ["Responsabilidad Civil Ilimitada", "Daños a terceros hasta 2 millones MXN", "Cobertura de lesiones personales hasta 600,000 MXN"],
            "Cobertura Adicional": ["Seguro contra robo", "Servicio de asistencia en carretera", "Reembolso por gastos médicos"],
            "Beneficios Especiales": ["Descuentos en mantenimiento", "Atención exclusiva por chat", "Beneficios digitales"]
        }
    },
    "HDI Seguros": {
        "logo": "hoyeon/hd.png",
        "description": "HDI Seguros se distingue por su atención personalizada y procesos de reclamación ágiles, ideal para clientes exigentes.",
        "strengths": ["Proceso de reclamación ágil", "Cobertura adaptada a cada cliente", "Atención personalizada"],
        "contact": "01-800-567-8901",
        "discounts": {
            "vehiculo_ecologico": 0.10,
            "sin_accidentes": 0.10,
            "auto_nuevo": 0.05
        },
        "coverage_details": {
            "Cobertura Básica": ["Responsabilidad Civil Ilimitada", "Daños a terceros hasta 2 millones MXN", "Cobertura de lesiones personales hasta 900,000 MXN"],
            "Cobertura Adicional": ["Seguro integral de auto", "Asistencia vial completa", "Servicio de grúa sin costo"],
            "Beneficios Especiales": ["Programa de lealtad HDI", "Descuentos en servicios de reparación", "Atención prioritaria"]
        }
    },
    "Chubb México": {
        "logo": "hoyeon/ch.png",
        "description": "Chubb México es conocido por sus altos niveles de seguridad y servicio al cliente, ofreciendo soluciones a medida.",
        "strengths": ["Altos límites de cobertura", "Servicio de atención 24/7", "Proceso digital sin papeles"],
        "contact": "01-800-678-9012",
        "discounts": {
            "vehiculo_ecologico": 0.15,
            "sin_accidentes": 0.15,
            "auto_nuevo": 0.07
        },
        "coverage_details": {
            "Cobertura Básica": ["Responsabilidad Civil Ilimitada", "Daños a terceros hasta 2 millones MXN", "Cobertura de lesiones personales hasta 500,000 MXN"],
            "Cobertura Adicional": ["Seguro a todo riesgo", "Asistencia en viaje", "Reembolso por gastos imprevistos"],
            "Beneficios Especiales": ["Descuentos por contratación múltiple", "Programa de seguridad vial", "Atención al cliente premium"]
        }
    },
    "Zurich México": {
        "logo": "hoyeon/zu.png",
        "description": "Zurich México ofrece soluciones integrales con atención global y soporte local especializado.",
        "strengths": ["Cobertura global con atención local", "Innovación en procesos digitales", "Amplia red de servicios"],
        "contact": "01-800-789-0123",
        "discounts": {
            "vehiculo_ecologico": 0.10,
            "sin_accidentes": 0.10,
            "auto_nuevo": 0.05
        },
        "coverage_details": {
            "Cobertura Básica": ["Responsabilidad Civil Ilimitada", "Daños a terceros hasta 3 millones MXN", "Cobertura de lesiones personales hasta 800,000 MXN"],
            "Cobertura Adicional": ["Seguro contra robo y colisión", "Asistencia legal", "Servicio de grúa 24/7"],
            "Beneficios Especiales": ["Descuentos en renovación", "Atención en línea personalizada", "Programa de prevención de accidentes"]
        }
    }
}

# Detalles de tipo de seguro en español
insurance_type_details = {
    "Seguro Ecológico": {
        "description": "Seguro diseñado exclusivamente para vehículos ecológicos, con cobertura especial para baterías y sistemas de carga.",
        "price_range": "15~25 MXN (miles)",
        "base_price": 200000,
        "coverages": {
            "Cobertura Obligatoria": [
                "Responsabilidad Civil Ilimitada",
                "Daños a terceros hasta 2 millones MXN",
                "Cobertura de lesiones personales hasta 1 millón MXN"
            ],
            "Cobertura Ecológica": [
                "Cobertura para daños en baterías de alto voltaje",
                "Seguro para accidentes en cargadores eléctricos",
                "Apoyo en reemplazo de piezas específicas para autos eléctricos",
                "Servicio de carga de emergencia"
            ],
            "Servicios Adicionales": [
                "Descuentos en centros de servicio para vehículos ecológicos",
                "Extensión de garantía para baterías",
                "Acumulación de puntos por reducción de emisiones"
            ]
        }
    },
    "Seguro Premium": {
        "description": "Paquete integral de seguro para vehículos de alta gama y clientes exigentes.",
        "price_range": "20~30 MXN (miles)",
        "base_price": 250000,
        "coverages": {
            "Cobertura Obligatoria": [
                "Responsabilidad Civil Ilimitada",
                "Daños a terceros hasta 3 millones MXN",
                "Cobertura de lesiones personales hasta 1 millón MXN"
            ],
            "Cobertura Especial": [
                "Seguro a todo riesgo (incluye robo, colisión y otros daños)",
                "Soporte en reemplazo de piezas originales (OEM)",
                "Servicio VIP de asistencia en carretera",
                "Atención prioritaria en reclamaciones"
            ],
            "Servicios Complementarios": [
                "Línea exclusiva de atención 24/7",
                "Opción de vehículo de reemplazo mejorado",
                "Soporte internacional en caso de accidente"
            ]
        }
    },
    "Seguro Estándar": {
        "description": "Seguro básico que ofrece coberturas esenciales para la mayoría de los vehículos.",
        "price_range": "10~20 MXN (miles)",
        "base_price": 150000,
        "coverages": {
            "Cobertura Obligatoria": [
                "Responsabilidad Civil Ilimitada",
                "Daños a terceros hasta 2 millones MXN",
                "Cobertura de lesiones personales hasta 500,000 MXN"
            ],
            "Cobertura Básica": [
                "Seguro contra daños parciales",
                "Reducción de deducible en colisiones",
                "Servicio de asistencia en carretera"
            ],
            "Cobertura Opcional": [
                "Cobertura para accesorios del vehículo",
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
            modelo_seleccionado = st.selectbox("Seleccione el modelo", list(launch_dates['현대'].keys()), key="modelo_auto")
        
        st.subheader("2. Información de Compra")
        col1, col2 = st.columns(2)
        with col1:
            monto_transaccion = st.number_input("Presupuesto (MXN)", min_value=10000000, step=1000000, format="%d", key="presupuesto")
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
            
            # Nota: A pesar de que la interfaz está en español, el modelo espera los nombres de columna en coreano.
            # Por ello, usamos los siguientes nombres de columna:
            # '거래 방식', '제품 출시년월', '제품 구매 날짜', '거래 금액', '제품 구매 빈도'
            input_segmento = pd.DataFrame(
                [[metodo_transaccion, launch_dates['현대'].get(modelo_seleccionado), 
                  fecha_compra, monto_transaccion, frecuencia_compra]],
                columns=['거래 방식', '제품 출시년월', '제품 구매 날짜', '거래 금액', '제품 구매 빈도']
            )
            segmento_cliente = segment_model.predict(input_segmento)[0]
            
            input_cluster = pd.DataFrame(
                [[sexo, tipo_vehiculo, metodo_transaccion, launch_dates['현대'].get(modelo_seleccionado),
                  fecha_compra, segmento_cliente,
                  "Sí" if modelo_seleccionado in eco_friendly_models['현대'] else "No",
                  edad, monto_transaccion, frecuencia_compra]],
                columns=['성별', '차량구분', '거래 방식', '제품 출시년월', 
                         '제품 구매 날짜', '고객 세그먼트', '친환경차',
                         '연령', '거래 금액', '제품 구매 빈도']
            )
            cluster_id = clustering_model.predict(input_cluster)[0]
            
            # Guardar estado de sesión (usando prefijo "car_insurance_")
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
                "car_insurance_is_eco_friendly": modelo_seleccionado in eco_friendly_models['현대']
            })
            
            st.rerun()

def Car_insurance_recommendation():
    st.title("🚗 Recomendación personalizada de seguros para autos mexicanos")
    
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
        
        recomendados = insurance_recommendations.get(cluster_id, ["AXA Seguros"])
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
                    if comp == "AXA Seguros":
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
            precio_base = tipo_info.get("base_price", 150000)
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
                {precio_min:,}₩ ~ {precio_max:,}₩
            </p>
            <p style='font-size: 0.9rem; margin: 0;'>* Esta es una estimación basada en el perfil del cliente y la información del vehículo.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("🔍 Detalles de cobertura por compañía")
        
        for comp, precio in precios_seguros.items():
            with st.expander(f"{comp} - Prima estimada: {precio:,}₩", expanded=True):
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

def run_car_customer_mx():
    load_css()
    
    if "car_insurance_step" not in st.session_state:
        st.session_state["car_insurance_step"] = 1
    
    if st.session_state["car_insurance_step"] == 1:
        input_customer_info()
    elif st.session_state["car_insurance_step"] == 2:
        Car_insurance_recommendation()

if __name__ == "__main__":
    run_car_customer_mx()
