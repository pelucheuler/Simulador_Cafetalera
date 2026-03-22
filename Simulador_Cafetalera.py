import streamlit as st
import streamlit.components.v1 as components
import random
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="HMI Cafetalera", page_icon="☕", layout="wide")

# ==========================================
# 1. MOTOR GRÁFICO DEL SCADA ANIMADO (SVG)
# ==========================================
def render_scada_cafetalera(vars_dict, faults_dict):
    # Variables de estado
    pwr_main = vars_dict['breaker_main']
    pwr_comp = vars_dict['compresor'] and pwr_main
    pwr_tost = vars_dict['tostadora'] and pwr_main
    pwr_banda = vars_dict['vfd_banda'] and pwr_main
    pwr_dosif = vars_dict['dosificador'] and pwr_main
    pwr_sell = vars_dict['selladora'] and pwr_main
    auto_mode = vars_dict['auto_mode'] and pwr_main

    # Colores y Animaciones
    c_on = "#39A900"
    c_off = "#95A5A6"
    c_error = "#E74C3C"
    c_warn = "#F1C40F"
    
    anim_banda = f"move_belt {max(0.2, 2.0 - (vars_dict['hz_banda']/50.0))}s linear infinite" if pwr_banda and vars_dict['hz_banda'] > 0 and not faults_dict['atasco_banda'] else "none"
    anim_comp = "shake 0.1s infinite" if pwr_comp and not faults_dict['fuga_aire'] else "none"
    
    # Estados visuales de equipos
    c_comp = c_on if pwr_comp else c_off
    if faults_dict['fuga_aire']: c_comp = c_error
    
    c_tost = c_warn if pwr_tost else c_off
    if faults_dict['falla_tost']: c_tost = c_error
    
    c_banda_motor = c_on if pwr_banda else c_off
    if faults_dict['atasco_banda']: c_banda_motor = c_error
    
    c_dosif = c_on if pwr_dosif else c_off
    if faults_dict['descalibre']: c_dosif = c_error
    
    c_sell = c_warn if pwr_sell else c_off
    if faults_dict['resistencia_quemada']: c_sell = c_error

    # SVG panorámico
    svg = f"""
    <style>
        @keyframes move_belt {{ 100% {{ stroke-dashoffset: -40; }} }}
        @keyframes shake {{ 0% {{ transform: translate(1px, 1px); }} 50% {{ transform: translate(-1px, -1px); }} 100% {{ transform: translate(1px, 1px); }} }}
        .scada-txt {{ font-family: Arial, sans-serif; font-size: 14px; font-weight: bold; fill: #333; }}
        .scada-val {{ font-family: 'Courier New', monospace; font-size: 18px; font-weight: bold; fill: #00324D; }}
        .scada-label {{ font-family: Arial, sans-serif; font-size: 11px; fill: #555; }}
        .pipe {{ stroke: #3498DB; stroke-width: 4; fill: none; stroke-dasharray: 5,5; }}
    </style>
    <svg viewBox="0 0 1000 550" width="100%" height="100%" style="background-color: #F4F6F9; border: 3px solid #7F8C8D; border-radius: 8px;">
        
        <!-- HEADER SCADA -->
        <rect x="0" y="0" width="1000" height="40" fill="#00324D"/>
        <text x="20" y="25" class="scada-txt" fill="#FFF">GEMELO DIGITAL: HMI CAFETALERA "EL BUEN GRANO"</text>
        <circle cx="950" cy="20" r="10" fill="{c_on if auto_mode else c_off}"/>
        <text x="890" y="25" class="scada-txt" fill="#FFF">AUTO</text>

        <!-- COMPRESOR -->
        <g style="animation: {anim_comp};">
            <rect x="750" y="70" width="140" height="90" fill="{c_comp}" stroke="#333" stroke-width="3" rx="10"/>
            <text x="760" y="95" class="scada-txt" fill="#FFF">COMPRESOR</text>
        </g>
        <rect x="770" y="110" width="100" height="40" fill="#FFF" stroke="#333"/>
        <text x="775" y="125" class="scada-label">Presión (PI-01)</text>
        <text x="775" y="142" class="scada-val" fill="{'#E74C3C' if faults_dict['fuga_aire'] else '#00324D'}">{vars_dict['presion_actual']:.1f} PSI</text>
        
        <!-- TUBERÍA NEUMÁTICA -->
        <path d="M 820,160 L 820,380 L 680,380" class="pipe"/>
        <path d="M 820,200 L 450,200 L 450,250" class="pipe"/>

        <!-- TOSTADORA -->
        <rect x="50" y="150" width="180" height="250" fill="{c_tost}" stroke="#333" stroke-width="4" rx="15"/>
        <text x="80" y="180" class="scada-txt" fill="#FFF">TOSTADORA</text>
        
        <rect x="70" y="220" width="140" height="60" fill="#FFF" stroke="#333"/>
        <text x="75" y="235" class="scada-label">Temperatura (TI-01)</text>
        <text x="75" y="260" class="scada-val">{vars_dict['temp_tost_actual']:.1f} °C</text>

        <!-- BANDA TRANSPORTADORA -->
        <rect x="230" y="420" width="650" height="25" fill="#BDC3C7" stroke="#333" stroke-width="2"/>
        <line x1="230" y1="432" x2="880" y2="432" stroke="{c_banda_motor}" stroke-width="6" stroke-dasharray="20,10" style="animation: {anim_banda};"/>
        
        <!-- MOTOR VFD BANDA -->
        <circle cx="210" cy="432" r="25" fill="{c_banda_motor}" stroke="#333" stroke-width="3"/>
        <text x="195" y="475" class="scada-txt">M-01</text>
        <rect x="250" y="460" width="120" height="50" fill="#FFF" stroke="#333"/>
        <text x="255" y="475" class="scada-label">VFD Frecuencia</text>
        <text x="255" y="495" class="scada-val">{vars_dict['hz_banda'] if not faults_dict['atasco_banda'] else 0.0} Hz</text>

        <!-- DOSIFICADOR -->
        <rect x="400" y="250" width="120" height="130" fill="{c_dosif}" stroke="#333" stroke-width="3"/>
        <polygon points="400,380 520,380 480,410 440,410" fill="#E67E22" stroke="#333"/>
        <text x="415" y="280" class="scada-txt" fill="#FFF">DOSIFICADOR</text>
        <rect x="410" y="300" width="100" height="50" fill="#FFF" stroke="#333"/>
        <text x="415" y="315" class="scada-label">Peso (WI-01)</text>
        <text x="415" y="335" class="scada-val" fill="{'#E74C3C' if faults_dict['descalibre'] else '#00324D'}">{vars_dict['peso_actual']:.1f} g</text>

        <!-- SELLADORA -->
        <rect x="620" y="280" width="100" height="120" fill="{c_sell}" stroke="#333" stroke-width="3"/>
        <rect x="650" y="400" width="40" height="20" fill="#95A5A6" stroke="#333"/>
        <text x="630" y="310" class="scada-txt" fill="#FFF">SELLADORA</text>
        <rect x="630" y="330" width="80" height="50" fill="#FFF" stroke="#333"/>
        <text x="635" y="345" class="scada-label">Temp Sello</text>
        <text x="635" y="365" class="scada-val">{vars_dict['temp_sell_actual']:.1f} °C</text>
        
    </svg>
    """
    return svg

# ==========================================
# 2. ESTILOS Y MEMORIA
# ==========================================
st.markdown("""<style>.stApp { background-color: #FFFFFF; font-family: 'Arial'; } .mision-box { background-color: #F8F9FA; border-left: 5px solid #00324D; padding: 20px; margin-bottom: 20px;} section[data-testid="stSidebar"] { background-color: #1E2129 !important; border-right: 3px solid #FF671F; } section[data-testid="stSidebar"] * { color: #F8F9FA !important; } .stSlider { margin-bottom: -15px; }</style>""", unsafe_allow_html=True)

if 'registrado' not in st.session_state: st.session_state.registrado = False
if 'nombre' not in st.session_state: st.session_state.nombre = ""
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'score' not in st.session_state: st.session_state.score = 0
if 'log' not in st.session_state: st.session_state.log = []
if 'completadas' not in st.session_state: st.session_state.completadas = []

# CORRECCIÓN AQUÍ: Variables de temperatura inicializadas en 20.0
if 'vars' not in st.session_state:
    st.session_state.vars = {
        'breaker_main': False, 'compresor': False, 'sp_presion': 0.0, 'presion_actual': 0.0,
        'tostadora': False, 'sp_temp_tost': 20.0, 'temp_tost_actual': 20.0,
        'vfd_banda': False, 'sp_hz': 0.0, 'hz_banda': 0.0,
        'dosificador': False, 'sp_peso': 0.0, 'peso_actual': 0.0,
        'selladora': False, 'sp_temp_sell': 20.0, 'temp_sell_actual': 20.0,
        'auto_mode': False
    }

if 'faults' not in st.session_state:
    st.session_state.faults = {
        'fuga_aire': True, 'falla_tost': False, 'atasco_banda': False, 
        'descalibre': True, 'resistencia_quemada': False
    }

# ==========================================
# 3. REGISTRO E INTERFAZ LATERAL
# ==========================================
if not st.session_state.registrado:
    st.title("🖥️ HMI SCADA: Cafetalera El Buen Grano")
    name = st.text_input("Ingresa tu Nombre Completo para iniciar el turno:")
    if st.button("INICIAR SIMULADOR", type="primary") and name:
        st.session_state.registrado = True
        st.session_state.nombre = name
        st.rerun()
    st.stop()

st.sidebar.success(f"👨‍💻 Jefe de Planta: {st.session_state.nombre}")
st.sidebar.markdown("---")

# PANELES DE CONTROL HMI
st.sidebar.markdown("### ⚡ TABLERO ELÉCTRICO")
st.session_state.vars['breaker_main'] = st.sidebar.toggle("Breaker Principal", value=st.session_state.vars['breaker_main'])

st.sidebar.markdown("### 🎛️ CONTROL DE EQUIPOS")
c1, c2 = st.sidebar.columns(2)
st.session_state.vars['compresor'] = c1.toggle("Compresor", value=st.session_state.vars['compresor'])
st.session_state.vars['tostadora'] = c2.toggle("Tostadora", value=st.session_state.vars['tostadora'])
st.session_state.vars['vfd_banda'] = c1.toggle("VFD Banda", value=st.session_state.vars['vfd_banda'])
st.session_state.vars['dosificador'] = c2.toggle("Dosificador", value=st.session_state.vars['dosificador'])
st.session_state.vars['selladora'] = c1.toggle("Selladora", value=st.session_state.vars['selladora'])
st.session_state.vars['auto_mode'] = st.sidebar.toggle("🟢 CICLO AUTOMÁTICO", value=st.session_state.vars['auto_mode'])

st.sidebar.markdown("### 🎚️ SETPOINTS (SP)")
st.session_state.vars['sp_presion'] = st.sidebar.slider("SP Presión (PSI)", 0, 120, int(st.session_state.vars['sp_presion']), 10)

# CORRECCIÓN AQUÍ: Sliders de temperatura empiezan en 20
st.session_state.vars['sp_temp_tost'] = st.sidebar.slider("SP Temp Tostadora (°C)", 20, 250, int(st.session_state.vars['sp_temp_tost']), 10)
st.session_state.vars['sp_hz'] = st.sidebar.slider("SP VFD Banda (Hz)", 0, 60, int(st.session_state.vars['sp_hz']), 5)
st.session_state.vars['sp_peso'] = st.sidebar.slider("SP Peso Dosificador (g)", 0, 1000, int(st.session_state.vars['sp_peso']), 50)
st.session_state.vars['sp_temp_sell'] = st.sidebar.slider("SP Temp Selladora (°C)", 20, 200, int(st.session_state.vars['sp_temp_sell']), 10)

st.sidebar.markdown("### 🔧 ÓRDENES DE MANTENIMIENTO")
col_m1, col_m2 = st.sidebar.columns(2)
btn_reparar_fugas = col_m1.button("Reparar Fugas Neumáticas")
btn_reset_tost = col_m2.button("Reset Térmico Tostadora")
btn_lubricar = col_m1.button("Lubricar Rodamientos Banda")
btn_calibrar = col_m2.button("Calibrar Celda de Carga")
btn_resistencia = st.sidebar.button("Cambiar Resistencia Quemada")

btn_avanzar = st.sidebar.button("⏱️ EJECUTAR / AVANZAR TIEMPO", type="primary", use_container_width=True)

# ==========================================
# 4. LÓGICA MATEMÁTICA Y DE FALLAS
# ==========================================
if btn_reparar_fugas: st.session_state.faults['fuga_aire'] = False
if btn_reset_tost: st.session_state.faults['falla_tost'] = False
if btn_lubricar: st.session_state.faults['atasco_banda'] = False
if btn_calibrar: st.session_state.faults['descalibre'] = False
if btn_resistencia: st.session_state.faults['resistencia_quemada'] = False

if btn_avanzar:
    v = st.session_state.vars
    f = st.session_state.faults
    
    # Simular paso del tiempo y físicas
    if v['breaker_main']:
        # Presión
        if v['compresor']:
            target_p = 40.0 if f['fuga_aire'] else v['sp_presion']
            v['presion_actual'] += (target_p - v['presion_actual']) * 0.5
        else: v['presion_actual'] = max(0.0, v['presion_actual'] - 10.0)
        
        # Temp Tostadora
        if st.session_state.idx == 6: f['falla_tost'] = True 
        if v['tostadora'] and not f['falla_tost']:
            v['temp_tost_actual'] += (v['sp_temp_tost'] - v['temp_tost_actual']) * 0.3
        else: v['temp_tost_actual'] = max(20.0, v['temp_tost_actual'] - 15.0) # CORRECCIÓN: Baja a 20°C
        
        # Banda
        if st.session_state.idx == 9: f['atasco_banda'] = True
        if v['vfd_banda'] and not f['atasco_banda']: v['hz_banda'] = v['sp_hz']
        else: v['hz_banda'] = 0.0
        
        # Dosificador
        if v['dosificador']:
            v['peso_actual'] = random.uniform(480, 530) if f['descalibre'] else v['sp_peso']
        else: v['peso_actual'] = 0.0
        
        # Selladora
        if st.session_state.idx == 15: f['resistencia_quemada'] = True
        if v['selladora'] and not f['resistencia_quemada']:
            v['temp_sell_actual'] += (v['sp_temp_sell'] - v['temp_sell_actual']) * 0.4
        else: v['temp_sell_actual'] = max(20.0, v['temp_sell_actual'] - 20.0) # CORRECCIÓN: Baja a 20°C
    else:
        # Todo se apaga
        v['presion_actual'] = max(0.0, v['presion_actual'] - 10.0)
        v['temp_tost_actual'] = max(20.0, v['temp_tost_actual'] - 10.0) # CORRECCIÓN: Baja a 20°C
        v['hz_banda'] = 0.0
        v['peso_actual'] = 0.0
        v['temp_sell_actual'] = max(20.0, v['temp_sell_actual'] - 10.0) # CORRECCIÓN: Baja a 20°C

# ==========================================
# 5. RENDER SCADA Y MISIONES
# ==========================================
st.markdown('<h1 style="color:#00324D; border-bottom:3px solid #FF671F;">🖥️ SCADA CAFETALERA</h1>', unsafe_allow_html=True)
components.html(render_scada_cafetalera(st.session_state.vars, st.session_state.faults), height=580)

MISIONES = [
    {"id": "M01", "q": "¿Por qué el tablero no enciende?", "ans": ["a) Falta internet.", "b) Breaker Principal abajo.", "c) Falta café."], "c": "b", "req": lambda v,f: v['breaker_main']},
    {"id": "M02", "q": "¿Qué equipo suministra energía neumática?", "ans": ["a) Compresor.", "b) VFD.", "c) Tostadora."], "c": "a", "req": lambda v,f: v['compresor']},
    {"id": "M03", "q": "Presión ideal de trabajo indicada en guía:", "ans": ["a) 10 PSI", "b) 90 PSI", "c) 500 PSI"], "c": "b", "req": lambda v,f: v['sp_presion'] == 90},
    {"id": "M04", "q": "Si SP=90 pero llega solo a 40 PSI, la falla es:", "ans": ["a) Sobrevoltaje.", "b) Fuga Neumática severa.", "c) Falla de PLC."], "c": "b", "req": lambda v,f: not f['fuga_aire']},
    {"id": "M05", "q": "Equipo que elimina la humedad del grano:", "ans": ["a) Compresor.", "b) Selladora.", "c) Tostadora."], "c": "c", "req": lambda v,f: v['tostadora']},
    {"id": "M06", "q": "Temperatura de perfil de tueste requerida:", "ans": ["a) 100°C", "b) 220°C", "c) 50°C"], "c": "b", "req": lambda v,f: v['sp_temp_tost'] == 220},
    {"id": "M07", "q": "Falla térmica en Tostadora detectada. Solución:", "ans": ["a) Reset Térmico.", "b) Cambiar PLC.", "c) Bajar presión."], "c": "a", "req": lambda v,f: not f['falla_tost']},
    {"id": "M08", "q": "Controla la velocidad del motor de la banda:", "ans": ["a) Cilindro.", "b) Variador de Frecuencia (VFD).", "c) Relé."], "c": "b", "req": lambda v,f: v['vfd_banda']},
    {"id": "M09", "q": "Frecuencia requerida para sincronización:", "ans": ["a) 10 Hz", "b) 50 Hz", "c) 100 Hz"], "c": "b", "req": lambda v,f: v['sp_hz'] == 50},
    {"id": "M10", "q": "La banda no gira (0 Hz real). Diagnóstico:", "ans": ["a) Falla internet.", "b) Atasco mecánico por falta de lubricación.", "c) Celda dañada."], "c": "b", "req": lambda v,f: not f['atasco_banda']},
    {"id": "M11", "q": "Equipo que pesa el producto:", "ans": ["a) Dosificador PLC.", "b) VFD.", "c) Compresor."], "c": "a", "req": lambda v,f: v['dosificador']},
    {"id": "M12", "q": "Peso neto requerido por bolsa:", "ans": ["a) 250g", "b) 500g", "c) 1000g"], "c": "b", "req": lambda v,f: v['sp_peso'] == 500},
    {"id": "M13", "q": "El peso oscila en el SCADA. Solución de Metrología:", "ans": ["a) Apagar tostadora.", "b) Calibrar Celda de Carga.", "c) Lubricar."], "c": "b", "req": lambda v,f: not f['descalibre']},
    {"id": "M14", "q": "Actuador que sella la bolsa térmica:", "ans": ["a) Resistencia Térmica.", "b) Motor.", "c) PLC."], "c": "a", "req": lambda v,f: v['selladora']},
    {"id": "M15", "q": "Temp. óptima de derretimiento del empaque:", "ans": ["a) 50°C", "b) 160°C", "c) 250°C"], "c": "b", "req": lambda v,f: v['sp_temp_sell'] == 160},
    {"id": "M16", "q": "Temperatura de sello cae a 25°C súbito. Diagnóstico:", "ans": ["a) Resistencia Abierta/Quemada.", "b) Fuga de aire.", "c) Sobrecarga."], "c": "a", "req": lambda v,f: not f['resistencia_quemada']},
    {"id": "M17", "q": "Fórmula del OEE Global:", "ans": ["a) Disp x Rend x Calidad", "b) MTBF / MTTR", "c) Voltaje x Corriente"], "c": "a", "req": lambda v,f: True},
    {"id": "M18", "q": "Mantenimiento Autónomo (TPM) implica:", "ans": ["a) Contratar externos.", "b) El operario limpia e inspecciona su equipo.", "c) No reparar nada."], "c": "b", "req": lambda v,f: True},
    {"id": "M19", "q": "Para ver la planta al máximo, activa:", "ans": ["a) Parada de Emergencia.", "b) Ciclo Automático Continuo.", "c) Reset general."], "c": "b", "req": lambda v,f: v['auto_mode']},
    {"id": "M20", "q": "Para una parada segura (Fin de turno):", "ans": ["a) Cortar internet.", "b) Bajar Breaker y todo en 0.", "c) Dejar automático."], "c": "b", "req": lambda v,f: not v['breaker_main'] and not v['auto_mode']}
]

if st.session_state.idx < 20:
    m = MISIONES[st.session_state.idx]
    st.markdown(f"<div class='mision-box'><b>Misión {st.session_state.idx + 1}/20:</b><br>{m['q']}</div>", unsafe_allow_html=True)
    ans = st.radio("Teoría:", m['ans'], key=f"rad_{m['id']}")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔎 Validar Teoría"):
            if ans.startswith(m['c']): st.success("✅ Teoría OK. Ejecuta la acción en el SCADA y Avanza el Tiempo.")
            else: st.error("❌ Teoría incorrecta.")
    with c2:
        if st.button("🚀 Validar Acción en SCADA", type="primary"):
            if ans.startswith(m['c']) and m['req'](st.session_state.vars, st.session_state.faults):
                st.session_state.idx += 1
                st.session_state.score += 5
                st.success("✅ ¡Misión superada!")
                st.rerun()
            else:
                st.error("❌ Ajusta los paneles HMI / Herramientas y dale a 'EJECUTAR / AVANZAR TIEMPO'.")
else:
    st.success(f"🏆 ¡Planta Asegurada! Puntaje: {st.session_state.score}/100")
    df = pd.DataFrame([{"Aprendiz": st.session_state.nombre, "Puntaje": st.session_state.score, "Misiones": "20/20"}])
    st.download_button("📥 Descargar CSV", df.to_csv(index=False), f"Reporte_{st.session_state.nombre}.csv", "text/csv")