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

# Definición de fuentes de sistema (Purga de Roboto/Webfonts)
SYS_SANS = '-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif'
SYS_MONO = 'ui-monospace, SFMono-Regular, "SF Mono", Menlo, Monaco, Consolas, "Liberation Mono", monospace'

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
        html, body, [class*="css"], .stMarkdown, p, div, span, label, button, .stSelectbox, .stNumberInput {{
            font-family: {SYS_SANS} !important;
            color: #ffffff;
        }}
        
        /* 2. Monospace para Datos y Números */
        .stTable, [data-testid="stTable"], code, .val-pos, .val-neg, .mono-font, .stMetric, .stDataFrame, .stNumberInput input {{
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
            text-transform: lowercase;
        }}
        .section-title::first-letter {{ text-transform: uppercase; }}

        /* 5. Tarjetas Industriales */
        .card-base {{
            border: 1px solid #30363d; border-radius: 4px; padding: 16px;
            text-align: center; margin-bottom: 12px; color: #ffffff !important;
        }}
        .bg-blue {{ background-color: #051e3e; }}
        .bg-green {{ background-color: #062d1a; }}
        .bg-red {{ background-color: #3e0a0a; }}
        .bg-gray {{ background-color: #161b22; }}
        .bg-gold {{ background-color: #3e2b05; }}
        .bg-indigo {{ background-color: #1e1b4b; }}
        .bg-light-green {{ background-color: #1b4332; border: 1px solid #3fb950; }}

        .val-pos {{ color: #58a6ff; font-size: 1.8rem; font-weight: 700; white-space: nowrap; }}
        .val-neg {{ color: #f85149; font-size: 1.8rem; font-weight: 700; white-space: nowrap; }}
        .label-card {{ font-size: 0.85rem; font-weight: 500; margin-bottom: 5px; opacity: 0.9; }}

        .info-box {{ font-size: 0.9rem; color: #8b949e; line-height: 1.6; margin-bottom: 20px; }}
        .footer-tip {{
            background-color: #0d1117; color: #ffffff; padding: 20px;
            border: 1px solid #30363d; border-left: 4px solid #58a6ff; margin-top: 30px;
        }}
        </style>
        """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("Entrada de datos ⚙️")
        val_depa = st.number_input("Precio de venta (S/.) 🏠", value=420000)
        inv_amoblado = st.number_input("Inversión amoblado (S/.) 🛋️", value=48000)
        st.write("---")
        tcea = st.number_input("Tcea bancaria (%) 🏦", value=10.2)
        plazo_años = st.selectbox("Plazo (Años) 🗓️", [10, 15, 20, 25], index=2)
        st.write("---")
        tarifa_base = st.number_input("Tarifa por noche (S/.) 💰", value=320)
        ocupacion_act = st.selectbox("Días ocupados al mes 🌙", list(range(1, 31)), index=19)
        st.write("---")
        renta_trad = st.number_input("Renta tradicional (S/.) 🏠", value=2800)

    # LÓGICA DE NEGOCIO
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

    tabs = st.tabs(["💎 Flujo operativo", "🏔️ Patrimonio", "⚖️ Sensibilidad", "🔄 Comparativa tradicional vs airbnb"])

    # --------------------------------------------------------- PESTAÑA 1
    with tabs[0]:
        st.markdown('<div class="section-title">Estructura de capital e ingresos 🏗️</div>', unsafe_allow_html=True)
        st.markdown('<p class="info-box">Cálculo del patrimonio neto inicial requerido y las fuentes de financiamiento para la adquisición 🏢.</p>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="card-base bg-blue"><div class="label-card">Cuota inicial 🏢</div><div class="val-pos">S/. {inicial:,.0f}</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="card-base bg-blue"><div class="label-card">Inversión amoblado 🛋️</div><div class="val-pos">S/. {inv_amoblado:,.0f}</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="card-base bg-gray"><div class="label-card">Desembolso total 💎</div><div class="val-pos">S/. {inv_total:,.0f}</div></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">Análisis operativo mensual 💸</div>', unsafe_allow_html=True)
        st.markdown('<p class="info-box">Flujo de caja libre tras el cumplimiento de obligaciones hipotecarias, tributarias y costos operativos 🧾.</p>', unsafe_allow_html=True)
        c4, c5, c6, c7 = st.columns(4)
        with c4: st.markdown(f'<div class="card-base bg-gray"><div class="label-card">Ingresos brutos 🏨</div><div class="val-pos">S/. {ingreso_bruto:,.0f}</div></div>', unsafe_allow_html=True)
        with c5: st.markdown(f'<div class="card-base bg-gray"><div class="label-card">Pago hipotecario 🏦</div><div class="val-neg">S/. -{cuota:,.0f}</div></div>', unsafe_allow_html=True)
        with c6: st.markdown(f'<div class="card-base bg-gray"><div class="label-card">Opex e impuestos 🧾</div><div class="val-neg">S/. -{gastos_op:,.0f}</div></div>', unsafe_allow_html=True)
        with c7: st.markdown(f'<div class="card-base bg-green"><div class="label-card">Flujo neto 💰</div><div class="val-pos">S/. {flujo_neto:,.0f}</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">Comparativa de rentabilidad ROI AIRBNB vs Mercado 📉</div>', unsafe_allow_html=True)
        cr1, cr2 = st.columns([1, 1.2])
        with cr1:
            st.markdown(f'<div class="card-base bg-light-green"><div class="label-card">ROI AIRBNB 🚀</div><div class="val-pos" style="color:white;">{roi_airbnb:.2f}%</div></div>', unsafe_allow_html=True)
        with cr2:
            st.table(pd.DataFrame({
                "Tipo de inversión": ["ROI AIRBNB", "Bolsa (S&P 500)", "Fondos mutuos", "Plazo fijo", "Cajas municipales", "Bonos del tesoro"],
                "Retorno esperado": [f"{roi_airbnb:.1f}%", "10.0%", "9.0%", "7.5%", "8.2%", "5.5%"]
            }))

        st.write("---")
        años_pb = 25; meses = np.arange(0, años_pb*12+1); f_acum = [-inv_total]; rec = 0
        for m in meses[1:]:
            f_acum.append(f_acum[-1] + (flujo_neto if m <= plazo_años*12 else ingreso_bruto-gastos_op))
            if rec == 0 and f_acum[-1] >= 0: rec = m/12
        
        cp1, cp2 = st.columns([0.8, 1.2])
        with cp1:
            st.markdown(f'<div class="card-base bg-indigo"><div class="label-card">Tiempo de recuperación (Payback) ⏳</div><div class="val-pos" style="color:white; font-size:2.5rem;">{rec:.1f} Años</div></div>', unsafe_allow_html=True)
            st.markdown('<p class="info-box">Muestra el momento exacto en el que la utilidad neta acumulada reembolsa la inversión inicial desembolsada por el propietario 🏛️.</p>', unsafe_allow_html=True)
        with cp2:
            fig_pb = go.Figure()
            fig_pb.add_trace(go.Scatter(x=meses/12, y=[min(0, x) for x in f_acum], fill='tozeroy', fillcolor='rgba(248, 81, 73, 0.4)', line=dict(width=0), showlegend=False))
            fig_pb.add_trace(go.Scatter(x=meses/12, y=[max(0, x) for x in f_acum], fill='tozeroy', fillcolor='rgba(63, 185, 80, 0.4)', line=dict(width=0), showlegend=False))
            fig_pb.add_trace(go.Scatter(x=meses/12, y=f_acum, line=dict(color='#ffffff', width=3), name="Balance"))
            fig_pb.update_layout(title="Progreso de recuperación de capital", height=380, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family=SYS_MONO, color="white"))
            st.plotly_chart(fig_pb, use_container_width=True)

        st.markdown('<div class="footer-tip">💡 <b>Recomendación financiera:</b> Mantenga un fondo de reserva equivalente a 3 meses de cuota hipotecaria para mitigar riesgos de vacacionalidad imprevista.</div>', unsafe_allow_html=True)

    # --------------------------------------------------------- PESTAÑA 2
    with tabs[1]:
        st.markdown('<div class="section-title">Evolución del patrimonio y plusvalía 🏔️</div>', unsafe_allow_html=True)
        st.markdown('<p class="info-box">Análisis de la valorización del activo por entorno urbano y demanda del mercado inmobiliario local 📊.</p>', unsafe_allow_html=True)
        p_slider = st.slider("Expectativa de plusvalía anual (%)", 0.0, 10.0, 4.0)
        
        c_p = st.columns(4)
        for i, a in enumerate([5, 10, 15, 20]):
            g = (val_depa * (1 + p_slider/100)**a) - val_depa
            with c_p[i]: 
                st.markdown(f'<div class="card-base bg-blue"><div class="label-card">Plusvalía {a} años 📈</div><div class="val-pos" style="color:white; font-size:1.6rem;">S/. {g:,.0f}</div></div>', unsafe_allow_html=True)
                st.caption(f"Valorización bruta a {a} años.")
        
        st.markdown('<div class="section-title">Gráfico de crecimiento patrimonial real 📊</div>', unsafe_allow_html=True)
        st.markdown('<p class="info-box">Visualización del patrimonio neto (Equity): Diferencia entre el valor de mercado proyectado y la deuda pendiente 🏔️.</p>', unsafe_allow_html=True)
        años = np.arange(0, 26); v_mkt = [val_depa * (1+p_slider/100)**a for a in años]
        eq = [v - (prestamo * (1 - a/plazo_años) if a < plazo_años else 0) for a, v in zip(años, v_mkt)]
        
        fig_p = go.Figure()
        fig_p.add_trace(go.Bar(x=años, y=v_mkt, name="Valor mercado", marker_color='#21262d'))
        fig_p.add_trace(go.Scatter(x=años, y=eq, name="Patrimonio real (Equity)", line=dict(color='#58a6ff', width=4)))
        fig_p.update_layout(title="Crecimiento del activo vs Amortización de deuda", height=450, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family=SYS_MONO, color="white"))
        st.plotly_chart(fig_p, use_container_width=True)

        st.markdown('<div class="footer-tip">📊 <b>Nota informativa:</b> Al finalizar el préstamo bancario, el valor total de la propiedad (incluyendo plusvalía acumulada) pasa a formar parte de su patrimonio líquido.</div>', unsafe_allow_html=True)

    # --------------------------------------------------------- PESTAÑA 3
    with tabs[2]:
        st.markdown('<div class="section-title">Análisis de sensibilidad operativa ⚖️</div>', unsafe_allow_html=True)
        st.markdown('<p class="info-box">Pruebas de estrés sobre las variables críticas del modelo: Ocupación y Tarifa nocturna 🚦.</p>', unsafe_allow_html=True)
        
        def color_roi(val):
            c = '#f85149' if val < 5 else '#d29922' if val < 10 else '#3fb950'
            return f'background-color: {c}; color: #000; font-weight: bold; font-family: {SYS_MONO};'

        # Sensibilidad 1
        st.subheader("Sensibilidad: Días de ocupación vs ROI")
        st.markdown('<p class="info-box">Impacto de la tasa de vacancia en el retorno de inversión (intervalos de 5 días) 🌙.</p>', unsafe_allow_html=True)
        cs1_t, cs1_g = st.columns([1, 1.8], vertical_alignment="center")
        d_range = list(range(5, 35, 5))
        roi_d = [((((tarifa_base*d*0.85) - cuota - mantenimiento - (tarifa_base*d*0.85*0.05))*12/inv_total)*100) for d in d_range]
        with cs1_t:
            st.table(pd.DataFrame({"Días/Mes": d_range, "ROI (%)": roi_d}).style.map(color_roi, subset=['ROI (%)']).format({"ROI (%)": "{:.2f}%"}))
        with cs1_g:
            fig_d = go.Figure(go.Scatter(x=d_range, y=roi_d, mode='lines+markers', line=dict(color='#58a6ff', width=5)))
            fig_d.update_layout(height=650, title="Curva de ROI según ocupación", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family=SYS_MONO, color="white"))
            st.plotly_chart(fig_d, use_container_width=True)

        # Sensibilidad 2
        st.subheader("Sensibilidad: Tarifa Airbnb vs ROI")
        st.markdown('<p class="info-box">Análisis del margen de seguridad sobre el precio por noche (intervalos de S/. 25) 💰.</p>', unsafe_allow_html=True)
        cs2_t, cs2_g = st.columns([1, 1.8], vertical_alignment="center")
        t_range = list(range(max(50, int(tarifa_base)-75), int(tarifa_base)+125, 25))
        roi_t = [((((t*ocupacion_act*0.85) - cuota - mantenimiento - (t*ocupacion_act*0.85*0.05))*12/inv_total)*100) for t in t_range]
        with cs2_t:
            st.table(pd.DataFrame({"Tarifa S/.": t_range, "ROI (%)": roi_t}).style.map(color_roi, subset=['ROI (%)']).format({"ROI (%)": "{:.2f}%"}))
        with cs2_g:
            fig_t = go.Figure(go.Scatter(x=t_range, y=roi_t, mode='lines+markers', line=dict(color='#3fb950', width=5)))
            fig_t.update_layout(height=650, title="Curva de ROI según tarifa", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family=SYS_MONO, color="white"))
            st.plotly_chart(fig_t, use_container_width=True)

        st.markdown('<div class="footer-tip">⚠️ <b>Recomendación operativa:</b> Si la ocupación desciende del 50%, aplique una estrategia de "Long Term Stay" (más de 28 días) para garantizar la cuota hipotecaria.</div>', unsafe_allow_html=True)

    # --------------------------------------------------------- PESTAÑA 4
    with tabs[3]:
        st.markdown('<div class="section-title">Comparativa tradicional vs airbnb 🔄</div>', unsafe_allow_html=True)
        st.markdown('<p class="info-box">Diferencial de flujo de caja libre entre el modelo de rentas cortas y el alquiler residencial convencional ⚖️.</p>', unsafe_allow_html=True)
        
        ventaja_anual = (flujo_neto * 12) - utilidad_trad
        dif_roi = roi_airbnb - roi_trad
        
        cc = st.columns(4)
        with cc[0]: st.markdown(f'<div class="card-base bg-green"><div class="label-card">Excedente anual Airbnb 💰</div><div class="val-pos" style="color:white;">S/. {ventaja_anual:,.0f}</div></div>', unsafe_allow_html=True)
        with cc[1]: st.markdown(f'<div class="card-base bg-gray"><div class="label-card">ROI Airbnb 🏨</div><div class="val-pos" style="color:white;">{roi_airbnb:.1f}%</div></div>', unsafe_allow_html=True)
        with cc[2]: st.markdown(f'<div class="card-base bg-gray"><div class="label-card">ROI tradicional 🏠</div><div class="val-pos" style="color:white;">{roi_trad:.1f}%</div></div>', unsafe_allow_html=True)
        with cc[3]: st.markdown(f'<div class="card-base bg-indigo"><div class="label-card">Diferencial de ROI 🚀</div><div class="val-pos" style="color:white;">{dif_roi:+.1f}%</div></div>', unsafe_allow_html=True)
        
        st.write("---")
        st.markdown('<p class="info-box"><b>Interpretación del gráfico:</b> Las barras muestran la utilidad neta líquida anualizada. El modelo Airbnb ofrece una mayor capitalización rápida a cambio de una mayor gestión operativa 📊.</p>', unsafe_allow_html=True)
        
        labels = ['MODELO AIRBNB', 'RENTA TRADICIONAL']
        vals = [flujo_neto*12, utilidad_trad]
        fig_c = go.Figure([go.Bar(
            x=labels, y=vals, 
            marker_color=['#3fb950' if v > 0 else '#f85149' for v in vals],
            text=[f'S/. {v:,.0f}' for v in vals],
            textposition='inside', insidetextanchor='middle',
            textfont=dict(size=28, color='white', weight='bold', family=SYS_MONO)
        )])
        fig_c.update_layout(title="Utilidad neta líquida por modelo", height=600, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family=SYS_SANS, color="white"))
        st.plotly_chart(fig_c, use_container_width=True)
        
        st.markdown('<p class="info-box" style="text-align:center;"><b>Relación de variables:</b> Mientras que Airbnb maximiza el ROI, conlleva gastos de limpieza, lavandería y gestión de anuncios. La renta tradicional es pasiva pero su tiempo de recuperación patrimonial es mucho más lento.</p>', unsafe_allow_html=True)

        st.markdown('<div class="footer-tip">🏁 <b>Dictamen final:</b> El modelo Airbnb es superior en flujo de caja y rentabilidad, ideal para perfiles que buscan acelerar la amortización de su crédito.</div>', unsafe_allow_html=True)

# =========================================================
# MOTOR DE PDF (HIGH DENSITY STRATEGIC REPORT)
# =========================================================
def generate_master_pdf(d):
    pdf = FPDF()
    pdf.add_page()
    # Header Dark
    pdf.set_fill_color(13, 17, 23); pdf.rect(0, 0, 210, 65, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_font("Helvetica", 'B', 18)
    pdf.cell(0, 25, "AUDITORIA TECNICA INMOBILIARIA JM", ln=True, align='C')
    pdf.set_font("Helvetica", '', 10); pdf.cell(0, 5, "ANALISIS POR: ING. JANCARLO MENDOZA - EXPERTO INTEGRAL", ln=True, align='C')
    pdf.cell(0, 5, f"LIMA, PERU | EMISION: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align='C')
    
    pdf.ln(35); pdf.set_text_color(0, 0, 0)

    # Bloque 1: Inversión
    pdf.set_font("Helvetica", 'B', 12); pdf.cell(0, 10, "1. DESGLOSE DE CAPITAL E INVERSION INICIAL", ln=True)
    pdf.set_font("Helvetica", '', 9)
    pdf.multi_cell(0, 5, "Se detalla la estructura de capital necesaria para la adquisicion. Se ha considerado una cuota inicial del 20% sobre el valor comercial de la unidad mas un presupuesto optimizado para equipamiento y diseño interior enfocado en rentas cortas.")
    pdf.ln(2); rows = [["ITEM", "VALOR (S/.)"], ["Precio Venta Activo", f"{d['val']:,.0f}"], ["Capital Propio (Equity)", f"{d['ini']:,.0f}"], ["Presupuesto Amoblado", f"{d['inv_a']:,.0f}"], ["DESEMBOLSO TOTAL", f"{d['inv_t']:,.0f}"]]
    for r in rows:
        pdf.cell(100, 7, r[0], 1); pdf.cell(90, 7, r[1], 1, ln=True, align='R')

    # Bloque 2: Operatividad
    pdf.ln(8); pdf.set_font("Helvetica", 'B', 12); pdf.cell(0, 10, "2. ANALISIS DE FLUJO Y RENTABILIDAD ANUAL", ln=True)
    pdf.set_font("Helvetica", '', 9)
    pdf.multi_cell(0, 5, "Analisis de flujos liquidos tras deducir el servicio de la deuda (Capital + Interes), mantenimiento del edificio, arbitrios, servicios e impuesto cedular de primera categoria (5% sobre el ingreso bruto).")
    pdf.ln(2)
    pdf.cell(0, 7, f"- ROI Anualizado Modelo Airbnb: {d['roi']:.2f}%", ln=True)
    pdf.cell(0, 7, f"- Flujo Neto Mensual (Liquidez Libre): S/. {d['flujo']:,.2f}", ln=True)
    pdf.cell(0, 7, f"- Punto de Equilibrio (Recuperacion): {d['pb']:.1f} años", ln=True)

    # Bloque 3: Plusvalía
    pdf.ln(8); pdf.set_font("Helvetica", 'B', 12); pdf.cell(0, 10, "3. CRECIMIENTO PATRIMONIAL Y PLUSVALIA", ln=True)
    pdf.set_font("Helvetica", '', 9)
    pdf.multi_cell(0, 5, "La plusvalia representa el crecimiento pasivo de su riqueza. En distritos de alta demanda, la revalorizacion compensa el costo financiero del credito hipotecario, permitiendo generar equity real desde el primer año.")

    # Bloque 4: Recomendaciones
    pdf.ln(8); pdf.set_font("Helvetica", 'B', 12); pdf.cell(0, 10, "4. RECOMENDACIONES ESTRATEGICAS", ln=True)
    pdf.set_font("Helvetica", '', 9)
    pdf.multi_cell(0, 5, "- OPTIMIZACION: Aplique precios dinamicos segun temporada para aumentar el ROI en un 12% adicional.\n- FISCALIDAD: Declare mensualmente sus impuestos para evitar contingencias con la autoridad tributaria local.\n- GESTION: Automatice el acceso con cerraduras inteligentes para reducir costos de personal y mejorar el ranking de plataforma.")

    pdf.ln(10); pdf.set_font("Helvetica", 'I', 8)
    pdf.multi_cell(0, 4, "AVISO: Este reporte es un analisis tecnico basado en proyecciones actuales de mercado. Jancarlo Mendoza no garantiza rentabilidades futuras ante cambios en la legislacion o fluctuaciones economicas externas.")

    return pdf.output(dest='S').encode('latin-1')

if st.session_state.authenticated:
    st.write("---")
    if st.button("📥 GENERAR AUDITORIA TECNICA COMPLETA (PDF)"):
        pdf_bytes = generate_master_pdf({
            "val": val_depa, "ini": inicial, "inv_a": inv_amoblado, "inv_t": inv_total,
            "roi": roi_airbnb, "flujo": flujo_neto, "pb": rec
        })
        st.download_button("Descargar Informe Técnico", data=pdf_bytes, file_name=f"Auditoria_Inmobiliaria_JM.pdf")
