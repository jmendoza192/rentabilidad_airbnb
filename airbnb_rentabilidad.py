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

    # --- 3. LÓGICA FINANCIERA BASE ---
    inicial = val_depa * 0.20
    prestamo = val_depa - inicial
    tem = (1 + tcea/100)**(1/12) - 1
    cuota = prestamo * (tem * (1 + tem)**(plazo_años*12)) / ((1 + tem)**(plazo_años*12) - 1)
    gastos_fijos_mes = (val_depa * 0.03) / 12 # Mantenimiento, arbitrios, seguros est.
    
    # Airbnb (Impuesto 5% sobre Bruto)
    ingreso_bruto_mes = tarifa * ocupacion_act * 0.85
    impuesto_air = ingreso_bruto_mes * 0.05
    utilidad_neta_mes = ingreso_bruto_mes - cuota - gastos_fijos_mes - impuesto_air
    
    # --- 4. TABS ---
    tab1, tab2, tab3 = st.tabs(["📊 Proyección de Flujos", "📈 Plusvalía y Patrimonio", "🛡️ Análisis de Riesgo"])

    with tab1:
        st.markdown('<div class="section-title">📊 Proyección de Ingresos, Egresos y Utilidad (25 Años)</div>', unsafe_allow_html=True)
        st.markdown('<p class="section-desc">Evolución del flujo de caja. Observe el incremento de utilidad al finalizar la hipoteca.</p>', unsafe_allow_html=True)

        años_proyeccion = 25
        meses = np.arange(1, años_proyeccion * 12 + 1)
        
        # Generar arrays de datos
        ingresos_linea = np.full(len(meses), ingreso_bruto_mes)
        # Egresos: Gastos fijos + Impuestos siempre. Cuota solo hasta el fin del plazo.
        egresos_linea = []
        for m in meses:
            costo_operativo = gastos_fijos_mes + impuesto_air
            costo_financiero = cuota if m <= (plazo_años * 12) else 0
            egresos_linea.append(costo_operativo + costo_financiero)
        
        utilidad_linea = ingresos_linea - np.array(egresos_linea)

        # Gráfico de Áreas Apiladas / Líneas
        fig_flujos = go.Figure()
        fig_flujos.add_trace(go.Scatter(x=meses/12, y=ingresos_linea, name="Ingreso Bruto", line=dict(color='#3b82f6', width=2)))
        fig_flujos.add_trace(go.Scatter(x=meses/12, y=egresos_linea, name="Egresos Totales (Inc. Hipoteca)", line=dict(color='#ef4444', width=2)))
        fig_flujos.add_trace(go.Scatter(x=meses/12, y=utilidad_linea, name="Utilidad Neta (Cashflow)", fill='tozeroy', line=dict(color='#10b981', width=3)))
        
        # Anotación del fin de deuda
        fig_flujos.add_vline(x=plazo_años, line_dash="dash", line_color="orange")
        fig_flujos.add_annotation(x=plazo_años, y=ingreso_bruto_mes, text="Fin de Deuda", showarrow=True, arrowhead=1, bgcolor="orange")

        fig_flujos.update_layout(height=450, margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor='rgba(0,0,0,0)', 
                                 plot_bgcolor='rgba(0,0,0,0)', font_color="white", xaxis_title="Años", yaxis_title="Soles (S/.)")
        st.plotly_chart(fig_flujos, use_container_width=True)

        col_inf1, col_inf2 = st.columns(2)
        with col_inf1:
            st.info(f"💡 **Etapa de Pago:** Utilidad neta de S/. {utilidad_neta_mes:,.2f} mensual.")
        with col_inf2:
            st.success(f"🔓 **Etapa Libre:** Tras el año {plazo_años}, la utilidad neta sube a S/. {ingreso_bruto_mes - gastos_fijos_mes - impuesto_air:,.2f} mensual.")

    with tab2:
        st.markdown('<div class="section-title">📈 Crecimiento Patrimonial y Plusvalía</div>', unsafe_allow_html=True)
        
        # Input de plusvalía movido aquí
        plus_input = st.slider("Tasa de Plusvalía Anual Estimada (%)", 0.0, 10.0, 4.0, help="Aumento anual del valor comercial del inmueble.")
        
        años_pat = np.arange(0, 26)
        val_mkt = [val_depa * (1 + plus_input/100)**a for a in años_pat]
        # Cálculo amortización lineal simplificada para visualización de equity
        saldo_deuda = [prestamo * (1 - a/plazo_años) if a < plazo_años else 0 for a in años_pat]
        equity = [v - d for v, d in zip(val_mkt, saldo_deuda)]

        fig_pat = go.Figure()
        fig_pat.add_trace(go.Bar(x=años_pat, y=val_mkt, name="Valor de Mercado", marker_color='#1f2630'))
        fig_pat.add_trace(go.Scatter(x=años_pat, y=equity, name="Patrimonio Real (Equity)", fill='tozeroy', line=dict(color='#00ffcc', width=4)))
        
        fig_pat.update_layout(height=450, barmode='overlay', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                               font_color="white", xaxis_title="Años", yaxis_title="Soles")
        st.plotly_chart(fig_pat, use_container_width=True)
        
        st.markdown(f"""
        <div class="mini-card">
            <b>Valor proyectado (Año 25):</b> S/. {val_mkt[-1]:,.0f}<br>
            <b>Plusvalía acumulada:</b> S/. {val_mkt[-1] - val_depa:,.0f}
        </div>
        """, unsafe_allow_html=True)

    with tab3:
        # Recuperamos el Análisis de Sensibilidad y el Duelo de Estrategias
        st.markdown('<div class="section-title">🛡️ Análisis de Sensibilidad Operativa</div>', unsafe_allow_html=True)
        
        col_be, col_res = st.columns([1, 2])
        with col_be:
            st.metric("Punto Equilibrio", f"{np.ceil(breakeven_dias):.0f} días")
            st.markdown('<p class="info-text">Noches para flujo cero.</p>', unsafe_allow_html=True)
        
        col_t, col_l = st.columns([1, 2])
        dias_tabla = [5, 10, 15, 20, 25, 30]
        # Recálculo ROI incluyendo impuesto 5%
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
        st.markdown('<div class="section-title">⚖️ Airbnb vs. Tradicional (Anual)</div>', unsafe_allow_html=True)
        
        # Tradicional Recálculo
        impuesto_trad = renta_trad * 0.05
        u_anual_trad = (renta_trad - cuota - (val_depa * 0.015 / 12) - impuesto_trad) * 12
        u_anual_air = flujo_neto_air * 12

        labels = ['Airbnb', 'Tradicional']
        valores = [u_anual_air, u_anual_trad]
        
        fig_comp = go.Figure([go.Bar(x=labels, y=valores, marker_color=['#3b82f6', '#10b981'], 
                                     text=[f"S/. {v:,.0f}" for v in valores], textposition='inside', insidetextanchor='middle', 
                                     textfont=dict(size=22, family="Arial Black", color="white"))])
        fig_comp.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_comp, use_container_width=True)

    if st.button("✅ Finalizar Auditoría"): st.balloons()
