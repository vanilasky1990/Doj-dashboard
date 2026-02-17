# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Page config - wide layout for dashboard feel
st.set_page_config(
    page_title="DOJ&CD Internal Dashboard",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for branding (orange accents, SA flag colors, government look)
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .header { 
        background: linear-gradient(to right, #002395, #006600, #FFB612); .
        color: white; padding: 20px; text-align: center; border-radius: 10px; 
        margin-bottom: 20px;
    }
    .sidebar .sidebar-content { background-color: #002395; color: white; }
    .stButton>button { background-color: #FFB612; color: black; border: none; }
    .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# Header Banner
st.markdown("""
    <div class="header">
        <h1>Department of Justice and Constitutional Development</h1>
        <h3>ACCESS TO JUSTICE FOR ALL</h3>
        <p>Internal Operational Dashboard • Republic of South Africa 🇿🇦</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar Navigation - mirroring your menu
st.sidebar.title("NAVIGATION")
st.sidebar.markdown("**Home**")

nav_options = [
    "Sundry", "Fleet Services", "Receipts", "Invoices", "MOJAPAY",
    "TWF", "Registers", "Checklists", "Circulars", "Subsistence"
]

selected = st.sidebar.radio("Main Sections", nav_options, index=0)  # default to first

# Placeholder message when section selected (we'll replace with real content)
if selected != "Home":  # we'll add Home later
    st.info(f"Section: **{selected}** – Coming soon! Tell me what to add here first (e.g. table, form, chart, status tracker).")

# Main Content Area - Partner Cards (like your Fidelity & FNB panels)
st.subheader("Key Service Providers")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.image("https://via.placeholder.com/150x80/00A651/FFFFFF?text=Fidelity+CIT", use_column_width=True)  # replace with real logo if you have URL
    st.markdown("**FIDELITY CIT**")
    st.markdown("Cash in Transit Services")
    st.markdown("dojservices@fidelity-services.com")
    if st.button("Request Collection / View Schedule", key="fidelity"):
        st.success("Collection request form would open here...")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.image("https://via.placeholder.com/150x80/FFB612/000000?text=FNB", use_column_width=True)  # placeholder
    st.markdown("**FNB CHANGE REQUEST**")
    st.markdown("Bank Change / Balancing Requests")
    st.markdown("DLFNBSelbyBalancing@fnb.co.za")
    if st.button("Submit Change Request", key="fnb"):
        st.success("Change request form would open here...")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**Other Services**")
    st.markdown("- Sundry Payments\n- Fleet & Subsistence\n- More coming...")
    st.markdown('</div>', unsafe_allow_html=True)

# Quick Stats / Overview (expand later)
st.subheader("Quick Overview")
col_a, col_b, col_c = st.columns(3)
col_a.metric("Pending Invoices", "42", "+5 today")
col_b.metric("Receipts This Month", "R 1.2M", "↑ 8%")
col_c.metric("Next CIT Collection", "Tomorrow", "JHB Office")

# Interactive Communication - Basic Team Chat (real-time in session)
st.subheader("💬 Team Communication")

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {"user": "Admin", "time": "15:45", "text": "Welcome to the new dashboard! Start adding your sections."},
        {"user": "Finance", "time": "15:50", "text": "Need to track Fidelity collections better..."}
    ]

for msg in st.session_state.chat_messages:
    with st.chat_message(msg["user"]):
        st.caption(f"{msg['user']} • {msg['time']}")
        st.write(msg["text"])

if prompt := st.chat_input("Type a message or query for the team..."):
    st.session_state.chat_messages.append({
        "user": "You",
        "time": datetime.now().strftime("%H:%M"),
        "text": prompt
    })
    st.rerun()

# Footer
st.markdown("---")
st.caption("DOJ&CD Internal Tool • Built with Streamlit • Confidential • © 2026")
