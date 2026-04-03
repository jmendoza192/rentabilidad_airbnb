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

# Definición estricta de fuentes de sistema (No Roboto/WebFonts)
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
        
        /* 2. Monospace para Datos, Tablas y Porcentajes */
        .stTable, [data-testid="stTable"], code, .val-pos, .val-neg, .mono-font, .stMetric, .stDataFrame {{
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
            font-family: {SYS_SANS} !important;
        }}

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
        val_depa = st.number_input("Precio de venta (S/.) 🏠", value=380000)
        inv_amoblado = st.number_input("Inversión amoblado (S/.) 🛋️", value=45000)
        st.write("---")
        tcea = st.number_input("Tcea bancaria (%) 🏦", value=10.5)
        plazo_años = st.selectbox("Plazo (Años) 🗓️", [10, 15, 20, 25], index=2)
        st.write("---")
        tarifa_base = st.number_input("Tarifa por noche (S/.) 💰", value=280)
        ocupacion_act = st.selectbox("Días ocupados al mes 🌙", list(range(1, 31)), index=19)
        st.write("---")
        renta_trad = st.number_input("Renta tradicional (S/.) 🏠", value=2500)

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
        st.markdown('<p class="info-box">Análisis del capital propio necesario y la liquidez operativa inicial 🏛️.</p>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="card-base bg-blue"><div class="label-card">Cuota inicial 🏢</div><div class="val-pos">S/. {inicial:,.0f}</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="card-base bg-blue"><div class="label-card">Inversión amoblado 🛋️</div><div class="val-pos">S/. {inv_amoblado:,.0f}</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="card-base bg-gray"><div class="label-card">Desembolso total 💎</div><div class="val-pos">S/. {inv_total:,.0f}</div></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">Análisis operativo mensual 💸</div>', unsafe_allow_html=True)
        st.markdown('<p class="info-box">Flujo de caja libre después de cubrir deuda, costos fijos e impuestos 🧾.</p>', unsafe_allow_html=True)
        c4, c5, c6, c7 = st.columns(4)
        with c4: st.markdown(f'<div class="card-base bg-gray"><div class="label-card">Ventas brutas 🏨</div><div class="val-pos">S/. {ingreso_bruto:,.0f}</div></div>', unsafe_allow_html=True)
        with c5: st.markdown(f'<div class="card-base bg-gray"><div class="label-card">Hipotecario 🏦</div><div class="val-neg">S/. -{cuota:,.0f}</div></div>', unsafe_allow_html=True)
        with c6: st.markdown(f'<div class="card-base bg-gray"><div class="label-card">Gastos y tributos 🧾</div><div class="val-neg">S/. -{gastos_op:,.0f}</div></div>', unsafe_allow_html=True)
        with c7: st.markdown(f'<div class="card-base bg-green"><div class="label-card">Flujo neto 💰</div><div class="val-pos">S/. {flujo_neto:,.0f}</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">Métricas comparativas de rendimiento 📈</div>', unsafe_allow_html=True)
        cr1, cr2 = st.columns([1, 1.2])
        with cr1:
            st.markdown(f'<div class="card-base bg-light-green"><div class="label-card">ROI AIRBNB 🚀</div><div class="val-pos" style="color:#ffffff;">{roi_airbnb:.2f}%</div></div>', unsafe_allow_html=True)
        with cr2:
            st.table(pd.DataFrame({
                "Alternativa de inversión": ["ROI AIRBNB", "S&P 500", "Factoring inmobiliario", "Plazo fijo local", "Fondos mutuos", "Bono soberano"],
                "Retorno esperado (%)": [f"{roi_airbnb:.1f}%", "10.0%", "13.2%", "7.5%", "9.0%", "5.6%"]
            }))

        st.write("---")
        años_pb = 25; meses = np.arange(0, años_pb*12+1); f_acum = [-inv_total]; rec = 0
        for m in meses[1:]:
            f_acum.append(f_acum[-1] + (flujo_neto if m <= plazo_años*12 else ingreso_bruto-gastos_op))
            if rec == 0 and f_acum[-1] >= 0: rec = m/12
        
        cp1, cp2 = st.columns([1, 1.4])
        with cp1:
            st.markdown(f'<div class="card-base bg-indigo"><div class="label-card">Tiempo de recuperación (Payback) ⏳</div><div class="val-pos" style="color:white; font-size:2.4rem;">{rec:.1f} Años</div></div>', unsafe_allow_html=True)
            st.markdown('<p class="info-box"><b>Nota:</b> El payback mide cuántos años tomará recuperar el capital líquido invertido mediante los flujos mensuales 🏛️.</p>', unsafe_allow_html=True)
        with cp2:
            fig_pb = go.Figure()
            fig_pb.add_trace(go.Scatter(x=meses/12, y=[min(0, x) for x in f_acum], fill='tozeroy', fillcolor='rgba(248, 81, 73, 0.4)', line=dict(width=0), showlegend=False))
            fig_pb.add_trace(go.Scatter(x=meses/12, y=[max(0, x) for x in f_acum], fill='tozeroy', fillcolor='rgba(63, 185, 80, 0.4)', line=dict(width=0), showlegend=False))
            fig_pb.add_trace(go.Scatter(x=meses/12, y=f_acum, line=dict(color='#ffffff', width=3), name="Balance"))
            fig_pb.update_layout(title="Curva de recuperación (Rojo: Déficit / Verde: Retorno)", height=350, margin=dict(t=40, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family=SYS_MONO, color="white"))
            st.plotly_chart(fig_pb, use_container_width=True)

        st.markdown('<div class="footer-tip">💡 <b>Recomendación:</b> Reduzca la vacancia mediante una estrategia dinámica de precios para acelerar el payback en un 15%.</div>', unsafe_allow_html=True)

    # --------------------------------------------------------- PESTAÑA 2
    with tabs[1]:
        st.markdown('<div class="section-title">Evolución del patrimonio y plusvalía 🏔️</div>', unsafe_allow_html=True)
        st.markdown('<p class="info-box">Análisis de la valorización del inmueble y crecimiento de su patrimonio neto (Equity) en el tiempo 📈.</p>', unsafe_allow_html=True)
        p_slider = st.slider("Expectativa de plusvalía anual (%)", 0.0, 10.0, 4.5)
        
        c_p = st.columns(4)
        for i, a in enumerate([5, 10, 15, 20]):
            g = (val_depa * (1 + p_slider/100)**a) - val_depa
            with c_p[i]: 
                st.markdown(f'<div class="card-base bg-blue"><div class="label-card">Plusvalía {a} años 📈</div><div class="val-pos" style="color:white; font-size:1.5rem;">S/. {g:,.0f}</div></div>', unsafe_allow_html=True)
                st.caption(f"Valorización bruta proyectada.")
        
        st.markdown('<div class="section-title">Crecimiento del equity real 📊</div>', unsafe_allow_html=True)
        st.markdown('<p class="info-box">Este gráfico muestra su riqueza neta: Valor de mercado menos deuda pendiente 📊.</p>', unsafe_allow_html=True)
        años = np.arange(0, 26); v_mkt = [val_depa * (1+p_slider/100)**a for a in años]
        eq = [v - (prestamo * (1 - a/plazo_años) if a < plazo_años else 0) for a, v in zip(años, v_mkt)]
        
        fig_p = go.Figure()
        fig_p.add_trace(go.Bar(x=años, y=v_mkt, name="Valor mercado", marker_color='#21262d'))
        fig_p.add_trace(go.Scatter(x=años, y=eq, name="Patrimonio real (Equity)", line=dict(color='#58a6ff', width=4)))
        fig_p.update_layout(title="Valorización del activo vs Saldo deudor bancario", height=450, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family=SYS_MONO, color="white"))
        st.plotly_chart(fig_p, use_container_width=True)

        st.markdown('<div class="footer-tip">📊 <b>Tip operativo:</b> La plusvalía en distritos como Miraflores o San Isidro suele ser un 2% superior al promedio de Lima.</div>', unsafe_allow_html=True)

    # --------------------------------------------------------- PESTAÑA 3
    with tabs[2]:
        st.markdown('<div class="section-title">Matrices de sensibilidad operativa ⚖️</div>', unsafe_allow_html=True)
        st.markdown('<p class="info-box">Determinación de escenarios críticos y márgenes de seguridad para el retorno de la inversión 🚦.</p>', unsafe_allow_html=True)
        
        def color_roi(val):
            c = '#f85149' if val < 5 else '#d29922' if val < 10 else '#3fb950'
            return f'background-color: {c}; color: #000; font-weight: bold; font-family: {SYS_MONO};'

        # Sensibilidad 1: Días
        st.subheader("Sensibilidad por ocupación mensual")
        st.markdown('<p class="info-box">Muestra el ROI variando los días de reserva (Intervalos de 5 días) 🌙.</p>', unsafe_allow_html=True)
        cs1_t, cs1_g = st.columns([1, 1.8], vertical_alignment="center")
        d_range = list(range(5, 35, 5))
        roi_d = [((((tarifa_base*d*0.85) - cuota - mantenimiento - (tarifa_base*d*0.85*0.05))*12/inv_total)*100) for d in d_range]
        with cs1_t:
            st.table(pd.DataFrame({"Días/Mes": d_range, "ROI (%)": roi_d}).style.map(color_roi, subset=['ROI (%)']).format({"ROI (%)": "{:.2f}%"}))
        with cs1_g:
            fig_d = go.Figure(go.Scatter(x=d_range, y=roi_d, mode='lines+markers', line=dict(color='#58a6ff', width=5)))
            fig_d.update_layout(height=600, title="Correlación ocupación vs ROI", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family=SYS_MONO, color="white"))
            st.plotly_chart(fig_d, use_container_width=True)

        # Sensibilidad 2: Tarifa
        st.subheader("Sensibilidad por tarifa nocturna")
        st.markdown('<p class="info-box">Muestra el ROI variando el precio por noche (Intervalos de S/. 25) 💰.</p>', unsafe_allow_html=True)
        cs2_t, cs2_g = st.columns([1, 1.8], vertical_alignment="center")
        t_range = list(range(max(50, int(tarifa_base)-75), int(tarifa_base)+125, 25))
        roi_t = [((((t*ocupacion_act*0.85) - cuota - mantenimiento - (t*ocupacion_act*0.85*0.05))*12/inv_total)*100) for t in t_range]
        with cs2_t:
            st.table(pd.DataFrame({"Tarifa S/.": t_range, "ROI (%)": roi_t}).style.map(color_roi, subset=['ROI (%)']).format({"ROI (%)": "{:.2f}%"}))
        with cs2_g:
            fig_t = go.Figure(go.Scatter(x=t_range, y=roi_t, mode='lines+markers', line=dict(color='#3fb950', width=5)))
            fig_t.update_layout(height=600, title="Correlación tarifa vs ROI", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family=SYS_MONO, color="white"))
            st.plotly_chart(fig_t, use_container_width=True)

        st.markdown('<div class="footer-tip">⚠️ <b>Advertencia:</b> Un ROI inferior al 6% sugiere que el modelo tradicional podría ser menos riesgoso en ese escenario particular.</div>', unsafe_allow_html=True)

    # --------------------------------------------------------- PESTAÑA 4
    with tabs[3]:
        st.markdown('<div class="section-title">Veredicto: comparativa tradicional vs airbnb 🔄</div>', unsafe_allow_html=True)
        st.markdown('<p class="info-box">Evaluación final de flujos excedentes y rentabilidad comparada entre modelos de gestión ⚖️.</p>', unsafe_allow_html=True)
        
        ventaja_anual = (flujo_neto * 12) - utilidad_trad
        dif_roi = roi_airbnb - roi_trad
        
        cc = st.columns(4)
        with cc[0]: st.markdown(f'<div class="card-base bg-green"><div class="label-card">Excedente anual Airbnb 🏆</div><div class="val-pos" style="color:white;">S/. {ventaja_anual:,.0f}</div></div>', unsafe_allow_html=True)
        with cc[1]: st.markdown(f'<div class="card-base bg-gray"><div class="label-card">ROI Airbnb 🏨</div><div class="val-pos" style="color:white;">{roi_airbnb:.1f}%</div></div>', unsafe_allow_html=True)
        with cc[2]: st.markdown(f'<div class="card-base bg-gray"><div class="label-card">ROI tradicional 🏠</div><div class="val-pos" style="color:white;">{roi_trad:.1f}%</div></div>', unsafe_allow_html=True)
        with cc[3]: st.markdown(f'<div class="card-base bg-indigo"><div class="label-card">Diferencial de retorno 🚀</div><div class="val-pos" style="color:white;">{dif_roi:+.1f}%</div></div>', unsafe_allow_html=True)
        
        st.write("---")
        st.markdown('<p class="info-box"><b>Gráfico de utilidad neta:</b> Las barras muestran el flujo de caja anual líquido (después de pagar hipoteca y costos). Airbnb suele duplicar la rentabilidad del alquiler convencional 📊.</p>', unsafe_allow_html=True)
        
        labels = ['<b>MODELO AIRBNB</b>', '<b>ALQUILER TRADICIONAL</b>']
        vals = [flujo_neto*12, utilidad_trad]
        fig_c = go.Figure([go.Bar(
            x=labels, y=vals, 
            marker_color=['#3fb950' if v > 0 else '#f85149' for v in vals],
            text=[f'S/. {v:,.0f}' for v in vals],
            textposition='inside', insidetextanchor='middle',
            textfont=dict(size=26, color='white', weight='bold', family=SYS_MONO)
        )])
        fig_c.update_layout(title="Utilidad líquida anualizada por modelo (Cash Flow)", height=550, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family=SYS_SANS, color="white"))
        st.plotly_chart(fig_c, use_container_width=True)
        
        st.markdown('<p class="info-box" style="text-align:center;"><b>Análisis de variables:</b> La rentabilidad superior de Airbnb justifica el riesgo operativo y los costos de mantenimiento más intensos. El modelo tradicional es puramente pasivo pero sacrifica el crecimiento del capital en el corto plazo.</p>', unsafe_allow_html=True)

        st.markdown('<div class="footer-tip">🏁 <b>Dictamen:</b> El modelo Airbnb es la opción ganadora para acelerar la creación de patrimonio bajo este perfil de activo.</div>', unsafe_allow_html=True)

# =========================================================
# MOTOR DE PDF (HIGH DENSITY INDUSTRIAL REPORT)
# =========================================================
def generate_master_pdf(d):
    pdf = FPDF()
    pdf.add_page()
    # Header Dark
    pdf.set_fill_color(13, 17, 23); pdf.rect(0, 0, 210, 65, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_font("Helvetica", 'B', 18)
    pdf.cell(0, 25, "AUDITORIA DE INVERSION INMOBILIARIA PROFESIONAL", ln=True, align='C')
    pdf.set_font("Helvetica", '', 10); pdf.cell(0, 5, "CONSULTOR: ING. JANCARLO MENDOZA | LIMA, PERU", ln=True, align='C')
    pdf.cell(0, 5, f"EMITIDO EL: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align='C')
    
    pdf.ln(35); pdf.set_text_color(0, 0, 0)

    # Sección 1: Estructura Financiera
    pdf.set_font("Helvetica", 'B', 14); pdf.cell(0, 10, "1. Estructura de capital e inversion inicial", ln=True)
    pdf.set_font("Helvetica", '', 10)
    pdf.multi_cell(0, 5, "Se detalla el capital liquido necesario para la ejecucion del proyecto. La inversion total considera el desembolso por cuota inicial bancaria (20%) y el presupuesto de adecuacion y amoblado completo para operacion inmediata.")
    pdf.ln(3)
    rows = [["CONCEPTO TECNICO", "MONTO (S/.)"], ["Precio de venta de la unidad", f"{d['val']:,.0f}"], ["Cuota inicial (Equity propio)", f"{d['ini']:,.0f}"], ["Capex de amoblado y diseño", f"{d['inv_a']:,.0f}"], ["TOTAL CASH-OUT REQUERIDO", f"{d['inv_t']:,.0f}"]]
    for r in rows:
        pdf.cell(110, 8, r[0], 1); pdf.cell(80, 8, r[1], 1, ln=True, align='R')

    # Sección 2: Operatividad y Retorno
    pdf.ln(10); pdf.set_font("Helvetica", 'B', 14); pdf.cell(0, 10, "2. Analisis de rentabilidad operativa (ROI)", ln=True)
    pdf.set_font("Helvetica", '', 10)
    pdf.multi_cell(0, 5, "Analisis de flujos proyectados basado en la tarifa promedio de mercado y tasas hipotecarias vigentes. Se deduce el servicio de la deuda, el impuesto a la renta de primera categoria y los gastos de mantenimiento del edificio.")
    pdf.ln(3)
    pdf.cell(0, 8, f"- ROI Anualizado Proyectado: {d['roi']:.2f}%", ln=True)
    pdf.cell(0, 8, f"- Flujo de caja neto mensual (Liquidez): S/. {d['flujo']:,.2f}", ln=True)
    pdf.cell(0, 8, f"- Tiempo estimado de recuperacion (Payback): {d['pb']:.1f} años", ln=True)

    # Sección 3: Veredicto
    pdf.ln(10); pdf.set_font("Helvetica", 'B', 14); pdf.cell(0, 10, "3. Veredicto y recomendaciones tecnicas", ln=True)
    pdf.set_font("Helvetica", '', 10)
    pdf.multi_cell(0, 5, f"Al comparar con el alquiler tradicional, el modelo Airbnb genera un excedente de S/. {d['exc']:,.0f} al año. Esto representa una ventaja competitiva del {d['dif']:.1f}% en rentabilidad. Se recomienda priorizar la automatizacion del check-in para reducir costos operativos.")
    
    pdf.ln(15); pdf.set_font("Helvetica", 'I', 8)
    pdf.multi_cell(0, 4, "AVISO LEGAL: Este reporte es una herramienta de analisis financiero. Jancarlo Mendoza no se responsabiliza por cambios en la legislacion tributaria o fluctuaciones externas en la demanda de plataformas de terceros.")

    return pdf.output(dest='S').encode('latin-1')

if st.session_state.authenticated:
    st.write("---")
    if st.button("📥 GENERAR INFORME DE AUDITORIA COMPLETO (PDF)"):
        pdf_bytes = generate_master_pdf({
            "val": val_depa, "ini": inicial, "inv_a": inv_amoblado, "inv_t": inv_total,
            "roi": roi_airbnb, "flujo": flujo_neto, "pb": rec, "exc": ventaja_anual, "dif": dif_roi
        })
        st.download_button("Descargar Informe Técnico", data=pdf_bytes, file_name=f"Auditoria_Inmobiliaria_JM.pdf")
