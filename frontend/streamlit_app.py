import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

API_URL = "http://127.0.0.1:8003"
REQUEST_TIMEOUT = 5
KNOWNCOMPUTE_LOGO_PATH = Path.home() / "Desktop/goknown_monorepo/frontend/src/assets/KnownCompute.jpg"

THEME = {
    "bg": "#070920",
    "bg_mid": "#000034",
    "panel": "rgba(12, 24, 54, 0.78)",
    "panel_deep": "rgba(2, 8, 23, 0.72)",
    "sidebar": "rgba(6, 10, 31, 0.96)",
    "accent": "#53bf99",
    "accent_soft": "#8be7d7",
    "cyan": "#67e8f9",
    "blue": "#2563eb",
    "text": "#f8fafc",
    "muted": "#98a8bc",
    "border": "rgba(83, 191, 153, 0.18)",
    "shadow": "0 18px 45px rgba(0, 0, 0, 0.24)",
    "high": "#ff4b4b",
    "medium": "#ffc107",
    "low": "#28a745",
}

st.set_page_config(page_title="DAppGenius KnownCompute", layout="wide")


def inject_theme_css():
    st.markdown(f"""
    <style>
        :root {{
            --kc-bg: {THEME["bg"]};
            --kc-bg-mid: {THEME["bg_mid"]};
            --kc-panel: {THEME["panel"]};
            --kc-panel-deep: {THEME["panel_deep"]};
            --kc-sidebar: {THEME["sidebar"]};
            --kc-accent: {THEME["accent"]};
            --kc-accent-soft: {THEME["accent_soft"]};
            --kc-cyan: {THEME["cyan"]};
            --kc-blue: {THEME["blue"]};
            --kc-text: {THEME["text"]};
            --kc-muted: {THEME["muted"]};
            --kc-border: {THEME["border"]};
            --kc-shadow: {THEME["shadow"]};
        }}

        .stApp {{
            background:
                radial-gradient(circle at 18% 8%, rgba(83, 191, 153, 0.16), transparent 28%),
                linear-gradient(135deg, var(--kc-bg) 0%, var(--kc-bg-mid) 48%, #061827 100%);
            color: var(--kc-text);
        }}

        [data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        footer {{
            display: none;
        }}

        .block-container {{
            max-width: 1240px;
            padding: 2rem 2rem 4rem;
        }}

        [data-testid="stSidebar"] {{
            background: var(--kc-sidebar);
            border-right: 1px solid var(--kc-border);
            box-shadow: 18px 0 45px rgba(0, 0, 0, 0.28);
            backdrop-filter: blur(16px);
        }}

        [data-testid="stSidebar"] > div:first-child {{
            padding: 1.35rem 1rem 1.25rem;
        }}

        [data-testid="stSidebar"] img {{
            border-radius: 16px;
            background: rgba(255, 255, 255, 0.94);
            padding: 8px;
            box-shadow: 0 10px 24px rgba(0, 0, 0, 0.18);
        }}

        .known-topbar h1,
        h1, h2, h3, h4 {{
            color: var(--kc-text) !important;
            letter-spacing: 0 !important;
        }}

        .known-sidebar-section,
        .known-eyebrow {{
            color: var(--kc-accent-soft);
            font-size: 12px;
            font-weight: 800;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }}

        .known-sidebar-title {{
            margin: 16px 0 2px;
            color: var(--kc-text);
            font-size: 20px;
            font-weight: 900;
            line-height: 1.15;
        }}

        .known-sidebar-subtitle {{
            margin: 0 0 18px;
            color: var(--kc-muted);
            font-size: 12px;
            font-weight: 800;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }}

        .known-sidebar-footer {{
            margin-top: 22px;
            padding: 14px 2px 0;
            border-top: 1px solid rgba(83, 191, 153, 0.14);
            color: #9fb2c7;
            font-size: 13px;
            line-height: 1.5;
        }}

        [data-testid="stSidebar"] [data-testid="stRadio"] {{
            margin-bottom: 0;
            padding: 0;
            border: 0;
            border-radius: 0;
            background: transparent;
            box-shadow: none;
        }}

        [data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] {{
            display: grid;
            gap: 7px;
        }}

        [data-testid="stSidebar"] [data-testid="stRadio"] [role="radio"] {{
            width: 100%;
            min-height: 48px;
            padding: 10px 12px;
            border: 1px solid transparent;
            border-radius: 12px;
            background: transparent;
            color: #9fb2c7;
            font-weight: 800;
            transition: background 0.2s, border-color 0.2s, color 0.2s, transform 0.2s;
        }}

        [data-testid="stSidebar"] [data-testid="stRadio"] [role="radio"]:hover {{
            color: var(--kc-text);
            background: rgba(83, 191, 153, 0.11);
            border-color: rgba(83, 191, 153, 0.2);
            transform: translateX(2px);
        }}

        [data-testid="stSidebar"] [data-testid="stRadio"] [aria-checked="true"] {{
            color: #fff;
            border-color: rgba(103, 232, 249, 0.38);
            background: linear-gradient(90deg, var(--kc-blue) 0%, #0891b2 100%);
        }}

        .known-topbar {{
            min-height: 74px;
            margin-bottom: 24px;
            padding: 18px 22px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 18px;
            background: rgba(3, 7, 32, 0.74);
            border: 1px solid rgba(83, 191, 153, 0.14);
            border-radius: 18px;
            box-shadow: var(--kc-shadow);
            backdrop-filter: blur(16px);
        }}

        .known-topbar h1 {{
            margin: 6px 0 0;
            font-size: 28px;
            line-height: 1.1;
        }}

        .known-status-card,
        .known-card,
        .known-tutorial-card {{
            border: 1px solid var(--kc-border);
            border-radius: 18px;
            padding: 18px;
            background: linear-gradient(145deg, var(--kc-panel), var(--kc-panel-deep));
            box-shadow: var(--kc-shadow);
        }}

        .known-status-card {{
            margin-bottom: 18px;
        }}

        .known-status-card strong {{
            display: block;
            color: var(--kc-text);
            font-size: 18px;
            margin-bottom: 6px;
        }}

        .known-status-card span,
        .known-card span {{
            color: var(--kc-muted);
        }}

        .known-status-card.normal {{
            border-color: rgba(83, 191, 153, 0.34);
        }}

        .known-status-card.alert {{
            border-color: rgba(255, 75, 75, 0.42);
            background: linear-gradient(145deg, rgba(82, 14, 30, 0.82), rgba(2, 8, 23, 0.72));
        }}

        .known-card {{
            margin-bottom: 16px;
            transition: transform 0.2s, border-color 0.2s, box-shadow 0.2s;
        }}

        .known-card:hover,
        .known-tutorial-card:hover {{
            transform: translateY(-2px);
            border-color: rgba(83, 191, 153, 0.48);
            box-shadow: 0 24px 55px rgba(0, 0, 0, 0.28);
        }}

        .known-card-title {{
            margin: 0 0 14px;
            color: var(--kc-text);
            font-size: 18px;
            font-weight: 800;
            text-transform: uppercase;
        }}

        .known-mini-metrics {{
            display: grid;
            grid-template-columns: repeat(4, minmax(58px, 1fr));
            gap: 8px;
            margin-bottom: 12px;
        }}

        .known-mini-metric {{
            min-height: 76px;
            border: 1px solid rgba(148, 163, 184, 0.15);
            border-radius: 14px;
            padding: 12px;
            background: rgba(15, 23, 42, 0.58);
        }}

        .known-mini-metric span {{
            display: block;
            color: var(--kc-muted);
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }}

        .known-mini-metric strong {{
            display: block;
            margin-top: 8px;
            color: var(--kc-text);
            font-size: 20px;
            line-height: 1;
            white-space: nowrap;
            word-break: keep-all;
            overflow-wrap: normal;
        }}

        [data-testid="stVerticalBlockBorderWrapper"] {{
            border: 1px solid var(--kc-border);
            border-radius: 18px;
            padding: 18px;
            background: linear-gradient(145deg, var(--kc-panel), var(--kc-panel-deep));
            box-shadow: var(--kc-shadow);
        }}

        .stButton > button,
        .stLinkButton > a,
        [data-testid="stBaseButton-secondary"],
        [data-testid="stBaseButton-primary"] {{
            border: 1px solid rgba(83, 191, 153, 0.34) !important;
            border-radius: 12px !important;
            background: rgba(83, 191, 153, 0.1) !important;
            color: var(--kc-text) !important;
            font-weight: 800 !important;
            transition: transform 0.2s, background 0.2s, border-color 0.2s !important;
        }}

        .stButton > button:hover,
        .stLinkButton > a:hover {{
            transform: translateY(-1px);
            background: rgba(83, 191, 153, 0.18) !important;
            border-color: rgba(83, 191, 153, 0.52) !important;
            color: var(--kc-text) !important;
        }}

        [data-testid="stRadio"] {{
            margin-bottom: 22px;
            padding: 14px;
            border: 1px solid var(--kc-border);
            border-radius: 18px;
            background: rgba(6, 10, 31, 0.72);
            box-shadow: var(--kc-shadow);
        }}

        [data-testid="stRadio"] > label {{
            color: var(--kc-accent-soft) !important;
            font-size: 12px;
            font-weight: 800;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }}

        .main [data-testid="stRadio"] [role="radiogroup"] {{
            gap: 8px;
            flex-wrap: wrap;
        }}

        .main [data-testid="stRadio"] [role="radio"] {{
            min-height: 44px;
            padding: 8px 12px;
            border: 1px solid rgba(148, 163, 184, 0.15);
            border-radius: 12px;
            background: rgba(15, 23, 42, 0.44);
            color: #9fb2c7;
        }}

        .main [data-testid="stRadio"] [aria-checked="true"] {{
            border-color: rgba(103, 232, 249, 0.38);
            background: linear-gradient(90deg, var(--kc-blue) 0%, #0891b2 100%);
            color: #fff;
        }}

        .stSelectbox label,
        .stFileUploader label,
        .stDataFrame,
        .stMarkdown,
        p, label, span {{
            color: var(--kc-text);
        }}

        [data-testid="stMetric"] {{
            min-height: 96px;
            border: 1px solid rgba(83, 191, 153, 0.2);
            border-radius: 16px;
            padding: 16px;
            background: linear-gradient(145deg, rgba(12, 24, 54, 0.86), rgba(2, 8, 23, 0.72));
        }}

        [data-testid="stMetricLabel"] p {{
            color: var(--kc-muted) !important;
            font-size: 12px;
            font-weight: 800;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }}

        [data-testid="stMetricValue"] {{
            color: var(--kc-text);
        }}

        .stAlert {{
            border-radius: 14px;
        }}

        hr {{
            display: none;
        }}

        iframe {{
            border: 1px solid rgba(148, 163, 184, 0.15);
            border-radius: 14px;
            background: rgba(2, 8, 23, 0.72);
        }}

        @media (max-width: 1050px) {{
            .block-container {{
                padding: 1rem 1rem 3rem;
            }}

            .known-topbar {{
                align-items: flex-start;
                flex-direction: column;
            }}
        }}

        @media (max-width: 720px) {{
            .known-mini-metrics {{
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }}
        }}
    </style>
    """, unsafe_allow_html=True)


def render_topbar():
    st.markdown("""
    <div class="known-topbar">
        <div>
            <span class="known-eyebrow">AI-governed workflow intelligence engine</span>
            <h1>DAppGenius KnownCompute</h1>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_status_card(alert):
    if alert is not None:
        st.markdown(f"""
        <div class="known-status-card alert">
            <strong>High anomaly detected</strong>
            <span>Workflow: {alert['workflow_id']}<br>
            State: {alert['to_state']}<br>
            Score: {round(alert['normalized_score'], 3)}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="known-status-card normal">
            <strong>System Status: Normal</strong>
            <span>No high-severity workflow anomaly is currently active.</span>
        </div>
        """, unsafe_allow_html=True)


def render_domain_card_start(domain, summary):
    total = sum(summary.values())
    st.markdown(f"""
    <div class="known-card">
        <div class="known-card-title">{domain.upper()}</div>
        <div class="known-mini-metrics">
            <div class="known-mini-metric"><span>Total</span><strong>{total}</strong></div>
            <div class="known-mini-metric"><span>High</span><strong>{summary["HIGH"]}</strong></div>
            <div class="known-mini-metric"><span>Medium</span><strong>{summary["MEDIUM"]}</strong></div>
            <div class="known-mini-metric"><span>Low</span><strong>{summary["LOW"]}</strong></div>
        </div>
    """, unsafe_allow_html=True)


def render_card_end():
    st.markdown("</div>", unsafe_allow_html=True)


def apply_dark_plotly_theme(fig, height=None):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": THEME["text"], "family": "Inter, system-ui, sans-serif"},
        margin={"l": 12, "r": 12, "t": 44, "b": 12},
        legend={"font": {"color": THEME["muted"]}},
    )
    if height:
        fig.update_layout(height=height)
    return fig


inject_theme_css()

# =====================================================
# HEADER
# =====================================================

render_topbar()

link_col1, link_col2, link_col3 = st.columns([1, 1, 4])
with link_col1:
    st.link_button("Learn More", "https://www.goknown.com/aboutus")
with link_col2:
    st.link_button("API Docs", f"{API_URL}/docs")

# =====================================================
# DATA
# =====================================================

@st.cache_data(ttl=5)
def fetch_governance_data():
    try:
        r = requests.get(f"{API_URL}/analytics/by-domain", timeout=REQUEST_TIMEOUT)
        if r.status_code == 200:
            return r.json()
    except:
        return {}
    return {}

@st.cache_data(ttl=5)
def fetch_full_history():
    try:
        r = requests.get(f"{API_URL}/analytics/history", timeout=REQUEST_TIMEOUT)
        if r.status_code == 200:
            return r.json()
    except:
        return []
    return []

# =====================================================
# SYSTEM HEALTH
# =====================================================

def calculate_system_health():
    history = fetch_full_history()
    if not history:
        return 100

    df = pd.DataFrame(history)
    severity_map = {"LOW":0,"MEDIUM":0.5,"HIGH":1}
    df["risk"] = df["severity"].map(severity_map)

    risk_index = df["risk"].mean()
    return int(100 - (risk_index * 100))

# =====================================================
# ALERT
# =====================================================

def check_high_anomalies():
    history = fetch_full_history()
    if not history:
        return None

    df = pd.DataFrame(history)
    high = df[df["severity"] == "HIGH"]

    if high.empty:
        return None

    return high.sort_values("timestamp", ascending=False).iloc[0]

alert = check_high_anomalies()

render_status_card(alert)

# =====================================================
# REFRESH
# =====================================================

if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# =====================================================
# MODE SELECTOR
# =====================================================

with st.sidebar:
    if KNOWNCOMPUTE_LOGO_PATH.exists():
        st.image(str(KNOWNCOMPUTE_LOGO_PATH), use_container_width=True)

    st.markdown("""
    <div class="known-sidebar-title">KnownCompute</div>
    <div class="known-sidebar-subtitle">GoKnown workspace</div>
    """, unsafe_allow_html=True)

    mode = st.radio(
        "Navigation",
        [
            "🧠 Live Execution",
            "📊 Governance Dashboard",
            "📜 Full History",
            "📥 Batch CSV Scoring",
            "⚙️ Admin Controls",
            "🎥 Tutorials"
        ]
    )

    st.markdown("""
    <div class="known-sidebar-footer">
        <div class="known-sidebar-section">System</div>
        <div>Local API: 127.0.0.1:8003</div>
    </div>
    """, unsafe_allow_html=True)

# =====================================================
# 🧠 LIVE EXECUTION
# =====================================================

if mode == "🧠 Live Execution":

    with st.container(border=True):
        st.header("Start Workflow")

        domain = st.selectbox(
            "Select Domain",
            ["cybersecurity","sessions","transactions","organizations"]
        )

        if st.button("Generate Model"):
            r = requests.post(f"{API_URL}/model/generate", params={"domain":domain})
            if r.status_code == 200:
                data = r.json()
                st.session_state.model_id = data["model_id"]
                st.session_state.version = data["version"]
                st.success("Model Generated")

        if "model_id" in st.session_state:

            action_col1, action_col2 = st.columns(2)

            with action_col1:
                if st.button("Activate Model"):
                    requests.post(
                        f"{API_URL}/model/activate",
                        params={
                            "model_id":st.session_state.model_id,
                            "version":st.session_state.version
                        }
                    )
                    st.success("Model Activated")

            with action_col2:
                if st.button("Create Workflow"):
                    r = requests.post(
                        f"{API_URL}/workflow/create",
                        params={
                            "model_id":st.session_state.model_id,
                            "version":st.session_state.version
                        }
                    )
                    if r.status_code == 200:
                        data = r.json()
                        st.session_state.workflow_id = data["workflow_id"]
                        st.session_state.current_state = data["current_state"]
                        st.success("Workflow Created")

        if "workflow_id" in st.session_state:

            st.subheader("Execute Transition")
            st.write("Current State:", st.session_state.current_state)

            r = requests.get(
                f"{API_URL}/workflow/{st.session_state.workflow_id}/allowed-events"
            )

            if r.status_code == 200:
                allowed = r.json()["events"]

                if allowed:
                    selected = st.selectbox("Allowed Events", allowed)

                    if st.button("Execute Event"):
                        r2 = requests.post(
                            f"{API_URL}/workflow/{st.session_state.workflow_id}/execute",
                            params={"event":selected}
                        )
                        if r2.status_code == 200:
                            data = r2.json()
                            st.session_state.current_state = data["new_state"]
                            st.success(f"Severity: {data['severity']}")
                            st.cache_data.clear()

# =====================================================
# 📊 GOVERNANCE DASHBOARD (FINAL POLISHED)
# =====================================================

elif mode == "📊 Governance Dashboard":

    with st.container(border=True):
        st.header("Governance Overview")

        health = calculate_system_health()
        data = fetch_governance_data()

        def render_health_visual():
            if health < 50:
                color = "#ff4b4b"
            elif health < 80:
                color = "#ffc107"
            else:
                color = "#28a745"

            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=health,
                title={'text': "System Health"},
                gauge={
                    'axis': {'range':[0,100], 'tickcolor': THEME["muted"]},
                    'bar': {'color': color},
                    'bgcolor': "rgba(2, 8, 23, 0.42)",
                    'bordercolor': "rgba(83, 191, 153, 0.22)",
                    'steps': [
                        {'range':[0,50],'color':"rgba(255, 75, 75, 0.28)"},
                        {'range':[50,80],'color':"rgba(255, 193, 7, 0.28)"},
                        {'range':[80,100],'color':"rgba(40, 167, 69, 0.28)"}
                    ]
                }
            ))
            fig.update_traces(number={"font": {"color": THEME["text"]}}, title={"font": {"color": THEME["accent_soft"]}})
            apply_dark_plotly_theme(fig, height=340)

            st.plotly_chart(fig, use_container_width=True)

        def render_domain_visual(domain, summary):
            render_domain_card_start(domain, summary)

            df = pd.DataFrame(summary.items(), columns=["Severity","Count"])

            fig = px.pie(
                df,
                values="Count",
                names="Severity",
                hole=0.5,
                color="Severity",
                color_discrete_map={
                    "HIGH":"#ff4b4b",
                    "MEDIUM":"#ffc107",
                    "LOW":"#28a745"
                }
            )
            fig.update_traces(
                textfont={"color": THEME["text"]},
                marker={"line": {"color": "rgba(2, 8, 23, 0.82)", "width": 2}},
            )
            apply_dark_plotly_theme(fig, height=260)

            st.plotly_chart(fig, use_container_width=True)

            render_card_end()

        visuals = [("health", None)]
        if data:
            visuals.extend(list(data.items()))

        for i in range(0, len(visuals), 2):
            cols = st.columns(2)

            for j in range(2):
                if i + j < len(visuals):
                    name, summary = visuals[i + j]

                    with cols[j]:
                        if name == "health":
                            render_health_visual()
                        else:
                            render_domain_visual(name, summary)

        if not data:
            st.info("No active transitions")

# =====================================================
# 📜 FULL HISTORY
# =====================================================

elif mode == "📜 Full History":

    with st.container(border=True):
        st.header("Full History")

        history = fetch_full_history()

        if history:
            df = pd.DataFrame(history)
            df["timestamp"] = pd.to_datetime(df["timestamp"])

            st.dataframe(df)

            st.subheader("State Heatmap")
            state_fig = px.imshow(
                df.pivot_table(index="workflow_id",columns="to_state",values="normalized_score",aggfunc="mean"),
                color_continuous_scale=["#061827", "#0891b2", "#8be7d7"],
            )
            apply_dark_plotly_theme(state_fig, height=360)
            st.plotly_chart(state_fig, use_container_width=True)

            st.subheader("Time Heatmap")
            df["bucket"] = df["timestamp"].dt.floor("5min")
            time_fig = px.imshow(
                df.pivot_table(index="workflow_id",columns="bucket",values="normalized_score",aggfunc="mean"),
                color_continuous_scale=["#061827", "#0891b2", "#8be7d7"],
            )
            apply_dark_plotly_theme(time_fig, height=360)
            st.plotly_chart(time_fig, use_container_width=True)

# =====================================================
# 📥 CSV
# =====================================================

elif mode == "📥 Batch CSV Scoring":

    with st.container(border=True):
        st.header("Batch CSV Scoring")

        file = st.file_uploader("Upload CSV", type=["csv"])

        if file:
            if st.button("Run Scoring"):
                r = requests.post(f"{API_URL}/analytics/score-csv", files={"file":file})
                if r.status_code == 200:
                    st.dataframe(pd.DataFrame(r.json()))

# =====================================================
# ⚙️ ADMIN
# =====================================================

elif mode == "⚙️ Admin Controls":

    with st.container(border=True):
        st.header("Admin Controls")

        admin_col1, admin_col2 = st.columns(2)

        with admin_col1:
            if st.button("Archive Data"):
                requests.post(f"{API_URL}/admin/soft-reset")

        with admin_col2:
            if st.button("Delete All Data"):
                requests.post(f"{API_URL}/admin/hard-reset")

# =====================================================
# 🎥 TUTORIALS
# =====================================================

elif mode == "🎥 Tutorials":

    with st.container(border=True):
        st.header("🎥 Tutorials")

        def card(title, url):
            embed = url.replace("share","embed")
            st.markdown(f"""
            <div class="known-tutorial-card">
                <h4>{title}</h4>
                <iframe src="{embed}" width="100%" height="250"></iframe>
            </div>
            """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            card("Overview","https://www.loom.com/share/fd970d33ffb3477392ad926f4f36b9ed")
            card("Workflow 1","https://www.loom.com/share/0be3e078110c4b8380361108d65643f5")
            card("Anomaly Detection","https://www.loom.com/share/da3a65d7d80743a5a6145e6066b797fc")
            card("Admin","https://www.loom.com/share/b42cb1b4832a4bc1bcaa9d7ddc80f529")
            card("Architecture","https://www.loom.com/share/4d48d976f13549d3af8388f05cb890c3")

        with col2:
            card("Intro","https://www.loom.com/share/797dbb8a71cf42f28870560f951d6e1c")
            card("Workflow 2","https://www.loom.com/share/cd0f710065fe458c9456f98fe689a877")
            card("Dashboard","https://www.loom.com/share/2390d5da10204d37afd4e331f302e597")
            card("CSV","https://www.loom.com/share/b6e989ae357147d996456c78e30a8f7c")
            card("Use Cases","https://www.loom.com/share/509b691fe44342678d1023cd6204ed33")
