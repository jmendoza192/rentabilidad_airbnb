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
    # CSS Personalizado: Tipografías Slim/Normal y Colores Tenues
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100;300;400;600&family=Roboto+Mono:wght@300&display=swap');
        
        /* Tipografía general e inputs */
        html, body, [class*="st-"], .stNumberInput, .stSelectbox, .stSlider {
            font-family: 'Inter', sans-serif;
        }
        
        .stNumberInput label, .stSelectbox label, .stSlider label {
            font-weight: 300 !important;
            letter-spacing: 0.5px;
            color: #94a3b8 !important;
        }

        .main { background-color: #0f1115; }

        /* Títulos Slim */
        .section-title { 
            margin-top: 40px; color: #f1f5f9; 
            font-size: 1.3rem; font-weight: 100; letter-spacing: 3px;
            text-transform: uppercase; border-bottom: 1px solid #1e293b; padding-bottom: 12px;
        }
        
        /* Tarjetas Multicolores Tenues */
        .card-base {
            border: 1px solid rgba(255,255,255,0.05); border-radius: 6px; padding: 22px;
            text-align: center; margin-bottom: 15px;
        }
        .card-blue { background-color: rgba(30, 41, 59, 0.5); }   /* Slate Blue */
        .card-purple { background-color: rgba(49, 46, 129, 0.3); } /* Indigo */
        .card-teal { background-color: rgba(19, 78, 74, 0.3); }    /* Teal */
        .card-neutral { background-color: rgba(31, 41, 55, 0.4); } /* Gray */

        .label-card { color: #94a3b8; font-size: 0.7rem; font-weight: 300; text-transform: uppercase; margin-bottom: 10px; }
        .val-pos { color: #60a5fa; font-size: 1.7rem; font-weight: 600; font-family: 'Inter'; }
        .val-neg { color: #f87171; font-size: 1.7rem; font-weight: 600; font-family: 'Inter'; }
        
        /* Cajas de Información */
        .info-box { 
            font-size: 0.85rem; color: #64748b; padding: 18px; 
            background-color: #111827; border-radius: 4px;
            margin: 10px 0; border: 1px solid #1e293b; line-height: 1.6;
        }
        .footer-tip {
            background-color: #064e3b; color: #a7f3d0; padding: 20px;
            border-radius: 8px; margin-top: 30px; font-size: 0.9rem; border-left: 5px solid #10b981;
        }
        </style>
        """, unsafe_allow_html=True)

    # 1. SIDEBAR (ENTRADAS TÉCNICAS)
    with st.sidebar:
        st.markdown("### 🛠️ Configuración del Activo")
        val_depa = st.number_input("Precio Inmueble (S/.)", value=250000)
        inv_amoblado = st.number_input("Inversión Amoblado (S/.)", value=25000)
        st.write("---")
        tcea = st.number_input("TCEA Bancaria %", value=9.5)
        plazo_años = st.selectbox("Plazo (Años)", [10, 15, 20, 25], index=2)
        st.write("---")
        tarifa_base = st.number_input("Tarifa Airbnb (S/.)", value=180)
        ocupacion_act = st.slider("Ocupación Mensual (Días)", 1, 30, 20)
        st.write("---")
        renta_trad = st.number_input("Alquiler Tradicional (S/.)", value=1800)

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
    roi_anual = (flujo_neto * 12 / inv_total) * 100
    utilidad_trad = (renta_trad - cuota - (val_depa*0.015/12) - (renta_trad*0.05)) * 12

    tabs = st.tabs(["💎 CAPITAL Y OPERACIÓN", "📈 PLUSVALÍA", "⚖️ SENSIBILIDAD", "🔄 COMPARATIVA"])

    # =========================================================
    # PESTAÑA 1: CAPITAL Y OPERACIÓN
    # =========================================================
    with tabs[0]:
        st.markdown('<div class="section-title">🏗️ Estructura de Capital e Ingresos</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Análisis del "Cash-Out" inicial. Este bloque define el capital propio expuesto antes de iniciar la operación.</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="card-base card-blue"><div class="label-card">Inicial Banco (20%)</div><div class="val-pos">S/. {inicial:,.0f}</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="card-base card-blue"><div class="label-card">Amoblado Capex</div><div class="val-pos">S/. {inv_amoblado:,.0f}</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="card-base card-purple"><div class="label-card">Inversión Total</div><div class="val-pos">S/. {inv_total:,.0f}</div></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">📉 Análisis Operativo Mensual</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Flujo de caja neto proyectado después de obligaciones financieras y tributarias.</div>', unsafe_allow_html=True)
        c4, c5, c6, c7 = st.columns(4)
        with c4: st.markdown(f'<div class="card-base card-neutral"><div class="label-card">Ingreso Bruto 🏨</div><div class="val-pos">S/. {ingreso_bruto:,.0f}</div></div>', unsafe_allow_html=True)
        with c5: st.markdown(f'<div class="card-base card-neutral"><div class="label-card">Cuota Hipotecaria 🏦</div><div class="val-neg">S/. -{cuota:,.0f}</div></div>', unsafe_allow_html=True)
        with c6: st.markdown(f'<div class="card-base card-neutral"><div class="label-card">Gastos + Imp. 🧾</div><div class="val-neg">S/. -{gastos_op:,.0f}</div></div>', unsafe_allow_html=True)
        with c7: st.markdown(f'<div class="card-base card-teal"><div class="label-card">Utilidad Neta 💰</div><div class="val-pos">S/. {flujo_neto:,.0f}</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">⏱️ Retorno de Capital (Payback)</div>', unsafe_allow_html=True)
        años_pb = 25; meses = np.arange(0, años_pb*12+1); f_acum = [-inv_total]; rec = 0
        for m in meses[1:]:
            f_acum.append(f_acum[-1] + (flujo_neto if m <= plazo_años*12 else ingreso_bruto-gastos_op))
            if rec == 0 and f_acum[-1] >= 0: rec = m/12

        cp1, cp2 = st.columns([1, 1.8])
        with cp1:
            st.write("<br>", unsafe_allow_html=True)
            st.markdown(f'<div class="card-base card-purple"><div class="label-card">Payback Proyectado ⏳</div><div class="val-pos" style="font-size:2.8rem;">{rec:.1f} Años</div></div>', unsafe_allow_html=True)
            st.markdown('<div class="info-box">El Payback es la métrica de riesgo principal. Indica el tiempo necesario para que el activo sea "gratis" tras recuperar el capital propio.</div>', unsafe_allow_html=True)
        with cp2:
            fig_pb = go.Figure()
            fig_pb.add_trace(go.Scatter(x=meses/12, y=f_acum, fill='tozeroy', fillcolor='rgba(96, 165, 250, 0.05)', line=dict(color='#60a5fa', width=2)))
            fig_pb.update_layout(title="<b>CURVA DE RECUPERACIÓN PATRIMONIAL</b>", height=320, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#94a3b8", size=10), margin=dict(t=50, l=0, r=0))
            st.plotly_chart(fig_pb, use_container_width=True)

        st.markdown('<div class="footer-tip">💡 <b>RECOMENDACIÓN OPERATIVA:</b> Para acelerar el Payback, enfoque su marketing en TikTok/Reels mostrando las "vistas" o "acabados premium" del departamento; esto permite subir la tarifa base un 15% sin afectar la ocupación.</div>', unsafe_allow_html=True)

    # =========================================================
    # PESTAÑA 2: PLUSVALÍA
    # =========================================================
    with tabs[1]:
        st.markdown('<div class="section-title">🏔️ Valorización y Equity Real</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Nota Informativa: La plusvalía es la ganancia de capital latente. Se estima según el crecimiento de m2 en distritos como Miraflores/Surco.</div>', unsafe_allow_html=True)
        plus_slider = st.slider("Expectativa Anual de Plusvalía %", 0.0, 8.0, 4.0)
        
        c_p = st.columns(4)
        for i, a in enumerate([5, 10, 15, 20]):
            g = (val_depa * (1 + plus_slider/100)**a) - val_depa
            with c_p[i]: 
                st.markdown(f'<div class="card-base card-blue"><div class="label-card">Plusvalía a {a} Años 📈</div><div class="val-pos">S/. {g:,.0f}</div></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">📊 Evolución del Patrimonio Neto</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Este gráfico muestra cómo su riqueza aumenta por dos vías: el valor de mercado sube y el saldo de la deuda baja mensualmente.</div>', unsafe_allow_html=True)
        años = np.arange(0, 26); v_mkt = [val_depa * (1+plus_slider/100)**a for a in años]
        eq = [v - (prestamo * (1 - a/plazo_años) if a < plazo_años else 0) for a, v in zip(años, v_mkt)]
        
        fig_p = go.Figure()
        fig_p.add_trace(go.Bar(x=años, y=v_mkt, name="Valor Propiedad", marker_color='#1e293b'))
        fig_p.add_trace(go.Scatter(x=años, y=eq, name="Equity Real", fill='tozeroy', fillcolor='rgba(96, 165, 250, 0.1)', line=dict(color='#60a5fa', width=3)))
        fig_p.update_layout(title="<b>CRECIMIENTO PATRIMONIAL (VALOR VS DEUDA)</b>", height=450, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#94a3b8")
        st.plotly_chart(fig_p, use_container_width=True)
        
        st.markdown('<div class="footer-tip">📈 <b>TIP FINANCIERO:</b> El apalancamiento permite que usted gane Plusvalía sobre el 100% del valor del inmueble, habiendo invertido solo el 20%. Esto se conoce como efecto multiplicador de riqueza.</div>', unsafe_allow_html=True)

    # =========================================================
    # PESTAÑA 3: SENSIBILIDAD
    # =========================================================
    with tabs[2]:
        st.markdown('<div class="section-title">🛡️ Escenarios de Resiliencia Inmobiliaria</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Análisis de estrés: ¿Qué pasa si el mercado cambia? Los colores semáforo indican la viabilidad del ROI (Rojo < 5% | Ámbar 5-10% | Verde > 10%).</div>', unsafe_allow_html=True)
        
        def color_roi(val):
            color = '#f87171' if val < 5 else '#fbbf24' if val < 10 else '#4ade80'
            return f'background-color: {color}; color: #000; font-weight: bold;'

        # 1. Días
        st.subheader("📍 Sensibilidad por Ocupación (Días al Mes)")
        col_s1_t, col_s1_g = st.columns([1, 1.8], gap="large")
        d_range = [5, 10, 15, 20, 25, 30]
        roi_d = [((((tarifa_base*d*0.85) - cuota - mantenimiento - (tarifa_base*d*0.85*0.05))*12/inv_total)*100) for d in d_range]
        with col_s1_t:
            st.write("<br>", unsafe_allow_html=True)
            df_d = pd.DataFrame({"Días Ocupados": d_range, "ROI Anual %": roi_d})
            st.table(df_d.style.map(color_roi, subset=['ROI Anual %']).format({"ROI Anual %": "{:.2f}%"}))
        with col_s1_g:
            fig_d = go.Figure(go.Scatter(x=d_range, y=roi_d, mode='lines+markers', line=dict(color='#60a5fa', width=5), marker=dict(size=12)))
            fig_d.update_layout(title="<b>CORRECCIÓN DE ROI VS OCUPACIÓN</b>", height=550, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#94a3b8")
            st.plotly_chart(fig_d, use_container_width=True)

        # 2. Tarifa
        st.subheader("💰 Sensibilidad por Tarifa Airbnb (S/.)")
        col_s2_t, col_s2_g = st.columns([1, 1.8], gap="large")
        t_range = list(range(int(tarifa_base)-40, int(tarifa_base)+60, 10))
        roi_t = [((((t*ocupacion_act*0.85) - cuota - mantenimiento - (t*ocupacion_act*0.85*0.05))*12/inv_total)*100) for t in t_range]
        with col_s2_t:
            st.write("<br>", unsafe_allow_html=True)
            df_t = pd.DataFrame({"Tarifa S/.": t_range, "ROI Anual %": roi_t})
            st.table(df_t.style.map(color_roi, subset=['ROI Anual %']).format({"ROI Anual %": "{:.2f}%"}))
        with col_s2_g:
            fig_t = go.Figure(go.Scatter(x=t_range, y=roi_t, mode='lines+markers', line=dict(color='#34d399', width=5), marker=dict(size=12)))
            fig_t.update_layout(title="<b>CORRECCIÓN DE ROI VS TARIFA</b>", height=550, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#94a3b8")
            st.plotly_chart(fig_t, use_container_width=True)

        st.markdown('<div class="footer-tip">⚠️ <b>TIP DE RIESGO:</b> Su punto de equilibrio (ROI > 0) se encuentra cerca de los 12 días de ocupación. Si el mercado baja de este umbral, el inmueble deja de autofinanciarse.</div>', unsafe_allow_html=True)

    # =========================================================
    # PESTAÑA 4: COMPARATIVA TRADICIONAL VS AIRBNB
    # =========================================================
    with tabs[3]:
        st.markdown('<div class="section-title">🏁 Comparativa: Renta Tradicional vs Airbnb</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">En este bloque se determina la conveniencia económica de la gestión intensiva (Airbnb) frente a la renta pasiva (Tradicional).</div>', unsafe_allow_html=True)
        
        ventaja_anual = (flujo_neto * 12) - utilidad_trad
        multiplicador = (flujo_neto * 12) / (utilidad_trad if utilidad_trad > 0 else 1)
        
        cc1, cc2 = st.columns(2)
        with cc1: st.markdown(f'<div class="card-base card-teal" style="border:1px solid #10b981;"><div class="label-card">Excedente Anual Airbnb 🏆</div><div class="val-pos" style="color:#10b981;">S/. {ventaja_anual:,.0f}</div></div>', unsafe_allow_html=True)
        with cc2: st.markdown(f'<div class="card-base card-neutral"><div class="label-card">Multiplicador de Ingreso 🚀</div><div class="val-pos">{multiplicador:.1f}x</div></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="info-box">Visualización de la utilidad neta líquida (Cash Flow) anualizada tras pagar banco, gastos operativos e impuestos.</div>', unsafe_allow_html=True)
        
        labels = ['<b>MODELO AIRBNB</b>', '<b>ALQUILER TRADICIONAL</b>']
        vals = [flujo_neto*12, utilidad_trad]
        fig_c = go.Figure([go.Bar(
            x=labels, y=vals, 
            marker_color=['#10b981' if v > 0 else '#ef4444' for v in vals],
            text=[f'S/. {v:,.0f}' for v in vals],
            textposition='inside', insidetextanchor='middle',
            textfont=dict(size=30, color='white', family='Inter', fontWeight='bold')
        )])
        fig_c.update_layout(title="<b>UTILIDAD NETA DISPONIBLE ANUAL</b>", height=600, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#94a3b8")
        st.plotly_chart(fig_c, use_container_width=True)

        st.markdown('<div class="footer-tip">🏁 <b>DICTAMEN FINAL:</b> El modelo Airbnb ofrece una mayor rentabilidad bruta, pero requiere gestión operativa. Si el multiplicador es mayor a 1.5x, la inversión en corta estancia está plenamente justificada.</div>', unsafe_allow_html=True)

# =========================================================
# MOTOR DE PDF (DENSIDAD INFORMATIVA AUDITORÍA)
# =========================================================
def generate_master_pdf(d):
    pdf = FPDF()
    pdf.add_page()
    # Header Audit
    pdf.set_fill_color(15, 23, 42); pdf.rect(0, 0, 210, 55, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", 'B', 18)
    pdf.cell(0, 20, "AUDITORIA TECNICA DE FACTIBILIDAD INMOBILIARIA", ln=True, align='C')
    pdf.set_font("Arial", '', 10); pdf.cell(0, 5, "ELABORADO POR: ING. JANCARLO MENDOZA - EXPERTO INMOBILIARIO", ln=True, align='C')
    pdf.cell(0, 5, f"LIMA, PERU | GENERADO EL: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align='C')
    pdf.ln(35); pdf.set_text_color(0, 0, 0)

    # Bloque 1: Inversión
    pdf.set_font("Arial", 'B', 12); pdf.set_text_color(59, 130, 246)
    pdf.cell(0, 10, "1. INGENIERIA DE CAPITAL Y APALANCAMIENTO", ln=True)
    pdf.set_font("Arial", '', 9); pdf.set_text_color(40, 40, 40)
    pdf.multi_cell(0, 5, "Este informe detalla la viabilidad financiera del proyecto inmobiliario. Se considera una estructura de financiamiento hipotecario con una cuota inicial del 20%. El 'Cash-Out' total incluye la inversion en equipamiento profesional (Capex) necesario para el mercado Airbnb.")
    pdf.ln(2)
    pdf.set_font("Arial", 'B', 9)
    rows = [["CONCEPTO ANALIZADO", "VALOR (S/.)", "NOTA TECNICA"],
            ["Valor Adquisicion Inmueble", f"{d['val']:,.0f}", "Valor comercial de mercado"],
            ["Aporte de Capital (Inicial)", f"{d['ini']:,.0f}", "Capital propio desembolsado"],
            ["Capex de Habilitacion", f"{d['inv_a']:,.0f}", "Mobiliario y Equipamiento"],
            ["INVERSION REAL TOTAL", f"{d['inv_t']:,.0f}", "Capital Total en Riesgo"]]
    for r in rows:
        pdf.cell(65, 8, r[0], 1); pdf.cell(35, 8, r[1], 1); pdf.cell(90, 8, r[2], 1, ln=True)

    # Bloque 2: Operación
    pdf.ln(8); pdf.set_font("Arial", 'B', 12); pdf.set_text_color(59, 130, 246)
    pdf.cell(0, 10, "2. ANALISIS DE FLUJOS OPERATIVOS (MONTHLY CASH FLOW)", ln=True)
    pdf.set_font("Arial", '', 9)
    pdf.multi_cell(0, 5, f"Se ha proyectado un escenario operativo basado en una ocupacion de {d['occ']:.1f}%. El flujo libre considera el pago de cuotas bancarias, mantenimiento del edificio e impuestos de ley (Primera Categoria).")
    pdf.ln(2)
    ops = [["Ingresos Netos Estimados (Airbnb)", f"S/. {d['i_b']:,.0f}"], ["Cuota de Servicio de Deuda", f"S/. -{d['cuo']:,.0f}"], ["Gasto Operativo e Impuestos", f"S/. -{d['gop']:,.0f}"], ["UTILIDAD NETA MENSUAL", f"S/. {d['f_n']:,.0f}"]]
    for r in ops:
        pdf.cell(90, 8, r[0], 1); pdf.cell(100, 8, r[1], 1, ln=True)

    # Bloque 3: Dictamen
    pdf.ln(8); pdf.set_font("Arial", 'B', 12); pdf.set_text_color(59, 130, 246)
    pdf.cell(0, 10, "3. DICTAMEN DE RENTABILIDAD Y PLUSVALIA", ln=True)
    pdf.set_font("Arial", '', 9); pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 7, f"- ROI Cash-on-Cash Proyectado: {d['roi']:.2f}% Anual (Sobre capital propio)", ln=True)
    pdf.cell(0, 7, f"- Horizonte de Payback (Recuperacion): {d['pb']:.1f} Años", ln=True)
    pdf.cell(0, 7, f"- Ganancia de Capital Latente (Plusvalia 10A): S/. {d['v10']:,.0f}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'I', 8)
    pdf.multi_cell(0, 4, "AVISO LEGAL: Los calculos presentados son simulaciones basadas en parametros actuales. La rentabilidad real depende de factores de mercado variables. Este documento sirve como herramienta de auditoria financiera para la toma de decisiones informada.")

    return pdf.output(dest='S').encode('latin-1')

if st.session_state.authenticated:
    st.write("---")
    if st.button("📥 GENERAR AUDITORIA INMOBILIARIA FULL (PDF)"):
        v10_calc = (val_depa * (1 + plus_slider/100)**10) - val_depa
        pdf_bytes = generate_master_pdf({
            "val": val_depa, "ini": inicial, "inv_a": inv_amoblado, "inv_t": inv_total,
            "i_b": ingreso_bruto, "cuo": cuota, "gop": gastos_op, "f_n": flujo_neto,
            "roi": roi_anual, "pb": rec, "v10": v10_calc, "occ": (ocupacion_act/30)*100
        })
        st.download_button("Descargar Reporte Profesional", data=pdf_bytes, file_name=f"Auditoria_Inmobiliaria_JM_{datetime.now().strftime('%Y%m%d')}.pdf")
