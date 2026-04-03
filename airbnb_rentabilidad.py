import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime

# =========================================================
# 0. CONFIGURACIÓN Y ESTÉTICA "INDUSTRIAL-TECH"
# =========================================================
try:
    st.set_page_config(page_title="Auditoría Inmobiliaria | JM", layout="wide")
except:
    pass

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
    # CSS: Estilo Industrial (Sin botones +/- y con tarjetas de colores sólidos)
    st.markdown("""
        <style>
        /* Reset de Inputs: Eliminar botones + y - */
        button.step-up, button.step-down { display: none !important; }
        input[type=number]::-webkit-inner-spin-button, 
        input[type=number]::-webkit-outer-spin-button { -webkit-appearance: none; margin: 0; }
        input[type=number] { -moz-appearance: textfield; }

        .main { background-color: #0e1117; }
        
        /* Títulos y Secciones */
        .section-title { 
            color: #ffffff; font-size: 1.4rem; font-weight: bold; 
            padding: 10px 0; border-bottom: 2px solid #30363d; margin-bottom: 20px;
        }

        /* Tarjetas Estilo Industrial */
        .card-base {
            border: 2px solid #30363d; border-radius: 5px; padding: 20px;
            text-align: center; margin-bottom: 15px; color: #ffffff !important;
        }
        .card-blue { background-color: #1c3d5a; }   /* Industrial Blue */
        .card-green { background-color: #1b4332; }  /* Forest Green */
        .card-red { background-color: #4c1d1d; }    /* Dark Red */
        .card-gray { background-color: #21262d; }   /* Steel Gray */
        .card-gold { background-color: #744210; }   /* Bronze/Gold */

        .val-pos { color: #60a5fa; font-size: 1.8rem; font-weight: bold; }
        .val-neg { color: #f87171; font-size: 1.8rem; font-weight: bold; }
        .label-card { font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; font-weight: 600; }

        /* Textos Informativos */
        .info-text { font-size: 0.9rem; color: #8b949e; margin-bottom: 15px; line-height: 1.4; }
        .footer-tip {
            background-color: #161b22; color: #ffffff; padding: 20px;
            border: 1px solid #30363d; border-left: 5px solid #58a6ff; margin-top: 30px;
        }
        </style>
        """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("📋 Parámetros Operativos")
        val_depa = st.number_input("Precio de Venta (S/.) 🏠", value=250000)
        inv_amoblado = st.number_input("Inversión Amoblado (S/.) 🛋️", value=25000)
        st.write("---")
        tcea = st.number_input("TCEA Hipotecaria (%) 🏦", value=9.5)
        plazo_años = st.selectbox("Plazo del Crédito (Años) 🗓️", [10, 15, 20, 25], index=2)
        st.write("---")
        tarifa_base = st.number_input("Tarifa Noche Airbnb (S/.) 💰", value=180)
        ocupacion_act = st.selectbox("Días de Ocupación Mensual 🌙", list(range(1, 31)), index=19)
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

    tabs = st.tabs(["📊 FLUJO OPERATIVO", "📈 PATRIMONIO", "⚖️ SENSIBILIDAD", "🔄 COMPARATIVA TRADICIONAL VS AIRBNB"])

    # --------------------------------------------------------- PESTAÑA 1
    with tabs[0]:
        st.markdown('<div class="section-title">🏗️ Estructura de Capital e Ingresos</div>', unsafe_allow_html=True)
        st.markdown('<p class="info-text">Información detallada sobre el desembolso inicial necesario y la composición del capital de inversión.</p>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="card-base card-blue"><div class="label-card">Cuota Inicial (20%)</div><div class="val-pos">S/. {inicial:,.0f}</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="card-base card-blue"><div class="label-card">Mobiliario/Equipamiento</div><div class="val-pos">S/. {inv_amoblado:,.0f}</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="card-base card-gray"><div class="label-card">Inversión Total Real</div><div class="val-pos">S/. {inv_total:,.0f}</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">💸 Análisis Operativo Mensual</div>', unsafe_allow_html=True)
        st.markdown('<p class="info-text">Balance entre ingresos proyectados y obligaciones financieras/operativas.</p>', unsafe_allow_html=True)
        c4, c5, c6, c7 = st.columns(4)
        with c4: st.markdown(f'<div class="card-base card-gray"><div class="label-card">Ingreso Airbnb</div><div class="val-pos">S/. {ingreso_bruto:,.0f}</div></div>', unsafe_allow_html=True)
        with c5: st.markdown(f'<div class="card-base card-gray"><div class="label-card">Servicio de Deuda</div><div class="val-neg">S/. -{cuota:,.0f}</div></div>', unsafe_allow_html=True)
        with c6: st.markdown(f'<div class="card-base card-gray"><div class="label-card">Gasto Op. / Impuestos</div><div class="val-neg">S/. -{gastos_op:,.0f}</div></div>', unsafe_allow_html=True)
        with c7: st.markdown(f'<div class="card-base card-green"><div class="label-card">Flujo Neto Mensual</div><div class="val-pos">S/. {flujo_neto:,.0f}</div></div>', unsafe_allow_html=True)

        st.write("---")
        # Payback y Gráfico
        cp1, cp2 = st.columns([1, 1.2])
        años_pb = 25; meses = np.arange(0, años_pb*12+1); f_acum = [-inv_total]; rec = 0
        for m in meses[1:]:
            f_acum.append(f_acum[-1] + (flujo_neto if m <= plazo_años*12 else ingreso_bruto-gastos_op))
            if rec == 0 and f_acum[-1] >= 0: rec = m/12
        
        with cp1:
            st.markdown(f'<div class="card-base card-blue"><div class="label-card">⏱️ Tiempo de Payback</div><div class="val-pos" style="color:white; font-size:2.5rem;">{rec:.1f} Años</div></div>', unsafe_allow_html=True)
            st.markdown('<p class="info-text">ℹ️ Este indicador determina el punto de equilibrio donde la inversión inicial es totalmente recuperada por el flujo de caja del activo.</p>', unsafe_allow_html=True)
        with cp2:
            fig_pb = go.Figure()
            fig_pb.add_trace(go.Scatter(x=meses/12, y=[min(0, x) for x in f_acum], fill='tozeroy', fillcolor='rgba(248, 113, 113, 0.4)', line=dict(width=0), showlegend=False))
            fig_pb.add_trace(go.Scatter(x=meses/12, y=[max(0, x) for x in f_acum], fill='tozeroy', fillcolor='rgba(96, 165, 250, 0.4)', line=dict(width=0), showlegend=False))
            fig_pb.add_trace(go.Scatter(x=meses/12, y=f_acum, line=dict(color='#ffffff', width=3), name="Capital"))
            fig_pb.update_layout(title="<b>ANÁLISIS DE RECUPERACIÓN DE CAPITAL</b>", height=350, margin=dict(t=40), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig_pb, use_container_width=True)
            st.markdown('<p class="info-text">Gráfico: El área roja indica deuda/inversión pendiente. El área azul representa la generación de riqueza neta sobre la inversión inicial.</p>', unsafe_allow_html=True)

        st.markdown('<div class="footer-tip">💡 <b>TIP OPERATIVO:</b> Optimizar el amoblado para durabilidad reduce el CAPEX de reposición a largo plazo, mejorando el ROI real anual.</div>', unsafe_allow_html=True)

    # --------------------------------------------------------- PESTAÑA 2
    with tabs[1]:
        st.markdown('<div class="section-title">🏔️ Proyección de Patrimonio y Plusvalía</div>', unsafe_allow_html=True)
        st.markdown('<p class="info-text">Análisis del crecimiento del valor del activo en el mercado inmobiliario de Lima.</p>', unsafe_allow_html=True)
        plus_slider = st.slider("Tasa de Plusvalía Anual (%) 📈", 0.0, 10.0, 4.0)
        
        c_p = st.columns(4)
        for i, a in enumerate([5, 10, 15, 20]):
            g = (val_depa * (1 + plus_slider/100)**a) - val_depa
            with c_p[i]: 
                st.markdown(f'<div class="card-base card-gray"><div class="label-card">Plusvalía a {a} Años</div><div class="val-pos">S/. {g:,.0f}</div></div>', unsafe_allow_html=True)
                st.markdown(f'<p class="info-text">Crecimiento estimado del valor del m2 tras {a} años de tenencia.</p>', unsafe_allow_html=True)
        
        st.write("---")
        años = np.arange(0, 26); v_mkt = [val_depa * (1+plus_slider/100)**a for a in años]
        eq = [v - (prestamo * (1 - a/plazo_años) if a < plazo_años else 0) for a, v in zip(años, v_mkt)]
        
        st.markdown('### 📊 Evolución del Equity (Patrimonio Neto)')
        fig_p = go.Figure()
        fig_p.add_trace(go.Bar(x=años, y=v_mkt, name="Valor Propiedad", marker_color='#30363d'))
        fig_p.add_trace(go.Scatter(x=años, y=eq, name="Patrimonio Real", line=dict(color='#58a6ff', width=4)))
        fig_p.update_layout(title="<b>CRECIMIENTO PATRIMONIAL VS DEUDA</b>", height=450, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_p, use_container_width=True)
        st.markdown('<p class="info-text">ℹ️ El Equity es su verdadera riqueza: el valor de la propiedad menos lo que le debe al banco. Este crece por la plusvalía y la amortización de la cuota.</p>', unsafe_allow_html=True)

        st.markdown('<div class="footer-tip">📉 <b>RECOMENDACIÓN:</b> En zonas de alta demanda como Surquillo o Magdalena, la plusvalía suele compensar incluso años de baja ocupación.</div>', unsafe_allow_html=True)

    # --------------------------------------------------------- PESTAÑA 3
    with tabs[2]:
        st.markdown('<div class="section-title">⚖️ Análisis de Resiliencia Operativa</div>', unsafe_allow_html=True)
        st.markdown('<p class="info-text">Pruebas de estrés para determinar la rentabilidad bajo diferentes escenarios de mercado.</p>', unsafe_allow_html=True)

        def semaforo_roi(val):
            color = '#f87171' if val < 5 else '#fbbf24' if val < 10 else '#4ade80'
            return f'background-color: {color}; color: black; font-weight: bold;'

        # Sensibilidad 1
        st.markdown('### 📍 Escenarios por Días de Ocupación')
        st.markdown('<p class="info-text">Relación directa entre la demanda mensual y el retorno anual sobre la inversión total.</p>', unsafe_allow_html=True)
        cs1_t, cs1_g = st.columns([1, 1.5], vertical_alignment="center")
        d_range = [5, 10, 15, 20, 25, 30]
        roi_d = [((((tarifa_base*d*0.85) - cuota - mantenimiento - (tarifa_base*d*0.85*0.05))*12/inv_total)*100) for d in d_range]
        with cs1_t:
            df_d = pd.DataFrame({"Días/Mes": d_range, "ROI Anual %": roi_d})
            st.table(df_d.style.map(semaforo_roi, subset=['ROI Anual %']).format({"ROI Anual %": "{:.2f}%", "Días/Mes": "{:d}"}))
        with cs1_g:
            fig_d = go.Figure(go.Scatter(x=d_range, y=roi_d, mode='lines+markers', line=dict(color='#58a6ff', width=4), marker=dict(size=10)))
            fig_d.update_layout(height=600, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", title="<b>CURVA SENSIBILIDAD: OCUPACIÓN</b>")
            st.plotly_chart(fig_d, use_container_width=True)

        # Sensibilidad 2
        st.markdown('### 💰 Escenarios por Tarifa Diaria')
        st.markdown('<p class="info-text">Análisis de competitividad de precios: ¿Cómo afecta el precio por noche a su rentabilidad final?</p>', unsafe_allow_html=True)
        cs2_t, cs2_g = st.columns([1, 1.5], vertical_alignment="center")
        t_range = list(range(int(tarifa_base)-40, int(tarifa_base)+60, 10))
        roi_t = [((((t*ocupacion_act*0.85) - cuota - mantenimiento - (t*ocupacion_act*0.85*0.05))*12/inv_total)*100) for t in t_range]
        with cs2_t:
            df_t = pd.DataFrame({"Tarifa S/.": t_range, "ROI Anual %": roi_t})
            st.table(df_t.style.map(semaforo_roi, subset=['ROI Anual %']).format({"ROI Anual %": "{:.2f}%", "Tarifa S/.": "{:d}"}))
        with cs2_g:
            fig_t = go.Figure(go.Scatter(x=t_range, y=roi_t, mode='lines+markers', line=dict(color='#4ade80', width=4), marker=dict(size=10)))
            fig_t.update_layout(height=600, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", title="<b>CURVA SENSIBILIDAD: TARIFA</b>")
            st.plotly_chart(fig_t, use_container_width=True)

        st.markdown('<div class="footer-tip">⚠️ <b>TIP DE RIESGO:</b> Mantener un fondo de reserva equivalente a 3 cuotas hipotecarias es vital para soportar meses de baja ocupación sin afectar su historial crediticio.</div>', unsafe_allow_html=True)

    # --------------------------------------------------------- PESTAÑA 4
    with tabs[3]:
        st.markdown('<div class="section-title">⚖️ Veredicto: Renta Tradicional vs Airbnb</div>', unsafe_allow_html=True)
        st.markdown('<p class="info-text">Comparativa final de rendimiento neto después de todos los gastos e impuestos.</p>', unsafe_allow_html=True)
        
        ventaja_anual = (flujo_neto * 12) - utilidad_trad
        dif_roi = roi_airbnb - roi_trad
        
        cc = st.columns(4)
        with cc[0]: st.markdown(f'<div class="card-base card-green"><div class="label-card">Excedente Anual Airbnb 🏆</div><div class="val-pos" style="color:white;">S/. {ventaja_anual:,.0f}</div></div>', unsafe_allow_html=True)
        with cc[1]: st.markdown(f'<div class="card-base card-gray"><div class="label-card">ROI Airbnb 🏨</div><div class="val-pos" style="color:white;">{roi_airbnb:.2f}%</div></div>', unsafe_allow_html=True)
        with cc[2]: st.markdown(f'<div class="card-base card-gray"><div class="label-card">ROI Tradicional 🏠</div><div class="val-pos" style="color:white;">{roi_trad:.2f}%</div></div>', unsafe_allow_html=True)
        with cc[3]: st.markdown(f'<div class="card-base card-blue"><div class="label-card">Diferencial ROI 🚀</div><div class="val-pos" style="color:white;">{dif_roi:+.2f}%</div></div>', unsafe_allow_html=True)
        
        st.write("---")
        st.markdown('### 📊 Comparativa de Utilidad Neta Líquida Anual')
        labels = ['<b>MODELO AIRBNB</b>', '<b>RENTA TRADICIONAL</b>']
        vals = [flujo_neto*12, utilidad_trad]
        fig_c = go.Figure([go.Bar(
            x=labels, y=vals, 
            marker_color=['#10b981' if v > 0 else '#ef4444' for v in vals],
            text=[f'S/. {v:,.0f}' for v in vals],
            textposition='inside', insidetextanchor='middle',
            textfont=dict(size=28, color='white', family='Arial', weight='bold')
        )])
        fig_c.update_layout(height=600, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_c, use_container_width=True)
        
        st.markdown('<p class="info-text" style="text-align:justify;"><b>Análisis de Variables y Relación:</b> El gráfico muestra la Utilidad Neta Líquida Anualizada (Cash Flow después de impuestos y deuda). La relación entre ambas barras determina el "Premio por Operación". Si el Modelo Airbnb no supera al Tradicional por al menos un 30%, el riesgo operativo de la gestión de cortas estancias podría no estar justificado financieramente frente a la estabilidad de un contrato anual tradicional.</p>', unsafe_allow_html=True)

        st.markdown('<div class="footer-tip">🏁 <b>DICTAMEN FINAL:</b> El Modelo Airbnb es la opción ganadora en este escenario, proporcionando un flujo de caja superior que permite acelerar el pago de la hipoteca.</div>', unsafe_allow_html=True)

# =========================================================
# MOTOR DE PDF (DENSIDAD INFORMATIVA EXTREMA)
# =========================================================
def generate_master_pdf(d):
    pdf = FPDF()
    pdf.add_page()
    # Header Audit
    pdf.set_fill_color(14, 17, 23); pdf.rect(0, 0, 210, 55, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", 'B', 18)
    pdf.cell(0, 20, "AUDITORIA DE FACTIBILIDAD E INGENIERIA INMOBILIARIA", ln=True, align='C')
    pdf.set_font("Arial", '', 10); pdf.cell(0, 5, "RESPONSABLE TECNICO: ING. JANCARLO MENDOZA", ln=True, align='C')
    pdf.cell(0, 5, f"REPORTE DE INVERSION - LIMA, PERU - {datetime.now().strftime('%d/%m/%Y')}", ln=True, align='C')
    pdf.ln(35); pdf.set_text_color(0, 0, 0)

    # Bloque 1: Ingeniería de Capital
    pdf.set_font("Arial", 'B', 12); pdf.set_text_color(28, 61, 90)
    pdf.cell(0, 10, "1. MEMORIA ANALITICA DE CAPITAL Y ADQUISICION", ln=True)
    pdf.set_font("Arial", '', 9); pdf.set_text_color(40, 40, 40)
    pdf.multi_cell(0, 5, "Este documento certifica el analisis tecnico de la inversion. Se considera un esquema de apalancamiento del 80% LTV (Loan to Value) con una tasa TCEA de mercado. La inversion total inicial contempla no solo la cuota de entrada sino tambien la habilitacion de activos mobiliarios para su explotacion comercial.")
    pdf.ln(2)
    rows = [["CONCEPTO ANALIZADO", "VALOR (S/.)", "DESCRIPCION"],
            ["Valor de Compra del Inmueble", f"{d['val']:,.0f}", "Valor comercial de mercado"],
            ["Cuota Inicial Pagada (20%)", f"{d['ini']:,.0f}", "Capital propio aportado"],
            ["Inversion en Amoblado/Capex", f"{d['inv_a']:,.0f}", "Equipamiento para operacion"],
            ["CASH-OUT TOTAL REQUERIDO", f"{d['inv_t']:,.0f}", "Monto total de inversion real"]]
    for r in rows:
        pdf.cell(65, 8, r[0], 1); pdf.cell(35, 8, r[1], 1); pdf.cell(90, 8, r[2], 1, ln=True)

    # Bloque 2: Flujos y Operatividad
    pdf.ln(8); pdf.set_font("Arial", 'B', 12); pdf.set_text_color(28, 61, 90)
    pdf.cell(0, 10, "2. PROYECCION DE FLUJO DE CAJA MENSUALIZADO", ln=True)
    pdf.set_font("Arial", '', 9)
    pdf.multi_cell(0, 5, f"Analisis de ingresos dinamicos basados en una ocupacion del {d['occ']:.1f}%. El modelo descuenta automaticamente los impuestos de ley (5% cedular de primera categoria) y las comisiones de plataforma.")
    pdf.ln(2)
    ops = [["Ingreso Bruto Mensual Estimado", f"S/. {d['i_b']:,.0f}"], ["Servicio de Deuda Hipotecaria", f"S/. -{d['cuo']:,.0f}"], ["Gastos Operativos (Manto/Arbitrios)", f"S/. -{d['gop']:,.0f}"], ["UTILIDAD NETA DISPONIBLE (CASH FLOW)", f"S/. {d['f_n']:,.0f}"]]
    for r in ops:
        pdf.cell(90, 8, r[0], 1); pdf.cell(100, 8, r[1], 1, ln=True)

    # Bloque 3: Dictamen Final
    pdf.ln(8); pdf.set_font("Arial", 'B', 12); pdf.set_text_color(28, 61, 90)
    pdf.cell(0, 10, "3. METRICAS DE RENTABILIDAD Y PLUSVALIA", ln=True)
    pdf.set_font("Arial", '', 9); pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 7, f"- ROI Cash-on-Cash Proyectado (Airbnb): {d['roi']:.2f}% Anual sobre inversion total.", ln=True)
    pdf.cell(0, 7, f"- ROI Modelo Tradicional: {d['roi_t']:.2f}% Anual (Escenario Conservador).", ln=True)
    pdf.cell(0, 7, f"- Tiempo de Recuperacion de Inversion (Payback): {d['pb']:.1f} Años.", ln=True)
    pdf.cell(0, 7, f"- Patrimonio Neto Proyectado a 10 Años (Equity): S/. {d['v10']:,.0f} (Valorizacion + Amortizacion).", ln=True)
    pdf.ln(10); pdf.set_font("Arial", 'I', 8)
    pdf.multi_cell(0, 4, "DECLARACION: Este reporte es una herramienta de apoyo a la decision. Las variaciones en la politica monetaria y la estacionalidad del turismo en Lima pueden afectar los resultados. Se recomienda una auditoria legal del reglamento de propiedad horizontal antes del desembolso.")

    return pdf.output(dest='S').encode('latin-1')

if st.session_state.authenticated:
    st.write("---")
    if st.button("📥 GENERAR INFORME DE AUDITORIA COMPLETO (PDF)"):
        v10_calc = (val_depa * (1 + plus_slider/100)**10) - (prestamo * 0.5) # Estimado simple
        pdf_bytes = generate_master_pdf({
            "val": val_depa, "ini": inicial, "inv_a": inv_amoblado, "inv_t": inv_total,
            "i_b": ingreso_bruto, "cuo": cuota, "gop": gastos_op, "f_n": flujo_neto,
            "roi": roi_airbnb, "roi_t": roi_trad, "pb": rec, "v10": v10_calc, "occ": (ocupacion_act/30)*100
        })
        st.download_button("Guardar Informe Técnico", data=pdf_bytes, file_name=f"Auditoria_Inmobiliaria_JM.pdf")
