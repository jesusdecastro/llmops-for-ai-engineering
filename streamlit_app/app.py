"""TechShop Agent — interfaz Streamlit profesional para el curso LLMOps."""

from __future__ import annotations

import os
import time
import uuid

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Configuración de página — debe ser la PRIMERA llamada a Streamlit
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="TechShop · Agente IA",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "TechShop Agent — Curso LLMOps · Powered by AWS Bedrock & Strands",
    },
)

# ---------------------------------------------------------------------------
# CSS personalizado — paleta Hiberus (azul #0062B8, blanco, grises claros)
# ---------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
/* ── Tipografía y fondo global ─────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Fondo principal */
.stApp {
    background: #F4F7FB;
}

/* ── Header hero ───────────────────────────────────────────────────── */
.hero-banner {
    background: linear-gradient(135deg, #0062B8 0%, #004A8F 50%, #003470 100%);
    border-radius: 16px;
    padding: 32px 40px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 8px 32px rgba(0, 98, 184, 0.25);
}
.hero-title {
    color: #FFFFFF;
    font-size: 2rem;
    font-weight: 700;
    margin: 0;
    letter-spacing: -0.5px;
}
.hero-subtitle {
    color: rgba(255,255,255,0.80);
    font-size: 0.95rem;
    margin: 6px 0 0 0;
    font-weight: 400;
}
.hero-badge {
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.30);
    border-radius: 24px;
    padding: 8px 18px;
    color: #FFFFFF;
    font-size: 0.80rem;
    font-weight: 500;
    backdrop-filter: blur(4px);
    white-space: nowrap;
}

/* ── Tarjeta de métricas ───────────────────────────────────────────── */
.metric-card {
    background: #FFFFFF;
    border: 1px solid #E2EBF6;
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    transition: box-shadow 0.2s ease;
}
.metric-card:hover { box-shadow: 0 4px 16px rgba(0, 98, 184, 0.12); }
.metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: #0062B8;
    line-height: 1;
}
.metric-label {
    font-size: 0.78rem;
    color: #6B7280;
    font-weight: 500;
    margin-top: 4px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* ── Contenedor del chat ───────────────────────────────────────────── */
.chat-container {
    background: #FFFFFF;
    border: 1px solid #E2EBF6;
    border-radius: 16px;
    padding: 8px 0;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    min-height: 420px;
}

/* ── Mensajes del chat ─────────────────────────────────────────────── */
[data-testid="stChatMessage"] {
    padding: 12px 20px;
    border-radius: 0;
    transition: background 0.15s ease;
}
[data-testid="stChatMessage"]:hover { background: #F8FAFF; }

/* Burbujas de usuario */
[data-testid="stChatMessage"][data-role="user"] {
    background: linear-gradient(135deg, #EBF4FF 0%, #F0F7FF 100%);
    border-left: 3px solid #0062B8;
}

/* ── Input del chat ────────────────────────────────────────────────── */
[data-testid="stChatInput"] {
    border-radius: 12px !important;
    border: 2px solid #E2EBF6 !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #0062B8 !important;
    box-shadow: 0 0 0 3px rgba(0,98,184,0.12) !important;
}

/* ── Sidebar ───────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #FFFFFF;
    border-right: 1px solid #E2EBF6;
}
[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
    color: #0062B8;
}

/* Logo sidebar */
.sidebar-logo {
    background: linear-gradient(135deg, #0062B8, #004A8F);
    border-radius: 12px;
    padding: 18px;
    text-align: center;
    margin-bottom: 8px;
    color: white;
    font-size: 1.6rem;
    font-weight: 700;
    letter-spacing: -0.5px;
}
.sidebar-logo span { font-size: 0.75rem; font-weight: 400; opacity: 0.80; display: block; }

/* Tarjeta de estado en sidebar */
.status-card {
    border-radius: 10px;
    padding: 12px 16px;
    margin: 6px 0;
    font-size: 0.85rem;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 8px;
}
.status-ok   { background: #ECFDF5; color: #065F46; border: 1px solid #A7F3D0; }
.status-warn { background: #FFFBEB; color: #92400E; border: 1px solid #FDE68A; }
.status-info { background: #EFF6FF; color: #1E40AF; border: 1px solid #BFDBFE; }

/* Botones de ejemplo */
.stButton > button {
    background: #FFFFFF;
    border: 1px solid #BFDBFE;
    color: #1E40AF;
    border-radius: 8px;
    font-size: 0.82rem;
    padding: 6px 12px;
    width: 100%;
    text-align: left;
    transition: all 0.15s ease;
    font-weight: 500;
}
.stButton > button:hover {
    background: #EFF6FF;
    border-color: #0062B8;
    color: #0062B8;
    box-shadow: 0 2px 6px rgba(0,98,184,0.15);
    transform: translateY(-1px);
}

/* Botón "Nueva sesión" — diferenciado */
.stButton > button[kind="secondary"] {
    background: linear-gradient(135deg, #0062B8, #004A8F);
    border: none;
    color: white;
}
.stButton > button[kind="secondary"]:hover {
    background: linear-gradient(135deg, #004A8F, #003470);
    color: white;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0,98,184,0.35);
}

/* ── Dividers ──────────────────────────────────────────────────────── */
hr { border-color: #E2EBF6; }

/* ── Code blocks ───────────────────────────────────────────────────── */
code {
    background: #EFF6FF;
    color: #1E40AF;
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 0.85em;
}

/* ── Spinner ───────────────────────────────────────────────────────── */
[data-testid="stSpinner"] { color: #0062B8; }

/* ── Scrollbar personalizada ───────────────────────────────────────── */
::-webkit-scrollbar       { width: 6px; }
::-webkit-scrollbar-track { background: #F4F7FB; }
::-webkit-scrollbar-thumb { background: #BFDBFE; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #0062B8; }

/* ── Footer ────────────────────────────────────────────────────────── */
.footer {
    text-align: center;
    color: #9CA3AF;
    font-size: 0.75rem;
    margin-top: 16px;
    padding: 12px 0;
    border-top: 1px solid #E2EBF6;
}

/* ── Ocultar elementos por defecto de Streamlit ────────────────────── */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Cache del agente a nivel de sesión de servidor (no recrea en cada rerun)
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def _build_agent():
    from techshop_agent import create_agent
    return create_agent()


# ---------------------------------------------------------------------------
# Estado de sesión
# ---------------------------------------------------------------------------
def _init_session() -> None:
    defaults: dict = {
        "messages": [],
        "session_id": f"streamlit-{uuid.uuid4().hex[:8]}",
        "total_queries": 0,
        "total_latency_ms": 0.0,
        "errors": 0,
        "langfuse_enabled": bool(
            os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY")
        ),
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ---------------------------------------------------------------------------
# Llamada al agente con tracing Langfuse opcional
# ---------------------------------------------------------------------------
def _call_agent(user_input: str) -> tuple[str, float]:
    """Invoca el agente y devuelve (respuesta_texto, latencia_ms)."""
    agent = _build_agent()
    start = time.monotonic()

    if st.session_state.langfuse_enabled:
        try:
            from langfuse.decorators import langfuse_context, observe

            @observe(name="streamlit_query")
            def _traced(query: str) -> str:
                langfuse_context.update_current_trace(
                    user_id="streamlit-student",
                    session_id=st.session_state.session_id,
                    metadata={"source": "streamlit_app"},
                )
                return str(agent(query))

            response = _traced(user_input)
        except Exception:
            response = str(agent(user_input))
    else:
        response = str(agent(user_input))

    latency_ms = (time.monotonic() - start) * 1000
    return response, latency_ms


# ---------------------------------------------------------------------------
# Componentes UI reutilizables
# ---------------------------------------------------------------------------
def _render_hero() -> None:
    model_short = os.getenv("MODEL_ID", "claude-haiku-4-5").split(".")[-1].split("-v")[0]
    st.markdown(
        f"""
        <div class="hero-banner">
            <div>
                <p class="hero-title">🛒 TechShop Agent</p>
                <p class="hero-subtitle">Asistente de atención al cliente · Laboratorio LLMOps</p>
            </div>
            <div class="hero-badge">✦ {model_short}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_metrics() -> None:
    queries = st.session_state.total_queries
    avg_latency = (
        st.session_state.total_latency_ms / queries if queries > 0 else 0.0
    )
    errors = st.session_state.errors

    c1, c2, c3, c4 = st.columns(4)
    for col, value, label in [
        (c1, str(queries), "Consultas"),
        (c2, f"{avg_latency:.0f} ms", "Latencia media"),
        (c3, str(len(st.session_state.messages) // 2), "Turnos"),
        (c4, str(errors), "Errores"),
    ]:
        with col:
            st.markdown(
                f"""<div class="metric-card">
                    <div class="metric-value">{value}</div>
                    <div class="metric-label">{label}</div>
                </div>""",
                unsafe_allow_html=True,
            )


def _render_sidebar() -> None:
    with st.sidebar:
        # Logo
        st.markdown(
            '<div class="sidebar-logo">TS<span>TechShop · LLMOps</span></div>',
            unsafe_allow_html=True,
        )

        # ── Sesión ──
        st.markdown("**Sesión activa**")
        st.code(st.session_state.session_id, language=None)

        if st.button("↻  Nueva sesión", type="secondary", use_container_width=True):
            for key in ("messages", "total_queries", "total_latency_ms", "errors"):
                st.session_state[key] = [] if key == "messages" else 0
            st.session_state.session_id = f"streamlit-{uuid.uuid4().hex[:8]}"
            st.rerun()

        st.divider()

        # ── Langfuse ──
        st.markdown("**Observabilidad**")
        if st.session_state.langfuse_enabled:
            host = os.getenv("LANGFUSE_HOST") or os.getenv("LANGFUSE_BASE_URL", "cloud.langfuse.com")
            st.markdown(
                f'<div class="status-card status-ok">✅ Langfuse conectado<br><small>{host}</small></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="status-card status-warn">⚠️ Langfuse no configurado</div>',
                unsafe_allow_html=True,
            )
            with st.expander("Cómo configurarlo"):
                st.code(
                    "LANGFUSE_PUBLIC_KEY=pk-...\nLANGFUSE_SECRET_KEY=sk-...\nLANGFUSE_HOST=http://localhost:3000",
                    language="bash",
                )

        st.divider()

        # ── Modelo ──
        st.markdown("**Modelo**")
        model_id = os.getenv("MODEL_ID", "us.anthropic.claude-haiku-4-5-20251001-v1:0")
        region = os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "us-east-1"))
        st.markdown(
            f'<div class="status-card status-info">🤖 {model_id.split(".")[-1]}</div>',
            unsafe_allow_html=True,
        )
        st.caption(f"Región: `{region}`")

        st.divider()

        # ── Preguntas de ejemplo ──
        st.markdown("**Preguntas de ejemplo**")
        ejemplos = [
            "¿Qué portátiles tenéis por menos de 1000€?",
            "¿Cuál es la política de devoluciones?",
            "Quiero auriculares con cancelación de ruido",
            "¿Hacéis envíos internacionales?",
            "Recomiéndame un smartphone gama alta",
            "¿Tenéis garantía extendida?",
        ]
        for ej in ejemplos:
            if st.button(ej, key=f"quick_{ej}", use_container_width=True):
                st.session_state._quick_input = ej
                st.rerun()

        # ── Footer ──
        st.markdown(
            '<div class="footer">Powered by AWS Bedrock · Strands Agents</div>',
            unsafe_allow_html=True,
        )


def _render_chat() -> None:
    """Renderiza el historial de mensajes y el input del chat."""
    # Historial
    chat_area = st.container()
    with chat_area:
        if not st.session_state.messages:
            st.markdown(
                """
                <div style="text-align:center; padding: 60px 20px; color: #9CA3AF;">
                    <div style="font-size:3rem; margin-bottom:12px">💬</div>
                    <div style="font-size:1rem; font-weight:500; color:#4B5563;">
                        Hola, soy Alex, tu asistente de TechShop
                    </div>
                    <div style="font-size:0.88rem; margin-top:6px;">
                        Pregúntame sobre productos, precios, envíos o políticas de la tienda.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
                    if msg["role"] == "assistant" and "latency_ms" in msg:
                        st.caption(f"⏱ {msg['latency_ms']:.0f} ms")

    # Input — soporta tanto escritura directa como ejemplos rápidos del sidebar
    prefill = st.session_state.pop("_quick_input", None)
    user_input = st.chat_input("Escribe tu pregunta a Alex…") or prefill

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Alex está pensando…"):
                try:
                    response, latency_ms = _call_agent(user_input)
                    st.session_state.total_queries += 1
                    st.session_state.total_latency_ms += latency_ms
                except Exception as exc:
                    response = f"Lo siento, ha ocurrido un error al procesar tu solicitud. Por favor, inténtalo de nuevo."
                    latency_ms = 0.0
                    st.session_state.errors += 1
                    st.error(f"Error interno: {exc}")

            st.markdown(response)
            st.caption(f"⏱ {latency_ms:.0f} ms")

        st.session_state.messages.append(
            {"role": "assistant", "content": response, "latency_ms": latency_ms}
        )
        st.rerun()  # Refresca métricas tras cada respuesta


# ---------------------------------------------------------------------------
# Punto de entrada principal
# ---------------------------------------------------------------------------
def main() -> None:
    _init_session()
    _render_sidebar()

    # Layout de dos columnas: chat principal (ancho) + panel de info (estrecho)
    col_main, col_info = st.columns([3, 1], gap="large")

    with col_main:
        _render_hero()
        _render_metrics()
        st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
        _render_chat()
        st.markdown("</div>", unsafe_allow_html=True)

    with col_info:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 💡 Sobre este lab")
        st.info(
            "Este agente tiene **4 fallos deliberados** (F1–F4) que descubrirás "
            "durante el curso LLMOps.\n\n"
            "Usa las trazas de Langfuse para detectarlos."
        )

        st.markdown("#### 🔧 Stack técnico")
        stack = {
            "🤖 LLM": "AWS Bedrock",
            "⚙️ Framework": "Strands Agents",
            "📊 Tracing": "Langfuse",
            "🛡️ Safety": "LLM Guard",
            "🧱 Infra": "Terraform / EC2",
        }
        for icon_label, value in stack.items():
            st.markdown(
                f'<div class="status-card status-info" style="justify-content:space-between;">'
                f'<span>{icon_label}</span><strong>{value}</strong></div>',
                unsafe_allow_html=True,
            )

        st.markdown("#### 📚 Módulos del curso")
        modulos = [
            ("M1", "Setup & Agentes"),
            ("M2", "Observabilidad"),
            ("M3", "Prompt Mgmt"),
            ("M4", "Evaluación"),
            ("M5", "Guardrails"),
            ("M6", "CI/CD"),
        ]
        for code, name in modulos:
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:8px;padding:5px 0;">'
                f'<span style="background:#0062B8;color:white;border-radius:4px;'
                f'padding:2px 7px;font-size:0.72rem;font-weight:600;">{code}</span>'
                f'<span style="font-size:0.85rem;color:#374151;">{name}</span></div>',
                unsafe_allow_html=True,
            )


if __name__ == "__main__":
    main()
