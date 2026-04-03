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
    st.set_page_config(page_title="Industrial Audit | JM", layout="wide")
except:
    pass

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def check_password():
    if not st.session_state.authenticated:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.title("🔐 Acceso Sistema Industrial")
            password = st.text_input("Contraseña de Consultor:", type="password")
            if st.button("Ingresar al Sistema"):
                if password == "Jancarlo2026":
                    st.session_state.authenticated = True
                    st.rerun()
                else: st.error("Acceso Denegado.")
        return False
    return True

if check_password():
    # CSS: Estilo Industrial (Tipografía Mono, Bordes Marcados, Sin +/-)
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
        
        /* Reset de Inputs: Eliminar botones + y - */
        button.step-up, button.step-down { display: none !important; }
        input[type=number]::-webkit-inner-spin-button, 
        input[type=number]::-webkit-outer-spin-button { -webkit-appearance: none; margin: 0; }
        input[type=number] { -moz-appearance: textfield; }

        .main { background-color: #0e1117; }
        
        /* Títulos */
        .section-title { 
            color: #ffffff !important; font-size: 1.5rem; font-weight: bold; 
            padding: 10px 0; border-bottom: 2px solid #30363d; margin-bottom: 20px;
            font-family: 'Roboto Mono', monospace;
        }

        /* Tarjetas Estilo Industrial */
        .card-base {
            border: 2px solid #30363d; border-radius: 5px; padding: 20px;
            text-align: center; margin-bottom: 15px; color: #ffffff !important;
            font-family: 'Roboto Mono', monospace;
        }
        .card-blue { background-color: #1c3d5a; }
        .card-green { background-color: #1b4332; }
        .card-red { background-color: #4c1d1d; }
        .card-gray { background-color: #21262d; }
        .card-gold { background-color: #744210; }
        .card-indigo { background-color: #312e81; }

        .val-pos { color: #60a5fa; font-size: 2rem; font-weight: bold; }
        .val-neg { color: #f87171; font-size: 2rem; font-weight: bold; }
        .label-card { font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; font-weight: bold; color: #ffffff; }

        .info-text { font-size: 0.95rem; color: #8b949e; margin-bottom: 15px; line-height: 1.5; }
        .footer-tip {
            background-color: #161b22; color: #ffffff; padding: 20px;
            border: 1px solid #30363d; border-left: 5px solid #58a6ff; margin-top: 30px;
            font-family: 'Roboto Mono', monospace;
        }
        </style>
        """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("📋 Parámetros de Auditoría")
        val_depa = st.number_input("Precio Propiedad (S/.) 🏠", value=250000)
        inv_amoblado = st.number_input("Inversión Amoblado (S/.) 🛋️", value=25000)
        st.write("---")
        tcea = st.number_input("TCEA Bancaria (%) 🏦", value=9.5)
        plazo_años = st.selectbox("Plazo Crédito (Años) 🗓️", [10, 15, 20, 25], index=2)
        st.write("---")
        tarifa_base = st.number_input("Tarifa Noche Airbnb (S/.) 💰", value=180)
        ocupacion_act = st.selectbox("Días Ocupación Mensual 🌙", list(range(1, 31)), index=19)
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

    tabs = st.tabs(["💎 CAPITAL Y FLUJO", "📈 CRECIMIENTO", "⚖️ SENSIBILIDAD", "🔄 COMPARATIVA TRADICIONAL VS AIRBNB"])

    # --------------------------------------------------------- PESTAÑA 1
    with tabs[0]:
        st.markdown('<div class="section-title">🏗️ Estructura de Capital e Ingresos</div>', unsafe_allow_html=True)
        st.markdown('<p class="info-text">Desglose de la inversión inicial requerida para la puesta en marcha del activo 🏛️.</p>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="card-base card-blue"><div class="label-card">Inicial Banco (20%) 🏢</div><div class="val-pos">S/. {inicial:,.0f}</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="card-base card-blue"><div class="label-card">Mobiliario Capex 🛋️</div><div class="val-pos">S/. {inv_amoblado:,.0f}</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="card-base card-gray"><div class="label-card">Inversión Total 💎</div><div class="val-pos">S/. {inv_total:,.0f}</div></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">💸 Análisis Operativo Mensual</div>', unsafe_allow_html=True)
        st.markdown('<p class="info-text">Balance mensual entre ingresos generados y obligaciones operativas/bancarias 🧾.</p>', unsafe_allow_html=True)
        c4, c5, c6, c7 = st.columns(4)
        with c4: st.markdown(f'<div class="card-base card-gray"><div class="label-card">Ingreso Bruto 🏨</div><div class="val-pos">S/. {ingreso_bruto:,.0f}</div></div>', unsafe_allow_html=True)
        with c5: st.markdown(f'<div class="card-base card-gray"><div class="label-card">Cuota Hipotecaria 🏦</div><div class="val-neg">S/. -{cuota:,.0f}</div></div>', unsafe_allow_html=True)
        with c6: st.markdown(f'<div class="card-base card-gray"><div class="label-card">Manto. e Impuestos 🧾</div><div class="val-neg">S/. -{gastos_op:,.0f}</div></div>', unsafe_allow_html=True)
        with c7: st.markdown(f'<div class="card-base card-green"><div class="label-card">Cash Flow Neto 💰</div><div class="val-pos">S/. {flujo_neto:,.0f}</div></div>', unsafe_allow_html=True)

        st.markdown('### 📊 Rendimiento y Benchmark Financiero')
        cr1, cr2 = st.columns([1, 1.2])
        with cr1:
            st.markdown(f'<div class="card-base card-gold"><div class="label-card">ROI Inversión Actual 📈</div><div class="val-pos" style="color:white;">{roi_airbnb:.2f}%</div></div>', unsafe_allow_html=True)
        with cr2:
            st.table(pd.DataFrame({
                "Activo": ["Airbnb Proyectado", "S&P 500", "Depósito Plazo", "Renta Local"],
                "ROI Est.": [f"{roi_airbnb:.1f}%", "10.0%", "6.5%", "5.0%"]
            }))

        st.write("---")
        cp1, cp2 = st.columns([1, 1.2])
        años_pb = 25; meses = np.arange(0, años_pb*12+1); f_acum = [-inv_total]; rec = 0
        for m in meses[1:]:
            f_acum.append(f_acum[-1] + (flujo_neto if m <= plazo_años*12 else ingreso_bruto-gastos_op))
            if rec == 0 and f_acum[-1] >= 0: rec = m/12
        
        with cp1:
            st.markdown(f'<div class="card-base card-blue" style="border: 2px solid white;"><div class="label-card">Payback (Recuperación) ⏳</div><div class="val-pos" style="color:white; font-size:2.5rem;">{rec:.1f} Años</div></div>', unsafe_allow_html=True)
            st.markdown('<p class="info-text">ℹ️ Este indicador determina el punto en el que el flujo de caja acumulado iguala a la inversión inicial.</p>', unsafe_allow_html=True)
        with cp2:
            fig_pb = go.Figure()
            fig_pb.add_trace(go.Scatter(x=meses/12, y=[min(0, x) for x in f_acum], fill='tozeroy', fillcolor='rgba(248, 113, 113, 0.4)', line=dict(width=0), showlegend=False))
            fig_pb.add_trace(go.Scatter(x=meses/12, y=[max(0, x) for x in f_acum], fill='tozeroy', fillcolor='rgba(16, 185, 129, 0.4)', line=dict(width=0), showlegend=False))
            fig_pb.add_trace(go.Scatter(x=meses/12, y=f_acum, line=dict(color='#ffffff', width=3), name="Capital"))
            fig_pb.update_layout(title="<b>FLUJO DE CAPITAL ACUMULADO (MÁRGENES ROJO/VERDE)</b>", height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig_pb, use_container_width=True)

        st.markdown('<div class="footer-tip">💡 <b>TIP OPERATIVO:</b> Reinvertir el 10% del flujo neto en mantenimiento preventivo garantiza una calificación de 5 estrellas constante 🌟.</div>', unsafe_allow_html=True)

    # --------------------------------------------------------- PESTAÑA 2
    with tabs[1]:
        st.markdown('<div class="section-title">🏔️ Notas de Valorización y Plusvalía</div>', unsafe_allow_html=True)
        st.markdown('<p class="info-text">Análisis del crecimiento del activo inmobiliario por el paso del tiempo 📈.</p>', unsafe_allow_html=True)
        p_slider = st.slider("Expectativa Plusvalía Anual (%)", 0.0, 10.0, 4.0)
        
        c_p = st.columns(4)
        for i, a in enumerate([5, 10, 15, 20]):
            g = (val_depa * (1 + p_slider/100)**a) - val_depa
            with c_p[i]: 
                st.markdown(f'<div class="card-base card-blue"><div class="label-card">Plusvalía {a}A 📈</div><div class="val-pos" style="color:white;">S/. {g:,.0f}</div></div>', unsafe_allow_html=True)
                st.caption(f"ℹ️ Ganancia de capital en {a} años.")
        
        st.markdown('<div class="section-title">📊 Evolución del Patrimonio Real</div>', unsafe_allow_html=True)
        años = np.arange(0, 26); v_mkt = [val_depa * (1+p_slider/100)**a for a in años]
        eq = [v - (prestamo * (1 - a/plazo_años) if a < plazo_años else 0) for a, v in zip(años, v_mkt)]
        
        fig_p = go.Figure()
        fig_p.add_trace(go.Bar(x=años, y=v_mkt, name="Valor Mercado", marker_color='#30363d'))
        fig_p.add_trace(go.Scatter(x=años, y=eq, name="Equity Real", line=dict(color='#58a6ff', width=4)))
        fig_p.update_layout(title="<b>CRECIMIENTO PATRIMONIAL VS AMORTIZACIÓN</b>", height=450, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_p, use_container_width=True)

        st.markdown('<div class="footer-tip">📈 <b>TIP FINANCIERO:</b> El "Equity" crece más rápido que la inflación gracias a la amortización de la cuota bancaria pagada por el huésped.</div>', unsafe_allow_html=True)

    # --------------------------------------------------------- PESTAÑA 3
    with tabs[2]:
        st.markdown('<div class="section-title">⚖️ Matriz de Estrés y Sensibilidad</div>', unsafe_allow_html=True)
        st.markdown('<p class="info-text">Pruebas de resistencia ante cambios en la ocupación y tarifas del mercado 🚦.</p>', unsafe_allow_html=True)
        
        def color_roi(val):
            c = '#f87171' if val < 5 else '#fbbf24' if val < 10 else '#4ade80'
            return f'background-color: {c}; color: #000; font-weight: bold;'

        # Sensibilidad 1
        st.subheader("📍 Días de Ocupación Mensual vs ROI")
        st.markdown('<p class="info-text">Determina cuántos días mínimo debe estar ocupado el departamento para ser rentable.</p>', unsafe_allow_html=True)
        cs1_t, cs1_g = st.columns([1, 1.8], vertical_alignment="center")
        d_range = [5, 10, 15, 20, 25, 30]
        roi_d = [((((tarifa_base*d*0.85) - cuota - mantenimiento - (tarifa_base*d*0.85*0.05))*12/inv_total)*100) for d in d_range]
        with cs1_t:
            st.table(pd.DataFrame({"Días/Mes": d_range, "ROI Anual %": roi_d}).style.map(color_roi, subset=['ROI Anual %']).format({"ROI Anual %": "{:.2f}%"}))
        with cs1_g:
            fig_d = go.Figure(go.Scatter(x=d_range, y=roi_d, mode='lines+markers', line=dict(color='#60a5fa', width=4), marker=dict(size=12)))
            fig_d.update_layout(height=650, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", title="<b>CURVA DE OCUPACIÓN</b>")
            st.plotly_chart(fig_d, use_container_width=True)

        # Sensibilidad 2
        st.subheader("💰 Tarifa Diaria vs ROI")
        st.markdown('<p class="info-text">Analiza el impacto de ajustar tus precios frente a la competencia 💵.</p>', unsafe_allow_html=True)
        cs2_t, cs2_g = st.columns([1, 1.8], vertical_alignment="center")
        t_range = list(range(int(tarifa_base)-30, int(tarifa_base)+40, 10))
        roi_t = [((((t*ocupacion_act*0.85) - cuota - mantenimiento - (t*ocupacion_act*0.85*0.05))*12/inv_total)*100) for t in t_range]
        with cs2_t:
            st.table(pd.DataFrame({"Tarifa S/.": t_range, "ROI Anual %": roi_t}).style.map(color_roi, subset=['ROI Anual %']).format({"ROI Anual %": "{:.2f}%"}))
        with cs2_g:
            fig_t = go.Figure(go.Scatter(x=t_range, y=roi_t, mode='lines+markers', line=dict(color='#34d399', width=4), marker=dict(size=12)))
            fig_t.update_layout(height=650, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", title="<b>CURVA DE TARIFA</b>")
            st.plotly_chart(fig_t, use_container_width=True)

        st.markdown('<div class="footer-tip">⚠️ <b>RECOMENDACIÓN:</b> Mantener un fondo de emergencia equivalente a 2 cuotas bancarias para absorber estacionalidades negativas.</div>', unsafe_allow_html=True)

    # --------------------------------------------------------- PESTAÑA 4
    with tabs[3]:
        st.markdown('<div class="section-title">⚖️ Comparativa: Renta Tradicional vs Airbnb</div>', unsafe_allow_html=True)
        st.markdown('<p class="info-text">ℹ️ Resumen ejecutivo del diferencial de rentabilidad entre ambos modelos de negocio.</p>', unsafe_allow_html=True)
        
        ventaja_anual = (flujo_neto * 12) - utilidad_trad
        dif_roi = roi_airbnb - roi_trad
        
        cc = st.columns(4)
        with cc[0]: st.markdown(f'<div class="card-base card-green"><div class="label-card">Excedente Anual Airbnb 🏆</div><div class="val-pos" style="color:white;">S/. {ventaja_anual:,.0f}</div></div>', unsafe_allow_html=True)
        with cc[1]: st.markdown(f'<div class="card-base card-gray"><div class="label-card">ROI Airbnb 🏨</div><div class="val-pos" style="color:white;">{roi_airbnb:.1f}%</div></div>', unsafe_allow_html=True)
        with cc[2]: st.markdown(f'<div class="card-base card-gray"><div class="label-card">ROI Tradicional 🏠</div><div class="val-pos" style="color:white;">{roi_trad:.1f}%</div></div>', unsafe_allow_html=True)
        with cc[3]: st.markdown(f'<div class="card-base card-indigo"><div class="label-card">Diferencia ROI 🚀</div><div class="val-pos" style="color:white;">{dif_roi:+.1f}%</div></div>', unsafe_allow_html=True)
        
        st.write("---")
        st.markdown('### 📊 Comparativa de Utilidad Neta Líquida Anual')
        labels = ['<b>MODELO AIRBNB</b>', '<b>RENTA TRADICIONAL</b>']
        vals = [flujo_neto*12, utilidad_trad]
        fig_c = go.Figure([go.Bar(
            x=labels, y=vals, 
            marker_color=['#10b981' if v > 0 else '#ef4444' for v in vals],
            text=[f'S/. {v:,.0f}' for v in vals],
            textposition='inside', insidetextanchor='middle',
            textfont=dict(size=30, color='white', family='Roboto Mono', weight='bold')
        )])
        fig_c.update_layout(height=600, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_c, use_container_width=True)
        
        st.markdown('<p class="info-text" style="text-align:justify;"><b>Análisis de Variables y Relación:</b> El gráfico muestra la rentabilidad líquida final. El Modelo Airbnb asume mayor riesgo operativo a cambio de un flujo de caja significativamente superior. La Renta Tradicional minimiza la gestión pero reduce el retorno. Este reporte sugiere que la diferencia de ROI justifica la gestión activa en este activo inmobiliario.</p>', unsafe_allow_html=True)

        st.markdown('<div class="footer-tip">🏁 <b>DICTAMEN FINAL:</b> El flujo de caja excedente permite amortizar el capital bancario en un 40% más de velocidad que el modelo tradicional.</div>', unsafe_allow_html=True)

# =========================================================
# MOTOR DE PDF (DENSIDAD INFORMATIVA EXTREMA)
# =========================================================
def generate_master_pdf(d):
    pdf = FPDF()
    pdf.add_page()
    # Header Audit
    pdf.set_fill_color(14, 17, 23); pdf.rect(0, 0, 210, 55, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", 'B', 18)
    pdf.cell(0, 20, "AUDITORIA TECNICA DE INVERSION INMOBILIARIA", ln=True, align='C')
    pdf.set_font("Arial", '', 10); pdf.cell(0, 5, "RESPONSABLE: ING. JANCARLO MENDOZA - EXPERTO INMOBILIARIO", ln=True, align='C')
    pdf.cell(0, 5, f"LIMA, PERU | FECHA DE EMISION: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align='C')
    pdf.ln(35); pdf.set_text_color(0, 0, 0)

    # Sección 1
    pdf.set_font("Arial", 'B', 12); pdf.set_text_color(28, 61, 90)
    pdf.cell(0, 10, "1. MEMORIA DE CAPITAL Y APALANCAMIENTO", ln=True)
    pdf.set_font("Arial", '', 9); pdf.set_text_color(50, 50, 50)
    pdf.multi_cell(0, 5, "Analisis detallado del desembolso inicial necesario. Se considera un apalancamiento del 80% (Loan-to-Value) con tasas TCEA vigentes. El 'Cash-on-Cash' se calcula sobre la inversion total que incluye el equipamiento del activo para operacion turistica.")
    pdf.ln(2)
    rows = [["CONCEPTO", "VALOR (S/.)", "COMENTARIO"], ["Precio Propiedad", f"{d['val']:,.0f}", "Valor comercial"], ["Cuota Inicial (20%)", f"{d['ini']:,.0f}", "Capital propio"], ["Inversion Amoblado", f"{d['inv_a']:,.0f}", "Habilitacion"], ["INVERSION TOTAL", f"{d['inv_t']:,.0f}", "Monto real invertido"]]
    for r in rows:
        pdf.cell(65, 8, r[0], 1); pdf.cell(35, 8, r[1], 1); pdf.cell(90, 8, r[2], 1, ln=True)

    # Sección 2
    pdf.ln(8); pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "2. PROYECCION DE FLUJO DE CAJA MENSUAL", ln=True)
    pdf.set_font("Arial", '', 9)
    pdf.multi_cell(0, 5, "Proyeccion operativa basada en ocupacion de mercado. Se descuenta el impuesto cedular (5%) y gastos de mantenimiento.")
    ops = [["Ingresos Airbnb", f"S/. {d['i_b']:,.0f}"], ["Cuota Bancaria", f"S/. -{d['cuo']:,.0f}"], ["Gastos/Impuestos", f"S/. -{d['gop']:,.0f}"], ["CASH FLOW NETO", f"S/. {d['f_n']:,.0f}"]]
    for r in ops:
        pdf.cell(90, 8, r[0], 1); pdf.cell(100, 8, r[1], 1, ln=True)

    # Sección 3
    pdf.ln(8); pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "3. METRICAS DE RENTABILIDAD Y DICTAMEN", ln=True)
    pdf.set_font("Arial", '', 9)
    pdf.cell(0, 7, f"- ROI Cash-on-Cash Proyectado: {d['roi']:.2f}% Anual", ln=True)
    pdf.cell(0, 7, f"- ROI Renta Tradicional: {d['roi_t']:.2f}% Anual", ln=True)
    pdf.cell(0, 7, f"- Tiempo de Recuperacion (Payback): {d['pb']:.1f} Años", ln=True)
    pdf.cell(0, 7, f"- Patrimonio Neto a 10 Años (Equity): S/. {d['v10']:,.0f}", ln=True)
    pdf.ln(5); pdf.set_font("Arial", 'I', 8)
    pdf.multi_cell(0, 4, "AVISO: Este reporte es una herramienta de soporte a la decision inmobiliaria. Los datos de ocupacion varian segun gestion y estacionalidad en la Ciudad de Lima.")

    return pdf.output(dest='S').encode('latin-1')

if st.session_state.authenticated:
    st.write("---")
    if st.button("📥 GENERAR INFORME TECNICO COMPLETO (PDF)"):
        v10_calc = (val_depa * (1 + p_slider/100)**10) - (prestamo * 0.5)
        pdf_bytes = generate_master_pdf({
            "val": val_depa, "ini": inicial, "inv_a": inv_amoblado, "inv_t": inv_total,
            "i_b": ingreso_bruto, "cuo": cuota, "gop": gastos_op, "f_n": flujo_neto,
            "roi": roi_airbnb, "roi_t": roi_trad, "pb": rec, "v10": v10_calc
        })
        st.download_button("Guardar Informe Técnico", data=pdf_bytes, file_name=f"Informe_Auditoria_JM.pdf")
