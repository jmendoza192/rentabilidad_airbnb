import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime

# =========================================================
# 0. CONFIGURACIÓN Y ESTILO DE BANCA PRIVADA
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
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
        
        html, body, [class*="st-"] {
            font-family: 'Inter', sans-serif;
            color: #f1f5f9;
        }

        .main { background-color: #0b0e14; }

        /* Títulos Minimalistas */
        .section-title { 
            margin-top: 45px; margin-bottom: 20px; color: #5c9dfa; 
            font-size: 1.1rem; font-weight: 400; letter-spacing: 1.5px;
            text-transform: uppercase; border-bottom: 1px solid #1e293b; padding-bottom: 12px;
        }

        /* Tarjetas con Marco Minimalista */
        .mini-card {
            border: 1px solid #1e293b; border-radius: 4px; padding: 22px;
            background-color: #0f172a; text-align: center; margin-bottom: 15px;
        }
        .label-card { color: #94a3b8; font-size: 0.7rem; letter-spacing: 0.8px; margin-bottom: 12px; font-weight: 400; text-transform: uppercase; }
        .val-pos { color: #60a5fa; font-size: 1.6rem; font-weight: 600; }
        .val-neg { color: #f87171; font-size: 1.6rem; font-weight: 600; }

        /* Notas Informativas */
        .info-box { 
            font-size: 0.8rem; color: #64748b; padding: 15px; 
            border-left: 1px solid #3b82f6; background-color: #111827; 
            margin: 12px 0; line-height: 1.6; font-weight: 300;
        }
        
        /* Tablas */
        .stTable { background-color: #0f172a; border-radius: 4px; overflow: hidden; }
        </style>
        """, unsafe_allow_html=True)

    # =========================================================
    # 1. SIDEBAR: ENTRADAS DE DATOS
    # =========================================================
    with st.sidebar:
        st.markdown("### 🛠️ Configuración")
        val_depa = st.number_input("Valor Inmueble (S/.)", value=250000)
        inv_amoblado = st.number_input("Inversión Amoblado (S/.)", value=25000)
        st.write("---")
        tcea = st.number_input("TCEA Bancaria %", value=9.5)
        plazo_años = st.selectbox("Plazo (Años)", [10, 15, 20, 25], index=2)
        st.write("---")
        tarifa_base = st.number_input("Tarifa Airbnb (S/.)", value=180)
        ocupacion_act = st.slider("Días Ocupados/Mes", 1, 30, 20)
        st.write("---")
        renta_trad = st.number_input("Alquiler Tradicional (S/.)", value=1800)

    # Lógica de Cálculos
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

    tabs = st.tabs(["01 ANÁLISIS DE FLUJOS", "02 PLUSVALÍA", "03 SENSIBILIDAD", "04 COMPARATIVA"])

    # =========================================================
    # PESTAÑA 1: FLUJOS
    # =========================================================
    with tabs[0]:
        st.markdown('<div class="section-title">Estructura de Capital e Ingresos</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="mini-card"><div class="label-card">Inicial Banco (20%)</div><div class="val-pos">S/. {inicial:,.0f}</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="mini-card"><div class="label-card">Amoblado</div><div class="val-pos">S/. {inv_amoblado:,.0f}</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="mini-card"><div class="label-card">Capital Expuesto</div><div class="val-pos">S/. {inv_total:,.0f}</div></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">Análisis Operativo Mensual</div>', unsafe_allow_html=True)
        c4, c5, c6, c7 = st.columns(4)
        with c4: st.markdown(f'<div class="mini-card"><div class="label-card">Ingreso Airbnb</div><div class="val-pos">S/. {ingreso_bruto:,.0f}</div></div>', unsafe_allow_html=True)
        with c5: st.markdown(f'<div class="mini-card"><div class="label-card">Cuota Banco</div><div class="val-neg">S/. -{cuota:,.0f}</div></div>', unsafe_allow_html=True)
        with c6: st.markdown(f'<div class="mini-card"><div class="label-card">Gastos + Imp.</div><div class="val-neg">S/. -{gastos_op:,.0f}</div></div>', unsafe_allow_html=True)
        with c7: st.markdown(f'<div class="mini-card"><div class="label-card">Utilidad Neta</div><div class="val-pos">S/. {flujo_neto:,.0f}</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">Retorno de Capital (Payback)</div>', unsafe_allow_html=True)
        años_pb = 25; meses = np.arange(0, años_pb*12+1); f_acum = [-inv_total]; rec = 0
        for m in meses[1:]:
            f_acum.append(f_acum[-1] + (flujo_neto if m <= plazo_años*12 else ingreso_bruto-gastos_op))
            if rec == 0 and f_acum[-1] >= 0: rec = m/12

        cp1, cp2 = st.columns([1, 2])
        with cp1:
            st.markdown(f'<div class="mini-card" style="border-color:#3b82f6;"><div class="label-card">Tiempo de Recuperación</div><div class="val-pos" style="font-size:2.2rem;">{rec:.1f} Años</div></div>', unsafe_allow_html=True)
            st.markdown('<div class="info-box">Indica el momento en que la operación devuelve el 100% del capital propio invertido.</div>', unsafe_allow_html=True)
        with cp2:
            fig_pb = go.Figure()
            fig_pb.add_trace(go.Scatter(x=meses/12, y=f_acum, fill='tozeroy', fillcolor='rgba(96, 165, 250, 0.1)', line=dict(color='#60a5fa', width=2)))
            fig_pb.update_layout(title="<b>CURVA DE RECUPERACIÓN PATRIMONIAL</b>", height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#94a3b8", size=10), margin=dict(t=40, l=0, r=0))
            st.plotly_chart(fig_pb, use_container_width=False)
            st.markdown('<div class="info-box"><b>Nota:</b> El gráfico muestra el flujo de caja acumulado. La zona sombreada representa el capital en riesgo.</div>', unsafe_allow_html=True)

    # =========================================================
    # PESTAÑA 2: PLUSVALÍA
    # =========================================================
    with tabs[1]:
        st.markdown('<div class="section-title">Análisis de Valorización y Equity</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">La plusvalía es el incremento del valor de mercado del activo. Se asume un entorno de crecimiento moderado en Lima Moderna.</div>', unsafe_allow_html=True)
        plus_slider = st.slider("Plusvalía Anual Estimada %", 0.0, 8.0, 4.0)
        
        c_p = st.columns(4)
        for i, a in enumerate([5, 10, 15, 20]):
            g = (val_depa * (1 + plus_slider/100)**a) - val_depa
            with c_p[i]: 
                st.markdown(f'<div class="mini-card"><div class="label-card">Plusvalía {a}A</div><div class="val-pos">S/. {g:,.0f}</div></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">Proyección de Patrimonio Real</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Visualización de cómo el valor de la propiedad sube mientras la deuda baja.</div>', unsafe_allow_html=True)
        años = np.arange(0, 26); v_mkt = [val_depa * (1+plus_slider/100)**a for a in años]
        eq = [v - (prestamo * (1 - a/plazo_años) if a < plazo_años else 0) for a, v in zip(años, v_mkt)]
        
        fig_p = go.Figure()
        fig_p.add_trace(go.Bar(x=años, y=v_mkt, name="Valor Mercado", marker_color='#1e293b'))
        fig_p.add_trace(go.Scatter(x=años, y=eq, name="Equity", fill='tozeroy', fillcolor='rgba(96, 165, 250, 0.1)', line=dict(color='#60a5fa', width=3)))
        fig_p.update_layout(title="<b>CRECIMIENTO DEL PATRIMONIO NETO</b>", height=450, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#94a3b8")
        st.plotly_chart(fig_p, use_container_width=True)

    # =========================================================
    # PESTAÑA 3: SENSIBILIDAD
    # =========================================================
    with tabs[2]:
        st.markdown('<div class="section-title">Pruebas de Estrés y Resiliencia</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Analice cómo cambia el ROI ante variaciones operativas. Los colores indican zonas de rentabilidad (Verde > 10%).</div>', unsafe_allow_html=True)
        
        def color_roi(val):
            color = '#f87171' if val < 5 else '#fbbf24' if val < 10 else '#4ade80'
            return f'background-color: {color}; color: #000; font-weight: bold;'

        # 1. Días
        st.subheader("1. Sensibilidad por Ocupación")
        cs1_t, cs1_g = st.columns([1, 1.8])
        d_range = [5, 10, 15, 20, 25, 30]
        roi_d = [((((tarifa_base*d*0.85) - cuota - mantenimiento - (tarifa_base*d*0.85*0.05))*12/inv_total)*100) for d in d_range]
        with cs1_t:
            st.write("<br><br>", unsafe_allow_html=True)
            df_d = pd.DataFrame({"Días": d_range, "ROI %": roi_d})
            st.table(df_d.style.map(color_roi, subset=['ROI %']).format({"ROI %": "{:.2f}%"}))
        with cs1_g:
            fig_d = go.Figure(go.Scatter(x=d_range, y=roi_d, mode='lines+markers', line=dict(color='#60a5fa', width=4)))
            fig_d.update_layout(title="<b>OCUPACIÓN VS ROI</b>", height=500, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#94a3b8")
            st.plotly_chart(fig_d, use_container_width=True)

        # 2. Tarifa
        st.subheader("2. Sensibilidad por Tarifa")
        cs2_t, cs2_g = st.columns([1, 1.8])
        t_range = list(range(int(tarifa_base)-40, int(tarifa_base)+60, 10))
        roi_t = [((((t*ocupacion_act*0.85) - cuota - mantenimiento - (t*ocupacion_act*0.85*0.05))*12/inv_total)*100) for t in t_range]
        with cs2_t:
            st.write("<br><br>", unsafe_allow_html=True)
            df_t = pd.DataFrame({"Tarifa S/.": t_range, "ROI %": roi_t})
            st.table(df_t.style.map(color_roi, subset=['ROI %']).format({"ROI %": "{:.2f}%"}))
        with cs2_g:
            fig_t = go.Figure(go.Scatter(x=t_range, y=roi_t, mode='lines+markers', line=dict(color='#60a5fa', width=4)))
            fig_t.update_layout(title="<b>TARIFA VS ROI</b>", height=500, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#94a3b8")
            st.plotly_chart(fig_t, use_container_width=True)

    # =========================================================
    # PESTAÑA 4: COMPARATIVA
    # =========================================================
    with tabs[3]:
        st.markdown('<div class="section-title">Diferencial de Modelos de Renta</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Comparativa directa de flujo neto anualizado tras gastos e impuestos.</div>', unsafe_allow_html=True)
        
        ventaja = (flujo_neto*12) - utilidad_trad
        cc1, cc2 = st.columns(2)
        with cc1: st.markdown(f'<div class="mini-card" style="border-color:#4ade80;"><div class="label-card">Ventaja Airbnb Anual</div><div class="val-pos" style="color:#4ade80;">S/. {ventaja:,.0f}</div></div>', unsafe_allow_html=True)
        with cc2: st.markdown(f'<div class="mini-card"><div class="label-card">ROI Delta</div><div class="val-pos">{roi_anual - (utilidad_trad*100/inv_total):.1f}%</div></div>', unsafe_allow_html=True)
        
        vals = [flujo_neto*12, utilidad_trad]
        fig_c = go.Figure([go.Bar(
            x=['<b>AIRBNB</b>', '<b>TRADICIONAL</b>'], y=vals, 
            marker_color=['#4ade80' if v > 0 else '#f87171' for v in vals],
            text=[f'<b>S/. {v:,.0f}</b>' for v in vals],
            textposition='inside', insidetextanchor='middle',
            textfont=dict(size=26, color='white', family='Inter')
        )])
        fig_c.update_layout(title="<b>CASH FLOW ANUAL NETO</b>", height=600, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#94a3b8")
        st.plotly_chart(fig_c, use_container_width=True)
        st.markdown('<div class="info-box">Este gráfico demuestra la superioridad del modelo de corta estancia en zonas de alta rotación turística.</div>', unsafe_allow_html=True)

# =========================================================
# MOTOR DE PDF (DENSIDAD DE AUDITORÍA)
# =========================================================
def generate_pdf_audit(d):
    pdf = FPDF()
    pdf.add_page()
    # Header
    pdf.set_fill_color(15, 23, 42); pdf.rect(0, 0, 210, 55, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", 'B', 20)
    pdf.cell(0, 20, "AUDITORIA DE INVERSION INMOBILIARIA", ln=True, align='C')
    pdf.set_font("Arial", '', 10); pdf.cell(0, 5, "ELABORADO POR: ING. JANCARLO MENDOZA", ln=True, align='C')
    pdf.cell(0, 5, f"LIMA, PERU | {datetime.now().strftime('%d/%m/%Y')}", ln=True, align='C')
    pdf.ln(30); pdf.set_text_color(0, 0, 0)

    # 1. Estrategia de Capital
    pdf.set_font("Arial", 'B', 12); pdf.set_text_color(59, 130, 246)
    pdf.cell(0, 10, "1. MEMORIA DE CAPITAL Y ESTRUCTURA FINANCIERA", ln=True)
    pdf.set_font("Arial", '', 9); pdf.set_text_color(50, 50, 50)
    pdf.multi_cell(0, 5, "El presente reporte técnico evalúa la viabilidad financiera de un activo inmobiliario. Se ha considerado una estructura de apalancamiento hipotecario estándar, priorizando el análisis del Cash-on-Cash ROI sobre el capital líquido desembolsado.")
    pdf.ln(3)
    
    rows = [["Componente", "Monto", "Detalle"],
            ["Valor Propiedad", f"S/. {d['val']:,.0f}", "Valor de adquisición"],
            ["Cuota Inicial", f"S/. {d['ini']:,.0f}", "Capital propio (20%)"],
            ["Inversión Capex", f"S/. {d['inv_a']:,.0f}", "Amoblado profesional"],
            ["TOTAL INVERTIDO", f"S/. {d['inv_t']:,.0f}", "Capital Total Expuesto"]]
    for r in rows:
        pdf.cell(60, 8, r[0], 1); pdf.cell(40, 8, r[1], 1); pdf.cell(90, 8, r[2], 1, ln=True)

    # 2. Análisis Operativo
    pdf.ln(8); pdf.set_font("Arial", 'B', 12); pdf.set_text_color(59, 130, 246)
    pdf.cell(0, 10, "2. PROYECCION OPERATIVA MENSUAL (AIRBNB)", ln=True)
    pdf.set_font("Arial", '', 9); pdf.set_text_color(50, 50, 50)
    pdf.multi_cell(0, 5, "La proyección operativa asume una gestión profesional de tarifas dinámicas. Se ha descontado la comisión de plataforma, impuestos de primera categoría y costos fijos de mantenimiento.")
    pdf.ln(2)
    ops = [["Ingresos Brutos", f"S/. {d['i_b']:,.0f}"], ["Cuota Bancaria", f"S/. -{d['cuo']:,.0f}"], ["Gasto Operativo", f"S/. -{d['gop']:,.0f}"], ["FLUJO NETO", f"S/. {d['f_n']:,.0f}"]]
    for r in ops:
        pdf.cell(90, 8, r[0], 1); pdf.cell(100, 8, r[1], 1, ln=True)

    # 3. Métricas de Valor
    pdf.ln(8); pdf.set_font("Arial", 'B', 12); pdf.set_text_color(59, 130, 246)
    pdf.cell(0, 10, "3. INDICADORES DE RENTABILIDAD Y PLUSVALIA", ln=True)
    pdf.set_font("Arial", '', 9); pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 7, f"- ROI Cash-on-Cash: {d['roi']:.2f}% Anual", ln=True)
    pdf.cell(0, 7, f"- Recuperacion de Inversion: {d['pb']:.1f} Años", ln=True)
    pdf.cell(0, 7, f"- Equity Estimado (Horizonte 10A): S/. {d['v10']:,.0f}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'I', 8)
    pdf.multi_cell(0, 4, "Este reporte es una herramienta de simulación basada en parámetros actuales de mercado. Los resultados pueden variar según el desempeño real de la propiedad y las condiciones macroeconómicas.")

    return pdf.output(dest='S').encode('latin-1')

if st.session_state.authenticated:
    st.write("---")
    if st.button("📥 DESCARGAR AUDITORIA TECNICA (PDF)"):
        v10_calc = (val_depa * (1 + plus_slider/100)**10) - val_depa
        pdf_b = generate_pdf_audit({
            "val": val_depa, "ini": inicial, "inv_a": inv_amoblado, "inv_t": inv_total,
            "i_b": ingreso_bruto, "cuo": cuota, "gop": gastos_op, "f_n": flujo_neto,
            "roi": roi_anual, "pb": rec, "v10": v10_calc
        })
        st.download_button("Guardar Reporte Auditoría", data=pdf_b, file_name=f"Auditoria_Mendoza_{datetime.now().strftime('%Y%m%d')}.pdf")
