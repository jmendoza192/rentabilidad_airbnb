import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- 1. CONFIGURACIÓN Y SEGURIDAD ---
st.set_page_config(page_title="Auditoría Pro | Jancarlo Mendoza", layout="wide")

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
    # RECUPERACIÓN DE ESTILOS ANTERIORES
    st.markdown("""
        <style>
        .main { background-color: #0e1117; }
        [data-testid="stMetricValue"] { font-size: 1.4rem !important; }
        [data-testid="stMetricLabel"] { font-size: 0.85rem !important; font-weight: bold; }
        div[data-testid="stMetric"] { background-color: #1f2630; padding: 12px; border-radius: 8px; border: 1px solid #30363d; }
        .info-text { font-size: 0.8rem; color: #a1a1a1; margin-top: 4px; line-height: 1.2; }
        .mini-card { padding: 15px; border-radius: 8px; border: 1px solid #30363d; background-color: #161b22; }
        .payback-card { background-color: #064e3b; padding: 15px; border-radius: 10px; border-left: 5px solid #00ffcc; margin-top: 10px; text-align: center; }
        .section-title { margin-top: 20px; margin-bottom: 2px; color: #3b82f6; font-size: 1.2rem; font-weight: bold; }
        .section-desc { font-size: 0.85rem; color: #8899a6; margin-bottom: 15px; }
        </style>
        """, unsafe_allow_html=True)

    # --- 2. SIDEBAR ---
    with st.sidebar:
        st.header("⚙️ Parámetros")
        val_depa = st.number_input("Precio Inmueble (S/.)", value=250000)
        tcea = st.number_input("TCEA % (Préstamo)", value=9.5)
        plazo = st.selectbox("Plazo Crédito (Años)", [10, 15, 20, 25], index=2)
        st.write("---")
        tarifa = st.number_input("Tarifa Airbnb/Día", value=180)
        ocupacion_act = st.slider("Días ocupados/mes", 1, 30, 20)
        st.write("---")
        renta_trad = st.number_input("Renta Tradicional/Mes", value=1800)
        plusvalia_est = st.slider("Plusvalía Anual Est. %", 0.0, 8.0, 4.0)

    # --- 3. LÓGICA FINANCIERA ---
    inicial = val_depa * 0.20
    prestamo = val_depa - inicial
    tem = (1 + tcea/100)**(1/12) - 1
    cuota = prestamo * (tem * (1 + tem)**(plazo*12)) / ((1 + tem)**(plazo*12) - 1)
    gastos_fijos_mes = (val_depa * 0.03) / 12
    
    # Airbnb (Incluyendo Impuesto 5% sobre Bruto - 1ra/Especial)
    ingreso_bruto_air = tarifa * ocupacion_act * 0.85
    impuesto_air = ingreso_bruto_air * 0.05
    flujo_neto_air = ingreso_bruto_air - cuota - gastos_fijos_mes - impuesto_air
    roi_anual_air = (flujo_neto_air * 12 / inicial) * 100
    breakeven_dias = (cuota + gastos_fijos_mes) / (tarifa * 0.85 * 0.95)

    # Tradicional (Impuesto 1ra Cat 5%)
    gastos_trad_mes = (val_depa * 0.015) / 12
    impuesto_trad = renta_trad * 0.05
    u_mes_trad = renta_trad - cuota - gastos_trad_mes - impuesto_trad
    roi_trad = (u_mes_trad * 12 / inicial) * 100

    # --- 4. TABS ---
    tab1, tab2, tab3 = st.tabs(["📊 Análisis Operativo", "📈 Plusvalía y Patrimonio", "🛡️ Escenarios de Riesgo"])

    with tab1:
        st.markdown('<div class="section-title">🎯 Auditoría de Flujo: Airbnb</div>', unsafe_allow_html=True)
        st.markdown('<p class="section-desc">Métricas de rendimiento mensual y retorno de capital inyectado.</p>', unsafe_allow_html=True)
        
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Cuota Mensual", f"S/. {cuota:,.2f}")
            st.markdown('<p class="info-text">Obligación hipotecaria fija con el banco.</p>', unsafe_allow_html=True)
        with m2:
            st.metric("Flujo Neto/Mes", f"S/. {flujo_neto_air:,.2f}")
            st.markdown('<p class="info-text">Efectivo libre tras gastos e impuestos.</p>', unsafe_allow_html=True)
        with m3:
            st.metric("ROI s/ Inicial", f"{roi_anual_air:.2f}%")
            st.markdown('<p class="info-text">Retorno Cash-on-Cash anualizado.</p>', unsafe_allow_html=True)

        st.write("---")
        st.markdown('<div class="section-title">📅 Payback: Recuperación del Capital en el Tiempo</div>', unsafe_allow_html=True)
        
        años_proy = 15
        eje_x = np.linspace(0, años_proy, años_proy * 12 + 1)
        flujo_acum = [-inicial]
        for m in range(1, len(eje_x)): flujo_acum.append(flujo_acum[-1] + flujo_neto_air)
        
        fig_pb = go.Figure()
        flujo_np = np.array(flujo_acum)
        fig_pb.add_trace(go.Scatter(x=eje_x, y=np.where(flujo_np <= 0, flujo_np, 0), fill='tozeroy', fillcolor='rgba(255, 0, 0, 0.2)', line=dict(color='rgba(0,0,0,0)'), showlegend=False))
        fig_pb.add_trace(go.Scatter(x=eje_x, y=np.where(flujo_np >= 0, flujo_np, 0), fill='tozeroy', fillcolor='rgba(0, 255, 0, 0.2)', line=dict(color='rgba(0,255,0,0)'), showlegend=False))
        fig_pb.add_trace(go.Scatter(x=eje_x, y=flujo_acum, line=dict(color='#3b82f6', width=3), name="Flujo Acumulado"))
        fig_pb.add_hline(y=0, line_dash="dash", line_color="white")
        fig_pb.update_layout(height=350, margin=dict(l=20, r=20, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", xaxis_title="Años", yaxis_title="Soles")
        st.plotly_chart(fig_pb, use_container_width=True)
        
        if flujo_neto_air > 0:
            st.markdown(f"""<div class="payback-card">🚀 <b>PUNTO DE EQUILIBRIO:</b> Recuperas tu inicial en <b>{ (inicial/flujo_neto_air)/12 :.1f} años</b>.</div>""", unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="section-title">📈 Crecimiento Patrimonial y Plusvalía</div>', unsafe_allow_html=True)
        st.markdown('<p class="section-desc">Análisis de valorización del activo (Equity) frente al saldo de deuda.</p>', unsafe_allow_html=True)
        
        años_pat = list(range(0, 11))
        val_mkt = [val_depa * (1 + plusvalia_est/100)**a for a in años_pat]
        saldo_deuda = [prestamo * (1 - a/plazo) if a < plazo else 0 for a in años_pat]
        equity = [v - d for v, d in zip(val_mkt, saldo_deuda)]

        fig_pat = go.Figure()
        fig_pat.add_trace(go.Bar(x=años_pat, y=val_mkt, name="Valor Propiedad", marker_color='#1f2630'))
        fig_pat.add_trace(go.Scatter(x=años_pat, y=equity, name="Patrimonio (Equity)", line=dict(color='#00ffcc', width=4), fill='tozeroy'))
        fig_pat.update_layout(height=400, barmode='overlay', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", xaxis_title="Años")
        st.plotly_chart(fig_pat, use_container_width=True)
        
        st.info(f"💡 **ROE proyectado:** Al año 5, tu patrimonio real en el inmueble sería de S/. {equity[5]:,.0f} gracias a la plusvalía.")

    with tab3:
        st.markdown('<div class="section-title">📊 Análisis de Sensibilidad y Riesgo</div>', unsafe_allow_html=True)
        
        c_be, _ = st.columns([1, 2])
        with c_be:
            st.metric("Punto Equilibrio Operativo", f"{np.ceil(breakeven_dias):.0f} días")
            st.markdown('<p class="info-text">Noches mínimas para cubrir 100% de costos.</p>', unsafe_allow_html=True)
        
        col_t, col_l = st.columns([1, 2])
        dias_tabla = [5, 10, 15, 20, 25, 30]
        roi_tabla = [((((tarifa * d * 0.85 * 0.95) - cuota - gastos_fijos_mes) * 12 / inicial) * 100) for d in dias_tabla]
        
        with col_t:
            df_s = pd.DataFrame({"Ocupación": [f"{d} d" for d in dias_tabla], "ROI %": roi_tabla})
            st.dataframe(df_s.style.format({"ROI %": "{:.1f}%"}).background_gradient(cmap='RdYlGn', axis=0), height=250, hide_index=True)
        with col_l:
            d_g = list(range(5, 31))
            r_g = [((((tarifa * d * 0.85 * 0.95) - cuota - gastos_fijos_mes) * 12 / inicial) * 100) for d in d_g]
            fig_s = go.Figure(go.Scatter(x=d_g, y=r_g, mode='lines', line=dict(color='#00ffcc', width=4)))
            fig_s.add_hline(y=0, line_dash="dot", line_color="red")
            fig_s.update_layout(height=250, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig_s, use_container_width=True)

        st.write("---")
        st.markdown('<div class="section-title">⚖️ Airbnb vs. Tradicional (Post-Impuestos)</div>', unsafe_allow_html=True)
        res_col, graf_col = st.columns([1, 1.5])
        with res_col:
            st.markdown(f"""<div class="mini-card"><b>🏠 Airbnb:</b> ROI {roi_anual_air:.1f}%<br><b>🏢 Tradicional:</b> ROI {roi_trad:.1f}%</div>""", unsafe_allow_html=True)
            st.markdown('<p class="info-text">Ambos escenarios incluyen el 5% de impuesto a la renta (Sunat).</p>', unsafe_allow_html=True)
        with graf_col:
            fig_c = go.Figure([go.Bar(x=['Airbnb', 'Tradicional'], y=[flujo_neto_air*12, u_mes_trad*12], marker_color=['#3b82f6', '#10b981'], 
                                     text=[f"S/. {flujo_neto_air*12:,.0f}", f"S/. {u_mes_trad*12:,.0f}"], textposition='inside', insidetextanchor='middle', textfont=dict(size=22, family="Arial Black", color="white"))])
            fig_c.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig_c, use_container_width=True)

    if st.button("✅ Finalizar"): st.balloons()
    
