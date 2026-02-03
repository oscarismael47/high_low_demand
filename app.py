import streamlit as st
import json
import pandas as pd
from pathlib import Path
import statistics

# --------------------------------------------------
# Page config (MUST be first Streamlit call)
# --------------------------------------------------
st.set_page_config(
    page_title="Electrical Consumption Issues",
    page_icon="⚡",
    layout="wide"
)

# --------------------------------------------------
# Data loading
# --------------------------------------------------
@st.cache_data
def load_consumption_issues():
    json_file = Path(__file__).parent / "consumption_issues.json"
    with open(json_file, "r", encoding="utf-8") as f:
        return json.load(f)

CONSUMPTION_ISSUES = load_consumption_issues()

# --------------------------------------------------
# Dialog: Issue Details
# --------------------------------------------------
@st.dialog("📋 Issue Details")
def show_issue_details(issue):
    st.markdown("### Issue Details")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Basic Information")
        st.write(f"**Issue ID:** {issue.get('id')}")
        st.write(f"**Location:** {issue.get('location')}")
        st.write(f"**Type:** {issue.get('issue_type')}")
        st.write(f"**Status:** {issue.get('status')}")
        st.write(f"**Severity:** {issue.get('severity')}")
        st.write(f"**Reported Date:** {issue.get('reported_date')}")

    with col2:
        st.markdown("#### Energy Metrics")
        st.write(f"**Current Usage:** {issue.get('current_usage')}")
        st.write(f"**Expected Usage:** {issue.get('expected_usage')}")

        deviation = issue.get("energy_deviation_percentage")
        if deviation is not None:
            st.write(f"**Deviation:** {float(deviation):+.1f}%")

        st.write(f"**Estimated Cost:** {issue.get('estimated_cost')}")

    st.markdown("---")
    st.markdown("#### Recommended Action")
    st.success(issue.get("recommended_action", "N/A"))

# --------------------------------------------------
# Header
# --------------------------------------------------
st.title("⚡ Electrical Consumption Issues")
st.markdown("Monitor and manage electrical consumption anomalies across all buildings")

# --------------------------------------------------
# Filters
# --------------------------------------------------
f1, f2, f3 = st.columns(3)

with f1:
    filter_status = st.selectbox("Status", ["All", "Open", "In Progress", "Resolved"])

with f2:
    filter_severity = st.selectbox("Severity", ["All", "Critical", "High", "Medium", "Low"])

with f3:
    filter_type = st.selectbox("Type", ["All", "High Consumption", "Low Consumption", "Intermittent"])

# --------------------------------------------------
# Apply filters
# --------------------------------------------------
filtered_issues = CONSUMPTION_ISSUES

if filter_status != "All":
    filtered_issues = [i for i in filtered_issues if i.get("status") == filter_status]

if filter_severity != "All":
    filtered_issues = [i for i in filtered_issues if i.get("severity") == filter_severity]

if filter_type != "All":
    filtered_issues = [i for i in filtered_issues if i.get("issue_type") == filter_type]

# --------------------------------------------------
# Issues Table
# --------------------------------------------------
if not filtered_issues:
    st.warning("No issues match the selected filters.")
else:
    st.markdown(f"### Found {len(filtered_issues)} issue(s)")
    
    # Prepare data for table
    table_data = []
    for issue in filtered_issues:
        icons = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}
        dev = issue.get("energy_deviation_percentage")
        deviation_str = f"{float(dev):+.1f}%" if dev is not None else "N/A"
        
        table_data.append({
            "ID": issue.get("id"),
            "Location": issue.get("location"),
            "Type": issue.get("issue_type"),
            "Severity": f"{icons.get(issue.get('severity'), '⚪')} {issue.get('severity')}",
            "Current Usage": issue.get("current_usage"),
            "Expected Usage": issue.get("expected_usage"),
            "Deviation": deviation_str,
            "Status": issue.get("status"),
            "Reported Date": issue.get("reported_date"),
        })
    
    # Display table
    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Details section
    st.markdown("### 📋 View Issue Details")
    issue_options = [None] + [issue.get("id") for issue in filtered_issues]
    issue_id = st.selectbox(
        "Select an issue to view details:",
        options=issue_options,
        format_func=lambda x: "None" if x is None else f"Issue #{x} - {next((i.get('location') for i in filtered_issues if i.get('id') == x), 'Unknown')}"
    )
    
    selected_issue = next((issue for issue in filtered_issues if issue.get("id") == issue_id), None) if issue_id is not None else None
    if selected_issue:
        show_issue_details(selected_issue)

# --------------------------------------------------
# Summary Stats
# --------------------------------------------------
st.markdown("### 📊 Summary Statistics")

s1, s2, s3, s4 = st.columns(4)

with s1:
    st.metric("Critical", sum(i["severity"]=="Critical" for i in CONSUMPTION_ISSUES))

with s2:
    st.metric("Open", sum(i["status"]=="Open" for i in CONSUMPTION_ISSUES))

with s3:
    st.metric("High Consumption", sum(i["issue_type"]=="High Consumption" for i in CONSUMPTION_ISSUES))

with s4:
    st.metric("Resolved", sum(i["status"]=="Resolved" for i in CONSUMPTION_ISSUES))
