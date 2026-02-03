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
    st.markdown("---")

    for issue in filtered_issues:
        with st.container():
            c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([2,1.2,1.2,1,0.8,1.2,2,0.8])

            with c1:
                st.write(f"**{issue.get('location')}**")
                st.caption(f"Issue #{issue.get('id')}")

            with c2:
                icons = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}
                st.write(f"{icons.get(issue.get('severity'), '⚪')} {issue.get('severity')}")

            with c3:
                st.write(issue.get("issue_type"))

            with c4:
                st.write(issue.get("current_usage"))
                dev = issue.get("energy_deviation_percentage")
                if dev is not None:
                    st.caption(f"{float(dev):+.1f}%")

            with c5:
                if st.button("📋", key=f"detail_{issue['id']}"):
                    show_issue_details(issue)

            with c6:
                status_options = ["Open", "In Progress", "Resolved"]
                new_status = st.selectbox(
                    "",
                    status_options,
                    index=status_options.index(issue.get("status", "Open")),
                    key=f"status_{issue['id']}"
                )

            with c7:
                solution = st.text_area(
                    "",
                    value=issue.get("solution", ""),
                    key=f"solution_{issue['id']}",
                    height=70
                )

            with c8:
                if st.button("Save", key=f"save_{issue['id']}"):
                    issue["status"] = new_status
                    issue["solution"] = solution

                    json_file = Path(__file__).parent / "consumption_issues.json"
                    with open(json_file, "w", encoding="utf-8") as f:
                        json.dump(CONSUMPTION_ISSUES, f, indent=4, ensure_ascii=False)

                    st.success("Saved")
                    st.rerun()

            st.markdown("---")

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
