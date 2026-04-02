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
    st.markdown('<p class="section-desc">Resumen ejecutivo del rendimiento financiero actual del proyecto.</p>', unsafe_allow_html=True)
    
    m1, m2, m3 = st.columns(3) # Reducido a 3 para mover Punto de Equilibrio
    with m1:
        st.metric("Cuota Mensual", f"S/. {cuota:,.2f}")
        st.markdown('<p class="info-text">Obligación hipotecaria fija estimada según TCEA y plazo.</p>', unsafe_allow_html=True)
    with m2:
        st.metric("Flujo Neto/Mes", f"S/. {ingreso_neto_mes_air:,.2f}")
        st.markdown('<p class="info-text">Efectivo libre (EBITDA) tras gastos operativos e hipoteca.</p>', unsafe_allow_html=True)
    with m3:
        st.metric("ROI s/ Inicial", f"{roi_anual_air:.2f}%")
        st.markdown('<p class="info-text">Retorno anual sobre el capital inicial desembolsado.</p>', unsafe_allow_html=True)

    st.write("---")

    # SECCIÓN: PAYBACK
    st.markdown('<div class="section-title">📅 Payback: Recuperación del Capital en el Tiempo</div>', unsafe_allow_html=True)
    st.markdown('<p class="section-desc">Visualización de la línea de tiempo hasta la recuperación total del desembolso inicial.</p>', unsafe_allow_html=True)
    
    años_proy = 15
    eje_x_años = np.linspace(0, años_proy, años_proy * 12 + 1)
    flujo_acum = [-inicial]
    for m in range(1, len(eje_x_años)):
        flujo_acum.append(flujo_acum[-1] + ingreso_neto_mes_air)

    fig_payback = go.Figure()
    flujo_np = np.array(flujo_acum)
    
    fig_payback.add_trace(go.Scatter(x=eje_x_años, y=np.where(flujo_np <= 0, flujo_np, 0),
                                     fill='tozeroy', fillcolor='rgba(255, 0, 0, 0.2)',
                                     line=dict(color='rgba(255, 0, 0, 0)'), showlegend=False))
    
    fig_payback.add_trace(go.Scatter(x=eje_x_años, y=np.where(flujo_np >= 0, flujo_np, 0),
                                     fill='tozeroy', fillcolor='rgba(0, 255, 0, 0.2)',
                                     line=dict(color='rgba(0, 255, 0, 0)'), showlegend=False))
    
    fig_payback.add_trace(go.Scatter(x=eje_x_años, y=flujo_acum, line=dict(color='#3b82f6', width=3), name="Flujo Acumulado"))
    fig_payback.add_hline(y=0, line_dash="dash", line_color="white")

    fig_payback.update_layout(height=350, margin=dict(l=20, r=20, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)', 
                              plot_bgcolor='rgba(0,0,0,0)', font_color="white", xaxis_title="Años", yaxis_title="Soles (S/.)")
    st.plotly_chart(fig_payback, use_container_width=True)
    
    if ingreso_neto_mes_air > 0:
        meses_retorno = inicial / ingreso_neto_mes_air
        años_retorno = meses_retorno / 12
        st.markdown(f"""<div class="payback-card">🚀 <b>PUNTO DE EQUILIBRIO FINANCIERO:</b> Recuperas tu inversión inicial (S/. {inicial:,.0f}) en aproximadamente <b>{años_retorno:.1f} años</b>.</div>""", unsafe_allow_html=True)
    else:
        st.error("⚠️ El flujo es negativo. La inversión no se recupera bajo estos parámetros.")

    st.write("---")

    # SECCIÓN: SENSIBILIDAD (CON PUNTO DE EQUILIBRIO AQUÍ)
    st.markdown('<div class="section-title">📊 Análisis de Sensibilidad: ROI vs. Ocupación</div>', unsafe_allow_html=True)
    st.markdown('<p class="section-desc">Evaluación del riesgo operativo y rentabilidad según variaciones en la vacancia.</p>', unsafe_allow_html=True)
    
    # Tarjeta de Punto de Equilibrio movida aquí
    col_be, col_empty = st.columns([1, 2])
    with col_be:
        st.metric("Punto Equilibrio Operativo", f"{np.ceil(breakeven_dias):.0f} días")
        st.markdown('<p class="info-text">Noches mínimas requeridas al mes para cubrir el 100% de los costos.</p>', unsafe_allow_html=True)
    
    st.write("") # Espacio
    
    col_table, col_line = st.columns([1, 2])
    dias_tabla = [5, 10, 15, 20, 25, 30]
    roi_tabla = [(((tarifa * d * 0.85) - cuota - gastos_fijos_mes) * 12 / inicial) * 100 for d in dias_tabla]
    dias_graf = list(range(5, 31))
    roi_graf = [(((tarifa * d * 0.85) - cuota - gastos_fijos_mes) * 12 / inicial) * 100 for d in dias_graf]
    
    with col_table:
        df_sens = pd.DataFrame({"Ocupación": [f"{d} días" for d in dias_tabla], "ROI %": roi_tabla})
        st.dataframe(df_sens.style.format({"ROI %": "{:.1f}%"}).background_gradient(cmap='RdYlGn', axis=0), height=250, hide_index=True, use_container_width=True)
        st.markdown('<p class="info-text">Tabla de proyección rápida de rentabilidad anual.</p>', unsafe_allow_html=True)
    
    with col_line:
        fig_sens = go.Figure()
        fig_sens.add_trace(go.Scatter(x=dias_graf, y=roi_graf, mode='lines', line=dict(color='#00ffcc', width=4)))
        fig_sens.add_hline(y=0, line_dash="dot", line_color="red")
        fig_sens.update_layout(height=250, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)', 
                               plot_bgcolor='rgba(0,0,0,0)', font_color="white", xaxis_title="Días/Mes", yaxis_title="ROI %")
        st.plotly_chart(fig_sens, use_container_width=True)
        st.markdown('<p class="info-text">La línea roja horizontal marca el límite de pérdida operativa.</p>', unsafe_allow_html=True)

    st.write("---")

    # SECCIÓN: COMPARATIVA FINAL
    st.markdown('<div class="section-title">⚖️ Duelo de Estrategias: Airbnb vs. Tradicional</div>', unsafe_allow_html=True)
    st.markdown('<p class="section-desc">Comparativa directa entre el modelo de renta vacacional y el alquiler convencional.</p>', unsafe_allow_html=True)
    
    col_res, col_graf = st.columns([1, 1.5])
    with col_res:
        st.markdown(f"""
        <div class="mini-card">
            <b>🏠 Airbnb ({ocupacion_act} días)</b><br>
            • Utilidad Anual: S/. {ingreso_neto_mes_air * 12:,.2f}<br>
            • ROI: <b>{roi_anual_air:.1f}%</b><br><br>
            <b>🏢 Tradicional</b><br>
            • Utilidad Anual: S/. {u_mes_trad * 12:,.2f}<br>
            • ROI: <b>{roi_trad:.1f}%</b>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<p class="info-text">El modelo tradicional ofrece estabilidad pero suele sacrificar rentabilidad potencial.</p>', unsafe_allow_html=True)

    with col_graf:
        labels = ['Airbnb', 'Tradicional']
        valores = [ingreso_neto_mes_air * 12, u_mes_trad * 12]
        fig_comp = go.Figure([go.Bar(
            x=labels, y=valores, 
            marker_color=['#3b82f6', '#10b981'],
            text=[f"S/. {v:,.0f}" for v in valores],
            textposition='inside',
            insidetextanchor='middle',
            textfont=dict(size=22, family="Arial Black", color="white")
        )])
        fig_comp.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10), 
                               paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_comp, use_container_width=True)
        st.markdown('<p class="info-text">Comparación visual de la utilidad neta anualizada (Soles).</p>', unsafe_allow_html=True)

    if st.button("✅ Finalizar Auditoría"): st.balloons()
