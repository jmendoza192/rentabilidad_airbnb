import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- 1. CONFIGURACIÓN Y SEGURIDAD ---
st.set_page_config(page_title="Airbnb vs Tradicional | Jancarlo Mendoza", layout="wide")

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.title("🔐 Acceso Consultoría")
            password = st.text_input("Contraseña:", type="password")
            if st.button("Ingresar"):
                if password == "Jancarlo2026":
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Acceso denegado.")
        return False
    return True

if check_password():
    # Estilos CSS
    st.markdown("""
        <style>
        .main { background-color: #0e1117; }
        .stMetric { background-color: #1f2630; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
        .comparison-card { padding: 20px; border-radius: 15px; margin-bottom: 20px; border: 1px solid #3b82f6; }
        .vs-text { font-size: 1.5rem; font-weight: bold; text-align: center; color: #ff4b4b; margin: 20px 0; }
        </style>
        """, unsafe_allow_html=True)

    # --- 2. SIDEBAR - INPUTS MEJORADOS ---
    with st.sidebar:
        st.header("📊 Variables del Proyecto")
        precio_depa = st.number_input("Precio Inmueble (S/.)", value=250000, step=10000)
        tcea = st.number_input("TCEA (%)", value=9.5, step=0.1)
        plazo = st.selectbox("Plazo (Años)", [10, 15, 20, 25], index=2)
        
        st.write("---")
        st.subheader("🏠 Configuración Airbnb")
        tarifa_dia = st.number_input("Tarifa Diaria (S/.)", value=180)
        dias_simulados = st.slider("Días ocupados al mes", 1, 30, 20)
        
        st.subheader("🏢 Configuración Tradicional")
        renta_mensual = st.number_input("Alquiler Mensual Fijo (S/.)", value=1800)
        
        st.caption("Estrategia Integral - Jancarlo Mendoza")

    # --- 3. CÁLCULOS FINANCIEROS BASE ---
    inicial = precio_depa * 0.20
    prestamo = precio_depa - inicial
    tem = (1 + tcea/100)**(1/12) - 1
    n_cuotas = plazo * 12
    cuota_mes = prestamo * (tem * (1 + tem)**n_cuotas) / ((1 + tem)**n_cuotas - 1)
    gastos_fijos_anuales = precio_depa * 0.03 # Predial, arbitrios, mantenimiento

    # Cálculos Airbnb
    ingreso_anual_air = tarifa_dia * dias_simulados * 12
    gastos_operativos_air = (ingreso_anual_air * 0.15) + gastos_fijos_anuales
    utilidad_air = ingreso_anual_air - (cuota_mes * 12) - (ingreso_anual_air * 0.15) - gastos_fijos_anuales
    roi_air = (utilidad_air / inicial) * 100

    # Cálculos Tradicional
    ingreso_anual_trad = renta_mensual * 12
    # El alquiler tradicional suele tener menos gastos (solo predial/arbitrios), asumimos 1.5% del valor del inmueble
    gastos_trad = precio_depa * 0.015 
    utilidad_trad = ingreso_anual_trad - (cuota_mes * 12) - gastos_trad
    roi_trad = (utilidad_trad / inicial) * 100

    # --- 4. INTERFAZ PRINCIPAL ---
    st.title("⚖️ Airbnb vs. Alquiler Tradicional")
    
    # KPIs Rápidos
    k1, k2, k3 = st.columns(3)
    k1.metric("Inversión Inicial (20%)", f"S/. {inicial:,.0f}")
    k2.metric("Cuota Hipotecaria", f"S/. {cuota_mes:,.2f}")
    k3.metric("Monto del Préstamo", f"S/. {prestamo:,.0f}")

    st.write("---")

    # SECCIÓN: ANALISIS ROI AJUSTADO
    st.subheader(f"📈 Análisis ROI Personalizado ({dias_simulados} días/mes)")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Utilidad Neta Airbnb", f"S/. {utilidad_air:,.2f}", delta=f"{roi_air:.2f}% ROI")
    with c2:
        st.metric("Utilidad Neta Tradicional", f"S/. {utilidad_trad:,.2f}", delta=f"{roi_trad:.2f}% ROI", delta_color="normal")
    with c3:
        breakeven_dias = (cuota_mes + (gastos_fijos_anuales/12)) / (tarifa_dia * 0.85)
        st.metric("Punto de Equilibrio", f"{np.ceil(breakeven_dias):.0f} noches", "Mínimo/mes")

    # SECCIÓN: COMPARATIVA VISUAL
    st.write("---")
    st.subheader("🔄 Duelo de Modelos de Negocio")
    
    col_air, col_vs, col_trad = st.columns([2, 0.5, 2])
    
    with col_air:
        st.markdown(f"""
        <div style="background-color:#1e3a8a; padding:20px; border-radius:10px; border:1px solid #3b82f6;">
            <h4>MODELO AIRBNB</h4>
            <p>Ingreso Bruto: S/. {ingreso_anual_air:,.0f}</p>
            <p>Gastos Operativos (15%): -S/. {ingreso_anual_air*0.15:,.0f}</p>
            <p style="font-size:1.2rem; font-weight:bold;">ROI: {roi_air:.2f}%</p>
        </div>
        """, unsafe_allow_html=True)

    with col_vs:
        st.markdown('<div class="vs-text">VS</div>', unsafe_allow_html=True)

    with col_trad:
        st.markdown(f"""
        <div style="background-color:#064e3b; padding:20px; border-radius:10px; border:1px solid #10b981;">
            <h4>ALQUILER TRADICIONAL</h4>
            <p>Ingreso Bruto: S/. {ingreso_anual_trad:,.0f}</p>
            <p>Gastos (Vacancia/Mant.): -S/. {gastos_trad:,.0f}</p>
            <p style="font-size:1.2rem; font-weight:bold;">ROI: {roi_trad:.2f}%</p>
        </div>
        """, unsafe_allow_html=True)

    # SECCIÓN: FLUJO DE CAJA ACUMULADO Y GRÁFICO
    st.write("---")
    st.subheader("📅 Proyección de Flujo de Caja (Año 1)")
    
    meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    flujo_mensual = (ingreso_anual_air / 12) - cuota_mes - (ingreso_anual_air * 0.15 / 12) - (gastos_fijos_anuales / 12)
    
    acumulado = []
    current = 0
    for m in meses:
        current += flujo_mensual
        acumulado.append(current)
        
    fig_flow = go.Figure()
    fig_flow.add_trace(go.Scatter(x=meses, y=acumulado, fill='tozeroy', 
                                 line=dict(color='#3b82f6', width=4),
                                 name="Flujo Acumulado"))
    
    # Línea de Cero
    fig_flow.add_shape(type="line", x0=0, y0=0, x1=11, y1=0, 
                       line=dict(color="red", width=2, dash="dash"))
    
    fig_flow.update_layout(title="Acumulado de Utilidad Neta (Airbnb)",
                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                          font_color="white", yaxis_title="Soles (S/.)")
    
    st.plotly_chart(fig_flow, use_container_width=True)
    
    if acumulado[-1] > 0:
        st.success(f"✅ **Proyecto Rentable:** Al finalizar el año 1 habrás generado **S/. {acumulado[-1]:,.2f}** de flujo de caja positivo.")
    else:
        st.error(f"⚠️ **Atención:** En este escenario, el proyecto cierra el año con un déficit de **S/. {acumulado[-1]:,.2f}**. Revisa la tarifa o aumenta los días de ocupación.")

    # Variables de Interés adicionales
    with st.expander("🔍 Otras Variables de Interés"):
        st.write(f"**Plusvalía Estimada (5% anual):** S/. {precio_depa * 0.05:,.2f}")
        st.write(f"**Pago a Capital en Año 1:** S/. {(cuota_mes * 12) - (prestamo * (tcea/100)):,.2f} (Ahorro indirecto)")
        st.write(f"**Carga de Deuda Mensual:** {((cuota_mes / 6000) * 100):.1f}% (Basado en ingreso referencial de S/ 6k)")

    if st.button("Finalizar Auditoría"):
        st.balloons()
