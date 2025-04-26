import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space
import time

# Path configurations
LOG_FILE_PATH = "/var/ossec/logs/alerts/alerts.json"
ACTIVE_RESPONSE_PATH = "/var/ossec/active-response"

# Define custom rule IDs for filtering
CUSTOM_RULE_IDS = [1002, 106032, 100300]

# Ensure response directory exists
os.makedirs(ACTIVE_RESPONSE_PATH, exist_ok=True)

# Set page configuration
st.set_page_config(
    page_title="Wazuh Alert Management Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .stButton button {
        width: 100%;
        border-radius: 4px;
    }
    .severity-high {
        color: white;
        background-color: #FF4B4B;
        padding: 2px 10px;
        border-radius: 20px;
        font-weight: 500;
    }
    .severity-medium {
        color: white;
        background-color: #FFA500;
        padding: 2px 10px;
        border-radius: 20px;
        font-weight: 500;
    }
    .severity-low {
        color: black;
        background-color: #FFD700;
        padding: 2px 10px;
        border-radius: 20px;
        font-weight: 500;
    }
    .timestamp {
        color: #666;
        font-size: 0.85em;
    }
    .metadata-pill {
        display: inline-block;
        background-color: #3AB0FF;
        border-radius: 20px;
        padding: 2px 10px;
        margin-right: 5px;
        font-size: 0.8em;
    }
</style>
""", unsafe_allow_html=True)

def read_logs(file_path, selected_rule_id=None):
    """Read and filter logs from the alerts file"""
    if not os.path.exists(file_path):
        st.error(f"⚠️ Log file not found at: {file_path}")
        return []

    logs = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    log_entry = json.loads(line)
                    rule = log_entry.get("rule", {})
                    rule_id = rule.get("id")

                    # Apply rule ID filter if specified
                    if selected_rule_id is not None:
                        try:
                            rule_id_int = int(rule_id)
                            if rule_id_int != selected_rule_id:
                                continue
                        except (ValueError, TypeError):
                            continue
                    
                    logs.append(log_entry)
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        st.error(f"Error reading log file: {e}")

    # Return last 10 logs or all if fewer than 10
    return logs[-10:] if logs else []

def write_active_response(log, index):
    """Create an active response file based on alert data"""
    rule = log.get("rule", {})
    agent = log.get("agent", {})
    timestamp = log.get("timestamp", datetime.utcnow().isoformat())
    rule_id = rule.get("id", "unknown")
    agent_id = agent.get("id", "unknown")
    full_log = log.get("full_log", "N/A")

    # Clean timestamp for filename
    safe_timestamp = timestamp.replace(":", "-").replace("+", "_").replace("T", "_")

    filename = f"response_{rule_id}_{agent_id}_{safe_timestamp}_{index}.txt"
    file_path = os.path.join(ACTIVE_RESPONSE_PATH, filename)

    try:
        with open(file_path, 'w') as f:
            f.write(f"Rule ID: {rule_id}\n")
            f.write(f"Agent ID: {agent_id}\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Full Log:\n{full_log}\n")
        return True, file_path
    except Exception as e:
        return False, str(e)

def get_severity_class(level):
    """Determine severity class based on rule level"""
    try:
        level_int = int(level)
        if level_int >= 10:
            return "severity-high"
        elif level_int >= 5:
            return "severity-medium"
        else:
            return "severity-low"
    except (ValueError, TypeError):
        return "severity-low"

def display_dashboard_header():
    """Display the dashboard header with metrics"""
    # Get all logs to calculate metrics
    all_logs = read_logs(LOG_FILE_PATH)
    
    if not all_logs:
        st.warning("No alert data available to display metrics")
        return
    
    # Calculate metrics
    total_alerts = len(all_logs)
    high_severity = sum(1 for log in all_logs if int(log.get("rule", {}).get("level", 0)) >= 10)
    unique_agents = len(set(log.get("agent", {}).get("id", "") for log in all_logs))
    
    # Display metrics in a grid
    colored_header(
        label="Security Monitoring Dashboard",
        description="Real-time alert monitoring and response management",
        color_name="blue-70"
    )
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="Total Alerts", value=total_alerts)
    
    with col2:
        st.metric(label="High Severity", value=high_severity)
    
    with col3:
        st.metric(label="Unique Agents", value=unique_agents)
    
    with col4:
        now = datetime.now()
        st.metric(label="Last Updated", value=now.strftime("%H:%M:%S"))

def render_alert_card(log, index):
    """Render a single alert as a card with actions"""
    rule = log.get("rule", {})
    agent = log.get("agent", {})
    timestamp = log.get("timestamp", "N/A")
    rule_id = rule.get("id", "N/A")
    level = rule.get("level", "N/A")
    location = log.get("location", "Unknown")
    decoder = log.get("decoder", {}).get("name", "Unknown")
    description = rule.get("description", "No description")
    
    # Generate a unique key for this alert
    unique_key = f"{rule_id}_{timestamp}_{index}"
    severity_class = get_severity_class(level)
    
    # Format the timestamp for better readability
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        formatted_time = dt.strftime("%b %d, %Y %H:%M:%S")
    except:
        formatted_time = timestamp
    
    # Create a card using Streamlit components
    with st.container():
        card = st.container()
        
        # Add a border and padding
        card.markdown("---")
        
        # Header row with description and severity
        header_col1, header_col2 = card.columns([3, 1])
        with header_col1:
            st.markdown(f"#### {description}")
        with header_col2:
            st.markdown(f"<span class='{severity_class}'>Level {level}</span>", unsafe_allow_html=True)
        
        # Metadata row
        st.markdown(
            f"<span class='metadata-pill'>Rule ID: {rule_id}</span>"
            f"<span class='metadata-pill'>Agent: {agent.get('name', 'N/A')}</span>"
            f"<span class='metadata-pill'>Decoder: {decoder}</span>",
            unsafe_allow_html=True
        )
        
        # Timestamp
        st.markdown(f"<span class='timestamp'>🕒 {formatted_time}</span>", unsafe_allow_html=True)
        
        # Create expandable details section
        with st.expander("View Details"):
            details_col1, details_col2 = st.columns(2)
            
            with details_col1:
                st.markdown("**Alert Information**")
                st.json({
                    "rule_id": rule_id,
                    "level": level,
                    "description": description,
                    "groups": rule.get("groups", []),
                    "mitre": rule.get("mitre", {})
                })
                
            with details_col2:
                st.markdown("**Source Information**")
                st.json({
                    "agent": {
                        "id": agent.get("id", "N/A"),
                        "name": agent.get("name", "N/A"),
                        "ip": agent.get("ip", "N/A")
                    },
                    "location": location,
                    "decoder": decoder
                })
            
            if 'full_log' in log:
                st.markdown("**Full Log Content**")
                st.code(log['full_log'], language="bash")
            
            # Action buttons
            action_col1, action_col2, action_col3 = st.columns([1, 1, 2])
            with action_col1:
                if st.button("🚨 Trigger Response", key=f"trigger_{unique_key}"):
                    with st.spinner("Processing response..."):
                        success, response = write_active_response(log, index)
                        time.sleep(0.5)  # Small delay for better UX
                        if success:
                            st.success("✅ Response triggered successfully")
                            st.caption(f"File: {os.path.basename(response)}")
                        else:
                            st.error(f"❌ Failed: {response}")
            
            with action_col2:
                if st.button("📋 Mark Reviewed", key=f"review_{unique_key}"):
                    st.info("Alert marked as reviewed")

def display_visualization(logs):
    """Create visualizations based on log data"""
    if not logs:
        return
    
    # Extract data for visualization
    viz_data = []
    for log in logs:
        rule = log.get("rule", {})
        viz_data.append({
            "rule_id": rule.get("id", "Unknown"),
            "level": rule.get("level", 0),
            "timestamp": log.get("timestamp", "")
        })
    
    df = pd.DataFrame(viz_data)
    
    # Convert timestamp to datetime
    try:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['date'] = df['timestamp'].dt.date
    except:
        st.warning("Unable to parse timestamps for visualization")
        return
    
    # Create severity distribution chart
    level_counts = df['level'].value_counts().reset_index()
    level_counts.columns = ['Level', 'Count']
    
    fig = px.bar(
        level_counts, 
        x='Level', 
        y='Count',
        title="Alert Severity Distribution",
        color='Level',
        color_continuous_scale=['yellow', 'orange', 'red'],
        labels={'Count': 'Number of Alerts'},
        height=300
    )
    
    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def main():
    """Main application function"""
    # Create sidebar
    with st.sidebar:
        st.image("https://wazuh.com/wp-content/uploads/2022/06/wazuh-logo.svg", width=200)
        st.markdown("## Alert Filters")
        
        # Rule ID filter
        selected_rule_id = st.selectbox(
            "Filter by Rule ID:",
            options=CUSTOM_RULE_IDS,
            format_func=lambda x: f"Rule {x}"
        )
        
        # Refresh button
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()

        
        st.markdown("---")
        st.markdown("### Dashboard Info")
        st.info(
            "This dashboard provides real-time monitoring of Wazuh security alerts "
            "with the ability to trigger active responses."
        )
        
        # Add version info at the bottom
        st.markdown("---")
        st.caption("Wazuh Alert Viewer v1.2.0")
        
    # Main content
    display_dashboard_header()
    
    # Load filtered logs
    filtered_logs = read_logs(LOG_FILE_PATH, selected_rule_id)
    
    # Tabs for different views
    tab1, tab2 = st.tabs(["Alert Feed", "Analytics"])
    
    with tab1:
        if not filtered_logs:
            st.warning(f"🚫 No alerts found for Rule ID {selected_rule_id}")
        else:
            st.success(f"Displaying {len(filtered_logs)} alerts for Rule ID {selected_rule_id}")
            
            # Display each alert
            for idx, log in enumerate(filtered_logs):
                render_alert_card(log, idx)
    
    with tab2:
        if not filtered_logs:
            st.warning("No data available for visualization")
        else:
            display_visualization(filtered_logs)
            
            # Add a data table
            st.subheader("Alert Data Table")
            
            # Extract relevant fields for the table
            table_data = []
            for log in filtered_logs:
                rule = log.get("rule", {})
                agent = log.get("agent", {})
                
                table_data.append({
                    "Rule ID": rule.get("id", ""),
                    "Level": rule.get("level", ""),
                    "Description": rule.get("description", ""),
                    "Agent": agent.get("name", ""),
                    "Timestamp": log.get("timestamp", "")
                })
            
            # Display as dataframe
            df = pd.DataFrame(table_data)
            st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    main()