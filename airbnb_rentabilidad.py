import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime

# =========================================================
# CONFIGURACIÓN Y ESTILOS (V37 BASE)
# =========================================================
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
        [data-testid="stMetricValue"] { font-size: 1.7rem !important; color: #00ffcc; font-weight: bold; }
        div[data-testid="stMetric"] { background-color: #1f2630; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
        .info-text { font-size: 0.85rem; color: #a1a1a1; margin-top: 5px; padding: 10px; border-left: 2px solid #3b82f6; background-color: #161b22; }
        .section-title { margin-top: 30px; margin-bottom: 15px; color: #3b82f6; font-size: 1.3rem; border-bottom: 1px solid #30363d; }
        .highlight-card { background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #3b82f6; text-align: center; }
        </style>
        """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("⚙️ Parámetros")
        val_depa = st.number_input("Precio Inmueble (S/.)", value=250000)
        inv_amoblado = st.number_input("Inversión Amoblado (S/.)", value=25000)
        st.write("---")
        tcea = st.number_input("TCEA %", value=9.5)
        plazo_años = st.selectbox("Plazo (Años)", [10, 15, 20, 25], index=2)
        st.write("---")
        tarifa = st.number_input("Tarifa Airbnb (S/.)", value=180)
        ocupacion_act = st.slider("Días/mes", 1, 30, 20)
        st.write("---")
        renta_trad = st.number_input("Renta Tradicional (S/.)", value=1800)

    # LÓGICA FINANCIERA
    inicial_banco = val_depa * 0.20
    inv_total_real = inicial_banco + inv_amoblado
    prestamo = val_depa - inicial_banco
    tem = (1 + tcea/100)**(1/12) - 1
    cuota = prestamo * (tem * (1 + tem)**(plazo_años*12)) / ((1 + tem)**(plazo_años*12) - 1)
    mantenimiento = (val_depa * 0.03) / 12
    ingreso_bruto = tarifa * ocupacion_act * 0.85
    impuesto = ingreso_bruto * 0.05
    gastos_operativos = mantenimiento + impuesto
    flujo_neto = ingreso_bruto - cuota - gastos_operativos
    roi_anual = (flujo_neto * 12 / inv_total_real) * 100
    u_anual_trad = (renta_trad - cuota - (val_depa*0.015/12) - (renta_trad*0.05)) * 12

    tab1, tab2, tab3, tab4 = st.tabs(["📊 Desglose de Flujos", "📈 Plusvalía", "🛡️ Sensibilidad", "🔄 Comparativa"])

    with tab1:
        st.markdown('<div class="section-title">Estructura de Capital e Ingresos</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        col1.metric("Inicial Banco (20%)", f"S/. {inicial_banco:,.0f}")
        col2.metric("Amoblado/Equipamiento", f"S/. {inv_amoblado:,.0f}")
        col3.metric("Inversión Total Real", f"S/. {inv_total_real:,.0f}")
        
        st.markdown('<div class="section-title">Análisis Operativo Mensual</div>', unsafe_allow_html=True)
        col4, col5, col6, col7 = st.columns(4)
        col4.metric("Ganancia Bruta Airbnb", f"S/. {ingreso_bruto:,.0f}")
        col5.metric("Cuota Mensual Banco", f"S/. -{cuota:,.0f}")
        col6.metric("Costos Op + Impuestos", f"S/. -{gastos_operativos:,.0f}")
        col7.metric("Utilidad Neta (Cash)", f"S/. {flujo_neto:,.0f}")

        st.markdown('<div class="section-title">Proyección de Payback</div>', unsafe_allow_html=True)
        años_pb = 25; meses = np.arange(0, años_pb*12+1); f_acum = [-inv_total_real]; año_rec = None
        for m in meses[1:]:
            f_acum.append(f_acum[-1] + (flujo_neto if m <= plazo_años*12 else ingreso_bruto-gastos_operativos))
            if año_rec is None and f_acum[-1] >= 0: año_rec = m/12
        
        c_pb1, c_pb2 = st.columns([1, 2.5])
        with c_pb1:
            st.markdown(f'<div class="highlight-card"><h2 style="color:#3b82f6; margin:0;">{año_rec:.1f} Años</h2><p style="color:white; font-size:0.8rem;">RECUPERACIÓN TOTAL</p></div>', unsafe_allow_html=True)
        with c_pb2:
            fig_pb = go.Figure()
            f_np = np.array(f_acum)
            fig_pb.add_trace(go.Scatter(x=meses/12, y=f_np, fill='tozeroy', fillcolor='rgba(16, 185, 129, 0.2)', line=dict(color='#3b82f6', width=3)))
            fig_pb.add_trace(go.Scatter(x=meses/12, y=np.minimum(f_np, 0), fill='tozeroy', fillcolor='rgba(239, 68, 68, 0.3)', line=dict(color='rgba(0,0,0,0)'), showlegend=False))
            fig_pb.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", margin=dict(t=20, b=20))
            st.plotly_chart(fig_pb, use_container_width=True)

    with tab2:
        st.markdown('<div class="section-title">Ganancias por Revalorización (Plusvalía)</div>', unsafe_allow_html=True)
        plus_slider = st.slider("Plusvalía Anual %", 0.0, 10.0, 4.0)
        c_p = st.columns(4)
        for i, a in enumerate([5, 10, 15, 20]):
            g = (val_depa * (1 + plus_slider/100)**a) - val_depa
            c_p[i].metric(f"Ganancia {a}A", f"S/. {g:,.0f}")
        
        años_range = np.arange(0, 26); v_mkt = [val_depa * (1+plus_slider/100)**a for a in años_range]
        equity = [v - (prestamo * (1 - a/plazo_años) if a < plazo_años else 0) for a, v in zip(años_range, v_mkt)]
        fig_p = go.Figure()
        fig_p.add_trace(go.Bar(x=años_range, y=v_mkt, name="Valor Mercado", marker_color='#1f2630'))
        fig_p.add_trace(go.Scatter(x=años_range, y=equity, name="Equity", fill='tozeroy', fillcolor='rgba(0, 255, 204, 0.2)', line=dict(color='#00ffcc', width=4)))
        fig_p.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_p, use_container_width=True)

    with tab3:
        st.markdown('<div class="section-title">Matrices de Sensibilidad Espejo</div>', unsafe_allow_html=True)
        
        # Ocupación
        st.subheader("1. Sensibilidad: ROI vs Ocupación")
        col_s1_t, col_s1_g = st.columns([1, 1.5])
        d_range = np.arange(12, 31, 2)
        roi_o = [((((tarifa*d*0.85) - cuota - mantenimiento - (tarifa*d*0.85*0.05))*12/inv_total_real)*100) for d in d_range]
        df_o = pd.DataFrame({"Días": d_range, "ROI %": roi_o})
        with col_s1_t:
            st.dataframe(df_o.style.background_gradient(cmap='RdYlGn', subset=['ROI %']).format("{:.2f}%"), use_container_width=True)
        with col_s1_g:
            fig_o = go.Figure(go.Scatter(x=d_range, y=roi_o, mode='lines+markers', line=dict(color='#3b82f6', width=3)))
            fig_o.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig_o, use_container_width=True)

        # Precio Compra
        st.subheader("2. Sensibilidad: ROI vs Precio de Compra")
        col_s2_t, col_s2_g = st.columns([1, 1.5])
        p_vars = [-10, -5, 0, 5, 10]
        roi_p = [ (flujo_neto*12 / ( (val_depa*(1+v/100)*0.2)+inv_amoblado ) * 100) for v in p_vars]
        df_p = pd.DataFrame({"Var %": p_vars, "ROI %": roi_p})
        with col_s2_t:
            st.dataframe(df_p.style.background_gradient(cmap='RdYlGn_r', subset=['ROI %']).format("{:.2f}%"), use_container_width=True)
        with col_s2_g:
            fig_p2 = go.Figure(go.Bar(x=p_vars, y=roi_p, marker_color='#3b82f6'))
            fig_p2.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig_p2, use_container_width=True)

    with tab4:
        st.markdown('<div class="section-title">Comparativa de Modelos de Renta</div>', unsafe_allow_html=True)
        col_c1, col_c2 = st.columns(2)
        ventaja_anual = (flujo_neto*12) - u_anual_trad
        col_c1.metric("Ventaja Airbnb (Anual)", f"S/. {ventaja_anual:,.0f}")
        col_c2.metric("ROI Airbnb vs Trad.", f"{roi_anual:.1f}% vs {(u_anual_trad*100/inv_total_real):.1f}%")
        
        fig_c = go.Figure([go.Bar(
            x=['<b>AIRBNB</b>', '<b>TRADICIONAL</b>'], 
            y=[flujo_neto*12, u_anual_trad], 
            marker_color=['#3b82f6', '#10b981'],
            text=[f'<b>S/. {flujo_neto*12:,.0f}</b>', f'<b>S/. {u_anual_trad:,.0f}</b>'],
            textposition='auto',
            textfont=dict(size=22, color='white')
        )])
        fig_c.update_layout(title="<b>UTILIDAD NETA ANUALIZADA</b>", height=500, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_c, use_container_width=True)

# =========================================================
# MOTOR DE PDF (DENSIDAD INFORMATIVA EXTREMA)
# =========================================================

def generate_ultra_report(d):
    pdf = FPDF()
    pdf.add_page()
    # Header
    pdf.set_fill_color(31, 38, 48); pdf.rect(0, 0, 210, 45, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 15, "INFORME DE AUDITORIA Y VIABILIDAD INMOBILIARIA", ln=True, align='C')
    pdf.set_font("Arial", '', 10); pdf.cell(0, 5, "ING. JANCARLO MENDOZA - EXPERTO INTEGRAL", ln=True, align='C')
    pdf.ln(25); pdf.set_text_color(0, 0, 0)

    # 1. Análisis de Inversión
    pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, "1. INGENIERIA DE COSTOS Y CAPITAL", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.multi_cell(0, 6, "Se ha determinado la estructura de capital necesaria considerando un apalancamiento bancario del 80%. La inversion inicial liquida comprende el equity inicial mas el equipamiento necesario para operar.")
    pdf.ln(2)
    data = [["Concepto", "Monto (S/.)"], ["Valor Inmueble", f"{d['val']:,.0f}"], ["Cuota Inicial (20%)", f"{d['ini']:,.0f}"], ["Inversion Amoblado", f"{d['inv_a']:,.0f}"], ["CAPITAL TOTAL REQUERIDO", f"{d['inv_t']:,.0f}"]]
    for r in data:
        pdf.cell(100, 8, r[0], 1); pdf.cell(80, 8, r[1], 1, ln=True)

    # 2. Operatividad Detallada
    pdf.ln(10); pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, "2. ANALISIS OPERATIVO Y CASH FLOW", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.multi_cell(0, 6, f"Bajo un escenario de {d['dias']} dias de ocupacion y una tarifa de S/. {d['tar']}, el flujo de caja se desglosa de la siguiente manera:")
    pdf.ln(2)
    data_f = [["Ingreso Bruto (Neto Plataforma)", f"{d['i_b']:,.0f}"], ["Servicio de Deuda (Banco)", f"-{d['cuo']:,.0f}"], ["Mantenimiento y Servicios", f"-{d['mant']:,.0f}"], ["Impuesto 1ra Cat (5%)", f"-{d['imp']:,.0f}"], ["UTILIDAD NETA MENSUAL", f"{d['f_n']:,.0f}"]]
    for r in data_f:
        pdf.cell(100, 8, r[0], 1); pdf.cell(80, 8, r[1], 1, ln=True)

    # 3. KPIs y Riesgo
    pdf.ln(10); pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, "3. INDICADORES CLAVE Y RESILIENCIA", ln=True)
    pdf.cell(0, 7, f"- ROI Cash-on-Cash: {d['roi']:.2f}% Anual", ln=True)
    pdf.cell(0, 7, f"- Tiempo de Recuperacion (Payback): {d['pb']:.1f} Años", ln=True)
    pdf.cell(0, 7, f"- Ventaja sobre Renta Tradicional: S/. {d['v_a']:,.0f} (Anual)", ln=True)
    pdf.cell(0, 7, f"- Valor de Mercado Est. (20 años): S/. {d['v20']:,.0f}", ln=True)
    
    # 4. Dictamen Final
    pdf.ln(10); pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, "4. DICTAMEN TECNICO", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.multi_cell(0, 6, "El proyecto muestra una robustez financiera superior al promedio de activos inmobiliarios convencionales. La capacidad de cobertura de deuda es positiva, permitiendo un apalancamiento eficiente. Se recomienda la ejecucion bajo el modelo de optimizacion de tarifas dinamicas para maximizar el ROI proyectado.")

    return pdf.output(dest='S').encode('latin-1')

if "authenticated" in st.session_state and st.session_state.authenticated:
    st.write("---")
    if st.button("📥 GENERAR AUDITORIA TECNICA COMPLETA"):
        v20_pdf = val_depa * (1 + plus_slider/100)**20
        pdf_b = generate_ultra_report({
            "val": val_depa, "ini": inicial_banco, "inv_a": inv_amoblado, "inv_t": inv_total_real,
            "i_b": ingreso_bruto, "cuo": cuota, "mant": mantenimiento, "imp": impuesto,
            "f_n": flujo_neto, "roi": roi_anual, "pb": año_rec if año_rec else 0,
            "v_a": ventaja_anual, "v20": v20_pdf, "dias": ocupacion_act, "tar": tarifa
        })
        st.download_button("Descargar Informe Profesional", data=pdf_b, file_name=f"Auditoria_JM_{datetime.now().strftime('%Y%m%d')}.pdf")
