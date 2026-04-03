import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime

# =========================================================
# BLOQUE 1: INTERFAZ WEB V37 (PROHIBIDO TOCAR)
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
    # --- ESTILOS CSS V37 ---
    st.markdown("""
        <style>
        .main { background-color: #0e1117; }
        [data-testid="stMetricValue"] { font-size: 1.8rem !important; color: #00ffcc; font-weight: bold; }
        [data-testid="stMetricLabel"] { font-size: 1rem !important; font-weight: 500; color: #ffffff; }
        div[data-testid="stMetric"] { background-color: #1f2630; padding: 20px; border-radius: 12px; border: 1px solid #30363d; }
        .info-text { font-size: 0.9rem; color: #a1a1a1; margin-top: 10px; padding: 12px; border-left: 2px solid #3b82f6; background-color: #161b22; line-height: 1.5; }
        .section-title { margin-top: 35px; margin-bottom: 12px; color: #3b82f6; font-size: 1.45rem; font-weight: 400; border-bottom: 1px solid #30363d; padding-bottom: 5px; }
        .highlight-card { background-color: #1e293b; padding: 25px; border-radius: 12px; border: 1px solid #3b82f6; text-align: center; margin-bottom: 10px; }
        .flow-card { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; height: 100%; margin-bottom: 10px; }
        .flow-val { font-size: 1.3rem; font-weight: bold; margin-bottom: 5px; }
        .flow-label { font-size: 0.85rem; color: #3b82f6; text-transform: uppercase; font-weight: 600; }
        </style>
        """, unsafe_allow_html=True)

    # --- SIDEBAR V37 ---
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

    # --- LÓGICA V37 ---
    inicial_banco = val_depa * 0.20
    inversion_total_real = inicial_banco + inv_amoblado
    prestamo = val_depa - inicial_banco
    tem = (1 + tcea/100)**(1/12) - 1
    cuota = prestamo * (tem * (1 + tem)**(plazo_años*12)) / ((1 + tem)**(plazo_años*12) - 1)
    mantenimiento_mes = (val_depa * 0.03) / 12
    ingreso_bruto_air = tarifa * ocupacion_act * 0.85
    impuesto_air = ingreso_bruto_air * 0.05
    flujo_neto_air = ingreso_bruto_air - cuota - mantenimiento_mes - impuesto_air
    roi_anual_air = (flujo_neto_air * 12 / inversion_total_real) * 100
    breakeven_dias = (cuota + mantenimiento_mes) / (tarifa * 0.85 * 0.95)
    u_anual_trad = (renta_trad - cuota - (val_depa*0.015/12) - (renta_trad*0.05)) * 12

    # --- TABS V37 (DISPOSICIÓN EXACTA) ---
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Flujos", "📈 Plusvalía", "🛡️ Sensibilidad", "🔄 Airbnb vs Tradicional"])

    with tab1:
        st.markdown('<div class="section-title">Desembolso Inicial</div>', unsafe_allow_html=True)
        st.metric("Inversión Total Real", f"S/. {inversion_total_real:,.0f}")
        st.markdown('<div class="info-text">Capital líquido inicial: 20% cuota inicial + inversión en amoblado y equipamiento.</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">Detalle de Flujo Mensual</div>', unsafe_allow_html=True)
        col_f1, col_f2, col_f3, col_f4, col_f5 = st.columns(5)
        with col_f1:
            st.markdown(f'<div class="flow-card"><div class="flow-label">Ingresos</div><div class="flow-val" style="color: #00ffcc;">S/. {ingreso_bruto_air:,.2f}</div><p style="font-size:0.8rem; color:#a1a1a1;">Ingreso neto tras comisión plataforma (15%).</p></div>', unsafe_allow_html=True)
        with col_f2:
            st.markdown(f'<div class="flow-card"><div class="flow-label">Hipotecario</div><div class="flow-val" style="color: #ef4444;">S/. -{cuota:,.2f}</div><p style="font-size:0.8rem; color:#a1a1a1;">Pago mensual del crédito según TCEA.</p></div>', unsafe_allow_html=True)
        with col_f3:
            st.markdown(f'<div class="flow-card"><div class="flow-label">Operativos</div><div class="flow-val" style="color: #ef4444;">S/. -{mantenimiento_mes:,.2f}</div><p style="font-size:0.8rem; color:#a1a1a1;">Edificio, servicios y limpieza.</p></div>', unsafe_allow_html=True)
        with col_f4:
            st.markdown(f'<div class="flow-card"><div class="flow-label">Impuestos</div><div class="flow-val" style="color: #ef4444;">S/. -{impuesto_air:,.2f}</div><p style="font-size:0.8rem; color:#a1a1a1;">Impuesto a la renta 1ra categoría (5%).</p></div>', unsafe_allow_html=True)
        with col_f5:
            st.markdown(f'<div class="flow-card" style="border: 1px solid #00ffcc;"><div class="flow-label">Flujo Neto</div><div class="flow-val" style="color: #00ffcc;">S/. {flujo_neto_air:,.2f}</div><p style="font-size:0.8rem; color:#a1a1a1;">Utilidad líquida al finalizar el mes.</p></div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">Proyección de Payback (Retorno de Capital)</div>', unsafe_allow_html=True)
        años_pb = 25; meses_pb = np.arange(0, años_pb * 12 + 1); flujo_acum = [-inversion_total_real]; año_rec = None
        for m in meses_pb[1:]:
            u_mes = flujo_neto_air if m <= (plazo_años * 12) else (ingreso_bruto_air - mantenimiento_mes - impuesto_air)
            flujo_acum.append(flujo_acum[-1] + u_mes)
            if año_rec is None and flujo_acum[-1] >= 0: año_rec = m / 12
        if año_rec: 
            st.markdown(f'<div class="highlight-card"><span style="color: #3b82f6; font-size: 2.5rem; font-weight: bold;">{año_rec:.1f} Años</span></div>', unsafe_allow_html=True)
        
        fig_pb = go.Figure(); f_np = np.array(flujo_acum)
        fig_pb.add_trace(go.Scatter(x=meses_pb/12, y=np.where(f_np <= 0, f_np, 0), fill='tozeroy', fillcolor='rgba(239, 68, 68, 0.3)', line=dict(color='rgba(0,0,0,0)'), showlegend=False))
        fig_pb.add_trace(go.Scatter(x=meses_pb/12, y=np.where(f_np >= 0, f_np, 0), fill='tozeroy', fillcolor='rgba(16, 185, 129, 0.3)', line=dict(color='rgba(0,0,0,0)'), showlegend=False))
        fig_pb.add_trace(go.Scatter(x=meses_pb/12, y=flujo_acum, line=dict(color='#3b82f6', width=4), name="Flujo Acumulado"))
        fig_pb.update_layout(height=500, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", xaxis_title="Años")
        st.plotly_chart(fig_pb, use_container_width=True)

    with tab2:
        st.markdown('<div class="section-title">Plusvalía Anual</div>', unsafe_allow_html=True)
        plus_val = st.slider("Plusvalía Anual (%)", 0.0, 10.0, 4.0)
        p_10 = (val_depa * (1 + plus_val/100)**10) - val_depa
        p_20 = (val_depa * (1 + plus_val/100)**20) - val_depa
        st.metric("A 10 años", f"S/. {p_10:,.0f}"); st.metric("A 20 años", f"S/. {p_20:,.0f}")
        
        años_p = np.arange(0, 26); v_mkt = [val_depa * (1 + plus_val/100)**a for a in años_p]; eq = [v - (prestamo * (1 - a/plazo_años) if a < plazo_años else 0) for a, v in zip(años_p, v_mkt)]
        fig_p = go.Figure(); fig_p.add_trace(go.Bar(x=años_p, y=v_mkt, name="Valor Mercado", marker_color='#1f2630')); fig_p.add_trace(go.Scatter(x=años_p, y=eq, name="Equity", fill='tozeroy', line=dict(color='#00ffcc', width=3)))
        fig_p.update_layout(height=450, barmode='overlay', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white"); st.plotly_chart(fig_p, use_container_width=True)

    with tab3:
        st.markdown('<div class="section-title">Análisis de Resiliencia</div>', unsafe_allow_html=True)
        c_m1, c_m2, c_m3 = st.columns(3); c_m1.metric("Punto Equilibrio (Días)", f"{np.ceil(breakeven_dias):.0f}"); c_m2.metric("Ocupación Objetivo", f"{ocupacion_act} días"); c_m3.metric("ROI Est. Anual", f"{roi_anual_air:.1f}%")
        
        st.markdown('<div class="section-title">Sensibilidad: ROI vs Ocupación Mensual</div>', unsafe_allow_html=True)
        c_o1, c_o2 = st.columns([1, 2])
        d_range = list(range(5, 31)); roi_o = [((((tarifa * d * 0.85 * 0.95) - cuota - mantenimiento_mes) * 12 / inversion_total_real) * 100) for d in d_range]
        with c_o1:
            df_o = pd.DataFrame({"Días": [f"{d}d" for d in [10, 15, 20, 25, 30]], "ROI %": [roi_o[d_range.index(d)] for d in [10, 15, 20, 25, 30]]})
            st.dataframe(df_o.style.format({"ROI %": "{:.1f}%"}).background_gradient(cmap='RdYlGn', subset=["ROI %"]), height=212, use_container_width=True, hide_index=True)
        with c_o2:
            fig_o = go.Figure(go.Scatter(x=d_range, y=roi_o, line=dict(color='#3b82f6', width=3))); fig_o.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig_o, use_container_width=True)

    with tab4:
        st.markdown('<div class="section-title">Comparativa de Modelos de Renta</div>', unsafe_allow_html=True)
        ventaja_anual = (flujo_neto_air*12) - u_anual_trad
        eficiencia = (roi_anual_air/((u_anual_trad/inversion_total_real)*100)) if u_anual_trad != 0 else 0
        st.metric("Ventaja Airbnb (Anual)", f"S/. {ventaja_anual:,.0f}")
        fig_c = go.Figure([go.Bar(x=['Airbnb', 'Tradicional'], y=[flujo_neto_air*12, u_anual_trad], marker_color=['#3b82f6', '#10b981'], 
                                 text=[f"S/. {flujo_neto_air*12:,.0f}", f"S/. {u_anual_trad:,.0f}"], textposition='inside', 
                                 textfont=dict(size=18, color="white", family="Arial Black"), insidetextanchor='middle')])
        fig_c.update_layout(height=450, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_c, use_container_width=True)
        st.markdown('<div class="info-text"><b>Ficha Informativa Final:</b> Esta comparativa proyecta la utilidad neta después de obligaciones.</div>', unsafe_allow_html=True)

# =========================================================
# BLOQUE 2: MOTOR DE PDF (AISLADO AL FINAL)
# =========================================================

def generate_pdf_engine(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "AUDITORIA TECNICA INMOBILIARIA", ln=True, align='C')
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(200, 8, "Ing. Jancarlo Mendoza - Real Estate Expert", ln=True, align='C')
    pdf.line(10, 35, 200, 35); pdf.ln(15)
    
    pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, "RESUMEN DE RESULTADOS", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 7, f"- Inversion Capital: S/. {data['inv']:,.2f}", ln=True)
    pdf.cell(0, 7, f"- Flujo Neto/Mes: S/. {data['flujo']:,.2f}", ln=True)
    pdf.cell(0, 7, f"- ROI Anual: {data['roi']:.2f}%", ln=True)
    pdf.cell(0, 7, f"- Ventaja vs Tradicional: S/. {data['ventaja']:,.2f}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- BOTÓN DE EXPORTACIÓN (FUERA DE LOS TABS) ---
if "authenticated" in st.session_state and st.session_state.authenticated:
    st.write("---")
    if st.button("📥 EXPORTAR INFORME PDF"):
        pdf_content = generate_pdf_engine({
            "inv": inversion_total_real, "flujo": flujo_neto_air, 
            "roi": roi_anual_air, "ventaja": ventaja_anual
        })
        st.download_button("Descargar Archivo", data=pdf_content, file_name="auditoria_v46.pdf")
