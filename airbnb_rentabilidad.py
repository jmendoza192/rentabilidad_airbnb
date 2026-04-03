import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime

# =========================================================
# CONFIGURACIÓN DE ESTILO MINIMALISTA (AUDIT-STYLE)
# =========================================================
try:
    st.set_page_config(page_title="Auditoría Pro | Jancarlo Mendoza", layout="wide")
except:
    pass

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def check_password():
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
    # CSS: Tipografía Profesional y Marcos Minimalistas
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
        html, body, [class*="st-"] { font-family: 'Inter', sans-serif; }
        
        .main { background-color: #0b0e14; }
        
        /* Títulos Refinados */
        .section-title { 
            margin-top: 40px; margin-bottom: 15px; color: #5c9dfa; 
            font-size: 1.2rem; font-weight: 300; letter-spacing: 1px;
            text-transform: uppercase; border-bottom: 1px solid #1e293b; padding-bottom: 10px;
        }
        
        /* Tarjetas con Marco Minimalista */
        .mini-card {
            border: 1px solid #1e293b; border-radius: 4px; padding: 18px;
            background-color: #0f172a; text-align: center; margin-bottom: 12px;
        }
        .label-card { color: #94a3b8; font-size: 0.75rem; letter-spacing: 0.5px; margin-bottom: 10px; font-weight: 400; }
        .val-pos { color: #60a5fa; font-size: 1.5rem; font-weight: 600; }
        .val-neg { color: #f87171; font-size: 1.5rem; font-weight: 600; }
        
        /* Notas Informativas */
        .info-box { 
            font-size: 0.8rem; color: #64748b; padding: 15px; 
            border-left: 1px solid #3b82f6; background-color: #111827; 
            margin: 10px 0; line-height: 1.5; font-weight: 300;
        }
        </style>
        """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("Entradas Técnicas")
        val_depa = st.number_input("Valor Inmueble (S/.)", value=250000)
        inv_amoblado = st.number_input("Inversión Amoblado (S/.)", value=25000)
        st.write("---")
        tcea = st.number_input("TCEA Bancaria %", value=9.5)
        plazo_años = st.selectbox("Plazo (Años)", [10, 15, 20, 25], index=2)
        st.write("---")
        tarifa_base = st.number_input("Tarifa Airbnb (S/.)", value=180)
        ocupacion_act = st.slider("Ocupación (Días)", 1, 30, 20)
        st.write("---")
        renta_trad = st.number_input("Alquiler Tradicional (S/.)", value=1800)

    # CÁLCULOS
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
    roi_anual = (flujo_neto * 12 / inv_total) * 100
    utilidad_trad = (renta_trad - cuota - (val_depa*0.015/12) - (renta_trad*0.05)) * 12

    tabs = st.tabs(["01 FLUJOS", "02 PLUSVALÍA", "03 SENSIBILIDAD", "04 COMPARATIVA"])

    # --------------------------------------------------------- PESTAÑA 1
    with tabs[0]:
        st.markdown('<div class="section-title">Estructura de Inversión Inicial</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="mini-card"><div class="label-card">Inicial Banco (20%)</div><div class="val-pos">S/. {inicial:,.0f}</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="mini-card"><div class="label-card">Amoblado y Equipamiento</div><div class="val-pos">S/. {inv_amoblado:,.0f}</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="mini-card"><div class="label-card">Capital Total Expuesto</div><div class="val-pos">S/. {inv_total:,.0f}</div></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">Análisis Operativo Mensual</div>', unsafe_allow_html=True)
        c4, c5, c6, c7 = st.columns(4)
        with c4: st.markdown(f'<div class="mini-card"><div class="label-card">Renta Bruta (Airbnb)</div><div class="val-pos">S/. {ingreso_bruto:,.0f}</div></div>', unsafe_allow_html=True)
        with c5: st.markdown(f'<div class="mini-card"><div class="label-card">Servicio de Deuda</div><div class="val-neg">S/. -{cuota:,.0f}</div></div>', unsafe_allow_html=True)
        with c6: st.markdown(f'<div class="mini-card"><div class="label-card">Gastos Operativos</div><div class="val-neg">S/. -{gastos_op:,.0f}</div></div>', unsafe_allow_html=True)
        with c7: st.markdown(f'<div class="mini-card"><div class="label-card">Utilidad Neta (Cash Flow)</div><div class="val-pos">S/. {flujo_neto:,.0f}</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">Recuperación de Capital</div>', unsafe_allow_html=True)
        # Lógica Payback
        años_pb = 25; meses = np.arange(0, años_pb*12+1); f_acum = [-inv_total]; rec = 0
        for m in meses[1:]:
            f_acum.append(f_acum[-1] + (flujo_neto if m <= plazo_años*12 else ingreso_bruto-gastos_op))
            if rec == 0 and f_acum[-1] >= 0: rec = m/12

        cp1, cp2 = st.columns([1, 1.8])
        with cp1:
            st.markdown(f'<div class="mini-card" style="border-color:#3b82f6;"><div class="label-card">Payback Proyectado</div><div class="val-pos" style="font-size:2.2rem;">{rec:.1f} Años</div></div>', unsafe_allow_html=True)
            st.markdown('<div class="info-box"><b>Nota:</b> El Payback es el umbral de seguridad. Indica cuándo el activo ha devuelto cada sol invertido de su bolsillo, eliminando el riesgo de capital inicial.</div>', unsafe_allow_html=True)
        with cp2:
            fig_pb = go.Figure()
            fig_pb.add_trace(go.Scatter(x=meses/12, y=f_acum, fill='tozeroy', fillcolor='rgba(59, 130, 246, 0.1)', line=dict(color='#3b82f6', width=2)))
            fig_pb.update_layout(title="<b>PROYECCIÓN DE FLUJO ACUMULADO</b>", height=350, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#94a3b8", size=10), margin=dict(t=50))
            st.plotly_chart(fig_pb, use_container_width=True)
            st.markdown('<div class="info-box">Visualización de la salud financiera a largo plazo. El cruce con el eje cero marca el éxito del retorno de inversión.</div>', unsafe_allow_html=True)

    # --------------------------------------------------------- PESTAÑA 2
    with tabs[1]:
        st.markdown('<div class="section-title">Valorización del Activo y Equity</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">La plusvalía es el "motor invisible" de la riqueza inmobiliaria. Se estima basada en el crecimiento histórico de Lima Moderna.</div>', unsafe_allow_html=True)
        plus_slider = st.slider("Plusvalía Anual Estimada %", 0.0, 8.0, 4.0)
        
        c_p = st.columns(4)
        for i, a in enumerate([5, 10, 15, 20]):
            g = (val_depa * (1 + plus_slider/100)**a) - val_depa
            with c_p[i]: 
                st.markdown(f'<div class="mini-card"><div class="label-card">Plusvalía {a}A</div><div class="val-pos">S/. {g:,.0f}</div></div>', unsafe_allow_html=True)
                st.markdown(f'<p style="font-size:0.7rem; color:#64748b; text-align:center;">Incremento bruto est.</p>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">Gráfico de Crecimiento Patrimonial</div>', unsafe_allow_html=True)
        años = np.arange(0, 26); v_mkt = [val_depa * (1+plus_slider/100)**a for a in años]
        eq = [v - (prestamo * (1 - a/plazo_años) if a < plazo_años else 0) for a, v in zip(años, v_mkt)]
        
        fig_p = go.Figure()
        fig_p.add_trace(go.Bar(x=años, y=v_mkt, name="Valor Mercado", marker_color='#1e293b'))
        fig_p.add_trace(go.Scatter(x=años, y=eq, name="Equity (Riqueza)", fill='tozeroy', fillcolor='rgba(96, 165, 250, 0.1)', line=dict(color='#60a5fa', width=3)))
        fig_p.update_layout(title="<b>VALOR DE MERCADO VS DEUDA</b>", height=450, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#94a3b8")
        st.plotly_chart(fig_p, use_container_width=True)
        st.markdown('<div class="info-box"><b>Nota:</b> El Equity es el valor neto que le pertenece después de liquidar la deuda bancaria en cualquier año dado.</div>', unsafe_allow_html=True)

    # --------------------------------------------------------- PESTAÑA 3
    with tabs[2]:
        st.markdown('<div class="section-title">Análisis de Resiliencia Operativa</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Este análisis determina la sensibilidad del ROI ante cambios en el mercado. Un modelo robusto mantiene ROI positivo incluso en escenarios pesimistas.</div>', unsafe_allow_html=True)
        
        # Semaforo Function
        def color_roi(val):
            color = '#f87171' if val < 5 else '#fbbf24' if val < 10 else '#4ade80'
            return f'background-color: {color}; color: black; font-weight: bold;'

        # Sensibilidad 1: Días
        st.subheader("1. Variación de Ocupación (Días/Mes)")
        st.markdown('<div class="info-box">Evalúa el impacto de la vacancia estacional.</div>', unsafe_allow_html=True)
        cs1_t, cs1_g = st.columns([1, 1.5])
        d_range = [5, 10, 15, 20, 25, 30]
        roi_d = [((((tarifa_base*d*0.85) - cuota - mantenimiento - (tarifa_base*d*0.85*0.05))*12/inv_total)*100) for d in d_range]
        with cs1_t:
            df_d = pd.DataFrame({"Días": d_range, "ROI %": roi_d})
            st.table(df_d.style.applymap(color_roi, subset=['ROI %']).format({"ROI %": "{:.2f}%"}))
        with cs1_g:
            fig_d = go.Figure(go.Scatter(x=d_range, y=roi_d, mode='lines+markers', line=dict(color='#60a5fa', width=4)))
            fig_d.update_layout(title="<b>SENSIBILIDAD: DÍAS VS ROI</b>", height=550, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#94a3b8")
            st.plotly_chart(fig_d, use_container_width=True)

        # Sensibilidad 2: Tarifa
        st.subheader("2. Variación de Tarifa (S/. Noche)")
        st.markdown('<div class="info-box">Evalúa la competitividad de precios frente al entorno.</div>', unsafe_allow_html=True)
        cs2_t, cs2_g = st.columns([1, 1.5])
        t_range = list(range(int(tarifa_base)-40, int(tarifa_base)+60, 10))
        roi_t = [((((t*ocupacion_act*0.85) - cuota - mantenimiento - (t*ocupacion_act*0.85*0.05))*12/inv_total)*100) for t in t_range]
        with cs2_t:
            df_t = pd.DataFrame({"Tarifa S/.": t_range, "ROI %": roi_t})
            st.table(df_t.style.applymap(color_roi, subset=['ROI %']).format({"ROI %": "{:.2f}%"}))
        with cs2_g:
            fig_t = go.Figure(go.Scatter(x=t_range, y=roi_t, mode='lines+markers', line=dict(color='#60a5fa', width=4)))
            fig_t.update_layout(title="<b>SENSIBILIDAD: TARIFA VS ROI</b>", height=550, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#94a3b8")
            st.plotly_chart(fig_t, use_container_width=True)

    # --------------------------------------------------------- PESTAÑA 4
    with tabs[3]:
        st.markdown('<div class="section-title">Análisis Comparativo de Estrategias</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Comparativa final entre la renta de corta estancia (Airbnb) y la renta tradicional anualizada.</div>', unsafe_allow_html=True)
        ventaja = (flujo_neto*12) - utilidad_trad
        
        cc1, cc2 = st.columns(2)
        with cc1: st.markdown(f'<div class="mini-card" style="border-color:#4ade80;"><div class="label-card">Ventaja Anual Airbnb</div><div class="val-pos" style="color:#4ade80;">S/. {ventaja:,.0f}</div></div>', unsafe_allow_html=True)
        with cc2: st.markdown(f'<div class="mini-card"><div class="label-card">Delta ROI (%)</div><div class="val-pos">{roi_anual - (utilidad_trad*100/inv_total):.1f}%</div></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="info-box">El gráfico a continuación muestra la utilidad líquida anual después de todos los gastos e impuestos.</div>', unsafe_allow_html=True)
        
        labels = ['<b>AIRBNB</b>', '<b>TRADICIONAL</b>']
        vals = [flujo_neto*12, utilidad_trad]
        fig_c = go.Figure([go.Bar(
            x=labels, y=vals, 
            marker_color=['#4ade80' if v > 0 else '#f87171' for v in vals],
            text=[f'<b>S/. {v:,.0f}</b>' for v in vals],
            textposition='inside', insidetextanchor='middle',
            textfont=dict(size=24, color='white')
        )])
        fig_c.update_layout(title="<b>UTILIDAD NETA ANUALIZADA</b>", height=600, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#94a3b8")
        st.plotly_chart(fig_c, use_container_width=True)

# =========================================================
# MOTOR DE PDF (DENSIDAD INFORMATIVA AUDITORÍA)
# =========================================================

def generate_pdf_audit(d):
    pdf = FPDF()
    pdf.add_page()
    # Header Audit
    pdf.set_fill_color(15, 23, 42); pdf.rect(0, 0, 210, 50, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", 'B', 20)
    pdf.cell(0, 20, "AUDITORIA DE FACTIBILIDAD INMOBILIARIA", ln=True, align='C')
    pdf.set_font("Arial", '', 10); pdf.cell(0, 5, "ANALISIS ELABORADO POR: ING. JANCARLO MENDOZA", ln=True, align='C')
    pdf.cell(0, 5, f"LIMA, PERU | GENERADO EL: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align='C')
    pdf.ln(25); pdf.set_text_color(0, 0, 0)

    # Bloque 1
    pdf.set_font("Arial", 'B', 12); pdf.set_text_color(59, 130, 246)
    pdf.cell(0, 10, "1. RESUMEN EJECUTIVO DE INVERSION", ln=True)
    pdf.set_font("Arial", '', 9); pdf.set_text_color(50, 50, 50)
    txt = ("Se ha evaluado un activo inmobiliario bajo un esquema de renta dinamica. "
           "La estructura de capital requiere un desembolso inicial del 20% del valor comercial, "
           "sumado a un CAPEX de habilitacion operativa (amoblado). El apalancamiento bancario "
           "se ha calculado sobre un LTV del 80% con amortizacion constante.")
    pdf.multi_cell(0, 5, txt); pdf.ln(3)

    # Tabla 1
    pdf.set_font("Arial", 'B', 9)
    res = [["Concepto", "Monto (S/.)", "Nota Técnica"],
           ["Valor del Activo", f"{d['val']:,.0f}", "Base imponible"],
           ["Capital Propio", f"{d['ini']:,.0f}", "Equity inicial (20%)"],
           ["Inversion Amoblado", f"{d['inv_a']:,.0f}", "Equipamiento Full"],
           ["TOTAL CASH-OUT", f"{d['inv_t']:,.0f}", "Inversion Liquida Real"]]
    for r in res:
        pdf.cell(60, 8, r[0], 1); pdf.cell(40, 8, r[1], 1); pdf.cell(90, 8, r[2], 1, ln=True)

    # Bloque 2
    pdf.ln(8); pdf.set_font("Arial", 'B', 12); pdf.set_text_color(59, 130, 246)
    pdf.cell(0, 10, "2. PROYECCION DE FLUJO DE CAJA OPERATIVO", ln=True)
    pdf.set_font("Arial", '', 9); pdf.set_text_color(50, 50, 50)
    pdf.multi_cell(0, 5, "El analisis de flujo de caja libre (Free Cash Flow to Equity) considera ingresos netos de plataforma, impuestos de ley y gastos de mantenimiento preventivo.")
    pdf.ln(2)
    ops = [["Ingresos Brutos Airbnb", f"{d['i_b']:,.0f}"], ["Servicio de Deuda", f"-{d['cuo']:,.0f}"], ["Gasto Operativo + Imp.", f"-{d['gop']:,.0f}"], ["UTILIDAD NETA MENSUAL", f"{d['f_n']:,.0f}"]]
    for r in ops:
        pdf.cell(90, 8, r[0], 1); pdf.cell(100, 8, r[1], 1, ln=True)

    # Bloque 3
    pdf.ln(8); pdf.set_font("Arial", 'B', 12); pdf.set_text_color(59, 130, 246)
    pdf.cell(0, 10, "3. CONCLUSIONES DE RENTABILIDAD Y RIESGO", ln=True)
    pdf.set_font("Arial", '', 9); pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 7, f"- ROI Cash-on-Cash Proyectado: {d['roi']:.2f}% Anual", ln=True)
    pdf.cell(0, 7, f"- Periodo de Recuperacion (Payback): {d['pb']:.1f} Años", ln=True)
    pdf.cell(0, 7, f"- Plusvalia Estimada (Horizonte 10A): S/. {d['v10']:,.0f}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'I', 8)
    pdf.multi_cell(0, 4, "Nota: Los calculos aqui presentados son proyecciones basadas en data de mercado actual. "
                         "No constituyen una garantia de rentabilidad futura, pero sirven como guia tecnica "
                         "para la toma de decisiones de inversion.")

    return pdf.output(dest='S').encode('latin-1')

if st.session_state.authenticated:
    st.write("---")
    if st.button("📥 GENERAR AUDITORIA TECNICA PDF"):
        v10_calc = (val_depa * (1 + plus_slider/100)**10) - val_depa
        pdf_bytes = generate_pdf_audit({
            "val": val_depa, "ini": inicial, "inv_a": inv_amoblado, "inv_t": inv_total,
            "i_b": ingreso_bruto, "cuo": cuota, "gop": gastos_op, "f_n": flujo_neto,
            "roi": roi_anual, "pb": rec, "v10": v10_calc
        })
        st.download_button("Descargar Reporte Profesional", data=pdf_bytes, file_name=f"Auditoria_JM_{datetime.now().strftime('%Y%m%d')}.pdf")
