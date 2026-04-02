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
            password = st.text_input("Contraseña de Usuario:", type="password")
            if st.button("Ingresar"):
                if password == "Jancarlo2026":
                    st.session_state.authenticated = True
                    st.rerun()
                else: st.error("Contraseña incorrecta.")
        return False
    return True

if check_password():
    # CSS para diseño compacto y profesional
    st.markdown("""
        <style>
        .main { background-color: #0e1117; }
        [data-testid="stMetricValue"] { font-size: 1.4rem !important; }
        [data-testid="stMetricLabel"] { font-size: 0.85rem !important; font-weight: bold; }
        div[data-testid="stMetric"] { background-color: #1f2630; padding: 12px; border-radius: 8px; border: 1px solid #30363d; }
        .info-text { font-size: 0.8rem; color: #a1a1a1; margin-top: 5px; line-height: 1.3; }
        .mini-card { padding: 15px; border-radius: 8px; border: 1px solid #30363d; background-color: #161b22; }
        .section-title { margin-top: 20px; margin-bottom: 10px; color: #3b82f6; font-size: 1.2rem; font-weight: bold; }
        </style>
        """, unsafe_allow_html=True)

    # --- 2. SIDEBAR ---
    with st.sidebar:
        st.header("⚙️ Parámetros")
        val_depa = st.number_input("Precio Inmueble (S/.)", value=250000)
        tcea = st.number_input("TCEA % (Préstamo)", value=9.5)
        plazo = st.selectbox("Plazo Crédito (Años)", [10, 15, 20, 25], index=2)
        st.write("---")
        tarifa = st.number_input("Tarifa Airbnb/Día (S/.)", value=180)
        ocupacion_act = st.slider("Días ocupados/mes", 1, 30, 20)
        st.write("---")
        renta_trad = st.number_input("Renta Tradicional/Mes", value=1800)

    # --- 3. LÓGICA FINANCIERA ---
    inicial = val_depa * 0.20
    prestamo = val_depa - inicial
    tem = (1 + tcea/100)**(1/12) - 1
    cuota = prestamo * (tem * (1 + tem)**(plazo*12)) / ((1 + tem)**(plazo*12) - 1)
    gastos_fijos_mes = (val_depa * 0.03) / 12
    
    # Airbnb
    ingreso_neto_mes_air = (tarifa * ocupacion_act * 0.85) - cuota - gastos_fijos_mes
    roi_anual_air = (ingreso_neto_mes_air * 12 / inicial) * 100
    breakeven_dias = (cuota + gastos_fijos_mes) / (tarifa * 0.85)

    # Tradicional
    gastos_trad_mes = (val_depa * 0.015) / 12 # 1.5% anual (menor mantenimiento)
    u_mes_trad = renta_trad - cuota - gastos_trad_mes
    roi_trad = (u_mes_trad * 12 / inicial) * 100

    # --- 4. DASHBOARD ---
    st.title("🎯 Auditoría de Inversión: Estrategia Airbnb")
    
    # Fila de métricas
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Cuota Mensual", f"S/. {cuota:,.2f}")
        st.markdown('<p class="info-text">Obligación fija con el banco. Representa el costo de apalancamiento financiero.</p>', unsafe_allow_html=True)
    with m2:
        st.metric("Punto Equilibrio", f"{np.ceil(breakeven_dias):.0f} días")
        st.markdown('<p class="info-text">Mínimo de noches al mes para que el inmueble se pague solo (Cero flujo de caja).</p>', unsafe_allow_html=True)
    with m3:
        st.metric("Flujo Neto/Mes", f"S/. {ingreso_neto_mes_air:,.2f}")
        st.markdown('<p class="info-text">Efectivo libre después de pagar hipoteca, comisiones de plataforma y gastos fijos.</p>', unsafe_allow_html=True)
    with m4:
        st.metric("ROI s/ Inicial", f"{roi_anual_air:.2f}%")
        st.markdown('<p class="info-text">Rentabilidad anual sobre el capital propio invertido (Cash-on-Cash Return).</p>', unsafe_allow_html=True)

    st.write("---")

    # SECCIÓN: PAYBACK (AÑOS)
    st.markdown('<div class="section-title">📅 Payback: Recuperación del Capital en el Tiempo</div>', unsafe_allow_html=True)
    
    años_proy = 15
    eje_x_años = np.linspace(0, años_proy, años_proy * 12 + 1)
    flujo_acum = [-inicial]
    for m in range(1, len(eje_x_años)):
        flujo_acum.append(flujo_acum[-1] + ingreso_neto_mes_air)

    fig_payback = go.Figure()
    fig_payback.add_trace(go.Scatter(x=eje_x_años, y=flujo_acum, fill='tozeroy', line_color='#3b82f6', name="Flujo Acumulado"))
    fig_payback.add_hline(y=0, line_dash="dash", line_color="red")
    
    # Encontrar año de retorno
    año_retorno = "N/A"
    if ingreso_neto_mes_air > 0:
        meses_retorno = inicial / ingreso_neto_mes_air
        año_retorno = f"{meses_retorno / 12:.1f} años"

    fig_payback.update_layout(height=350, margin=dict(l=20, r=20, t=10, b=20), paper_bgcolor='rgba(0,0,0,0)', 
                              plot_bgcolor='rgba(0,0,0,0)', font_color="white", xaxis_title="Tiempo (Años)", yaxis_title="Saldo Acumulado (S/.)")
    st.plotly_chart(fig_payback, use_container_width=True)
    st.info(f"💡 **Análisis de Retorno:** El punto donde la curva cruza el eje rojo indica que has recuperado el 100% de tu inversión inicial (S/. {inicial:,.0f}). En este escenario, ocurre a los **{año_retorno}**.")

    # SECCIÓN: SENSIBILIDAD
    st.write("---")
    st.markdown('<div class="section-title">📊 Análisis de Sensibilidad: ROI vs. Ocupación</div>', unsafe_allow_html=True)
    
    dias_rango = list(range(5, 31))
    roi_rango = [(((tarifa * d * 0.85) - cuota - gastos_fijos_mes) * 12 / inicial) * 100 for d in dias_rango]
    
    fig_sens = go.Figure()
    fig_sens.add_trace(go.Scatter(x=dias_rango, y=roi_rango, mode='lines+markers', line_color='#00ffcc', name="ROI %"))
    fig_sens.add_hline(y=0, line_dash="dot", line_color="white")
    
    fig_sens.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", xaxis_title="Días Ocupados al Mes", yaxis_title="ROI Anual %")
    st.plotly_chart(fig_sens, use_container_width=True)
    st.warning(f"⚠️ **Punto Crítico:** El ROI 0% se alcanza a los **{np.ceil(breakeven_dias):.0f} días**. Por debajo de este nivel, la propiedad genera pérdidas mensuales que deben ser cubiertas por el propietario.")

    # SECCIÓN: COMPARATIVA FINAL
    st.write("---")
    st.markdown('<div class="section-title">⚖️ Duelo de Estrategias: Airbnb vs. Tradicional</div>', unsafe_allow_html=True)
    
    col_res, col_graf = st.columns([1, 1.5])
    with col_res:
        st.markdown(f"""
        <div class="mini-card">
            <b>🏠 Airbnb (Activo)</b><br>
            • Ingreso Bruto Anual: S/. {tarifa * ocupacion_act * 12:,.0f}<br>
            • Utilidad Neta Anual: S/. {ingreso_neto_mes_air * 12:,.2f}<br>
            • ROI: {roi_anual_air:.1f}%<br><br>
            <b>🏢 Tradicional (Pasivo)</b><br>
            • Ingreso Bruto Anual: S/. {renta_trad * 12:,.0f}<br>
            • Utilidad Neta Anual: S/. {u_mes_trad * 12:,.2f}<br>
            • ROI: {roi_trad:.1f}%
        </div>
        """, unsafe_allow_html=True)
        st.caption("Nota: El alquiler tradicional asume un gasto de mantenimiento e impuestos del 1.5% anual del valor de la propiedad.")

    with col_graf:
        # Gráfico comparativo de barras
        labels = ['Utilidad Anual Airbnb', 'Utilidad Anual Tradicional']
        valores = [ingreso_neto_mes_air * 12, u_mes_trad * 12]
        fig_comp = go.Figure([go.Bar(x=labels, y=valores, marker_color=['#3b82f6', '#10b981'], text=[f"S/. {v:,.0f}" for v in valores], textposition='auto')])
        fig_comp.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_comp, use_container_width=True)

    if st.button("✅ Finalizar Auditoría"):
        st.balloons()
