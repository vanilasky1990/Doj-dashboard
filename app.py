# app.py - DOJ&CD Modern Dashboard (Sleek Nav + Sidebar)
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict

# ────────────────────────────────────────────────
# Page config + modern theme
# ────────────────────────────────────────────────
st.set_page_config(
    page_title="DOJ&CD Dashboard • MC Tsakane",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"  # ← changed to expanded for modern feel
)

# ────────────────────────────────────────────────
# Sleek CSS (updated with better tabs + sidebar + cards)
# ────────────────────────────────────────────────
st.markdown("""
    <style>
    /* General */
    .stApp { background-color: #f8fafc; font-family: 'Segoe UI', system-ui, sans-serif; }
    
    /* Header */
    .header {
        background: linear-gradient(135deg, #005c28 0%, #00451f 100%);
        color: white;
        padding: 2.2rem 2rem;
        border-radius: 0 0 16px 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
        text-align: center;
        margin-bottom: 1.8rem;
    }
    .header h1 { margin: 0; font-size: 2.6rem; font-weight: 700; letter-spacing: -0.5px; }
    .header h3 { margin: 0.6rem 0 0; font-size: 1.35rem; font-weight: 400; opacity: 0.95; }

    /* Tabs - Sleek modern look */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.6rem;
        background: transparent;
        border-bottom: none;
        padding: 0.6rem 1.5rem;
        justify-content: center;
    }
    .stTabs [data-baseweb="tab"] {
        height: 3.1rem;
        background: rgba(255,255,255,0.9);
        border-radius: 12px 12px 0 0;
        font-size: 1.05rem;
        font-weight: 600;
        color: #444;
        border: 1px solid #e2e8f0;
        border-bottom: none;
        padding: 0 1.8rem;
        transition: all 0.25s ease;
    }
    .stTabs [aria-selected="true"] {
        background: white !important;
        color: #005c28 !important;
        border-bottom: 4px solid #005c28 !important;
        box-shadow: 0 -3px 12px rgba(0,92,40,0.12);
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: #f1f5f9;
        transform: translateY(-2px);
    }

    /* Cards */
    .card {
        background: white;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        padding: 1.6rem;
        margin-bottom: 1.5rem;
        border: 1px solid #e2e8f0;
    }

    /* Status badges */
    .status-good  { color: #16a34a; font-weight: 600; }
    .status-warning { color: #ea580c; font-weight: 600; }
    .status-alert   { color: #dc2626; font-weight: 600; }

    /* Sidebar tweaks */
    section[data-testid="stSidebar"] {
        background: white;
        border-right: 1px solid #e2e8f0;
        box-shadow: 2px 0 12px rgba(0,0,0,0.06);
    }
    </style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────
# Vehicle status function
# ────────────────────────────────────────────────
def get_vehicle_status(vehicle_id: int) -> Dict[str, any]:
    statuses = {
        1: {"location": "JHB Magistrate Court", "fuel": 65, "odo": 124850, "last_service": "2025-11-15", "alerts": "None"},
        2: {"location": "En Route to CPT", "fuel": 28, "odo": 98740, "last_service": "2025-10-20", "alerts": "Low Fuel Warning"},
        3: {"location": "Parked - PE Office", "fuel": 92, "odo": 156320, "last_service": "2026-01-10", "alerts": "Service Due Soon"}
    }
    return statuses.get(vehicle_id, {"location": "Unknown", "fuel": 0, "odo": 0, "last_service": "N/A", "alerts": "N/A"})

# ────────────────────────────────────────────────
# Sidebar – modern quick access + global controls
# ────────────────────────────────────────────────
with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Coat_of_arms_of_South_Africa.svg/200px-Coat_of_arms_of_South_Africa.svg.png",
        width=140,
        caption="DOJ&CD"
    )
    st.title("MC Tsakane")
    st.caption(f"Internal Dashboard • {datetime.now().year}")

    st.divider()

    st.subheader("Quick Navigation")
    current_year = datetime.now().year

    # You can later make this control tab selection via session state
    st.radio(
        "Main Section",
        options=["Home Overview", "Witness Fees (Sundry)", "Fleet Services"],
        key="main_nav",
        horizontal=False
    )

    st.divider()
    st.info("Logged in as: Admin User\nEdenvale, Gauteng")

# ────────────────────────────────────────────────
# Header (now slimmer + gradient)
# ────────────────────────────────────────────────
st.markdown('<div class="header">', unsafe_allow_html=True)
st.markdown(f"""
    <h1>Department of Justice Dashboard</h1>
    <h3>Access to Justice for All</h3>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ────────────────────────────────────────────────
# Main sleek tabs
# ────────────────────────────────────────────────
tab_home, tab_sundry, tab_fleet = st.tabs([
    "🏠 Home",
    "📊 Sundry – Witness Fees",
    "🚗 Fleet Services"
])

# ────────────────────────────────────────────────
# HOME tab
# ────────────────────────────────────────────────
with tab_home:
    st.markdown("<h2 style='color:#005c28;text-align:center;'>Witness Fees – Monthly Overview</h2>", unsafe_allow_html=True)
    
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    amounts = [45000, 62000, 38000, 75000, 51000, 89000, 42000, 67000, 93000, 55000, 48000, 72000]
    df = pd.DataFrame({"Month": months, "Amount (ZAR)": amounts})
    
    fig = px.bar(df, x="Month", y="Amount (ZAR)", title=f"{current_year} Expenditure Trend",
                 color="Amount (ZAR)", color_continuous_scale="Greens_r", text_auto=",.0f")
    fig.update_layout(showlegend=False, xaxis_title=None)
    st.plotly_chart(fig, use_container_width=True, key="home_chart")

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("Quick action → Switch to **Sundry** tab for full table & editing.")
    if st.button("View Detailed Witness Table", type="primary"):
        st.switch_page("app.py")  # placeholder – later use multi-page
    st.markdown("</div>", unsafe_allow_html=True)

# ────────────────────────────────────────────────
# SUNDRY tab
# ────────────────────────────────────────────────
with tab_sundry:
    st.header("Witness Fees Register")
    # ... keep your existing table code here ...
    # (insert your sample_data, data_editor, metrics – same as before)
    # Suggestion: wrap in <div class="card"> ... </div> for nicer look

# ────────────────────────────────────────────────
# FLEET tab – keep your loop structure, just add card wrappers
# ────────────────────────────────────────────────
with tab_fleet:
    st.header("Fleet Management – Gauteng")
    
    vehicle_list = [...]  # your existing list
    
    vehicle_tabs = st.tabs([f"{v['name']} ({v['reg']})" for v in vehicle_list])
    
    for idx, tab in enumerate(vehicle_tabs):
        # ... your existing per-vehicle content ...
        # Suggestion: wrap status + chart + table in <div class="card">...</div>

# Footer
st.markdown("---")
st.caption(f"© Department of Justice and Constitutional Development • {current_year} • Internal Use Only")
