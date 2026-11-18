"""
PRESSURE-X AI Scouting Lab — Streamlit Dashboard Page
Integrates Backboard API (Google Gemini) into the interactive scouting assistant.
"""

import streamlit as st
import pandas as pd
from typing import Optional
from src.ai.backboard_scouting_assistant import BackboardScoutingAssistant
from dashboard.utils.formatting import RR_PINK, RR_GOLD, RR_ROYAL_BLUE

# ── Singleton assistant (cached per session) ─────────────────────────────────

@st.cache_resource
def get_assistant() -> BackboardScoutingAssistant:
    return BackboardScoutingAssistant()


# ── UI helpers ───────────────────────────────────────────────────────────────

def _status_badge(configured: bool) -> str:
    if configured:
        return "🟢 **Backboard AI Active** (Google Gemini)"
    return "🔴 **AI Offline** — Deterministic fallback enabled"


def _render_player_card(rec: dict, rank: int) -> None:
    """Render a recommended player card inside the AI page."""
    nat_icon = "🇮🇳" if rec.get("nationality") == "Indian" else "🌐"
    score = rec.get("verified_rr_scouting_score", 0.0)
    p_score = rec.get("pressure_or_eq_score", 0.0)
    age = rec.get("age_as_of_2027_04_01", 0.0)
    category = rec.get("development_category", "")

    card_html = f"""
<div style="background:#1C2541;border:1px solid rgba(234,27,134,0.3);border-radius:8px;padding:14px 18px;margin-bottom:12px;">
<div style="font-size:1.05rem;font-weight:800;color:#FFFFFF;">
#{rank} {nat_icon} {rec.get("player_name")}
<span style="font-size:0.8rem;color:#94A3B8;font-weight:400;">
&nbsp;{rec.get("country","")} · {rec.get("role","")} · Age {age:.1f}
</span>
</div>
<div style="font-size:0.78rem;color:#94A3B8;margin:4px 0 8px 0;">{category}</div>
<div style="display:flex;gap:24px;margin-bottom:10px;">
<div>
<span style="font-size:0.7rem;color:#94A3B8;">RR Scouting Score</span><br>
<span style="font-size:1.3rem;font-weight:800;color:#EA1B86;">{score:.2f}</span>
</div>
<div>
<span style="font-size:0.7rem;color:#94A3B8;">Pressure / EQ Score</span><br>
<span style="font-size:1.3rem;font-weight:800;color:#004BA0;">{p_score:.2f}</span>
</div>
<div>
<span style="font-size:0.7rem;color:#94A3B8;">Form</span><br>
<span style="font-size:0.9rem;font-weight:600;color:#F59E0B;">{rec.get("current_form_rating","")}</span>
</div>
</div>
<div style="font-size:0.82rem;color:#E2E8F0;margin-bottom:6px;">
<b style="color:#10B981;">Tactical Fit:</b> {rec.get("tactical_role_fit","")}
</div>
<div style="font-size:0.82rem;color:#CBD5E1;margin-bottom:4px;">
<b style="color:#FFFFFF;">Suitability:</b> {rec.get("suitability_explanation","")}
</div>
<div style="font-size:0.78rem;color:#F59E0B;">
⚠️ <b>Risk:</b> {rec.get("risk_assessment","")}
</div>
</div>
"""
    clean_html = "\n".join(line.strip() for line in card_html.splitlines() if line.strip())
    st.markdown(clean_html, unsafe_allow_html=True)


# ── Main render function (called from app.py) ────────────────────────────────

def render_ai_scouting_lab(all_players_df: pd.DataFrame) -> None:
    """
    Renders the full AI Scouting Lab page.
    Expects a combined dataframe with columns from get_all_shortlist_players().
    """
    assistant = get_assistant()

    # ── Header ──────────────────────────────────────────────────────────────
    st.markdown("""
        <div style="background:linear-gradient(135deg,#0B132B 60%,#2a0a1a);
                    border:1px solid rgba(234,27,134,0.4);border-radius:10px;
                    padding:22px 28px;margin-bottom:24px;">
            <div style="font-size:1.6rem;font-weight:800;color:#FFFFFF;">
                🤖 PRESSURE-X AI Scouting Lab
                <span style="font-size:0.9rem;font-weight:400;color:#94A3B8;"> — Powered by Backboard × Google Gemini</span>
            </div>
            <div style="font-size:0.85rem;color:#94A3B8;margin-top:6px;">
                Natural-language scouting queries with persistent multi-turn conversation memory.
                All recommendations are verified against empirical PRESSURE-X evidence.
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ── Status banner ────────────────────────────────────────────────────────
    is_on = assistant.is_configured
    if is_on:
        st.success(_status_badge(is_on))
        col_model, col_key = st.columns(2)
        with col_model:
            import re as _re
            # Read the stored model name — do NOT call verify_and_select_gemini_model()
            # here as it triggers a live API call every render and may return a Model object
            # on certain SDK versions. The model is already resolved during first query.
            raw_name = str(assistant.model_name or assistant.DEFAULT_MODEL)
            # Safety extract: if the string looks like a repr (contains 'description=')
            # pull out the actual gemini-* identifier with regex
            if "gemini" not in raw_name.lower():
                _m = _re.search(r"gemini[-\w.]+", raw_name, _re.IGNORECASE)
                raw_name = _m.group(0) if _m else assistant.DEFAULT_MODEL
            st.caption(f"**Provider:** `{assistant.provider}`  |  **Model:** `{raw_name}`  |  **API Key:** `{assistant.masked_api_key}`")
    else:
        st.warning(_status_badge(is_on))
        st.info(
            "**Configure Backboard API key to activate Google Gemini AI features.**\n\n"
            "Add your key to `.streamlit/secrets.toml`:\n"
            "```toml\nBACKBOARD_API_KEY = \"your_key_here\"\n```\n"
            "Or set the environment variable `BACKBOARD_API_KEY`. "
            "Get your key at https://app.backboard.io/dashboard/api-keys\n\n"
            "Dashboard filters, rankings and visualizations remain fully available without an API key.",
            icon="🔑"
        )

    st.markdown("---")

    # ── Session state init ───────────────────────────────────────────────────
    if "scout_thread_id" not in st.session_state:
        st.session_state.scout_thread_id = None
    if "scout_history" not in st.session_state:
        st.session_state.scout_history = []
    if "scout_result" not in st.session_state:
        st.session_state.scout_result = None

    # ── Filters sidebar panel ────────────────────────────────────────────────
    with st.expander("🎯 Candidate Pool Filters", expanded=True):
        fc0, fc1, fc2, fc3, fc4 = st.columns([1.5, 1, 1, 1.2, 1])
        with fc0:
            pool_scope = st.selectbox(
                "Search Scope",
                ["Complete Auction Dataset (303 Players)", "Final Shortlist Only (28 Players)"],
                key="ai_pool_scope"
            )

        active_pool_df = all_players_df.copy()
        if "Shortlist" in pool_scope and 'is_shortlisted' in active_pool_df.columns:
            active_pool_df = active_pool_df[active_pool_df['is_shortlisted'] == True]

        with fc1:
            role_filter = st.selectbox(
                "Role",
                ["All", "Batter", "Bowler"],
                key="ai_role_filter"
            )
        with fc2:
            nat_filter = st.selectbox(
                "Nationality",
                ["All", "Indian", "Overseas"],
                key="ai_nat_filter"
            )
        with fc3:
            cat_opts = ["All"] + sorted(all_players_df['development_category'].dropna().unique().tolist())
            cat_filter = st.selectbox("Development Stage", cat_opts, key="ai_cat_filter")
        with fc4:
            max_age = st.number_input(
                "Max Age (Apr 2027)",
                min_value=18.0, max_value=45.0, value=35.0, step=0.5,
                key="ai_max_age"
            )

        # Show eligible pool count
        try:
            preview_df = assistant.filter_eligible_candidates(
                active_pool_df,
                role=None if role_filter == "All" else role_filter,
                nationality=None if nat_filter == "All" else nat_filter,
                development_category=None if cat_filter == "All" else cat_filter,
                max_age=max_age
            )
            st.caption(f"🔍 **{len(preview_df)} eligible candidates** in active search scope matching filters.")
        except Exception:
            pass

    # ── Query input ──────────────────────────────────────────────────────────
    st.markdown("### 💬 Scouting Query")

    example_queries = [
        "Recommend 3 young Indian batters under 24 with high pressure scores for top-order development.",
        "Find the best overseas all-rounders with strong death-bowling evidence and emerging potential.",
        "Who are the highest-ceiling spinners available that fit RR's development philosophy?",
        "Compare our top two emerging batter candidates on pressure performance and skill ceiling.",
    ]
    selected_example = st.selectbox(
        "Quick-start examples (or type your own below):",
        ["— Type your own query —"] + example_queries,
        key="ai_example_query"
    )

    default_query = selected_example if selected_example != "— Type your own query —" else ""
    user_query = st.text_area(
        "Enter your scouting query:",
        value=default_query,
        height=100,
        placeholder="e.g., 'Find 3 emerging Indian spinners with strong pressure execution and development runway'",
        key="ai_user_query"
    )

    # ── Conversation controls ────────────────────────────────────────────────
    cc1, cc2, cc3 = st.columns([2, 1, 1])
    with cc1:
        run_btn = st.button(
            "🚀 Generate Scouting Recommendations",
            type="primary",
            use_container_width=True,
            disabled=not user_query.strip()
        )
    with cc2:
        continue_btn = st.button(
            "🔁 Continue Thread",
            use_container_width=True,
            disabled=not (user_query.strip() and st.session_state.scout_thread_id),
            help="Continue the existing AI conversation (preserves memory context)."
        )
    with cc3:
        reset_btn = st.button(
            "🗑️ New Session",
            use_container_width=True,
            help="Start a new scouting conversation (clears memory context)."
        )

    if reset_btn:
        st.session_state.scout_thread_id = None
        st.session_state.scout_history = []
        st.session_state.scout_result = None
        st.rerun()

    # ── Execute query ────────────────────────────────────────────────────────
    trigger = run_btn or continue_btn
    if trigger and user_query.strip():
        thread_id = st.session_state.scout_thread_id if continue_btn else None

        with st.spinner("🤖 Querying Backboard AI with Google Gemini..."):
            result = assistant.query_scouting_assistant(
                user_query=user_query.strip(),
                candidates_df=active_pool_df,
                thread_id=thread_id,
                role_filter=None if role_filter == "All" else role_filter,
                nationality_filter=None if nat_filter == "All" else nat_filter,
                category_filter=None if cat_filter == "All" else cat_filter,
                max_age_filter=max_age
            )

        st.session_state.scout_result = result
        if result.get("thread_id"):
            st.session_state.scout_thread_id = result["thread_id"]
        st.session_state.scout_history.append({
            "query": user_query.strip(),
            "source": result.get("source", "unknown"),
            "count": len(result.get("recommended_players", []))
        })

    # ── Render results ───────────────────────────────────────────────────────
    result = st.session_state.scout_result
    if result:
        st.markdown("---")

        # Source badge
        source = result.get("source", "unknown")
        if source == "backboard_google_gemini":
            st.success(f"✅ Recommendations from **Backboard × Google Gemini** | Model: `{result.get('model','unknown')}` | Thread: `{result.get('thread_id','')[:12]}...`")
        elif source == "deterministic_fallback":
            st.info(f"🔄 **Deterministic Fallback Active** — {result.get('fallback_notice','')}")
        elif source == "validation_gate":
            st.error("❌ No eligible candidates match your filter criteria. Relax filters and try again.")

        if not result.get("success"):
            st.error(f"⚠️ Error: {result.get('error', 'Unknown error')}")
        else:
            # Analysis summary
            st.markdown("### 📋 Strategic Analysis")
            st.markdown(
                f"<div style='background:#0F1C38;border-left:3px solid #EA1B86;padding:14px 18px;"
                f"border-radius:0 8px 8px 0;font-size:0.9rem;color:#E2E8F0;'>"
                f"{result.get('analysis_summary','')}</div>",
                unsafe_allow_html=True
            )

            # Player recommendations
            recs = result.get("recommended_players", [])
            if recs:
                st.markdown(f"### 👥 Recommended Players ({len(recs)} candidates)")
                for i, rec in enumerate(recs, 1):
                    _render_player_card(rec, i)

            # Squad balance
            balance_note = result.get("squad_balance_note", "")
            if balance_note:
                st.markdown("### ⚖️ Squad Balance Assessment")
                st.info(balance_note)

            # Memory acknowledgement
            mem_note = result.get("memory_context_acknowledged", "")
            if mem_note and source == "backboard_google_gemini":
                with st.expander("🧠 Persistent Memory Context"):
                    st.caption(mem_note)

        # Thread info
        if st.session_state.scout_thread_id and source == "backboard_google_gemini":
            st.caption(f"🔗 Active Thread ID: `{st.session_state.scout_thread_id}` — Use 'Continue Thread' to extend this conversation.")

    # ── Conversation history ─────────────────────────────────────────────────
    if st.session_state.scout_history:
        st.markdown("---")
        with st.expander("📜 Session Query History"):
            for i, entry in enumerate(reversed(st.session_state.scout_history), 1):
                src_icon = "🤖" if "gemini" in entry["source"] else "⚙️"
                st.markdown(
                    f"**{i}.** {src_icon} `{entry['source']}` → "
                    f"**{entry['count']} players** · _{entry['query'][:80]}{'...' if len(entry['query']) > 80 else ''}_"
                )

