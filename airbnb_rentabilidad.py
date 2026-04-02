import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- 1. CONFIGURACIÓN Y SEGURIDAD ---
st.set_page_config(page_title="Rentabilidad Airbnb | Jancarlo Mendoza", layout="wide")

# Función de seguridad simple
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.title("🔐 Acceso Restringido")
            password = st.text_input("Ingrese la contraseña de consultoría:", type="password")
            if st.button("Ingresar"):
                if password == "Jancarlo2026": # Puedes cambiar esta contraseña
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Contraseña incorrecta.")
        return False
    return True

if check_password():
    # Estilos CSS personalizados
    st.markdown("""
        <style>
        .main { background-color: #0e1117; }
        [data-testid="stMetricValue"] { color: #ffffff !important; font-size: 1.8rem !important; }
        .stNumberInput div div input { color: white !important; }
        .card-renta {
            background-color: #1f2630;
            padding: 20px;
            border-radius: 12px;
            border-left: 5px solid #3b82f6;
            margin-bottom: 20px;
        }
        .break-even {
            background: linear-gradient(135deg, #1e3a8a, #1e40af);
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            border: 1px solid #3b82f6;
        }
        </style>
        """, unsafe_allow_html=True)

    # --- 2. SIDEBAR - INPUTS ---
    with st.sidebar:
        st.header("📊 Parámetros de Inversión")
        precio_depa = st.number_input("Precio del Departamento (S/.)", min_value=100000, value=250000, step=10000)
        tarifa_diaria = st.number_input("Tarifa Diaria Promedio (S/.)", min_value=50, value=180)
        tcea = st.number_input("TCEA (%)", min_value=1.0, max_value=25.0, value=9.0, step=0.1)
        plazo_anios = st.selectbox("Plazo de Financiamiento (Años)", [10, 15, 20, 25], index=2)
        
        st.write("---")
        st.caption("Desarrollado por: Ing. Jancarlo Mendoza")

    # --- 3. LÓGICA DE CÁLCULO ---
    # Conceptos Iniciales
    inicial = precio_depa * 0.20
    prestamo = precio_depa - inicial
    
    # Cálculo Cuota Hipotecaria
    tem = (1 + tcea/100)**(1/12) - 1
    n_cuotas = plazo_anios * 12
    cuota_mensual = prestamo * (tem * (1 + tem)**n_cuotas) / ((1 + tem)**n_cuotas - 1)
    
    # Gastos Fijos y Operativos
    gastos_anuales_fijos = precio_depa * 0.03 # Mantenimiento, arbitrios, predial, etc.
    cuota_anual = cuota_mensual * 12
    
    # Escenario Base (20 días/mes)
    dias_ocupados_base = 20 * 12
    ingreso_anual_base = tarifa_diaria * dias_ocupados_base
    gastos_airbnb_base = ingreso_anual_base * 0.15
    utilidad_neta_base = ingreso_anual_base - cuota_anual - gastos_airbnb_base - gastos_anuales_fijos
    roi_anual_base = (utilidad_neta_base / inicial) * 100

    # Break-Even Mensual (Días necesarios para pagar TODO el mes)
    # Ecuación: (Tarifa * Días * 0.85) - Cuota Mensual - (Gasto Fijo / 12) = 0
    gastos_fijos_mes = gastos_anuales_fijos / 12
    dias_punto_equilibrio = (cuota_mensual + gastos_fijos_mes) / (tarifa_diaria * 0.85)

    # --- 4. INTERFAZ PRINCIPAL ---
    st.title("🚀 Análisis de Rentabilidad Airbnb")
    st.write(f"Inversión para departamento de **S/. {precio_depa:,.0f}**")

    # Fila 1: Métricas de Financiamiento
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Inicial (20%)", f"S/. {inicial:,.0f}")
    m2.metric("Préstamo", f"S/. {prestamo:,.0f}")
    m3.metric("Cuota Mensual", f"S/. {cuota_mensual:,.2f}")
    m4.metric("TCEA", f"{tcea}%")

    st.write("---")

    # Fila 2: Escenario Base y Punto de Equilibrio
    col_main, col_be = st.columns([2, 1])
    
    with col_main:
        st.subheader("📍 Escenario Base (Ocupación: 20 días/mes)")
        st.markdown(f"""
        <div class="card-renta">
            <table style="width:100%; color:white;">
                <tr><td>Ingresos Anuales:</td><td style="text-align:right;">S/. {ingreso_anual_base:,.2f}</td></tr>
                <tr><td>Cuota Bancaria Anual:</td><td style="text-align:right; color:#ff4b4b;">- S/. {cuota_anual:,.2f}</td></tr>
                <tr><td>Comisiones Airbnb (15%):</td><td style="text-align:right; color:#ff4b4b;">- S/. {gastos_airbnb_base:,.2f}</td></tr>
                <tr><td>Mantenimiento/Impuestos (3%):</td><td style="text-align:right; color:#ff4b4b;">- S/. {gastos_anuales_fijos:,.2f}</td></tr>
                <tr style="font-weight:bold; font-size:1.2rem; border-top:1px solid #555;">
                    <td style="padding-top:10px;">Utilidad Neta Anual:</td>
                    <td style="text-align:right; padding-top:10px; color:#28a745;">S/. {utilidad_neta_base:,.2f}</td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        st.metric("ROI sobre la Inicial", f"{roi_anual_base:.2f}%", help="Utilidad Neta / Cuota Inicial")

    with col_be:
        st.subheader("🎯 Punto de Equilibrio")
        st.markdown(f"""
        <div class="break-even">
            <p style="font-size: 1rem; margin-bottom: 0;">Días mínimos al mes para cubrir gastos:</p>
            <h1 style="font-size: 3.5rem; margin: 0; color: #60a5fa;">{np.ceil(dias_punto_equilibrio):.0f}</h1>
            <p style="font-size: 0.9rem; opacity: 0.8;">Noches ocupadas / mes</p>
        </div>
        """, unsafe_allow_html=True)
        st.info(f"A partir de la noche {np.ceil(dias_punto_equilibrio) + 1:.0f}, todo es utilidad neta.")

    # --- 5. ANÁLISIS DE SENSIBILIDAD ---
    st.write("---")
    st.subheader("📈 Análisis de Sensibilidad (Ocupación)")
    
    # Crear datos de sensibilidad
    rangos_ocupacion = [10, 15, 20, 25, 28]
    data_sens = []
    for dias in rangos_ocupacion:
        ingreso = tarifa_diaria * dias * 12
        utilidad = ingreso - cuota_anual - (ingreso * 0.15) - gastos_anuales_fijos
        roi = (utilidad / inicial) * 100
        data_sens.append({"Días/Mes": dias, "Utilidad Anual": utilidad, "ROI %": round(roi, 2)})
    
    df_sens = pd.DataFrame(data_sens)
    
    c1, c2 = st.columns([1, 2])
    with c1:
        st.dataframe(df_sens.style.format({"Utilidad Anual": "S/. {:,.2f}", "ROI %": "{:.2f}%"}), use_container_width=True)
    
    with c2:
        fig = px.line(df_sens, x="Días/Mes", y="ROI %", title="Impacto de la Ocupación en el ROI",
                     markers=True, text="ROI %")
        fig.update_traces(textposition="top left", line_color='#3b82f6')
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig, use_container_width=True)

    if st.button("✅ Finalizar Simulación"):
        st.balloons()
        st.success("Análisis completado exitosamente.")
