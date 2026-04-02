import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- 1. CONFIGURACIÓN Y SEGURIDAD (CONGELADO) ---
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
        .highlight-card { background-color: #1e293b; padding: 20px; border-radius: 10px; border: 1px solid #3b82f6; text-align: center; margin-bottom: 20px; }
        </style>
        """, unsafe_allow_html=True)

    # --- 2. SIDEBAR (CONGELADO) ---
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

    # --- 3. LÓGICA FINANCIERA (CONGELADO) ---
    inicial_banco = val_depa * 0.20
    inversion_total_real = inicial_banco + inv_amoblado
    prestamo = val_depa - inicial_banco
    tem = (1 + tcea/100)**(1/12) - 1
    cuota = prestamo * (tem * (1 + tem)**(plazo_años*12)) / ((1 + tem)**(plazo_años*12) - 1)
    mantenimiento_mes = (val_depa * 0.03) / 12
    ingreso_bruto_air = tarifa * ocupacion_act * 0.85
    impuesto_air = ingreso_bruto_air * 0.05
    flujo_neto_air = ingreso_bruto_air - cuota - mantenimiento_mes - impuesto_air
    roi_anual_air = (flujo_neto_air * 12 / inversion_total_real) * 100
    breakeven_dias = (cuota + mantenimiento_mes) / (tarifa * 0.85 * 0.95)
    
    # Renta Tradicional: Gastos estimados menores (1.5% anual mantenim., 5% impuesto)
    u_anual_trad = (renta_trad - cuota - (val_depa*0.015/12) - (renta_trad*0.05)) * 12
    roi_trad = (u_anual_trad / inversion_total_real) * 100

    # --- 4. TABS ---
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Flujos", "📈 Plusvalía", "🛡️ Sensibilidad", "🔄 Airbnb vs Tradicional"])

    # --- PESTAÑA 1 & 2 (CONGELADAS) ---
    with tab1:
        st.markdown('<div class="section-title">💰 Estructura de Desembolso Inicial</div>', unsafe_allow_html=True)
        st.metric("Inversión Total", f"S/. {inversion_total_real:,.0f}")
        st.markdown(f'<p class="info-text">Suma de Cuota Inicial (S/. {inicial_banco:,.0f}) + Equipamiento Airbnb (S/. {inv_amoblado:,.0f}).</p>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📉 Flujo de Caja Operativo</div>', unsafe_allow_html=True)
        st.table(pd.DataFrame({"Concepto": ["Ingresos (Airbnb)", "Cuota Hipotecaria", "Gastos Fijos", "Impuestos", "UTILIDAD NETA"], "Mensual": [f"S/. {ingreso_bruto_air:,.2f}", f"S/. -{cuota:,.2f}", f"S/. -{mantenimiento_mes:,.2f}", f"S/. -{impuesto_air:,.2f}", f"S/. {flujo_neto_air:,.2f}"], "Anual": [f"S/. {ingreso_bruto_air*12:,.2f}", f"S/. -{cuota*12:,.2f}", f"S/. -{mantenimiento_mes*12:,.2f}", f"S/. -{impuesto_air*12:,.2f}", f"S/. {flujo_neto_air*12:,.2f}"]}))
        st.markdown('<div class="section-title">🎯 Benchmark de Mercado</div>', unsafe_allow_html=True)
        col_roi, col_bench = st.columns([1, 1.5])
        with col_roi: st.metric("Tu ROI Anual Real", f"{roi_anual_air:.2f}%")
        with col_bench: st.markdown(f"""<div class="compare-card"><b>📊 Referencias de Mercado:</b><br><span style='color:#8899a6'>• Depósito Fijo:</span> 6.8% | <span style='color:#8899a6'>• Caja:</span> 7.5%<br><span style='color:#8899a6'>• Fondos:</span> 8.2% | <span style='color:#8899a6'>• Tradicional:</span> 4.5%<br><span style='color: #00ffcc'>• Tu Airbnb: <b>{roi_anual_air:.2f}%</b></span></div>""", unsafe_allow_html=True)
        st.markdown('<div class="section-title">📅 Payback</div>', unsafe_allow_html=True)
        años_pb = 25; meses_pb = np.arange(0, años_pb * 12 + 1); flujo_acum = [-inversion_total_real]; año_rec = None
        for m in meses_pb[1:]:
            u_mes = flujo_neto_air if m <= (plazo_años * 12) else (ingreso_bruto_air - mantenimiento_mes - impuesto_air)
            flujo_acum.append(flujo_acum[-1] + u_mes)
            if año_rec is None and flujo_acum[-1] >= 0: año_rec = m / 12
        if año_rec: st.markdown(f"""<div class="highlight-card"><span style="color: #3b82f6; font-size: 2.2rem; font-weight: bold;">{año_rec:.1f} Años</span><br><span style="color: #00ffcc; font-size: 0.9rem;">Recuperación de S/. {inversion_total_real:,.0f}</span></div>""", unsafe_allow_html=True)
        fig_pb = go.Figure(); f_np = np.array(flujo_acum); fig_pb.add_trace(go.Scatter(x=meses_pb/12, y=np.where(f_np <= 0, f_np, 0), fill='tozeroy', fillcolor='rgba(239, 68, 68, 0.2)', line=dict(color='rgba(0,0,0,0)'), name="Recuperación")); fig_pb.add_trace(go.Scatter(x=meses_pb/12, y=np.where(f_np >= 0, f_np, 0), fill='tozeroy', fillcolor='rgba(16, 185, 129, 0.2)', line=dict(color='rgba(0,0,0,0)'), name="Ganancia")); fig_pb.add_trace(go.Scatter(x=meses_pb/12, y=flujo_acum, line=dict(color='#3b82f6', width=4), name="Saldo")); fig_pb.add_hline(y=0, line_dash="dash", line_color="white"); fig_pb.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", xaxis_title="Años"); st.plotly_chart(fig_pb, use_container_width=True)

    with tab2:
        st.markdown('<div class="section-title">📈 Plusvalía: El Valor del Tiempo</div>', unsafe_allow_html=True)
        plus_val = st.slider("Plusvalía Anual (%)", 0.0, 10.0, 4.0)
        col_5, col_10, col_15, col_20 = st.columns(4)
        col_5.metric("Valorización 5 años", f"S/. {(val_depa * (1 + plus_val/100)**5) - val_depa:,.0f}")
        col_10.metric("Valorización 10 años", f"S/. {(val_depa * (1 + plus_val/100)**10) - val_depa:,.0f}")
        col_15.metric("Valorización 15 años", f"S/. {(val_depa * (1 + plus_val/100)**15) - val_depa:,.0f}")
        col_20.metric("Valorización 20 años", f"S/. {(val_depa * (1 + plus_val/100)**20) - val_depa:,.0f}")
        años_p = np.arange(0, 26); v_mkt = [val_depa * (1 + plus_val/100)**a for a in años_p]; s_deuda = [prestamo * (1 - a/plazo_años) if a < plazo_años else 0 for a in años_p]; eq = [v - d for v, d in zip(v_mkt, s_deuda)]
        fig_p = go.Figure(); fig_p.add_trace(go.Bar(x=años_p, y=v_mkt, name="Valor Propiedad", marker_color='#1f2630')); fig_p.add_trace(go.Scatter(x=años_p, y=eq, name="Equity", fill='tozeroy', line=dict(color='#00ffcc', width=3)))
        fig_p.update_layout(height=400, barmode='overlay', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", title="Patrimonio vs Deuda"); st.plotly_chart(fig_p, use_container_width=True)

    # --- PESTAÑA 3: SENSIBILIDAD (ACTUALIZADA) ---
    with tab3:
        st.markdown('<div class="section-title">🛡️ Escenarios de Estrés (Sensibilidad)</div>', unsafe_allow_html=True)
        st.markdown('<p class="section-desc">¿Cómo responde el ROI ante cambios en la ocupación y la tarifa? Análisis de volatilidad.</p>', unsafe_allow_html=True)
        
        st.metric("Punto de Equilibrio Crítico", f"{np.ceil(breakeven_dias):.0f} días/mes", help="Días mínimos para que el flujo de caja sea S/. 0.")

        # Grafico 1: ROI vs Ocupación
        st.markdown('<div class="section-title">📉 1. ROI vs Días de Ocupación</div>', unsafe_allow_html=True)
        col_o1, col_o2 = st.columns([1, 2])
        d_range = list(range(5, 31))
        roi_o = [((((tarifa * d * 0.85 * 0.95) - cuota - mantenimiento_mes) * 12 / inversion_total_real) * 100) for d in d_range]
        with col_o1:
            st.dataframe(pd.DataFrame({"Días": [f"{d}d" for d in [10, 15, 20, 25, 30]], "ROI %": [roi_o[d_range.index(d)] for d in [10, 15, 20, 25, 30]]}).style.format({"ROI %": "{:.1f}%"}).background_gradient(cmap='RdYlGn'), hide_index=True)
        with col_o2:
            fig_o = go.Figure(go.Scatter(x=d_range, y=roi_o, line=dict(color='#3b82f6', width=3), name="Curva ROI"))
            fig_o.add_hline(y=0, line_dash="dot", line_color="red")
            fig_o.update_layout(height=250, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", xaxis_title="Días/Mes")
            st.plotly_chart(fig_o, use_container_width=True)

        # Grafico 2: ROI vs Tarifa
        st.markdown('<div class="section-title">📈 2. ROI vs Tarifa Diaria</div>', unsafe_allow_html=True)
        col_t1, col_t2 = st.columns([1, 2])
        t_range = list(range(int(tarifa*0.5), int(tarifa*1.5), 10))
        roi_t = [((((t * ocupacion_act * 0.85 * 0.95) - cuota - mantenimiento_mes) * 12 / inversion_total_real) * 100) for t in t_range]
        with col_t1:
            st.dataframe(pd.DataFrame({"Tarifa (S/)": [f"S/ {t}" for t in t_range[::2]], "ROI %": roi_t[::2]}).style.format({"ROI %": "{:.1f}%"}).background_gradient(cmap='RdYlGn'), hide_index=True)
        with col_t2:
            fig_t = go.Figure(go.Scatter(x=t_range, y=roi_t, line=dict(color='#00ffcc', width=3)))
            fig_t.add_hline(y=0, line_dash="dot", line_color="red")
            fig_t.update_layout(height=250, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", xaxis_title="Tarifa por Noche")
            st.plotly_chart(fig_t, use_container_width=True)

    # --- PESTAÑA 4: COMPARATIVA (NUEVA) ---
    with tab4:
        st.markdown('<div class="section-title">🔄 Análisis Comparativo: Airbnb vs Tradicional</div>', unsafe_allow_html=True)
        st.markdown('<p class="section-desc">Comparación directa de rentabilidad neta anual y eficiencia del capital.</p>', unsafe_allow_html=True)
        
        # Datos Importantes
        c_comp1, c_comp2, c_comp3 = st.columns(3)
        c_comp1.metric("Ventaja Airbnb (Anual)", f"S/. {(flujo_neto_air*12) - u_anual_trad:,.0f}")
        c_comp2.metric("Eficiencia Airbnb", f"{(roi_anual_air/roi_trad):.1f}x", help="Cuántas veces más rentable es Airbnb frente al tradicional.")
        c_comp3.metric("Riesgo de Vacancia", "Moderado", help="Airbnb depende de flujo diario, Tradicional de un solo contrato.")

        st.write("---")
        
        # Gráfico de Utilidad Neta (Movido de Tab 3)
        fig_c = go.Figure([go.Bar(x=['Airbnb (Corto Plazo)', 'Renta Tradicional'], y=[flujo_neto_air*12, u_anual_trad], marker_color=['#3b82f6', '#10b981'], text=[f"S/. {flujo_neto_air*12:,.0f}", f"S/. {u_anual_trad:,.0f}"], textposition='inside')])
        fig_c.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", title="Utilidad Neta Anual (Cashflow Libre)")
        st.plotly_chart(fig_c, use_container_width=True)
        
        st.markdown("""
        <div class="compare-card">
            <b>📌 Notas Estratégicas del Análisis:</b><br><br>
            <span style='color:#8899a6'>• <b>Impuestos:</b> Ambos consideran el 5% de SUNAT, pero Airbnb permite una mayor rotación de precios.</span><br>
            <span style='color:#8899a6'>• <b>Mantenimiento:</b> El modelo tradicional desgasta menos el inmueble, pero el modelo Airbnb permite inspecciones constantes.</span><br>
            <span style='color:#8899a6'>• <b>Capital:</b> Aunque Airbnb requiere S/. 25,000 extra de inversión, la velocidad de recuperación (ROI) suele compensarlo en menos de 2 años.</span>
        </div>
        """, unsafe_allow_html=True)

    if st.button("✅ Finalizar Auditoría"): st.balloons()
