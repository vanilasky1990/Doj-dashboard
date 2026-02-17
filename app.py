# app.py - DOJ&CD Internal Dynamic Dashboard
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

# Custom CSS - simplified single-color header + clean styling
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .header { 
        background-color: #002395;  /* Solid deep navy blue - professional & trustworthy */
        color: white; 
        padding: 25px 20px; 
        text-align: center; 
        border-radius: 0 0 12px 12px; 
        margin-bottom: 25px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.15);
    }
    .header h1 { margin: 0; font-size: 2.2rem; }
    .header h3 { margin: 8px 0 0; font-size: 1.3rem; font-weight: 400; }
    .header p { margin: 8px 0 0; font-size: 1rem; opacity: 0.9; }
    .sidebar .sidebar-content { background-color: #001a7a; color: white; }  /* Darker blue sidebar */
    .stButton>button { 
        background-color: #FFB612; 
        color: black; 
        border: none; 
        font-weight: bold; 
        padding: 10px 16px;
    }
    .card { 
        background: white; 
        padding: 20px; 
        border-radius: 10px; 
        box-shadow: 0 4px 8px rgba(0,0,0,0.1); 
        margin-bottom: 20px; 
        border-left: 5px solid #002395; 
    }
    </style>
""", unsafe_allow_html=True)

# Simplified Header - single solid color
st.markdown("""
    <div class="header">
        <h1>Department of Justice and Constitutional Development</h1>
        <h3>ACCESS TO JUSTICE FOR ALL</h3>
        <p>Internal Operational Dashboard • Republic of South Africa 🇿🇦</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar Navigation - mirroring your original menu
st.sidebar.title("NAVIGATION")
st.sidebar.markdown("**Home**")

nav_options = [
    "Sundry", "Fleet Services", "Receipts", "Invoices", "MOJAPAY",
    "TWF", "Registers", "Checklists", "Circulars", "Subsistence"
]

selected = st.sidebar.radio("Main Sections", nav_options, index=0)

# Placeholder for selected section (we'll build these one by one)
if selected != "Home":
    st.info(f"Section: **{selected}** – Coming soon! Let me know what content to add here first (e.g. table, form, status list, chart).")

# Main Content Area - Key Service Providers (like your Fidelity & FNB panels)
st.subheader("Key Service Providers")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.image("https://via.placeholder.com/150x80/00A651/FFFFFF?text=Fidelity+CIT", use_column_width=True)
    st.markdown("**FIDELITY CIT**")
    st.markdown("Cash in Transit Services")
    st.markdown("dojservices@fidelity-services.com")
    if st.button("Request Collection / View Schedule", key="fidelity"):
        st.success("Collection request form opens here (to be built)...")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.image("https://via.placeholder.com/150x80/FFB612/000000?text=FNB", use_column_width=True)
    st.markdown("**FNB CHANGE REQUEST**")
    st.markdown("Bank Change / Balancing Requests")
    st.markdown("DLFNBSelbyBalancing@fnb.co.za")
    if st.button("Submit Change Request", key="fnb"):
        st.success("Change request form opens here (to be built)...")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**Other Services**")
    st.markdown("- Sundry Payments\n- Fleet & Subsistence\n- More sections coming...")
    st.markdown('</div>', unsafe_allow_html=True)

# Quick Stats / Overview (placeholder - expand later)
st.subheader("Quick Overview")
col_a, col_b, col_c = st.columns(3)
col_a.metric("Pending Invoices", "42", "+5 today")
col_b.metric("Receipts This Month", "R 1.2M", "↑ 8%")
col_c.metric("Next CIT Collection", "Tomorrow", "JHB Office")

# Interactive Communication - Team Chat (real-time in browser session)
st.subheader("💬 Team Communication")

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {"user": "Admin", "time": "15:45", "text": "Welcome to the DOJ&CD dashboard!"},
        {"user": "Finance", "time": "15:50", "text": "Looking forward to tracking invoices and CIT better."}
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
st.caption("DOJ&CD Internal Tool • Confidential • © 2026")
