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
    # CSS: Tipografías Slim, Colores Tenues y Reset de Inputs (Sin +/-)
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100;300;400;600&display=swap');
        
        html, body, [class*="st-"] { font-family: 'Inter', sans-serif !important; }
        
        /* Ocultar botones + / - en inputs numéricos */
        button.step-up, button.step-down { display: none !important; }
        input[type=number]::-webkit-inner-spin-button, 
        input[type=number]::-webkit-outer-spin-button { -webkit-appearance: none; margin: 0; }
        input[type=number] { -moz-appearance: textfield; }

        /* Estilo Slim para Inputs */
        .stNumberInput input, .stSelectbox div, .stSlider div {
            font-weight: 300 !important;
            background-color: #1a1d23 !important;
            color: #f1f5f9 !important;
        }
        
        .stNumberInput label, .stSelectbox label, .stSlider label {
            font-weight: 100 !important;
            letter-spacing: 1px;
            color: #94a3b8 !important;
            text-transform: uppercase;
        }

        .main { background-color: #0f1115; }

        /* Títulos y Tarjetas con Letras Blancas */
        .section-title { 
            margin-top: 40px; color: #ffffff !important; 
            font-size: 1.3rem; font-weight: 100; letter-spacing: 3px;
            text-transform: uppercase; border-bottom: 1px solid #1e293b; padding-bottom: 12px;
        }
        
        .card-base {
            border: 1px solid rgba(255,255,255,0.15); border-radius: 10px; padding: 22px;
            text-align: center; margin-bottom: 15px; color: #ffffff !important;
        }
        .card-blue { background-color: rgba(30, 64, 175, 0.4); }   
        .card-purple { background-color: rgba(88, 28, 135, 0.4); } 
        .card-teal { background-color: rgba(13, 148, 136, 0.4); }    
        .card-slate { background-color: rgba(51, 65, 85, 0.5); } 

        .label-card { color: #ffffff; font-size: 0.75rem; font-weight: 300; text-transform: uppercase; margin-bottom: 10px; opacity: 0.8; }
        .val-pos { color: #60a5fa; font-size: 1.8rem; font-weight: 600; }
        .val-neg { color: #f87171; font-size: 1.8rem; font-weight: 600; }
        
        .info-box { 
            font-size: 0.85rem; color: #ffffff; padding: 15px; 
            background-color: #161b22; border-radius: 6px; 
            margin: 10px 0; border: 1px solid #30363d; font-weight: 300;
        }
        .footer-tip {
            background-color: #064e3b; color: #ffffff; padding: 18px;
            border-radius: 8px; margin-top: 25px; font-size: 0.9rem; border-left: 4px solid #10b981;
        }
        </style>
        """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("⚙️ Parámetros de Auditoría")
        val_depa = st.number_input("Precio Inmueble (S/.)", value=250000)
        inv_amoblado = st.number_input("Inversión Amoblado (S/.)", value=25000)
        st.write("---")
        tcea = st.number_input("TCEA Bancaria (%)", value=9.5)
        plazo_años = st.selectbox("Plazo Crédito (Años)", [10, 15, 20, 25], index=2)
        st.write("---")
        tarifa_base = st.number_input("Tarifa Airbnb (S/.)", value=180)
        # Selector de 1-30 sin botones +/-
        ocupacion_act = st.selectbox("Días Ocupados al Mes", list(range(1, 31)), index=19)
        st.write("---")
        renta_trad = st.number_input("Renta Tradicional (S/.)", value=1800)

    # CÁLCULOS BASE
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

    tabs = st.tabs(["💎 CAPITAL Y OPERACIÓN", "📈 PLUSVALÍA", "⚖️ SENSIBILIDAD", "🔄 COMPARATIVA"])

    # --------------------------------------------------------- PESTAÑA 1
    with tabs[0]:
        st.markdown('<div class="section-title">🧱 Estructura de Capital e Ingresos</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">ℹ️ Desglose del capital propio necesario para la adquisición y puesta en marcha del activo inmobiliario.</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="card-base card-blue"><div class="label-card">Cuota Inicial (20%) 🏦</div><div class="val-pos">S/. {inicial:,.0f}</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="card-base card-blue"><div class="label-card">Mobiliario/Capex 🛋️</div><div class="val-pos">S/. {inv_amoblado:,.0f}</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="card-base card-purple"><div class="label-card">Inversión Total 💎</div><div class="val-pos">S/. {inv_total:,.0f}</div></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">📊 Análisis Operativo Mensual</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">ℹ️ Estimación de ingresos netos vs egresos financieros y operativos mensuales.</div>', unsafe_allow_html=True)
        c4, c5, c6, c7 = st.columns(4)
        with c4: st.markdown(f'<div class="card-base card-slate"><div class="label-card">Airbnb Bruto 🏨</div><div class="val-pos">S/. {ingreso_bruto:,.0f}</div></div>', unsafe_allow_html=True)
        with c5: st.markdown(f'<div class="card-base card-slate"><div class="label-card">Cuota Banco 🏦</div><div class="val-neg">S/. -{cuota:,.0f}</div></div>', unsafe_allow_html=True)
        with c6: st.markdown(f'<div class="card-base card-slate"><div class="label-card">Costos/Imp. 🧾</div><div class="val-neg">S/. -{gastos_op:,.0f}</div></div>', unsafe_allow_html=True)
        with c7: st.markdown(f'<div class="card-base card-teal"><div class="label-card">Utilidad Neta 💰</div><div class="val-pos">S/. {flujo_neto:,.0f}</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">⏱️ Payback y Recuperación</div>', unsafe_allow_html=True)
        años_pb = 25; meses = np.arange(0, años_pb*12+1); f_acum = [-inv_total]; rec = 0
        for m in meses[1:]:
            f_acum.append(f_acum[-1] + (flujo_neto if m <= plazo_años*12 else ingreso_bruto-gastos_op))
            if rec == 0 and f_acum[-1] >= 0: rec = m/12

        cp1, cp2 = st.columns([1, 1.8])
        with cp1:
            st.markdown(f'<div class="card-base card-purple" style="border: 2px solid #ffffff;"><div class="label-card">Payback Proyectado ⌛</div><div class="val-pos" style="color:#ffffff; font-size:2.8rem;">{rec:.1f} Años</div></div>', unsafe_allow_html=True)
            st.markdown('<div class="info-box">El tiempo de recuperación indica cuándo el activo ha devuelto el 100% del capital propio invertido a través de sus flujos.</div>', unsafe_allow_html=True)
        with cp2:
            fig_pb = go.Figure()
            # Pintar áreas
            fig_pb.add_trace(go.Scatter(x=meses/12, y=[min(0, x) for x in f_acum], fill='tozeroy', fillcolor='rgba(248, 113, 113, 0.2)', line=dict(width=0), showlegend=False))
            fig_pb.add_trace(go.Scatter(x=meses/12, y=[max(0, x) for x in f_acum], fill='tozeroy', fillcolor='rgba(16, 185, 129, 0.2)', line=dict(width=0), showlegend=False))
            fig_pb.add_trace(go.Scatter(x=meses/12, y=f_acum, line=dict(color='#ffffff', width=2), name="Flujo Acumulado"))
            fig_pb.update_layout(title="<b>CURVA DE RECUPERACIÓN PATRIMONIAL (ROE)</b>", height=350, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#ffffff", margin=dict(t=50))
            st.plotly_chart(fig_pb, use_container_width=True)
            st.markdown('<div class="info-box">Gráfico: El área roja representa la exposición de capital; el área verde es la generación de riqueza neta tras recuperar la inversión.</div>', unsafe_allow_html=True)

        st.markdown('<div class="footer-tip">🚀 <b>RECOMENDACIÓN OPERATIVA:</b> La clave del éxito en Airbnb Lima es el "Superhost status". Esto garantiza un 20% más de visibilidad y permite mantener tarifas altas incluso en temporada baja.</div>', unsafe_allow_html=True)

    # --------------------------------------------------------- PESTAÑA 2
    with tabs[1]:
        st.markdown('<div class="section-title">🏔️ Valorización y Notas Informativas</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">ℹ️ La plusvalía es el incremento del valor de mercado del inmueble. En distritos como Miraflores/San Isidro, la tasa histórica oscila entre 3% y 6%.</div>', unsafe_allow_html=True)
        plus_slider = st.slider("Plusvalía Anual Estimada (%)", 0.0, 10.0, 4.0)
        
        c_p = st.columns(4)
        for i, a in enumerate([5, 10, 15, 20]):
            g = (val_depa * (1 + plus_slider/100)**a) - val_depa
            with c_p[i]: 
                st.markdown(f'<div class="card-base card-blue"><div class="label-card">Plusvalía a {a} Años 📈</div><div class="val-pos" style="color:white;">S/. {g:,.0f}</div></div>', unsafe_allow_html=True)
                st.caption(f"Valorización acumulada tras {a} años.")
        
        st.markdown('<div class="section-title">📊 Proyección de Patrimonio Real</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">ℹ️ Este gráfico ilustra la "magia" de los bienes raíces: mientras el valor de la propiedad sube, su deuda bancaria baja, ampliando su patrimonio neto.</div>', unsafe_allow_html=True)
        años = np.arange(0, 26); v_mkt = [val_depa * (1+plus_slider/100)**a for a in años]
        eq = [v - (prestamo * (1 - a/plazo_años) if a < plazo_años else 0) for a, v in zip(años, v_mkt)]
        
        fig_p = go.Figure()
        fig_p.add_trace(go.Bar(x=años, y=v_mkt, name="Valor Mercado", marker_color='rgba(255,255,255,0.1)'))
        fig_p.add_trace(go.Scatter(x=años, y=eq, name="Patrimonio Neto", fill='tozeroy', fillcolor='rgba(96, 165, 250, 0.2)', line=dict(color='#60a5fa', width=3)))
        fig_p.update_layout(title="<b>CRECIMIENTO DEL PATRIMONIO (EQUITY BUILDUP)</b>", height=450, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#ffffff")
        st.plotly_chart(fig_p, use_container_width=True)
        
        st.markdown('<div class="footer-tip">📈 <b>TIP FINANCIERO:</b> La plusvalía es una rentabilidad "invisible" pero potente. Un inmueble que se valoriza al 4% anual duplica su valor en aproximadamente 18 años.</div>', unsafe_allow_html=True)

    # --------------------------------------------------------- PESTAÑA 3
    with tabs[2]:
        st.markdown('<div class="section-title">⚖️ Matriz de Sensibilidad Operativa</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">ℹ️ Análisis de escenarios: Evaluamos cómo cambia la rentabilidad final ante variaciones en la ocupación y el precio.</div>', unsafe_allow_html=True)
        
        def color_roi(val):
            color = '#f87171' if val < 5 else '#fbbf24' if val < 10 else '#4ade80'
            return f'background-color: {color}; color: #000; font-weight: bold;'

        # Sensibilidad Días
        st.subheader("📍 Días de Ocupación vs ROI")
        st.markdown('<div class="info-box">ℹ️ Variación de la rentabilidad anual según la cantidad de días rentados al mes.</div>', unsafe_allow_html=True)
        c_s1_t, c_s1_g = st.columns([1, 1.8], vertical_alignment="center")
        d_range = [5, 10, 15, 20, 25, 30]
        roi_d = [((((tarifa_base*d*0.85) - cuota - mantenimiento - (tarifa_base*d*0.85*0.05))*12/inv_total)*100) for d in d_range]
        with c_s1_t:
            df_d = pd.DataFrame({"Días/Mes": d_range, "ROI %": roi_d})
            st.table(df_d.style.map(color_roi, subset=['ROI %']).format({"ROI %": "{:.2f}%"}))
        with c_s1_g:
            fig_d = go.Figure(go.Scatter(x=d_range, y=roi_d, mode='lines+markers', line=dict(color='#60a5fa', width=4), marker=dict(size=12)))
            fig_d.update_layout(height=550, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#ffffff")
            st.plotly_chart(fig_d, use_container_width=True)

        # Sensibilidad Tarifa
        st.subheader("💰 Tarifa Airbnb vs ROI")
        st.markdown('<div class="info-box">ℹ️ Variación de la rentabilidad anual según el precio promedio por noche.</div>', unsafe_allow_html=True)
        c_s2_t, c_s2_g = st.columns([1, 1.8], vertical_alignment="center")
        t_range = list(range(int(tarifa_base)-30, int(tarifa_base)+40, 10))
        roi_t = [((((t*ocupacion_act*0.85) - cuota - mantenimiento - (t*ocupacion_act*0.85*0.05))*12/inv_total)*100) for t in t_range]
        with c_s2_t:
            df_t = pd.DataFrame({"Tarifa S/.": t_range, "ROI %": roi_t})
            st.table(df_t.style.map(color_roi, subset=['ROI %']).format({"ROI %": "{:.2f}%"}))
        with c_s2_g:
            fig_t = go.Figure(go.Scatter(x=t_range, y=roi_t, mode='lines+markers', line=dict(color='#34d399', width=4), marker=dict(size=12)))
            fig_t.update_layout(height=550, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#ffffff")
            st.plotly_chart(fig_t, use_container_width=True)

        st.markdown('<div class="footer-tip">⚠️ <b>RECOMENDACIÓN:</b> Si su ROI cae por debajo del 5% en el escenario de 15 días, el proyecto tiene un riesgo elevado. Busque reducir el precio de compra o mejorar el amoblado para subir la tarifa.</div>', unsafe_allow_html=True)

    # --------------------------------------------------------- PESTAÑA 4
    with tabs[3]:
        st.markdown('<div class="section-title">🔄 Comparativa: Tradicional vs Airbnb</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">ℹ️ Análisis comparativo de la utilidad neta anualizada y el retorno sobre la inversión de ambos modelos.</div>', unsafe_allow_html=True)
        
        ventaja_anual = (flujo_neto * 12) - utilidad_trad
        dif_roi = roi_airbnb - roi_trad
        
        cc = st.columns(4)
        with cc[0]: st.markdown(f'<div class="card-base card-emerald"><div class="label-card">Excedente Airbnb 🏆</div><div class="val-pos" style="color:white;">S/. {ventaja_anual:,.0f}</div></div>', unsafe_allow_html=True)
        with cc[1]: st.markdown(f'<div class="card-base card-slate"><div class="label-card">ROI Airbnb 🏨</div><div class="val-pos" style="color:white;">{roi_airbnb:.1f}%</div></div>', unsafe_allow_html=True)
        with cc[2]: st.markdown(f'<div class="card-base card-slate"><div class="label-card">ROI Tradicional 🏠</div><div class="val-pos" style="color:white;">{roi_trad:.1f}%</div></div>', unsafe_allow_html=True)
        with cc[3]: st.markdown(f'<div class="card-base card-indigo"><div class="label-card">Diferencia ROI 🚀</div><div class="val-pos" style="color:white;">{dif_roi:+.1f}%</div></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="info-box">Gráfico de barras que muestra la utilidad neta líquida disponible para el inversionista cada año tras pagar todos los compromisos.</div>', unsafe_allow_html=True)
        
        labels = ['<b>MODELO AIRBNB</b>', '<b>RENTA ANUAL</b>']
        vals = [flujo_neto*12, utilidad_trad]
        fig_c = go.Figure([go.Bar(
            x=labels, y=vals, 
            marker_color=['#10b981' if v > 0 else '#ef4444' for v in vals],
            text=[f'S/. {v:,.0f}' for v in vals],
            textposition='inside', insidetextanchor='middle',
            textfont=dict(size=26, color='white', family='Inter')
        )])
        fig_c.update_layout(title="<b>UTILIDAD NETA ANUALIZADA LÍQUIDA</b>", height=600, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#ffffff")
        st.plotly_chart(fig_c, use_container_width=True)
        
        st.markdown('<div class="info-box" style="text-align:justify;"><b>Variables de la Relación:</b> El gráfico muestra el diferencial de flujo de caja libre. El <b>Modelo Airbnb</b> tiene un mayor potencial de ingresos pero asume costos variables (servicios, limpieza, mantenimiento) y riesgo de vacancia. El <b>Modelo Tradicional</b> ofrece estabilidad absoluta pero un techo de rentabilidad menor que a menudo apenas cubre la hipoteca.</div>', unsafe_allow_html=True)

        st.markdown('<div class="footer-tip">🏁 <b>DICTAMEN FINAL:</b> Si la diferencia de ROI es mayor al 4%, la gestión intensiva de Airbnb justifica plenamente el esfuerzo operativo adicional.</div>', unsafe_allow_html=True)

# =========================================================
# MOTOR DE PDF (MÁXIMA DENSIDAD INFORMATIVA)
# =========================================================
def generate_master_pdf(d):
    pdf = FPDF()
    pdf.add_page()
    # Header Audit
    pdf.set_fill_color(15, 23, 42); pdf.rect(0, 0, 210, 55, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", 'B', 18)
    pdf.cell(0, 20, "AUDITORIA DE FACTIBILIDAD INMOBILIARIA", ln=True, align='C')
    pdf.set_font("Arial", '', 10); pdf.cell(0, 5, "ELABORADO POR: ING. JANCARLO MENDOZA - EXPERTO INMOBILIARIO", ln=True, align='C')
    pdf.cell(0, 5, f"LIMA, PERU | REPORTE DE ANALISIS TECNICO: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align='C')
    pdf.ln(35); pdf.set_text_color(0, 0, 0)

    # Bloque 1: Capital
    pdf.set_font("Arial", 'B', 12); pdf.set_text_color(59, 130, 246)
    pdf.cell(0, 10, "1. INGENIERIA DE CAPITAL Y ESTRUCTURA DE COMPRA", ln=True)
    pdf.set_font("Arial", '', 9); pdf.set_text_color(40, 40, 40)
    pdf.multi_cell(0, 5, "Este informe analiza la viabilidad del activo inmobiliario mediante el uso de apalancamiento financiero. El capital inicial o 'Equity' representa el aporte directo del inversionista, el cual se recupera mediante la operacion del activo.")
    pdf.ln(2)
    rows = [["CONCEPTO", "VALOR (S/.)", "DESCRIPCION TECNICA"],
            ["Valor Adquisicion", f"{d['val']:,.0f}", "Precio de mercado del inmueble"],
            ["Cuota Inicial (20%)", f"{d['ini']:,.0f}", "Capital propio para desembolso inicial"],
            ["Capex de Mobiliario", f"{d['inv_a']:,.0f}", "Inversion en equipamiento para Airbnb"],
            ["CASH-OUT TOTAL", f"{d['inv_t']:,.0f}", "Monto total de inversion real"]]
    for r in rows:
        pdf.cell(60, 8, r[0], 1); pdf.cell(35, 8, r[1], 1); pdf.cell(95, 8, r[2], 1, ln=True)

    # Bloque 2: Flujos
    pdf.ln(8); pdf.set_font("Arial", 'B', 12); pdf.set_text_color(59, 130, 246)
    pdf.cell(0, 10, "2. ANALISIS DE FLUJOS OPERATIVOS (MONTHLY CASH FLOW)", ln=True)
    pdf.set_font("Arial", '', 9)
    pdf.multi_cell(0, 5, f"Se ha proyectado un escenario basado en una ocupacion de {d['occ']:.1f}%. El flujo de caja neto es el resultado de restar la cuota bancaria y los gastos operativos (mantenimiento e impuestos) al ingreso bruto.")
    pdf.ln(2)
    ops = [["Ingresos Netos Estimados", f"S/. {d['i_b']:,.0f}"], ["Cuota Hipotecaria (TCEA)", f"S/. -{d['cuo']:,.0f}"], ["Gasto Operativo + Sunat", f"S/. -{d['gop']:,.0f}"], ["UTILIDAD NETA DISPONIBLE", f"S/. {d['f_n']:,.0f}"]]
    for r in ops:
        pdf.cell(90, 8, r[0], 1); pdf.cell(100, 8, r[1], 1, ln=True)

    # Bloque 3: Rentabilidad
    pdf.ln(8); pdf.set_font("Arial", 'B', 12); pdf.set_text_color(59, 130, 246)
    pdf.cell(0, 10, "3. METRICAS DE RENTABILIDAD Y DICTAMEN", ln=True)
    pdf.set_font("Arial", '', 9); pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 7, f"- ROI Cash-on-Cash Proyectado: {d['roi']:.2f}% Anual", ln=True)
    pdf.cell(0, 7, f"- Tiempo de Recuperacion Estimado (Payback): {d['pb']:.1f} Años", ln=True)
    pdf.cell(0, 7, f"- Plusvalia Latente Acumulada (10 Años): S/. {d['v10']:,.0f}", ln=True)
    pdf.ln(10); pdf.set_font("Arial", 'I', 8)
    pdf.multi_cell(0, 4, "AVISO LEGAL: Los calculos son proyecciones basadas en modelos financieros. El Ing. Jancarlo Mendoza recomienda auditar la partida registral y el reglamento interno antes de cualquier firma de minuta.")

    return pdf.output(dest='S').encode('latin-1')

if st.session_state.authenticated:
    st.write("---")
    if st.button("📥 GENERAR AUDITORÍA PROFESIONAL (PDF)"):
        v10_calc = (val_depa * (1 + plus_slider/100)**10) - val_depa
        pdf_bytes = generate_master_pdf({
            "val": val_depa, "ini": inicial, "inv_a": inv_amoblado, "inv_t": inv_total,
            "i_b": ingreso_bruto, "cuo": cuota, "gop": gastos_op, "f_n": flujo_neto,
            "roi": roi_airbnb, "pb": rec, "v10": v10_calc, "occ": (ocupacion_act/30)*100
        })
        st.download_button("Descargar Reporte de Auditoría", data=pdf_bytes, file_name=f"Auditoria_Inmobiliaria_JM.pdf")
