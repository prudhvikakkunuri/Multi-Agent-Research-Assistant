import streamlit as st
import time
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain


# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResearchMind · AI Research Agent",
    page_icon="●",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@500;600;700;800&family=Sora:wght@600;700;800&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ── Tokens ──
   graphite-950  #0B0D10   page background
   graphite-900  #15181D   card / surface
   graphite-800  #1E2229   inset / hover
   line-700      #2B3038   hairline border
   ink-100       #E7E9EC   primary text
   ink-500       #8A93A3   secondary text
   indigo-500    #6C7BFF   brand / primary action
   amber-500     #E8A33D   running state
   green-500     #4CAF7D   done / success state
*/

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: #E7E9EC;
}

.stApp { background: #0B0D10; }

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 3rem 4rem; max-width: 1180px; }

/* ── Top status strip ── */
.topbar {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    padding-bottom: 1rem;
    margin-bottom: 0.5rem;
}
.status-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.06em;
    color: #4CAF7D;
    background: rgba(76,175,125,0.08);
    border: 1px solid rgba(76,175,125,0.3);
    border-radius: 20px;
    padding: 0.28rem 0.75rem;
}
.status-chip::before {
    content: '';
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #4CAF7D;
}

/* ── Centered hero title ── */
.hero-center {
    text-align: center;
    padding: 1rem 0 2.4rem;
}
.wordmark-big {
    font-family: 'Sora', sans-serif;
    font-weight: 700;
    font-size: clamp(2.6rem, 5.5vw, 4.2rem);
    letter-spacing: -0.02em;
    color: #E7E9EC;
    margin-bottom: 1.1rem;
}
.hero-tagline {
    font-family: 'Inter', sans-serif;
    font-weight: 300;
    font-size: 1.05rem;
    line-height: 1.7;
    color: #8A93A3;
    text-align: center !important;
    max-width: 620px;
    margin: 0 auto !important;
}

/* ── Section heading ── */
.section-title {
    font-family: 'Manrope', sans-serif;
    font-weight: 700;
    font-size: 0.78rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #8A93A3;
    margin: 2rem 0 0.9rem;
}

/* ── New run card ── */
.card {
    background: #15181D;
    border: 1px solid #2B3038;
    border-radius: 10px;
    padding: 1.5rem 1.7rem;
    margin-bottom: 1rem;
}

.stTextInput > div > div > input {
    background: #1E2229 !important;
    border: 1px solid #2B3038 !important;
    border-radius: 7px !important;
    color: #E7E9EC !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
    padding: 0.7rem 0.9rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: #6C7BFF !important;
    box-shadow: 0 0 0 3px rgba(108,123,255,0.15) !important;
}
.stTextInput > label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: #8A93A3 !important;
    font-weight: 500 !important;
}

.stButton > button {
    background: #6C7BFF !important;
    color: #0B0D10 !important;
    font-family: 'Manrope', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    border: none !important;
    border-radius: 7px !important;
    padding: 0.7rem 1.6rem !important;
    cursor: pointer !important;
    transition: filter 0.15s !important;
    width: 100%;
    margin-top: 0.3rem;
}
.stButton > button:hover { filter: brightness(1.12) !important; }
.stButton > button:active { filter: brightness(0.95) !important; }

/* ── Pipeline run rows (CI-style) ── */
.run-table {
    background: #15181D;
    border: 1px solid #2B3038;
    border-radius: 10px;
    overflow: hidden;
}
.run-row {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.95rem 1.4rem;
    border-bottom: 1px solid #2B3038;
}
.run-row:last-child { border-bottom: none; }
.run-dot {
    width: 9px; height: 9px;
    border-radius: 50%;
    background: #3A4048;
    flex-shrink: 0;
}
.run-dot.running { background: #E8A33D; box-shadow: 0 0 8px rgba(232,163,61,0.6); }
.run-dot.done { background: #4CAF7D; }
.run-num {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: #8A93A3;
    width: 22px;
    flex-shrink: 0;
}
.run-name {
    font-family: 'Manrope', sans-serif;
    font-weight: 600;
    font-size: 0.9rem;
    color: #E7E9EC;
    width: 150px;
    flex-shrink: 0;
}
.run-desc {
    font-size: 0.82rem;
    color: #8A93A3;
    flex-grow: 1;
}
.run-badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.66rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 0.22rem 0.6rem;
    border-radius: 4px;
    flex-shrink: 0;
}
.run-badge.waiting { color: #6B7280; background: rgba(107,114,128,0.1); }
.run-badge.running { color: #E8A33D; background: rgba(232,163,61,0.1); }
.run-badge.done     { color: #4CAF7D; background: rgba(76,175,125,0.1); }

/* ── Console / output panels ── */
.console {
    background: #101317;
    border: 1px solid #2B3038;
    border-radius: 8px;
    margin-top: 0.9rem;
    margin-bottom: 1.2rem;
    overflow: hidden;
}
.console-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.65rem 1.1rem;
    background: #15181D;
    border-bottom: 1px solid #2B3038;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.06em;
    color: #8A93A3;
}
.console-head.amber { color: #E8A33D; }
.console-head.green { color: #4CAF7D; }
.console-body {
    padding: 1.3rem 1.4rem;
    font-size: 0.88rem;
    line-height: 1.75;
    color: #C7CCD4;
    white-space: pre-wrap;
    font-family: 'Inter', sans-serif;
}

/* ── Spinner ── */
.stSpinner > div { color: #6C7BFF !important; }

/* ── Expander ── */
details summary {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.74rem !important;
    color: #8A93A3 !important;
    letter-spacing: 0.04em !important;
    cursor: pointer;
}

/* ── Footer ── */
.footnote {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    color: #3E434B;
    text-align: center;
    margin-top: 3rem;
    letter-spacing: 0.08em;
}
</style>
""", unsafe_allow_html=True)


# ── Session state init ────────────────────────────────────────────────────────
for key in ("results", "running", "done"):
    if key not in st.session_state:
        st.session_state[key] = {} if key == "results" else False


# ── Top status strip ────────────────────────────────────────────────────────
st.markdown(
    '<div class="topbar"><span></span><span class="status-chip">System Nominal</span></div>',
    unsafe_allow_html=True,
)

# ── Centered hero title ──────────────────────────────────────────────────────
st.markdown(
    '<div class="hero-center">'
    '<div class="wordmark-big">ResearchMind</div>'
    '<div class="hero-tagline">Four specialized AI agents collaborate — searching, scraping, writing, and critiquing — ' \
    'to deliver a polished research report on any topic.</div>'
    '</div>',
    unsafe_allow_html=True,
)


# ── Input ─────────────────────────────────────────────────────────────────────
topic = st.text_input(
    "Research Topic",
    placeholder="e.g. Quantum computing breakthroughs in 2025",
    key="topic_input",
    label_visibility="visible",
)
run_btn = st.button("Run Pipeline", use_container_width=True)


# ── Pipeline (CI-style run rows) ────────────────────────────────────────────────
st.markdown('<div class="section-title">Pipeline</div>', unsafe_allow_html=True)

r = st.session_state.results
done = st.session_state.done


def step_state(step):
    if not r:
        return "waiting"
    steps = ["search", "reader", "writer", "critic"]
    if step in r:
        return "done"
    if st.session_state.running:
        for k in steps:
            if k not in r:
                return "running" if k == step else "waiting"
    return "waiting"


step_defs = [
    ("01", "search", "Search Agent", "Gathers recent web information"),
    ("02", "reader", "Reader Agent", "Scrapes & extracts deep content"),
    ("03", "writer", "Writer Chain", "Drafts the full research report"),
    ("04", "critic", "Critic Chain", "Reviews & scores the report"),
]

badge_label = {"waiting": "Standby", "running": "Running", "done": "Complete"}

row_parts = ['<div class="run-table">']
for num, key, name, desc in step_defs:
    st_state = step_state(key)
    row_parts.append(
        f'<div class="run-row">'
        f'<span class="run-dot {st_state}"></span>'
        f'<span class="run-num">{num}</span>'
        f'<span class="run-name">{name}</span>'
        f'<span class="run-desc">{desc}</span>'
        f'<span class="run-badge {st_state}">{badge_label[st_state]}</span>'
        f'</div>'
    )
row_parts.append('</div>')
rows_html = "".join(row_parts)
st.markdown(rows_html, unsafe_allow_html=True)


# ── Run pipeline ──────────────────────────────────────────────────────────────
if run_btn:
    if not topic.strip():
        st.warning("Please enter a research topic first.")
    else:
        st.session_state.results = {}
        st.session_state.running = True
        st.session_state.done = False
        st.rerun()

if st.session_state.running and not st.session_state.done:
    results = {}
    topic_val = st.session_state.topic_input

    # ── Step 1: Search ──
    with st.spinner("🔍  Search Agent is working…"):
        search_agent = build_search_agent()
        sr = search_agent.invoke({
            "messages": [("user", f"Find recent, reliable and detailed information about: {topic_val}")]
        })
        results["search"] = sr["messages"][-1].content
        st.session_state.results = dict(results)
    st.rerun() if False else None   # keep inline for now

    # ── Step 2: Reader ──
    with st.spinner("📄  Reader Agent is scraping top resources…"):
        reader_agent = build_reader_agent()
        rr = reader_agent.invoke({
            "messages": [("user",
                f"Based on the following search results about '{topic_val}', "
                f"pick the most relevant URL and scrape it for deeper content.\n\n"
                f"Search Results:\n{results['search'][:800]}"
            )]
        })
        results["reader"] = rr["messages"][-1].content
        st.session_state.results = dict(results)

    # ── Step 3: Writer ──
    with st.spinner("✍️  Writer is drafting the report…"):
        research_combined = (
            f"SEARCH RESULTS:\n{results['search']}\n\n"
            f"DETAILED SCRAPED CONTENT:\n{results['reader']}"
        )
        results["writer"] = writer_chain.invoke({
            "topic": topic_val,
            "research": research_combined
        })
        st.session_state.results = dict(results)

    # ── Step 4: Critic ──
    with st.spinner("🧐  Critic is reviewing the report…"):
        results["critic"] = critic_chain.invoke({
            "report": results["writer"]
        })
        st.session_state.results = dict(results)

    st.session_state.running = False
    st.session_state.done = True
    st.rerun()


# ── Results display ───────────────────────────────────────────────────────────
r = st.session_state.results

if r:
    st.markdown('<div class="section-title">Results</div>', unsafe_allow_html=True)

    # Raw outputs in expanders
    if "search" in r:
        with st.expander("Search results (raw)", expanded=False):
            st.markdown(f'<div class="console"><div class="console-head">OUTPUT — search_agent</div>'
                        f'<div class="console-body">{r["search"]}</div></div>', unsafe_allow_html=True)

    if "reader" in r:
        with st.expander("Scraped content (raw)", expanded=False):
            st.markdown(f'<div class="console"><div class="console-head">OUTPUT — reader_agent</div>'
                        f'<div class="console-body">{r["reader"]}</div></div>', unsafe_allow_html=True)

    # Final report
    if "writer" in r:
        st.markdown(
            '<div class="console">'
            '<div class="console-head amber">FINAL REPORT — writer_chain</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div style="padding:1.3rem 1.4rem;">', unsafe_allow_html=True)
        st.markdown(r["writer"])   # render markdown natively
        st.markdown("</div></div>", unsafe_allow_html=True)

        # Download
        st.download_button(
            label="Download report (.md)",
            data=r["writer"],
            file_name=f"research_report_{int(time.time())}.md",
            mime="text/markdown",
        )

    # Critic feedback
    if "critic" in r:
        st.markdown(
            '<div class="console">'
            '<div class="console-head green">CRITIC REVIEW — critic_chain</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div style="padding:1.3rem 1.4rem;">', unsafe_allow_html=True)
        st.markdown(r["critic"])
        st.markdown("</div></div>", unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footnote">
    ResearchMind · LangChain multi-agent pipeline · Built with Streamlit
</div>
""", unsafe_allow_html=True)
