import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime

# =========================================================
# 0. CONFIGURACIÓN Y ESTÉTICA "LUXURY AUDIT"
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
    # CSS: Tipografías Slim/Normal, Colores Tenues y Diseño de Inputs
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100;300;400;600&display=swap');
        
        html, body, [class*="st-"] { font-family: 'Inter', sans-serif !important; }
        
        /* Estilo Slim para Inputs y Widgets */
        .stNumberInput input, .stSelectbox div, .stSlider div {
            font-family: 'Inter', sans-serif !important;
            font-weight: 300 !important;
            background-color: #1a1d23 !important;
            color: #f1f5f9 !important;
        }
        
        .stNumberInput label, .stSelectbox label, .stSlider label {
            font-weight: 100 !important;
            letter-spacing: 1px;
            color: #94a3b8 !important;
            text-transform: uppercase;
            font-size: 0.8rem;
        }

        .main { background-color: #0f1115; }

        /* Títulos Slim con Línea Inferior */
        .section-title { 
            margin-top: 40px; color: #f1f5f9; 
            font-size: 1.3rem; font-weight: 100; letter-spacing: 3px;
            text-transform: uppercase; border-bottom: 1px solid #1e293b; padding-bottom: 12px;
        }
        
        /* Tarjetas con Colores Tenues y Marcos */
        .card-base {
            border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 22px;
            text-align: center; margin-bottom: 15px;
        }
        .card-slate { background-color: rgba(30, 41, 59, 0.4); }   
        .card-indigo { background-color: rgba(49, 46, 129, 0.2); } 
        .card-emerald { background-color: rgba(6, 78, 59, 0.2); }    
        .card-dark { background-color: rgba(17, 24, 39, 0.6); } 

        .label-card { color: #94a3b8; font-size: 0.75rem; font-weight: 300; text-transform: uppercase; margin-bottom: 10px; }
        .val-pos { color: #60a5fa; font-size: 1.8rem; font-weight: 600; }
        .val-neg { color: #f87171; font-size: 1.8rem; font-weight: 600; }
        
        /* Cajas Informativas */
        .info-box { 
            font-size: 0.85rem; color: #94a3b8; padding: 15px; 
            background-color: #161b22; border-radius: 6px; 
            margin: 10px 0; border: 1px solid #30363d; font-weight: 300;
        }
        .footer-tip {
            background-color: #064e3b; color: #d1fae5; padding: 18px;
            border-radius: 8px; margin-top: 25px; font-size: 0.9rem; border-left: 4px solid #10b981;
        }
        </style>
        """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("🏢 Datos del Activo")
        val_depa = st.number_input("Precio Venta (S/.)", value=250000)
        inv_amoblado = st.number_input("Equipamiento Capex (S/.)", value=25000)
        st.write("---")
        tcea = st.number_input("TCEA Bancaria (%)", value=9.5)
        plazo_años = st.selectbox("Plazo del Crédito (Años)", [10, 15, 20, 25], index=2)
        st.write("---")
        tarifa_base = st.number_input("Tarifa Airbnb (S/.)", value=180)
        ocupacion_act = st.slider("Ocupación (Días)", 1, 30, 20)
        st.write("---")
        renta_trad = st.number_input("Renta Tradicional (S/.)", value=1800)

    # LÓGICA DE AUDITORÍA
    inicial = val_depa * 0.20
    inv_total = inicial + inv_amoblado
    prestamo = val_depa - inicial
    tem = (1 + tcea/100)**(1/12) - 1
    cuota = prestamo * (tem * (1 + tem)**(plazo_años*12)) / ((1 + tem)**(plazo_años*12) - 1)
    mantenimiento = (val_depa * 0.03) / 12
    ingreso_bruto = tarifa_base * ocupacion_act * 0.85 # Neto de comisión plataforma
    impuesto = ingreso_bruto * 0.05
    gastos_op = mantenimiento + impuesto
    flujo_neto = ingreso_bruto - cuota - gastos_op
    roi_anual = (flujo_neto * 12 / inv_total) * 100
    utilidad_trad = (renta_trad - cuota - (val_depa*0.015/12) - (renta_trad*0.05)) * 12

    tabs = st.tabs(["💎 CAPITAL Y FLUJO", "📈 CRECIMIENTO", "⚖️ SENSIBILIDAD", "🔄 COMPARATIVA TRADICIONAL VS AIRBNB"])

    # --------------------------------------------------------- PESTAÑA 1
    with tabs[0]:
        st.markdown('<div class="section-title">📊 Estructura de Capital e Ingresos</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">ℹ️ Esta sección detalla el capital propio necesario (Equity) y la inversión inicial en mobiliario para habilitar el activo.</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="card-base card-slate"><div class="label-card">Cuota Inicial (20%)</div><div class="val-pos">S/. {inicial:,.0f}</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="card-base card-slate"><div class="label-card">Inversión Amoblado</div><div class="val-pos">S/. {inv_amoblado:,.0f}</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="card-base card-indigo"><div class="label-card">Inversión Total Cash-Out</div><div class="val-pos">S/. {inv_total:,.0f}</div></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">💸 Análisis Operativo Mensual</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">ℹ️ Resumen de ingresos y egresos recurrentes. Los números en azul representan flujo a favor y en rojo las obligaciones.</div>', unsafe_allow_html=True)
        c4, c5, c6, c7 = st.columns(4)
        with c4: st.markdown(f'<div class="card-base card-dark"><div class="label-card">Ingreso Airbnb Bruto</div><div class="val-pos">S/. {ingreso_bruto:,.0f}</div></div>', unsafe_allow_html=True)
        with c5: st.markdown(f'<div class="card-base card-dark"><div class="label-card">Cuota Bancaria</div><div class="val-neg">S/. -{cuota:,.0f}</div></div>', unsafe_allow_html=True)
        with c6: st.markdown(f'<div class="card-base card-dark"><div class="label-card">Costos Operativos</div><div class="val-neg">S/. -{gastos_op:,.0f}</div></div>', unsafe_allow_html=True)
        with c7: st.markdown(f'<div class="card-base card-emerald"><div class="label-card">Cash Flow Neto</div><div class="val-pos">S/. {flujo_neto:,.0f}</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">⏱️ Retorno de Capital (Payback)</div>', unsafe_allow_html=True)
        años_pb = 25; meses = np.arange(0, años_pb*12+1); f_acum = [-inv_total]; rec = 0
        for m in meses[1:]:
            f_acum.append(f_acum[-1] + (flujo_neto if m <= plazo_años*12 else ingreso_bruto-gastos_op))
            if rec == 0 and f_acum[-1] >= 0: rec = m/12

        cp1, cp2 = st.columns([1, 1.8])
        with cp1:
            st.markdown(f'<div class="card-base card-indigo" style="border: 2px solid #6366f1;"><div class="label-card">Tiempo de Recuperación</div><div class="val-pos" style="font-size:2.6rem;">{rec:.1f} Años</div></div>', unsafe_allow_html=True)
            st.markdown('<div class="info-box">El Payback mide cuántos años le tomará al flujo neto del departamento devolverle cada sol de su inversión inicial.</div>', unsafe_allow_html=True)
        with cp2:
            fig_pb = go.Figure()
            fig_pb.add_trace(go.Scatter(x=meses/12, y=f_acum, fill='tozeroy', fillcolor='rgba(96, 165, 250, 0.05)', line=dict(color='#60a5fa', width=2)))
            fig_pb.update_layout(title="<b>CURVA DE RECUPERACIÓN PATRIMONIAL ACUMULADA</b>", height=320, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#94a3b8", size=10), margin=dict(t=50, l=0, r=0))
            st.plotly_chart(fig_pb, use_container_width=True)
            st.markdown('<div class="info-box">Gráfico: El punto donde la curva cruza el eje 0 marca el fin del riesgo de capital.</div>', unsafe_allow_html=True)

        st.markdown('<div class="footer-tip">💡 <b>TIP FINANCIERO:</b> Para acelerar el Payback, intente realizar abonos a capital en su cuota hipotecaria usando el excedente anual. Esto reduce intereses y años de deuda drásticamente.</div>', unsafe_allow_html=True)

    # --------------------------------------------------------- PESTAÑA 2
    with tabs[1]:
        st.markdown('<div class="section-title">🏔️ Valorización Patrimonial (Equity)</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Nota: La riqueza inmobiliaria se compone de flujo de caja + plusvalía (apreciación del valor del m2 en el tiempo).</div>', unsafe_allow_html=True)
        plus_slider = st.slider("Plusvalía Anual Estimada (%)", 0.0, 10.0, 4.0)
        
        c_p = st.columns(4)
        for i, a in enumerate([5, 10, 15, 20]):
            ganancia = (val_depa * (1 + plus_slider/100)**a) - val_depa
            with c_p[i]: 
                st.markdown(f'<div class="card-base card-slate"><div class="label-card">Plusvalía a {a}A 📈</div><div class="val-pos">S/. {ganancia:,.0f}</div></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">📊 Crecimiento del Valor de Mercado vs Saldo Deuda</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Este gráfico visualiza cómo el "Equity" (su riqueza real) se expande a medida que la propiedad sube de valor y la deuda bancaria se extingue.</div>', unsafe_allow_html=True)
        años = np.arange(0, 26); v_mkt = [val_depa * (1+plus_slider/100)**a for a in años]
        eq = [v - (prestamo * (1 - a/plazo_años) if a < plazo_años else 0) for a, v in zip(años, v_mkt)]
        
        fig_p = go.Figure()
        fig_p.add_trace(go.Bar(x=años, y=v_mkt, name="Valor Propiedad", marker_color='#1e293b'))
        fig_p.add_trace(go.Scatter(x=años, y=eq, name="Patrimonio Neto (Equity)", fill='tozeroy', fillcolor='rgba(96, 165, 250, 0.1)', line=dict(color='#60a5fa', width=3)))
        fig_p.update_layout(title="<b>EVOLUCIÓN PATRIMONIAL A LARGO PLAZO</b>", height=450, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#94a3b8")
        st.plotly_chart(fig_p, use_container_width=True)
        
        st.markdown('<div class="footer-tip">📈 <b>TIP OPERATIVO:</b> En distritos consolidados, la plusvalía actúa como un "ahorro forzoso". Incluso con un Cash Flow neutro, usted está ganando riqueza vía apreciación del activo.</div>', unsafe_allow_html=True)

    # --------------------------------------------------------- PESTAÑA 3
    with tabs[2]:
        st.markdown('<div class="section-title">🛡️ Escenarios de Sensibilidad y Resiliencia</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">ℹ️ Análisis de riesgo: Identifique qué tan sensible es su ROI ante variaciones en la demanda o el precio del mercado.</div>', unsafe_allow_html=True)
        
        def color_roi(val):
            color = '#f87171' if val < 5 else '#fbbf24' if val < 10 else '#4ade80'
            return f'background-color: {color}; color: #000; font-weight: bold;'

        # 1. Sensibilidad por Días
        st.subheader("📍 Impacto de la Ocupación Mensual")
        st.markdown('<div class="info-box">Relación entre los días que el departamento está rentado y el retorno sobre su capital propio.</div>', unsafe_allow_html=True)
        c_s1_t, c_s1_g = st.columns([1, 1.8], gap="large")
        d_range = [5, 10, 15, 20, 25, 30]
        roi_d = [((((tarifa_base*d*0.85) - cuota - mantenimiento - (tarifa_base*d*0.85*0.05))*12/inv_total)*100) for d in d_range]
        with c_s1_t:
            df_d = pd.DataFrame({"Días/Mes": d_range, "ROI Anual %": roi_d})
            st.table(df_d.style.map(color_roi, subset=['ROI Anual %']).format({"ROI Anual %": "{:.2f}%"}))
        with c_s1_g:
            fig_d = go.Figure(go.Scatter(x=d_range, y=roi_d, mode='lines+markers', line=dict(color='#60a5fa', width=4), marker=dict(size=10)))
            fig_d.update_layout(height=500, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#94a3b8")
            st.plotly_chart(fig_d, use_container_width=True)

        # 2. Sensibilidad por Tarifa
        st.subheader("💰 Impacto de la Tarifa Noche (S/.)")
        st.markdown('<div class="info-box">Variación del ROI según el precio promedio diario (ADR) que logre colocar en la plataforma.</div>', unsafe_allow_html=True)
        c_s2_t, c_s2_g = st.columns([1, 1.8], gap="large")
        t_range = list(range(int(tarifa_base)-40, int(tarifa_base)+60, 10))
        roi_t = [((((t*ocupacion_act*0.85) - cuota - mantenimiento - (t*ocupacion_act*0.85*0.05))*12/inv_total)*100) for t in t_range]
        with c_s2_t:
            df_t = pd.DataFrame({"Tarifa S/.": t_range, "ROI Anual %": roi_t})
            st.table(df_t.style.map(color_roi, subset=['ROI Anual %']).format({"ROI Anual %": "{:.2f}%"}))
        with c_s2_g:
            fig_t = go.Figure(go.Scatter(x=t_range, y=roi_t, mode='lines+markers', line=dict(color='#34d399', width=4), marker=dict(size=10)))
            fig_t.update_layout(height=500, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#94a3b8")
            st.plotly_chart(fig_t, use_container_width=True)

        st.markdown('<div class="footer-tip">⚠️ <b>TIP DE RIESGO:</b> Identifique su "Punto de Equilibrio". En este modelo, con menos de 10 días de ocupación, el inmueble deja de autofinanciarse.</div>', unsafe_allow_html=True)

    # --------------------------------------------------------- PESTAÑA 4
    with tabs[3]:
        st.markdown('<div class="section-title">🏁 Comparativa: Renta Tradicional vs Airbnb</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">ℹ️ Análisis final para decidir el modelo de gestión. El modelo Airbnb ofrece mayor flujo pero requiere gestión operativa.</div>', unsafe_allow_html=True)
        
        ventaja_anual = (flujo_neto * 12) - utilidad_trad
        tir_adicional = (ventaja_anual / inv_total) * 100
        
        cc1, cc2 = st.columns(2)
        with cc1: st.markdown(f'<div class="card-base card-emerald"><div class="label-card">Excedente Anual Airbnb 🏆</div><div class="val-pos" style="color:#4ade80;">S/. {ventaja_anual:,.0f}</div></div>', unsafe_allow_html=True)
        with cc2: st.markdown(f'<div class="card-base card-indigo"><div class="label-card">+TIR Adicional Airbnb 🚀</div><div class="val-pos">+{tir_adicional:.2f}%</div></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="info-box">Comparativa visual del Cash Flow Anual disponible después de impuestos y servicio de deuda.</div>', unsafe_allow_html=True)
        
        labels = ['<b>MODELO AIRBNB</b>', '<b>RENTA ANUAL</b>']
        vals = [flujo_neto*12, utilidad_trad]
        fig_c = go.Figure([go.Bar(
            x=labels, y=vals, 
            marker_color=['#10b981' if v > 0 else '#ef4444' for v in vals],
            text=[f'S/. {v:,.0f}' for v in vals],
            textposition='inside', insidetextanchor='middle',
            textfont=dict(size=28, color='white', family='Inter')
        )])
        fig_c.update_layout(title="<b>UTILIDAD NETA ANUALIZADA LÍQUIDA</b>", height=600, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#94a3b8")
        st.plotly_chart(fig_c, use_container_width=True)
        
        st.markdown('<div class="info-box" style="text-align:justify;"><b>Análisis de Variables:</b> La barra verde (Airbnb) representa el ingreso dinámico sujeto a estacionalidad turística. La barra roja (Tradicional) representa un ingreso estable pero limitado por el mercado de alquiler local. La relación entre ambas muestra el "premio por gestión" que usted recibe al operar el inmueble de forma activa.</div>', unsafe_allow_html=True)

        st.markdown('<div class="footer-tip">🏁 <b>DICTAMEN FINAL:</b> Si el excedente anual cubre más del 20% de su cuota inicial anualizada, el modelo de corta estancia es la opción financieramente superior.</div>', unsafe_allow_html=True)

# =========================================================
# MOTOR DE PDF (DENSIDAD INFORMATIVA EXTREMA)
# =========================================================
def generate_master_pdf(d):
    pdf = FPDF()
    pdf.add_page()
    # Header Audit
    pdf.set_fill_color(15, 23, 42); pdf.rect(0, 0, 210, 55, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", 'B', 18)
    pdf.cell(0, 20, "AUDITORIA TECNICA DE FACTIBILIDAD INMOBILIARIA", ln=True, align='C')
    pdf.set_font("Arial", '', 10); pdf.cell(0, 5, "ELABORADO POR: ING. JANCARLO MENDOZA - CONSULTOR RE", ln=True, align='C')
    pdf.cell(0, 5, f"LIMA, PERU | REPORTE EMITIDO: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align='C')
    pdf.ln(35); pdf.set_text_color(0, 0, 0)

    # Bloque 1: Ingeniería de Capital
    pdf.set_font("Arial", 'B', 12); pdf.set_text_color(59, 130, 246)
    pdf.cell(0, 10, "1. MEMORIA ANALITICA DE INVERSION (EQUITY)", ln=True)
    pdf.set_font("Arial", '', 9); pdf.set_text_color(40, 40, 40)
    pdf.multi_cell(0, 5, "Este informe detalla la viabilidad del activo inmobiliario considerando un apalancamiento hipotecario estándar. La inversión total incluye la cuota inicial y el mobiliario necesario para la operación turística.")
    pdf.ln(2)
    rows = [["CONCEPTO ANALIZADO", "VALOR (S/.)", "TIPO DE FLUJO"],
            ["Valor Adquisicion Inmueble", f"{d['val']:,.0f}", "Activo Fijo"],
            ["Aporte Capital Propio (20%)", f"{d['ini']:,.0f}", "Equity Inicial"],
            ["Capex Equipamiento", f"{d['inv_a']:,.0f}", "Gasto de Capital"],
            ["INVERSION REAL TOTAL", f"{d['inv_t']:,.0f}", "CASH-OUT"]]
    for r in rows:
        pdf.cell(65, 8, r[0], 1); pdf.cell(35, 8, r[1], 1); pdf.cell(90, 8, r[2], 1, ln=True)

    # Bloque 2: Operación
    pdf.ln(8); pdf.set_font("Arial", 'B', 12); pdf.set_text_color(59, 130, 246)
    pdf.cell(0, 10, "2. PROYECCION DE FLUJO DE CAJA MENSUAL (AIRBNB)", ln=True)
    pdf.set_font("Arial", '', 9)
    pdf.multi_cell(0, 5, f"Se ha proyectado un escenario operativo basado en una ocupacion de {d['occ']:.1f}%. El flujo libre considera el pago de cuotas bancarias, mantenimiento del edificio e impuestos de SUNAT.")
    pdf.ln(2)
    ops = [["Ingresos Netos Estimados (Airbnb)", f"S/. {d['i_b']:,.0f}"], ["Cuota de Servicio de Deuda", f"S/. -{d['cuo']:,.0f}"], ["Gasto Operativo e Impuestos", f"S/. -{d['gop']:,.0f}"], ["UTILIDAD NETA LIQUIDA", f"S/. {d['f_n']:,.0f}"]]
    for r in ops:
        pdf.cell(90, 8, r[0], 1); pdf.cell(100, 8, r[1], 1, ln=True)

    # Bloque 3: Dictamen
    pdf.ln(8); pdf.set_font("Arial", 'B', 12); pdf.set_text_color(59, 130, 246)
    pdf.cell(0, 10, "3. CONCLUSIONES Y RENTABILIDAD PATRIMONIAL", ln=True)
    pdf.set_font("Arial", '', 9); pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 7, f"- ROI Cash-on-Cash Proyectado: {d['roi']:.2f}% Anual", ln=True)
    pdf.cell(0, 7, f"- Tiempo de Recuperacion (Payback): {d['pb']:.1f} Años", ln=True)
    pdf.cell(0, 7, f"- Plusvalia Latente Estimada (10A): S/. {d['v10']:,.0f}", ln=True)
    pdf.ln(10); pdf.set_font("Arial", 'I', 8)
    pdf.multi_cell(0, 4, "AVISO: Este documento es una simulacion financiera basada en datos actuales de mercado. El Ing. Jancarlo Mendoza recomienda monitorear la ocupacion y ADR para optimizar el rendimiento del activo.")

    return pdf.output(dest='S').encode('latin-1')

if st.session_state.authenticated:
    st.write("---")
    if st.button("📥 DESCARGAR AUDITORÍA COMPLETA (PDF)"):
        v10_calc = (val_depa * (1 + plus_slider/100)**10) - val_depa
        pdf_bytes = generate_master_pdf({
            "val": val_depa, "ini": inicial, "inv_a": inv_amoblado, "inv_t": inv_total,
            "i_b": ingreso_bruto, "cuo": cuota, "gop": gastos_op, "f_n": flujo_neto,
            "roi": roi_anual, "pb": rec, "v10": v10_calc, "occ": (ocupacion_act/30)*100
        })
        st.download_button("Guardar Reporte Auditoría", data=pdf_bytes, file_name=f"Auditoria_Inmobiliaria_{datetime.now().strftime('%Y%m%d')}.pdf")
