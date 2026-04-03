import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime

# =========================================================
# CONFIGURACIÓN Y ESTILOS
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
    # --- ESTILOS CSS ---
    st.markdown("""
        <style>
        .main { background-color: #0e1117; }
        .val-pos { color: #3b82f6 !important; font-weight: bold; font-size: 1.7rem; }
        .val-neg { color: #ef4444 !important; font-weight: bold; font-size: 1.7rem; }
        div[data-testid="stMetric"] { background-color: #1f2630; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
        .info-text { font-size: 0.85rem; color: #a1a1a1; margin-top: 5px; padding: 10px; border-left: 2px solid #3b82f6; background-color: #161b22; line-height: 1.4; }
        .section-title { margin-top: 30px; margin-bottom: 10px; color: #3b82f6; font-size: 1.3rem; border-bottom: 1px solid #30363d; }
        .highlight-card { background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #3b82f6; text-align: center; }
        </style>
        """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("⚙️ Parámetros de Entrada")
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

    tab1, tab2, tab3, tab4 = st.tabs(["📊 Desglose de Flujos", "📈 Plusvalía", "🛡️ Sensibilidad", "🔄 Comparativa"])

    with tab1:
        st.markdown('<div class="section-title">Estructura de Capital e Ingresos</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"**Inicial Banco (20%)** \n<span class='val-pos'>S/. {inicial_banco:,.0f}</span>", unsafe_allow_html=True)
        c2.markdown(f"**Amoblado/Equipamiento** \n<span class='val-pos'>S/. {inv_amoblado:,.0f}</span>", unsafe_allow_html=True)
        c3.markdown(f"**Inversión Total Real** \n<span class='val-pos'>S/. {inv_total_real:,.0f}</span>", unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">Análisis Operativo Mensual</div>', unsafe_allow_html=True)
        c4, c5, c6, c7 = st.columns(4)
        c4.markdown(f"**Ingreso Airbnb** \n<span class='val-pos'>S/. {ingreso_bruto:,.0f}</span>", unsafe_allow_html=True)
        c5.markdown(f"**Cuota Banco** \n<span class='val-neg'>S/. -{cuota:,.0f}</span>", unsafe_allow_html=True)
        c6.markdown(f"**Costos + Imp.** \n<span class='val-neg'>S/. -{gastos_operativos:,.0f}</span>", unsafe_allow_html=True)
        c7.markdown(f"**Utilidad Neta** \n<span class='val-pos'>S/. {flujo_neto:,.0f}</span>", unsafe_allow_html=True)

        st.markdown('<div class="section-title">Proyección de Payback</div>', unsafe_allow_html=True)
        años_pb = 25; meses = np.arange(0, años_pb*12+1); f_acum = [-inv_total_real]; año_rec = None
        for m in meses[1:]:
            f_acum.append(f_acum[-1] + (flujo_neto if m <= plazo_años*12 else ingreso_bruto-gastos_operativos))
            if año_rec is None and f_acum[-1] >= 0: año_rec = m/12
        
        st.markdown(f'<div class="highlight-card"><h2 style="color:#3b82f6; margin:0;">{año_rec:.1f} Años</h2><p style="color:white; font-size:0.9rem;">TIEMPO ESTIMADO DE RETORNO DE CAPITAL</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="info-text">Este gráfico representa la recuperación del flujo de caja. El área roja indica capital aún no recuperado, mientras que el área azul representa la generación de riqueza neta sobre la inversión inicial.</div>', unsafe_allow_html=True)
        
        fig_pb = go.Figure()
        f_np = np.array(f_acum)
        fig_pb.add_trace(go.Scatter(x=meses/12, y=f_np, line=dict(color='#3b82f6', width=4), name="Flujo Acumulado"))
        fig_pb.add_trace(go.Scatter(x=meses/12, y=np.minimum(f_np, 0), fill='tozeroy', fillcolor='rgba(239, 68, 68, 0.3)', line=dict(color='rgba(0,0,0,0)'), showlegend=False))
        fig_pb.add_trace(go.Scatter(x=meses/12, y=np.maximum(f_np, 0), fill='tozeroy', fillcolor='rgba(59, 130, 246, 0.2)', line=dict(color='rgba(0,0,0,0)'), showlegend=False))
        fig_pb.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", margin=dict(t=10))
        st.plotly_chart(fig_pb, use_container_width=True)

    with tab2:
        st.markdown('<div class="section-title">Análisis de Plusvalía y Patrimonio</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-text">La plusvalía es el aumento del valor comercial del inmueble por factores externos (desarrollo urbano). Las tarjetas muestran la ganancia bruta solo por valorización del activo en el tiempo.</div>', unsafe_allow_html=True)
        plus_slider = st.slider("Ajuste Plusvalía Anual (%)", 0.0, 10.0, 4.0)
        
        c_p = st.columns(4)
        for i, a in enumerate([5, 10, 15, 20]):
            g = (val_depa * (1 + plus_slider/100)**a) - val_depa
            c_p[i].metric(f"Ganancia a {a} Años", f"S/. {g:,.0f}")
        
        st.markdown('<div class="section-title">Gráfico de Crecimiento Patrimonial</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-text">El área sombreada (Equity) representa el valor real de su propiedad después de restar la deuda pendiente con el banco. A medida que pasan los años, su riqueza crece por dos vías: el pago de la deuda y la plusvalía.</div>', unsafe_allow_html=True)
        años_range = np.arange(0, 26); v_mkt = [val_depa * (1+plus_slider/100)**a for a in años_range]
        equity = [v - (prestamo * (1 - a/plazo_años) if a < plazo_años else 0) for a, v in zip(años_range, v_mkt)]
        fig_p = go.Figure()
        fig_p.add_trace(go.Bar(x=años_range, y=v_mkt, name="Valor de Mercado", marker_color='#1f2630'))
        fig_p.add_trace(go.Scatter(x=años_range, y=equity, name="Equity Real", fill='tozeroy', fillcolor='rgba(0, 255, 204, 0.2)', line=dict(color='#00ffcc', width=4)))
        fig_p.update_layout(height=450, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", xaxis_title="Años")
        st.plotly_chart(fig_p, use_container_width=True)

    with tab3:
        st.markdown('<div class="section-title">Análisis de Resiliencia y Riesgo</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-text">Estas matrices permiten entender cómo varía la rentabilidad ante cambios en la operación. Un ROI superior al 8% se considera óptimo para el mercado de Lima.</div>', unsafe_allow_html=True)
        
        # Ocupación cada 5 días
        st.subheader("1. Sensibilidad por Días de Ocupación")
        st.markdown('<div class="info-text">Muestra cuántos días al mes debe estar alquilado el departamento para mantener un ROI positivo.</div>', unsafe_allow_html=True)
        col_s1_t, col_s1_g = st.columns([1, 1.5])
        d_range = [5, 10, 15, 20, 25, 30]
        roi_o = [((((tarifa_base*d*0.85) - cuota - mantenimiento - (tarifa_base*d*0.85*0.05))*12/inv_total_real)*100) for d in d_range]
        with col_s1_t:
            st.dataframe(pd.DataFrame({"Días al Mes": d_range, "ROI Anual %": roi_o}).style.background_gradient(cmap='RdYlGn', subset=['ROI Anual %']).format("{:.2f}%"), use_container_width=True)
        with col_s1_g:
            fig_o = go.Figure(go.Scatter(x=d_range, y=roi_o, mode='lines+markers', line=dict(color='#3b82f6', width=4)))
            fig_o.update_layout(height=500, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", xaxis_title="Días Ocupados")
            st.plotly_chart(fig_o, use_container_width=True)

        # Tarifa cada 10 soles
        st.subheader("2. Sensibilidad por Tarifa Noche (S/.)")
        st.markdown('<div class="info-text">Analiza el impacto de subir o bajar el precio por noche manteniendo la ocupación actual.</div>', unsafe_allow_html=True)
        col_s2_t, col_s2_g = st.columns([1, 1.5])
        t_range = list(range(int(tarifa_base)-40, int(tarifa_base)+50, 10))
        roi_t = [((((t*ocupacion_act*0.85) - cuota - mantenimiento - (t*ocupacion_act*0.85*0.05))*12/inv_total_real)*100) for t in t_range]
        with col_s2_t:
            st.dataframe(pd.DataFrame({"Tarifa S/.": t_range, "ROI Anual %": roi_t}).style.background_gradient(cmap='RdYlGn', subset=['ROI Anual %']).format("{:.2f}%"), use_container_width=True)
        with col_s2_g:
            fig_t = go.Figure(go.Scatter(x=t_range, y=roi_t, mode='lines+markers', line=dict(color='#00ffcc', width=4)))
            fig_t.update_layout(height=500, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", xaxis_title="Tarifa por Noche (S/.)")
            st.plotly_chart(fig_t, use_container_width=True)

    with tab4:
        st.markdown('<div class="section-title">Airbnb vs Alquiler Tradicional</div>', unsafe_allow_html=True)
        ventaja_anual = (flujo_neto*12) - u_anual_trad
        col_c1, col_c2 = st.columns(2)
        col_c1.metric("Ventaja Airbnb (Anual)", f"S/. {ventaja_anual:,.0f}")
        col_c2.metric("Punto de Equilibrio (Días)", f"{np.ceil((cuota+mantenimiento)/(tarifa_base*0.85*0.95)):.0f} días")
        
        fig_c = go.Figure([go.Bar(
            x=['<b>AIRBNB</b>', '<b>TRADICIONAL</b>'], 
            y=[flujo_neto*12, u_anual_trad], 
            marker_color=['#3b82f6', '#1b2635'],
            text=[f'<b>S/. {flujo_neto*12:,.0f}</b>', f'<b>S/. {u_anual_trad:,.0f}</b>'],
            textposition='inside',
            insidetextanchor='middle',
            textfont=dict(size=26, color='white')
        )])
        fig_c.update_layout(title="UTILIDAD NETA ANUALIZADA", height=550, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_c, use_container_width=True)

# =========================================================
# MOTOR DE PDF (DENSIDAD INFORMATIVA MAXIMA)
# =========================================================

def generate_full_pdf(d):
    pdf = FPDF()
    pdf.add_page()
    # Header Pro
    pdf.set_fill_color(31, 38, 48); pdf.rect(0, 0, 210, 50, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", 'B', 18)
    pdf.cell(0, 20, "AUDITORIA TECNICA Y ANALISIS DE RENTABILIDAD", ln=True, align='C')
    pdf.set_font("Arial", '', 10); pdf.cell(0, 5, "ELABORADO POR: ING. JANCARLO MENDOZA - CONSULTORIA REAL ESTATE", ln=True, align='C')
    pdf.cell(0, 5, f"LIMA, PERU | {datetime.now().strftime('%d/%m/%Y')}", ln=True, align='C')
    pdf.ln(25); pdf.set_text_color(0, 0, 0)

    # Bloque 1: Inversión
    pdf.set_font("Arial", 'B', 12); pdf.set_text_color(59, 130, 246)
    pdf.cell(0, 10, "1. MEMORIA DESCRIPTIVA DE LA INVERSION", ln=True)
    pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", '', 9)
    pdf.multi_cell(0, 5, "El presente informe detalla la viabilidad financiera de un activo inmobiliario destinado al mercado de rentas de corta estancia (Airbnb). Se asume una estructura de financiamiento estandar del 80% LTV con una TCEA competitiva. La inversion inicial no solo cubre la cuota inicial, sino tambien la puesta en marcha operativa (amoblado de alto transito).")
    pdf.ln(3)
    
    data = [["Rubro de Inversion", "Monto Unitario", "Observacion"], 
            ["Precio Inmueble", f"S/. {d['val']:,.0f}", "Valor comercial estimado"],
            ["Cuota Inicial (20%)", f"S/. {d['val']*0.2:,.0f}", "Capital liquido"],
            ["Equipamiento Pro", f"S/. {d['inv_a']:,.0f}", "Mobiliario y tecnologia"],
            ["TOTAL CASH-OUT", f"S/. {d['inv_t']:,.0f}", "Inversion Real Total"]]
    
    pdf.set_font("Arial", 'B', 9)
    for row in data:
        pdf.cell(70, 8, row[0], 1); pdf.cell(40, 8, row[1], 1); pdf.cell(70, 8, row[2], 1, ln=True)

    # Bloque 2: Operación
    pdf.ln(5); pdf.set_font("Arial", 'B', 12); pdf.set_text_color(59, 130, 246)
    pdf.cell(0, 10, "2. PROYECCION OPERATIVA MENSUAL", ln=True)
    pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", '', 9)
    pdf.multi_cell(0, 5, f"Basado en un escenario de ocupacion del {d['occ']}%, se proyecta una generacion de ingresos brutos de S/. {d['i_b']:,.0f} mensuales. Tras deducir el servicio de deuda y gastos de mantenimiento, el activo genera un flujo de caja neto positivo.")
    pdf.ln(2)
    ops = [["Ingresos Brutos (Airbnb)", f"S/. {d['i_b']:,.0f}"], ["Cuota Hipotecaria", f"S/. -{d['cuo']:,.0f}"], ["Gasto Operativo (Limpieza/Mtto)", f"S/. -{d['mant']:,.0f}"], ["Reserva Impositiva (IR 5%)", f"S/. -{d['imp']:,.0f}"], ["NET CASH FLOW", f"S/. {d['f_n']:,.0f}"]]
    for row in ops:
        pdf.cell(100, 8, row[0], 1); pdf.cell(80, 8, row[1], 1, ln=True)

    # Bloque 3: KPIs
    pdf.ln(5); pdf.set_font("Arial", 'B', 12); pdf.set_text_color(59, 130, 246)
    pdf.cell(0, 10, "3. INDICADORES DE RENDIMIENTO (KPIs)", ln=True)
    pdf.set_font("Arial", '', 9); pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 6, f"- ROI Cash-on-Cash: {d['roi']:.2f}% (Rendimiento sobre capital invertido)", ln=True)
    pdf.cell(0, 6, f"- Payback Period: {d['pb']:.1f} Años (Punto de equilibrio de capital)", ln=True)
    pdf.cell(0, 6, f"- Plusvalia Proyectada (20A): S/. {d['v20']:,.0f} (Crecimiento patrimonial)", ln=True)
    pdf.cell(0, 6, f"- Ventaja Airbnb vs Tradicional: +S/. {d['v_a']:,.0f} Anuales", ln=True)

    # Bloque 4: Glosario Técnico
    pdf.ln(5); pdf.set_font("Arial", 'B', 10); pdf.cell(0, 8, "GLOSARIO TECNICO:", ln=True)
    pdf.set_font("Arial", 'I', 8)
    pdf.multi_cell(0, 4, "- TCEA: Tasa de Costo Efectivo Anual. Incluye intereses, comisiones y seguros.\n- ROI: Return on Investment. Relacion entre la utilidad neta anual y la inversion inicial.\n- EQUITY: La porción de la propiedad que es realmente suya (Valor Mercado - Saldo Deuda).\n- PLUSVALIA: Incremento del valor de un inmueble debido a la evolucion del entorno urbano.")

    return pdf.output(dest='S').encode('latin-1')

if st.session_state.authenticated:
    st.write("---")
    if st.button("📥 GENERAR AUDITORIA TECNICA COMPLETA (PDF)"):
        v20_calc = val_depa * (1 + plus_slider/100)**20
        pdf_bytes = generate_full_pdf({
            "val": val_depa, "inv_a": inv_amoblado, "inv_t": inv_total_real, "i_b": ingreso_bruto,
            "cuo": cuota, "mant": mantenimiento, "imp": impuesto, "f_n": flujo_neto,
            "roi": roi_anual, "pb": año_rec if año_rec else 0, "v_a": ventaja_anual,
            "v20": v20_calc, "occ": (ocupacion_act/30)*100, "p_a": plus_slider
        })
        st.download_button("Descargar Informe JM Auditoría", data=pdf_bytes, file_name=f"Auditoria_Mendoza_B2_{datetime.now().strftime('%Y%m%d')}.pdf")
