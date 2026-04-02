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
        .info-text { font-size: 0.8rem; color: #a1a1a1; margin-top: 4px; line-height: 1.3; font-style: italic; }
        .section-title { margin-top: 25px; margin-bottom: 5px; color: #3b82f6; font-size: 1.3rem; font-weight: bold; }
        .section-desc { font-size: 0.85rem; color: #8899a6; margin-bottom: 15px; }
        .compare-card { background-color: #161b22; padding: 20px; border-radius: 10px; border: 1px solid #30363d; height: 100%; }
        .payback-card { background-color: #064e3b; padding: 15px; border-radius: 10px; border-left: 5px solid #00ffcc; margin-top: 15px; text-align: center; font-size: 0.95rem; }
        </style>
        """, unsafe_allow_html=True)

    # --- 2. SIDEBAR ---
    with st.sidebar:
        st.header("⚙️ Parámetros del Proyecto")
        val_depa = st.number_input("Precio Inmueble (S/.)", value=250000)
        inv_amoblado = st.number_input("Inversión Amoblado/Equipamiento (S/.)", value=25000)
        st.write("---")
        tcea = st.number_input("TCEA % (Costo del Banco)", value=9.5)
        plazo_años = st.selectbox("Plazo Crédito (Años)", [10, 15, 20, 25], index=2)
        st.write("---")
        tarifa = st.number_input("Tarifa Airbnb/Día (Neto)", value=180)
        ocupacion_act = st.slider("Días ocupados/mes", 1, 30, 20)
        st.write("---")
        renta_trad = st.number_input("Renta Tradicional/Mes", value=1800)

    # --- 3. LÓGICA FINANCIERA CENTRAL ---
    inicial_banco = val_depa * 0.20
    inversion_total_real = inicial_banco + inv_amoblado
    prestamo = val_depa - inicial_banco
    tem = (1 + tcea/100)**(1/12) - 1
    cuota = prestamo * (tem * (1 + tem)**(plazo_años*12)) / ((1 + tem)**(plazo_años*12) - 1)
    mantenimiento_mes = (val_depa * 0.03) / 12
    
    # Airbnb
    ingreso_bruto_air = tarifa * ocupacion_act * 0.85
    impuesto_air = ingreso_bruto_air * 0.05
    flujo_neto_air = ingreso_bruto_air - cuota - mantenimiento_mes - impuesto_air
    roi_anual_air = (flujo_neto_air * 12 / inversion_total_real) * 100
    breakeven_dias = (cuota + mantenimiento_mes) / (tarifa * 0.85 * 0.95)

    # Tradicional
    u_anual_trad = (renta_trad - cuota - (val_depa*0.015/12) - (renta_trad*0.05)) * 12

    # --- 4. TABS ---
    tab1, tab2, tab3 = st.tabs(["📊 Flujos y Payback", "📈 Plusvalía y Patrimonio", "🛡️ Riesgo y Sensibilidad"])

    with tab1:
        st.markdown('<div class="section-title">💰 Estructura de Desembolso Inicial</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.metric("Inversión Total", f"S/. {inversion_total_real:,.0f}")
        c1.markdown(f'<p class="info-text">Suma de Cuota Inicial (S/. {inicial_banco:,.0f}) + Equipamiento Airbnb (S/. {inv_amoblado:,.0f}).</p>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">📉 Flujo de Caja Operativo</div>', unsafe_allow_html=True)
        df_res = pd.DataFrame({
            "Concepto": ["Ingresos (Airbnb)", "Cuota Hipotecaria", "Gastos Fijos", "Impuestos", "UTILIDAD NETA"],
            "Mensual": [f"S/. {ingreso_bruto_air:,.2f}", f"S/. -{cuota:,.2f}", f"S/. -{mantenimiento_mes:,.2f}", f"S/. -{impuesto_air:,.2f}", f"S/. {flujo_neto_air:,.2f}"],
            "Anual": [f"S/. {ingreso_bruto_air*12:,.2f}", f"S/. -{cuota*12:,.2f}", f"S/. -{mantenimiento_mes*12:,.2f}", f"S/. -{impuesto_air*12:,.2f}", f"S/. {flujo_neto_air*12:,.2f}"]
        })
        st.table(df_res)

        st.markdown('<div class="section-title">🎯 Desempeño y Benchmark de Mercado</div>', unsafe_allow_html=True)
        col_roi, col_bench = st.columns([1, 1.5])
        with col_roi:
            st.metric("Tu ROI Anual Real", f"{roi_anual_air:.2f}%")
            st.markdown('<p class="info-text">Rendimiento anual sobre cada sol invertido de tu bolsillo.</p>', unsafe_allow_html=True)
        with col_bench:
            st.markdown(f"""
            <div class="compare-card">
                <b>📊 5 Referencias de Mercado (ROI Promedio):</b><br>
                <span style='color:#8899a6'>1. Depósito Plazo Fijo (Banca Top):</span> 6.8%<br>
                <span style='color:#8899a6'>2. Caja Municipal (Ahorro):</span> 7.5%<br>
                <span style='color:#8899a6'>3. Fondos Mutuos (S&P 500 hist):</span> 8.2%<br>
                <span style='color:#8899a6'>4. Alquiler Tradicional (Lima):</span> 4.5%<br>
                <span style='color: #00ffcc'>5. Tu Inversión Airbnb: <b>{roi_anual_air:.2f}%</b></span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="section-title">📅 Payback: Recuperación del Capital</div>', unsafe_allow_html=True)
        años_pb = 25
        meses_pb = np.arange(0, años_pb * 12 + 1)
        flujo_acum = [-inversion_total_real]
        for m in meses_pb[1:]:
            u_mes = flujo_neto_air if m <= (plazo_años * 12) else (ingreso_bruto_air - mantenimiento_mes - impuesto_air)
            flujo_acum.append(flujo_acum[-1] + u_mes)
        
        fig_pb = go.Figure()
        fig_pb.add_trace(go.Scatter(x=meses_pb/12, y=flujo_acum, line=dict(color='#3b82f6', width=4), name="Flujo Acumulado"))
        fig_pb.add_hline(y=0, line_dash="dash", line_color="white")
        fig_pb.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", xaxis_title="Años")
        st.plotly_chart(fig_pb, use_container_width=True)

    with tab2:
        st.markdown('<div class="section-title">📈 Plusvalía: El Valor del Tiempo</div>', unsafe_allow_html=True)
        st.markdown('<p class="section-desc">Nota: La plusvalía es el aumento del valor comercial del inmueble por factores de mercado y zona.</p>', unsafe_allow_html=True)
        
        plus_val = st.slider("Expectativa de Plusvalía Anual (%)", 0.0, 10.0, 4.0)
        años_p = np.arange(0, 26)
        v_mkt = [val_depa * (1 + plus_val/100)**a for a in años_p]
        s_deuda = [prestamo * (1 - a/plazo_años) if a < plazo_años else 0 for a in años_p]
        eq = [v - d for v, d in zip(v_mkt, s_deuda)]
        
        fig_p = go.Figure()
        fig_p.add_trace(go.Bar(x=años_p, y=v_mkt, name="Valor Propiedad", marker_color='#1f2630'))
        fig_p.add_trace(go.Scatter(x=años_p, y=eq, name="Equity (Patrimonio)", fill='tozeroy', line=dict(color='#00ffcc', width=3)))
        fig_p.update_layout(height=400, barmode='overlay', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", title="Evolución del Patrimonio vs Deuda")
        st.plotly_chart(fig_p, use_container_width=True)
        st.markdown('<p class="info-text">💡 <b>Concepto Equity:</b> Es la porción de la propiedad que ya es suya. Al inicio es solo su inicial, al final es el 100% del valor revalorizado.</p>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="section-title">🛡️ Escenarios y Resiliencia del Proyecto</div>', unsafe_allow_html=True)
        st.markdown('<p class="section-desc">Análisis de qué tan preparado está el departamento para soportar bajas temporadas.</p>', unsafe_allow_html=True)
        
        col_m, col_t = st.columns([1, 2])
        with col_m:
            st.metric("Punto de Equilibrio", f"{np.ceil(breakeven_dias):.0f} días")
            st.markdown('<p class="info-text">Si alquila menos de estos días al mes, la operación generará pérdidas de flujo de caja.</p>', unsafe_allow_html=True)
        
        st.write("---")
        st.markdown('<div class="section-title">⚖️ Airbnb vs Alquiler Tradicional</div>', unsafe_allow_html=True)
        fig_c = go.Figure([go.Bar(x=['Airbnb (Auditado)', 'Tradicional'], y=[flujo_neto_air*12, u_anual_trad], marker_color=['#3b82f6', '#10b981'], text=[f"S/. {flujo_neto_air*12:,.0f}", f"S/. {u_anual_trad:,.0f}"], textposition='inside')])
        fig_c.update_layout(height=350, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", title="Utilidad Anual Comparada")
        st.plotly_chart(fig_c, use_container_width=True)
        st.markdown('<p class="info-text">Nota: El alquiler tradicional tiene menos riesgo pero generalmente ofrece un retorno significativamente menor en zonas de alta demanda turística.</p>', unsafe_allow_html=True)

    if st.button("✅ Finalizar Informe"): st.balloons()
