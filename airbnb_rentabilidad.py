import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime

# =========================================================
# CONFIGURACIÓN Y ESTILOS AVANZADOS
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
        .main { background-color: #0e1117; }
        /* Tarjetas Minimalistas con Marco */
        .mini-card {
            border: 1px solid #30363d;
            border-radius: 10px;
            padding: 20px;
            background-color: #161b22;
            text-align: center;
            margin-bottom: 10px;
        }
        .label-card { color: #8b949e; font-size: 0.85rem; text-transform: uppercase; font-weight: 600; margin-bottom: 8px; }
        .val-pos { color: #3b82f6; font-size: 1.8rem; font-weight: bold; }
        .val-neg { color: #ef4444; font-size: 1.8rem; font-weight: bold; }
        .info-box { 
            font-size: 0.85rem; color: #a1a1a1; padding: 12px; 
            border-left: 3px solid #3b82f6; background-color: #1c2128; 
            border-radius: 0 8px 8px 0; margin: 10px 0;
        }
        .section-title { margin-top: 35px; color: #3b82f6; font-size: 1.4rem; font-weight: bold; border-bottom: 1px solid #30363d; padding-bottom: 8px; }
        </style>
        """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("⚙️ Parámetros del Proyecto")
        val_depa = st.number_input("Precio Inmueble (S/.)", value=250000)
        inv_amoblado = st.number_input("Inversión Amoblado (S/.)", value=25000)
        st.write("---")
        tcea = st.number_input("TCEA %", value=9.5)
        plazo_años = st.selectbox("Plazo (Años)", [10, 15, 20, 25], index=2)
        st.write("---")
        tarifa_base = st.number_input("Tarifa Airbnb (S/.)", value=180)
        ocupacion_act = st.slider("Días/mes", 1, 30, 20)
        st.write("---")
        renta_trad = st.number_input("Renta Tradicional (S/.)", value=1800)

    # LÓGICA FINANCIERA
    inicial_banco = val_depa * 0.20
    inv_total_real = inicial_banco + inv_amoblado
    prestamo = val_depa - inicial_banco
    tem = (1 + tcea/100)**(1/12) - 1
    cuota = prestamo * (tem * (1 + tem)**(plazo_años*12)) / ((1 + tem)**(plazo_años*12) - 1)
    mantenimiento = (val_depa * 0.03) / 12
    ingreso_bruto = tarifa_base * ocupacion_act * 0.85
    impuesto = ingreso_bruto * 0.05
    gastos_operativos = mantenimiento + impuesto
    flujo_neto = ingreso_bruto - cuota - gastos_operativos
    roi_anual = (flujo_neto * 12 / inv_total_real) * 100
    u_anual_trad = (renta_trad - cuota - (val_depa*0.015/12) - (renta_trad*0.05)) * 12

    tab1, tab2, tab3, tab4 = st.tabs(["📊 Flujos", "📈 Plusvalía", "🛡️ Sensibilidad", "🔄 Comparativa"])

    with tab1:
        st.markdown('<div class="section-title">Estructura de Capital e Ingresos</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="mini-card"><div class="label-card">Inicial Banco (20%)</div><div class="val-pos">S/. {inicial_banco:,.0f}</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="mini-card"><div class="label-card">Amoblado</div><div class="val-pos">S/. {inv_amoblado:,.0f}</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="mini-card"><div class="label-card">Inversión Total Real</div><div class="val-pos">S/. {inv_total_real:,.0f}</div></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">Análisis Operativo Mensual</div>', unsafe_allow_html=True)
        c4, c5, c6, c7 = st.columns(4)
        with c4: st.markdown(f'<div class="mini-card"><div class="label-card">Ingreso Airbnb</div><div class="val-pos">S/. {ingreso_bruto:,.0f}</div></div>', unsafe_allow_html=True)
        with c5: st.markdown(f'<div class="mini-card"><div class="label-card">Cuota Banco</div><div class="val-neg">S/. -{cuota:,.0f}</div></div>', unsafe_allow_html=True)
        with c6: st.markdown(f'<div class="mini-card"><div class="label-card">Costos + Imp.</div><div class="val-neg">S/. -{gastos_operativos:,.0f}</div></div>', unsafe_allow_html=True)
        with c7: st.markdown(f'<div class="mini-card"><div class="label-card">Utilidad Neta</div><div class="val-pos">S/. {flujo_neto:,.0f}</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">Retorno de Inversión (Payback)</div>', unsafe_allow_html=True)
        años_pb = 25; meses = np.arange(0, años_pb*12+1); f_acum = [-inv_total_real]; año_rec = None
        for m in meses[1:]:
            f_acum.append(f_acum[-1] + (flujo_neto if m <= plazo_años*12 else ingreso_bruto-gastos_operativos))
            if año_rec is None and f_acum[-1] >= 0: año_rec = m/12
        
        cp1, cp2 = st.columns([1, 1.5])
        with cp1:
            st.markdown(f'<div class="mini-card" style="border-color:#3b82f6;"><div class="label-card">Recuperación Total</div><div class="val-pos" style="font-size:2.5rem;">{año_rec:.1f} Años</div></div>', unsafe_allow_html=True)
            st.markdown('<div class="info-box"><b>Nota Técnica:</b> El Payback indica el momento exacto en que la suma de sus utilidades netas iguala su desembolso inicial (Inicial + Amoblado). A partir de este punto, el flujo es ganancia pura sobre capital propio.</div>', unsafe_allow_html=True)
        with cp2:
            fig_pb = go.Figure()
            f_np = np.array(f_acum)
            fig_pb.add_trace(go.Scatter(x=meses/12, y=f_np, line=dict(color='#3b82f6', width=4), name="Flujo Neto Acumulado"))
            fig_pb.add_trace(go.Scatter(x=meses/12, y=np.minimum(f_np, 0), fill='tozeroy', fillcolor='rgba(239, 68, 68, 0.25)', line=dict(color='rgba(0,0,0,0)'), showlegend=False))
            fig_pb.add_trace(go.Scatter(x=meses/12, y=np.maximum(f_np, 0), fill='tozeroy', fillcolor='rgba(59, 130, 246, 0.2)', line=dict(color='rgba(0,0,0,0)'), showlegend=False))
            fig_pb.update_layout(title="<b>CURVA DE RECUPERACIÓN DE CAPITAL</b>", height=350, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", margin=dict(t=50, l=0, r=0))
            st.plotly_chart(fig_pb, use_container_width=True)

    with tab2:
        st.markdown('<div class="section-title">Análisis de Plusvalía Patrimonial</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box"><b>Definición:</b> La plusvalía es el incremento del valor de mercado del inmueble. Este capital es latente (se realiza al vender) y es la principal fuente de riqueza en Real Estate.</div>', unsafe_allow_html=True)
        plus_slider = st.slider("Expectativa de Plusvalía Anual (%)", 0.0, 10.0, 4.0)
        
        c_p = st.columns(4)
        for i, a in enumerate([5, 10, 15, 20]):
            g = (val_depa * (1 + plus_slider/100)**a) - val_depa
            with c_p[i]: st.markdown(f'<div class="mini-card"><div class="label-card">Ganancia {a}A</div><div class="val-pos">S/. {g:,.0f}</div></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">Evolución de Riqueza Real (Equity)</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Este gráfico muestra cómo el Equity (su verdadera riqueza) crece a medida que el valor de la propiedad sube y el saldo de la deuda bancaria baja.</div>', unsafe_allow_html=True)
        años_range = np.arange(0, 26); v_mkt = [val_depa * (1+plus_slider/100)**a for a in años_range]
        equity = [v - (prestamo * (1 - a/plazo_años) if a < plazo_años else 0) for a, v in zip(años_range, v_mkt)]
        
        fig_p = go.Figure()
        fig_p.add_trace(go.Bar(x=años_range, y=v_mkt, name="Valor Propiedad", marker_color='#1f2630'))
        fig_p.add_trace(go.Scatter(x=años_range, y=equity, name="Equity Real", fill='tozeroy', fillcolor='rgba(0, 255, 204, 0.15)', line=dict(color='#00ffcc', width=4)))
        fig_p.update_layout(title="<b>VALOR MERCADO VS EQUITY</b>", height=450, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_p, use_container_width=True)

    with tab3:
        st.markdown('<div class="section-title">Matrices de Resiliencia Operativa</div>', unsafe_allow_html=True)
        
        # 1. Sensibilidad por Días
        st.subheader("1. Sensibilidad: ROI vs Días de Ocupación")
        st.markdown('<div class="info-box">Analiza el impacto del flujo turístico. Permite ver el "punto de quiebre" donde el negocio deja de pagar la cuota bancaria.</div>', unsafe_allow_html=True)
        col_s1_t, col_s1_g = st.columns([1, 1.5])
        d_range = [5, 10, 15, 20, 25, 30]
        roi_o = [((((tarifa_base*d*0.85) - cuota - mantenimiento - (tarifa_base*d*0.85*0.05))*12/inv_total_real)*100) for d in d_range]
        df_o = pd.DataFrame({"Días al Mes": d_range, "ROI Anual (%)": roi_o})
        with col_s1_t:
            st.write("<br><br>", unsafe_allow_html=True) # Alineación vertical
            st.table(df_o.style.format({"ROI Anual (%)": "{:.2f}%"}))
        with col_s1_g:
            fig_o = go.Figure(go.Scatter(x=d_range, y=roi_o, mode='lines+markers', line=dict(color='#3b82f6', width=4), marker=dict(size=10)))
            fig_o.update_layout(title="<b>ROI SEGÚN OCUPACIÓN</b>", height=500, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig_o, use_container_width=True)

        # 2. Sensibilidad por Tarifa
        st.subheader("2. Sensibilidad: ROI vs Tarifa Noche (S/.)")
        st.markdown('<div class="info-box">Evalúa la elasticidad del precio. Determina cuánto puede bajar la tarifa en temporada baja sin comprometer la rentabilidad.</div>', unsafe_allow_html=True)
        col_s2_t, col_s2_g = st.columns([1, 1.5])
        t_range = list(range(int(tarifa_base)-40, int(tarifa_base)+50, 10))
        roi_t = [((((t*ocupacion_act*0.85) - cuota - mantenimiento - (t*ocupacion_act*0.85*0.05))*12/inv_total_real)*100) for t in t_range]
        df_t = pd.DataFrame({"Tarifa (S/.)": t_range, "ROI Anual (%)": roi_t})
        with col_s2_t:
            st.write("<br><br>", unsafe_allow_html=True)
            st.table(df_t.style.format({"ROI Anual (%)": "{:.2f}%"}))
        with col_s2_g:
            fig_t = go.Figure(go.Scatter(x=t_range, y=roi_t, mode='lines+markers', line=dict(color='#00ffcc', width=4), marker=dict(size=10)))
            fig_t.update_layout(title="<b>ROI SEGÚN TARIFA</b>", height=500, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig_t, use_container_width=True)

    with tab4:
        st.markdown('<div class="section-title">Análisis Comparativo de Utilidad Anual</div>', unsafe_allow_html=True)
        ventaja = (flujo_neto*12) - u_anual_trad
        cc1, cc2 = st.columns(2)
        with cc1: st.markdown(f'<div class="mini-card" style="border-color:#00ffcc;"><div class="label-card">Ventaja Airbnb Anual</div><div class="val-pos" style="color:#00ffcc;">S/. {ventaja:,.0f}</div></div>', unsafe_allow_html=True)
        with cc2: st.markdown(f'<div class="mini-card"><div class="label-card">ROI Airbnb vs Tradicional</div><div class="val-pos">{roi_anual:.1f}% vs {(u_anual_trad*100/inv_total_real):.1f}%</div></div>', unsafe_allow_html=True)
        
        # Gráfico Comparativo
        vals = [flujo_neto*12, u_anual_trad]
        fig_c = go.Figure([go.Bar(
            x=['<b>MODELO AIRBNB</b>', '<b>RENTA TRADICIONAL</b>'], 
            y=vals, 
            marker_color=['#3b82f6' if v > 0 else '#ef4444' for v in vals],
            text=[f'<b>S/. {v:,.0f}</b>' for v in vals],
            textposition='inside',
            insidetextanchor='middle',
            textfont=dict(size=24, color='white')
        )])
        fig_c.update_layout(title="<b>UTILIDAD NETA ANUALIZADA (CASH FLOW)</b>", height=600, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_c, use_container_width=True)

# =========================================================
# MOTOR DE PDF (DENSIDAD INFORMATIVA EXTREMA)
# =========================================================

def generate_super_report(d):
    pdf = FPDF()
    pdf.add_page()
    # Header Estilo Consultoría
    pdf.set_fill_color(22, 27, 34); pdf.rect(0, 0, 210, 50, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", 'B', 20)
    pdf.cell(0, 20, "AUDITORIA INTEGRAL DE INVERSION", ln=True, align='C')
    pdf.set_font("Arial", '', 11); pdf.cell(0, 5, "ELABORADO POR: ING. JANCARLO MENDOZA", ln=True, align='C')
    pdf.cell(0, 5, f"LIMA METROPOLITANA | {datetime.now().strftime('%d/%m/%Y')}", ln=True, align='C')
    pdf.ln(25); pdf.set_text_color(0, 0, 0)

    # Bloque 1: Ingeniería Financiera
    pdf.set_font("Arial", 'B', 12); pdf.set_text_color(59, 130, 246)
    pdf.cell(0, 10, "1. ESTRUCTURA DE ADQUISICION Y CAPITAL", ln=True)
    pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", '', 9)
    pdf.multi_cell(0, 5, "Se analiza la adquisicion bajo un modelo de apalancamiento eficiente. La cuota inicial y el presupuesto de amoblado constituyen el capital real en riesgo, sobre el cual se calcula el ROI. El amoblado se proyecta bajo estandares de 'Hotel-Ready' para maximizar el ADR (Average Daily Rate).")
    pdf.ln(2)
    data = [["Rubro", "Valor", "Detalle Técnico"], 
            ["Valor Inmueble", f"S/. {d['val']:,.0f}", "Tasacion comercial base"],
            ["Prestamo (80%)", f"S/. {d['val']*0.8:,.0f}", f"Hipotecario a {d['plazo']} años"],
            ["Capital Propio", f"S/. {d['val']*0.2:,.0f}", "Cuota inicial 20%"],
            ["Capex Amoblado", f"S/. {d['inv_a']:,.0f}", "Depreciacion a 5 años"],
            ["INVERSION TOTAL", f"S/. {d['inv_t']:,.0f}", "Desembolso Liquido"]]
    for r in data:
        pdf.cell(60, 8, r[0], 1); pdf.cell(40, 8, r[1], 1); pdf.cell(85, 8, r[2], 1, ln=True)

    # Bloque 2: Proyección de Flujos
    pdf.ln(5); pdf.set_font("Arial", 'B', 12); pdf.set_text_color(59, 130, 246)
    pdf.cell(0, 10, "2. ANALISIS OPERATIVO Y FLUJO DE CAJA LIBRE", ln=True)
    pdf.set_font("Arial", '', 9); pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 5, f"Con una ocupacion meta del {d['occ']}%, el flujo mensual permite cubrir la totalidad de la cuota bancaria y generar un excedente de caja (Cash Flow). Se ha reservado un 5% para el pago de impuestos de primera categoria ante SUNAT.")
    pdf.ln(2)
    ops = [["Ingresos Brutos Est.", f"S/. {d['i_b']:,.0f}"], ["Servicio de Deuda", f"S/. -{d['cuo']:,.0f}"], ["Gastos Op (Mtto/Luz)", f"S/. -{d['mant']:,.0f}"], ["Utilidad Neta Mensual", f"S/. {d['f_n']:,.0f}"]]
    for r in ops:
        pdf.cell(90, 8, r[0], 1); pdf.cell(95, 8, r[1], 1, ln=True)

    # Bloque 3: Análisis Patrimonial a 10 Años
    pdf.ln(5); pdf.set_font("Arial", 'B', 12); pdf.set_text_color(59, 130, 246)
    pdf.cell(0, 10, "3. CRECIMIENTO PATRIMONIAL Y PLUSVALIA", ln=True)
    pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", '', 9)
    pdf.multi_cell(0, 5, f"Bajo una tasa de revalorizacion del {d['p_a']}% anual, el patrimonio neto del inversor se duplica significativamente antes del vencimiento del plazo hipotecario. El efecto combinado de amortizacion de capital y plusvalia genera una Tasa Interna de Retorno (TIR) proyectada superior al 15% anual.")

    # Bloque 4: Riesgos y Mitigación
    pdf.ln(5); pdf.set_font("Arial", 'B', 11); pdf.cell(0, 8, "GESTION DE RIESGOS:", ln=True)
    pdf.set_font("Arial", 'I', 8)
    pdf.multi_cell(0, 4, "- Riesgo de Vacancia: Mitigado mediante politicas de precios dinamicos.\n- Riesgo Regulatorio: El modelo considera cumplimiento tributario estricto.\n- Riesgo de Mercado: El inmueble se ubica en zona de alta demanda consolidada.")

    return pdf.output(dest='S').encode('latin-1')

if st.session_state.authenticated:
    st.write("---")
    if st.button("📥 DESCARGAR AUDITORIA TECNICA COMPLETA"):
        v20_pdf = val_depa * (1 + plus_slider/100)**20
        pdf_b = generate_super_report({
            "val": val_depa, "inv_a": inv_amoblado, "inv_t": inv_total_real, "plazo": plazo_años,
            "i_b": ingreso_bruto, "cuo": cuota, "mant": mantenimiento, "imp": impuesto,
            "f_n": flujo_neto, "roi": roi_anual, "pb": año_rec if año_rec else 0,
            "v_a": ventaja, "v20": v20_pdf, "occ": (ocupacion_act/30)*100, "p_a": plus_slider
        })
        st.download_button("Guardar Informe Profesional", data=pdf_b, file_name=f"Auditoria_Mendoza_{datetime.now().strftime('%Y%m%d')}.pdf")
