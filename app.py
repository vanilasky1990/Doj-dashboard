import streamlit as st
import pandas as pd
import plotly.express as px

# Page config for wide dashboard look
st.set_page_config(page_title="Tsakane Dashboard", layout="wide", page_icon="🇿🇦")

# Custom CSS for orange banner and cards
st.markdown("""
    <style>
    .tsakane-banner {
        background-color: #FFB612;
        color: #000000;
        padding: 40px 20px;
        text-align: center;
        border-radius: 0 0 15px 15px;
        box-shadow: 0 6px 12px rgba(0,0,0,0.2);
        margin-bottom: 30px;
    }
    .tsakane-title { font-size: 3.5rem; font-weight: bold; margin: 0; }
    .tsakane-subtitle { font-size: 1.5rem; margin: 10px 0 0; }
    .kpi-card {
        background: #ffffff;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
    .status-approved { background-color: #d4edda !important; color: #155724; }
    .status-pending { background-color: #fff3cd !important; color: #856404; }
    .status-processed { background-color: #cce5ff !important; color: #004085; }
    </style>
""", unsafe_allow_html=True)

# Solid orange banner
st.markdown("""
    <div class="tsakane-banner">
        <h1 class="tsakane-title">Tsakane Dashboard</h1>
        <p class="tsakane-subtitle">Joy in Every Operation • Internal Tool 🇿🇦</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("NAVIGATION")
st.sidebar.markdown("**Tsakane Operations**")

nav_options = [
    "Sundry", "Fleet Services", "Receipts", "Invoices", "MOJAPAY",
    "TWF", "Registers", "Checklists", "Circulars", "Subsistence"
]

selected_section = st.sidebar.radio("Main Sections", nav_options)

# Show placeholder for selected section (we'll expand these later)
if selected_section:
    st.sidebar.info(f"Currently viewing: **{selected_section}**")
    st.subheader(f"{selected_section} Section")
    st.write(f"Content for **{selected_section}** will go here. Tell me what features to add (table, form, status tracker, etc.)")

# Main Dashboard Overview
st.subheader("Dashboard Overview")

# KPI Cards row
kpi_cols = st.columns(4)

with kpi_cols[0]:
    st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
    st.metric("Pending Invoices", "1,342", delta="+48 today")
    st.markdown('</div>', unsafe_allow_html=True)

with kpi_cols[1]:
    st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
    st.metric("Receipts This Month", "R 2.8M", delta="↑ 12%")
    st.markdown('</div>', unsafe_allow_html=True)

with kpi_cols[2]:
    st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
    st.metric("Upcoming CIT Collections", "18", delta="Next: Tomorrow JHB")
    st.markdown('</div>', unsafe_allow_html=True)

with kpi_cols[3]:
    st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
    st.metric("Subsistence Claims Pending", "92", delta="Total: 456")
    st.markdown('</div>', unsafe_allow_html=True)

# Charts row
chart_cols = st.columns(2)

with chart_cols[0]:
    st.subheader("Transactions by Category")
    category_data = pd.DataFrame({
        "Category": ["Invoices", "Receipts", "Fleet", "Subsistence", "Sundry", "Other"],
        "Count": [850, 620, 310, 280, 190, 120]
    })
    fig_bar = px.bar(
        category_data,
        x="Category",
        y="Count",
        color="Category",
        title="Monthly Volume"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with chart_cols[1]:
    st.subheader("Status Breakdown")
    status_data = pd.DataFrame({
        "Status": ["Processed", "In Progress", "Pending Approval", "Draft"],
        "Count": [2340, 1782, 1596, 450]
    })
    fig_donut = px.pie(
        status_data,
        values="Count",
        names="Status",
        hole=0.4,
        title="Overall Status",
        color_discrete_sequence=px.colors.sequential.Oranges
    )
    st.plotly_chart(fig_donut, use_container_width=True)

# Recent Items Table
st.subheader("Recent / My Items")

recent_df = pd.DataFrame({
    "ID": ["INV-0042", "REC-1289", "FLEET-567", "SUB-091", "SUN-312"],
    "Description": ["Electricity Supplier Invoice", "Court Fees Collection", "Vehicle Maintenance Claim", "Travel Subsistence", "Sundry Payment"],
    "Amount": ["R 45,200", "R 12,500", "R 8,900", "R 3,200", "R 1,800"],
    "Status": ["Pending Approval", "Processed", "Draft", "Approved", "In Progress"]
})

# Apply color styling to Status column
def style_status(val):
    if val == "Approved":
        return "status-approved"
    elif val == "Pending Approval":
        return "status-pending"
    elif val == "Processed":
        return "status-processed"
    return ""

styled_df = recent_df.style.applymap(style_status, subset=["Status"])

st.dataframe(styled_df, use_container_width=True)

# Interactive Team Communication
st.subheader("💬 Team Communication")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome to Tsakane Dashboard! How can the team help today?"}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Type your message or question to the team..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Simple echo response for demo (in real version could integrate logic)
    st.session_state.messages.append({"role": "assistant", "content": f"Thanks for the message! Noted: '{prompt}'"})
    st.rerun()

# Footer
st.markdown("---")
st.caption("Tsakane Dashboard • Internal Use Only • Ekurhuleni / Gauteng • © 2026")
