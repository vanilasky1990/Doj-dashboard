import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta, time
from typing import Dict

# ────────────────────────────────────────────────
# Page configuration
# ────────────────────────────────────────────────
st.set_page_config(
    page_title="DOJ&CD - MC Tsakane Dashboard",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ────────────────────────────────────────────────
# Styling
# ────────────────────────────────────────────────
st.markdown("""
    <style>
    .stApp { background-color: #f9fbfd; font-family: 'Segoe UI', system-ui, sans-serif; }
    .header { 
        background-color: #FFB612; 
        color: #1a1a1a; 
        padding: 30px 20px; 
        text-align: center; 
        border-bottom: 4px solid #005c28; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .header h1 { margin: 0; font-size: 2.6rem; font-weight: 700; }
    .header h3 { margin: 10px 0 0; font-size: 1.45rem; font-weight: 400; }
    .header p { margin: 10px 0 0; font-size: 1.15rem; opacity: 0.9; }
    .status-good    { color: #006400; font-weight: bold; }
    .status-warning { color: #d2691e; font-weight: bold; }
    .status-alert   { color: #c00000; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────
# Vehicle status lookup
# ────────────────────────────────────────────────
def get_vehicle_status(vehicle_id: int) -> Dict:
    data = {
        1: {"location": "JHB Magistrate Court", "fuel": 65, "odo": 124850, "last_service": "2025-11-15", "alerts": "None"},
        2: {"location": "En Route to CPT",      "fuel": 28, "odo": 98740,  "last_service": "2025-10-20", "alerts": "Low Fuel Warning"},
        3: {"location": "Parked - PE Office",   "fuel": 92, "odo": 156320, "last_service": "2026-01-10", "alerts": "Service Due Soon"}
    }
    return data.get(vehicle_id, {"location": "Unknown", "fuel": 0, "odo": 0, "last_service": "N/A", "alerts": "N/A"})

# ────────────────────────────────────────────────
# Estimate next service (6 months OR 15,000 km rule)
# ────────────────────────────────────────────────
def estimate_next_service(status: Dict):
    last_date_str = status["last_service"]
    last_date = datetime.strptime(last_date_str, "%Y-%m-%d").date()
    
    # Time-based: 6 months from last service
    next_by_time = last_date + timedelta(days=180)  # ≈ 6 months
    
    # Km-based: 15,000 km interval
    km_since_last_service = status["odo"] % 15000
    km_remaining = 15000 - km_since_last_service
    next_by_km = f"+{km_remaining:,} km"
    
    # Show both estimates (you can later decide to show only the earlier one)
    return (
        next_by_time.strftime("%Y-%m-%d"),
        next_by_km,
        km_remaining
    )

# ────────────────────────────────────────────────
# Header
# ────────────────────────────────────────────────
st.markdown('<div class="header">', unsafe_allow_html=True)
st.image(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Coat_of_arms_of_South_Africa.svg/200px-Coat_of_arms_of_South_Africa.svg.png",
    width=160
)
st.markdown(f"""
    <h1>MC Tsakane Dashboard</h1>
    <h3>Department of Justice and Constitutional Development</h3>
    <p>Internal Use • {datetime.now().year}</p>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ────────────────────────────────────────────────
# Main tabs
# ────────────────────────────────────────────────
tab_home, tab_sundry, tab_fleet = st.tabs(["HOME", "SUNDRY", "FLEET SERVICES"])

# ================================================
# HOME TAB – Witness Fees + Fleet Analysis
# ================================================
with tab_home:
    st.subheader("Witness Fees – Monthly Expenditure Overview")

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    amounts = [45000, 62000, 38000, 75000, 51000, 89000, 42000, 67000, 93000, 55000, 48000, 72000]
    df = pd.DataFrame({"Month": months, "Amount (ZAR)": amounts})

    fig = px.bar(df, x="Month", y="Amount (ZAR)", title=f"Monthly Witness Fees Expenditure {datetime.now().year}",
                 color="Amount (ZAR)", color_continuous_scale="Greens", text_auto=",.0f")
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    # ────────────────────────────────────────────────
    # Fleet Health & Service Overview
    # ────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("🚗 Fleet Health & Service Overview")
    st.markdown("Current status and estimated next service (6 months **or** 15,000 km interval).")

    vehicles = [
        {"id": 1, "reg": "JM 45 CY GP", "short": "Vehicle 1"},
        {"id": 2, "reg": "BW 47 KG GP", "short": "Vehicle 2"},
        {"id": 3, "reg": "LR 93 VW GP", "short": "Vehicle 3"},
    ]

    summary_data = []
    for v in vehicles:
        status = get_vehicle_status(v["id"])
        next_date, next_km, km_remaining = estimate_next_service(status)
        
        days_to_service = (datetime.strptime(next_date, "%Y-%m-%d").date() - datetime.now().date()).days
        
        if days_to_service < 30 or km_remaining < 2000:
            service_status = "🟥 Due Soon"
        elif days_to_service < 90 or km_remaining < 5000:
            service_status = "🟧 Approaching"
        else:
            service_status = "🟩 On Track"

        summary_data.append({
            "Vehicle": v["reg"],
            "Location": status["location"],
            "Fuel": f"{status['fuel']}%",
            "Odometer": f"{status['odo']:,} km",
            "Last Service": status["last_service"],
            "Next Service (Date)": next_date,
            "Km Remaining": next_km,
            "Status": service_status
        })

    summary_df = pd.DataFrame(summary_data)

    # Summary Cards
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Vehicles", len(vehicles))
    avg_fuel = sum(get_vehicle_status(i)["fuel"] for i in range(1, len(vehicles)+1)) / len(vehicles)
    col2.metric("Avg Fuel Level", f"{avg_fuel:.0f}%")
    total_odo = sum(get_vehicle_status(i)["odo"] for i in range(1, len(vehicles)+1))
    col3.metric("Total Fleet Odometer", f"{total_odo:,} km")
    due_soon_count = len([r for r in summary_data if "Due Soon" in r["Status"]])
    col4.metric("Vehicles Needing Attention", due_soon_count)

    # Fleet table
    st.dataframe(
        summary_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Fuel": st.column_config.TextColumn("Fuel"),
            "Km Remaining": st.column_config.TextColumn("Km Remaining"),
            "Status": st.column_config.TextColumn("Service Status")
        }
    )

    st.caption("Next service is triggered by whichever comes first: **6 months** from last service or **15,000 km** since last service.")

# ────────────────────────────────────────────────
# SUNDRY tab (unchanged)
# ────────────────────────────────────────────────
with tab_sundry:
    st.subheader("Witness Fees Register")

    sample_data = {
        "Date": ["2026-01-15", "2026-01-22", "2026-02-05", "2026-02-10", "2026-02-18"],
        "Witness Name": ["A. Nkosi", "B. Mthembu", "C. v/d Merwe", "D. Pillay", "E. Sithole"],
        "Case Number": ["JHB/2026/001", "CPT/2026/045", "DBN/2026/112", "JHB/2026/078", "PE/2026/023"],
        "Amount Paid (ZAR)": [1200.00, 850.00, 1500.00, 950.00, 1100.00],
        "Status": ["Paid", "Pending Approval", "Paid", "Awaiting Receipt", "Paid"],
        "Court/Office": ["JHB Magistrate", "CPT High", "DBN Regional", "JHB High", "PE Magistrate"]
    }

    df = pd.DataFrame(sample_data)
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

    total_spent = edited_df["Amount Paid (ZAR)"].sum()
    pending = edited_df[edited_df["Status"].isin(["Pending Approval", "Awaiting Receipt"])]["Amount Paid (ZAR)"].sum()

    col1, col2 = st.columns(2)
    col1.metric("Total Spent", f"R {total_spent:,.2f}")
    col2.metric("Pending / Awaiting", f"R {pending:,.2f}")

# ────────────────────────────────────────────────
# FLEET SERVICES tab (your existing detailed view)
# ────────────────────────────────────────────────
with tab_fleet:
    st.subheader("Fleet Services – Gauteng Region")
    st.markdown("Detailed vehicle logs, refuelling and toll slip entry.")

    # ... paste your full fleet tab code here (with the forms, time column, multiple toll rows support, etc.) ...
    # For brevity I'm not repeating the entire 200+ lines again — just keep your previous working version
    st.info("Switch here for detailed trip logs, fuel slips and toll entries (multiple tolls per day supported).")

# Footer
st.markdown("---")
st.caption(f"© Department of Justice and Constitutional Development • {datetime.now().year} • Internal use only")
