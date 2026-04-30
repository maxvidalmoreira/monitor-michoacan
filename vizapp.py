"""
Monitor Estratégico del Estado de Michoacán
Autoría: MAX VIDAL MOREIRA (MVM)

INSTRUCCIONES:
1. Guarda este archivo como: vizapp.py
2. Coloca en la misma carpeta el Excel: CONCENTRADO DE INFO MICHO.xlsx
3. Ejecuta:

    pip install streamlit pandas numpy plotly openpyxl
    streamlit run vizapp.py

El dashboard carga los datos directamente desde el Excel. No usa carga manual de CSV.
"""

from pathlib import Path
from datetime import datetime
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# =========================================================
# CONFIGURACIÓN GENERAL
# =========================================================
st.set_page_config(
    page_title="Monitor Estratégico Michoacán",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

PRIMARY = "#081B75"
PRIMARY_DARK = "#050B38"
ACCENT = "#1DA1F2"
BG = "#F4F6FB"
CARD = "#FFFFFF"
TEXT = "#111827"
MUTED = "#6B7280"
LIGHT_BLUE = "#93C5FD"
RISK_HIGH = "#DC2626"
RISK_MED = "#F59E0B"
RISK_LOW = "#16A34A"
DATA_UPDATE_LABEL = datetime.now().strftime("%d/%m/%Y")

st.markdown(
    f"""
    <style>
    .stApp {{background:{BG}; color:{TEXT};}}
    header[data-testid="stHeader"] {{display:none !important;}}
    [data-testid="stToolbar"] {{display:none !important;}}
    [data-testid="stDecoration"] {{display:none !important;}}
    #MainMenu {{visibility:hidden;}}
    footer {{visibility:hidden;}}
    .block-container {{padding-top:1.1rem; padding-left:1.8rem; padding-right:1.8rem; padding-bottom:2rem;}}
    section[data-testid="stSidebar"] {{background:linear-gradient(180deg,#050B38 0%,#081B75 58%,#0E2CB8 100%);}}
    section[data-testid="stSidebar"] * {{color:white !important;}}
    div[data-testid="stSidebarUserContent"] {{padding-top:1.2rem;}}
    .topbar {{background:white; border:1px solid rgba(15,23,42,.06); border-radius:24px; padding:1.15rem 1.35rem; display:flex; justify-content:space-between; align-items:center; box-shadow:0 10px 28px rgba(15,23,42,.06); margin-bottom:1rem;}}
    .topbar-title {{font-size:1.45rem; font-weight:900; color:{PRIMARY}; letter-spacing:-.02em; margin:0;}}
    .topbar-subtitle {{font-size:.86rem; color:{MUTED}; margin-top:.2rem;}}
    .tag {{background:#EEF4FF; color:{PRIMARY}; padding:.45rem .7rem; border-radius:999px; font-weight:800; font-size:.78rem; border:1px solid #DDE7FF;}}
    .hero {{background:radial-gradient(circle at top right,#1DA1F2 0%,#0E2CB8 35%,#050B38 100%); padding:2.2rem; border-radius:30px; color:white; margin-bottom:1.1rem; box-shadow:0 18px 44px rgba(8,27,117,.20); min-height:210px; display:flex; flex-direction:column; justify-content:center;}}
    .hero h1 {{font-size:2.7rem; margin:0; line-height:1.02; font-weight:950; max-width:900px; letter-spacing:-.04em;}}
    .hero p {{color:rgba(255,255,255,.78); font-size:1rem; margin-top:.8rem; max-width:920px;}}
    .kpi-card {{background:{CARD}; border-radius:24px; padding:1.25rem 1.15rem; box-shadow:0 12px 30px rgba(15,23,42,.07); border:1px solid rgba(15,23,42,.06); min-height:125px;}}
    .kpi-label {{color:{MUTED}; font-size:.75rem; text-transform:uppercase; letter-spacing:.08em; font-weight:850; margin-bottom:.5rem;}}
    .kpi-value {{color:{PRIMARY}; font-size:2rem; font-weight:950; line-height:1; letter-spacing:-.04em;}}
    .kpi-note {{color:{MUTED}; font-size:.78rem; margin-top:.55rem;}}
    .module-card {{background:white; border-radius:22px; padding:1.1rem; min-height:110px; box-shadow:0 10px 24px rgba(15,23,42,.06); border:1px solid rgba(15,23,42,.06);}}
    .module-title {{color:{PRIMARY}; font-weight:900; font-size:1rem; margin-bottom:.25rem;}}
    .module-text {{color:{MUTED}; font-size:.82rem;}}
    .section-title {{color:{PRIMARY}; font-size:1.28rem; font-weight:950; margin:.9rem 0 .55rem 0; letter-spacing:-.02em;}}
    .footer {{margin-top:1.25rem; font-size:.74rem; color:{MUTED}; text-align:right;}}
    .small-note {{color:{MUTED}; font-size:.82rem;}}
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# UBICACIÓN DEL EXCEL
# =========================================================
APP_DIR = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()
DATA_FILE = APP_DIR / "CONCENTRADO DE INFO MICHO.xlsx"

# Imagen del perfil. Puedes usar cualquiera de estos nombres en la misma carpeta que vizapp.py.
PROFILE_IMAGE_OPTIONS = [
    APP_DIR / "politico.jpg",
    APP_DIR / "politico.jpeg",
    APP_DIR / "politico.png",
    APP_DIR / "politico.JPG",
    APP_DIR / "politico.JPEG",
    APP_DIR / "politico.PNG",
]
PROFILE_IMAGE = next((p for p in PROFILE_IMAGE_OPTIONS if p.exists()), None)

# =========================================================
# FUNCIONES AUXILIARES
# =========================================================
def clean_cols(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).replace("\n", " ").strip() for c in df.columns]
    return df


def nfmt(x):
    try:
        x = float(x)
        if abs(x) >= 1_000_000:
            return f"{x/1_000_000:.2f} mill."
        if abs(x) >= 1_000:
            return f"{x/1_000:.0f} mil"
        return f"{x:,.0f}"
    except Exception:
        return str(x)


def pct(x):
    try:
        return f"{float(x):.1%}"
    except Exception:
        return str(x)


def topbar(title, subtitle):
    st.markdown(
        f"""
        <div class="topbar">
            <div>
                <div class="topbar-title">{title}</div>
                <div class="topbar-subtitle">{subtitle}</div>
            </div>
            <div class="tag">MVM · Excel</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def hero(title, subtitle):
    st.markdown(f"""<div class="hero"><h1>{title}</h1><p>{subtitle}</p></div>""", unsafe_allow_html=True)


def kpi(label, value, note=""):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def module_card(title, text):
    st.markdown(
        f"""
        <div class="module-card">
            <div class="module-title">{title}</div>
            <div class="module-text">{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def chart_layout(fig, height=450):
    """Layout global para que todos los ejes/textos de gráficas salgan en negro.
    También evita que Plotly muestre 'undefined' cuando una gráfica no trae título.
    """
    if not fig.layout.title or fig.layout.title.text is None:
        fig.update_layout(title_text="")
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="black", family="Arial"),
        title_font=dict(color="black"),
        margin=dict(l=25, r=25, t=55, b=30),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.04,
            xanchor="right",
            x=1,
            font=dict(color="black"),
        ),
    )
    fig.update_xaxes(
        title_font=dict(color="black"),
        tickfont=dict(color="black"),
        color="black",
        gridcolor="rgba(0,0,0,0.14)",
        linecolor="black",
        zerolinecolor="black",
    )
    fig.update_yaxes(
        title_font=dict(color="black"),
        tickfont=dict(color="black"),
        color="black",
        gridcolor="rgba(0,0,0,0.14)",
        linecolor="black",
        zerolinecolor="black",
    )
    return fig


def footer():
    st.markdown("<div class='footer'>MAX VIDAL MOREIRA (MVM)</div>", unsafe_allow_html=True)


def no_data_message():
    st.warning("No hay datos para los filtros seleccionados.")


def make_executive_table(mapa_riesgo: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "municipio",
        "lista_nominal",
        "porcentaje_ln",
        "riesgo_label",
        "riesgo_score",
        "prioridad_score",
        "prioridad",
    ]
    available = [c for c in cols if c in mapa_riesgo.columns]
    table = mapa_riesgo[available].copy()
    if "prioridad_score" in table.columns:
        table = table.sort_values("prioridad_score", ascending=False)
    return table.head(15)


def build_risk_by_municipio(encuestas: pd.DataFrame, mapa: pd.DataFrame) -> pd.DataFrame:
    """Calcula riesgo territorial por municipio usando variables negativas / realizadas."""
    neg_cols = [
        "No Hubo Quien Contestara",
        "Menor De Edad",
        "Domicilio No Encontrado",
        "No Quisieron Contestar",
        "Otro",
    ]
    neg_cols = [c for c in neg_cols if c in encuestas.columns]
    if encuestas.empty or "Municipio" not in encuestas.columns or "Realizadas" not in encuestas.columns:
        base = mapa.copy()
        base["riesgo_score"] = 0
        base["riesgo_nivel"] = "Bajo"
        base["riesgo_label"] = "Bajo"
        base["prioridad_score"] = base.get("lista_nominal", 0)
        return base

    temp = encuestas.copy()
    temp["negativas"] = temp[neg_cols].sum(axis=1) if neg_cols else 0
    risk = temp.groupby("Municipio", dropna=False).agg(
        realizadas=("Realizadas", "sum"),
        completadas=("Completadas", "sum") if "Completadas" in temp.columns else ("Realizadas", "sum"),
        negativas=("negativas", "sum"),
    ).reset_index()
    risk["riesgo_score"] = np.where(risk["realizadas"] > 0, risk["negativas"] / risk["realizadas"] * 100, 0)
    risk["riesgo_nivel"] = np.select(
        [risk["riesgo_score"] >= 35, risk["riesgo_score"] >= 18],
        ["Alto", "Medio"],
        default="Bajo",
    )
    risk["riesgo_label"] = np.select(
        [risk["riesgo_score"] >= 35, risk["riesgo_score"] >= 18],
        ["🔴 Alto", "🟡 Medio"],
        default="🟢 Bajo",
    )

    base = mapa.merge(risk, left_on="municipio", right_on="Municipio", how="left")
    for col in ["realizadas", "completadas", "negativas", "riesgo_score"]:
        if col in base.columns:
            base[col] = base[col].fillna(0)
    base["riesgo_nivel"] = base["riesgo_nivel"].fillna("Bajo")
    base["riesgo_label"] = base["riesgo_label"].fillna("🟢 Bajo")
    base["prioridad_score"] = base["lista_nominal"].fillna(0) * (1 + base["riesgo_score"].fillna(0) / 100)
    return base

# =========================================================
# CARGA DIRECTA DEL EXCEL
# =========================================================
@st.cache_data
def load_excel_data(file_path: Path):
    if not file_path.exists():
        st.error(
            "No encontré el archivo **CONCENTRADO DE INFO MICHO.xlsx**. "
            "Debe estar en la misma carpeta que `vizapp.py`."
        )
        st.stop()

    xls = pd.ExcelFile(file_path)

    solicitudes = clean_cols(pd.read_excel(xls, sheet_name="SOLICITUDES"))
    # La hoja MAPA DE MICH tiene una fila de título arriba; los encabezados reales están en la fila 2.
    mapa = clean_cols(pd.read_excel(xls, sheet_name="MAPA DE MICH", header=1))
    historico = clean_cols(pd.read_excel(xls, sheet_name="HISTORICO ELECCIONES"))
    casillas = clean_cols(pd.read_excel(xls, sheet_name="CASILLAS"))
    satisfaccion = clean_cols(pd.read_excel(xls, sheet_name="ENCUESTAS DE SATISFACCION "))
    encuestas = clean_cols(pd.read_excel(xls, sheet_name="ENCUESTAS"))
    contexto_electoral = clean_cols(pd.read_excel(xls, sheet_name="CONTEXTO ELECTORAL"))
    edades = clean_cols(pd.read_excel(xls, sheet_name="LISTA NOMINAL POR EDADES"))
    contexto_estatal = clean_cols(pd.read_excel(xls, sheet_name="CONTEXTO ESTATAL"))

    mapa = mapa.rename(
        columns={
            "Latitud": "lat",
            "Longitud": "lon",
            "Municipio": "municipio",
            "Lista_Nominal": "lista_nominal",
            "Porcentaje_LN": "porcentaje_ln",
        }
    )

    for col in ["lat", "lon", "lista_nominal", "porcentaje_ln"]:
        if col in mapa.columns:
            mapa[col] = pd.to_numeric(mapa[col], errors="coerce")

    mapa = mapa.dropna(subset=["lat", "lon", "municipio"])
    mapa["municipio"] = mapa["municipio"].astype(str).str.strip()

    if "porcentaje_ln" in mapa.columns:
        q75 = mapa["porcentaje_ln"].quantile(0.75)
        q40 = mapa["porcentaje_ln"].quantile(0.40)
        mapa["prioridad"] = np.where(
            mapa["porcentaje_ln"] >= q75,
            "Alta",
            np.where(mapa["porcentaje_ln"] >= q40, "Media", "Baja"),
        )
    else:
        mapa["prioridad"] = "Media"

    solicitudes["Fecha"] = pd.to_datetime(solicitudes.get("Fecha"), errors="coerce")
    solicitudes["Fecha de atención"] = pd.to_datetime(solicitudes.get("Fecha de atención"), errors="coerce")
    if "Municipio" in solicitudes.columns:
        solicitudes["Municipio"] = solicitudes["Municipio"].astype(str).str.strip()

    if {"TOTAL", "Lista"}.issubset(casillas.columns):
        casillas["Participación"] = pd.to_numeric(casillas["TOTAL"], errors="coerce") / pd.to_numeric(casillas["Lista"], errors="coerce")
    else:
        casillas["Participación"] = np.nan

    party_cols = [c for c in ["PAN", "PRI", "PRD", "MOR"] if c in casillas.columns]
    if party_cols:
        casillas["Ganador"] = casillas[party_cols].apply(pd.to_numeric, errors="coerce").idxmax(axis=1)
    else:
        casillas["Ganador"] = "N/A"

    if "Municipio" in encuestas.columns:
        encuestas["Municipio"] = encuestas["Municipio"].astype(str).str.strip().str.title()

    return solicitudes, mapa, historico, casillas, satisfaccion, encuestas, contexto_electoral, edades, contexto_estatal


solicitudes_df, mapa_df, historico_df, casillas_df, satisfaccion_df, encuestas_df, contexto_electoral_df, edades_df, contexto_estatal_df = load_excel_data(DATA_FILE)

# Base enriquecida para riesgo territorial y ranking estratégico.
mapa_riesgo_df = build_risk_by_municipio(encuestas_df, mapa_df)

# =========================================================
# SIDEBAR / FILTROS
# =========================================================
st.sidebar.markdown("## Monitor Michoacán")
st.sidebar.caption("Control de información")
st.sidebar.markdown("---")

PAGES = [
    "01 · Menú ejecutivo",
    "02 · Mapa nominal",
    "03 · Datos estatales",
    "04 · Datos electorales",
    "05 · Edad y género",
    "06 · Histórico votaciones",
    "07 · Encuestas",
    "08 · Casillas",
    "09 · Solicitudes",
    "10 · Opinión programas sociales",
]

page = st.sidebar.radio("Navegación", PAGES)

st.sidebar.markdown("---")
st.sidebar.markdown("### Filtros complementarios")

municipios_mapa = sorted(mapa_riesgo_df["municipio"].dropna().unique().tolist()) if "municipio" in mapa_riesgo_df.columns else []
municipios_encuestas = sorted(encuestas_df["Municipio"].dropna().unique().tolist()) if "Municipio" in encuestas_df.columns else []
municipios_solicitudes = sorted(solicitudes_df["Municipio"].dropna().unique().tolist()) if "Municipio" in solicitudes_df.columns else []
municipios_all = sorted(set(municipios_mapa + municipios_encuestas + municipios_solicitudes))

municipio_activo = st.sidebar.selectbox(
    "Municipio activo",
    options=["Todos"] + municipios_all,
    index=0,
    help="Filtro territorial global para mapa, encuestas y solicitudes."
)
st.session_state["municipio_activo"] = municipio_activo

prioridad_filter = st.sidebar.multiselect(
    "Prioridad solicitud",
    sorted(solicitudes_df["Prioridad"].dropna().unique().tolist()) if "Prioridad" in solicitudes_df.columns else [],
    default=[],
)
estatus_filter = st.sidebar.multiselect(
    "Estatus solicitud",
    sorted(solicitudes_df["Estatus"].dropna().unique().tolist()) if "Estatus" in solicitudes_df.columns else [],
    default=[],
)

mapa_view = mapa_riesgo_df.copy()
encuestas_view = encuestas_df.copy()
solicitudes_view = solicitudes_df.copy()

if municipio_activo != "Todos":
    if "municipio" in mapa_view.columns:
        mapa_view = mapa_view[mapa_view["municipio"] == municipio_activo]
    if "Municipio" in encuestas_view.columns:
        encuestas_view = encuestas_view[encuestas_view["Municipio"] == municipio_activo]
    if "Municipio" in solicitudes_view.columns:
        solicitudes_view = solicitudes_view[solicitudes_view["Municipio"] == municipio_activo]

if prioridad_filter and "Prioridad" in solicitudes_view.columns:
    solicitudes_view = solicitudes_view[solicitudes_view["Prioridad"].isin(prioridad_filter)]
if estatus_filter and "Estatus" in solicitudes_view.columns:
    solicitudes_view = solicitudes_view[solicitudes_view["Estatus"].isin(estatus_filter)]

st.sidebar.markdown("---")
# Modo presentación controlado desde sidebar.
# Para salir se usa un botón con callback para evitar errores de session_state.
if "presentacion_activa" not in st.session_state:
    st.session_state["presentacion_activa"] = False

def activar_presentacion():
    st.session_state["presentacion_activa"] = True


def salir_presentacion():
    st.session_state["presentacion_activa"] = False

presentacion_toggle = st.sidebar.toggle(
    "Modo presentación",
    value=st.session_state["presentacion_activa"],
    on_change=lambda: st.session_state.update(
        {"presentacion_activa": st.session_state.get("presentacion_toggle_widget", False)}
    ),
    key="presentacion_toggle_widget",
)

presentacion = st.session_state["presentacion_activa"]

if presentacion:
    st.markdown(
        """
        <style>
        /* Modo presentación real */
        section[data-testid="stSidebar"] {display:none !important;}
        div[data-testid="collapsedControl"] {display:none !important;}
        header[data-testid="stHeader"] {display:none !important;}
        [data-testid="stToolbar"] {display:none !important;}
        [data-testid="stDecoration"] {display:none !important;}
        #MainMenu {visibility:hidden;}
        footer {visibility:hidden;}

        .block-container {
            padding-top:1.2rem;
            padding-left:2.5rem;
            padding-right:2.5rem;
            padding-bottom:2rem;
            max-width:100% !important;
        }
        .hero {
            min-height:260px !important;
            padding:3rem !important;
        }
        .hero h1 {font-size:3.45rem !important;}
        .hero p {font-size:1.25rem !important;}
        .kpi-card {
            min-height:150px !important;
            padding:1.55rem 1.35rem !important;
        }
        .kpi-value {font-size:2.8rem !important;}
        .kpi-label {font-size:.85rem !important;}
        .topbar-title {font-size:2rem !important;}
        .topbar-subtitle {font-size:1rem !important;}
        div[data-testid="stButton"] button {
            background:#081B75 !important;
            color:white !important;
            border:1px solid #081B75 !important;
            font-weight:800 !important;
            border-radius:14px !important;
        }
        div[data-testid="stButton"] button p {
            color:white !important;
        }
        </style>

        """,
        unsafe_allow_html=True,
    )

    nav_col, exit_col = st.columns([5, 1])
    with nav_col:
        page = st.selectbox(
            "Navegación modo presentación",
            PAGES,
            index=PAGES.index(page) if page in PAGES else 0,
            key="presentacion_page_selector",
        )
    with exit_col:
        st.write("")
        st.button("Salir", use_container_width=True, on_click=salir_presentacion)

st.sidebar.caption("MAX VIDAL MOREIRA (MVM)")

# =========================================================
# PÁGINAS
# =========================================================
if page == "01 · Menú ejecutivo":
    intro_col, image_col = st.columns([2.6, 1])
    with intro_col:
        hero(
            "Monitor Estratégico del Estado de Michoacán",
            "Panel web interactivo conectado directamente al concentrado de información. Incluye navegación por módulos, filtros, KPIs territoriales, análisis electoral, encuestas, casillas y solicitudes.",
        )
    with image_col:
        if PROFILE_IMAGE is not None:
            st.image(str(PROFILE_IMAGE), use_container_width=True)
            st.caption("Perfil de referencia para representación de datos")
        else:
            st.info("Coloca la imagen como `politico.jpg`, `politico.jpeg` o `politico.png` en la misma carpeta que `vizapp.py`.")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi("Municipios en mapa", mapa_view["municipio"].nunique() if len(mapa_view) else 0, "Coordenadas + lista nominal")
    with c2:
        kpi("Lista nominal", nfmt(mapa_view["lista_nominal"].sum()) if len(mapa_view) else "0", "Base por municipio")
    with c3:
        kpi("Solicitudes", len(solicitudes_view), "Según filtros activos")
    with c4:
        total_realizadas = encuestas_view["Realizadas"].sum() if "Realizadas" in encuestas_view.columns and len(encuestas_view) else 0
        kpi("Encuestas realizadas", nfmt(total_realizadas), "Base operativa")

    c5, c6, c7, c8 = st.columns(4)
    municipio_critico = mapa_riesgo_df.sort_values("prioridad_score", ascending=False).iloc[0] if len(mapa_riesgo_df) else None
    with c5:
        kpi(
            "Municipio crítico",
            municipio_critico["municipio"] if municipio_critico is not None else "N/A",
            "Mayor score estratégico"
        )
    with c6:
        meta_total = encuestas_view["Meta"].sum() if "Meta" in encuestas_view.columns and len(encuestas_view) else 0
        completadas_total = encuestas_view["Completadas"].sum() if "Completadas" in encuestas_view.columns and len(encuestas_view) else 0
        cobertura = completadas_total / meta_total if meta_total else 0
        kpi("Cobertura territorial", pct(cobertura), "Completadas / meta")
    with c7:
        riesgo_prom = mapa_view["riesgo_score"].mean() if "riesgo_score" in mapa_view.columns and len(mapa_view) else 0
        riesgo_label_global = "🔴 Alto" if riesgo_prom >= 35 else "🟡 Medio" if riesgo_prom >= 18 else "🟢 Bajo"
        kpi("Semáforo de riesgo", riesgo_label_global, f"Índice: {riesgo_prom:.1f}")
    with c8:
        kpi("Actualización", DATA_UPDATE_LABEL, "Control de información")

    st.markdown("<div class='section-title'>Briefing territorial</div>", unsafe_allow_html=True)
    b1, b2 = st.columns([1.15, 2.85])
    with b1:
        if municipio_activo != "Todos" and len(mapa_view):
            riesgo_actual = mapa_view["riesgo_score"].mean()
            riesgo_label = mapa_view["riesgo_label"].iloc[0]
        else:
            riesgo_actual = mapa_riesgo_df["riesgo_score"].mean() if len(mapa_riesgo_df) else 0
            riesgo_label = "🔴 Alto" if riesgo_actual >= 35 else "🟡 Medio" if riesgo_actual >= 18 else "🟢 Bajo"
        kpi("Semáforo de riesgo", riesgo_label, f"Índice: {riesgo_actual:.1f}")
    with b2:
        top_priority = mapa_riesgo_df.sort_values("prioridad_score", ascending=False).head(10)
        fig_rank = px.bar(
            top_priority,
            x="prioridad_score",
            y="municipio",
            orientation="h",
            color="prioridad",
            text="riesgo_label",
            title="Top 10 municipios prioritarios",
            color_discrete_map={"Alta": PRIMARY, "Media": ACCENT, "Baja": LIGHT_BLUE},
        )
        fig_rank.update_yaxes(autorange="reversed", title="")
        fig_rank.update_xaxes(title="Score estratégico")
        st.plotly_chart(chart_layout(fig_rank, 420), use_container_width=True)

    st.markdown("<div class='section-title'>Ranking ejecutivo territorial</div>", unsafe_allow_html=True)
    executive_table = make_executive_table(mapa_riesgo_df)
    st.dataframe(executive_table, use_container_width=True, hide_index=True)
    csv_exec = executive_table.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="Descargar ranking ejecutivo CSV",
        data=csv_exec,
        file_name="ranking_ejecutivo_michoacan.csv",
        mime="text/csv",
    )

    st.markdown("<div class='section-title'>Módulos del monitor</div>", unsafe_allow_html=True)
    cols = st.columns(3)
    modules = [
        ("Mapa nominal", "Mapa territorial con lista nominal por municipio."),
        ("Datos estatales", "Contexto demográfico, social y económico."),
        ("Datos electorales", "Padrón, lista nominal, distritos y secciones."),
        ("Edad y género", "Lista nominal por edad, hombres y mujeres."),
        ("Histórico votaciones", "Comparativo 2021 vs 2024 por partido."),
        ("Encuestas", "Avance de levantamiento por municipio."),
        ("Casillas", "Votos por sección, partido y colonia."),
        ("Solicitudes", "Gestión territorial de solicitudes."),
        ("Opinión programas sociales", "Score de satisfacción por respondente."),
    ]
    for i, (title, text) in enumerate(modules):
        with cols[i % 3]:
            module_card(title, text)
            st.write("")
    footer()

elif page == "02 · Mapa nominal":
    topbar("Mapa nominal", "Selecciona un municipio para enfocar el mapa y actualizar los indicadores.")

    col_selector, col_hint = st.columns([1.2, 2.8])
    with col_selector:
        municipio_mapa = st.selectbox(
            "Seleccionar municipio en mapa",
            options=["Todos"] + municipios_mapa,
            index=(["Todos"] + municipios_mapa).index(st.session_state.get("municipio_activo", "Todos")) if st.session_state.get("municipio_activo", "Todos") in (["Todos"] + municipios_mapa) else 0,
            key="selector_mapa_nominal",
        )
        st.session_state["municipio_activo"] = municipio_mapa
    with col_hint:
        st.markdown(
            "<div class='small-note'>El selector funciona como interacción territorial. Al cambiar municipio, el mapa y los KPIs se enfocan en la selección. Para volver a ver todo el estado, selecciona <b>Todos</b>.</div>",
            unsafe_allow_html=True,
        )

    mapa_page_view = mapa_riesgo_df.copy()
    if municipio_mapa != "Todos":
        mapa_page_view = mapa_page_view[mapa_page_view["municipio"] == municipio_mapa]

    if mapa_page_view.empty:
        no_data_message()
    else:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            kpi("Lista nominal", nfmt(mapa_page_view["lista_nominal"].sum()))
        with c2:
            kpi("Municipios visibles", mapa_page_view["municipio"].nunique())
        with c3:
            kpi("Mayor municipio", mapa_page_view.sort_values("lista_nominal", ascending=False).iloc[0]["municipio"])
        with c4:
            kpi("% LN visible", pct(mapa_page_view["porcentaje_ln"].sum()))

        center_lat = mapa_page_view["lat"].mean()
        center_lon = mapa_page_view["lon"].mean()
        zoom_level = 9 if municipio_mapa != "Todos" else 6

        fig = px.scatter_mapbox(
            mapa_page_view,
            lat="lat",
            lon="lon",
            size="lista_nominal",
            color="riesgo_nivel",
            hover_name="municipio",
            hover_data={"lista_nominal": ":,", "porcentaje_ln": ":.2%", "lat": False, "lon": False},
            zoom=zoom_level,
            height=570,
            mapbox_style="carto-positron",
            color_discrete_map={"Alto": RISK_HIGH, "Medio": RISK_MED, "Bajo": RISK_LOW},
            center={"lat": center_lat, "lon": center_lon},
        )
        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), font=dict(color="black"), title_text="")
        st.plotly_chart(fig, use_container_width=True)
        cols_to_show = [c for c in ["CVE_MUN", "municipio", "lista_nominal", "porcentaje_ln", "prioridad"] if c in mapa_page_view.columns]
        st.dataframe(mapa_page_view[cols_to_show], use_container_width=True, hide_index=True)
    footer()

elif page == "03 · Datos estatales":
    topbar("Contexto del Estado de Michoacán", "Indicadores generales desde la hoja CONTEXTO ESTATAL.")
    row = contexto_estatal_df.iloc[0]
    values = [
        ("Habitantes totales", nfmt(row["Habitantes totales"]), "Población estatal"),
        ("Mujeres", pct(row["% Mujeres"]), "Distribución"),
        ("Hombres", pct(row["% Hombres"]), "Distribución"),
        ("PEA", nfmt(row["PEA (Población Económicamente Activa)"]), "Población activa"),
        ("No activa", nfmt(row["Población Económicamente No Activa"]), "Población no activa"),
        ("Beneficiarios", nfmt(row["Beneficiarios Programas del Bienestar"]), "Programas bienestar"),
        ("Pobreza moderada", nfmt(row["Personas en pobreza moderada"]), "Estimación"),
        ("Pobreza extrema", nfmt(row["Personas en pobreza extrema"]), "Estimación"),
        ("Pobreza laboral", pct(row["% en pobreza laboral"]), "Ingreso laboral"),
        ("Informalidad", pct(row["% Informalidad laboral"]), "Mercado laboral"),
        ("Escolaridad", row["Años de escolaridad promedio"], "Años promedio"),
        ("Viviendas", nfmt(row["Viviendas habitadas"]), "Habitadas"),
    ]
    cols = st.columns(4)
    for i, (label, value, note) in enumerate(values):
        with cols[i % 4]:
            kpi(label, value, note)
            st.write("")
    footer()

elif page == "04 · Datos electorales":
    topbar("Contexto electoral del Estado de Michoacán", "Indicadores desde la hoja CONTEXTO ELECTORAL.")
    row = contexto_electoral_df.iloc[0]
    values = [
        ("Municipios", row["Municipios"], "Total estatal"),
        ("Distritos federales", row["Distritos federales"], "Estructura electoral"),
        ("Distritos locales", row["Distritos locales"], "Estructura electoral"),
        ("Secciones", nfmt(row["Secciones electorales"]), "Secciones electorales"),
        ("Padrón electoral", nfmt(row["Padrón electoral total"]), "Total"),
        ("Padrón mujeres", nfmt(row["Padrón electoral – Mujeres"]), "Mujeres"),
        ("Padrón hombres", nfmt(row["Padrón electoral – Hombres"]), "Hombres"),
        ("Lista nominal", nfmt(row["Lista nominal total"]), "Total"),
        ("Lista nominal mujeres", nfmt(row["Lista nominal – Mujeres"]), "Mujeres"),
        ("Lista nominal hombres", nfmt(row["Lista nominal – Hombres"]), "Hombres"),
        ("No binario", row["Lista nominal – No binario"], "Lista nominal"),
        ("Corte", row["Corte de datos"], "Fecha"),
    ]
    cols = st.columns(4)
    for i, (label, value, note) in enumerate(values):
        with cols[i % 4]:
            kpi(label, value, note)
            st.write("")
    footer()

elif page == "05 · Edad y género":
    topbar("Edad y género", "Lista nominal por rango de edad, hombres, mujeres y total.")
    edades_long = edades_df.melt(id_vars="Edad (años)", value_vars=["Hombres", "Mujeres"], var_name="Género", value_name="Personas")
    fig = px.bar(
        edades_long,
        x="Edad (años)",
        y="Personas",
        color="Género",
        barmode="group",
        text="Personas",
        color_discrete_map={"Hombres": ACCENT, "Mujeres": PRIMARY},
    )
    fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fig.update_yaxes(title="Personas")
    st.plotly_chart(chart_layout(fig, 520), use_container_width=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        kpi("Mujeres", nfmt(edades_df["Mujeres"].sum()), "Lista nominal")
    with c2:
        kpi("Hombres", nfmt(edades_df["Hombres"].sum()), "Lista nominal")
    with c3:
        kpi("Total", nfmt(edades_df["Total"].sum()), "Lista nominal")
    st.dataframe(edades_df, use_container_width=True, hide_index=True)
    footer()

elif page == "06 · Histórico votaciones":
    topbar("Histórico de votaciones", "Comparativo por partido entre los dos bloques electorales del archivo.")
    hist = historico_df.rename(
        columns={
            "Partido Político": "Partido 2021",
            "Votación": "Votación 2021",
            "Porcentaje": "% 2021",
            "Partido Político_1": "Partido",
            "Votación_2": "Votación 2024",
            "Porcentaje_3": "% 2024",
        }
    )
    hist["Diferencia pp"] = hist["% 2024"] - hist["% 2021"]
    long = pd.DataFrame(
        {
            "Partido": list(hist["Partido"]) * 2,
            "Año": ["2021"] * len(hist) + ["2024"] * len(hist),
            "Porcentaje": list(hist["% 2021"]) + list(hist["% 2024"]),
        }
    )
    color_partidos = {
        "MORENA": "#7A1038",
        "PAN": "#0057B8",
        "PRI": "#00843D",
        "PRD": "#F6C600",
        "PT": "#D71920",
        "PVEM": "#00A650",
        "MC": "#F58220",
        "PES": "#6D28D9",
    }
    fig = px.bar(
        long,
        x="Partido",
        y="Porcentaje",
        color="Partido",
        facet_col="Año",
        text="Porcentaje",
        color_discrete_map=color_partidos,
    )
    fig.update_traces(texttemplate="%{text:.1%}", textposition="outside")
    fig.update_yaxes(tickformat=".0%", matches=None)
    fig.update_xaxes(tickangle=-25)
    st.plotly_chart(chart_layout(fig, 520), use_container_width=True)
    c1, c2 = st.columns([2, 1])
    with c1:
        diff = px.bar(
            hist,
            x="Partido",
            y="Diferencia pp",
            color="Partido",
            text="Diferencia pp",
            title="Diferencia 2024 vs 2021",
            color_discrete_map=color_partidos,
        )
        diff.update_traces(texttemplate="%{text:.1%}", textposition="outside")
        diff.update_yaxes(tickformat=".0%")
        st.plotly_chart(chart_layout(diff, 360), use_container_width=True)
    with c2:
        kpi("Votación total 2021", nfmt(hist["Votación 2021"].sum()))
        st.write("")
        kpi("Votación total 2024", nfmt(hist["Votación 2024"].sum()))
    st.dataframe(hist, use_container_width=True, hide_index=True)
    footer()

elif page == "07 · Encuestas":
    topbar("Encuestas", "Avance por municipio: completadas, realizadas, meta, variables negativas y riesgo territorial calculado.")
    if encuestas_view.empty:
        no_data_message()
    else:
        c1, c2, c3, c4, c5 = st.columns(5)
        realizadas = encuestas_view["Realizadas"].sum()
        completadas = encuestas_view["Completadas"].sum()
        neg_cols_riesgo = [
            "No Hubo Quien Contestara",
            "Menor De Edad",
            "Domicilio No Encontrado",
            "No Quisieron Contestar",
            "Otro",
        ]
        neg_cols_riesgo = [c for c in neg_cols_riesgo if c in encuestas_view.columns]
        negativos_total = encuestas_view[neg_cols_riesgo].sum().sum() if neg_cols_riesgo else 0
        riesgo_municipio = (negativos_total / realizadas * 100) if realizadas else 0
        with c1:
            kpi("Realizadas", nfmt(realizadas))
        with c2:
            kpi("Completadas", nfmt(completadas))
        with c3:
            kpi("Meta", nfmt(encuestas_view["Meta"].sum()))
        with c4:
            kpi("% Completadas", pct(completadas / realizadas if realizadas else 0))
        with c5:
            nivel_riesgo = "🔴 Alto" if riesgo_municipio >= 35 else "🟡 Medio" if riesgo_municipio >= 18 else "🟢 Bajo"
            kpi("Riesgo", nivel_riesgo, f"Índice: {riesgo_municipio:.1f}")

        fig = px.bar(
            encuestas_view.sort_values("Realizadas", ascending=False),
            x="Municipio",
            y=["Completadas", "Realizadas"],
            barmode="group",
            text_auto=True,
            color_discrete_sequence=[PRIMARY, ACCENT],
        )
        fig.update_yaxes(title="Encuestas")
        st.plotly_chart(chart_layout(fig, 520), use_container_width=True)

        neg_cols = [
            "No Hubo Quien Contestara",
            "Menor De Edad",
            "Domicilio No Encontrado",
            "No Quisieron Contestar",
            "Otro",
        ]
        neg_cols = [c for c in neg_cols if c in encuestas_view.columns]
        if neg_cols:
            neg = encuestas_view[neg_cols].sum().reset_index()
            neg.columns = ["Variable", "Total"]
            fig2 = px.bar(neg, x="Variable", y="Total", text="Total", title="Variables negativas acumuladas", color_discrete_sequence=[PRIMARY])
            st.plotly_chart(chart_layout(fig2, 380), use_container_width=True)
        st.dataframe(encuestas_view, use_container_width=True, hide_index=True)
    footer()

elif page == "08 · Casillas":
    topbar("Casillas", "Análisis por sección, colonia, partido ganador y participación.")
    if casillas_df.empty:
        no_data_message()
    else:
        seccion = st.selectbox("Selecciona sección", casillas_df["Sección"].tolist())
        view = casillas_df[casillas_df["Sección"] == seccion].iloc[0]
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            kpi("Sección", int(view["Sección"]))
        with c2:
            kpi("Colonia", view["Colonia"])
        with c3:
            kpi("Lista", nfmt(view["Lista"]))
        with c4:
            kpi("Ganador", view["Ganador"])
        with c5:
            kpi("Participación", pct(view["Participación"]))

        parties = [c for c in ["PAN", "PRI", "PRD", "MOR", "NULOS"] if c in casillas_df.columns]
        selected_row = pd.DataFrame({"Partido": parties, "Votos": [view[p] for p in parties]})
        fig = px.bar(selected_row, x="Partido", y="Votos", text="Votos", color="Partido", color_discrete_sequence=[ACCENT, PRIMARY, "#64748B", "#0F172A", "#CBD5E1"])
        st.plotly_chart(chart_layout(fig, 420), use_container_width=True)

        fig2 = px.bar(casillas_df, x="Sección", y="TOTAL", color="Ganador", text="TOTAL", title="Votos totales por sección")
        fig2.update_xaxes(type="category")
        st.plotly_chart(chart_layout(fig2, 480), use_container_width=True)
        st.dataframe(casillas_df, use_container_width=True, hide_index=True)
    footer()

elif page == "09 · Solicitudes":
    topbar("Solicitudes", "Gestión territorial de solicitudes por municipio/colonia, sector, prioridad y estatus.")
    if solicitudes_view.empty:
        no_data_message()
    else:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            kpi("Total solicitudes", len(solicitudes_view))
        with c2:
            kpi("En trámite", int((solicitudes_view["Estatus"] == "En trámite").sum()))
        with c3:
            kpi("Terminadas", int((solicitudes_view["Estatus"] == "Terminado").sum()))
        with c4:
            kpi("Prioridad alta", int((solicitudes_view["Prioridad"] == "Alta").sum()))

        c5, c6 = st.columns([1.35, 1])
        with c5:
            st.dataframe(solicitudes_view, use_container_width=True, hide_index=True)
        with c6:
            fig = px.pie(solicitudes_view, names="Estatus", title="Distribución por estatus", hole=.58, color_discrete_sequence=[PRIMARY, ACCENT, LIGHT_BLUE])
            st.plotly_chart(chart_layout(fig, 410), use_container_width=True)
            sector_col = "Sector para su atención"
            if sector_col in solicitudes_view.columns:
                sector_df = solicitudes_view.groupby(sector_col, dropna=False).size().reset_index(name="Solicitudes")
                fig2 = px.bar(sector_df, x=sector_col, y="Solicitudes", text="Solicitudes", title="Solicitudes por sector", color_discrete_sequence=[PRIMARY])
                st.plotly_chart(chart_layout(fig2, 360), use_container_width=True)
    footer()

elif page == "10 · Opinión programas sociales":
    topbar("Encuestas de satisfacción con programas sociales", "Resultados por respondente y score total.")
    if satisfaccion_df.empty:
        no_data_message()
    else:
        question_cols = [c for c in satisfaccion_df.columns if c not in ["Respondente", "Score Total"]]
        c1, c2, c3 = st.columns(3)
        with c1:
            kpi("Score promedio", f"{satisfaccion_df['Score Total'].mean():.1f}", "Sobre escala del archivo")
        with c2:
            kpi("Respondentes", len(satisfaccion_df), "Encuestas")
        with c3:
            kpi("Mayor score", f"{satisfaccion_df['Score Total'].max():.0f}", "Máximo observado")

        fig = px.bar(satisfaccion_df, x="Respondente", y="Score Total", text="Score Total", color="Score Total", color_continuous_scale=[[0, LIGHT_BLUE], [1, PRIMARY]])
        st.plotly_chart(chart_layout(fig, 470), use_container_width=True)

        avg_questions = satisfaccion_df[question_cols].mean(numeric_only=True).reset_index()
        avg_questions.columns = ["Pregunta", "Promedio"]
        fig2 = px.bar(avg_questions, x="Promedio", y="Pregunta", orientation="h", text="Promedio", title="Promedio por pregunta", color_discrete_sequence=[PRIMARY])
        fig2.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        st.plotly_chart(chart_layout(fig2, 500), use_container_width=True)
        st.dataframe(satisfaccion_df, use_container_width=True, hide_index=True)
    footer()










