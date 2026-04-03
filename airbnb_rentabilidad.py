import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime

# =========================================================
# 0. CONFIGURACIÓN Y ESTÉTICA "PREMIUM MINIMALIST"
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
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100;300;400;600&display=swap');
        
        html, body, [class*="st-"] { font-family: 'Inter', sans-serif; }
        
        .main { background-color: #0f1115; }

        /* Títulos Estilo Slim */
        .section-title { 
            margin-top: 40px; color: #94a3b8; 
            font-size: 1.4rem; font-weight: 100; letter-spacing: 2px;
            text-transform: uppercase; border-bottom: 1px solid #2d3748; padding-bottom: 10px;
        }
        
        /* Tarjetas con Colores Tenues y Marcos */
        .card-base {
            border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 20px;
            text-align: center; margin-bottom: 15px;
        }
        .bg-slate { background-color: #1e293b; }
        .bg-indigo { background-color: #312e81; }
        .bg-teal { background-color: #134e4a; }
        .bg-gray { background-color: #1a1d23; }

        .label-card { color: #cbd5e1; font-size: 0.75rem; font-weight: 300; text-transform: uppercase; margin-bottom: 8px; }
        .val-pos { color: #60a5fa; font-size: 1.7rem; font-weight: 600; }
        .val-neg { color: #f87171; font-size: 1.7rem; font-weight: 600; }
        
        /* Cajas de Texto Informativo */
        .info-box { 
            font-size: 0.85rem; color: #94a3b8; padding: 15px; 
            border-radius: 4px; background-color: #161b22; 
            margin: 10px 0; border: 1px solid #30363d; font-weight: 300;
        }
        .tip-box {
            background-color: #064e3b; color: #6ee7b7; padding: 15px;
            border-radius: 8px; margin-top: 20px; font-size: 0.9rem;
        }
        </style>
        """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("🏢 Parámetros de Activo")
        val_depa = st.number_input("Precio Inmueble (S/.)", value=250000)
        inv_amoblado = st.number_input("Inversión Equipamiento (S/.)", value=25000)
        st.write("---")
        tcea = st.number_input("TCEA %", value=9.5)
        plazo_años = st.selectbox("Plazo (Años)", [10, 15, 20, 25], index=2)
        st.write("---")
        tarifa_base = st.number_input("Tarifa Airbnb (S/.)", value=180)
        ocupacion_act = st.slider("Ocupación Mensual (Días)", 1, 30, 20)
        st.write("---")
        renta_trad = st.number_input("Renta Tradicional (S/.)", value=1800)

    # LÓGICA CORE
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

    tabs = st.tabs(["💎 ESTRUCTURA", "📈 CRECIMIENTO", "⚖️ ESCENARIOS", "🔄 FINAL"])

    # --------------------------------------------------------- PESTAÑA 1
    with tabs[0]:
        st.markdown('<div class="section-title">📊 Estructura de Capital e Ingresos</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Análisis del desembolso inicial necesario para activar la inversión.</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="card-base bg-slate"><div class="label-card">Inicial (20%)</div><div class="val-pos">S/. {inicial:,.0f}</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="card-base bg-slate"><div class="label-card">Amoblado</div><div class="val-pos">S/. {inv_amoblado:,.0f}</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="card-base bg-indigo"><div class="label-card">Total Expuesto</div><div class="val-pos">S/. {inv_total:,.0f}</div></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">💸 Análisis Operativo Mensual</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Flujo de caja proyectado bajo gestión de corta estancia.</div>', unsafe_allow_html=True)
        c4, c5, c6, c7 = st.columns(4)
        with c4: st.markdown(f'<div class="card-base bg-gray"><div class="label-card">Airbnb Bruto</div><div class="val-pos">S/. {ingreso_bruto:,.0f}</div></div>', unsafe_allow_html=True)
        with c5: st.markdown(f'<div class="card-base bg-gray"><div class="label-card">Cuota Banco</div><div class="val-neg">S/. -{cuota:,.0f}</div></div>', unsafe_allow_html=True)
        with c6: st.markdown(f'<div class="card-base bg-gray"><div class="label-card">Costos/Imp.</div><div class="val-neg">S/. -{gastos_op:,.0f}</div></div>', unsafe_allow_html=True)
        with c7: st.markdown(f'<div class="card-base bg-teal"><div class="label-card">Utilidad Neta</div><div class="val-pos">S/. {flujo_neto:,.0f}</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">⏱️ Retorno de Capital (Payback)</div>', unsafe_allow_html=True)
        años_pb = 25; meses = np.arange(0, años_pb*12+1); f_acum = [-inv_total]; rec = 0
        for m in meses[1:]:
            f_acum.append(f_acum[-1] + (flujo_neto if m <= plazo_años*12 else ingreso_bruto-gastos_op))
            if rec == 0 and f_acum[-1] >= 0: rec = m/12

        cp1, cp2 = st.columns([1, 1.8])
        with cp1:
            st.markdown(f'<div class="card-base bg-indigo" style="border:1px solid #6366f1;"><div class="label-card">Recuperación Total</div><div class="val-pos" style="font-size:2.5rem;">{rec:.1f} Años</div></div>', unsafe_allow_html=True)
            st.markdown('<div class="info-box"><b>Tip Operativo:</b> El payback puede acelerarse un 15% optimizando la tarifa durante eventos clave en Lima (Cumbres, Conciertos).</div>', unsafe_allow_html=True)
        with cp2:
            fig_pb = go.Figure()
            fig_pb.add_trace(go.Scatter(x=meses/12, y=f_acum, fill='tozeroy', fillcolor='rgba(96, 165, 250, 0.05)', line=dict(color='#60a5fa', width=2)))
            fig_pb.update_layout(title="<b>CURVA DE RECUPERACIÓN PROYECTADA</b>", height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#94a3b8", size=10), margin=dict(t=40, l=0, r=0))
            st.plotly_chart(fig_pb, use_container_width=True)
            st.markdown('<div class="info-box">Este gráfico muestra el momento exacto en que la inversión deja de ser "riesgo" y pasa a ser "patrimonio neto".</div>', unsafe_allow_html=True)

        st.markdown('<div class="tip-box">💡 <b>Recomendación de Jancarlo:</b> Considere reinvertir el flujo de los primeros 12 meses en mejoras estéticas (iluminación, arte local) para subir su ADR (Average Daily Rate) en un 10%.</div>', unsafe_allow_html=True)

    # --------------------------------------------------------- PESTAÑA 2
    with tabs[1]:
        st.markdown('<div class="section-title">🏔️ Valorización Patrimonial (Equity)</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">El crecimiento real de su riqueza proviene de la plusvalía sumada a la amortización de la deuda.</div>', unsafe_allow_html=True)
        plus_slider = st.slider("Expectativa de Plusvalía Anual %", 0.0, 8.0, 4.0)
        
        c_p = st.columns(4)
        for i, a in enumerate([5, 10, 15, 20]):
            g = (val_depa * (1 + plus_slider/100)**a) - val_depa
            with c_p[i]: 
                st.markdown(f'<div class="card-base bg-slate"><div class="label-card">Plusvalía {a}A</div><div class="val-pos">S/. {g:,.0f}</div></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">📊 Evolución del Valor de Mercado vs Equity</div>', unsafe_allow_html=True)
        años = np.arange(0, 26); v_mkt = [val_depa * (1+plus_slider/100)**a for a in años]
        eq = [v - (prestamo * (1 - a/plazo_años) if a < plazo_años else 0) for a, v in zip(años, v_mkt)]
        
        fig_p = go.Figure()
        fig_p.add_trace(go.Bar(x=años, y=v_mkt, name="Valor Mercado", marker_color='#1e293b'))
        fig_p.add_trace(go.Scatter(x=años, y=eq, name="Equity (Riqueza Real)", fill='tozeroy', fillcolor='rgba(96, 165, 250, 0.1)', line=dict(color='#60a5fa', width=3)))
        fig_p.update_layout(title="<b>CRECIMIENTO PATRIMONIAL A LARGO PLAZO</b>", height=450, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#94a3b8")
        st.plotly_chart(fig_p, use_container_width=True)
        st.markdown('<div class="info-box"><b>Nota:</b> El Equity es el dinero que quedaría en su bolsillo si vendiera la propiedad hoy mismo.</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="tip-box">📈 <b>Tip Financiero:</b> En distritos consolidados como Miraflores o San Isidro, la plusvalía suele actuar como un escudo contra la inflación del 3-5% anual.</div>', unsafe_allow_html=True)

    # --------------------------------------------------------- PESTAÑA 3
    with tabs[2]:
        st.markdown('<div class="section-title">🛡️ Escenarios de Sensibilidad y Resiliencia</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Determine la robustez de su negocio ante cambios en la ocupación turística o precios de mercado.</div>', unsafe_allow_html=True)
        
        def color_roi(val):
            color = '#f87171' if val < 5 else '#fbbf24' if val < 10 else '#4ade80'
            return f'background-color: {color}; color: #000; font-weight: bold;'

        # 1. Días
        st.subheader("📍 Sensibilidad por Días de Ocupación")
        col_s1_t, col_s1_g = st.columns([1, 1.8], gap="large")
        d_range = [5, 10, 15, 20, 25, 30]
        roi_d = [((((tarifa_base*d*0.85) - cuota - mantenimiento - (tarifa_base*d*0.85*0.05))*12/inv_total)*100) for d in d_range]
        with col_s1_t:
            st.markdown("##### Tabla de Retorno (ROI)")
            df_d = pd.DataFrame({"Días/Mes": d_range, "ROI Anual %": roi_d})
            st.table(df_d.style.map(color_roi, subset=['ROI Anual %']).format({"ROI Anual %": "{:.2f}%"}))
        with col_s1_g:
            fig_d = go.Figure(go.Scatter(x=d_range, y=roi_d, mode='lines+markers', line=dict(color='#60a5fa', width=4), marker=dict(size=10)))
            fig_d.update_layout(title="<b>CURVA DE SENSIBILIDAD: OCUPACIÓN</b>", height=500, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#94a3b8")
            st.plotly_chart(fig_d, use_container_width=True)

        # 2. Tarifa
        st.subheader("💰 Sensibilidad por Tarifa Noche (S/.)")
        col_s2_t, col_s2_g = st.columns([1, 1.8], gap="large")
        t_range = list(range(int(tarifa_base)-40, int(tarifa_base)+60, 10))
        roi_t = [((((t*ocupacion_act*0.85) - cuota - mantenimiento - (t*ocupacion_act*0.85*0.05))*12/inv_total)*100) for t in t_range]
        with col_s2_t:
            st.markdown("##### Tabla de Precios")
            df_t = pd.DataFrame({"Tarifa S/.": t_range, "ROI Anual %": roi_t})
            st.table(df_t.style.map(color_roi, subset=['ROI Anual %']).format({"ROI Anual %": "{:.2f}%"}))
        with col_s2_g:
            fig_t = go.Figure(go.Scatter(x=t_range, y=roi_t, mode='lines+markers', line=dict(color='#34d399', width=4), marker=dict(size=10)))
            fig_t.update_layout(title="<b>CURVA DE SENSIBILIDAD: TARIFA</b>", height=500, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#94a3b8")
            st.plotly_chart(fig_t, use_container_width=True)

        st.markdown('<div class="tip-box">⚠️ <b>Tip de Riesgo:</b> Identifique su "Punto de Equilibrio". En este modelo, con menos de 10 días al mes, el activo requiere inyección de capital para pagar la deuda.</div>', unsafe_allow_html=True)

    # --------------------------------------------------------- PESTAÑA 4
    with tabs[3]:
        st.markdown('<div class="section-title">🏁 Conclusión: Airbnb vs Tradicional</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Comparativa final del flujo de caja disponible anualmente tras todos los costos.</div>', unsafe_allow_html=True)
        
        ventaja = (flujo_neto*12) - utilidad_trad
        cc1, cc2 = st.columns(2)
        with cc1: st.markdown(f'<div class="card-base bg-teal" style="border:1px solid #4ade80;"><div class="label-card">Excedente Anual Airbnb</div><div class="val-pos" style="color:#4ade80;">S/. {ventaja:,.0f}</div></div>', unsafe_allow_html=True)
        with cc2: st.markdown(f'<div class="card-base bg-gray"><div class="label-card">Delta ROI (%)</div><div class="val-pos">+{roi_anual - (utilidad_trad*100/inv_total):.1f}%</div></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="info-box">Gráfico de utilidad neta líquida después de impuestos y servicio de deuda.</div>', unsafe_allow_html=True)
        vals = [flujo_neto*12, utilidad_trad]
        fig_c = go.Figure([go.Bar(
            x=['<b>MODELO AIRBNB</b>', '<b>RENTA ANUAL</b>'], y=vals, 
            marker_color=['#10b981' if v > 0 else '#ef4444' for v in vals],
            text=[f'<b>S/. {v:,.0f}</b>' for v in vals],
            textposition='inside', insidetextanchor='middle',
            textfont=dict(size=28, color='white', family='Inter', fontWeight='bold')
        )])
        fig_c.update_layout(title="<b>UTILIDAD NETA ANUALIZADA</b>", height=600, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#94a3b8")
        st.plotly_chart(fig_c, use_container_width=True)

        st.markdown('<div class="tip-box">🏁 <b>Dictamen Final:</b> El modelo Airbnb genera un flujo de caja significativamente superior, ideal para inversores que buscan liquidez inmediata. El modelo tradicional es preferible solo si se busca una gestión pasiva de "cero esfuerzo".</div>', unsafe_allow_html=True)

# =========================================================
# MOTOR DE PDF (DENSIDAD INFORMATIVA EXTREMA)
# =========================================================
def generate_super_pdf(d):
    pdf = FPDF()
    pdf.add_page()
    # Header Audit
    pdf.set_fill_color(15, 23, 42); pdf.rect(0, 0, 210, 55, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", 'B', 20)
    pdf.cell(0, 20, "AUDITORIA DE FACTIBILIDAD INMOBILIARIA", ln=True, align='C')
    pdf.set_font("Arial", '', 10); pdf.cell(0, 5, "ELABORADO POR: ING. JANCARLO MENDOZA", ln=True, align='C')
    pdf.cell(0, 5, f"LIMA, PERU | GENERADO EL: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align='C')
    pdf.ln(30); pdf.set_text_color(0, 0, 0)

    # Sección 1: Ingeniería de Capital
    pdf.set_font("Arial", 'B', 12); pdf.set_text_color(59, 130, 246)
    pdf.cell(0, 10, "1. MEMORIA ANALITICA DE CAPITAL", ln=True)
    pdf.set_font("Arial", '', 9); pdf.set_text_color(50, 50, 50)
    pdf.multi_cell(0, 5, "Este informe detalla la viabilidad financiera de una propiedad destinada al mercado de renta corta. Se considera el capital inicial propio (20%) y el CAPEX de habilitacion como la base de la inversion real. El apalancamiento bancario ha sido calculado bajo una TCEA competitiva del mercado peruano.")
    pdf.ln(3)
    rows = [["CONCEPTO", "VALOR (S/.)", "COMENTARIO TECNICO"],
            ["Valor Comercial Activo", f"{d['val']:,.0f}", "Valor base de compra"],
            ["Aporte Propio Inicial", f"{d['ini']:,.0f}", "Equity desembolsado"],
            ["Inversion Amoblado", f"{d['inv_a']:,.0f}", "Mobiliario y Equipamiento"],
            ["TOTAL CASH OUT", f"{d['inv_t']:,.0f}", "Inversion Real en Riesgo"]]
    for r in rows:
        pdf.cell(65, 8, r[0], 1); pdf.cell(35, 8, r[1], 1); pdf.cell(90, 8, r[2], 1, ln=True)

    # Sección 2: Flujo de Caja
    pdf.ln(8); pdf.set_font("Arial", 'B', 12); pdf.set_text_color(59, 130, 246)
    pdf.cell(0, 10, "2. PROYECCION DE FLUJO DE CAJA LIBRE (MONTHLY)", ln=True)
    pdf.set_font("Arial", '', 9); pdf.set_text_color(50, 50, 50)
    pdf.multi_cell(0, 5, f"Bajo una ocupacion meta del {d['occ']}%, el activo genera ingresos suficientes para cubrir el servicio de deuda (banco) y gastos operativos. Se ha reservado un 5% de impuesto SUNAT para cumplimiento legal.")
    pdf.ln(2)
    ops = [["Ingresos Brutos Estimados", f"S/. {d['i_b']:,.0f}"], ["Servicio de Deuda Mensual", f"S/. -{d['cuo']:,.0f}"], ["Gastos Operativos + Mtto", f"S/. -{d['gop']:,.0f}"], ["UTILIDAD NETA DISPONIBLE", f"S/. {d['f_n']:,.0f}"]]
    for r in ops:
        pdf.cell(90, 8, r[0], 1); pdf.cell(100, 8, r[1], 1, ln=True)

    # Sección 3: Dictamen
    pdf.ln(8); pdf.set_font("Arial", 'B', 12); pdf.set_text_color(59, 130, 246)
    pdf.cell(0, 10, "3. INDICADORES DE PERFORMANCE Y RIESGO", ln=True)
    pdf.set_font("Arial", '', 9); pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 7, f"- ROI Cash-on-Cash Proyectado: {d['roi']:.2f}% Anual", ln=True)
    pdf.cell(0, 7, f"- Tiempo de Recuperacion de Inversion: {d['pb']:.1f} Años", ln=True)
    pdf.cell(0, 7, f"- Plusvalia Latente Estimada (10A): S/. {d['v10']:,.0f}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'I', 8)
    pdf.multi_cell(0, 4, "IMPORTANTE: Las cifras presentadas son proyecciones basadas en data historica de mercado. "
                         "El Ing. Jancarlo Mendoza recomienda monitorear mensualmente el ADR y la ocupacion "
                         "para ajustar la estrategia de precios dinamicos.")

    return pdf.output(dest='S').encode('latin-1')

if st.session_state.authenticated:
    st.write("---")
    if st.button("📥 DESCARGAR INFORME TÉCNICO COMPLETO (PDF)"):
        v10_calc = (val_depa * (1 + plus_slider/100)**10) - val_depa
        pdf_bytes = generate_super_pdf({
            "val": val_depa, "ini": inicial, "inv_a": inv_amoblado, "inv_t": inv_total,
            "i_b": ingreso_bruto, "cuo": cuota, "gop": gastos_op, "f_n": flujo_neto,
            "roi": roi_anual, "pb": rec, "v10": v10_calc, "occ": (ocupacion_act/30)*100
        })
        st.download_button("Guardar Reporte Auditoría", data=pdf_bytes, file_name=f"Informe_Mendoza_RE_{datetime.now().strftime('%Y%m%d')}.pdf")
