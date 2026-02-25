import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
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
# Styling - solid orange header
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
# Header - solid orange
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

# ────────────────────────────────────────────────
# HOME tab
# ────────────────────────────────────────────────
with tab_home:
    st.subheader("Witness Fees – Monthly Expenditure Overview")

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    amounts = [45000, 62000, 38000, 75000, 51000, 89000, 42000, 67000, 93000, 55000, 48000, 72000]

    df = pd.DataFrame({"Month": months, "Amount (ZAR)": amounts})

    fig = px.bar(
        df,
        x="Month",
        y="Amount (ZAR)",
        title=f"Monthly Witness Fees Expenditure {datetime.now().year}",
        color="Amount (ZAR)",
        color_continuous_scale="Greens",
        text_auto=",.0f"
    )
    fig.update_layout(showlegend=False)

    st.plotly_chart(fig, use_container_width=True)

    if st.button("View detailed witness fees table"):
        st.info("Please switch to the **SUNDRY** tab above")

# ────────────────────────────────────────────────
# SUNDRY tab
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

with tab_fleet:
    st.subheader("Fleet Services – Gauteng Region")

    vehicles = [
        {"id": 1, "reg": "JM 45 CY GP", "short": "Vehicle 1"},
        {"id": 2, "reg": "BW 47 KG GP", "short": "Vehicle 2"},
        {"id": 3, "reg": "LR 93 VW GP", "short": "Vehicle 3"},
    ]

    vehicle_tabs = st.tabs([f"{v['short']} ({v['reg']})" for v in vehicles])

    for idx, tab in enumerate(vehicle_tabs):
        veh = vehicles[idx]
        vid = veh["id"]
        reg = veh["reg"]
        status = get_vehicle_status(vid)

        with tab:
            st.markdown(f"### {reg}")

            c1, c2, c3 = st.columns([2, 2, 1.4])

            c1.markdown(f"**Current location**  \n{status['location']}")

            fuel_color = "green" if status["fuel"] > 50 else "orange" if status["fuel"] > 20 else "red"
            with c2:
                c2.markdown(f"**Fuel level**  \n<span style='color:{fuel_color}'>{status['fuel']}%</span>", unsafe_allow_html=True)
                c2.progress(status["fuel"] / 100)
                c2.markdown(f"**Odometer**  \n{status['odo']:,} km")

            alert_cls = "status-good" if "None" in status["alerts"] else "status-warning" if "Low" in status["alerts"] else "status-alert"
            c3.markdown(f"**Last service**  \n{status['last_service']}")
            c3.markdown(f"**Alerts**  \n<span class='{alert_cls}'>{status['alerts']}</span>", unsafe_allow_html=True)

            # ────────────────────────────────────────────────
            # Mileage chart – ADD UNIQUE KEY HERE
            dates = [datetime.now().date() - timedelta(days=x) for x in range(13, -1, -1)]
            km_list = [45, 0, 120, 85, 0, 60, 30, 95, 110, 20, 75, 0, 55, 140]  # dummy – same for all now
            df_mileage = pd.DataFrame({"Date": dates, "Daily km": km_list})
            fig = px.line(df_mileage, x="Date", y="Daily km", title="Last 14 days mileage")
            fig.update_traces(line_color="#005c28")

            st.plotly_chart(
                fig,
                use_container_width=True,
                key=f"mileage_chart_vehicle_{vid}"   # ← This fixes the duplicate ID
            )

            # Trips log (add key here too for safety)
            st.subheader("Recent trips")
            trips_data = pd.DataFrame({
                "Date":      ["2026-02-20", "2026-02-15", "2026-02-10", "2026-02-05"],
                "Driver":    ["J. Smith", "A. Nkosi", "M. Botha", "S. Naidoo"],
                "Purpose":   ["Court appearance", "Site inspection", "Maintenance", "Transfer"],
                "Start Odo": [124600, 124500, 124200, 123900],
                "End Odo":   [124950, 124850, 124400, 124150],
                "Distance":  [350, 350, 200, 250],
            })
            st.data_editor(
                trips_data,
                num_rows="dynamic",
                use_container_width=True,
                key=f"trips_log_vehicle_{vid}"       # ← optional but recommended
            )
# ────────────────────────────────────────────────
# Footer
# ────────────────────────────────────────────────
st.markdown("---")
st.caption(f"© Department of Justice and Constitutional Development • {datetime.now().year} • Internal use only")
