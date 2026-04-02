import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

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
    gastos_trad_mes = (val_depa * 0.015) / 12
    u_mes_trad = renta_trad - cuota - gastos_trad_mes
    roi_trad = (u_mes_trad * 12 / inicial) * 100

    # --- 4. DASHBOARD ---
    st.title("🎯 Auditoría de Inversión: Estrategia Airbnb")
    
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Cuota Mensual", f"S/. {cuota:,.2f}")
        st.markdown('<p class="info-text">Obligación fija con el banco.</p>', unsafe_allow_html=True)
    with m2:
        st.metric("Punto Equilibrio", f"{np.ceil(breakeven_dias):.0f} días")
        st.markdown('<p class="info-text">Mínimo para flujo de caja cero.</p>', unsafe_allow_html=True)
    with m3:
        st.metric("Flujo Neto/Mes", f"S/. {ingreso_neto_mes_air:,.2f}")
        st.markdown('<p class="info-text">Efectivo libre tras gastos e hipoteca.</p>', unsafe_allow_html=True)
    with m4:
        st.metric("ROI s/ Inicial", f"{roi_anual_air:.2f}%")
        st.markdown('<p class="info-text">Rentabilidad Cash-on-Cash anual.</p>', unsafe_allow_html=True)

    st.write("---")

    # SECCIÓN: PAYBACK (CON SOMBREADO CONDICIONAL)
    st.markdown('<div class="section-title">📅 Payback: Recuperación del Capital en el Tiempo</div>', unsafe_allow_html=True)
    
    años_proy = 15
    eje_x_años = np.linspace(0, años_proy, años_proy * 12 + 1)
    flujo_acum = [-inicial]
    for m in range(1, len(eje_x_años)):
        flujo_acum.append(flujo_acum[-1] + ingreso_neto_mes_air)

    fig_payback = go.Figure()
    # Separar datos positivos y negativos para el sombreado
    flujo_np = np.array(flujo_acum)
    
    fig_payback.add_trace(go.Scatter(x=eje_x_años, y=np.where(flujo_np <= 0, flujo_np, 0),
                                     fill='tozeroy', fillcolor='rgba(255, 0, 0, 0.2)',
                                     line=dict(color='rgba(255, 0, 0, 0)'), name="Zona de Recuperación"))
    
    fig_payback.add_trace(go.Scatter(x=eje_x_años, y=np.where(flujo_np >= 0, flujo_np, 0),
                                     fill='tozeroy', fillcolor='rgba(0, 255, 0, 0.2)',
                                     line=dict(color='rgba(0, 255, 0, 0)'), name="Zona de Ganancia"))
    
    fig_payback.add_trace(go.Scatter(x=eje_x_años, y=flujo_acum, line=dict(color='#3b82f6', width=3), name="Flujo Neto"))
    fig_payback.add_hline(y=0, line_dash="dash", line_color="white")

    fig_payback.update_layout(height=400, margin=dict(l=20, r=20, t=10, b=20), paper_bgcolor='rgba(0,0,0,0)', 
                              plot_bgcolor='rgba(0,0,0,0)', font_color="white", xaxis_title="Tiempo (Años)", yaxis_title="Soles (S/.)")
    st.plotly_chart(fig_payback, use_container_width=True)
    st.info(f"💡 **Punto de Retorno:** La transición del rojo al verde marca el momento exacto en que la inversión se vuelve 'dinero gratis'.")

    # SECCIÓN: SENSIBILIDAD CON CUADRO LATERAL
    st.write("---")
    st.markdown('<div class="section-title">📊 Análisis de Sensibilidad: ROI vs. Ocupación</div>', unsafe_allow_html=True)
    
    col_table, col_line = st.columns([1, 2])
    
    dias_rango = list(range(5, 31))
    roi_rango = [(((tarifa * d * 0.85) - cuota - gastos_fijos_mes) * 12 / inicial) * 100 for d in dias_rango]
    
    with col_table:
        df_sens = pd.DataFrame({"Días": dias_rango, "ROI %": roi_rango})
        st.dataframe(df_sens.style.format({"ROI %": "{:.1f}%"}).background_gradient(cmap='RdYlGn'), height=350, hide_index=True)
    
    with col_line:
        fig_sens = go.Figure()
        fig_sens.add_trace(go.Scatter(x=dias_rango, y=roi_rango, mode='lines+markers', line_color='#00ffcc', name="ROI %"))
        fig_sens.add_hline(y=0, line_dash="dot", line_color="red")
        fig_sens.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)', 
                               plot_bgcolor='rgba(0,0,0,0)', font_color="white", xaxis_title="Días/Mes", yaxis_title="ROI %")
        st.plotly_chart(fig_sens, use_container_width=True)
    st.warning(f"⚠️ **ROI 0%:** Se alcanza a los **{np.ceil(breakeven_dias):.0f} días**. Por debajo de este punto, el inversor debe inyectar capital mensual.")

    # SECCIÓN: COMPARATIVA FINAL (ESTILO MEJORADO)
    st.write("---")
    st.markdown('<div class="section-title">⚖️ Duelo de Estrategias: Airbnb vs. Tradicional</div>', unsafe_allow_html=True)
    
    col_res, col_graf = st.columns([1, 1.5])
    with col_res:
        st.markdown(f"""
        <div class="mini-card">
            <b>🏠 Airbnb ({ocupacion_act} días)</b><br>
            • Ingreso Bruto: S/. {tarifa * ocupacion_act * 12:,.0f}<br>
            • ROI: <b>{roi_anual_air:.1f}%</b><br><br>
            <b>🏢 Tradicional</b><br>
            • Ingreso Bruto: S/. {renta_trad * 12:,.0f}<br>
            • ROI: <b>{roi_trad:.1f}%</b><br><br>
            <i>Diferencia de flujo anual: S/. {abs((ingreso_neto_mes_air - u_mes_trad)*12):,.2f}</i>
        </div>
        """, unsafe_allow_html=True)

    with col_graf:
        labels = ['Utilidad Anual Airbnb', 'Utilidad Anual Tradicional']
        valores = [ingreso_neto_mes_air * 12, u_mes_trad * 12]
        
        fig_comp = go.Figure([go.Bar(
            x=labels, y=valores, 
            marker_color=['#3b82f6', '#10b981'],
            text=[f"S/. {v:,.0f}" for v in valores],
            textposition='inside',
            textfont=dict(size=18, family="Arial Black", color="white")
        )])
        
        fig_comp.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10), 
                               paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_comp, use_container_width=True)

    if st.button("✅ Finalizar Auditoría"): st.balloons()
