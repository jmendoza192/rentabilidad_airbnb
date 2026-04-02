import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# --- 1. CONFIGURACIÓN Y SEGURIDAD ---
st.set_page_config(page_title="ROI Airbnb Pro | Jancarlo Mendoza", layout="wide")

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
                else: st.error("Acceso denegado.")
        return False
    return True

if check_password():
    # CSS para reducir tamaño de tarjetas y fuentes
    st.markdown("""
        <style>
        .main { background-color: #0e1117; }
        [data-testid="stMetricValue"] { font-size: 1.4rem !important; }
        [data-testid="stMetricLabel"] { font-size: 0.8rem !important; }
        div[data-testid="stMetric"] { background-color: #1f2630; padding: 10px; border-radius: 8px; }
        .mini-card { padding: 12px; border-radius: 8px; border: 1px solid #30363d; margin-bottom: 10px; font-size: 0.85rem; }
        .stSlider { padding-top: 0rem; }
        </style>
        """, unsafe_allow_html=True)

    # --- 2. SIDEBAR COMPACTO ---
    with st.sidebar:
        st.subheader("🏦 Financiamiento")
        val_depa = st.number_input("Precio Depa", value=250000)
        tcea = st.number_input("TCEA %", value=9.5)
        plazo = st.selectbox("Años", [10, 15, 20, 25], index=2)
        
        st.subheader("🏠 Operación Airbnb")
        tarifa = st.number_input("Tarifa/Día (S/.)", value=180)
        ocupacion_act = st.slider("Ocupación mensual (Días)", 1, 30, 20)
        
        st.subheader("🏢 Tradicional")
        renta_trad = st.number_input("Renta mensual fija", value=1800)

    # --- 3. LÓGICA FINANCIERA ---
    inicial = val_depa * 0.20
    prestamo = val_depa - inicial
    tem = (1 + tcea/100)**(1/12) - 1
    cuota = prestamo * (tem * (1 + tem)**(plazo*12)) / ((1 + tem)**(plazo*12) - 1)
    
    # Gastos fijos (Mantenimiento, arbitrios, predial) - 3% anual
    gastos_fijos_mes = (val_depa * 0.03) / 12
    
    # Ingresos Netos Airbnb (Considerando 15% comisión plataforma)
    ingreso_neto_mes_air = (tarifa * ocupacion_act * 0.85) - cuota - gastos_fijos_mes
    roi_anual_air = (ingreso_neto_mes_air * 12 / inicial) * 100

    # --- 4. DASHBOARD ---
    st.title("🎯 Auditoría de Inversión Airbnb")
    
    # Fila de métricas reducidas
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Cuota Mensual", f"S/. {cuota:,.2f}")
    c2.metric("Punto Equilibrio", f"{np.ceil((cuota + gastos_fijos_mes)/(tarifa*0.85)):.0f} días")
    c3.metric("Utilidad Neto/Mes", f"S/. {ingreso_neto_mes_air:,.2f}")
    c4.metric("ROI s/ Inicial", f"{roi_anual_air:.2f}%")

    st.write("---")

    # SECCIÓN: FLUJO DE CAJA ACUMULADO (PUNTO DE INFLEXIÓN)
    st.subheader("📅 Payback: Recuperación de la Inversión Inicial")
    
    # Proyección a 5 años (60 meses)
    meses_proy = 60
    eje_x = list(range(0, meses_proy + 1))
    # El flujo empieza en NEGATIVO (la inicial)
    flujo_acum = [-inicial]
    for m in range(1, meses_proy + 1):
        flujo_acum.append(flujo_acum[-1] + ingreso_neto_mes_air)

    fig_payback = go.Figure()
    fig_payback.add_trace(go.Scatter(x=eje_x, y=flujo_acum, fill='tozeroy', name="Flujo de Caja Acumulado"))
    fig_payback.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="Punto de Retorno")
    
    fig_payback.update_layout(height=350, margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor='rgba(0,0,0,0)', 
                              plot_bgcolor='rgba(0,0,0,0)', font_color="white",
                              xaxis_title="Meses de Operación", yaxis_title="Soles (S/.)")
    st.plotly_chart(fig_payback, use_container_width=True)

    # SECCIÓN: ANALISIS DE SENSIBILIDAD (ROI vs OCUPACIÓN)
    st.write("---")
    st.subheader("📊 Sensibilidad de Rentabilidad")
    
    dias_rango = [10, 12, 15, 18, 20, 22, 25, 28]
    data_sens = []
    for d in dias_rango:
        u_mes = (tarifa * d * 0.85) - cuota - gastos_fijos_mes
        roi = (u_mes * 12 / inicial) * 100
        data_sens.append({"Días": d, "Utilidad/Mes": u_mes, "ROI%": roi})
    
    df_sens = pd.DataFrame(data_sens)
    
    col_t, col_g = st.columns([1, 1.5])
    with col_t:
        st.dataframe(df_sens.style.format({"Utilidad/Mes": "S/. {:,.0f}", "ROI%": "{:.1f}%"}), hide_index=True)
    with col_g:
        fig_sens = go.Figure(go.Bar(x=df_sens["Días"], y=df_sens["ROI%"], marker_color='#3b82f6', text=df_sens["ROI%"].round(1)))
        fig_sens.update_layout(height=250, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_sens, use_container_width=True)

    # SECCIÓN: COMPARATIVA RÁPIDA VS TRADICIONAL
    st.write("---")
    u_mes_trad = renta_trad - cuota - (val_depa * 0.015 / 12)
    roi_trad = (u_mes_trad * 12 / inicial) * 100
    
    st.subheader("⚖️ Airbnb vs. Tradicional")
    ca, ct = st.columns(2)
    with ca:
        st.markdown(f"""<div class="mini-card" style="border-color: #3b82f6;"><b>Airbnb ({ocupacion_act} días):</b><br>Utilidad Neto: S/. {ingreso_neto_mes_air:,.2f}<br>ROI: {roi_anual_air:.1f}%</div>""", unsafe_allow_html=True)
    with ct:
        st.markdown(f"""<div class="mini-card" style="border-color: #10b981;"><b>Tradicional:</b><br>Utilidad Neto: S/. {u_mes_trad:,.2f}<br>ROI: {roi_trad:.1f}%</div>""", unsafe_allow_html=True)

    if st.button("Finalizar"): st.balloons()
