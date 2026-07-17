"""
RESILIENCIA VALLE NORTE | Brigadas y Continuidad del Negocio
MBA - Gestión de Emergencias y Crisis (trabajo en equipo)
------------------------------------------------------------------
Módulo 1: Brigadas de Emergencia - dimensionamiento y competencias (40 min)
Módulo 2: Respuesta MATPEL y contención química (40 min)
Módulo 3: Integración con Continuidad del Negocio - BCP (40 min)

La capacidad del Módulo 2 depende de las decisiones del Módulo 1.
El cierre integra los tres módulos en un Índice de Resiliencia Organizacional.

Dependencias fijadas: streamlit==1.38.0 pandas==2.2.2 plotly==5.24.1
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
import os
from datetime import datetime

st.set_page_config(page_title="RESILIENCIA VALLE NORTE", page_icon="🧑‍🚒", layout="wide")

INSTRUCTOR_PASSWORD = "Resiliencia2026"
CSV_PATH = "resultados_resiliencia.csv"
MOD_MIN = 40
ROLES = ["Evacuación", "Primeros auxilios", "Contra incendios"]
HORAS_ROL = {"Evacuación": 8, "Primeros auxilios": 16, "Contra incendios": 24}
PRESUPUESTO_HORAS = 200
PISOS = [1, 2, 3]
TURNOS = ["Día", "Noche"]

# =========================================================
# ESTILO
# =========================================================
st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: #e6edf3; }
    .vn-card { background: linear-gradient(145deg, #161b22, #1c2330); border: 1px solid #2a3140;
               border-radius: 14px; padding: 22px 26px; margin-bottom: 16px; }
    .vn-badge { display:inline-block; background: linear-gradient(90deg, #d4a017, #f2c94c); color:#1c1c1c;
                font-weight:700; padding:6px 14px; border-radius:20px; margin:4px 6px 4px 0; font-size:0.85em; }
    .vn-alert { background-color:#3a1414; border-left:5px solid #e5484d; padding:14px 18px; border-radius:8px; margin-bottom:14px; }
    .vn-warn  { background-color:#3a2c14; border-left:5px solid #d4a017; padding:14px 18px; border-radius:8px; margin-bottom:14px; }
    .vn-timer { font-size:1.5em; font-weight:800; color:#f2c94c; }
    .vn-title { color:#f2c94c; font-weight:800; letter-spacing:1px; }
    div[data-testid="stMetricValue"] { color:#f2c94c; }
    .stButton>button { border-radius:8px; border:1px solid #3a4150; background-color:#1c2330; color:#e6edf3; font-weight:600; }
    .stButton>button:hover { border-color:#f2c94c; color:#f2c94c; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# PERSISTENCIA
# =========================================================
def load_scores():
    if os.path.exists(CSV_PATH):
        return pd.read_csv(CSV_PATH)
    return pd.DataFrame(columns=["timestamp", "equipo", "integrantes", "score_m1", "score_m2",
                                  "score_m3", "indice_resiliencia", "tiempo_total_min", "conclusion"])

def save_score(row):
    df = load_scores()
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(CSV_PATH, index=False)

def init_state():
    defaults = {
        "equipo": "", "integrantes": "",
        "m1_step": 0, "m1_start": None, "m1_score": None, "m1_log": [], "m1_capacidad_matpel": 0,
        "m2_step": 0, "m2_start": None, "m2_score": None, "m2_log": [],
        "m3_step": 0, "m3_start": None, "m3_score": None, "m3_log": [],
        "final_done": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

def timer_block(start_key, label):
    if st.session_state[start_key] is None:
        st.session_state[start_key] = time.time()
    elapsed = (time.time() - st.session_state[start_key]) / 60
    remaining = max(0, MOD_MIN - elapsed)
    c1, c2 = st.columns([3, 1])
    with c1:
        st.progress(min(1.0, elapsed / MOD_MIN))
    with c2:
        st.markdown(f'<span class="vn-timer">⏱ {remaining:0.1f} min</span>', unsafe_allow_html=True)
    if remaining <= 0:
        st.error(f"⏰ Tiempo agotado para {label}. Cierren la discusión y avancen.")
    if st.button("🔄 Actualizar cronómetro", key=f"refresh_{start_key}"):
        st.rerun()
    return elapsed

def gauge(value, title, vmin=0, vmax=100):
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=value,
        title={'text': title, 'font': {'color': '#e6edf3', 'size': 13}},
        number={'font': {'color': '#e6edf3'}},
        gauge={'axis': {'range': [vmin, vmax]}, 'bar': {'color': '#f2c94c'},
               'bgcolor': '#161b22', 'bordercolor': '#2a3140'}
    ))
    fig.update_layout(paper_bgcolor='#0d1117', height=200, margin=dict(l=10, r=10, t=40, b=10))
    return fig

def word_count(txt):
    return len((txt or "").split())

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.markdown("## 🧑‍🚒 RESILIENCIA VALLE NORTE")
st.sidebar.caption("Simulador MBA · Trabajo en equipo")
page = st.sidebar.radio("Navegación", [
    "🏠 Inicio", "🧯 Módulo 1: Brigadas", "☣️ Módulo 2: MATPEL",
    "🏢 Módulo 3: Continuidad (BCP)", "📈 Cierre integrador", "👨‍🏫 Panel Docente",
])
st.sidebar.divider()
st.session_state["equipo"] = st.sidebar.text_input("Nombre del equipo", st.session_state["equipo"])
st.session_state["integrantes"] = st.sidebar.text_area("Integrantes (uno por línea)", st.session_state["integrantes"], height=90)

def guard():
    if not st.session_state["equipo"] or not st.session_state["integrantes"]:
        st.warning("⬅️ Ingresen el nombre del equipo y sus integrantes en la barra lateral.")
        st.stop()

# =========================================================
# INICIO
# =========================================================
if page == "🏠 Inicio":
    st.markdown('<h1 class="vn-title">BRIGADAS Y RESILIENCIA EMPRESARIAL</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div class="vn-card">
    Trabajan como <b>comité de resiliencia de Grupo Valle Norte S.A.C.</b> Este simulador tiene
    <b>tres módulos encadenados</b>: lo que decidan en el Módulo 1 <b>afecta directamente</b> su
    capacidad de respuesta en el Módulo 2. El Módulo 3 cierra con un informe ejecutivo integrador
    que su equipo debe redactar. Trabajen en conjunto: cada módulo exige discusión y consenso,
    no respuestas individuales.
    </div>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""<div class="vn-card"><h4>🧯 Módulo 1</h4>
        <p>Dimensionen y asignen su brigada de emergencia con presupuesto de horas limitado.</p>
        <p><i>40 min</i></p></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class="vn-card"><h4>☣️ Módulo 2</h4>
        <p>Respondan a un derrame químico: EPP, zonas de aislamiento y contención.</p>
        <p><i>40 min · depende del Módulo 1</i></p></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""<div class="vn-card"><h4>🏢 Módulo 3</h4>
        <p>Construyan un mini BIA y activen estrategias de continuidad con presupuesto acotado.</p>
        <p><i>40 min</i></p></div>""", unsafe_allow_html=True)
    st.info("Sugerencia docente: asignen dentro del equipo un(a) coordinador(a) de brigadas, un(a) especialista MATPEL y un(a) analista BCP — pero decidan todo en conjunto, como comité.")

# =========================================================
# MÓDULO 1 — BRIGADAS
# =========================================================
elif page == "🧯 Módulo 1: Brigadas":
    guard()
    st.markdown('<h1 class="vn-title">🧯 MÓDULO 1 · Brigadas de Emergencia</h1>', unsafe_allow_html=True)
    elapsed = timer_block("m1_start", "Módulo 1")
    step = st.session_state["m1_step"]

    if step == 0:
        st.markdown("""
        <div class="vn-alert">
        <b>Sede:</b> planta de Valle Norte de 3 pisos, 180 colaboradores, operación en 2 turnos
        (día y noche). Riesgo medio-alto por procesos industriales. Deben dimensionar y asignar
        su brigada de emergencia cubriendo evacuación, primeros auxilios y contra incendios,
        con un presupuesto de <b>200 horas</b> de capacitación disponibles.
        </div>
        """, unsafe_allow_html=True)
        st.caption(f"Costo de capacitación por rol: Evacuación {HORAS_ROL['Evacuación']}h · Primeros auxilios {HORAS_ROL['Primeros auxilios']}h · Contra incendios {HORAS_ROL['Contra incendios']}h.")
        st.write("Como equipo, discutan: ¿cuántos brigadistas necesitan y con qué criterio? No hay una única cifra correcta en la norma peruana — deben justificar el criterio que apliquen (Ley 29783, tamaño de planta, nivel de riesgo).")
        if st.button("▶️ Iniciar dimensionamiento", type="primary"):
            st.session_state["m1_step"] = 1
            st.rerun()

    elif step == 1:
        st.subheader("Etapa 1 · Selección y asignación de brigadistas")
        st.caption("Marquen 'Seleccionado' y asignen un rol. La cobertura ideal cubre los 3 pisos en ambos turnos para cada especialidad.")

        candidatos = pd.DataFrame({
            "Colaborador": [f"Colaborador {i+1}" for i in range(10)],
            "Turno": ["Día", "Día", "Noche", "Día", "Noche", "Día", "Noche", "Día", "Noche", "Día"],
            "Piso": [1, 1, 1, 2, 2, 2, 3, 3, 3, 1],
            "Condición física": ["Apto", "Apto", "Apto con restricciones", "Apto", "Apto", "Apto con restricciones",
                                  "Apto", "Apto", "Apto", "Apto"],
            "Experiencia previa": ["Sí", "No", "Sí", "No", "No", "Sí", "No", "Sí", "No", "No"],
            "Seleccionado": [False] * 10,
            "Rol asignado": ["Ninguno"] * 10,
        })

        edited = st.data_editor(
            candidatos, use_container_width=True, hide_index=True, key="m1_editor",
            column_config={
                "Seleccionado": st.column_config.CheckboxColumn(),
                "Rol asignado": st.column_config.SelectboxColumn(options=["Ninguno"] + ROLES),
            },
            disabled=["Colaborador", "Turno", "Piso", "Condición física", "Experiencia previa"],
        )

        brigada = edited[(edited["Seleccionado"]) & (edited["Rol asignado"] != "Ninguno")]
        horas_totales = brigada["Rol asignado"].map(HORAS_ROL).sum()
        st.metric("Horas de capacitación usadas", f"{horas_totales} / {PRESUPUESTO_HORAS}")
        if horas_totales > PRESUPUESTO_HORAS:
            st.error("⚠️ Han excedido el presupuesto de horas. Ajusten su selección.")

        justificacion = st.text_area(
            "Justifiquen como equipo el criterio de dimensionamiento y asignación usado (mínimo ~40 palabras):",
            key="m1_justif", height=120,
        )

        if st.button("Confirmar dimensionamiento de brigada", type="primary"):
            n_pisos_turnos = len(PISOS) * len(TURNOS)
            cobertura_total = 0
            for rol in ROLES:
                subset = brigada[brigada["Rol asignado"] == rol]
                combos = subset[["Piso", "Turno"]].drop_duplicates()
                cobertura_total += len(combos)
            cobertura_pct = cobertura_total / (n_pisos_turnos * len(ROLES))

            pts_cobertura = round(cobertura_pct * 40)
            pts_presupuesto = 20 if horas_totales <= PRESUPUESTO_HORAS else 0
            tam = len(brigada)
            pts_tamano = 20 if 12 <= tam <= 22 else (10 if 8 <= tam < 12 or 22 < tam <= 26 else 0)
            pts_justif = 20 if word_count(justificacion) >= 40 else (10 if word_count(justificacion) >= 15 else 0)

            score = pts_cobertura + pts_presupuesto + pts_tamano + pts_justif
            st.session_state["m1_score"] = score
            st.session_state["m1_capacidad_matpel"] = int((brigada["Rol asignado"] == "Contra incendios").sum())
            st.session_state["m1_log"] = [
                f"Brigadistas asignados: {tam}", f"Horas usadas: {horas_totales}/{PRESUPUESTO_HORAS}",
                f"Cobertura piso-turno-rol: {cobertura_pct*100:.0f}%",
                f"Capacitados en contra incendios (base para MATPEL): {st.session_state['m1_capacidad_matpel']}",
            ]
            st.session_state["m1_justif_texto"] = justificacion
            st.session_state["m1_step"] = 2
            st.rerun()

    elif step == 2:
        st.subheader("📊 Resultado — Módulo 1")
        st.metric("Puntaje del equipo", f"{st.session_state['m1_score']}/100")
        for l in st.session_state["m1_log"]:
            st.write("• " + l)
        with st.expander("Justificación registrada"):
            st.write(st.session_state.get("m1_justif_texto", ""))
        st.markdown("""<div class="vn-warn">La cantidad de brigadistas capacitados en <b>contra incendios</b>
        que asignaron aquí determinará la capacidad de respuesta disponible en el Módulo 2 (MATPEL).</div>""",
                    unsafe_allow_html=True)
        if st.session_state["m1_score"] >= 80:
            st.success("🏆 Insignia de equipo: Comité de Brigadas de Alto Desempeño")

# =========================================================
# MÓDULO 2 — MATPEL
# =========================================================
elif page == "☣️ Módulo 2: MATPEL":
    guard()
    if st.session_state["m1_score"] is None:
        st.warning("⚠️ Recomendamos completar primero el Módulo 1: la capacidad de respuesta MATPEL depende de su brigada contra incendios. Pueden continuar, pero partirán con capacidad mínima.")
        capacidad = 0
    else:
        capacidad = st.session_state["m1_capacidad_matpel"]

    st.markdown('<h1 class="vn-title">☣️ MÓDULO 2 · Respuesta MATPEL y Contención Química</h1>', unsafe_allow_html=True)
    if capacidad < 4:
        st.markdown(f"""<div class="vn-warn">Capacidad heredada del Módulo 1: solo <b>{capacidad}</b>
        brigadistas contra incendios/MATPEL disponibles. Con menos de 4, su equipo solo puede operar
        en <b>nivel básico de contención</b> (no ingreso a zona caliente); esto limita el puntaje máximo alcanzable a 70.</div>""",
                    unsafe_allow_html=True)
    else:
        st.info(f"Capacidad heredada del Módulo 1: {capacidad} brigadistas contra incendios/MATPEL disponibles. Nivel de respuesta completo habilitado.")

    elapsed = timer_block("m2_start", "Módulo 2")
    step = st.session_state["m2_step"]

    if step == 0:
        st.markdown("""
        <div class="vn-alert">
        <b>08:15 a.m.</b> — Derrame de ácido sulfúrico concentrado en zona de almacenamiento del
        pabellón industrial. Se observan vapores corrosivos y olor irritante a 15 metros. Un
        trabajador reporta irritación en vías respiratorias. No se conoce el volumen exacto derramado.
        </div>
        """, unsafe_allow_html=True)
        if st.button("▶️ Activar protocolo MATPEL", type="primary"):
            st.session_state["m2_step"] = 1
            st.rerun()

    elif step == 1:
        st.subheader("Etapa 1 · Clasificación del riesgo (rombo NFPA 704)")
        st.caption("Como equipo, definan los valores del rombo según la descripción del incidente (escala 0 = mínimo, 4 = severo).")
        salud = st.slider("Salud (riesgo por exposición/inhalación)", 0, 4, 2)
        inflam = st.slider("Inflamabilidad", 0, 4, 2)
        react = st.slider("Reactividad", 0, 4, 2)
        esperado = {"salud": 3, "inflam": 0, "react": 1}
        if st.button("Confirmar clasificación", type="primary"):
            aciertos = sum([abs(salud - esperado["salud"]) <= 1, abs(inflam - esperado["inflam"]) <= 1, abs(react - esperado["react"]) <= 1])
            pts = aciertos * 8
            st.session_state["m2_log"].append(f"Rombo NFPA propuesto: Salud {salud}, Inflamabilidad {inflam}, Reactividad {react} ({aciertos}/3 dentro de rango esperado).")
            st.session_state.setdefault("m2_score_parcial", 0)
            st.session_state["m2_score_parcial"] += pts
            st.session_state["m2_step"] = 2
            st.rerun()

    elif step == 2:
        st.subheader("Etapa 2 · Nivel de equipo de protección personal (EPP)")
        st.caption("""Guía de decisión simplificada: Nivel A = atmósfera IDLH o desconocida con alto riesgo de vapor;
        Nivel B = riesgo respiratorio alto pero contacto dérmico moderado; Nivel C = solo riesgo de salpicadura con
        contaminante conocido; Nivel D = riesgo mínimo.""")
        epp = st.radio("Nivel de EPP a emplear:", ["Nivel A", "Nivel B", "Nivel C", "Nivel D"])
        if st.button("Confirmar EPP", type="primary"):
            pts = 25 if epp == "Nivel B" else (12 if epp == "Nivel A" else 0)
            st.session_state["m2_score_parcial"] += pts
            st.session_state["m2_log"].append(f"EPP seleccionado: {epp}")
            st.session_state["m2_step"] = 3
            st.rerun()

    elif step == 3:
        st.subheader("Etapa 3 · Zona de aislamiento y método de contención")
        st.caption("Tabla simplificada con fines pedagógicos (no reemplaza el ERG oficial): para corrosivos con vapor irritante y volumen desconocido, el rango de referencia sugerido es 25–50 m de radio en zona caliente.")
        radio = st.slider("Radio de aislamiento de zona caliente (m)", 5, 100, 30)
        metodos = st.multiselect(
            "Métodos de contención a aplicar (selección múltiple):",
            ["Dique de contención con material absorbente inerte", "Neutralización con cal o carbonato de calcio",
             "Ventilación forzada de la zona", "Lavado directo con agua a presión sobre el derrame", "Evacuación total del edificio"],
        )
        if st.button("Confirmar zona y contención", type="primary"):
            pts_radio = 15 if 25 <= radio <= 50 else (8 if 15 <= radio < 25 or 50 < radio <= 70 else 0)
            correctos = {"Dique de contención con material absorbente inerte", "Neutralización con cal o carbonato de calcio", "Ventilación forzada de la zona"}
            incorrecto_elegido = "Lavado directo con agua a presión sobre el derrame" in metodos
            aciertos_metodo = len(set(metodos) & correctos)
            pts_metodo = aciertos_metodo * 6 - (10 if incorrecto_elegido else 0)
            pts_metodo = max(0, pts_metodo)
            st.session_state["m2_score_parcial"] += pts_radio + pts_metodo
            st.session_state["m2_log"].append(f"Radio de aislamiento: {radio} m. Métodos: {', '.join(metodos) if metodos else 'ninguno'}")
            st.session_state["m2_step"] = 4
            st.rerun()

    elif step == 4:
        st.subheader("Etapa 4 · Análisis de causa raíz y lecciones aprendidas")
        causa = st.text_area("¿Cuál fue la causa raíz probable del derrame? (análisis de equipo)", height=90)
        fallas = st.text_area("¿Qué fallas de contención o preparación identifican?", height=90)
        mejoras = st.text_area("¿Qué mejoras proponen para reducir la probabilidad/impacto de un evento similar?", height=90)
        if st.button("Cerrar Módulo 2", type="primary"):
            textos = [causa, fallas, mejoras]
            pts_analisis = sum(10 if word_count(t) >= 20 else (5 if word_count(t) >= 8 else 0) for t in textos)
            score = st.session_state.get("m2_score_parcial", 0) + pts_analisis
            if capacidad < 4:
                score = min(score, 70)
            st.session_state["m2_score"] = min(100, score)
            st.session_state["m2_log"].append("Análisis de causa raíz y lecciones aprendidas registrado.")
            st.session_state["m2_analisis"] = {"causa": causa, "fallas": fallas, "mejoras": mejoras}
            st.session_state["m2_step"] = 5
            st.rerun()

    elif step == 5:
        st.subheader("📊 Resultado — Módulo 2")
        st.metric("Puntaje del equipo", f"{st.session_state['m2_score']}/100")
        for l in st.session_state["m2_log"]:
            st.write("• " + l)
        with st.expander("Análisis de causa raíz registrado"):
            for k, v in st.session_state.get("m2_analisis", {}).items():
                st.write(f"**{k.capitalize()}:** {v}")
        if st.session_state["m2_score"] >= 80:
            st.success("🏆 Insignia de equipo: Respuesta MATPEL de Alto Nivel")

# =========================================================
# MÓDULO 3 — BCP
# =========================================================
elif page == "🏢 Módulo 3: Continuidad (BCP)":
    guard()
    st.markdown('<h1 class="vn-title">🏢 MÓDULO 3 · Integración con Continuidad del Negocio</h1>', unsafe_allow_html=True)
    elapsed = timer_block("m3_start", "Módulo 3")
    step = st.session_state["m3_step"]

    procesos = pd.DataFrame({
        "Proceso": ["Producción", "Logística / despacho", "Sistemas TI", "Atención al cliente", "Nómina", "Compras"],
        "Criticidad": ["Alta", "Alta", "Alta", "Media", "Media", "Baja"],
        "MTPD (horas)": [8, 12, 4, 24, 72, 96],
        "Pérdida estimada por hora (S/)": [15000, 9000, 6000, 2000, 500, 300],
    })

    if step == 0:
        st.markdown("""
        <div class="vn-alert">
        Tras el incidente MATPEL, la planta principal permanece parcialmente inoperativa.
        La Gerencia General les encarga activar el Plan de Continuidad del Negocio (BCP)
        con un presupuesto de recuperación de <b>S/ 300,000</b>.
        </div>
        """, unsafe_allow_html=True)
        st.dataframe(procesos, use_container_width=True, hide_index=True)
        st.caption("MTPD = tiempo máximo tolerable de interrupción antes de un daño severo al negocio.")
        if st.button("▶️ Iniciar construcción del BIA", type="primary"):
            st.session_state["m3_step"] = 1
            st.rerun()

    elif step == 1:
        st.subheader("Etapa 1 · Estrategias de recuperación y RTO objetivo")
        st.caption("Para cada proceso, asignen una estrategia y un RTO (tiempo objetivo de recuperación). Presupuesto total: S/ 300,000.")

        costos = {"Sitio alterno": 90000, "Trabajo remoto": 25000, "Proveedor alterno": 40000, "Aceptar pérdida (sin estrategia)": 0}
        filas = []
        presupuesto_usado = 0
        for _, row in procesos.iterrows():
            c1, c2, c3 = st.columns([2, 2, 2])
            with c1:
                st.markdown(f"**{row['Proceso']}** · Criticidad {row['Criticidad']} · MTPD {row['MTPD (horas)']}h")
            with c2:
                estrategia = st.selectbox("Estrategia", list(costos.keys()), key=f"estr_{row['Proceso']}")
            with c3:
                rto = st.slider("RTO objetivo (h)", 1, 100, min(24, row["MTPD (horas)"]), key=f"rto_{row['Proceso']}")
            presupuesto_usado += costos[estrategia]
            filas.append({**row, "Estrategia": estrategia, "RTO asignado": rto, "Costo": costos[estrategia]})

        st.metric("Presupuesto usado", f"S/ {presupuesto_usado:,.0f} / S/ 300,000")
        if presupuesto_usado > 300000:
            st.error("⚠️ Han excedido el presupuesto de recuperación.")

        if st.button("Confirmar plan de continuidad", type="primary"):
            df_plan = pd.DataFrame(filas)
            pts = 0
            gaps = []
            for _, r in df_plan.iterrows():
                cumple_rto = r["RTO asignado"] <= r["MTPD (horas)"]
                if r["Criticidad"] == "Alta":
                    ok_estrategia = r["Estrategia"] in ["Sitio alterno", "Trabajo remoto"]
                elif r["Criticidad"] == "Media":
                    ok_estrategia = r["Estrategia"] != "Aceptar pérdida (sin estrategia)"
                else:
                    ok_estrategia = True
                if cumple_rto and ok_estrategia:
                    pts += 12
                elif cumple_rto or ok_estrategia:
                    pts += 6
                else:
                    gaps.append(r["Proceso"])
            pts_presupuesto = 15 if presupuesto_usado <= 300000 else 0
            score = min(100, pts + pts_presupuesto)
            st.session_state["m3_score"] = score
            st.session_state["m3_log"] = [f"Presupuesto usado: S/ {presupuesto_usado:,.0f}"]
            if gaps:
                st.session_state["m3_log"].append(f"Brechas críticas detectadas en: {', '.join(gaps)}")
            st.session_state["m3_plan"] = df_plan
            st.session_state["m3_step"] = 2
            st.rerun()

    elif step == 2:
        st.subheader("📊 Resultado — Módulo 3")
        st.metric("Puntaje del equipo", f"{st.session_state['m3_score']}/100")
        st.dataframe(st.session_state["m3_plan"][["Proceso", "Criticidad", "MTPD (horas)", "Estrategia", "RTO asignado", "Costo"]],
                     use_container_width=True, hide_index=True)
        for l in st.session_state["m3_log"]:
            st.write("• " + l)
        if st.session_state["m3_score"] >= 80:
            st.success("🏆 Insignia de equipo: Arquitectos de la Continuidad")

# =========================================================
# CIERRE INTEGRADOR
# =========================================================
elif page == "📈 Cierre integrador":
    guard()
    st.markdown('<h1 class="vn-title">📈 Cierre Integrador · Índice de Resiliencia Organizacional</h1>', unsafe_allow_html=True)

    scores = [st.session_state["m1_score"], st.session_state["m2_score"], st.session_state["m3_score"]]
    if any(s is None for s in scores):
        st.warning("Deben completar los tres módulos antes de generar el cierre integrador.")
        pendientes = []
        if st.session_state["m1_score"] is None: pendientes.append("Módulo 1")
        if st.session_state["m2_score"] is None: pendientes.append("Módulo 2")
        if st.session_state["m3_score"] is None: pendientes.append("Módulo 3")
        st.write("Pendientes: " + ", ".join(pendientes))
        st.stop()

    indice = round(sum(scores) / 3)
    c1, c2, c3, c4 = st.columns(4)
    c1.plotly_chart(gauge(st.session_state["m1_score"], "Módulo 1: Brigadas"), use_container_width=True, config={'displayModeBar': False})
    c2.plotly_chart(gauge(st.session_state["m2_score"], "Módulo 2: MATPEL"), use_container_width=True, config={'displayModeBar': False})
    c3.plotly_chart(gauge(st.session_state["m3_score"], "Módulo 3: BCP"), use_container_width=True, config={'displayModeBar': False})
    c4.plotly_chart(gauge(indice, "Índice de Resiliencia"), use_container_width=True, config={'displayModeBar': False})

    st.markdown("### Informe ejecutivo del equipo")
    st.caption("Redacten en conjunto: ¿cómo se conectaron sus decisiones de brigadas, MATPEL y BCP? ¿Qué harían distinto si repitieran el ejercicio?")
    conclusion = st.text_area("Conclusiones integradoras (mínimo ~80 palabras):", height=180, key="conclusion_final")
    st.caption(f"Palabras: {word_count(conclusion)}")

    if st.button("💾 Registrar informe final del equipo", type="primary"):
        if word_count(conclusion) < 40:
            st.error("El informe ejecutivo es muy breve para un cierre integrador. Amplíen su análisis.")
        else:
            tiempo_total = 0
            for k in ["m1_start", "m2_start", "m3_start"]:
                if st.session_state[k]:
                    tiempo_total += (time.time() - st.session_state[k]) / 60
            save_score({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "equipo": st.session_state["equipo"], "integrantes": st.session_state["integrantes"],
                "score_m1": st.session_state["m1_score"], "score_m2": st.session_state["m2_score"],
                "score_m3": st.session_state["m3_score"], "indice_resiliencia": indice,
                "tiempo_total_min": round(tiempo_total, 1), "conclusion": conclusion,
            })
            st.session_state["final_done"] = True
            st.success("✅ Informe final registrado. ¡Buen trabajo, equipo!")
            if indice >= 85:
                st.balloons()

# =========================================================
# PANEL DOCENTE
# =========================================================
elif page == "👨‍🏫 Panel Docente":
    st.markdown('<h1 class="vn-title">👨‍🏫 Panel Docente</h1>', unsafe_allow_html=True)
    pwd = st.text_input("Contraseña de instructor", type="password")
    if pwd != INSTRUCTOR_PASSWORD:
        st.info("Ingresa la contraseña para ver los informes de los equipos.")
        st.stop()

    df = load_scores()
    if df.empty:
        st.warning("Aún no hay informes registrados.")
        st.stop()

    st.success(f"{len(df)} equipos han registrado su informe final.")
    st.dataframe(df.sort_values("indice_resiliencia", ascending=False), use_container_width=True)

    fig = go.Figure(go.Bar(x=df["equipo"], y=df["indice_resiliencia"], marker_color="#f2c94c"))
    fig.update_layout(title="Índice de Resiliencia por equipo", paper_bgcolor='#0d1117', plot_bgcolor='#0d1117',
                       font_color='#e6edf3', height=350)
    st.plotly_chart(fig, use_container_width=True)

    st.download_button("⬇️ Descargar resultados (CSV)", df.to_csv(index=False).encode("utf-8"),
                        "resultados_resiliencia.csv", "text/csv")

    st.divider()
    if st.button("🗑️ Reiniciar todos los resultados (irreversible)"):
        if os.path.exists(CSV_PATH):
            os.remove(CSV_PATH)
        st.success("Resultados reiniciados.")
        st.rerun()
