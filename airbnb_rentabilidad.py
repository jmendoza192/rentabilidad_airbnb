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
        .stTable { background-color: #161b22; border-radius: 10px; }
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

    # --- 3. LÓGICA FINANCIERA BASE ---
    inicial = val_depa * 0.20
    prestamo = val_depa - inicial
    tem = (1 + tcea/100)**(1/12) - 1
    cuota = prestamo * (tem * (1 + tem)**(plazo_años*12)) / ((1 + tem)**(plazo_años*12) - 1)
    mantenimiento_estimado = (val_depa * 0.03) / 12 # 3% anual aprox para Lima
    
    ingreso_bruto_mes = tarifa * ocupacion_act * 0.85 # Neto de comisión Airbnb
    impuesto_sunat = ingreso_bruto_mes * 0.05
    egresos_mes = cuota + mantenimiento_estimado + impuesto_sunat
    utilidad_neta_mes = ingreso_bruto_mes - egresos_mes
    roi_actual = (utilidad_neta_mes * 12 / inicial) * 100
    breakeven_dias = (cuota + mantenimiento_estimado) / (tarifa * 0.85 * 0.95)

    # --- 4. TABS ---
    tab1, tab2, tab3 = st.tabs(["📊 Proyección de Flujos", "📈 Plusvalía y Patrimonio", "🛡️ Análisis de Riesgo"])

    with tab1:
        st.markdown('<div class="section-title">📊 Resumen de Flujos: Ingresos, Egresos y Utilidad</div>', unsafe_allow_html=True)
        
        # CUADRO INFORMATIVO (TABLA)
        data_resumen = {
            "Concepto": ["Ingresos Brutos (Airbnb)", "Cuota Hipotecaria", "Mantenimiento / Otros", "Impuestos (Sunat)", "Egresos Totales", "Utilidad Neta"],
            "Mensual (S/.)": [f"S/. {ingreso_bruto_mes:,.2f}", f"S/. -{cuota:,.2f}", f"S/. -{mantenimiento_estimado:,.2f}", f"S/. -{impuesto_sunat:,.2f}", f"S/. -{egresos_mes:,.2f}", f"S/. {utilidad_neta_mes:,.2f}"],
            "Anual (S/.)": [f"S/. {ingreso_bruto_mes*12:,.2f}", f"S/. -{cuota*12:,.2f}", f"S/. -{mantenimiento_estimado*12:,.2f}", f"S/. -{impuesto_sunat*12:,.2f}", f"S/. -{egresos_mes*12:,.2f}", f"S/. {utilidad_neta_mes*12:,.2f}"]
        }
        df_resumen = pd.DataFrame(data_resumen)
        st.table(df_resumen)
        
        st.metric("ROI Actual sobre Inicial", f"{roi_actual:.2f}%")

        # GRÁFICO DE FLUJOS (25 AÑOS)
        años_proy = 25
        meses = np.arange(1, años_proy * 12 + 1)
        ingresos_linea = np.full(len(meses), ingreso_bruto_mes)
        egresos_linea = [(mantenimiento_estimado + impuesto_sunat + (cuota if m <= (plazo_años * 12) else 0)) for m in meses]
        utilidad_linea = ingresos_linea - np.array(egresos_linea)

        fig_flujos = go.Figure()
        fig_flujos.add_trace(go.Scatter(x=meses/12, y=ingresos_linea, name="Ingresos", line=dict(color='#3b82f6')))
        fig_flujos.add_trace(go.Scatter(x=meses/12, y=egresos_linea, name="Egresos", line=dict(color='#ef4444')))
        fig_flujos.add_trace(go.Scatter(x=meses/12, y=utilidad_linea, name="Utilidad Neta", fill='tozeroy', line=dict(color='#10b981', width=3)))
        fig_flujos.add_vline(x=plazo_años, line_dash="dash", line_color="orange")
        fig_flujos.update_layout(height=400, title="Evolución de Ingresos vs Egresos (Fin de deuda en año " + str(plazo_años) + ")", 
                                 paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_flujos, use_container_width=True)

        # GRÁFICO DE EVOLUCIÓN DEL ROI
        st.markdown('<div class="section-title">📈 Evolución del ROI Anualizado</div>', unsafe_allow_html=True)
        st.markdown('<p class="section-desc">Retorno sobre la inversión inicial según la etapa del crédito.</p>', unsafe_allow_html=True)
        
        roi_evolucion = [(u * 12 / inicial) * 100 for u in utilidad_linea]
        
        fig_roi = go.Figure()
        fig_roi.add_trace(go.Scatter(x=meses/12, y=roi_evolucion, name="ROI %", line=dict(color='#00ffcc', width=4), fill='tozeroy', fillcolor='rgba(0, 255, 204, 0.1)'))
        fig_roi.update_layout(height=350, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", 
                              xaxis_title="Años", yaxis_title="ROI %", yaxis=dict(ticksuffix="%"))
        st.plotly_chart(fig_roi, use_container_width=True)

    with tab2:
        st.markdown('<div class="section-title">📈 Crecimiento Patrimonial y Plusvalía</div>', unsafe_allow_html=True)
        plus_input = st.slider("Plusvalía Anual (%)", 0.0, 10.0, 4.0)
        años_pat = np.arange(0, 26)
        val_mkt = [val_depa * (1 + plus_input/100)**a for a in años_pat]
        saldo_d = [prestamo * (1 - a/plazo_años) if a < plazo_años else 0 for a in años_pat]
        equity = [v - d for v, d in zip(val_mkt, saldo_d)]
        fig_p = go.Figure()
        fig_p.add_trace(go.Bar(x=años_pat, y=val_mkt, name="Valor Mercado", marker_color='#1f2630'))
        fig_p.add_trace(go.Scatter(x=años_pat, y=equity, name="Equity (Patrimonio)", fill='tozeroy', line=dict(color='#00ffcc')))
        fig_p.update_layout(height=400, barmode='overlay', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_p, use_container_width=True)

    with tab3:
        st.markdown('<div class="section-title">🛡️ Análisis de Sensibilidad Operativa</div>', unsafe_allow_html=True)
        c_be, _ = st.columns([1, 2])
        c_be.metric("Punto Equilibrio", f"{np.ceil(breakeven_dias):.0f} días")
        col_t, col_l = st.columns([1, 2])
        d_tabla = [5, 10, 15, 20, 25, 30]
        r_tabla = [((((tarifa * d * 0.85 * 0.95) - cuota - mantenimiento_estimado) * 12 / inicial) * 100) for d in d_tabla]
        with col_t:
            df = pd.DataFrame({"Ocupación": [f"{d} d" for d in d_tabla], "ROI %": r_tabla})
            st.dataframe(df.style.format({"ROI %": "{:.1f}%"}).background_gradient(cmap='RdYlGn', axis=0), hide_index=True)
        with col_l:
            d_g = list(range(5, 31))
            r_g = [((((tarifa * d * 0.85 * 0.95) - cuota - mantenimiento_estimado) * 12 / inicial) * 100) for d in d_g]
            fig_s = go.Figure(go.Scatter(x=d_g, y=r_g, mode='lines', line=dict(color='#00ffcc', width=4)))
            fig_s.add_hline(y=0, line_dash="dot", line_color="red")
            fig_s.update_layout(height=250, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig_s, use_container_width=True)
        st.write("---")
        labels = ['Airbnb', 'Tradicional']
        valores = [flujo_neto_air * 12, (renta_trad - cuota - (val_depa*0.015/12) - (renta_trad*0.05)) * 12]
        fig_c = go.Figure([go.Bar(x=labels, y=valores, marker_color=['#3b82f6', '#10b981'], text=[f"S/. {v:,.0f}" for v in valores], textposition='inside', insidetextanchor='middle', textfont=dict(size=22, family="Arial Black"))])
        fig_c.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_c, use_container_width=True)

    if st.button("✅ Finalizar Auditoría"): st.balloons()
