import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Auditoría Inmobiliaria | Jancarlo Mendoza", layout="wide")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Acceso Consultoría")
    password = st.text_input("Contraseña:", type="password")
    if st.button("Ingresar"):
        if password == "Jancarlo2026":
            st.session_state.authenticated = True
            st.rerun()
else:
    # --- ESTILOS ---
    st.markdown("""
        <style>
        [data-testid="stMetricValue"] { font-size: 1.4rem !important; }
        .info-text { font-size: 0.8rem; color: #a1a1a1; margin-top: 4px; }
        .section-title { color: #3b82f6; font-size: 1.2rem; font-weight: bold; margin-top: 15px; }
        </style>
        """, unsafe_allow_html=True)

    # --- 2. SIDEBAR ---
    with st.sidebar:
        st.header("⚙️ Parámetros Base")
        val_depa = st.number_input("Precio Inmueble (S/.)", value=250000)
        tcea = st.number_input("TCEA %", value=9.5)
        plazo = st.selectbox("Plazo (Años)", [10, 15, 20, 25], index=2)
        st.write("---")
        tarifa = st.number_input("Tarifa Airbnb/Día", value=180)
        ocupacion = st.slider("Días ocupados/mes", 1, 30, 20)
        st.write("---")
        plusvalia_anual = st.slider("Plusvalía Anual Est. %", 0.0, 8.0, 4.0)
        renta_trad = st.number_input("Renta Tradicional/Mes", value=1800)

    # --- 3. CÁLCULOS ---
    inicial = val_depa * 0.20
    prestamo = val_depa - inicial
    tem = (1 + tcea/100)**(1/12) - 1
    cuota = prestamo * (tem * (1 + tem)**(plazo*12)) / ((1 + tem)**(plazo*12) - 1)
    gastos_fijos_mes = (val_depa * 0.03) / 12
    
    # Airbnb con Impuestos (Régimen MYPE/Especial estimado 10% sobre neta o 5% bruto)
    ingreso_bruto_mes = tarifa * ocupacion * 0.85
    utilidad_pre_impuesto = ingreso_bruto_mes - cuota - gastos_fijos_mes
    impuesto_air = ingreso_bruto_mes * 0.05 # Estimado 5% arbitrio/renta
    flujo_neto_air = utilidad_pre_impuesto - impuesto_air

    # --- 4. TABS ---
    t1, t2, t3 = st.tabs(["📊 Flujo y Payback", "📈 Plusvalía y Patrimonio", "🛡️ Escenarios de Riesgo"])

    with t1:
        st.markdown('<div class="section-title">Análisis de Flujo de Caja</div>', unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        m1.metric("Flujo Neto Mensual", f"S/. {flujo_neto_air:,.2f}")
        m2.metric("ROI Anual", f"{(flujo_neto_air*12/inicial)*100:.2f}%")
        m3.metric("Punto Equilibrio", f"{np.ceil((cuota + gastos_fijos_mes)/(tarifa*0.85)):.0f} días")
        
        # Gráfico Payback
        años_proy = 15
        eje_x = np.linspace(0, años_proy, años_proy * 12 + 1)
        flujo_acum = [-inicial]
        for m in range(1, len(eje_x)): flujo_acum.append(flujo_acum[-1] + flujo_neto_air)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=eje_x, y=flujo_acum, fill='tozeroy', line_color='#3b82f6'))
        fig.update_layout(height=300, title="Recuperación de Capital (Años)", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig, use_container_width=True)

    with t2:
        st.markdown('<div class="section-title">Crecimiento Patrimonial (Plusvalía)</div>', unsafe_allow_html=True)
        st.write("Análisis de cuánto valdrá la propiedad y cómo crece el capital del cliente.")
        
        años = list(range(0, 11))
        valor_propiedad = [val_depa * (1 + plusvalia_anual/100)**a for a in años]
        equity = [v - (prestamo * (1 - a/plazo) if a < plazo else 0) for a, v in zip(años, valor_propiedad)]
        
        fig_patrimonio = go.Figure()
        fig_patrimonio.add_trace(go.Bar(x=años, y=valor_propiedad, name="Valor Mercado Inmueble", marker_color='#1f2630'))
        fig_patrimonio.add_trace(go.Scatter(x=años, y=equity, name="Patrimonio Real (Valor - Deuda)", line=dict(color='#00ffcc', width=4)))
        fig_patrimonio.update_layout(height=400, barmode='overlay', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_patrimonio, use_container_width=True)
        
        ganancia_10a = valor_propiedad[10] - val_depa
        st.info(f"💰 **Efecto Plusvalía:** En 10 años, la propiedad habrá ganado S/. {ganancia_10a:,.0f} en valor, adicionales al flujo de renta.")

    with t3:
        st.markdown('<div class="section-title">Prueba de Estrés: Escenarios</div>', unsafe_allow_html=True)
        
        col_esc, col_det = st.columns([1, 1.5])
        with col_esc:
            escenario = st.radio("Selecciona Escenario:", ["Conservador (Actual)", "Optimista (Lleno)", "Crisis (Vacancia Alta)"])
            
            if escenario == "Optimista (Lleno)":
                e_occ, e_tar = 26, tarifa * 1.1
            elif escenario == "Crisis (Vacancia Alta)":
                e_occ, e_tar = 12, tarifa * 0.9
            else:
                e_occ, e_tar = ocupacion, tarifa

            e_ingreso = e_tar * e_occ * 0.85
            e_flujo = e_ingreso - cuota - gastos_fijos_mes - (e_ingreso * 0.05)
            
        with col_det:
            st.metric("Flujo Neto en este Escenario", f"S/. {e_flujo:,.2f}", delta=f"{e_flujo - flujo_neto_air:,.2f}")
            if e_flujo < 0:
                st.error("🚨 En este escenario, el cliente debe aportar capital propio para pagar la cuota.")
            else:
                st.success("✅ El proyecto resiste este escenario sin requerir inyección de capital.")

        # Comparativa Tradicional Final
        st.write("---")
        u_mes_trad = renta_trad - cuota - (val_depa * 0.015 / 12) - (renta_trad * 0.05) # Incluye 5% impuesto 1ra cat
        
        st.markdown(f"**Comparativa vs Tradicional (Post-Impuestos):**")
        c_a, c_t = st.columns(2)
        c_a.metric("Airbnb ROI", f"{(flujo_neto_air*12/inicial)*100:.1f}%")
        c_t.metric("Tradicional ROI", f"{(u_mes_trad*12/inicial)*100:.1f}%")
