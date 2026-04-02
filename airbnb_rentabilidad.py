import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime
import numpy as np

# 0. AUTENTICACIÓN SIMPLE (SIN ARCHIVOS EXTRAS)
def verificar_contraseña():
    """Verifica contraseña simple"""
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
    
    if not st.session_state.autenticado:
        st.title("🔐 Acceso Restringido")
        contraseña = st.text_input("Ingresa la contraseña:", type="password")
        
        if st.button("Acceder"):
            if contraseña == "tu_contraseña_aqui":  # ← CAMBIA ESTO POR TU CONTRASEÑA
                st.session_state.autenticado = True
                st.success("✅ Acceso permitido")
                st.rerun()
            else:
                st.error("❌ Contraseña incorrecta")
        st.stop()

# Ejecutar autenticación
verificar_contraseña()

# --- Si llegó aquí, está autenticado ---

# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS UI
st.set_page_config(page_title="Rentabilidad Airbnb | Calculador", layout="wide")

# Botón de logout
if st.button("🚪 Cerrar Sesión", key="logout_btn"):
    st.session_state.autenticado = False
    st.rerun()

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    [data-testid="stMetricValue"] { color: #ffffff !important; font-weight: bold !important; font-size: 1.9rem !important; }
    [data-testid="stMetricLabel"] { color: #a1a1a1 !important; font-size: 0.9rem !important; }
    div[data-testid="stMetric"] {
        background-color: #1f2630;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #30363d;
    }
    .resultado-card { 
        padding: 22px; border-radius: 15px; color: white !important; text-align: center; margin-bottom: 20px;
        min-height: 200px;
    }
    .verde { background: linear-gradient(135deg, #28a745, #1e7e34); }
    .amarillo { background: linear-gradient(135deg, #ffc107, #e0a800); }
    .rojo { background: linear-gradient(135deg, #dc3545, #b02830); }
    .azul { background: linear-gradient(135deg, #0e2647, #1b3a61); }
    
    .opt-card {
        padding: 18px; 
        border-radius: 10px; 
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .opt-blue { background-color: #1e3a8a; border: 1px solid #3b82f6; }
    .opt-green { background-color: #064e3b; border: 1px solid #10b981; }
    .opt-red { background-color: #7c2d12; border: 1px solid #ea580c; }
    
    .opt-header { margin-top:0; font-size: 1.05rem; font-weight: bold; margin-bottom: 5px; }
    .header-blue { color: #60a5fa; }
    .header-green { color: #34d399; }
    .header-red { color: #fb923c; }
    
    .opt-text { font-size: 0.85rem; color: #d1d5db; margin-bottom: 8px; line-height: 1.2; }
    .opt-monto { color: white; margin-bottom: 0; font-size: 1.45rem; font-weight: bold; }
    
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. FUNCIÓN DE EXPORTACIÓN PDF PROFESIONAL ---
def generar_pdf(datos_informe, escenarios, break_even_meses, roi_actual):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_draw_color(14, 38, 71); pdf.set_line_width(0.8); pdf.rect(10, 10, 190, 30)
    pdf.set_y(15); pdf.set_font("Arial", 'B', 16); pdf.set_text_color(14, 38, 71)
    pdf.cell(0, 10, "ANALISIS DE RENTABILIDAD AIRBNB", ln=True, align='C')
    ahora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    pdf.set_font("Arial", '', 9); pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, f"Fecha y hora de realizacion: {ahora}", ln=True, align='C')
    pdf.ln(15)
    pdf.set_fill_color(14, 38, 71); pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, " 1. DATOS DEL PROYECTO", ln=True, fill=True)
    pdf.ln(2); pdf.set_text_color(30, 30, 30); pdf.set_font("Arial", '', 11)
    for k, v in datos_informe.items():
        pdf.cell(95, 10, f" {k}:", "B"); pdf.cell(0, 10, f"{v}", "B", ln=True, align='R')
    pdf.ln(10)
    pdf.set_fill_color(215, 179, 93); pdf.set_text_color(14, 38, 71); pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, " 2. PROYECCIONES POR OCUPACION", ln=True, fill=True)
    pdf.set_font("Arial", 'B', 10)
    for esc in escenarios:
        pdf.cell(50, 10, f" {esc['nombre']}", "B")
        pdf.cell(40, 10, f" ROI: {esc['roi']:.2f}%", "B", 0, 'C')
        pdf.cell(50, 10, f" Utilidad: S/ {esc['utilidad']:,}", "B", 1, 'C')
    pdf.ln(10)
    pdf.set_fill_color(14, 38, 71); pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, " 3. BREAK-EVEN", ln=True, fill=True)
    pdf.ln(2); pdf.set_text_color(30, 30, 30); pdf.set_font("Arial", '', 11)
    pdf.cell(95, 10, f" Break-even (meses):", "B"); pdf.cell(0, 10, f"{break_even_meses:.1f} meses ({break_even_meses/12:.2f} años)", "B", ln=True, align='R')
    pdf.cell(95, 10, f" ROI Anual (Base 20 días):", "B"); pdf.cell(0, 10, f"{roi_actual:.2f}%", "B", ln=True, align='R')
    pdf.ln(10); pdf.set_font("Arial", 'I', 9); pdf.set_text_color(80, 80, 80)
    texto_ref = (
        "IMPORTANTE: Este reporte es estrictamente REFERENCIAL. Los calculos asumen ocupacion constante y no consideran "
        "variaciones estacionales, mantenimientos extraordinarios, o cambios en tarifas. La rentabilidad real depende de "
        "multiples factores externos como ubicacion, competencia local y tendencias del mercado."
    )
    pdf.multi_cell(0, 5, texto_ref); pdf.ln(20)
    pdf.set_draw_color(215, 179, 93); pdf.line(120, pdf.get_y(), 200, pdf.get_y()); pdf.ln(2)
    pdf.set_font("Arial", 'B', 11); pdf.set_text_color(14, 38, 71)
    pdf.cell(0, 6, "Realizado con: Calculador de Rentabilidad Airbnb", ln=True, align='R')
    return pdf.output(dest='S').encode('latin-1')

# --- 3. PANEL LATERAL (INPUTS) ---
with st.sidebar:
    st.title("🏠 Datos del Proyecto")
    with st.expander("💰 Inversión y Financiamiento", expanded=True):
        precio = st.number_input("Precio del Departamento (S/)", min_value=0, value=250000)
        inicial_pct = 0.20  # 20% fijo
        inicial = int(precio * inicial_pct)
        prestamo = precio - inicial
        st.caption(f"✅ Inicial requerida (20%): S/ {inicial:,}")
        st.caption(f"📊 Préstamo necesario: S/ {prestamo:,}")

    with st.expander("🌙 Operación Airbnb", expanded=True):
        tarifa_diaria = st.number_input("Tarifa Diaria Promedio (S/)", min_value=0, value=180)
        
    with st.expander("🏦 Financiamiento", expanded=True):
        tcea = st.number_input("TCEA (%)", min_value=0.0, value=9.5)
        plazo_anos = st.selectbox("Plazo de Financiamiento", options=[10, 15, 20, 25], index=2)
    
    with st.expander("📋 Gastos Operativos", expanded=False):
        comision_airbnb = st.slider("Comisión Airbnb (%)", min_value=0, max_value=15, value=3)
        mantenimiento_pct = st.slider("Mantenimiento (%)", min_value=0, max_value=15, value=5)
        gastos_anuales_pct = st.slider("Gastos Anuales (%)", min_value=0, max_value=10, value=3)

# --- 4. CÁLCULOS FINANCIEROS ---
# Factor de amortización hipotecaria
tcea_decimal = tcea / 100
tem = (1 + tcea_decimal) ** (1/12) - 1
meses_plazo = plazo_anos * 12
factor = (1 - (1 + tem) ** -meses_plazo) / tem if tem > 0 else meses_plazo
cuota_mensual = int(prestamo * factor)

# Escenarios de ocupación (15, 20, 25 días/mes)
escenarios = []
for dias_mes in [15, 20, 25]:
    dias_anuales = dias_mes * 12
    ingresos_anuales = tarifa_diaria * dias_anuales
    cuota_anual = cuota_mensual * 12
    gastos_operativos = int(ingresos_anuales * (comision_airbnb + mantenimiento_pct) / 100)
    gastos_anuales = int(precio * gastos_anuales_pct / 100)
    utilidad_neta = ingresos_anuales - cuota_anual - gastos_operativos - gastos_anuales
    roi_anual = (utilidad_neta / inicial * 100) if inicial > 0 else 0
    
    escenarios.append({
        "nombre": f"{dias_mes} días/mes",
        "dias_anuales": dias_anuales,
        "ingresos_anuales": ingresos_anuales,
        "cuota_anual": cuota_anual,
        "gastos_operativos": gastos_operativos,
        "gastos_anuales": gastos_anuales,
        "utilidad_neta": utilidad_neta,
        "roi": roi_anual,
        "utilidad_mensual": utilidad_neta / 12,
        "ocupacion_pct": (dias_mes / 30) * 100
    })

# Escenario base (20 días/mes = índice 1)
base = escenarios[1]

# --- 5. CÁLCULO DE BREAK-EVEN ---
utilidad_mensual_base = base['utilidad_neta'] / 12
if utilidad_mensual_base > 0:
    break_even_meses = inicial / utilidad_mensual_base
else:
    break_even_meses = float('inf')

# --- 6. ANÁLISIS DE SENSIBILIDAD (OCUPACIÓN) ---
ocupaciones_test = np.linspace(5, 30, 26)  # 5 a 30 días/mes
sensibilidad_data = []
for dias in ocupaciones_test:
    dias_anuales = dias * 12
    ingresos_anuales = tarifa_diaria * dias_anuales
    cuota_anual = cuota_mensual * 12
    gastos_operativos = int(ingresos_anuales * (comision_airbnb + mantenimiento_pct) / 100)
    gastos_anuales = int(precio * gastos_anuales_pct / 100)
    utilidad_neta = ingresos_anuales - cuota_anual - gastos_operativos - gastos_anuales
    roi_anual = (utilidad_neta / inicial * 100) if inicial > 0 else 0
    sensibilidad_data.append({
        "ocupacion_dias": dias,
        "ocupacion_pct": (dias / 30) * 100,
        "roi": roi_anual,
        "utilidad_neta": utilidad_neta
    })

df_sensibilidad = pd.DataFrame(sensibilidad_data)

# --- 7. INTERFAZ WEB (SECCIÓN 1: RESUMEN) ---
st.title("🏠 Calculador de Rentabilidad Airbnb")
st.write("---")
st.subheader("1. Resumen de Inversión")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Precio del Depa", f"S/ {precio:,}")
col2.metric("Inicial Requerida (20%)", f"S/ {inicial:,}")
col3.metric("Préstamo", f"S/ {prestamo:,}")
col4.metric("Cuota Mensual", f"S/ {cuota_mensual:,}")

# --- SECCIÓN 2: ESCENARIOS DE OCUPACIÓN ---
st.write("---")
st.subheader("2. Proyecciones por Ocupación (Escenario Base)")

e1, e2, e3 = st.columns(3)
colores_esc = ["amarillo", "verde", "rojo"]
for i, (col, esc, color) in enumerate(zip([e1, e2, e3], escenarios, colores_esc)):
    with col:
        st.markdown(f'<div class="resultado-card {color}"><h3 style="font-size: 1.1rem;">{esc["nombre"]}</h3><p style="font-size: 0.85rem;">Ocupación: {esc["ocupacion_pct"]:.1f}%</p><h1 style="font-size: 1.7rem;">ROI {esc["roi"]:.2f}%</h1><hr style="border: 0.5px solid rgba(255,255,255,0.3)"><p style="font-size: 0.9rem;"><b>Utilidad Anual:</b><br>S/ {esc["utilidad_neta"]:,}</p></div>', unsafe_allow_html=True)

# --- SECCIÓN 3: DESGLOSE ESCENARIO BASE (20 DÍAS) ---
st.write("---")
st.subheader("3. Desglose Financiero - Escenario Base (20 días/mes)")

col_base1, col_base2, col_base3 = st.columns(3)
with col_base1:
    st.metric("Ingresos Anuales", f"S/ {base['ingresos_anuales']:,}")
    st.metric("Cuota Anual (Hipoteca)", f"S/ {base['cuota_anual']:,}")
with col_base2:
    st.metric("Gastos Operativos", f"S/ {base['gastos_operativos']:,}")
    st.metric("Gastos Anuales", f"S/ {base['gastos_anuales']:,}")
with col_base3:
    st.metric("Utilidad Neta Anual", f"S/ {base['utilidad_neta']:,}")
    st.metric("Utilidad Mensual", f"S/ {int(base['utilidad_mensual']):,}")

# --- SECCIÓN 4: BREAK-EVEN ---
st.write("---")
st.subheader("4. 📍 Punto de Equilibrio (Break-Even)")

if break_even_meses == float('inf') or break_even_meses < 0:
    st.error("⚠️ **Break-Even No Viable:** Con el escenario actual (20 días/mes), no hay ganancia neta. Revisa tu ocupación o gastos.")
else:
    col_be1, col_be2, col_be3 = st.columns(3)
    with col_be1:
        st.markdown(f'<div class="opt-card opt-green"><div class="opt-header header-green">⏱️ Tiempo de Recuperación</div><div class="opt-text">Recuperas tu inversión inicial en:</div><div class="opt-monto">{break_even_meses:.1f} meses</div><p style="color: #d1d5db; font-size: 0.9rem;">({break_even_meses/12:.2f} años)</p></div>', unsafe_allow_html=True)
    
    with col_be2:
        break_even_anos = break_even_meses / 12
        if break_even_anos <= 5:
            estado = "✅ EXCELENTE"
            color_estado = "#28a745"
        elif break_even_anos <= 10:
            estado = "⚠️ BUENO"
            color_estado = "#ffc107"
        else:
            estado = "❌ RIESGO"
            color_estado = "#dc3545"
        st.markdown(f'<div style="background-color: #1f2630; padding: 18px; border-radius: 12px; border: 1px solid {color_estado}; text-align: center;"><p style="color: #a1a1a1; font-size: 0.9rem; margin-bottom: 10px;">Estado de Viabilidad</p><p style="color: {color_estado}; font-size: 1.5rem; font-weight: bold;">{estado}</p></div>', unsafe_allow_html=True)
    
    with col_be3:
        st.markdown(f'<div class="opt-card opt-blue"><div class="opt-header header-blue">💰 Inversión Inicial</div><div class="opt-text">Monto que necesitas recuperar:</div><div class="opt-monto">S/ {inicial:,}</div><p style="color: #d1d5db; font-size: 0.9rem;">al {base["roi"]:.2f}% ROI anual</p></div>', unsafe_allow_html=True)

    # Gráfico de Flujo de Caja Acumulado
    meses_proyeccion = int(break_even_meses) + 24
    flujo_acumulado = []
    for mes in range(0, meses_proyeccion + 1):
        flujo = -inicial + (base['utilidad_neta'] / 12) * mes
        flujo_acumulado.append(flujo)
    
    df_flujo = pd.DataFrame({
        "Mes": range(0, meses_proyeccion + 1),
        "Flujo Acumulado": flujo_acumulado
    })
    
    fig_flujo = go.Figure()
    fig_flujo.add_trace(go.Scatter(
        x=df_flujo["Mes"],
        y=df_flujo["Flujo Acumulado"],
        mode='lines',
        fill='tozeroy',
        name='Flujo Acumulado',
        line=dict(color='#10b981', width=3),
        fillcolor='rgba(16, 185, 129, 0.2)'
    ))
    
    # Línea de break-even
    fig_flujo.add_hline(y=0, line_dash="dash", line_color="yellow", annotation_text="Break-Even")
    fig_flujo.add_vline(x=break_even_meses, line_dash="dash", line_color="orange", annotation_text=f"Mes {break_even_meses:.0f}")
    
    fig_flujo.update_layout(
        title="Flujo de Caja Acumulado (Escenario Base 20 días/mes)",
        xaxis_title="Meses",
        yaxis_title="Flujo Acumulado (S/)",
        template="plotly_dark",
        hovermode="x unified",
        height=400,
        paper_bgcolor='rgba(14, 17, 23, 0.5)',
        plot_bgcolor='rgba(31, 38, 48, 0.5)'
    )
    st.plotly_chart(fig_flujo, use_container_width=True)

# --- SECCIÓN 5: ANÁLISIS DE SENSIBILIDAD ---
st.write("---")
st.subheader("5. 📊 Análisis de Sensibilidad - Ocupación")
st.info("💡 **Cómo cambia tu ROI según los días/mes que logres ocupar el depa**")

# Gráfico: ROI vs Ocupación
fig_sensib_roi = go.Figure()
fig_sensib_roi.add_trace(go.Scatter(
    x=df_sensibilidad["ocupacion_pct"],
    y=df_sensibilidad["roi"],
    mode='lines+markers',
    name='ROI Anual (%)',
    line=dict(color='#3b82f6', width=3),
    marker=dict(size=6)
))

# Línea de ocupación actual (20 días)
ocupacion_actual = (20 / 30) * 100
fig_sensib_roi.add_vline(x=ocupacion_actual, line_dash="dash", line_color="#10b981", 
                          annotation_text=f"Actual: {ocupacion_actual:.1f}%")

fig_sensib_roi.update_layout(
    title="ROI vs Ocupación",
    xaxis_title="Ocupación (%)",
    yaxis_title="ROI Anual (%)",
    template="plotly_dark",
    hovermode="x",
    height=400,
    paper_bgcolor='rgba(14, 17, 23, 0.5)',
    plot_bgcolor='rgba(31, 38, 48, 0.5)'
)
st.plotly_chart(fig_sensib_roi, use_container_width=True)

# Tabla de sensibilidad (cada 5 días)
st.subheader("Tabla de Sensibilidad - Ocupación")
df_tabla = df_sensibilidad[df_sensibilidad["ocupacion_dias"] % 5 == 0].copy()
df_tabla["ocupacion_dias"] = df_tabla["ocupacion_dias"].astype(int)
df_tabla["ocupacion_pct"] = df_tabla["ocupacion_pct"].round(1)
df_tabla["roi"] = df_tabla["roi"].round(2)
df_tabla["utilidad_neta"] = df_tabla["utilidad_neta"].astype(int)
df_tabla = df_tabla.rename(columns={
    "ocupacion_dias": "Días/Mes",
    "ocupacion_pct": "Ocupación %",
    "roi": "ROI Anual %",
    "utilidad_neta": "Utilidad Neta S/"
})
st.dataframe(df_tabla, use_container_width=True, hide_index=True)

# --- SECCIÓN 6: RECOMENDACIONES ---
st.write("---")
st.subheader("6. 💡 Análisis y Recomendaciones")

rec1, rec2, rec3 = st.columns(3)

# Ocupación mínima para romper gastos
ocupacion_minima = (((cuota_mensual * 12) + (precio * gastos_anuales_pct / 100)) / 
                     (tarifa_diaria * 30 * (1 - (comision_airbnb + mantenimiento_pct) / 100)))
ocupacion_minima_dias = ocupacion_minima * 30

with rec1:
    if ocupacion_minima_dias > 0:
        st.markdown(f'<div class="opt-card opt-blue"><div class="opt-header header-blue">⚠️ Ocupación Mínima</div><div class="opt-text">Necesitas al menos esta ocupacion para cubrirte:</div><div class="opt-monto">{ocupacion_minima_dias:.1f} días/mes</div><p style="color: #d1d5db; font-size: 0.9rem;">({ocupacion_minima*100:.1f}% ocupacion)</p></div>', unsafe_allow_html=True)

# Impacto de cambios en ocupación
roi_15 = escenarios[0]['roi']
roi_20 = escenarios[1]['roi']
roi_25 = escenarios[2]['roi']
cambio_5dias = roi_20 - roi_15

with rec2:
    st.markdown(f'<div class="opt-card opt-green"><div class="opt-header header-green">📈 Impacto de +5 días</div><div class="opt-text">Si pasas de 15 a 20 días/mes, tu ROI aumenta:</div><div class="opt-monto">+{cambio_5dias:.2f}%</div><p style="color: #d1d5db; font-size: 0.9rem;">({roi_15:.2f}% → {roi_20:.2f}%)</p></div>', unsafe_allow_html=True)

# Recomendación final
with rec3:
    if base['roi'] > 10:
        recomendacion = "✅ MUY RENTABLE"
        color_rec = "#28a745"
    elif base['roi'] > 5:
        recomendacion = "⚠️ RENTABLE"
        color_rec = "#ffc107"
    else:
        recomendacion = "❌ REVISAR"
        color_rec = "#dc3545"
    
    st.markdown(f'<div style="background-color: #1f2630; padding: 18px; border-radius: 10px; border: 2px solid {color_rec}; text-align: center;"><p style="color: #a1a1a1; font-size: 0.9rem; margin-bottom: 10px;">Rentabilidad General</p><p style="color: {color_rec}; font-size: 1.5rem; font-weight: bold;">{recomendacion}</p><p style="color: #d1d5db; font-size: 0.9rem;">ROI: {base["roi"]:.2f}% anual</p></div>', unsafe_allow_html=True)

# --- SECCIÓN 7: EXPORTAR PDF ---
st.write("---")
st.subheader("7. 📄 Generar Reporte")

if st.button("✅ Generar Reporte PDF"):
    st.balloons()
    d_pdf = {
        "Precio del Depa": f"S/ {precio:,}",
        "Tarifa Diaria": f"S/ {tarifa_diaria}",
        "TCEA": f"{tcea}%",
        "Plazo": f"{plazo_anos} años",
        "Cuota Mensual": f"S/ {cuota_mensual:,}",
        "Inicial Requerida": f"S/ {inicial:,}"
    }
    
    esc_pdf = [
        {"nombre": "15 días/mes", "roi": escenarios[0]['roi'], "utilidad": escenarios[0]['utilidad_neta']},
        {"nombre": "20 días/mes (Base)", "roi": escenarios[1]['roi'], "utilidad": escenarios[1]['utilidad_neta']},
        {"nombre": "25 días/mes", "roi": escenarios[2]['roi'], "utilidad": escenarios[2]['utilidad_neta']}
    ]
    
    p_bytes = generar_pdf(d_pdf, esc_pdf, break_even_meses, base['roi'])
    st.download_button(
        "📥 Descargar Reporte PDF",
        data=p_bytes,
        file_name=f"Rentabilidad_Airbnb_{datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf"
    )

st.write("")
st.caption("💡 **Disclaimer:** Este calculador es una herramienta de referencia. La rentabilidad real depende de múltiples factores como estacionalidad, competencia local, cambios de tasas y mantenimientos extraordinarios. Consulta con un asesor financiero antes de tomar decisiones.")
