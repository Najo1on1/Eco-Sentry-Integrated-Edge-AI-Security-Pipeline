import streamlit as st
import pandas as pd
import time
import os

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
LOG_FILE = "../monitor_stream.csv"
IDLE_TIMEOUT = 3.0  # Seconds to wait before considering system "Idle"

st.set_page_config(page_title="Eco Sentry | Watchtower", layout="wide")

# ---------------------------------------------------------
# UI LAYOUT
# ---------------------------------------------------------
st.title("🛡️ Eco Sentry: Cognitive Security Node")

# Create layout columns
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Real-Time Anomaly Scores")
    # FIX: Create TWO separate placeholders to prevent ghosting
    status_placeholder = st.empty()
    chart_placeholder = st.empty()

with col2:
    st.subheader("Live Log Feed")
    log_placeholder = st.empty()

# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------
def get_system_status():
    """
    Checks if the log file is being actively written to.
    """
    if not os.path.exists(LOG_FILE):
        return "IDLE"
    
    try:
        last_modified = os.path.getmtime(LOG_FILE)
        current_time = time.time()
        if (current_time - last_modified) > IDLE_TIMEOUT:
            return "IDLE"
        return "ACTIVE"
    except OSError:
        return "IDLE"

def load_data():
    try:
        # Read only the last 50 lines
        return pd.read_csv(LOG_FILE).tail(50)
    except (pd.errors.EmptyDataError, FileNotFoundError):
        return pd.DataFrame(columns=["timestamp", "score", "is_threat", "log", "analysis"])

# ---------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------
while True:
    status = get_system_status()
    
    if status == "IDLE":
        # IDLE STATE: Show Shield in the Chart Area
        status_placeholder.empty() # Clear the status bar
        
        with chart_placeholder.container():
            st.markdown(
                """
                <div style="text-align: center; padding: 50px;">
                    <h1 style="font-size: 80px;">🛡️</h1>
                    <h3>System Idle</h3>
                    <p style="color: gray;">Waiting for live telemetry stream...</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        with log_placeholder.container():
            st.info("Status: Standby - No Data Stream")

    elif status == "ACTIVE":
        # LIVE STATE
        df = load_data()
        
        if not df.empty:
            last_row = df.iloc[-1]
            last_score = last_row["score"]

            # 1. Update Status Placeholder (Isolated)
            with status_placeholder.container():
                if last_score > 0.12:
                    st.error(f"🚨 ANOMALY DETECTED: Score {last_score:.4f}")
                    # Show AI Analysis
                    if pd.notna(last_row.get("analysis")) and str(last_row["analysis"]) != "nan":
                        st.warning(f"🤖 **Edge AI Analysis:** {last_row['analysis']}")
                else:
                    st.success("✅ System Status: NORMAL")

            # 2. Update Chart Placeholder (Isolated)
            with chart_placeholder.container():
                # This container now ONLY handles the chart, preventing duplicates
                st.line_chart(df[["score"]])

            # 3. Update Log Feed
            with log_placeholder.container():
                display_cols = ["timestamp", "log", "is_threat"]
                recent_logs = df.iloc[::-1][display_cols].head(15)
                st.dataframe(recent_logs, hide_index=True, use_container_width=True)

    # Refresh Rate
    time.sleep(1)
    st.rerun()