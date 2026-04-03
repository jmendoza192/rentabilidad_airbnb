import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime

# =========================================================
# 0. CONFIGURACIÓN Y ESTÉTICA DE SISTEMA (SANS & MONO)
# =========================================================
try:
    st.set_page_config(page_title="Auditoría JM", layout="wide")
except:
    pass

# Definición estricta de fuentes de sistema
SYS_SANS = '-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif'
SYS_MONO = 'ui-monospace, SFMono-Regular, SF Mono, Menlo, Monaco, Consolas, "Liberation Mono", monospace'

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def check_password():
    if not st.session_state.authenticated:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.title("Acceso al sistema 🔐")
            password = st.text_input("Contraseña de consultor:", type="password")
            if st.button("Ingresar"):
                if password == "Jancarlo2026":
                    st.session_state.authenticated = True
                    st.rerun()
                else: st.error("Acceso denegado.")
        return False
    return True

if check_password():
    # CSS: ELIMINACIÓN DE +/- Y UNIFICACIÓN DE FUENTES
    st.markdown(f"""
        <style>
        /* 1. Reset de Fuente Global */
        html, body, [class*="css"], .stMarkdown, p, div, span, label, button {{
            font-family: {SYS_SANS} !important;
            color: #ffffff;
        }}
        
        /* 2. Monospace para Datos y Tablas */
        .stTable, [data-testid="stTable"], code, .val-pos, .val-neg, .mono-font {{
            font-family: {SYS_MONO} !important;
        }}

        /* 3. Limpieza de Inputs (No +/-) */
        button.step-up, button.step-down {{ display: none !important; }}
        input[type=number]::-webkit-inner-spin-button, 
        input[type=number]::-webkit-outer-spin-button {{ -webkit-appearance: none; margin: 0; }}
        input[type=number] {{ -moz-appearance: textfield; }}

        .main {{ background-color: #0d1117; }}
        
        /* 4. Estilo de Títulos (Tipo Oración) */
        .section-title {{ 
            color: #ffffff; font-size: 1.6rem; font-weight: 600; 
            padding: 10px 0; border-bottom: 1px solid #30363d; margin: 25px 0 15px 0;
        }}

        /* 5. Tarjetas Industrias (Letras Blancas Siempre) */
        .card-base {{
            border: 1px solid #30363d; border-radius: 4px; padding: 18px;
            text-align: center; margin-bottom: 15px; color: #ffffff !important;
        }}
        .bg-blue {{ background-color: #1c3d5a; }}
        .bg-green {{ background-color: #1b4332; }}
        .bg-red {{ background-color: #4c1d1d; }}
        .bg-gray {{ background-color: #21262d; }}
        .bg-gold {{ background-color: #744210; }}
        .bg-indigo {{ background-color: #312e81; }}

        .val-pos {{ color: #58a6ff; font-size: 1.9rem; font-weight: 700; white-space: nowrap; }}
        .val-neg {{ color: #f85149; font-size: 1.9rem; font-weight: 700; white-space: nowrap; }}
        .label-card {{ font-size: 0.8rem; font-weight: 500; margin-bottom: 5px; opacity: 0.95; }}

        .info-box {{ font-size: 0.92rem; color: #8b949e; line-height: 1.6; margin-bottom: 20px; }}
        .footer-tip {{
            background-color: #161b22; color: #ffffff; padding: 22px;
            border: 1px solid #30363d; border-left: 4px solid #58a6ff; margin-top: 40px;
        }}
        </style>
        """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("Entrada de parámetros ⚙️")
        val_depa = st.number_input("Precio de venta (S/.) 🏠", value=350000)
        inv_amoblado = st.number_input("Inversión amoblado (S/.) 🛋️", value=40000)
        st.write("---")
        tcea = st.number_input("Tcea bancaria (%) 🏦", value=9.9)
        plazo_años = st.selectbox("Plazo del crédito (Años) 🗓️", [10, 15, 20, 25], index=2)
        st.write("---")
        tarifa_base = st.number_input("Tarifa por noche (S/.) 💰", value=250)
        ocupacion_act = st.selectbox("Días ocupados al mes 🌙", list(range(1, 31)), index=19)
        st.write("---")
        renta_trad = st.number_input("Renta tradicional (S/.) 🏠", value=2300)

    # LÓGICA FINANCIERA
    inicial = val_depa * 0.20
    inv_total = inicial + inv_amoblado
    prestamo = val_depa - inicial
    tem = (1 + tcea/100)**(1/12) - 1
    cuota = prestamo * (tem * (1 + tem)**(plazo_años*12)) / ((1 + tem)**(plazo_años*12) - 1)
    mantenimiento = (val_depa * 0.028) / 12
    ingreso_bruto = tarifa_base * ocupacion_act * 0.85 
    impuesto = ingreso_bruto * 0.05
    gastos_op = mantenimiento + impuesto
    flujo_neto = ingreso_bruto - cuota - gastos_op
    roi_airbnb = (flujo_neto * 12 / inv_total) * 100
    utilidad_trad = (renta_trad - cuota - (val_depa*0.012/12) - (renta_trad*0.05)) * 12
    roi_trad = (utilidad_trad / inicial) * 100

    tabs = st.tabs(["💎 Flujo operativo", "🏔️ Patrimonio", "⚖️ Sensibilidad", "🔄 Comparativa tradicional vs airbnb"])

    # --------------------------------------------------------- PESTAÑA 1
    with tabs[0]:
        st.markdown('<div class="section-title">Estructura de capital e ingresos 🏗️</div>', unsafe_allow_html=True)
        st.markdown('<p class="info-box">Cálculo de los recursos propios necesarios y la liquidez inicial para la adquisición del activo 🏢.</p>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="card-base bg-blue"><div class="label-card">Cuota inicial bancaria 🏢</div><div class="val-pos">S/. {inicial:,.0f}</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="card-base bg-blue"><div class="label-card">Inversión en amoblado 🛋️</div><div class="val-pos">S/. {inv_amoblado:,.0f}</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="card-base bg-gray"><div class="label-card">Desembolso total 💎</div><div class="val-pos">S/. {inv_total:,.0f}</div></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">Análisis operativo mensual 💸</div>', unsafe_allow_html=True)
        st.markdown('<p class="info-box">Determinación del flujo de caja mensual después de obligaciones hipotecarias y tributarias 🧾.</p>', unsafe_allow_html=True)
        c4, c5, c6, c7 = st.columns(4)
        with c4: st.markdown(f'<div class="card-base bg-gray"><div class="label-card">Ingreso bruto Airbnb 🏨</div><div class="val-pos">S/. {ingreso_bruto:,.0f}</div></div>', unsafe_allow_html=True)
        with c5: st.markdown(f'<div class="card-base bg-gray"><div class="label-card">Servicio de deuda 🏦</div><div class="val-neg">S/. -{cuota:,.0f}</div></div>', unsafe_allow_html=True)
        with c6: st.markdown(f'<div class="card-base bg-gray"><div class="label-card">Gasto operacional 🧾</div><div class="val-neg">S/. -{gastos_op:,.0f}</div></div>', unsafe_allow_html=True)
        with c7: st.markdown(f'<div class="card-base bg-green"><div class="label-card">Flujo neto de caja 💰</div><div class="val-pos">S/. {flujo_neto:,.0f}</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">Comparativa de rentabilidad 📊</div>', unsafe_allow_html=True)
        cr1, cr2 = st.columns([1, 1.2])
        with cr1:
            st.markdown(f'<div class="card-base bg-gold"><div class="label-card">ROI AIRBNB 📈</div><div class="val-pos" style="color:white;">{roi_airbnb:.2f}%</div></div>', unsafe_allow_html=True)
        with cr2:
            st.table(pd.DataFrame({
                "Alternativa": ["ROI AIRBNB", "S&P 500 (Bolsa USA)", "Factoring Local", "Fondos Mutuos", "Cajas (Plazo Fijo)", "Bonos Soberanos"],
                "Rendimiento": [f"{roi_airbnb:.1f}%", "10.0%", "12.0%", "8.5%", "7.2%", "5.8%"]
            }))

        st.write("---")
        cp1, cp2 = st.columns([1, 1.4])
        años_pb = 25; meses = np.arange(0, años_pb*12+1); f_acum = [-inv_total]; rec = 0
        for m in meses[1:]:
            f_acum.append(f_acum[-1] + (flujo_neto if m <= plazo_años*12 else ingreso_bruto-gastos_op))
            if rec == 0 and f_acum[-1] >= 0: rec = m/12
        
        with cp1:
            st.markdown(f'<div class="card-base bg-indigo"><div class="label-card">Punto de equilibrio (Payback) ⏳</div><div class="val-pos" style="color:white; font-size:2.4rem;">{rec:.1f} Años</div></div>', unsafe_allow_html=True)
            st.markdown('<p class="info-box">Este indicador marca el momento exacto en el que el flujo de caja neto recupera la inversión total de capital propio 🏛️.</p>', unsafe_allow_html=True)
        with cp2:
            fig_pb = go.Figure()
            fig_pb.add_trace(go.Scatter(x=meses/12, y=[min(0, x) for x in f_acum], fill='tozeroy', fillcolor='rgba(248, 81, 73, 0.4)', line=dict(width=0), showlegend=False))
            fig_pb.add_trace(go.Scatter(x=meses/12, y=[max(0, x) for x in f_acum], fill='tozeroy', fillcolor='rgba(63, 185, 80, 0.4)', line=dict(width=0), showlegend=False))
            fig_pb.add_trace(go.Scatter(x=meses/12, y=f_acum, line=dict(color='#ffffff', width=3), name="Balance"))
            fig_pb.update_layout(title="Curva de recuperación de capital (Áreas de balance)", height=350, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family=SYS_SANS, color="white"))
            st.plotly_chart(fig_pb, use_container_width=True)

        st.markdown('<div class="footer-tip">💡 <b>Recomendación operativa:</b> Un Payback menor a 12 años se considera un proyecto de alto rendimiento en el mercado limeño 🌟.</div>', unsafe_allow_html=True)

    # --------------------------------------------------------- PESTAÑA 2
    with tabs[1]:
        st.markdown('<div class="section-title">Evolución del patrimonio y plusvalía 🏔️</div>', unsafe_allow_html=True)
        st.markdown('<p class="info-box">La plusvalía es el beneficio económico obtenido por la diferencia positiva entre el precio de compra y venta del activo 📈.</p>', unsafe_allow_html=True)
        p_slider = st.slider("Plusvalía anual proyectada (%)", 0.0, 10.0, 4.0)
        
        c_p = st.columns(4)
        for i, a in enumerate([5, 10, 15, 20]):
            g = (val_depa * (1 + p_slider/100)**a) - val_depa
            with c_p[i]: 
                st.markdown(f'<div class="card-base bg-blue"><div class="label-card">Plusvalía {a} años 📈</div><div class="val-pos" style="color:white;">S/. {g:,.0f}</div></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">Crecimiento patrimonial acumulado 📊</div>', unsafe_allow_html=True)
        st.markdown('<p class="info-box">Este gráfico visualiza cómo se construye su riqueza (Equity) mediante el pago de deuda y la revalorización del activo 📊.</p>', unsafe_allow_html=True)
        años = np.arange(0, 26); v_mkt = [val_depa * (1+p_slider/100)**a for a in años]
        eq = [v - (prestamo * (1 - a/plazo_años) if a < plazo_años else 0) for a, v in zip(años, v_mkt)]
        
        fig_p = go.Figure()
        fig_p.add_trace(go.Bar(x=años, y=v_mkt, name="Valor mercado", marker_color='#21262d'))
        fig_p.add_trace(go.Scatter(x=años, y=eq, name="Patrimonio real (Equity)", line=dict(color='#58a6ff', width=4)))
        fig_p.update_layout(title="Proyección de valorización vs Deuda remanente", height=450, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family=SYS_SANS, color="white"))
        st.plotly_chart(fig_p, use_container_width=True)

        st.markdown('<div class="footer-tip">🏔️ <b>Tip patrimonial:</b> El verdadero negocio inmobiliario no solo está en la renta, sino en el apalancamiento que genera la plusvalía a largo plazo.</div>', unsafe_allow_html=True)

    # --------------------------------------------------------- PESTAÑA 3
    with tabs[2]:
        st.markdown('<div class="section-title">Análisis de sensibilidad operativa ⚖️</div>', unsafe_allow_html=True)
        st.markdown('<p class="info-box">Permite evaluar la resiliencia del proyecto ante cambios drásticos en la demanda o precios de mercado 🚦.</p>', unsafe_allow_html=True)
        
        def color_roi(val):
            c = '#f85149' if val < 5 else '#d29922' if val < 10 else '#3fb950'
            return f'background-color: {c}; color: #000; font-weight: bold; font-family: {SYS_MONO};'

        # Sensibilidad 1: Ocupación
        st.subheader("Efecto de la ocupación mensual en el ROI")
        st.markdown('<p class="info-box">Sensibilidad basada en días ocupados. Intervalos de 5 días 🌙.</p>', unsafe_allow_html=True)
        cs1_t, cs1_g = st.columns([1, 1.8], vertical_alignment="center")
        d_range = list(range(5, 35, 5))
        roi_d = [((((tarifa_base*d*0.85) - cuota - mantenimiento - (tarifa_base*d*0.85*0.05))*12/inv_total)*100) for d in d_range]
        with cs1_t:
            st.table(pd.DataFrame({"Días/Mes": d_range, "ROI (%)": roi_d}).style.map(color_roi, subset=['ROI (%)']).format({"ROI (%)": "{:.2f}%"}))
        with cs1_g:
            fig_d = go.Figure(go.Scatter(x=d_range, y=roi_d, mode='lines+markers', line=dict(color='#58a6ff', width=5)))
            fig_d.update_layout(height=650, title="Curva de rentabilidad por ocupación", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family=SYS_SANS, color="white"))
            st.plotly_chart(fig_d, use_container_width=True)

        # Sensibilidad 2: Tarifa
        st.subheader("Efecto de la tarifa nocturna en el ROI")
        st.markdown('<p class="info-box">Sensibilidad basada en precio por noche. Intervalos de S/. 25 💰.</p>', unsafe_allow_html=True)
        cs2_t, cs2_g = st.columns([1, 1.8], vertical_alignment="center")
        t_range = list(range(max(50, int(tarifa_base)-75), int(tarifa_base)+100, 25))
        roi_t = [((((t*ocupacion_act*0.85) - cuota - mantenimiento - (t*ocupacion_act*0.85*0.05))*12/inv_total)*100) for t in t_range]
        with cs2_t:
            st.table(pd.DataFrame({"Tarifa S/.": t_range, "ROI (%)": roi_t}).style.map(color_roi, subset=['ROI (%)']).format({"ROI (%)": "{:.2f}%"}))
        with cs2_g:
            fig_t = go.Figure(go.Scatter(x=t_range, y=roi_t, mode='lines+markers', line=dict(color='#3fb950', width=5)))
            fig_t.update_layout(height=650, title="Curva de rentabilidad por tarifa", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family=SYS_SANS, color="white"))
            st.plotly_chart(fig_t, use_container_width=True)

        st.markdown('<div class="footer-tip">⚠️ <b>Recomendación operativa:</b> Si el ROI proyectado cae a niveles amarillos, debe revisar su estrategia de costos o mejorar los amenities para justificar una tarifa más alta.</div>', unsafe_allow_html=True)

    # --------------------------------------------------------- PESTAÑA 4
    with tabs[3]:
        st.markdown('<div class="section-title">Comparativa tradicional vs airbnb 🔄</div>', unsafe_allow_html=True)
        st.markdown('<p class="info-box">Análisis del excedente de caja (Cash Flow) comparando ambos modelos de gestión ⚖️.</p>', unsafe_allow_html=True)
        
        ventaja_anual = (flujo_neto * 12) - utilidad_trad
        dif_roi = roi_airbnb - roi_trad
        
        cc = st.columns(4)
        with cc[0]: st.markdown(f'<div class="card-base bg-green"><div class="label-card">Excedente anual Airbnb 🏆</div><div class="val-pos" style="color:white;">S/. {ventaja_anual:,.0f}</div></div>', unsafe_allow_html=True)
        with cc[1]: st.markdown(f'<div class="card-base bg-gray"><div class="label-card">ROI Airbnb 🏨</div><div class="val-pos" style="color:white;">{roi_airbnb:.1f}%</div></div>', unsafe_allow_html=True)
        with cc[2]: st.markdown(f'<div class="card-base bg-gray"><div class="label-card">ROI tradicional 🏠</div><div class="val-pos" style="color:white;">{roi_trad:.1f}%</div></div>', unsafe_allow_html=True)
        with cc[3]: st.markdown(f'<div class="card-base bg-indigo"><div class="label-card">Diferencial de rois 🚀</div><div class="val-pos" style="color:white;">{dif_roi:+.1f}%</div></div>', unsafe_allow_html=True)
        
        st.write("---")
        st.markdown('<p class="info-box"><b>Interpretación del gráfico:</b> Las barras representan la utilidad neta anualizada. El modelo de rentas cortas (Airbnb) suele presentar mayor flujo, pero requiere mayor gestión operativa 📊.</p>', unsafe_allow_html=True)
        
        labels = ['<b>MODELO AIRBNB</b>', '<b>ALQUILER TRADICIONAL</b>']
        vals = [flujo_neto*12, utilidad_trad]
        fig_c = go.Figure([go.Bar(
            x=labels, y=vals, 
            marker_color=['#3fb950' if v > 0 else '#f85149' for v in vals],
            text=[f'S/. {v:,.0f}' for v in vals],
            textposition='inside', insidetextanchor='middle',
            textfont=dict(size=28, color='white', weight='bold', family=SYS_SANS)
        )])
        fig_c.update_layout(title="Utilidad neta anualizada líquida (S/.)", height=600, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family=SYS_SANS, color="white"))
        st.plotly_chart(fig_c, use_container_width=True)
        
        st.markdown('<p class="info-box" style="text-align:center;"><b>Relación de variables:</b> El excedente de Airbnb compensa el riesgo operativo y los gastos de mantenimiento más intensivos. La renta tradicional es más estable pero sacrifica rentabilidad inmediata.</p>', unsafe_allow_html=True)

        st.markdown('<div class="footer-tip">🏁 <b>Dictamen final:</b> El modelo Airbnb es superior en flujo de caja, ideal para inversores que buscan acelerar la amortización de su crédito.</div>', unsafe_allow_html=True)

# =========================================================
# MOTOR DE PDF (HIGH-DENSITY REPORT)
# =========================================================
def generate_master_pdf(d):
    pdf = FPDF()
    pdf.add_page()
    # Header Estilo Dark Industrial
    pdf.set_fill_color(13, 17, 23); pdf.rect(0, 0, 210, 65, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", 'B', 18)
    pdf.cell(0, 25, "AUDITORIA TECNICA DE INVERSION INMOBILIARIA", ln=True, align='C')
    pdf.set_font("Arial", '', 10); pdf.cell(0, 5, "ELABORADO POR: ING. JANCARLO MENDOZA - EXPERTO INMOBILIARIO", ln=True, align='C')
    pdf.cell(0, 5, f"EMISION: {datetime.now().strftime('%d/%m/%Y')} | LIMA, PERU", ln=True, align='C')
    
    pdf.ln(35); pdf.set_text_color(0, 0, 0)

    # Bloque 1: Capital
    pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, "1. Desglose de capital e inversion inicial", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.multi_cell(0, 5, "Este informe analiza la viabilidad financiera del activo. La inversion inicial contempla el 20% del valor del inmueble mas el equipamiento necesario para operar en plataformas digitales de alta gama.")
    pdf.ln(3)
    rows = [["CONCEPTO", "VALOR (S/.)"], ["Precio Venta Activo", f"{d['val']:,.0f}"], ["Capital Propio (Cuota Inicial)", f"{d['ini']:,.0f}"], ["Inversion en Equipamiento", f"{d['inv_a']:,.0f}"], ["DESEMBOLSO TOTAL REQUERIDO", f"{d['inv_t']:,.0f}"]]
    for r in rows:
        pdf.cell(110, 8, r[0], 1); pdf.cell(80, 8, r[1], 1, ln=True, align='R')

    # Bloque 2: Operatividad
    pdf.ln(10); pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, "2. Analisis de flujo y rentabilidad anual", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.multi_cell(0, 5, "Se ha calculado un flujo de caja neto considerando la tasa TCEA pactada y los gastos operativos locales (mantenimiento y tributos de ley).")
    pdf.ln(3)
    pdf.cell(0, 8, f"- ROI Anualizado Modelo Airbnb: {d['roi']:.2f}%", ln=True)
    pdf.cell(0, 8, f"- Flujo de Caja Neto Mensual: S/. {d['flujo']:,.2f}", ln=True)
    pdf.cell(0, 8, f"- Tiempo de Recuperacion de Capital (Payback): {d['pb']:.1f} años", ln=True)

    # Bloque 3: Estrategia
    pdf.ln(10); pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, "3. Veredicto estrategico", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.multi_cell(0, 5, "Basado en los datos, el modelo de rentas cortas genera un excedente de caja significativo que permite una amortizacion acelerada de la deuda bancaria. Se recomienda mantener estandares de limpieza y atencion superiores para sostener la tarifa proyectada.")
    
    pdf.ln(15); pdf.set_font("Arial", 'I', 8)
    pdf.multi_cell(0, 4, "AVISO: Los calculos aqui presentados son proyecciones basadas en condiciones actuales de mercado. Jancarlo Mendoza no garantiza rentabilidades futuras ante cambios en leyes tributarias o politicas de plataformas externas.")

    return pdf.output(dest='S').encode('latin-1')

if st.session_state.authenticated:
    st.write("---")
    if st.button("📥 GENERAR REPORTE TECNICO COMPLETO (PDF)"):
        pdf_bytes = generate_master_pdf({
            "val": val_depa, "ini": inicial, "inv_a": inv_amoblado, "inv_t": inv_total,
            "roi": roi_airbnb, "flujo": flujo_neto, "pb": rec
        })
        st.download_button("Descargar Informe de Auditoría", data=pdf_bytes, file_name=f"Auditoria_Inmobiliaria_JM.pdf")
