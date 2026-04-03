import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime

# =========================================================
# BLOQUE 1: INTERFAZ WEB V37 (RESTAURADA Y AJUSTADA)
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
    # --- ESTILOS CSS V37 (INALTERADOS) ---
    st.markdown("""
        <style>
        .main { background-color: #0e1117; }
        [data-testid="stMetricValue"] { font-size: 1.8rem !important; color: #00ffcc; font-weight: bold; }
        [data-testid="stMetricLabel"] { font-size: 1rem !important; font-weight: 500; color: #ffffff; }
        div[data-testid="stMetric"] { background-color: #1f2630; padding: 20px; border-radius: 12px; border: 1px solid #30363d; }
        .info-text { font-size: 0.9rem; color: #a1a1a1; margin-top: 10px; padding: 12px; border-left: 2px solid #3b82f6; background-color: #161b22; line-height: 1.5; }
        .section-title { margin-top: 35px; margin-bottom: 12px; color: #3b82f6; font-size: 1.45rem; font-weight: 400; border-bottom: 1px solid #30363d; padding-bottom: 5px; }
        .highlight-card { background-color: #1e293b; padding: 25px; border-radius: 12px; border: 1px solid #3b82f6; text-align: center; margin-bottom: 10px; }
        .flow-card { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; height: 100%; margin-bottom: 10px; }
        .flow-val { font-size: 1.3rem; font-weight: bold; margin-bottom: 5px; }
        .flow-label { font-size: 0.85rem; color: #3b82f6; text-transform: uppercase; font-weight: 600; }
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

    # Lógica de cálculo
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

    tab1, tab2, tab3, tab4 = st.tabs(["📊 Flujos", "📈 Plusvalía", "🛡️ Sensibilidad", "🔄 Airbnb vs Tradicional"])

    with tab1:
        st.markdown('<div class="section-title">Desembolso Inicial</div>', unsafe_allow_html=True)
        st.metric("Inversión Total Real", f"S/. {inversion_total_real:,.0f}")
        st.markdown('<div class="info-text">Capital líquido inicial: 20% cuota inicial + inversión en amoblado y equipamiento.</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">Detalle de Flujo Mensual</div>', unsafe_allow_html=True)
        col_f = st.columns(5)
        metrics = [
            ("Ingresos", f"S/. {ingreso_bruto_air:,.2f}", "#00ffcc", "Neto tras comisión plataforma (15%)."),
            ("Hipotecario", f"S/. -{cuota:,.2f}", "#ef4444", "Pago mensual del crédito según TCEA."),
            ("Operativos", f"S/. -{mantenimiento_mes:,.2f}", "#ef4444", "Edificio, servicios y limpieza."),
            ("Impuestos", f"S/. -{impuesto_air:,.2f}", "#ef4444", "Impuesto a la renta (5%)."),
            ("Flujo Neto", f"S/. {flujo_neto_air:,.2f}", "#00ffcc", "Utilidad líquida mensual.")
        ]
        for i, m in enumerate(metrics):
            with col_f[i]:
                st.markdown(f'<div class="flow-card"><div class="flow-label">{m[0]}</div><div class="flow-val" style="color: {m[2]};">{m[1]}</div><p style="font-size:0.8rem; color:#a1a1a1;">{m[3]}</p></div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">Proyección de Payback (Retorno de Capital)</div>', unsafe_allow_html=True)
        años_pb = 25; meses_pb = np.arange(0, años_pb * 12 + 1); flujo_acum = [-inversion_total_real]; año_rec = None
        for m in meses_pb[1:]:
            u_mes = flujo_neto_air if m <= (plazo_años * 12) else (ingreso_bruto_air - mantenimiento_mes - impuesto_air)
            flujo_acum.append(flujo_acum[-1] + u_mes)
            if año_rec is None and flujo_acum[-1] >= 0: año_rec = m / 12
        
        col_pb1, col_pb2 = st.columns([1, 2])
        with col_pb1:
            if año_rec: st.markdown(f'<div class="highlight-card"><span style="color: #3b82f6; font-size: 2rem; font-weight: bold;">{año_rec:.1f} Años</span></div>', unsafe_allow_html=True)
            st.markdown('<div class="info-text">Punto donde la utilidad acumulada cubre el 100% de la inversión inicial (Equity + Amoblado).</div>', unsafe_allow_html=True)
        
        with col_pb2:
            fig_pb = go.Figure(); f_np = np.array(flujo_acum)
            fig_pb.add_trace(go.Scatter(x=meses_pb/12, y=flujo_acum, line=dict(color='#3b82f6', width=4)))
            fig_pb.update_layout(title="Curva de Retorno Acumulado", height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig_pb, use_container_width=True)
            st.markdown('<div class="info-text">El gráfico muestra la evolución del capital. La zona positiva representa riqueza neta generada.</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="section-title">Plusvalía Anual</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-text">Estimación del incremento del valor del activo en el tiempo por desarrollo del entorno.</div>', unsafe_allow_html=True)
        plus_val = st.slider("Plusvalía Anual (%)", 0.0, 10.0, 4.0)
        
        c_p = st.columns(4)
        for i, a in enumerate([5, 10, 15, 20]):
            gain = (val_depa * (1 + plus_val/100)**a) - val_depa
            c_p[i].metric(f"Ganancia {a} años", f"S/. {gain:,.0f}")
        
        años_p = np.arange(0, 26); v_mkt = [val_depa * (1 + plus_val/100)**a for a in años_p]
        fig_p = go.Figure(); fig_p.add_trace(go.Bar(x=años_p, y=v_mkt, name="Valor Mercado", marker_color='#1f2630'))
        fig_p.update_layout(title="Crecimiento Patrimonial Proyectado", height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_p, use_container_width=True)
        st.markdown('<div class="info-text">Representación del valor total del inmueble. El aumento es exponencial gracias al interés compuesto de la plusvalía.</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="section-title">Análisis de Resiliencia</div>', unsafe_allow_html=True)
        st.columns(3)[0].metric("Punto Equilibrio (Días)", f"{np.ceil(breakeven_dias):.0f}")
        
        # Sensibilidad Ocupación
        st.markdown('<div class="section-title">Sensibilidad: ROI vs Ocupación Mensual</div>', unsafe_allow_html=True)
        d_range = list(range(5, 31)); roi_o = [((((tarifa * d * 0.85 * 0.95) - cuota - mantenimiento_mes) * 12 / inversion_total_real) * 100) for d in d_range]
        fig_o = go.Figure(go.Scatter(x=d_range, y=roi_o, line=dict(color='#3b82f6', width=3)))
        fig_o.update_layout(height=350, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_o, use_container_width=True)
        
        # RESTAURACIÓN: Sensibilidad ROI vs Precio/m2 (Simulado por Variación de Precio)
        st.markdown('<div class="section-title">Sensibilidad: ROI vs Variación de Precio Compra</div>', unsafe_allow_html=True)
        p_vars = [-10, -5, 0, 5, 10]; roi_p = [((flujo_neto_air * 12 / ( (val_depa*(1+v/100)*0.2) + inv_amoblado)) * 100) for v in p_vars]
        st.dataframe(pd.DataFrame({"Var. Precio %": p_vars, "ROI Est. %": roi_p}).style.format("{:.2f}%"))

    with tab4:
        st.markdown('<div class="section-title">Comparativa de Modelos de Renta</div>', unsafe_allow_html=True)
        col_c1, col_c2 = st.columns([1, 2])
        ventaja_anual = (flujo_neto_air*12) - u_anual_trad
        with col_c1:
            st.metric("Ventaja Airbnb (Anual)", f"S/. {ventaja_anual:,.0f}")
            st.markdown('<div class="info-text">Diferencia neta anual que el modelo Airbnb genera por encima del alquiler tradicional.</div>', unsafe_allow_html=True)
        with col_c2:
            fig_c = go.Figure([go.Bar(x=['Airbnb', 'Tradicional'], y=[flujo_neto_air*12, u_anual_trad], marker_color=['#3b82f6', '#10b981'])])
            fig_c.update_layout(height=350, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig_c, use_container_width=True)

# =========================================================
# BLOQUE 2: MOTOR DE PDF TÉCNICO (CONTENIDO COMPLETO)
# =========================================================

def generate_backup2_pdf(d):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(31, 38, 48); pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", 'B', 18)
    pdf.cell(0, 15, "INFORME TECNICO DE AUDITORIA INMOBILIARIA", ln=True, align='C')
    pdf.set_font("Arial", '', 10); pdf.cell(0, 5, "ING. JANCARLO MENDOZA - BACKUP 2", ln=True, align='C')
    pdf.ln(15); pdf.set_text_color(0, 0, 0)

    pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, "1. ESTRUCTURA DE INVERSION", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 7, f"- Valor Inmueble: S/. {d['val_inm']:,.2f}", ln=True)
    pdf.cell(0, 7, f"- Inversion Total Real (Equity + Amoblado): S/. {d['inv_total']:,.2f}", ln=True)
    
    pdf.ln(5); pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, "2. ANALISIS DE FLUJO MENSUAL", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 7, f"- Ingresos Airbnb Brutos: S/. {d['ing_bruto']:,.2f}", ln=True)
    pdf.cell(0, 7, f"- Cuota Hipotecaria: S/. {d['cuota']:,.2f}", ln=True)
    pdf.cell(0, 7, f"- Flujo Neto Mensual: S/. {d['flujo_neto']:,.2f}", ln=True)
    
    pdf.ln(5); pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, "3. RENDIMIENTO Y PLUSVALIA", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 7, f"- ROI Anual: {d['roi']:.2f}%", ln=True)
    pdf.cell(0, 7, f"- Payback Estimado: {d['payback']:.1f} Años", ln=True)
    pdf.cell(0, 7, f"- Plusvalia Proyectada a 20 años: S/. {d['p20']:,.2f}", ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

if "authenticated" in st.session_state and st.session_state.authenticated:
    st.write("---")
    if st.button("📥 GENERAR BACKUP 2 (PDF COMPLETO)"):
        p20_val = (val_depa * (1 + plus_val/100)**20) - val_depa
        bytes_out = generate_backup2_pdf({
            "val_inm": val_depa, "inv_total": inversion_total_real, "ing_bruto": ingreso_bruto_air,
            "cuota": cuota, "flujo_neto": flujo_neto_air, "roi": roi_anual_air,
            "payback": año_rec if año_rec else 0, "p20": p20_val
        })
        st.download_button("Descargar Backup 2", data=bytes_out, file_name="Auditoria_Backup2.pdf")
