import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- 1. CONFIGURACIÓN Y SEGURIDAD ---
try:
    st.set_page_config(page_title="Auditoría Pro | Jancarlo Mendoza", layout="wide")
except:
    pass

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
    st.markdown("""
        <style>
        .main { background-color: #0e1117; }
        [data-testid="stMetricValue"] { font-size: 1.6rem !important; color: #00ffcc; }
        [data-testid="stMetricLabel"] { font-size: 0.9rem !important; font-weight: bold; }
        div[data-testid="stMetric"] { background-color: #1f2630; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
        .info-text { font-size: 0.8rem; color: #a1a1a1; margin-top: 4px; line-height: 1.2; font-style: italic; }
        .section-title { margin-top: 25px; margin-bottom: 5px; color: #3b82f6; font-size: 1.3rem; font-weight: bold; }
        .section-desc { font-size: 0.85rem; color: #8899a6; margin-bottom: 15px; }
        .compare-card { background-color: #161b22; padding: 20px; border-radius: 10px; border: 1px solid #30363d; height: 100%; }
        .payback-card { background-color: #064e3b; padding: 15px; border-radius: 10px; border-left: 5px solid #00ffcc; margin-top: 10px; text-align: center; font-size: 0.95rem; }
        </style>
        """, unsafe_allow_html=True)

    # --- 2. SIDEBAR ---
    with st.sidebar:
        st.header("⚙️ Parámetros")
        val_depa = st.number_input("Precio Inmueble (S/.)", value=250000)
        tcea = st.number_input("TCEA % (Préstamo)", value=9.5)
        plazo_años = st.selectbox("Plazo Crédito (Años)", [10, 15, 20, 25], index=2)
        st.write("---")
        tarifa = st.number_input("Tarifa Airbnb/Día", value=180)
        ocupacion_act = st.slider("Días ocupados/mes", 1, 30, 20)
        st.write("---")
        renta_trad = st.number_input("Renta Tradicional/Mes", value=1800)

    # --- 3. LÓGICA FINANCIERA (Global) ---
    inicial = val_depa * 0.20
    prestamo = val_depa - inicial
    tem = (1 + tcea/100)**(1/12) - 1
    cuota = prestamo * (tem * (1 + tem)**(plazo_años*12)) / ((1 + tem)**(plazo_años*12) - 1)
    mantenimiento_mes = (val_depa * 0.03) / 12
    
    ingreso_bruto_air = tarifa * ocupacion_act * 0.85
    impuesto_air = ingreso_bruto_air * 0.05
    flujo_neto_air = ingreso_bruto_air - cuota - mantenimiento_mes - impuesto_air
    roi_anual_air = (flujo_neto_air * 12 / inicial) * 100
    breakeven_dias = (cuota + mantenimiento_mes) / (tarifa * 0.85 * 0.95)

    # --- 4. TABS ---
    tab1, tab2, tab3 = st.tabs(["📊 Flujos y Payback", "📈 Plusvalía y Patrimonio", "🛡️ Riesgo y Sensibilidad"])

    with tab1:
        st.markdown('<div class="section-title">💰 Estructura de Ingresos y Gastos</div>', unsafe_allow_html=True)
        data_resumen = {
            "Concepto": ["Ingresos Brutos (Neto Airbnb)", "Cuota Hipotecaria", "Mantenimiento / Arbitrios", "Impuestos (Sunat 5%)", "UTILIDAD NETA (Cashflow)"],
            "Mensual": [f"S/. {ingreso_bruto_air:,.2f}", f"S/. -{cuota:,.2f}", f"S/. -{mantenimiento_mes:,.2f}", f"S/. -{impuesto_air:,.2f}", f"S/. {flujo_neto_air:,.2f}"],
            "Anual": [f"S/. {ingreso_bruto_air*12:,.2f}", f"S/. -{cuota*12:,.2f}", f"S/. -{mantenimiento_mes*12:,.2f}", f"S/. -{impuesto_air*12:,.2f}", f"S/. {flujo_neto_air*12:,.2f}"]
        }
        st.table(pd.DataFrame(data_resumen))

        # --- SECCIÓN NUEVA: ROI COMPARATIVO ---
        st.markdown('<div class="section-title">🎯 Desempeño del Capital (ROI)</div>', unsafe_allow_html=True)
        col_roi, col_bench = st.columns([1, 1.5])
        
        with col_roi:
            st.metric("Tu ROI Anual (Cash-on-Cash)", f"{roi_anual_air:.2f}%")
            st.markdown('<p class="info-text">Rendimiento directo sobre el capital inicial invertido (S/. {:,.0f}).</p>'.format(inicial), unsafe_allow_html=True)
        
        with col_bench:
            st.markdown("""
            <div class="compare-card">
                <b>📊 Comparativa de Mercado (Promedios):</b><br>
                <span style='color:#8899a6'>• Depósito a Plazo Fijo:</span> 6.0% - 7.5%<br>
                <span style='color:#8899a6'>• Fondos Mutuos (Moderado):</span> 5.0% - 8.0%<br>
                <span style='color:#8899a6'>• Inmueble Tradicional:</span> 4.0% - 6.0%<br>
                <span style='color: #00ffcc'>• Tu Proyecto Airbnb: <b>{:.2f}%</b></span>
            </div>
            """.format(roi_anual_air), unsafe_allow_html=True)

        # --- GRÁFICO PAYBACK ---
        st.markdown('<div class="section-title">📅 Payback: Recuperación de la Inversión Inicial</div>', unsafe_allow_html=True)
        años_pb = 25
        meses_pb = np.arange(0, años_pb * 12 + 1)
        flujo_acum = [-inicial]
        for m in meses_pb[1:]:
            u_mes = flujo_neto_air if m <= (plazo_años * 12) else (ingreso_bruto_air - mantenimiento_mes - impuesto_air)
            flujo_acum.append(flujo_acum[-1] + u_mes)

        fig_pb = go.Figure()
        f_np = np.array(flujo_acum)
        fig_pb.add_trace(go.Scatter(x=meses_pb/12, y=np.where(f_np <= 0, f_np, 0), fill='tozeroy', fillcolor='rgba(239, 68, 68, 0.2)', line=dict(color='rgba(0,0,0,0)'), name="Fase Recuperación"))
        fig_pb.add_trace(go.Scatter(x=meses_pb/12, y=np.where(f_np >= 0, f_np, 0), fill='tozeroy', fillcolor='rgba(16, 185, 129, 0.2)', line=dict(color='rgba(0,0,0,0)'), name="Ganancia Neta"))
        fig_pb.add_trace(go.Scatter(x=meses_pb/12, y=flujo_acum, line=dict(color='#3b82f6', width=4), name="Saldo Acumulado"))
        fig_pb.add_hline(y=0, line_dash="dash", line_color="white")
        fig_pb.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", xaxis_title="Años")
        st.plotly_chart(fig_pb, use_container_width=True)
        
        if flujo_neto_air > 0:
            años_r = (inicial / (flujo_neto_air * 12))
            st.markdown(f"""<div class="payback-card">🚀 <b>ANÁLISIS:</b> Recuperas tu inicial en <b>{años_r:.1f} años</b>. A partir de ahí, todo es utilidad neta sobre capital recuperado.</div>""", unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="section-title">📈 Proyección Patrimonial (Plusvalía)</div>', unsafe_allow_html=True)
        plus_input = st.slider("Plusvalía Anual Estimada (%)", 0.0, 10.0, 4.0)
        años_p = np.arange(0, 26)
        v_mkt = [val_depa * (1 + plus_input/100)**a for a in años_p]
        s_deuda = [prestamo * (1 - a/plazo_años) if a < plazo_años else 0 for a in años_p]
        eq = [v - d for v, d in zip(v_mkt, s_deuda)]
        fig_p = go.Figure()
        fig_p.add_trace(go.Bar(x=años_p, y=v_mkt, name="Valor Comercial", marker_color='#1f2630'))
        fig_p.add_trace(go.Scatter(x=años_p, y=eq, name="Equity", fill='tozeroy', line=dict(color='#00ffcc')))
        fig_p.update_layout(height=400, barmode='overlay', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_p, use_container_width=True)

    with tab3:
        st.markdown('<div class="section-title">🛡️ Escenarios de Riesgo y Sensibilidad</div>', unsafe_allow_html=True)
        st.metric("Punto Equilibrio", f"{np.ceil(breakeven_dias):.0f} días")
        col_t, col_l = st.columns([1, 2])
        d_t = [5, 10, 15, 20, 25, 30]
        r_t = [((((tarifa * d * 0.85 * 0.95) - cuota - mantenimiento_mes) * 12 / inicial) * 100) for d in d_t]
        with col_t:
            st.dataframe(pd.DataFrame({"Ocupación": [f"{d} d" for d in d_t], "ROI %": r_t}).style.format({"ROI %": "{:.1f}%"}).background_gradient(cmap='RdYlGn'), hide_index=True)
        with col_l:
            d_g = list(range(5, 31))
            r_g = [((((tarifa * d * 0.85 * 0.95) - cuota - mantenimiento_mes) * 12 / inicial) * 100) for d in d_g]
            fig_s = go.Figure(go.Scatter(x=d_g, y=r_g, mode='lines', line=dict(color='#00ffcc', width=4)))
            fig_s.add_hline(y=0, line_dash="dot", line_color="red")
            fig_s.update_layout(height=250, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig_s, use_container_width=True)

    if st.button("✅ Finalizar Auditoría"): st.balloons()
