import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime
import base64

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

# --- FUNCIÓN GENERADORA DE PDF ---
def generate_pdf(data_dict):
    pdf = FPDF()
    pdf.add_page()
    
    # Encabezado
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "REPORTE DE AUDITORÍA INMOBILIARIA", ln=True, align='C')
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(200, 10, f"Realizado por: Ing. Jancarlo Mendoza - Asesoría Inmobiliaria", ln=True, align='C')
    pdf.cell(200, 10, f"Fecha y Hora de Exportación: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", ln=True, align='C')
    pdf.line(10, 35, 200, 35)
    
    # Sección 1: Flujos
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "1. RESUMEN DE FLUJOS Y RETORNO", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.multi_cell(0, 5, f"Inversión Total: S/. {data_dict['inv_total']:,.2f}\n"
                         f"Flujo Neto Mensual: S/. {data_dict['flujo_neto']:,.2f}\n"
                         f"Tiempo de Recuperación (Payback): {data_dict['payback']:.1f} años.")
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(0, 5, "TIP: El flujo neto es el 'oxígeno' de su inversión. Siempre mantenga una reserva equivalente a 3 meses de cuota hipotecaria para contingencias.")
    pdf.set_text_color(0, 0, 0)

    # Sección 2: Plusvalía
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "2. PROYECCIÓN DE PATRIMONIO (PLUSVALÍA)", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.multi_cell(0, 5, f"Plusvalía estimada a 10 años: S/. {data_dict['plus_10']:,.2f}\n"
                         f"Plusvalía estimada a 20 años: S/. {data_dict['plus_20']:,.2f}")
    pdf.multi_cell(0, 5, "INFORMACIÓN COMPLEMENTARIA: La plusvalía en distritos consolidados de Lima (Miraflores/San Isidro) suele ser más estable, mientras que en distritos en crecimiento (Surquillo/Magdalena) el potencial de apreciación es mayor por m2.")

    # Sección 3: Sensibilidad
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "3. ANÁLISIS DE RESILIENCIA (ESCENARIOS)", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.multi_cell(0, 5, f"Punto de Equilibrio: {data_dict['be_days']} noches/mes.\n"
                         f"ROI Anual Estimado: {data_dict['roi']:.2f}%")
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(0, 5, "TIP DE RIESGO: Si su ocupación baja del punto de equilibrio, el inmueble deja de ser 'autosustentable' y requiere inyección de capital propio para cubrir la deuda.")
    pdf.set_text_color(0, 0, 0)

    # Sección 4: Comparativa
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "4. COMPARATIVA: AIRBNB VS TRADICIONAL", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.multi_cell(0, 5, f"Utilidad Extra Anual (Airbnb): S/. {data_dict['ventaja']:,.2f}\n"
                         f"Factor de Eficiencia: {data_dict['factor']:.1f}x")
    pdf.multi_cell(0, 5, "CONCLUSIÓN TÉCNICA: El modelo de renta corta (Airbnb) maximiza el ROI pero incrementa el gasto operativo y el desgaste del mobiliario. El modelo tradicional es ideal para inversores que buscan 'pasividad' total.")
    
    return pdf.output(dest='S').encode('latin-1')

if check_password():
    # ESTILOS CSS (MANTENIENDO FORMATO WEB)
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

    # --- 2. SIDEBAR ---
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

    # --- 3. LÓGICA FINANCIERA ---
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

    # --- 4. TABS (CONTENIDO WEB INTACTO) ---
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
        eficiencia = (roi_anual_air/((u_anual_trad/inversion_total_real)*100))
        st.metric("Ventaja Airbnb (Anual)", f"S/. {ventaja_anual:,.0f}")
        
        fig_c = go.Figure([go.Bar(x=['Airbnb', 'Tradicional'], y=[flujo_neto_air*12, u_anual_trad], marker_color=['#3b82f6', '#10b981'], 
                                 text=[f"S/. {flujo_neto_air*12:,.0f}", f"S/. {u_anual_trad:,.0f}"], textposition='inside', 
                                 textfont=dict(size=18, family="Arial Black"))])
        fig_c.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_c, use_container_width=True)
        st.markdown('<div class="info-text"><b>Ficha Informativa Final:</b> Comparativa técnica de flujos post-deuda.</div>', unsafe_allow_html=True)

    # --- 5. BOTONES FINALES Y EXPORTACIÓN ---
    st.write("---")
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("✅ Finalizar Auditoría"): st.balloons()
    
    with col_btn2:
        # Preparación de datos para PDF
        report_data = {
            "inv_total": inversion_total_real,
            "flujo_neto": flujo_neto_air,
            "payback": año_rec if año_rec else 0,
            "plus_10": p_10,
            "plus_20": p_20,
            "be_days": np.ceil(breakeven_dias),
            "roi": roi_anual_air,
            "ventaja": ventaja_anual,
            "factor": eficiencia
        }
        
        pdf_bytes = generate_pdf(report_data)
        st.download_button(
            label="📥 Exportar Auditoría a PDF",
            data=pdf_bytes,
            file_name=f"Auditoria_Inmobiliaria_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf"
        )
