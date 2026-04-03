import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime

# =========================================================
# 0. CONFIGURACIÓN Y ESTÉTICA DE SISTEMA PURA
# =========================================================
try:
    st.set_page_config(page_title="Auditoría JM", layout="wide")
except:
    pass

# Definición de fuentes de sistema (Sin Roboto ni Google Fonts)
SYS_SANS = '-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif'
SYS_MONO = 'ui-monospace, SFMono-Regular, SF Mono, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace'

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def check_password():
    if not st.session_state.authenticated:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.title("Acceso al sistema de auditoría 🔐")
            password = st.text_input("Contraseña de consultor:", type="password")
            if st.button("Ingresar"):
                if password == "Jancarlo2026":
                    st.session_state.authenticated = True
                    st.rerun()
                else: st.error("Acceso denegado.")
        return False
    return True

if check_password():
    # CSS: ELIMINACIÓN DE BOTONES +/- Y UNIFICACIÓN DE FUENTES
    st.markdown(f"""
        <style>
        /* 1. Fuente de Sistema en todo el DOM */
        html, body, [class*="css"], .stMarkdown, p, div, span, label, button {{
            font-family: {SYS_SANS} !important;
            color: #ffffff;
        }}
        
        /* 2. Monospace estricto para números y tablas */
        .stTable, [data-testid="stTable"], code, .val-pos, .val-neg, .mono-data {{
            font-family: {SYS_MONO} !important;
        }}

        /* 3. Limpieza de Inputs (No +/-) */
        button.step-up, button.step-down {{ display: none !important; }}
        input[type=number]::-webkit-inner-spin-button, 
        input[type=number]::-webkit-outer-spin-button {{ -webkit-appearance: none; margin: 0; }}
        input[type=number] {{ -moz-appearance: textfield; }}

        .main {{ background-color: #0d1117; }}
        
        /* 4. Títulos estilo oración */
        .section-title {{ 
            color: #ffffff; font-size: 1.6rem; font-weight: 600; 
            padding: 10px 0; border-bottom: 1px solid #30363d; margin: 20px 0;
        }}

        /* 5. Tarjetas industriales */
        .card-base {{
            border: 1px solid #30363d; border-radius: 6px; padding: 20px;
            text-align: center; margin-bottom: 15px; color: #ffffff !important;
        }}
        .bg-blue {{ background-color: #051e3e; }}
        .bg-green {{ background-color: #062d1a; }}
        .bg-red {{ background-color: #3e0a0a; }}
        .bg-gray {{ background-color: #161b22; }}
        .bg-gold {{ background-color: #3e2b05; }}
        .bg-indigo {{ background-color: #1e1b4b; }}

        .val-pos {{ color: #58a6ff; font-size: 2.2rem; font-weight: 700; }}
        .val-neg {{ color: #f85149; font-size: 2.2rem; font-weight: 700; }}
        .label-card {{ font-size: 0.85rem; font-weight: 500; margin-bottom: 8px; opacity: 0.9; }}

        .info-box {{ font-size: 0.9rem; color: #8b949e; line-height: 1.5; margin: 10px 0; }}
        .footer-tip {{
            background-color: #0d1117; color: #ffffff; padding: 20px;
            border: 1px solid #30363d; border-left: 4px solid #58a6ff; margin-top: 30px;
        }}
        </style>
        """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("Entrada de datos 📋")
        val_depa = st.number_input("Precio de venta (S/.) 🏠", value=320000)
        inv_amoblado = st.number_input("Inversión en amoblado (S/.) 🛋️", value=35000)
        st.write("---")
        tcea = st.number_input("Tcea bancaria (%) 🏦", value=10.2)
        plazo_años = st.selectbox("Plazo del crédito (Años) 🗓️", [10, 15, 20, 25], index=2)
        st.write("---")
        tarifa_base = st.number_input("Tarifa por noche (S/.) 💰", value=220)
        ocupacion_act = st.selectbox("Días ocupados al mes 🌙", list(range(1, 31)), index=19)
        st.write("---")
        renta_trad = st.number_input("Renta tradicional mensual (S/.) 🏠", value=2100)

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

    tabs = st.tabs(["💎 Flujo operativo", "📈 Patrimonio", "⚖️ Sensibilidad", "🔄 Comparativa tradicional vs airbnb"])

    # --------------------------------------------------------- PESTAÑA 1
    with tabs[0]:
        st.markdown('<div class="section-title">Estructura de capital e ingresos 🏗️</div>', unsafe_allow_html=True)
        st.markdown('<p class="info-box">Análisis del capital propio (Equity) necesario para la puesta en marcha del activo inmobiliario.</p>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="card-base bg-blue"><div class="label-card">Cuota inicial 🏦</div><div class="val-pos">S/. {inicial:,.0f}</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="card-base bg-blue"><div class="label-card">Gasto amoblado 🛋️</div><div class="val-pos">S/. {inv_amoblado:,.0f}</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="card-base bg-gray"><div class="label-card">Inversión total 💎</div><div class="val-pos">S/. {inv_total:,.0f}</div></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">Análisis operativo mensual 💸</div>', unsafe_allow_html=True)
        st.markdown('<p class="info-box">Determinación del flujo de caja libre mensual tras el cumplimiento de obligaciones financieras y tributarias.</p>', unsafe_allow_html=True)
        c4, c5, c6, c7 = st.columns(4)
        with c4: st.markdown(f'<div class="card-base bg-gray"><div class="label-card">Ingresos brutos 🏨</div><div class="val-pos">S/. {ingreso_bruto:,.0f}</div></div>', unsafe_allow_html=True)
        with c5: st.markdown(f'<div class="card-base bg-gray"><div class="label-card">Pago hipotecario 🏦</div><div class="val-neg">S/. -{cuota:,.0f}</div></div>', unsafe_allow_html=True)
        with c6: st.markdown(f'<div class="card-base bg-gray"><div class="label-card">Opex e impuestos 🧾</div><div class="val-neg">S/. -{gastos_op:,.0f}</div></div>', unsafe_allow_html=True)
        with c7: st.markdown(f'<div class="card-base bg-green"><div class="label-card">Flujo neto 💰</div><div class="val-pos">S/. {flujo_neto:,.0f}</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">Comparativa de rentabilidad de la inversión 📈</div>', unsafe_allow_html=True)
        cr1, cr2 = st.columns([1, 1.2])
        with cr1:
            st.markdown(f'<div class="card-base bg-gold"><div class="label-card">Roi anual del proyecto 🚀</div><div class="val-pos" style="color:white;">{roi_airbnb:.2f}%</div></div>', unsafe_allow_html=True)
        with cr2:
            st.table(pd.DataFrame({
                "Tipo de inversión": ["Proyecto JM", "S&P 500", "Bolsa de valores (Local)", "Fondos mutuos", "Plazo fijo", "Bonos del tesoro"],
                "Retorno esperado": [f"{roi_airbnb:.1f}%", "10.0%", "12.5%", "8.0%", "6.5%", "5.5%"]
            }))

        st.write("---")
        cp1, cp2 = st.columns([1, 1.4])
        años_pb = 25; meses = np.arange(0, años_pb*12+1); f_acum = [-inv_total]; rec = 0
        for m in meses[1:]:
            f_acum.append(f_acum[-1] + (flujo_neto if m <= plazo_años*12 else ingreso_bruto-gastos_op))
            if rec == 0 and f_acum[-1] >= 0: rec = m/12
        
        with cp1:
            st.markdown(f'<div class="card-base bg-indigo"><div class="label-card">Tiempo de recuperación (Payback) ⏳</div><div class="val-pos" style="color:white; font-size:2.6rem;">{rec:.1f} Años</div></div>', unsafe_allow_html=True)
            st.markdown('<p class="info-box">Este indicador muestra el momento exacto en que la utilidad neta acumulada reembolsa la inversión inicial desembolsada.</p>', unsafe_allow_html=True)
        with cp2:
            fig_pb = go.Figure()
            fig_pb.add_trace(go.Scatter(x=meses/12, y=[min(0, x) for x in f_acum], fill='tozeroy', fillcolor='rgba(248, 81, 73, 0.4)', line=dict(width=0), showlegend=False))
            fig_pb.add_trace(go.Scatter(x=meses/12, y=[max(0, x) for x in f_acum], fill='tozeroy', fillcolor='rgba(63, 185, 80, 0.4)', line=dict(width=0), showlegend=False))
            fig_pb.add_trace(go.Scatter(x=meses/12, y=f_acum, line=dict(color='#ffffff', width=3), name="Balance"))
            fig_pb.update_layout(title="Progreso de recuperación de capital (Áreas de estrés operativo)", height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family=SYS_SANS, color="white"))
            st.plotly_chart(fig_pb, use_container_width=True)

        st.markdown('<div class="footer-tip">💡 <b>Tip financiero:</b> Procure amortizar capital extraordinario durante los primeros 5 años para reducir drásticamente el pago de intereses bancarios.</div>', unsafe_allow_html=True)

    # --------------------------------------------------------- PESTAÑA 2
    with tabs[1]:
        st.markdown('<div class="section-title">Evolución del patrimonio y plusvalía 🏔️</div>', unsafe_allow_html=True)
        st.markdown('<p class="info-box">La plusvalía es el incremento del valor del activo por factores de mercado y entorno urbano.</p>', unsafe_allow_html=True)
        p_slider = st.slider("Estimación de plusvalía anual (%)", 0.0, 10.0, 4.0)
        
        c_p = st.columns(4)
        for i, a in enumerate([5, 10, 15, 20]):
            g = (val_depa * (1 + p_slider/100)**a) - val_depa
            with c_p[i]: 
                st.markdown(f'<div class="card-base bg-blue"><div class="label-card">Plusvalía estimada en {a}A 📈</div><div class="val-pos" style="color:white;">S/. {g:,.0f}</div></div>', unsafe_allow_html=True)
                st.caption(f"Valorización esperada a {a} años.")
        
        st.markdown('<div class="section-title">Gráfico de crecimiento patrimonial real 📊</div>', unsafe_allow_html=True)
        st.markdown('<p class="info-box">Este gráfico detalla el "Equity" o patrimonio neto: la diferencia entre el valor de mercado y la deuda pendiente con el banco.</p>', unsafe_allow_html=True)
        años = np.arange(0, 26); v_mkt = [val_depa * (1+p_slider/100)**a for a in años]
        eq = [v - (prestamo * (1 - a/plazo_años) if a < plazo_años else 0) for a, v in zip(años, v_mkt)]
        
        fig_p = go.Figure()
        fig_p.add_trace(go.Bar(x=años, y=v_mkt, name="Valor de mercado", marker_color='#21262d'))
        fig_p.add_trace(go.Scatter(x=años, y=eq, name="Equity real (Patrimonio)", line=dict(color='#58a6ff', width=4)))
        fig_p.update_layout(title="Crecimiento del activo vs Amortización de deuda", height=450, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family=SYS_SANS, color="white"))
        st.plotly_chart(fig_p, use_container_width=True)

        st.markdown('<div class="footer-tip">📊 <b>Nota informativa:</b> Al cabo del plazo hipotecario, el 100% del valor de mercado se convierte en capital líquido disponible para el propietario.</div>', unsafe_allow_html=True)

    # --------------------------------------------------------- PESTAÑA 3
    with tabs[2]:
        st.markdown('<div class="section-title">Matrices de sensibilidad operativa ⚖️</div>', unsafe_allow_html=True)
        st.markdown('<p class="info-box">Análisis prospectivo para determinar la resiliencia del ROI ante variaciones en la ocupación y tarifas.</p>', unsafe_allow_html=True)
        
        def color_roi(val):
            c = '#f85149' if val < 5 else '#d29922' if val < 10 else '#3fb950'
            return f'background-color: {c}; color: #000; font-weight: bold; font-family: {SYS_MONO};'

        # Sensibilidad 1
        st.subheader("Sensibilidad: Días de ocupación vs Roi")
        st.markdown('<p class="info-box">Muestra cómo varía la rentabilidad según la cantidad de días reservados al mes (intervalos de 5 días).</p>', unsafe_allow_html=True)
        cs1_t, cs1_g = st.columns([1, 1.8], vertical_alignment="center")
        d_range = list(range(5, 35, 5))
        roi_d = [((((tarifa_base*d*0.85) - cuota - mantenimiento - (tarifa_base*d*0.85*0.05))*12/inv_total)*100) for d in d_range]
        with cs1_t:
            st.table(pd.DataFrame({"Días al mes": d_range, "Roi (%)": roi_d}).style.map(color_roi, subset=['Roi (%)']).format({"Roi (%)": "{:.2f}%"}))
        with cs1_g:
            fig_d = go.Figure(go.Scatter(x=d_range, y=roi_d, mode='lines+markers', line=dict(color='#58a6ff', width=4)))
            fig_d.update_layout(height=600, title="Curva de sensibilidad por ocupación", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family=SYS_SANS, color="white"))
            st.plotly_chart(fig_d, use_container_width=True)

        # Sensibilidad 2
        st.subheader("Sensibilidad: Tarifa airbnb vs Roi")
        st.markdown('<p class="info-box">Evaluación de rentabilidad basada en el ajuste de precios por noche (intervalos de S/. 10).</p>', unsafe_allow_html=True)
        cs2_t, cs2_g = st.columns([1, 1.8], vertical_alignment="center")
        t_range = list(range(int(tarifa_base)-30, int(tarifa_base)+40, 10))
        roi_t = [((((t*ocupacion_act*0.85) - cuota - mantenimiento - (t*ocupacion_act*0.85*0.05))*12/inv_total)*100) for t in t_range]
        with cs2_t:
            st.table(pd.DataFrame({"Tarifa (S/.)": t_range, "Roi (%)": roi_t}).style.map(color_roi, subset=['Roi (%)']).format({"Roi (%)": "{:.2f}%"}))
        with cs2_g:
            fig_t = go.Figure(go.Scatter(x=t_range, y=roi_t, mode='lines+markers', line=dict(color='#3fb950', width=4)))
            fig_t.update_layout(height=600, title="Curva de sensibilidad por tarifa", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family=SYS_SANS, color="white"))
            st.plotly_chart(fig_t, use_container_width=True)

        st.markdown('<div class="footer-tip">⚠️ <b>Recomendación estratégica:</b> Si la ocupación baja del 50%, considere una estrategia de precios agresiva para mejorar el posicionamiento en el algoritmo de Airbnb.</div>', unsafe_allow_html=True)

    # --------------------------------------------------------- PESTAÑA 4
    with tabs[3]:
        st.markdown('<div class="section-title">Veredicto de inversión 🔄</div>', unsafe_allow_html=True)
        st.markdown('<p class="info-box">Comparativa final de rendimiento entre el modelo de rentas cortas y el alquiler convencional.</p>', unsafe_allow_html=True)
        
        ventaja_anual = (flujo_neto * 12) - utilidad_trad
        dif_roi = roi_airbnb - roi_trad
        
        cc = st.columns(4)
        with cc[0]: st.markdown(f'<div class="card-base bg-green"><div class="label-card">Excedente anual airbnb 💰</div><div class="val-pos" style="color:white;">S/. {ventaja_anual:,.0f}</div></div>', unsafe_allow_html=True)
        with cc[1]: st.markdown(f'<div class="card-base bg-gray"><div class="label-card">Roi airbnb 🏨</div><div class="val-pos" style="color:white;">{roi_airbnb:.1f}%</div></div>', unsafe_allow_html=True)
        with cc[2]: st.markdown(f'<div class="card-base bg-gray"><div class="label-card">Roi tradicional 🏠</div><div class="val-pos" style="color:white;">{roi_trad:.1f}%</div></div>', unsafe_allow_html=True)
        with cc[3]: st.markdown(f'<div class="card-base bg-indigo"><div class="label-card">Diferencia de rois 🚀</div><div class="val-pos" style="color:white;">{dif_roi:+.1f}%</div></div>', unsafe_allow_html=True)
        
        st.write("---")
        st.markdown('<p class="info-box"><b>Interpretación del gráfico:</b> El gráfico muestra la utilidad neta líquida que queda en el bolsillo del inversor después de pagar absolutamente todos los gastos e impuestos anuales.</p>', unsafe_allow_html=True)
        
        labels = ['MODELO AIRBNB', 'RENTA TRADICIONAL']
        vals = [flujo_neto*12, utilidad_trad]
        fig_c = go.Figure([go.Bar(
            x=labels, y=vals, 
            marker_color=['#3fb950' if v > 0 else '#f85149' for v in vals],
            text=[f'S/. {v:,.0f}' for v in vals],
            textposition='inside', insidetextanchor='middle',
            textfont=dict(size=26, color='white', weight='bold', family=SYS_SANS)
        )])
        fig_c.update_layout(title="Utilidad neta anualizada líquida (S/.)", height=550, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family=SYS_SANS, color="white"))
        st.plotly_chart(fig_c, use_container_width=True)
        
        st.markdown('<p class="info-box" style="text-align:center;"><b>Relación de variables:</b> Mientras que Airbnb ofrece una mayor rentabilidad, conlleva una mayor gestión operativa. La Renta Tradicional es pasiva pero el tiempo de recuperación de capital es considerablemente mayor.</p>', unsafe_allow_html=True)

        st.markdown('<div class="footer-tip">🏁 <b>Dictamen final:</b> El modelo Airbnb es altamente recomendable para este perfil de activo debido al diferencial de flujo de caja libre generado.</div>', unsafe_allow_html=True)

# =========================================================
# MOTOR DE PDF (EXTENDED REPORT)
# =========================================================
def generate_master_pdf(d):
    pdf = FPDF()
    pdf.add_page()
    # Header
    pdf.set_fill_color(13, 17, 23); pdf.rect(0, 0, 210, 60, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", 'B', 18)
    pdf.cell(0, 20, "REPORTE DE AUDITORIA INMOBILIARIA PROFESIONAL", ln=True, align='C')
    pdf.set_font("Arial", '', 10); pdf.cell(0, 5, "CONSULTORIA ESPECIALIZADA: ING. JANCARLO MENDOZA", ln=True, align='C')
    pdf.cell(0, 5, f"FECHA: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align='C')
    
    pdf.ln(35); pdf.set_text_color(0, 0, 0)

    # Sección 1
    pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, "1. Datos del proyecto y capital inicial", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.multi_cell(0, 5, "Este documento detalla la viabilidad financiera para la adquisicion de un activo inmobiliario destinado a rentas cortas. Se considera un desembolso inicial que cubre la cuota inicial bancaria y el equipamiento premium para optimizar el ranking en plataformas digitales.")
    pdf.ln(3)
    rows = [["Item", "Valor proyectado"], ["Valor de la propiedad", f"S/. {d['val']:,.0f}"], ["Capital propio (20% inicial)", f"S/. {d['ini']:,.0f}"], ["Capex amoblado", f"S/. {d['inv_a']:,.0f}"], ["CASH-OUT TOTAL REQUERIDO", f"S/. {d['inv_t']:,.0f}"]]
    for r in rows:
        pdf.cell(100, 8, r[0], 1); pdf.cell(90, 8, r[1], 1, ln=True, align='R')

    # Sección 2
    pdf.ln(10); pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, "2. Analisis de flujo de caja y rentabilidad", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.multi_cell(0, 5, "Se proyecta un flujo neto tras deducir el servicio de la deuda (Capital + Intereses), gastos de mantenimiento del edificio, servicios y el impuesto cedular de primera categoria (5% sobre ingresos brutos).")
    pdf.ln(3)
    pdf.cell(0, 8, f"- Ingreso mensual bruto proyectado: S/. {d['bruto']:,.2f}", ln=True)
    pdf.cell(0, 8, f"- ROI anual estimado (Modelo Airbnb): {d['roi']:.2f}%", ln=True)
    pdf.cell(0, 8, f"- Tiempo estimado de recuperacion de capital: {d['pb']:.1f} años", ln=True)

    # Sección 3
    pdf.ln(10); pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, "3. Analisis comparativo y veredicto", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.multi_cell(0, 5, f"Al comparar ambos modelos, se observa un beneficio anual excedente de S/. {d['exc']:,.0f} a favor del modelo de rentas cortas. Esto representa una aceleracion patrimonial significativa. El inversor debe priorizar ubicaciones con alta demanda turistica para mantener estos ratios.")
    
    pdf.ln(15); pdf.set_font("Arial", 'I', 8)
    pdf.multi_cell(0, 4, "Nota: Los calculos son estimaciones basadas en datos actuales de mercado. Jancarlo Mendoza no se hace responsable por fluctuaciones economicas externas o cambios en las politicas de plataformas de terceros.")

    return pdf.output(dest='S').encode('latin-1')

if st.session_state.authenticated:
    st.write("---")
    if st.button("📥 Generar reporte técnico extendido (PDF)"):
        pdf_bytes = generate_master_pdf({
            "val": val_depa, "ini": inicial, "inv_a": inv_amoblado, "inv_t": inv_total,
            "bruto": ingreso_bruto, "roi": roi_airbnb, "pb": rec, "exc": ventaja_anual
        })
        st.download_button("Descargar Auditoría PDF", data=pdf_bytes, file_name=f"Auditoria_Inmobiliaria_JM.pdf")
