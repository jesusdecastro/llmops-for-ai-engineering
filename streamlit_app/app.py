"""TechShop Agent — interfaz Streamlit con ciclo LLMOps integrado."""

from __future__ import annotations

import contextlib
import io
import os
import time
import uuid

from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from app_config import (
    AGENT_ICON,
    AGENT_NAME,
    AGENT_SUBTITLE,
    ENVIRONMENTS,
    EXAMPLES,
    PAGE_ICON,
    PAGE_LAYOUT,
    PAGE_TITLE,
    TRACING_SOURCE,
    TRACING_USER_ID,
)

# .env está en la raíz del repo, no en streamlit_app/
_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_ENV_FILE, override=True)

if os.getenv("AWS_ACCESS_KEY_ID"):
    os.environ.pop("AWS_PROFILE", None)

# ---------------------------------------------------------------------------
# Página
# ---------------------------------------------------------------------------
st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide")

_CSS = """
<style>
#MainMenu, footer, header { visibility: hidden; }
.latency { font-size: 0.72rem; color: #9CA3AF; }
.scores { font-size: 0.72rem; color: #6B7280; margin-top: 2px; }
.score-good { color: #10B981; }
.score-warn { color: #F59E0B; }
.score-bad { color: #EF4444; }
.eval-pass { background: #D1FAE5; padding: 12px; border-radius: 8px; border-left: 4px solid #10B981; }
.eval-fail { background: #FEE2E2; padding: 12px; border-radius: 8px; border-left: 4px solid #EF4444; }
</style>
"""
st.markdown(_CSS, unsafe_allow_html=True)

# Nombres legibles para los scores
_SCORE_LABELS: dict[str, str] = {
    "response_quality": "Calidad",
    "scope_adherence": "Ámbito",
}


def _render_scores_html(scores: dict[str, float]) -> str:
    if not scores:
        return ""
    parts = []
    for name, value in scores.items():
        label = _SCORE_LABELS.get(name, name)
        css_class = "score-good" if value >= 0.8 else ("score-warn" if value >= 0.5 else "score-bad")
        parts.append(f'<span class="{css_class}">{label}: {value:.0%}</span>')
    return f'<span class="scores">📊 {" · ".join(parts)}</span>'


# ---------------------------------------------------------------------------
# Agentes (cacheados a nivel de servidor)
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def _build_base_agent() -> object:
    from techshop_agent import create_agent
    return create_agent()


@st.cache_resource(show_spinner=False)
def _build_instrumented_agent() -> object:
    from techshop_agent.solution.observability import create_observed_agent
    return create_observed_agent()


# ---------------------------------------------------------------------------
# Estado de sesión
# ---------------------------------------------------------------------------
def _init_session() -> None:
    defaults: dict = {
        "messages": [],
        "session_id": f"streamlit-{uuid.uuid4().hex[:8]}",
        "agent_mode": "base",
        "prompt_env": "🟢 Production",
        "langfuse_enabled": bool(
            os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY")
        ),
        "eval_result": None,
        "eval_running": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ---------------------------------------------------------------------------
# Llamada al agente
# ---------------------------------------------------------------------------
def _call_agent(user_input: str) -> tuple[str, float, dict[str, float]]:
    start = time.monotonic()
    mode: str = st.session_state.agent_mode
    scores: dict[str, float] = {}

    if mode == "instrumented":
        try:
            prompt_label = ENVIRONMENTS.get(st.session_state.prompt_env, "production")
            from techshop_agent.solution.prompt_provider import process_query_with_prompt

            with contextlib.redirect_stdout(io.StringIO()):
                response, scores = process_query_with_prompt(
                    user_input,
                    prompt_label=prompt_label,
                    user_id=TRACING_USER_ID,
                    session_id=st.session_state.session_id,
                    source=TRACING_SOURCE,
                )
        except ImportError:
            from techshop_agent.solution.observability import process_query

            with contextlib.redirect_stdout(io.StringIO()):
                response = process_query(
                    user_input,
                    user_id=TRACING_USER_ID,
                    session_id=st.session_state.session_id,
                    source=TRACING_SOURCE,
                )
        except Exception as exc:
            response = f"Error: {type(exc).__name__} — {exc}"
    else:
        agent = _build_base_agent()

        if st.session_state.langfuse_enabled:
            try:
                from langfuse.decorators import langfuse_context, observe

                @observe(name="streamlit_query")
                def _traced(query: str) -> str:
                    langfuse_context.update_current_trace(
                        user_id=TRACING_USER_ID,
                        session_id=st.session_state.session_id,
                        metadata={"source": TRACING_SOURCE, "mode": "base"},
                    )
                    with contextlib.redirect_stdout(io.StringIO()):
                        return str(agent(query))

                response = _traced(user_input)
            except Exception:
                response = str(agent(user_input))
        else:
            with contextlib.redirect_stdout(io.StringIO()):
                response = str(agent(user_input))

    latency_ms = (time.monotonic() - start) * 1000
    return response, latency_ms, scores


# ---------------------------------------------------------------------------
# Diálogo para ver el prompt activo
# ---------------------------------------------------------------------------
@st.dialog("Prompt activo", width="large")
def _show_prompt_dialog(label: str) -> None:
    try:
        from techshop_agent.solution.prompt_provider import get_prompt_client

        pc = get_prompt_client(label=label, cache_ttl_seconds=0)
        if pc.is_fallback:
            st.warning("Se está usando el prompt **fallback local** (Langfuse no disponible).")
        else:
            st.info(f"**Label:** `{label}` — **Versión:** v{pc.version}")
        st.code(pc.compile(), language="markdown")
    except Exception as exc:
        st.error(f"No se pudo obtener el prompt: {exc}")
        from techshop_agent.solution.prompt_provider import FALLBACK_PROMPT

        st.caption("Mostrando fallback local:")
        st.code(FALLBACK_PROMPT, language="markdown")


# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR — Siempre visible: sesión, modo, prompt management
# ═══════════════════════════════════════════════════════════════════════════
def _render_sidebar() -> None:
    with st.sidebar:
        col_session, col_btn = st.columns([3, 1])
        with col_session:
            st.caption(f"Sesión `{st.session_state.session_id}`")
        with col_btn:
            if st.button("↻", help="Nueva sesión", key="_new_session"):
                st.session_state.messages = []
                st.session_state.session_id = f"streamlit-{uuid.uuid4().hex[:8]}"
                st.rerun()

        with st.expander("⚙️ Modo del agente", expanded=True):
            new_mode = st.radio(
                label="Selecciona modo:",
                options=["base", "instrumented"],
                format_func=lambda x: (
                    "🤖 Base (sin tracing)" if x == "base" else "📊 Instrumentado (Langfuse)"
                ),
                index=0 if st.session_state.agent_mode == "base" else 1,
                key="_mode_radio",
                label_visibility="collapsed",
            )
            if new_mode != st.session_state.agent_mode:
                st.session_state.agent_mode = new_mode
                st.session_state.messages = []
                st.session_state.session_id = f"streamlit-{uuid.uuid4().hex[:8]}"
                st.rerun()

            if st.session_state.agent_mode == "instrumented":
                if st.session_state.langfuse_enabled:
                    st.success("Langfuse conectado", icon="📊")
                else:
                    st.warning("Langfuse no configurado", icon="⚠️")
            else:
                st.caption("Sin tracing. Cambia a Instrumentado.")

        if st.session_state.agent_mode == "instrumented":
            with st.expander("🏷️ Prompt Management", expanded=True):
                env_names = list(ENVIRONMENTS.keys())
                current_idx = (
                    env_names.index(st.session_state.prompt_env)
                    if st.session_state.prompt_env in env_names
                    else 0
                )
                selected_env = st.radio(
                    label="Selecciona entorno:",
                    options=env_names,
                    index=current_idx,
                    key="_env_radio",
                    label_visibility="collapsed",
                )

                selected_label = ENVIRONMENTS[selected_env]
                active_label = ENVIRONMENTS[st.session_state.prompt_env]

                _prompt_available = False
                _prompt_version: int | None = None
                _check_error: str | None = None

                if st.session_state.langfuse_enabled:
                    try:
                        from techshop_agent.solution.prompt_provider import get_prompt_client

                        _pc = get_prompt_client(label=selected_label, cache_ttl_seconds=0)
                        if not _pc.is_fallback:
                            _prompt_available = True
                            _prompt_version = _pc.version
                        else:
                            _check_error = "fallback"
                    except Exception as exc:
                        _check_error = str(exc)

                if _prompt_available:
                    st.caption(f"✅ `{selected_label}` — v{_prompt_version}")
                elif _check_error == "fallback":
                    st.error(
                        f"❌ **No existe** prompt con label `{selected_label}` en Langfuse.\n\n"
                        "Se usará el fallback local.",
                        icon="🚫",
                    )
                elif _check_error:
                    st.error(f"❌ Error: `{_check_error}`", icon="🚫")
                elif not st.session_state.langfuse_enabled:
                    st.warning("Langfuse no configurado.", icon="⚠️")

                if selected_env != st.session_state.prompt_env:
                    st.caption(f"Label activa: `{active_label}` → `{selected_label}`")
                    if st.button(
                        f"🔄 Aplicar cambio a {selected_env}",
                        use_container_width=True,
                        type="primary",
                    ):
                        st.session_state.prompt_env = selected_env
                        st.session_state.messages = []
                        st.session_state.session_id = f"streamlit-{uuid.uuid4().hex[:8]}"
                        st.rerun()
                    st.caption("Cambiar label reinicia la conversación.")

                if st.button("👁 Ver prompt activo", use_container_width=True):
                    _show_prompt_dialog(active_label)

                st.divider()
                st.caption("🔍 **Debug**: última versión creada")
                if st.button("🏷️ Ver prompt `latest`", use_container_width=True):
                    _show_prompt_dialog("latest")

        with st.expander("💬 Ejemplos", expanded=False):
            for ej in EXAMPLES:
                if st.button(ej, key=f"ex_{ej}", use_container_width=True):
                    st.session_state._quick = ej
                    st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
# TAB 1: Chat
# ═══════════════════════════════════════════════════════════════════════════
def _tab_chat() -> None:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                meta_parts = []
                if "latency_ms" in msg:
                    meta_parts.append(f'{msg["latency_ms"]:.0f} ms')
                scores_html = _render_scores_html(msg.get("scores", {}))
                if meta_parts or scores_html:
                    html = f'<span class="latency">{" · ".join(meta_parts)}</span>'
                    if scores_html:
                        html += f" {scores_html}"
                    st.markdown(html, unsafe_allow_html=True)

    prefill = st.session_state.pop("_quick", None)
    user_input = st.chat_input("Escribe tu pregunta…") or prefill

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner(""):
                try:
                    response, latency_ms, scores = _call_agent(user_input)
                except Exception as exc:
                    response = f"Error: {type(exc).__name__} — {exc}"
                    latency_ms = 0.0
                    scores = {}
                    st.error(response)

            st.markdown(response)
            meta_html = f'<span class="latency">{latency_ms:.0f} ms</span>'
            scores_html = _render_scores_html(scores)
            if scores_html:
                meta_html += f" {scores_html}"
            st.markdown(meta_html, unsafe_allow_html=True)

        st.session_state.messages.append(
            {"role": "assistant", "content": response, "latency_ms": latency_ms, "scores": scores}
        )
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
# TAB 2: Evaluation
# ═══════════════════════════════════════════════════════════════════════════
def _tab_evaluation() -> None:
    st.subheader("🧪 Quality Gate — Evaluación de Prompt")
    st.caption(
        "Ejecuta la suite de evaluación completa contra una label de Langfuse. "
        "Incluye evaluadores deterministas (scope, hallucination, tool usage, quality) "
        "y LLM-as-Judge (faithfulness). Los resultados se registran como experimento en Langfuse."
    )

    col_label, col_threshold = st.columns([2, 1])
    with col_label:
        eval_label = st.selectbox(
            "Label a evaluar",
            options=["staging", "production", "development", "latest"],
            index=0,
            key="_eval_label",
        )
    with col_threshold:
        eval_threshold = st.slider(
            "Threshold",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.05,
            key="_eval_threshold",
            help="Score mínimo para pasar el quality gate",
        )

    can_run = st.session_state.langfuse_enabled and not st.session_state.eval_running

    if st.button(
        "▶️ Ejecutar evaluación",
        use_container_width=True,
        type="primary",
        disabled=not can_run,
    ):
        st.session_state.eval_running = True
        st.session_state.eval_result = None

        with st.status(f"Evaluando label `{eval_label}`…", expanded=True) as status:
            try:
                st.write(f"📥 Fetching prompt `{eval_label}` desde Langfuse…")
                from techshop_agent.evaluation import run_evaluation

                # Capture stdout (the runner prints progress)
                output_buf = io.StringIO()
                with contextlib.redirect_stdout(output_buf):
                    result = run_evaluation(
                        label=eval_label, threshold=eval_threshold,
                    )

                st.session_state.eval_result = result
                progress_text = output_buf.getvalue()
                if progress_text:
                    st.code(progress_text, language="text")

                if result.passes_threshold(eval_threshold):
                    status.update(label="✅ Quality Gate PASSED", state="complete")
                else:
                    status.update(label="❌ Quality Gate FAILED", state="error")
            except Exception as exc:
                st.error(f"Error ejecutando evaluación: {exc}")
                status.update(label="💥 Error", state="error")
            finally:
                st.session_state.eval_running = False

    if not st.session_state.langfuse_enabled:
        st.warning("Langfuse no configurado. Define LANGFUSE_PUBLIC_KEY y LANGFUSE_SECRET_KEY en .env.", icon="⚠️")

    # ── Mostrar resultados ──────────────────────────────────────────────
    result = st.session_state.eval_result
    if result is not None:
        st.divider()

        passed = result.passes_threshold(eval_threshold if "eval_threshold" in dir() else 0.7)
        css_class = "eval-pass" if passed else "eval-fail"
        verdict = "✅ PASS" if passed else "❌ FAIL"

        st.markdown(
            f'<div class="{css_class}">'
            f"<strong>Quality Gate: {verdict}</strong> — "
            f"Label: <code>{result.label}</code> · "
            f"Casos: {result.total_cases} · "
            f"Aprobados: {result.passed_cases}/{result.total_cases} · "
            f"Duración: {result.duration_seconds:.1f}s"
            f"</div>",
            unsafe_allow_html=True,
        )

        st.markdown("#### Scores por evaluador")
        score_data = {
            "Evaluador": [],
            "Score": [],
            "Status": [],
        }
        for name, value in [
            ("Scope Adherence", result.avg_scope_adherence),
            ("Hallucination Check", result.avg_hallucination),
            ("Response Quality", result.avg_response_quality),
            ("Tool Usage", result.avg_tool_usage),
            ("Faithfulness (LLM Judge)", result.avg_faithfulness),
        ]:
            if value is not None:
                score_data["Evaluador"].append(name)
                score_data["Score"].append(f"{value:.1%}")
                score_data["Status"].append("✅" if value >= 0.7 else "❌")

        if score_data["Evaluador"]:
            st.dataframe(score_data, use_container_width=True, hide_index=True)

        with st.expander("📋 Resumen completo (texto)", expanded=False):
            st.code(result.summary(), language="text")


# ═══════════════════════════════════════════════════════════════════════════
# TAB 3: Prompt CI/CD
# ═══════════════════════════════════════════════════════════════════════════
def _tab_cicd() -> None:
    st.subheader("🚀 Prompt CI/CD")
    st.caption(
        "Sube nuevas versiones de prompt a Langfuse y promueve entre entornos. "
        "Esto replica el flujo que haría un pipeline de CI/CD automatizado."
    )

    cicd_push, cicd_promote = st.tabs(["📤 Push Prompt", "🔄 Promote Prompt"])

    # ── Push Prompt ─────────────────────────────────────────────────────
    with cicd_push:
        st.markdown("#### Subir nueva versión de prompt a Langfuse")
        st.caption(
            "Crea una nueva versión inmutable del prompt con las labels que selecciones. "
            "Equivale a ejecutar `python -m techshop_agent.cicd.push_prompt`."
        )

        # Load current prompt file as default
        _prompt_file = Path(__file__).resolve().parent.parent / "prompts" / "system_prompt.txt"
        _default_content = ""
        if _prompt_file.exists():
            _default_content = _prompt_file.read_text(encoding="utf-8")

        push_content = st.text_area(
            "Contenido del prompt",
            value=_default_content,
            height=300,
            key="_push_content",
            help="Puedes pegar cualquier prompt aquí. Por defecto se carga prompts/system_prompt.txt",
        )

        push_col1, push_col2 = st.columns([2, 1])
        with push_col1:
            push_labels = st.multiselect(
                "Labels",
                options=["staging", "production", "development", "latest"],
                default=["staging"],
                key="_push_labels",
                help="Labels de Langfuse para esta versión",
            )
        with push_col2:
            push_author = st.text_input(
                "Autor",
                value="streamlit-student",
                key="_push_author",
            )

        if st.button(
            "📤 Push Prompt",
            use_container_width=True,
            type="primary",
            disabled=not (push_content and push_labels and st.session_state.langfuse_enabled),
        ):
            try:
                from techshop_agent.cicd.push_prompt import push_prompt

                result = push_prompt(
                    content=push_content,
                    labels=push_labels,
                    config={"author": push_author, "source": "streamlit_app"},
                )
                st.success(
                    f"✅ Prompt creado — Labels: {result['labels']} · "
                    f"Longitud: {result['content_length']} chars",
                    icon="🎉",
                )
            except Exception as exc:
                st.error(f"Error: {exc}")

        if not st.session_state.langfuse_enabled:
            st.warning("Langfuse no configurado.", icon="⚠️")

    # ── Promote Prompt ──────────────────────────────────────────────────
    with cicd_promote:
        st.markdown("#### Promover prompt entre entornos")
        st.caption(
            "Copia el contenido de una label a otra. Esto es el equivalente a "
            "mover la label en la UI de Langfuse o ejecutar `python -m techshop_agent.cicd.promote_prompt`."
        )

        prom_col1, prom_col2 = st.columns(2)
        with prom_col1:
            from_label = st.selectbox(
                "Desde label",
                options=["staging", "production", "development", "latest"],
                index=0,
                key="_prom_from",
            )
        with prom_col2:
            to_label = st.selectbox(
                "Hacia label",
                options=["production", "staging", "development"],
                index=0,
                key="_prom_to",
            )

        # Preview what we're promoting
        if st.session_state.langfuse_enabled and from_label:
            with st.expander(f"👁 Preview: contenido de `{from_label}`", expanded=False):
                try:
                    from techshop_agent.solution.prompt_provider import get_prompt_client

                    pc = get_prompt_client(label=from_label, cache_ttl_seconds=0)
                    if pc.is_fallback:
                        st.warning(f"No hay prompt con label `{from_label}`.")
                    else:
                        st.caption(f"Versión: v{pc.version}")
                        st.code(pc.compile(), language="markdown")
                except Exception as exc:
                    st.error(str(exc))

        if from_label == to_label:
            st.warning("Las labels de origen y destino deben ser diferentes.")

        if st.button(
            f"🚀 Promover `{from_label}` → `{to_label}`",
            use_container_width=True,
            type="primary",
            disabled=not (
                st.session_state.langfuse_enabled and from_label != to_label
            ),
        ):
            try:
                from techshop_agent.cicd.promote_prompt import promote_prompt

                result = promote_prompt(from_label=from_label, to_label=to_label)
                st.success(
                    f"✅ Prompt promovido: `{result['from_label']}` (v{result['source_version']}) "
                    f"→ `{result['to_label']}`",
                    icon="🚀",
                )
                st.balloons()
            except Exception as exc:
                st.error(f"Error: {exc}")


# ═══════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════
def main() -> None:
    _init_session()

    st.title(f"{AGENT_ICON} {AGENT_NAME}")
    st.caption(AGENT_SUBTITLE)

    _render_sidebar()

    tab_chat, tab_eval, tab_cicd = st.tabs([
        "💬 Chat",
        "🧪 Evaluación",
        "🚀 Prompt CI/CD",
    ])

    with tab_chat:
        _tab_chat()

    with tab_eval:
        _tab_evaluation()

    with tab_cicd:
        _tab_cicd()


if __name__ == "__main__":
    main()
