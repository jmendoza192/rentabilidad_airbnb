import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime

# =========================================================
# 0. CONFIGURACIÓN Y ESTÉTICA INDUSTRIAL TOTAL
# =========================================================
try:
    st.set_page_config(page_title="Auditoría Pro | JM", layout="wide")
except:
    pass

# Fuentes del Proyecto Base
FONT_SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
FONT_MONO = "'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace"

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
    # CSS: FUERZA BRUTA TIPOGRÁFICA Y ELIMINACIÓN DE BOTONES +/-
    st.markdown(f"""
        <style>
        /* 1. Fuente Global */
        html, body, [class*="css"], .stMarkdown, p, div, span {{
            font-family: {FONT_SANS} !important;
            color: #ffffff;
        }}
        
        /* 2. Monospace para Datos y Tablas */
        .stTable, [data-testid="stTable"], code, .val-pos, .val-neg {{
            font-family: {FONT_MONO} !important;
        }}

        /* 3. Inputs Limpios (Sin + / -) */
        button.step-up, button.step-down {{ display: none !important; }}
        input[type=number]::-webkit-inner-spin-button, 
        input[type=number]::-webkit-outer-spin-button {{ -webkit-appearance: none; margin: 0; }}
        input[type=number] {{ -moz-appearance: textfield; }}

        .main {{ background-color: #0e1117; }}
        
        /* 4. Estilo de Títulos y Secciones */
        .section-title {{ 
            color: #ffffff; font-size: 1.5rem; font-weight: 700; 
            padding: 15px 0; border-bottom: 2px solid #30363d; margin: 25px 0 15px 0;
            text-transform: uppercase; letter-spacing: 1px;
        }}

        /* 5. Tarjetas Multicolores Letras Blancas */
        .card-base {{
            border: 1px solid #30363d; border-radius: 8px; padding: 22px;
            text-align: center; margin-bottom: 15px; color: #ffffff !important;
        }}
        .bg-blue {{ background-color: #1c3d5a; border-left: 5px solid #3182ce; }}
        .bg-green {{ background-color: #1b4332; border-left: 5px solid #48bb78; }}
        .bg-red {{ background-color: #4c1d1d; border-left: 5px solid #f56565; }}
        .bg-gray {{ background-color: #21262d; border-left: 5px solid #8b949e; }}
        .bg-gold {{ background-color: #744210; border-left: 5px solid #ecc94b; }}
        .bg-indigo {{ background-color: #312e81; border-left: 5px solid #818cf8; }}

        .val-pos {{ color: #60a5fa; font-size: 2rem; font-weight: 800; }}
        .val-neg {{ color: #f87171; font-size: 2rem; font-weight: 800; }}
        .label-card {{ font-size: 0.8rem; font-weight: 600; text-transform: uppercase; margin-bottom: 10px; opacity: 0.9; }}

        .info-text {{ font-size: 0.9rem; color: #8b949e; line-height: 1.6; margin-bottom: 20px; }}
        .footer-tip {{
            background-color: #161b22; color: #ffffff; padding: 25px;
            border: 1px solid #30363d; border-left: 5px solid #58a6ff; border-radius: 4px; margin-top: 40px;
        }}
        </style>
        """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("⚙️ Parámetros Base")
        val_depa = st.number_input("Precio Venta (S/.) 🏠", value=280000)
        inv_amoblado = st.number_input("Inversión Equipamiento (S/.) 🛋️", value=30000)
        st.write("---")
        tcea = st.number_input("TCEA Bancaria (%) 🏦", value=9.8)
        plazo_años = st.selectbox("Plazo (Años) 🗓️", [10, 15, 20, 25], index=2)
        st.write("---")
        tarifa_base = st.number_input("Tarifa Airbnb (S/.) 💰", value=210)
        ocupacion_act = st.selectbox("Días Ocupados/Mes 🌙", list(range(1, 31)), index=19)
        st.write("---")
        renta_trad = st.number_input("Renta Tradicional (S/.) 🏠", value=1950)

    # LÓGICA FINANCIERA
    inicial = val_depa * 0.20
    inv_total = inicial + inv_amoblado
    prestamo = val_depa - inicial
    tem = (1 + tcea/100)**(1/12) - 1
    cuota = prestamo * (tem * (1 + tem)**(plazo_años*12)) / ((1 + tem)**(plazo_años*12) - 1)
    mantenimiento = (val_depa * 0.025) / 12
    ingreso_bruto = tarifa_base * ocupacion_act * 0.85 
    impuesto = ingreso_bruto * 0.05
    gastos_op = mantenimiento + impuesto
    flujo_neto = ingreso_bruto - cuota - gastos_op
    roi_airbnb = (flujo_neto * 12 / inv_total) * 100
    utilidad_trad = (renta_trad - cuota - (val_depa*0.012/12) - (renta_trad*0.05)) * 12
    roi_trad = (utilidad_trad / inicial) * 100

    tabs = st.tabs(["📊 FLUJO OPERATIVO", "🏔️ PATRIMONIO", "⚖️ SENSIBILIDAD", "🔄 COMPARATIVA TRADICIONAL VS AIRBNB"])

    # --------------------------------------------------------- PESTAÑA 1
    with tabs[0]:
        st.markdown('<div class="section-title">🏗️ Estructura de Capital e Ingresos</div>', unsafe_allow_html=True)
        st.markdown('<p class="info-text">Desglose del capital líquido requerido para la ejecución del proyecto inmobiliario 🏛️.</p>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="card-base bg-blue"><div class="label-card">Cuota Inicial (20%) 🏢</div><div class="val-pos">S/. {inicial:,.0f}</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="card-base bg-blue"><div class="label-card">Capex Amoblado 🛋️</div><div class="val-pos">S/. {inv_amoblado:,.0f}</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="card-base bg-gray"><div class="label-card">Cash-Out Necesario 💎</div><div class="val-pos">S/. {inv_total:,.0f}</div></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">💸 Análisis Operativo Mensual</div>', unsafe_allow_html=True)
        st.markdown('<p class="info-text">Cálculo del flujo de caja neto tras obligaciones financieras, fiscales y operativas 🧾.</p>', unsafe_allow_html=True)
        c4, c5, c6, c7 = st.columns(4)
        with c4: st.markdown(f'<div class="card-base bg-gray"><div class="label-card">Ventas Airbnb 🏨</div><div class="val-pos">S/. {ingreso_bruto:,.0f}</div></div>', unsafe_allow_html=True)
        with c5: st.markdown(f'<div class="card-base bg-gray"><div class="label-card">Servicio Deuda 🏦</div><div class="val-neg">S/. -{cuota:,.0f}</div></div>', unsafe_allow_html=True)
        with c6: st.markdown(f'<div class="card-base bg-gray"><div class="label-card">OpEx e Impuestos 🧾</div><div class="val-neg">S/. -{gastos_op:,.0f}</div></div>', unsafe_allow_html=True)
        with c7: st.markdown(f'<div class="card-base bg-green"><div class="label-card">Flujo Neto Final 💰</div><div class="val-pos">S/. {flujo_neto:,.0f}</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">📈 Benchmark de Rentabilidad</div>', unsafe_allow_html=True)
        cr1, cr2 = st.columns([1, 1.2])
        with cr1:
            st.markdown(f'<div class="card-base bg-gold"><div class="label-card">ROI Proyectado Anual 📈</div><div class="val-pos" style="color:white;">{roi_airbnb:.2f}%</div></div>', unsafe_allow_html=True)
        with cr2:
            st.table(pd.DataFrame({"Activo": ["Auditoría JM", "S&P 500 (Histórico)", "Plazo Fijo Local"], "ROI Estimado": [f"{roi_airbnb:.1f}%", "10.0%", "6.2%"]}))

        st.write("---")
        cp1, cp2 = st.columns([1, 1.2])
        años_pb = 25; meses = np.arange(0, años_pb*12+1); f_acum = [-inv_total]; rec = 0
        for m in meses[1:]:
            f_acum.append(f_acum[-1] + (flujo_neto if m <= plazo_años*12 else ingreso_bruto-gastos_op))
            if rec == 0 and f_acum[-1] >= 0: rec = m/12
        
        with cp1:
            st.markdown(f'<div class="card-base bg-indigo" style="border: 2px solid white;"><div class="label-card">Punto de Equilibrio (Payback) ⏳</div><div class="val-pos" style="color:white; font-size:2.4rem;">{rec:.1f} Años</div></div>', unsafe_allow_html=True)
            st.markdown('<p class="info-text"><b>Nota Técnica:</b> El Payback mide el tiempo necesario para que los flujos netos acumulados igualen la inversión inicial de capital propio 🏛️.</p>', unsafe_allow_html=True)
        with cp2:
            fig_pb = go.Figure()
            fig_pb.add_trace(go.Scatter(x=meses/12, y=[min(0, x) for x in f_acum], fill='tozeroy', fillcolor='rgba(248, 113, 113, 0.4)', line=dict(width=0), showlegend=False))
            fig_pb.add_trace(go.Scatter(x=meses/12, y=[max(0, x) for x in f_acum], fill='tozeroy', fillcolor='rgba(16, 185, 129, 0.4)', line=dict(width=0), showlegend=False))
            fig_pb.add_trace(go.Scatter(x=meses/12, y=f_acum, line=dict(color='#ffffff', width=3), name="Balance Neto"))
            fig_pb.update_layout(title="<b>CURVA DE RECUPERACIÓN DE CAPITAL (ROJO: DÉFICIT / VERDE: UTILIDAD)</b>", height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family=FONT_SANS, color="white"))
            st.plotly_chart(fig_pb, use_container_width=True)

        st.markdown('<div class="footer-tip">💡 <b>RECOMENDACIÓN OPERATIVA:</b> La optimización de costos en mantenimiento preventivo puede elevar el flujo neto en un 5% anual 🌟.</div>', unsafe_allow_html=True)

    # --------------------------------------------------------- PESTAÑA 2
    with tabs[1]:
        st.markdown('<div class="section-title">🏔️ Proyección Patrimonial por Plusvalía</div>', unsafe_allow_html=True)
        st.markdown('<p class="info-text"><b>Nota Informativa:</b> La plusvalía es el incremento del valor de mercado del inmueble debido a factores externos (ubicación, demanda, inflación) 📈.</p>', unsafe_allow_html=True)
        p_slider = st.slider("Expectativa Plusvalía Anual (%)", 0.0, 10.0, 4.0)
        
        c_p = st.columns(4)
        for i, a in enumerate([5, 10, 15, 20]):
            g = (val_depa * (1 + p_slider/100)**a) - val_depa
            with c_p[i]: 
                st.markdown(f'<div class="card-base bg-blue"><div class="label-card">Plusvalía en {a}A 📈</div><div class="val-pos" style="color:white;">S/. {g:,.0f}</div></div>', unsafe_allow_html=True)
                st.caption(f"ℹ️ Beneficio bruto por tiempo.")
        
        st.markdown('<div class="section-title">📊 Gráfico de Equity Real</div>', unsafe_allow_html=True)
        st.markdown('<p class="info-text"><b>Análisis:</b> Este gráfico muestra la relación entre el valor del activo y el Equity (tu propiedad real sobre el bien conforme pagas al banco) 📊.</p>', unsafe_allow_html=True)
        años = np.arange(0, 26); v_mkt = [val_depa * (1+p_slider/100)**a for a in años]
        eq = [v - (prestamo * (1 - a/plazo_años) if a < plazo_años else 0) for a, v in zip(años, v_mkt)]
        
        fig_p = go.Figure()
        fig_p.add_trace(go.Bar(x=años, y=v_mkt, name="Valor Mercado", marker_color='#30363d'))
        fig_p.add_trace(go.Scatter(x=años, y=eq, name="Patrimonio Real (Equity)", line=dict(color='#58a6ff', width=4)))
        fig_p.update_layout(title="<b>CRECIMIENTO DE VALOR VS DEUDA REMANENTE</b>", height=450, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family=FONT_SANS, color="white"))
        st.plotly_chart(fig_p, use_container_width=True)

        st.markdown('<div class="footer-tip">📈 <b>TIP FINANCIERO:</b> El Equity es su verdadera riqueza neta. Considere refinanciar su deuda si el valor del mercado sube considerablemente.</div>', unsafe_allow_html=True)

    # --------------------------------------------------------- PESTAÑA 3
    with tabs[2]:
        st.markdown('<div class="section-title">⚖️ Matrices de Sensibilidad Operativa</div>', unsafe_allow_html=True)
        st.markdown('<p class="info-text"><b>Nota:</b> Estas matrices permiten prever cómo variaciones mínimas en el mercado afectan la rentabilidad final del activo 🚦.</p>', unsafe_allow_html=True)
        
        def color_roi(val):
            c = '#f87171' if val < 5 else '#fbbf24' if val < 10 else '#4ade80'
            return f'background-color: {c}; color: #000; font-weight: bold; font-family: {FONT_MONO};'

        # Sensibilidad 1
        st.subheader("📍 Sensibilidad: Días de Ocupación")
        st.markdown('<p class="info-text">Impacto de la vacancia en el ROI. Intervalos de 5 días 🌙.</p>', unsafe_allow_html=True)
        cs1_t, cs1_g = st.columns([1, 1.8], vertical_alignment="center")
        d_range = list(range(5, 35, 5))
        roi_d = [((((tarifa_base*d*0.85) - cuota - mantenimiento - (tarifa_base*d*0.85*0.05))*12/inv_total)*100) for d in d_range]
        with cs1_t:
            st.table(pd.DataFrame({"Días/Mes": d_range, "ROI (%)": roi_d}).style.map(color_roi, subset=['ROI (%)']).format({"ROI (%)": "{:.2f}%"}))
        with cs1_g:
            fig_d = go.Figure(go.Scatter(x=d_range, y=roi_d, mode='lines+markers', line=dict(color='#60a5fa', width=5), marker=dict(size=12)))
            fig_d.update_layout(height=650, title="<b>CORRELACIÓN OCUPACIÓN VS ROI</b>", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family=FONT_SANS, color="white"))
            st.plotly_chart(fig_d, use_container_width=True)

        # Sensibilidad 2
        st.subheader("💰 Sensibilidad: Tarifa por Noche")
        st.markdown('<p class="info-text">Impacto del precio de mercado en la rentabilidad. Intervalos de S/. 10 💰.</p>', unsafe_allow_html=True)
        cs2_t, cs2_g = st.columns([1, 1.8], vertical_alignment="center")
        t_range = list(range(int(tarifa_base)-30, int(tarifa_base)+40, 10))
        roi_t = [((((t*ocupacion_act*0.85) - cuota - mantenimiento - (t*ocupacion_act*0.85*0.05))*12/inv_total)*100) for t in t_range]
        with cs2_t:
            st.table(pd.DataFrame({"Tarifa S/.": t_range, "ROI (%)": roi_t}).style.map(color_roi, subset=['ROI (%)']).format({"ROI (%)": "{:.2f}%"}))
        with cs2_g:
            fig_t = go.Figure(go.Scatter(x=t_range, y=roi_t, mode='lines+markers', line=dict(color='#34d399', width=5), marker=dict(size=12)))
            fig_t.update_layout(height=650, title="<b>CORRELACIÓN TARIFA VS ROI</b>", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family=FONT_SANS, color="white"))
            st.plotly_chart(fig_t, use_container_width=True)

        st.markdown('<div class="footer-tip">⚠️ <b>RECOMENDACIÓN:</b> Un ROI por debajo del 5% indica que el activo no está cubriendo el riesgo operativo de Airbnb. Reevalúe precios.</div>', unsafe_allow_html=True)

    # --------------------------------------------------------- PESTAÑA 4
    with tabs[3]:
        st.markdown('<div class="section-title">🔄 Veredicto: Tradicional vs Airbnb</div>', unsafe_allow_html=True)
        st.markdown('<p class="info-text">Evaluación comparativa de la utilidad líquida anualizada tras todas las obligaciones ⚖️.</p>', unsafe_allow_html=True)
        
        ventaja_anual = (flujo_neto * 12) - utilidad_trad
        dif_roi = roi_airbnb - roi_trad
        
        cc = st.columns(4)
        with cc[0]: st.markdown(f'<div class="card-base bg-green"><div class="label-card">Excedente Anual Airbnb 🏆</div><div class="val-pos" style="color:white;">S/. {ventaja_anual:,.0f}</div></div>', unsafe_allow_html=True)
        with cc[1]: st.markdown(f'<div class="card-base bg-gray"><div class="label-card">ROI Airbnb 🏨</div><div class="val-pos" style="color:white;">{roi_airbnb:.1f}%</div></div>', unsafe_allow_html=True)
        with cc[2]: st.markdown(f'<div class="card-base bg-gray"><div class="label-card">ROI Tradicional 🏠</div><div class="val-pos" style="color:white;">{roi_trad:.1f}%</div></div>', unsafe_allow_html=True)
        with cc[3]: st.markdown(f'<div class="card-base bg-indigo"><div class="label-card">Diferencial Rentabilidad 🚀</div><div class="val-pos" style="color:white;">{dif_roi:+.1f}%</div></div>', unsafe_allow_html=True)
        
        st.write("---")
        st.markdown('<p class="info-text"><b>Gráfico de Utilidad:</b> Visualización del excedente de caja anualizado. Las barras muestran el "cash flow" real después de pagar al banco 📊.</p>', unsafe_allow_html=True)
        
        labels = ['<b>MODELO AIRBNB</b>', '<b>RENTA TRADICIONAL</b>']
        vals = [flujo_neto*12, utilidad_trad]
        fig_c = go.Figure([go.Bar(
            x=labels, y=vals, 
            marker_color=['#10b981' if v > 0 else '#ef4444' for v in vals],
            text=[f'S/. {v:,.0f}' for v in vals],
            textposition='inside', insidetextanchor='middle',
            textfont=dict(size=30, color='white', weight='bold', family=FONT_MONO)
        )])
        fig_c.update_layout(title="<b>UTILIDAD NETA ANUALIZADA LÍQUIDA (S/.)</b>", height=600, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family=FONT_SANS, color="white"))
        st.plotly_chart(fig_c, use_container_width=True)
        
        st.markdown('<p class="info-text" style="text-align:center;"><b>Análisis de Variables:</b> El modelo Airbnb se ve favorecido por la tarifa dinámica, pero tiene un OpEx (Gastos Operativos) mayor por servicios y limpieza. La Renta Tradicional minimiza la vacancia pero sacrifica el flujo mensual de caja libre.</p>', unsafe_allow_html=True)

        st.markdown('<div class="footer-tip">🏁 <b>DICTAMEN:</b> La estrategia Airbnb es ganadora siempre que la ubicación garantice una ocupación superior al 60% mensual.</div>', unsafe_allow_html=True)

# =========================================================
# MOTOR DE PDF (DATA-RICH VERSION)
# =========================================================
def generate_master_pdf(d):
    pdf = FPDF()
    pdf.add_page()
    # Header Industrial
    pdf.set_fill_color(14, 17, 23); pdf.rect(0, 0, 210, 60, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", 'B', 18)
    pdf.cell(0, 20, "AUDITORIA DE INVERSION INMOBILIARIA", ln=True, align='C')
    pdf.set_font("Arial", '', 11); pdf.cell(0, 5, "ELABORADO POR: ING. JANCARLO MENDOZA - EXPERTO INMOBILIARIO", ln=True, align='C')
    pdf.cell(0, 5, f"FECHA DE REPORTE: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align='C')
    
    pdf.ln(35); pdf.set_text_color(0, 0, 0)

    # Bloque 1: Capital
    pdf.set_font("Arial", 'B', 13); pdf.cell(0, 10, "1. INGENIERIA DE CAPITAL Y CAPEX", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.multi_cell(0, 5, "Este análisis contempla la inversión inicial líquida (Cash-Out) necesaria para la adquisición de la unidad, amoblado completo y puesta en marcha operativa.")
    pdf.ln(2)
    rows = [["CONCEPTO", "VALOR (S/.)"], ["Precio de Lista", f"{d['val']:,.0f}"], ["Cuota Inicial (20%)", f"{d['ini']:,.0f}"], ["Mobiliario y Deco", f"{d['inv_a']:,.0f}"], ["INVERSION TOTAL", f"{d['inv_t']:,.0f}"]]
    for r in rows:
        pdf.cell(100, 8, r[0], 1); pdf.cell(90, 8, r[1], 1, ln=True, align='R')

    # Bloque 2: Operatividad
    pdf.ln(10); pdf.set_font("Arial", 'B', 13); pdf.cell(0, 10, "2. ANALISIS OPERATIVO MENSUAL (AIRBNB)", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 7, f"- Ingreso Bruto Estimado (Ocup. {ocupacion_act} dias): S/. {d['bruto']:,.2f}", ln=True)
    pdf.cell(0, 7, f"- Cuota Hipotecaria (TCEA {tcea}%): S/. {cuota:,.2f}", ln=True)
    pdf.cell(0, 7, f"- Gastos Operativos (Mantenimiento + Impuestos): S/. {gastos_op:,.2f}", ln=True)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 10, f"CASH FLOW NETO MENSUAL: S/. {d['flujo']:,.2f}", ln=True)

    # Bloque 3: Veredicto
    pdf.ln(10); pdf.set_font("Arial", 'B', 13); pdf.cell(0, 10, "3. METRICAS COMPARATIVAS Y VERDICTO", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 7, f"- ROI Anualizado Airbnb: {d['roi']:.2f}%", ln=True)
    pdf.cell(0, 7, f"- ROI Anualizado Tradicional: {d['roi_t']:.2f}%", ln=True)
    pdf.cell(0, 7, f"- Tiempo de Recuperacion (Payback): {d['pb']:.1f} Años", ln=True)
    
    pdf.ln(10); pdf.set_font("Arial", 'I', 8)
    pdf.multi_cell(0, 4, "AVISO LEGAL: Este reporte es una herramienta tecnica de proyeccion financiera. Los resultados reales pueden variar segun la gestion operativa del propietario y las fluctuaciones del mercado inmobiliario en Lima. Jancarlo Mendoza recomienda una auditoria legal del reglamento interno antes de la compra.")

    return pdf.output(dest='S').encode('latin-1')

if st.session_state.authenticated:
    st.write("---")
    if st.button("📥 GENERAR INFORME TECNICO PROFESIONAL (PDF)"):
        pdf_bytes = generate_master_pdf({
            "val": val_depa, "ini": inicial, "inv_a": inv_amoblado, "inv_t": inv_total,
            "bruto": ingreso_bruto, "flujo": flujo_neto, "roi": roi_airbnb, 
            "roi_t": roi_trad, "pb": rec
        })
        st.download_button("Descargar Auditoría PDF", data=pdf_bytes, file_name=f"Auditoria_Inmobiliaria_JM.pdf")
