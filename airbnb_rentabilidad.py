import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime

# --- 1. CONFIGURACIÓN Y SEGURIDAD ---
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

# --- FUNCIÓN GENERADORA DE PDF (MEJORADA CON TIPS Y 80% DATA) ---
def generate_pdf(d):
    pdf = FPDF()
    pdf.add_page()
    
    # Encabezado Profesional
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "REPORTE ESTRATÉGICO DE INVERSIÓN INMOBILIARIA", ln=True, align='C')
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(200, 8, f"Realizado por: Ing. Jancarlo Mendoza - Asesoría Inmobiliaria", ln=True, align='C')
    pdf.cell(200, 8, f"Exportado el: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", ln=True, align='C')
    pdf.line(10, 38, 200, 38)
    pdf.ln(12)

    # Bloque 1: Flujos (Pestaña 1)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "1. AUDITORÍA DE FLUJOS MENSUALES (80% Data)", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 7, f"- Inversión Inicial Real: S/. {d['inv_total']:,.2f}", ln=True)
    pdf.cell(0, 7, f"- Ingreso Bruto Proyectado: S/. {d['ing_bruto']:,.2f}", ln=True)
    pdf.cell(0, 7, f"- Cuota Bancaria (Estimada): S/. {d['cuota']:,.2f}", ln=True)
    pdf.cell(0, 7, f"- Utilidad Líquida (Flujo Neto): S/. {d['flujo_neto']:,.2f}", ln=True)
    pdf.set_font("Arial", 'I', 9)
    pdf.set_text_color(50, 50, 50)
    pdf.multi_cell(0, 5, "TIP INGENIERÍA: Un flujo neto positivo es vital. Si el flujo es marginal, considere aumentar la cuota inicial para reducir el apalancamiento y mejorar la resiliencia del activo.")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)

    # Bloque 2: Plusvalía y Patrimonio (Pestaña 2)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "2. VALORIZACIÓN Y PATRIMONIO", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 7, f"- Plusvalía Acumulada (10 años): S/. {d['plus_10']:,.2f}", ln=True)
    pdf.cell(0, 7, f"- Plusvalía Acumulada (20 años): S/. {d['plus_20']:,.2f}", ln=True)
    pdf.multi_cell(0, 5, "INFO COMPLEMENTARIA: La plusvalía no es solo apreciación del mercado, es la construcción de 'Equity'. Al finalizar el préstamo, el 100% del valor del inmueble más la apreciación forman su patrimonio neto.")
    pdf.ln(5)

    # Bloque 3: Sensibilidad (Pestaña 3)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "3. ESCENARIOS DE ESTRÉS OPERATIVO", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 7, f"- Punto de Equilibrio: {d['be_days']} noches/mes para cubrir costos.", ln=True)
    pdf.cell(0, 7, f"- ROI Anual Proyectado: {d['roi']:.2f}% sobre capital invertido.", ln=True)
    pdf.set_text_color(200, 0, 0)
    pdf.multi_cell(0, 5, "TIP DE RIESGO: Monitoree su ADR (Tarifa Diaria). En meses de baja ocupación, es preferible bajar ligeramente el precio para asegurar el volumen de noches y no caer por debajo del punto de equilibrio.")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)

    # Bloque 4: Comparativa (Pestaña 4)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "4. ANÁLISIS COMPARATIVO DE MODELOS", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 7, f"- Diferencial Airbnb vs Tradicional: S/. {d['ventaja']:,.2f} adicionales/año.", ln=True)
    pdf.cell(0, 7, f"- Factor de Eficiencia: {d['factor']:.1f}x más rentable.", ln=True)
    pdf.set_font("Arial", 'B', 10)
    pdf.multi_cell(0, 5, "ASESORÍA FINAL: El modelo Airbnb requiere una gestión activa o un Property Manager. Si busca ingresos 100% pasivos, el modelo tradicional sigue siendo la opción más estable a largo plazo.")

    return pdf.output(dest='S').encode('latin-1')

if check_password():
    # --- ESTILOS CSS (RESTAURACIÓN V37) ---
    st.markdown("""
        <style>
        .main { background-color: #0e1117; }
        [data-testid="stMetricValue"] { font-size: 1.8rem !important; color: #00ffcc; font-weight: bold; }
        div[data-testid="stMetric"] { background-color: #1f2630; padding: 20px; border-radius: 12px; border: 1px solid #30363d; }
        .info-text { font-size: 0.9rem; color: #a1a1a1; margin-top: 10px; padding: 12px; border-left: 2px solid #3b82f6; background-color: #161b22; line-height: 1.5; }
        .section-title { margin-top: 35px; margin-bottom: 12px; color: #3b82f6; font-size: 1.45rem; border-bottom: 1px solid #30363d; padding-bottom: 5px; }
        .highlight-card { background-color: #1e293b; padding: 25px; border-radius: 12px; border: 1px solid #3b82f6; text-align: center; }
        .flow-card { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; height: 100%; margin-bottom: 10px; }
        .flow-val { font-size: 1.3rem; font-weight: bold; margin-bottom: 5px; }
        .flow-label { font-size: 0.85rem; color: #3b82f6; text-transform: uppercase; font-weight: 600; }
        </style>
        """, unsafe_allow_html=True)

    # --- SIDEBAR PARÁMETROS ---
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

    # --- LÓGICA FINANCIERA ---
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
    u_anual_trad = (renta_trad - cuota - (val_depa*0.015/12) - (renta_trad*0.05)) * 12

    # --- TABS (FORMATO WEB ORIGINAL) ---
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Flujos", "📈 Plusvalía", "🛡️ Sensibilidad", "🔄 Airbnb vs Tradicional"])

    with tab1:
        st.markdown('<div class="section-title">Desembolso Inicial</div>', unsafe_allow_html=True)
        st.metric("Inversión Total Real", f"S/. {inversion_total_real:,.0f}")
        st.markdown('<div class="section-title">Detalle de Flujo Mensual</div>', unsafe_allow_html=True)
        col_f1, col_f2, col_f3, col_f4, col_f5 = st.columns(5)
        with col_f1: st.markdown(f'<div class="flow-card"><div class="flow-label">Ingresos</div><div class="flow-val" style="color: #00ffcc;">S/. {ingreso_bruto_air:,.2f}</div></div>', unsafe_allow_html=True)
        with col_f2: st.markdown(f'<div class="flow-card"><div class="flow-label">Hipotecario</div><div class="flow-val" style="color: #ef4444;">S/. -{cuota:,.2f}</div></div>', unsafe_allow_html=True)
        with col_f3: st.markdown(f'<div class="flow-card"><div class="flow-label">Operativos</div><div class="flow-val" style="color: #ef4444;">S/. -{mantenimiento_mes:,.2f}</div></div>', unsafe_allow_html=True)
        with col_f4: st.markdown(f'<div class="flow-card"><div class="flow-label">Impuestos</div><div class="flow-val" style="color: #ef4444;">S/. -{impuesto_air:,.2f}</div></div>', unsafe_allow_html=True)
        with col_f5: st.markdown(f'<div class="flow-card" style="border: 1px solid #00ffcc;"><div class="flow-label">Flujo Neto</div><div class="flow-val" style="color: #00ffcc;">S/. {flujo_neto_air:,.2f}</div></div>', unsafe_allow_html=True)
        
        años_pb = 25; meses_pb = np.arange(0, años_pb * 12 + 1); flujo_acum = [-inversion_total_real]; año_rec = None
        for m in meses_pb[1:]:
            u_mes = flujo_neto_air if m <= (plazo_años * 12) else (ingreso_bruto_air - mantenimiento_mes - impuesto_air)
            flujo_acum.append(flujo_acum[-1] + u_mes)
            if año_rec is None and flujo_acum[-1] >= 0: año_rec = m / 12
        
        fig_pb = go.Figure(); f_np = np.array(flujo_acum)
        fig_pb.add_trace(go.Scatter(x=meses_pb/12, y=np.where(f_np <= 0, f_np, 0), fill='tozeroy', fillcolor='rgba(239, 68, 68, 0.3)', line=dict(color='rgba(0,0,0,0)')))
        fig_pb.add_trace(go.Scatter(x=meses_pb/12, y=np.where(f_np >= 0, f_np, 0), fill='tozeroy', fillcolor='rgba(16, 185, 129, 0.3)', line=dict(color='rgba(0,0,0,0)')))
        fig_pb.add_trace(go.Scatter(x=meses_pb/12, y=flujo_acum, line=dict(color='#3b82f6', width=4)))
        fig_pb.update_layout(title="Curva de Retorno", height=500, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_pb, use_container_width=True)

    with tab2:
        st.markdown('<div class="section-title">Plusvalía Anual</div>', unsafe_allow_html=True)
        plus_val = st.slider("Plusvalía Anual (%)", 0.0, 10.0, 4.0)
        p_10 = (val_depa * (1 + plus_val/100)**10) - val_depa
        p_20 = (val_depa * (1 + plus_val/100)**20) - val_depa
        st.metric("A 10 años", f"S/. {p_10:,.0f}")
        st.metric("A 20 años", f"S/. {p_20:,.0f}")

    with tab3:
        st.markdown('<div class="section-title">Análisis de Sensibilidad</div>', unsafe_allow_html=True)
        st.metric("ROI Est. Anual", f"{roi_anual_air:.1f}%")

    with tab4:
        st.markdown('<div class="section-title">Comparativa de Modelos</div>', unsafe_allow_html=True)
        ventaja_anual = (flujo_neto_air*12) - u_anual_trad
        eficiencia = (roi_anual_air/((u_anual_trad/inversion_total_real)*100)) if u_anual_trad != 0 else 0
        st.metric("Ventaja Airbnb (Anual)", f"S/. {ventaja_anual:,.0f}")
        
        fig_c = go.Figure([go.Bar(x=['Airbnb', 'Tradicional'], y=[flujo_neto_air*12, u_anual_trad], marker_color=['#3b82f6', '#10b981'], 
                                 text=[f"S/. {flujo_neto_air*12:,.0f}", f"S/. {u_anual_trad:,.0f}"], textposition='inside', 
                                 textfont=dict(size=18, family="Arial Black"))])
        fig_c.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_c, use_container_width=True)

    # --- BOTONES FINALES ---
    st.write("---")
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("✅ Finalizar Auditoría"): st.balloons()
    
    with col_btn2:
        report_data = {
            "inv_total": inversion_total_real,
            "ing_bruto": ingreso_bruto_air,
            "cuota": cuota,
            "flujo_neto": flujo_neto_air,
            "payback": año_rec if año_rec else 0,
            "plus_10": p_10,
            "plus_20": p_20,
            "be_days": int(np.ceil(breakeven_dias)),
            "roi": roi_anual_air,
            "ventaja": ventaja_anual,
            "factor": eficiencia
        }
        
        pdf_bytes = generate_pdf(report_data)
        st.download_button(
            label="📥 Exportar Auditoría a PDF",
            data=pdf_bytes,
            file_name=f"Auditoria_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf"
        )
