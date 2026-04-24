import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

API_URL = "http://127.0.0.1:8003"
REQUEST_TIMEOUT = 5

st.set_page_config(page_title="DappGenius CyberFlow™", layout="wide")

# =====================================================
# HEADER
# =====================================================

logo_path = os.path.join(os.path.dirname(__file__), "..", "static", "goknown.png")

col1, col2, col3 = st.columns([1,5,2])

with col1:
    if os.path.exists(logo_path):
        st.image(logo_path, width=120)

with col2:
    st.markdown("""
    <h1 style='margin-bottom:0;'>DappGenius CyberFlow™</h1>
    <p style='margin-top:0;color:gray;font-size:18px;'>
    AI-Governed Workflow Intelligence Engine
    </p>
    """, unsafe_allow_html=True)

with col3:
    st.link_button("Learn More", "https://www.goknown.com/aboutus")
    st.link_button("API Docs", f"{API_URL}/docs")

st.divider()

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

if alert is not None:
    st.markdown(f"""
<div style="background-color:#ff4b4b;padding:15px;border-radius:10px;color:white;font-weight:bold;">
🚨 HIGH ANOMALY DETECTED<br>
Workflow: {alert['workflow_id']}<br>
State: {alert['to_state']}<br>
Score: {round(alert['normalized_score'],3)}
</div>
""", unsafe_allow_html=True)
else:
    st.success("🟢 System Status: Normal")

st.divider()

# =====================================================
# REFRESH
# =====================================================

if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

st.divider()

# =====================================================
# MODE SELECTOR
# =====================================================

mode = st.radio(
    "Select Mode",
    [
        "🧠 Live Execution",
        "📊 Governance Dashboard",
        "📜 Full History",
        "📥 Batch CSV Scoring",
        "⚙️ Admin Controls",
        "🎥 Tutorials"
    ],
    horizontal=True
)

st.divider()

# =====================================================
# 🧠 LIVE EXECUTION
# =====================================================

if mode == "🧠 Live Execution":

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

        if st.button("Activate Model"):
            requests.post(
                f"{API_URL}/model/activate",
                params={
                    "model_id":st.session_state.model_id,
                    "version":st.session_state.version
                }
            )
            st.success("Model Activated")

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

    st.header("Governance Overview")

    col1, col2 = st.columns([1,2])

    # HEALTH
    with col1:

        health = calculate_system_health()

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
                'axis': {'range':[0,100]},
                'bar': {'color': color},
                'steps': [
                    {'range':[0,50],'color':"#ff4b4b"},
                    {'range':[50,80],'color':"#ffc107"},
                    {'range':[80,100],'color':"#28a745"}
                ]
            }
        ))

        st.plotly_chart(fig, use_container_width=True)

    # KPI + CHART GRID
    with col2:

        data = fetch_governance_data()

        if not data:
            st.info("No active transitions")

        else:
            domains = list(data.items())

            for i in range(0, len(domains), 2):

                cols = st.columns(2)

                for j in range(2):

                    if i + j < len(domains):

                        domain, summary = domains[i + j]

                        with cols[j]:

                            st.markdown("""
                            <div style="border:1px solid #eee;
                                        border-radius:12px;
                                        padding:12px;
                                        margin-bottom:15px;">
                            """, unsafe_allow_html=True)

                            st.subheader(domain.upper())

                            total = sum(summary.values())

                            k1, k2, k3, k4 = st.columns(4)
                            k1.metric("Total", total)
                            k2.metric("High", summary["HIGH"])
                            k3.metric("Medium", summary["MEDIUM"])
                            k4.metric("Low", summary["LOW"])

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

                            st.plotly_chart(fig, use_container_width=True)

                            st.markdown("</div>", unsafe_allow_html=True)

# =====================================================
# 📜 FULL HISTORY
# =====================================================

elif mode == "📜 Full History":

    history = fetch_full_history()

    if history:
        df = pd.DataFrame(history)
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        st.dataframe(df)

        st.subheader("State Heatmap")
        st.plotly_chart(px.imshow(
            df.pivot_table(index="workflow_id",columns="to_state",values="normalized_score",aggfunc="mean")
        ))

        st.subheader("Time Heatmap")
        df["bucket"] = df["timestamp"].dt.floor("5min")
        st.plotly_chart(px.imshow(
            df.pivot_table(index="workflow_id",columns="bucket",values="normalized_score",aggfunc="mean")
        ))

# =====================================================
# 📥 CSV
# =====================================================

elif mode == "📥 Batch CSV Scoring":

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

    if st.button("Archive Data"):
        requests.post(f"{API_URL}/admin/soft-reset")

    if st.button("Delete All Data"):
        requests.post(f"{API_URL}/admin/hard-reset")

# =====================================================
# 🎥 TUTORIALS
# =====================================================

elif mode == "🎥 Tutorials":

    st.header("🎥 Tutorials")

    def card(title, url):
        embed = url.replace("share","embed")
        st.markdown(f"""
        <div style="border:1px solid #eee;border-radius:10px;padding:10px;margin-bottom:15px;">
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
