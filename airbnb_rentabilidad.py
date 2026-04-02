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
    st.markdown("""
        <style>
        .main { background-color: #0e1117; }
        [data-testid="stMetricValue"] { font-size: 1.4rem !important; }
        [data-testid="stMetricLabel"] { font-size: 0.85rem !important; font-weight: bold; }
        div[data-testid="stMetric"] { background-color: #1f2630; padding: 12px; border-radius: 8px; border: 1px solid #30363d; }
        .info-text { font-size: 0.8rem; color: #a1a1a1; margin-top: 4px; line-height: 1.2; }
        .section-title { margin-top: 20px; margin-bottom: 2px; color: #3b82f6; font-size: 1.2rem; font-weight: bold; }
        .section-desc { font-size: 0.85rem; color: #8899a6; margin-bottom: 15px; }
        </style>
        """, unsafe_allow_html=True)

    # --- 2. SIDEBAR ---
    with st.sidebar:
        st.header("⚙️ Parámetros Operativos")
        val_depa = st.number_input("Precio Inmueble (S/.)", value=250000)
        tcea = st.number_input("TCEA % (Préstamo)", value=9.5)
        plazo_años = st.selectbox("Plazo Crédito (Años)", [10, 15, 20, 25], index=2)
        st.write("---")
        tarifa = st.number_input("Tarifa Airbnb/Día", value=180)
        ocupacion_act = st.slider("Días ocupados/mes", 1, 30, 20)
        st.write("---")
        renta_trad = st.number_input("Renta Tradicional/Mes", value=1800)

    # --- 3. LÓGICA FINANCIERA CENTRAL (Cálculos Globales) ---
    # Inversión Inicial
    inicial = val_depa * 0.20
    prestamo = val_depa - inicial
    
    # Hipoteca
    tem = (1 + tcea/100)**(1/12) - 1
    cuota = prestamo * (tem * (1 + tem)**(plazo_años*12)) / ((1 + tem)**(plazo_años*12) - 1)
    
    # Costos Operativos (Mantenimiento 3% anual, Tradicional 1.5% anual)
    mantenimiento_mes = (val_depa * 0.03) / 12
    gastos_trad_mes = (val_depa * 0.015) / 12
    
    # Airbnb (Ingreso neto de comisión 15%, Impuesto Sunat 5%)
    ingreso_bruto_mes_air = tarifa * ocupacion_act * 0.85
    impuesto_air = ingreso_bruto_mes_air * 0.05
    flujo_neto_air = ingreso_bruto_mes_air - cuota - mantenimiento_mes - impuesto_air
    roi_actual_air = (flujo_neto_air * 12 / inicial) * 100
    breakeven_dias = (cuota + mantenimiento_mes) / (tarifa * 0.85 * 0.95)

    # Tradicional (Impuesto Sunat 5%)
    impuesto_trad = renta_trad * 0.05
    u_mes_trad = renta_trad - cuota - gastos_trad_mes - impuesto_trad
    roi_actual_trad = (u_mes_trad * 12 / inicial) * 100

    # --- 4. TABS ---
    tab1, tab2, tab3 = st.tabs(["📊 Proyección de Flujos", "📈 Plusvalía y Patrimonio", "🛡️ Análisis de Riesgo"])

    with tab1:
        st.markdown('<div class="section-title">📊 Resumen de Flujos: Ingresos, Egresos y Utilidad</div>', unsafe_allow_html=True)
        
        # Tabla Informativa
        data_resumen = {
            "Concepto": ["Ingresos Brutos (Airbnb)", "Cuota Hipotecaria", "Mantenimiento / Otros", "Impuestos (Sunat)", "Egresos Totales", "Utilidad Neta"],
            "Mensual (S/.)": [f"S/. {ingreso_bruto_mes_air:,.2f}", f"S/. -{cuota:,.2f}", f"S/. -{mantenimiento_mes:,.2f}", f"S/. -{impuesto_air:,.2f}", f"S/. -{cuota+mantenimiento_mes+impuesto_air:,.2f}", f"S/. {flujo_neto_air:,.2f}"],
            "Anual (S/.)": [f"S/. {ingreso_bruto_mes_air*12:,.2f}", f"S/. -{cuota*12:,.2f}", f"S/. -{mantenimiento_mes*12:,.2f}", f"S/. -{impuesto_air*12:,.2f}", f"S/. -{(cuota+mantenimiento_mes+impuesto_air)*12:,.2f}", f"S/. {flujo_neto_air*12:,.2f}"]
        }
        st.table(pd.DataFrame(data_resumen))
        st.metric("ROI Actual sobre Inicial", f"{roi_actual_air:.2f}%")

        # Gráfico Proyección 25 Años
        años_proy = 25
        meses = np.arange(1, años_proy * 12 + 1)
        ing_linea = np.full(len(meses), ingreso_bruto_mes_air)
        egr_linea = [(mantenimiento_mes + impuesto_air + (cuota if m <= (plazo_años * 12) else 0)) for m in meses]
        util_linea = ing_linea - np.array(egr_linea)

        fig_f = go.Figure()
        fig_f.add_trace(go.Scatter(x=meses/12, y=ing_linea, name="Ingresos", line=dict(color='#3b82f6')))
        fig_f.add_trace(go.Scatter(x=meses/12, y=egr_linea, name="Egresos", line=dict(color='#ef4444')))
        fig_f.add_trace(go.Scatter(x=meses/12, y=util_linea, name="Utilidad Neta", fill='tozeroy', line=dict(color='#10b981', width=3)))
        fig_f.add_vline(x=plazo_años, line_dash="dash", line_color="orange")
        fig_f.update_layout(height=400, title="Flujo de Caja a 25 Años", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_f, use_container_width=True)

        # Gráfico Evolución ROI
        st.markdown('<div class="section-title">📈 Evolución del ROI Anualizado</div>', unsafe_allow_html=True)
        roi_evol = [(u * 12 / inicial) * 100 for u in util_linea]
        fig_roi = go.Figure(go.Scatter(x=meses/12, y=roi_evol, name="ROI %", line=dict(color='#00ffcc', width=4), fill='tozeroy', fillcolor='rgba(0, 255, 204, 0.1)'))
        fig_roi.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", yaxis_title="ROI %")
        st.plotly_chart(fig_roi, use_container_width=True)

    with tab2:
        st.markdown('<div class="section-title">📈 Crecimiento Patrimonial y Plusvalía</div>', unsafe_allow_html=True)
        plus_input = st.slider("Plusvalía Anual (%)", 0.0, 10.0, 4.0)
        años_p = np.arange(0, 26)
        v_mkt = [val_depa * (1 + plus_input/100)**a for a in años_p]
        s_deuda = [prestamo * (1 - a/plazo_años) if a < plazo_años else 0 for a in años_p]
        eq = [v - d for v, d in zip(v_mkt, s_deuda)]
        
        fig_p = go.Figure()
        fig_p.add_trace(go.Bar(x=años_p, y=v_mkt, name="Valor Mercado", marker_color='#1f2630'))
        fig_p.add_trace(go.Scatter(x=años_p, y=eq, name="Equity", fill='tozeroy', line=dict(color='#00ffcc')))
        fig_p.update_layout(height=400, barmode='overlay', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_p, use_container_width=True)

    with tab3:
        st.markdown('<div class="section-title">🛡️ Análisis de Sensibilidad Operativa</div>', unsafe_allow_html=True)
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

        st.write("---")
        st.markdown('<div class="section-title">⚖️ Airbnb vs. Tradicional (Anual)</div>', unsafe_allow_html=True)
        fig_c = go.Figure([go.Bar(x=['Airbnb', 'Tradicional'], y=[flujo_neto_air*12, u_mes_trad*12], marker_color=['#3b82f6', '#10b981'], text=[f"S/. {flujo_neto_air*12:,.0f}", f"S/. {u_mes_trad*12:,.0f}"], textposition='inside', insidetextanchor='middle', textfont=dict(size=22, family="Arial Black"))])
        fig_c.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_c, use_container_width=True)

    if st.button("✅ Finalizar Auditoría"): st.balloons()
