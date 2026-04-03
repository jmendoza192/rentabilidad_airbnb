import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime

# =========================================================
# 0. CONFIGURACIÓN Y ESTÉTICA "TOTAL CONSISTENCY"
# =========================================================
try:
    st.set_page_config(page_title="Industrial Audit | JM", layout="wide")
except:
    pass

# Constante de Fuente para Gráficos
BASE_FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def check_password():
    if not st.session_state.authenticated:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.title("🔐 Acceso Sistema de Auditoría")
            password = st.text_input("Contraseña de Consultor:", type="password")
            if st.button("Ingresar al Sistema"):
                if password == "Jancarlo2026":
                    st.session_state.authenticated = True
                    st.rerun()
                else: st.error("Acceso Denegado.")
        return False
    return True

if check_password():
    # CSS: UNIFICACIÓN TOTAL (TEXTOS, NÚMEROS, TABLAS, INPUTS)
    st.markdown(f"""
        <style>
        /* 1. Reset Global de Fuente */
        html, body, [class*="css"], .stMarkdown, .stText, .stButton, .stSelectbox, .stNumberInput {{
            font-family: {BASE_FONT} !important;
        }}

        /* 2. Forzar en Tablas y Dataframes */
        .stTable, [data-testid="stTable"], [data-testid="stDataFrame"] {{
            font-family: {BASE_FONT} !important;
        }}
        
        /* 3. Números y Valores en Tarjetas */
        .val-pos, .val-neg, .label-card {{
            font-family: {BASE_FONT} !important;
        }}

        /* 4. Eliminar botones de incremento (+/-) */
        button.step-up, button.step-down {{ display: none !important; }}
        input[type=number]::-webkit-inner-spin-button, 
        input[type=number]::-webkit-outer-spin-button {{ -webkit-appearance: none; margin: 0; }}
        input[type=number] {{ -moz-appearance: textfield; }}

        .main {{ background-color: #0e1117; }}
        
        /* Títulos */
        .section-title {{ 
            color: #ffffff; font-size: 1.6rem; font-weight: 700; 
            padding: 12px 0; border-bottom: 3px solid #30363d; margin-bottom: 20px;
            text-transform: uppercase;
        }}

        /* Tarjetas Estilo Industrial Base */
        .card-base {{
            border: 1px solid #30363d; border-radius: 4px; padding: 20px;
            text-align: center; margin-bottom: 15px; color: #ffffff !important;
        }}
        .bg-blue {{ background-color: #1c3d5a; }}
        .bg-green {{ background-color: #1b4332; }}
        .bg-red {{ background-color: #4c1d1d; }}
        .bg-gray {{ background-color: #21262d; }}
        .bg-gold {{ background-color: #744210; }}
        .bg-indigo {{ background-color: #312e81; }}

        .val-pos {{ color: #60a5fa; font-size: 2.1rem; font-weight: bold; }}
        .val-neg {{ color: #f87171; font-size: 2.1rem; font-weight: bold; }}
        .label-card {{ font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; color: #ffffff; }}

        .info-text {{ font-size: 0.95rem; color: #8b949e; margin-bottom: 15px; line-height: 1.5; }}
        .footer-tip {{
            background-color: #161b22; color: #ffffff; padding: 20px;
            border: 1px solid #30363d; border-left: 5px solid #58a6ff; margin-top: 30px;
        }}
        </style>
        """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("📋 Parámetros de Auditoría")
        val_depa = st.number_input("Precio Propiedad (S/.) 🏠", value=250000)
        inv_amoblado = st.number_input("Inversión Amoblado (S/.) 🛋️", value=25000)
        st.write("---")
        tcea = st.number_input("TCEA Bancaria (%) 🏦", value=9.5)
        plazo_años = st.selectbox("Plazo del Crédito (Años) 🗓️", [10, 15, 20, 25], index=2)
        st.write("---")
        tarifa_base = st.number_input("Tarifa Noche Airbnb (S/.) 💰", value=180)
        ocupacion_act = st.selectbox("Días Ocupados al Mes 🌙", list(range(1, 31)), index=19)
        st.write("---")
        renta_trad = st.number_input("Renta Tradicional (S/.) 🏠", value=1800)

    # LÓGICA DE CÁLCULO
    inicial = val_depa * 0.20
    inv_total = inicial + inv_amoblado
    prestamo = val_depa - inicial
    tem = (1 + tcea/100)**(1/12) - 1
    cuota = prestamo * (tem * (1 + tem)**(plazo_años*12)) / ((1 + tem)**(plazo_años*12) - 1)
    mantenimiento = (val_depa * 0.03) / 12
    ingreso_bruto = tarifa_base * ocupacion_act * 0.85 
    impuesto = ingreso_bruto * 0.05
    gastos_op = mantenimiento + impuesto
    flujo_neto = ingreso_bruto - cuota - gastos_op
    roi_airbnb = (flujo_neto * 12 / inv_total) * 100
    utilidad_trad = (renta_trad - cuota - (val_depa*0.015/12) - (renta_trad*0.05)) * 12
    roi_trad = (utilidad_trad / inicial) * 100

    tabs = st.tabs(["💎 CAPITAL Y FLUJO", "📈 CRECIMIENTO", "⚖️ SENSIBILIDAD", "🔄 COMPARATIVA"])

    # --------------------------------------------------------- PESTAÑA 1
    with tabs[0]:
        st.markdown('<div class="section-title">🏗️ Estructura de Capital e Ingresos</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="card-base bg-blue"><div class="label-card">Inicial Banco (20%) 🏢</div><div class="val-pos">S/. {inicial:,.0f}</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="card-base bg-blue"><div class="label-card">Mobiliario/Equipos 🛋️</div><div class="val-pos">S/. {inv_amoblado:,.0f}</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="card-base bg-gray"><div class="label-card">Cash-Out Total 💎</div><div class="val-pos">S/. {inv_total:,.0f}</div></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">💸 Análisis Operativo Mensual</div>', unsafe_allow_html=True)
        c4, c5, c6, c7 = st.columns(4)
        with c4: st.markdown(f'<div class="card-base bg-gray"><div class="label-card">Airbnb Bruto 🏨</div><div class="val-pos">S/. {ingreso_bruto:,.0f}</div></div>', unsafe_allow_html=True)
        with c5: st.markdown(f'<div class="card-base bg-gray"><div class="label-card">Cuota Hipotecaria 🏦</div><div class="val-neg">S/. -{cuota:,.0f}</div></div>', unsafe_allow_html=True)
        with c6: st.markdown(f'<div class="card-base bg-gray"><div class="label-card">Gastos + Impuestos 🧾</div><div class="val-neg">S/. -{gastos_op:,.0f}</div></div>', unsafe_allow_html=True)
        with c7: st.markdown(f'<div class="card-base bg-green"><div class="label-card">Cash Flow Neto 💰</div><div class="val-pos">S/. {flujo_neto:,.0f}</div></div>', unsafe_allow_html=True)

        st.markdown('### 📊 Rentabilidad de Inversión')
        cr1, cr2 = st.columns([1, 1.2])
        with cr1:
            st.markdown(f'<div class="card-base bg-gold"><div class="label-card">ROI Anual Proyectado 📈</div><div class="val-pos" style="color:white;">{roi_airbnb:.2f}%</div></div>', unsafe_allow_html=True)
        with cr2:
            st.table(pd.DataFrame({"Activo": ["Proyecto JM", "S&P 500", "Plazo Fijo PE"], "Retorno": [f"{roi_airbnb:.1f}%", "10.0%", "6.5%"]}))

        st.write("---")
        cp1, cp2 = st.columns([1, 1.2])
        años_pb = 25; meses = np.arange(0, años_pb*12+1); f_acum = [-inv_total]; rec = 0
        for m in meses[1:]:
            f_acum.append(f_acum[-1] + (flujo_neto if m <= plazo_años*12 else ingreso_bruto-gastos_op))
            if rec == 0 and f_acum[-1] >= 0: rec = m/12
        
        with cp1:
            st.markdown(f'<div class="card-base bg-blue" style="border: 2px solid white;"><div class="label-card">Tiempo de Payback ⏳</div><div class="val-pos" style="color:white; font-size:2.5rem;">{rec:.1f} Años</div></div>', unsafe_allow_html=True)
        with cp2:
            fig_pb = go.Figure()
            fig_pb.add_trace(go.Scatter(x=meses/12, y=f_acum, line=dict(color='#ffffff', width=3), name="Balance"))
            # Forzar fuente en Plotly
            fig_pb.update_layout(
                title="<b>RECUPERACIÓN DE CAPITAL</b>", height=400,
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family=BASE_FONT, color="white")
            )
            st.plotly_chart(fig_pb, use_container_width=True)

    # --------------------------------------------------------- PESTAÑA 3 (SENSIBILIDAD)
    with tabs[2]:
        st.markdown('<div class="section-title">⚖️ Matriz de Sensibilidad de Rentabilidad</div>', unsafe_allow_html=True)
        
        def color_roi(val):
            c = '#f87171' if val < 5 else '#fbbf24' if val < 10 else '#4ade80'
            return f'background-color: {c}; color: #000; font-weight: bold;'

        st.subheader("📍 Días de Ocupación vs ROI")
        cs1_t, cs1_g = st.columns([1, 1.8], vertical_alignment="center")
        d_range = [5, 10, 15, 20, 25, 30]
        roi_d = [((((tarifa_base*d*0.85) - cuota - mantenimiento - (tarifa_base*d*0.85*0.05))*12/inv_total)*100) for d in d_range]
        with cs1_t:
            st.table(pd.DataFrame({"Días/Mes": d_range, "ROI %": roi_d}).style.applymap(color_roi, subset=['ROI %']).format({"ROI %": "{:.2f}%"}))
        with cs1_g:
            fig_d = go.Figure(go.Scatter(x=d_range, y=roi_d, mode='lines+markers', line=dict(color='#60a5fa', width=4)))
            fig_d.update_layout(height=600, font=dict(family=BASE_FONT, color="white"), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_d, use_container_width=True)

    # --------------------------------------------------------- PESTAÑA 4 (COMPARATIVA)
    with tabs[3]:
        st.markdown('<div class="section-title">🔄 Comparativa: Tradicional vs Airbnb</div>', unsafe_allow_html=True)
        ventaja_anual = (flujo_neto * 12) - utilidad_trad
        dif_roi = roi_airbnb - roi_trad
        
        cc = st.columns(4)
        with cc[0]: st.markdown(f'<div class="card-base bg-green"><div class="label-card">Excedente Anual Airbnb 🏆</div><div class="val-pos" style="color:white;">S/. {ventaja_anual:,.0f}</div></div>', unsafe_allow_html=True)
        with cc[1]: st.markdown(f'<div class="card-base bg-gray"><div class="label-card">ROI Airbnb 🏨</div><div class="val-pos" style="color:white;">{roi_airbnb:.1f}%</div></div>', unsafe_allow_html=True)
        with cc[2]: st.markdown(f'<div class="card-base bg-gray"><div class="label-card">ROI Tradicional 🏠</div><div class="val-pos" style="color:white;">{roi_trad:.1f}%</div></div>', unsafe_allow_html=True)
        with cc[3]: st.markdown(f'<div class="card-base bg-indigo"><div class="label-card">Diferencial ROI 🚀</div><div class="val-pos" style="color:white;">{dif_roi:+.1f}%</div></div>', unsafe_allow_html=True)
        
        st.write("---")
        labels = ['<b>MODELO AIRBNB</b>', '<b>RENTA TRADICIONAL</b>']
        vals = [flujo_neto*12, utilidad_trad]
        fig_c = go.Figure([go.Bar(
            x=labels, y=vals, 
            marker_color=['#10b981' if v > 0 else '#ef4444' for v in vals],
            text=[f'S/. {v:,.0f}' for v in vals],
            textposition='inside', insidetextanchor='middle',
            textfont=dict(size=28, color='white', weight='bold', family=BASE_FONT)
        )])
        fig_c.update_layout(title="<b>UTILIDAD NETA ANUALIZADA LÍQUIDA</b>", height=600, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family=BASE_FONT, color="white"))
        st.plotly_chart(fig_c, use_container_width=True)

# =========================================================
# MOTOR DE PDF
# =========================================================
def generate_master_pdf(d):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(14, 17, 23); pdf.rect(0, 0, 210, 50, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 15, "AUDITORIA DE INVERSION INMOBILIARIA", ln=True, align='C')
    pdf.set_font("Arial", '', 10); pdf.cell(0, 5, "ELABORADO POR: ING. JANCARLO MENDOZA - EXPERTO INMOBILIARIO", ln=True, align='C')
    pdf.ln(35); pdf.set_text_color(0, 0, 0)

    pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, "1. INGENIERÍA DE CAPITAL", ln=True)
    pdf.set_font("Arial", '', 9)
    rows = [["CONCEPTO", "VALOR (S/.)"], ["Precio Propiedad", f"{d['val']:,.0f}"], ["Cuota Inicial 20%", f"{d['ini']:,.0f}"], ["Equipamiento Amoblado", f"{d['inv_a']:,.0f}"], ["CASH-OUT INICIAL TOTAL", f"{d['inv_t']:,.0f}"]]
    for r in rows:
        pdf.cell(95, 8, r[0], 1); pdf.cell(95, 8, r[1], 1, ln=True)

    pdf.ln(10); pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, "2. MÉTRICAS DE RENTABILIDAD", ln=True)
    pdf.set_font("Arial", '', 9)
    pdf.cell(0, 7, f"- ROI Airbnb Proyectado: {d['roi']:.2f}% Anual", ln=True)
    pdf.cell(0, 7, f"- ROI Renta Tradicional: {d['roi_t']:.2f}% Anual", ln=True)
    pdf.cell(0, 7, f"- Payback Estimado: {d['pb']:.1f} Años", ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

if st.session_state.authenticated:
    st.write("---")
    if st.button("📥 GENERAR INFORME TÉCNICO COMPLETO (PDF)"):
        pdf_bytes = generate_master_pdf({
            "val": val_depa, "ini": inicial, "inv_a": inv_amoblado, "inv_t": inv_total,
            "roi": roi_airbnb, "roi_t": roi_trad, "pb": rec
        })
        st.download_button("Descargar Reporte de Auditoría", data=pdf_bytes, file_name=f"Auditoria_Inmueble_JM.pdf")
