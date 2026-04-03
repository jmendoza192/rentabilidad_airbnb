import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime

# =========================================================
# BLOQUE 1: INTERFAZ WEB V37 (OPTIMIZACIÓN VISUAL CRÍTICA)
# =========================================================

try:
    st.set_page_config(page_title="Auditoría Pro | Jancarlo Mendoza", layout="wide")
except:
    pass

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
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
        [data-testid="stMetricValue"] { font-size: 1.8rem !important; color: #00ffcc; font-weight: bold; }
        div[data-testid="stMetric"] { background-color: #1f2630; padding: 20px; border-radius: 12px; border: 1px solid #30363d; }
        .info-text { font-size: 0.9rem; color: #a1a1a1; margin-top: 10px; padding: 12px; border-left: 2px solid #3b82f6; background-color: #161b22; line-height: 1.5; }
        .section-title { margin-top: 35px; margin-bottom: 12px; color: #3b82f6; font-size: 1.45rem; border-bottom: 1px solid #30363d; padding-bottom: 5px; }
        .highlight-card { background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #3b82f6; text-align: center; }
        .flow-card { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; height: 100%; }
        .flow-val { font-size: 1.2rem; font-weight: bold; }
        .flow-label { font-size: 0.8rem; color: #3b82f6; text-transform: uppercase; font-weight: 600; }
        </style>
        """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("⚙️ Parámetros")
        val_depa = st.number_input("Precio Inmueble (S/.)", value=250000)
        inv_amoblado = st.number_input("Inversión Amoblado (S/.)", value=25000)
        st.write("---")
        tcea = st.number_input("TCEA %", value=9.5)
        plazo_años = st.selectbox("Plazo (Años)", [10, 15, 20, 25], index=2)
        st.write("---")
        tarifa = st.number_input("Tarifa Airbnb (S/.)", value=180)
        ocupacion_act = st.slider("Días/mes", 1, 30, 20)
        st.write("---")
        renta_trad = st.number_input("Renta Tradicional (S/.)", value=1800)

    # Lógica Financiera
    inicial_banco = val_depa * 0.20
    inv_total_real = inicial_banco + inv_amoblado
    prestamo = val_depa - inicial_banco
    tem = (1 + tcea/100)**(1/12) - 1
    cuota = prestamo * (tem * (1 + tem)**(plazo_años*12)) / ((1 + tem)**(plazo_años*12) - 1)
    mantenimiento = (val_depa * 0.03) / 12
    ingreso_bruto = tarifa * ocupacion_act * 0.85
    impuesto = ingreso_bruto * 0.05
    flujo_neto = ingreso_bruto - cuota - mantenimiento - impuesto
    roi_anual = (flujo_neto * 12 / inv_total_real) * 100
    u_anual_trad = (renta_trad - cuota - (val_depa*0.015/12) - (renta_trad*0.05)) * 12

    tab1, tab2, tab3, tab4 = st.tabs(["📊 Flujos", "📈 Plusvalía", "🛡️ Sensibilidad", "🔄 Comparativa"])

    with tab1:
        st.markdown('<div class="section-title">Desembolso Inicial</div>', unsafe_allow_html=True)
        st.metric("Inversión Total Real", f"S/. {inv_total_real:,.0f}")
        st.markdown('<div class="info-text">Capital líquido inicial: 20% inicial + amoblado.</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">Proyección de Payback</div>', unsafe_allow_html=True)
        años_pb = 25; meses = np.arange(0, años_pb*12+1); f_acum = [-inv_total_real]
        año_rec = None
        for m in meses[1:]:
            f_acum.append(f_acum[-1] + (flujo_neto if m <= plazo_años*12 else ingreso_bruto-mantenimiento-impuesto))
            if año_rec is None and f_acum[-1] >= 0: año_rec = m/12
        
        c1, c2 = st.columns([1, 3])
        with c1:
            st.markdown(f'<div class="highlight-card"><h2 style="color:#3b82f6;">{año_rec:.1f} Años</h2><p style="color:white; font-size:0.8rem;">RECUPERACIÓN TOTAL</p></div>', unsafe_allow_html=True)
            st.markdown('<div class="info-text">Punto de retorno del capital líquido invertido.</div>', unsafe_allow_html=True)
        with c2:
            fig_pb = go.Figure()
            f_np = np.array(f_acum)
            fig_pb.add_trace(go.Scatter(x=meses/12, y=f_np, fill='tozeroy', line=dict(color='#3b82f6', width=3)))
            # Sombreado Rojo/Verde
            fig_pb.add_trace(go.Scatter(x=meses/12, y=np.minimum(f_np, 0), fill='tozeroy', fillcolor='rgba(239, 68, 68, 0.3)', line=dict(color='rgba(0,0,0,0)'), showlegend=False))
            fig_pb.add_trace(go.Scatter(x=meses/12, y=np.maximum(f_np, 0), fill='tozeroy', fillcolor='rgba(16, 185, 129, 0.3)', line=dict(color='rgba(0,0,0,0)'), showlegend=False))
            fig_pb.update_layout(title="Curva de Recuperación Acumulada", height=350, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig_pb, use_container_width=True)

    with tab2:
        st.markdown('<div class="section-title">Crecimiento Patrimonial y Plusvalía</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-text">Apreciación del inmueble proyectada por el mercado.</div>', unsafe_allow_html=True)
        p_anual = st.slider("Plusvalía %", 0.0, 10.0, 4.0)
        
        # Ganancia a distintos años
        c_p = st.columns(4)
        for i, a in enumerate([5, 10, 15, 20]):
            g = (val_depa * (1 + p_anual/100)**a) - val_depa
            c_p[i].metric(f"Ganancia {a}A", f"S/. {g:,.0f}")
            
        años_range = np.arange(0, 26)
        v_mkt = [val_depa * (1+p_anual/100)**a for a in años_range]
        equity = [v - (prestamo * (1 - a/plazo_años) if a < plazo_años else 0) for a, v in zip(años_range, v_mkt)]
        
        fig_p = go.Figure()
        fig_p.add_trace(go.Bar(x=años_range, y=v_mkt, name="Valor Mercado", marker_color='#1f2630'))
        fig_p.add_trace(go.Scatter(x=años_range, y=equity, name="Equity (Propiedad Real)", fill='tozeroy', fillcolor='rgba(0, 255, 204, 0.2)', line=dict(color='#00ffcc', width=4)))
        fig_p.update_layout(title="Proyección de Valor vs Deuda Pendiente", height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_p, use_container_width=True)

    with tab3:
        # Sensibilidad 1: ROI vs Ocupación
        st.markdown('<div class="section-title">Sensibilidad: ROI vs Ocupación</div>', unsafe_allow_html=True)
        d_range = np.arange(10, 31, 2)
        roi_o = [((( (tarifa*d*0.85) - cuota - mantenimiento - (tarifa*d*0.85*0.05))*12/inv_total_real)*100) for d in d_range]
        df_o = pd.DataFrame({"Días": d_range, "ROI %": roi_o})
        st.dataframe(df_o.style.background_gradient(cmap='RdYlGn', subset=['ROI %']).format("{:.2f}%"))
        fig_o = go.Figure(go.Scatter(x=d_range, y=roi_o, mode='lines+markers', line=dict(color='#3b82f6')))
        fig_o.update_layout(title="ROI según Días de Ocupación", height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_o, use_container_width=True)

        # Sensibilidad 2: ROI vs Precio Compra (Variación)
        st.markdown('<div class="section-title">Sensibilidad: ROI vs Precio de Adquisición</div>', unsafe_allow_html=True)
        p_vars = [-10, -5, 0, 5, 10]
        roi_p = [ (flujo_neto*12 / ( (val_depa*(1+v/100)*0.2)+inv_amoblado ) * 100) for v in p_vars]
        df_p = pd.DataFrame({"Var. Precio %": p_vars, "ROI %": roi_p})
        st.dataframe(df_p.style.background_gradient(cmap='RdYlGn_r', subset=['ROI %']).format("{:.2f}%"))
        fig_p2 = go.Figure(go.Bar(x=p_vars, y=roi_p, marker_color='#3b82f6'))
        fig_p2.update_layout(title="Impacto del Precio de Compra en el Retorno", height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_p2, use_container_width=True)

    with tab4:
        st.markdown('<div class="section-title">Comparativa: Airbnb vs Tradicional</div>', unsafe_allow_html=True)
        col_c = st.columns([1, 2])
        ventaja = (flujo_neto*12) - u_anual_trad
        with col_c[0]:
            st.markdown(f'<div class="highlight-card"><h3>S/. {ventaja:,.0f}</h3><p>VENTAJA ANUAL AIRBNB</p></div>', unsafe_allow_html=True)
            st.markdown('<div class="info-text">Diferencial de ganancia neta anualizada.</div>', unsafe_allow_html=True)
        with col_c[1]:
            fig_c = go.Figure([go.Bar(
                x=['Airbnb', 'Tradicional'], 
                y=[flujo_neto*12, u_anual_trad], 
                marker_color=['#3b82f6', '#10b981'],
                text=[f"S/. {flujo_neto*12:,.0f}", f"S/. {u_anual_trad:,.0f}"],
                textposition='auto'
            )])
            fig_c.update_layout(title="Utilidad Neta Anual", height=350, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig_c, use_container_width=True)

# =========================================================
# BLOQUE 2: MOTOR PDF TÉCNICO (DETALLE EXTREMO)
# =========================================================

def generate_full_report(d):
    pdf = FPDF()
    pdf.add_page()
    # Header
    pdf.set_fill_color(31, 38, 48); pdf.rect(0, 0, 210, 45, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 15, "AUDITORIA DE INVERSION REAL ESTATE - LIMA", ln=True, align='C')
    pdf.set_font("Arial", '', 10); pdf.cell(0, 5, "ING. JANCARLO MENDOZA | CONSULTORIA INTEGRAL", ln=True, align='C')
    pdf.cell(0, 5, f"FECHA: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align='C')
    pdf.ln(20); pdf.set_text_color(0, 0, 0)

    # 1. Inversión
    pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, "1. DESGLOSE DE INVERSION INICIAL", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(100, 8, "Valor del Inmueble:", 1); pdf.cell(80, 8, f"S/. {d['val']:,.2f}", 1, ln=True)
    pdf.cell(100, 8, "Capital Propio (20% Inicial):", 1); pdf.cell(80, 8, f"S/. {d['val']*0.2:,.2f}", 1, ln=True)
    pdf.cell(100, 8, "Inversion Amoblado/Equipamiento:", 1); pdf.cell(80, 8, f"S/. {d['inv_a']:,.2f}", 1, ln=True)
    pdf.set_font("Arial", 'B', 10); pdf.cell(100, 8, "INVERSION TOTAL REAL:", 1); pdf.cell(80, 8, f"S/. {d['inv_t']:,.2f}", 1, ln=True)
    
    # 2. Operatividad
    pdf.ln(10); pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, "2. ANALISIS OPERATIVO MENSUAL (AIRBNB)", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(100, 8, f"Ingreso Bruto ({d['dias']} dias/mes):", 1); pdf.cell(80, 8, f"S/. {d['i_b']:,.2f}", 1, ln=True)
    pdf.cell(100, 8, "Cuota Bancaria Estimada:", 1); pdf.cell(80, 8, f"S/. -{d['cuota']:,.2f}", 1, ln=True)
    pdf.cell(100, 8, "Gasto Operativo (Mantenimiento/Servicios):", 1); pdf.cell(80, 8, f"S/. -{d['mant']:,.2f}", 1, ln=True)
    pdf.cell(100, 8, "Impuesto a la Renta (5% Sunat):", 1); pdf.cell(80, 8, f"S/. -{d['imp']:,.2f}", 1, ln=True)
    pdf.set_font("Arial", 'B', 10); pdf.cell(100, 8, "FLUJO NETO DISPONIBLE:", 1); pdf.cell(80, 8, f"S/. {d['f_n']:,.2f}", 1, ln=True)

    # 3. KPIs
    pdf.ln(10); pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, "3. INDICADORES DE RENTABILIDAD (KPIs)", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(100, 8, "ROI Anual Estimado:", 1); pdf.cell(80, 8, f"{d['roi']:.2f}%", 1, ln=True)
    pdf.cell(100, 8, "Payback (Recuperacion de Capital):", 1); pdf.cell(80, 8, f"{d['pb']:.1f} Años", 1, ln=True)
    pdf.cell(100, 8, "Ganancia vs Alquiler Tradicional (Anual):", 1); pdf.cell(80, 8, f"S/. {d['v_a']:,.2f}", 1, ln=True)
    
    # 4. Patrimonio
    pdf.ln(10); pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, "4. PROYECCION PATRIMONIAL (PLUSVALIA 20 AÑOS)", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.multi_cell(0, 7, f"Al finalizar un periodo de 20 años con una plusvalia conservadora del {d['p_a']}%, el activo tendra un valor de mercado proyectado de S/. {d['val_20']:,.2f}, generando una riqueza patrimonial neta ( Equity) superior al monto de inversion inicial en mas de un 300%.")

    return pdf.output(dest='S').encode('latin-1')

if "authenticated" in st.session_state and st.session_state.authenticated:
    st.write("---")
    if st.button("📥 GENERAR INFORME TECNICO BACKUP 2"):
        p20 = val_depa * (1 + p_anual/100)**20
        pdf_bytes = generate_report({
            "val": val_depa, "inv_a": inv_amoblado, "inv_t": inv_total_real,
            "i_b": ingreso_bruto, "cuota": cuota, "mant": mantenimiento,
            "imp": impuesto, "f_n": flujo_neto, "roi": roi_anual,
            "pb": año_rec, "v_a": ventaja, "p_a": p_anual, "val_20": p20, "dias": ocupacion_act
        })
        st.download_button("Descargar PDF Auditoría", data=pdf_bytes, file_name="Auditoria_Mendoza_B2.pdf")
