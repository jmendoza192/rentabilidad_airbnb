import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime
import random
import string

# =========================================================
# 0. CONFIGURACIÓN Y ESTÉTICA SANS-SERIF DE SISTEMA
# =========================================================
try:
    st.set_page_config(page_title="Auditoría JM", layout="wide")
except:
    pass

# Fuente de sistema pura (Elimina Roboto/Webfonts)
SYS_SANS = '-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif'

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "assessment_finished" not in st.session_state:
    st.session_state.assessment_finished = False

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
    st.markdown(f"""
        <style>
        /* Reset Global a Sans-Serif de Sistema */
        html, body, [class*="css"], .stMarkdown, p, div, span, label, button, .stSelectbox, .stNumberInput, .stTable, .stDataFrame {{
            font-family: {SYS_SANS} !important;
            color: #ffffff;
        }}
        
        /* Eliminación de botones +/- */
        button.step-up, button.step-down {{ display: none !important; }}
        input[type=number]::-webkit-inner-spin-button, 
        input[type=number]::-webkit-outer-spin-button {{ -webkit-appearance: none; margin: 0; }}
        input[type=number] {{ -moz-appearance: textfield; }}

        .main {{ background-color: #0d1117; }}
        
        /* Títulos tipo oración */
        .section-title {{ 
            color: #ffffff; font-size: 1.6rem; font-weight: 600; 
            padding: 10px 0; border-bottom: 1px solid #30363d; margin: 25px 0 15px 0;
            text-transform: lowercase;
        }}
        .section-title::first-letter {{ text-transform: uppercase; }}

        /* Tarjetas con letras blancas y colores variados */
        .card-base {{
            border: 1px solid #30363d; border-radius: 8px; padding: 20px;
            text-align: center; margin-bottom: 15px; color: #ffffff !important;
        }}
        .bg-blue {{ background-color: #051e3e; }}
        .bg-green {{ background-color: #062d1a; }}
        .bg-red {{ background-color: #3e0a0a; border: 1px solid #f85149; }}
        .bg-gray {{ background-color: #161b22; }}
        .bg-gold {{ background-color: #3e2b05; }}
        .bg-indigo {{ background-color: #1e1b4b; }}
        .bg-cyan {{ background-color: #003d3d; border: 1px solid #58a6ff; }}

        /* Estilos Pestaña 1 (Azul/Rojo) */
        .val-pos {{ color: #58a6ff; font-size: 1.8rem; font-weight: 700; }}
        .val-neg {{ color: #f85149; font-size: 1.8rem; font-weight: 700; }}
        .label-card {{ font-size: 0.85rem; font-weight: 500; margin-bottom: 5px; opacity: 0.9; }}

        .info-box {{ font-size: 0.92rem; color: #8b949e; line-height: 1.6; margin-bottom: 20px; }}
        .footer-tip {{
            background-color: #0d1117; color: #ffffff; padding: 25px;
            border: 1px solid #30363d; border-left: 5px solid #58a6ff; margin-top: 40px;
        }}
        </style>
        """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("Entradas de auditoría ⚙️")
        val_depa = st.number_input("Precio de venta (S/.) 🏠", value=465000)
        inv_amoblado = st.number_input("Inversión amoblado (S/.) 🛋️", value=52000)
        st.write("---")
        tcea = st.number_input("Tcea bancaria (%) 🏦", value=10.1)
        plazo_años = st.selectbox("Plazo hipotecario (Años) 🗓️", [10, 15, 20, 25], index=2)
        st.write("---")
        tarifa_base = st.number_input("Tarifa noche (S/.) 💰", value=360)
        ocupacion_act = st.selectbox("Días ocupados al mes 🌙", list(range(1, 31)), index=19)
        st.write("---")
        renta_trad = st.number_input("Renta tradicional (S/.) 🏠", value=3100)

    # LÓGICA CORE
    inicial = val_depa * 0.20
    inv_total = inicial + inv_amoblado
    prestamo = val_depa - inicial
    tem = (1 + tcea/100)**(1/12) - 1
    cuota = prestamo * (tem * (1 + tem)**(plazo_años*12)) / ((1 + tem)**(plazo_años*12) - 1)
    mantenimiento = (val_depa * 0.035) / 12
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
        st.markdown('<p class="info-box">Determinación del capital propio necesario para la compra y el equipamiento inicial del activo 🏢.</p>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="card-base bg-cyan"><div class="label-card">Cuota inicial 🏢</div><div class="val-pos">S/. {inicial:,.0f}</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="card-base bg-cyan"><div class="label-card">Inversión amoblado 🛋️</div><div class="val-pos">S/. {inv_amoblado:,.0f}</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="card-base bg-gray"><div class="label-card">Desembolso total 💎</div><div class="val-pos">S/. {inv_total:,.0f}</div></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">Análisis operativo mensual 💸</div>', unsafe_allow_html=True)
        st.markdown('<p class="info-box">Flujo de caja libre después de obligaciones bancarias, tributarias y operativas 🧾.</p>', unsafe_allow_html=True)
        c4, c5, c6, c7 = st.columns(4)
        with c4: st.markdown(f'<div class="card-base bg-gray"><div class="label-card">Ingreso bruto 🏨</div><div class="val-pos">S/. {ingreso_bruto:,.0f}</div></div>', unsafe_allow_html=True)
        with c5: st.markdown(f'<div class="card-base bg-red"><div class="label-card">Pago banco 🏦</div><div class="val-neg">S/. -{cuota:,.0f}</div></div>', unsafe_allow_html=True)
        with c6: st.markdown(f'<div class="card-base bg-red"><div class="label-card">Gastos operativos 🧾</div><div class="val-neg">S/. -{gastos_op:,.0f}</div></div>', unsafe_allow_html=True)
        with c7: st.markdown(f'<div class="card-base bg-green"><div class="label-card">Flujo neto 💰</div><div class="val-pos">S/. {flujo_neto:,.0f}</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">Rentabilidad comparativa ROI AIRBNB 📈</div>', unsafe_allow_html=True)
        cr1, cr2 = st.columns([1, 1.2])
        with cr1:
            st.markdown(f'<div class="card-base bg-indigo"><div class="label-card">ROI AIRBNB 🚀</div><div class="val-pos" style="color:white;">{roi_airbnb:.2f}%</div></div>', unsafe_allow_html=True)
        with cr2:
            st.markdown('<div style="background-color:#1b4332; padding:15px; border-radius:8px; border:1px solid #3fb950;">', unsafe_allow_html=True)
            st.table(pd.DataFrame({
                "Alternativa": ["ROI AIRBNB", "S&P 500", "Factoring Local", "Cajas Municipales", "Bonos Soberanos", "Depósito Plazo Fijo"],
                "Retorno %": [f"{roi_airbnb:.1f}%", "10.0%", "12.0%", "8.5%", "6.0%", "7.5%"]
            }))
            st.markdown('</div>', unsafe_allow_html=True)

        st.write("---")
        años_pb = 25; meses = np.arange(0, años_pb*12+1); f_acum = [-inv_total]; rec = 0
        for m in meses[1:]:
            f_acum.append(f_acum[-1] + (flujo_neto if m <= plazo_años*12 else ingreso_bruto-gastos_op))
            if rec == 0 and f_acum[-1] >= 0: rec = m/12
        
        cp1, cp2 = st.columns([0.8, 1.2])
        with cp1:
            st.markdown(f'<div class="card-base bg-indigo"><div class="label-card">Tiempo de recuperación (Payback) ⏳</div><div class="val-pos" style="color:white; font-size:2.8rem;">{rec:.1f} Años</div></div>', unsafe_allow_html=True)
            st.markdown('<p class="info-box"><b>Nota:</b> Periodo estimado para que la utilidad neta acumulada reembolse el 100% del desembolso de capital inicial 🏛️.</p>', unsafe_allow_html=True)
        with cp2:
            fig_pb = go.Figure()
            fig_pb.add_trace(go.Scatter(x=meses/12, y=[min(0, x) for x in f_acum], fill='tozeroy', fillcolor='rgba(248, 81, 73, 0.4)', line=dict(width=0), showlegend=False))
            fig_pb.add_trace(go.Scatter(x=meses/12, y=[max(0, x) for x in f_acum], fill='tozeroy', fillcolor='rgba(63, 185, 80, 0.4)', line=dict(width=0), showlegend=False))
            fig_pb.add_trace(go.Scatter(x=meses/12, y=f_acum, line=dict(color='#ffffff', width=3), name="Caja acumulada"))
            fig_pb.update_layout(title="Curva de balance neto acumulado", height=380, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family=SYS_SANS, color="white"))
            st.plotly_chart(fig_pb, use_container_width=True)

        st.markdown('<div class="footer-tip">💡 <b>Recomendación operativa:</b> Un payback menor a 12 años en bienes raíces con apalancamiento indica una inversión de alta eficiencia financiera 📊.</div>', unsafe_allow_html=True)

    # --------------------------------------------------------- PESTAÑA 2
    with tabs[1]:
        st.markdown('<div class="section-title">Evolución del patrimonio y plusvalía 🏔️</div>', unsafe_allow_html=True)
        st.markdown('<p class="info-box">Estimación de la revalorización del activo basada en la maduración del entorno comercial local 📈.</p>', unsafe_allow_html=True)
        p_slider = st.slider("Expectativa de plusvalía anual (%)", 0.0, 10.0, 4.0)
        
        c_p = st.columns(4)
        for i, a in enumerate([5, 10, 15, 20]):
            g = (val_depa * (1 + p_slider/100)**a) - val_depa
            with c_p[i]: 
                st.markdown(f'<div class="card-base bg-blue"><div class="label-card">Plusvalía {a} años 📈</div><div class="val-pos" style="color:white; font-size:1.5rem; white-space:nowrap;">S/. {g:,.0f}</div></div>', unsafe_allow_html=True)
        
        st.markdown('<p class="info-box"><b>Nota informativa:</b> Estas cifras representan la ganancia de capital bruta estimada por el incremento del valor de mercado 🏔️.</p>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">Crecimiento del activo total vs deuda 📊</div>', unsafe_allow_html=True)
        años = np.arange(0, 26); v_mkt = [val_depa * (1+p_slider/100)**a for a in años]
        eq = [v - (prestamo * (1 - a/plazo_años) if a < plazo_años else 0) for a, v in zip(años, v_mkt)]
        
        fig_p = go.Figure()
        fig_p.add_trace(go.Bar(x=años, y=v_mkt, name="Valor Mercado", marker_color='#21262d'))
        fig_p.add_trace(go.Scatter(x=años, y=eq, name="Equity Real", line=dict(color='#58a6ff', width=4)))
        fig_p.update_layout(title="Valorización acumulada vs Saldo hipotecario", height=450, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family=SYS_SANS, color="white"))
        st.plotly_chart(fig_p, use_container_width=True)

        st.markdown('<div class="footer-tip">📊 <b>Tip financiero:</b> A medida que la deuda disminuye, su patrimonio líquido (Equity) crece de forma acelerada, permitiendo refinanciamientos o nuevas inversiones.</div>', unsafe_allow_html=True)

    # --------------------------------------------------------- PESTAÑA 3
    with tabs[2]:
        st.markdown('<div class="section-title">Matrices de sensibilidad financiera ⚖️</div>', unsafe_allow_html=True)
        st.markdown('<p class="info-box">Análisis detallado de la resiliencia del proyecto ante fluctuaciones críticas de ocupación y precio 🚦.</p>', unsafe_allow_html=True)
        
        def color_roi(val):
            c = '#f85149' if val < 5 else '#d29922' if val < 10 else '#3fb950'
            return f'background-color: {c}; color: #000; font-weight: bold;'

        # Sensibilidad 1
        st.subheader("Sensibilidad: Ocupación mensual")
        st.markdown('<p class="info-box">Impacto de la tasa de reserva en el retorno anual (Intervalos de 5 días) 🌙.</p>', unsafe_allow_html=True)
        cs1_t, cs1_g = st.columns([1, 1.8], vertical_alignment="center")
        d_range = list(range(5, 35, 5))
        roi_d = [((((tarifa_base*d*0.85) - cuota - mantenimiento - (tarifa_base*d*0.85*0.05))*12/inv_total)*100) for d in d_range]
        with cs1_t:
            st.table(pd.DataFrame({"Días/Mes": d_range, "ROI (%)": roi_d}).style.map(color_roi, subset=['ROI (%)']).format({"ROI (%)": "{:.2f}%"}))
        with cs1_g:
            fig_d = go.Figure(go.Scatter(x=d_range, y=roi_d, mode='lines+markers', line=dict(color='#58a6ff', width=5)))
            fig_d.update_layout(height=650, title="Curva de ROI según ocupación", xaxis_title="Días de reserva al mes", yaxis_title="ROI %", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family=SYS_SANS, color="white"))
            st.plotly_chart(fig_d, use_container_width=True)

        # Sensibilidad 2
        st.subheader("Sensibilidad: Tarifa Airbnb")
        st.markdown('<p class="info-box">Impacto del precio por noche en el retorno anual (Intervalos de S/. 25) 💰.</p>', unsafe_allow_html=True)
        cs2_t, cs2_g = st.columns([1, 1.8], vertical_alignment="center")
        t_range = list(range(max(50, int(tarifa_base)-75), int(tarifa_base)+125, 25))
        roi_t = [((((t*ocupacion_act*0.85) - cuota - mantenimiento - (t*ocupacion_act*0.85*0.05))*12/inv_total)*100) for t in t_range]
        with cs2_t:
            st.table(pd.DataFrame({"Tarifa S/.": t_range, "ROI (%)": roi_t}).style.map(color_roi, subset=['ROI (%)']).format({"ROI (%)": "{:.2f}%"}))
        with cs2_g:
            fig_t = go.Figure(go.Scatter(x=t_range, y=roi_t, mode='lines+markers', line=dict(color='#3fb950', width=5)))
            fig_t.update_layout(height=650, title="Curva de ROI según tarifa", xaxis_title="Precio por noche (S/.)", yaxis_title="ROI %", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family=SYS_SANS, color="white"))
            st.plotly_chart(fig_t, use_container_width=True)

        st.markdown('<div class="footer-tip">⚠️ <b>Recomendación operativa:</b> Si el mercado se vuelve agresivo, mantenga una ocupación mínima del 60% para garantizar la cobertura de la cuota bancaria 🚦.</div>', unsafe_allow_html=True)

    # --------------------------------------------------------- PESTAÑA 4
    with tabs[3]:
        st.markdown('<div class="section-title">Comparativa tradicional vs airbnb 🔄</div>', unsafe_allow_html=True)
        st.markdown('<p class="info-box">Evaluación del diferencial de flujos netos entre rentas cortas y alquiler de largo plazo ⚖️.</p>', unsafe_allow_html=True)
        
        ventaja_anual = (flujo_neto * 12) - utilidad_trad
        dif_roi = roi_airbnb - roi_trad
        
        cc = st.columns(4)
        with cc[0]: st.markdown(f'<div class="card-base bg-green"><div class="label-card">Excedente anual Airbnb 💰</div><div class="val-pos" style="color:white;">S/. {ventaja_anual:,.0f}</div></div>', unsafe_allow_html=True)
        with cc[1]: st.markdown(f'<div class="card-base bg-gray"><div class="label-card">ROI Airbnb 🏨</div><div class="val-pos" style="color:white;">{roi_airbnb:.1f}%</div></div>', unsafe_allow_html=True)
        with cc[2]: st.markdown(f'<div class="card-base bg-gray"><div class="label-card">ROI tradicional 🏠</div><div class="val-pos" style="color:white;">{roi_trad:.1f}%</div></div>', unsafe_allow_html=True)
        with cc[3]: st.markdown(f'<div class="card-base bg-indigo"><div class="label-card">Diferencia de ROIs 🚀</div><div class="val-pos" style="color:white;">{dif_roi:+.1f}%</div></div>', unsafe_allow_html=True)
        
        st.write("---")
        st.markdown('<p class="info-box"><b>Análisis visual:</b> El gráfico muestra la utilidad neta líquida anualizada. Se observa que el modelo Airbnb acelera drásticamente la capitalización anual 📊.</p>', unsafe_allow_html=True)
        
        labels = ['MODELO AIRBNB', 'MODELO TRADICIONAL']
        vals = [flujo_neto*12, utilidad_trad]
        fig_c = go.Figure([go.Bar(
            x=labels, y=vals, 
            marker_color=['#3fb950' if v > 0 else '#f85149' for v in vals],
            text=[f'S/. {v:,.0f}' for v in vals],
            textposition='inside', insidetextanchor='middle',
            textfont=dict(size=28, color='white', weight='bold', family=SYS_SANS)
        )])
        fig_c.update_layout(title="Utilidad neta anualizada (Caja libre)", height=550, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family=SYS_SANS, color="white"))
        st.plotly_chart(fig_c, use_container_width=True)
        
        st.markdown('<p class="info-box" style="text-align:center;"><b>Explicación de variables:</b> La brecha de rentabilidad justifica el tiempo de gestión operativa del modelo de rentas cortas frente al alquiler residencial convencional.</p>', unsafe_allow_html=True)

        st.markdown('<div class="footer-tip">🏁 <b>Dictamen final:</b> Airbnb es el modelo óptimo para inversores que buscan flujo de caja máximo e independencia financiera acelerada 🇵🇪.</div>', unsafe_allow_html=True)

# =========================================================
# LÓGICA DE EXPORTACIÓN Y CELEBRACIÓN
# =========================================================
if st.session_state.authenticated:
    st.write("---")
    if not st.session_state.assessment_finished:
        if st.button("✅ ASESORÍA TERMINADA"):
            st.balloons()
            st.session_state.assessment_finished = True
            st.rerun()
    else:
        # MOTOR DE PDF (HIGH DENSITY INDUSTRIAL)
        def generate_master_pdf(d):
            pdf = FPDF()
            pdf.add_page()
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            
            # Header Dark Industrial
            pdf.set_fill_color(13, 17, 23); pdf.rect(0, 0, 210, 60, 'F')
            pdf.set_text_color(255, 255, 255); pdf.set_font("Helvetica", 'B', 16)
            pdf.cell(0, 20, "AUDITORIA DE INVERSION INMOBILIARIA PROFESIONAL", ln=True, align='C')
            pdf.set_font("Helvetica", '', 9); pdf.cell(0, 5, "POR: ING. JANCARLO MENDOZA - EXPERTO INTEGRAL", ln=True, align='C')
            pdf.cell(0, 5, f"CODIGO: JM-{code} | LIMA, PERU | {datetime.now().strftime('%d/%m/%Y')}", ln=True, align='C')
            
            pdf.ln(35); pdf.set_text_color(0, 0, 0)

            # Bloque 1: Capital
            pdf.set_font("Helvetica", 'B', 12); pdf.cell(0, 10, "1. Estructura de capital e inversion inicial", ln=True)
            pdf.set_font("Helvetica", '', 9)
            pdf.multi_cell(0, 5, "Analisis del flujo de salida inicial. Incluye cuota inicial (20%) y presupuesto de amoblado diseñado para maximizar el ranking en plataformas digitales.")
            pdf.ln(2); rows = [["Detalle", "Monto (S/.)"], ["Precio de Compra", f"{d['val']:,.0f}"], ["Capital Propio (Cuota)", f"{d['ini']:,.0f}"], ["Inversion Amoblado", f"{d['inv_a']:,.0f}"], ["DESEMBOLSO TOTAL", f"{d['inv_t']:,.0f}"]]
            for r in rows:
                pdf.cell(90, 7, r[0], 1); pdf.cell(90, 7, r[1], 1, ln=True, align='R')

            # Bloque 2: Operatividad
            pdf.ln(8); pdf.set_font("Helvetica", 'B', 12); pdf.cell(0, 10, "2. Rentabilidad operativa mensual", ln=True)
            pdf.set_font("Helvetica", '', 9)
            pdf.multi_cell(0, 5, f"El proyecto arroja un ROI Anual del {d['roi']:.2f}% bajo el modelo Airbnb. El flujo de caja neto mensual es de S/. {d['flujo']:,.2f}, permitiendo recuperar el 100% del capital en {d['pb']:.1f} años.")

            # Bloque 3: Patrimonio
            pdf.ln(8); pdf.set_font("Helvetica", 'B', 12); pdf.cell(0, 10, "3. Crecimiento patrimonial (Plusvalia)", ln=True)
            pdf.set_font("Helvetica", '', 9)
            pdf.multi_cell(0, 5, "La valorización urbana proyectada genera una ganancia de capital masiva. El equity real del propietario crece exponencialmente conforme se amortiza la deuda hipotecaria.")

            # Bloque 4: Sensibilidad y Comparativa
            pdf.ln(8); pdf.set_font("Helvetica", 'B', 12); pdf.cell(0, 10, "4. Resiliencia y veredicto comparativo", ln=True)
            pdf.set_font("Helvetica", '', 9)
            pdf.multi_cell(0, 5, f"Airbnb genera un excedente de S/. {d['exc']:,.0f} anual frente al modelo tradicional. Las pruebas de sensibilidad confirman que el proyecto es solvente incluso ante caidas moderadas de ocupacion.")

            # Recomendaciones
            pdf.ln(8); pdf.set_font("Helvetica", 'B', 12); pdf.cell(0, 10, "5. Recomendaciones financieras JM", ln=True)
            pdf.set_font("Helvetica", '', 9)
            pdf.multi_cell(0, 5, "1. Invierta en fotografia profesional para elevar la ocupacion.\n2. Automatice check-ins con cerraduras inteligentes.\n3. Mantenga un fondo de emergencia de 3 meses de cuota hipotecaria.")

            # Aviso Legal
            pdf.ln(12); pdf.set_font("Helvetica", 'I', 7)
            pdf.multi_cell(0, 4, "AVISO IMPORTANTE: Este reporte es un modelo de estudio tecnico-financiero. Los resultados proyectados no garantizan la realidad futura ante cambios en las leyes peruanas, impuestos o fluctuaciones del mercado inmobiliario local.")

            return pdf.output(dest='S').encode('latin-1'), f"Auditoria_JM_{code}.pdf"

        pdf_bytes, pdf_name = generate_master_pdf({
            "val": val_depa, "ini": inicial, "inv_a": inv_amoblado, "inv_t": inv_total,
            "roi": roi_airbnb, "flujo": flujo_neto, "pb": rec, "exc": ventaja_anual
        })
        st.download_button("📥 DESCARGAR INFORME DE AUDITORIA (PDF)", data=pdf_bytes, file_name=pdf_name)
