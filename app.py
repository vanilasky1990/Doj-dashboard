# app.py - DOJ&CD Dashboard: HOME + SUNDRY + FLEET SERVICES (with vehicle sub-tabs)
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="DOJ&CD Internal Dashboard",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Clean CSS with DOJ&CD green scheme
st.markdown("""
    <style>
    .stApp { background-color: #f9fbfd; font-family: 'Helvetica Neue', Arial, sans-serif; }
    .header { background-color: #005c28; color: white; padding: 30px 20px; text-align: center; margin-bottom: 30px; border-bottom: 4px solid #FFB612; }
    .header-logo { max-width: 180px; margin-bottom: 15px; }
    .header h1 { margin: 0; font-size: 2.4rem; font-weight: 600; }
    .header h3 { margin: 10px 0 0; font-size: 1.4rem; font-weight: 400; }
    .header p { margin: 10px 0 0; font-size: 1.1rem; opacity: 0.95; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background-color: #ffffff; border-bottom: 2px solid #e0e0e0; padding: 0 20px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #f0f4f8; border-radius: 8px 8px 0 0; font-size: 1.1rem; font-weight: 500; color: #333; }
    .stTabs [aria-selected="true"] { background-color: #ffffff !important; border-bottom: 3px solid #005c28; color: #005c28 !important; }
    .stButton > button { background-color: #FFB612; color: black; border: none; font-weight: bold; padding: 10px 20px; border-radius: 6px; }
    .stButton > button:hover { background-color: #e6a000; }
    .status-good { color: green; font-weight: bold; }
    .status-warning { color: orange; font-weight: bold; }
    .status-alert { color: red; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# Header with Logo
st.markdown('<div class="header">', unsafe_allow_html=True)
st.image(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Coat_of_arms_of_South_Africa.svg/200px-Coat_of_arms_of_South_Africa.svg.png",
    use_column_width=False
)
st.markdown("""
    <h1>Department of Justice and Constitutional Development</h1>
    <h3>ACCESS TO JUSTICE FOR ALL</h3>
    <p>Internal Dashboard • Republic of South Africa 🇿🇦</p>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Main Tabs: HOME, SUNDRY, FLEET SERVICES
tab_home, tab_sundry, tab_fleet = st.tabs(["HOME", "SUNDRY", "FLEET SERVICES"])

# HOME tab (unchanged - monthly chart)
with tab_home:
    st.markdown("<h2 style='text-align: center; color: #005c28; margin-top: 30px;'>Witness Fees Expenditure Overview</h2>", unsafe_allow_html=True)
    
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    amounts = [45000, 62000, 38000, 75000, 51000, 89000, 42000, 67000, 93000, 55000, 48000, 72000]
    df_chart = pd.DataFrame({"Month": months, "Amount Spent (ZAR)": amounts})
    
    fig = px.bar(df_chart, x="Month", y="Amount Spent (ZAR)", title="Monthly Witness Fees Expenditure (Current Year)",
                 color="Amount Spent (ZAR)", color_continuous_scale="Greens", text_auto=True)
    fig.update_layout(xaxis_title="Month", yaxis_title="Amount (ZAR)", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<h3 style='text-align: center; color: #005c28;'>View Detailed Witness Fees Table</h3>", unsafe_allow_html=True)
    if st.button("Open Witness Fees Table (SUNDRY Section)"):
        st.success("Switch to the **SUNDRY** tab above.")

# SUNDRY tab (witness fees table - unchanged)
with tab_sundry:
    st.header("Witness Fees Table")
    sample_data = {
        "Date": ["2026-01-15", "2026-01-22", "2026-02-05", "2026-02-10", "2026-02-18"],
        "Witness Name": ["A. Nkosi", "B. Mthembu", "C. van der Merwe", "D. Pillay", "E. Sithole"],
        "Case Number": ["JHB/2026/001", "CPT/2026/045", "DBN/2026/112", "JHB/2026/078", "PE/2026/023"],
        "Amount Paid (ZAR)": [1200.00, 850.00, 1500.00, 950.00, 1100.00],
        "Status": ["Paid", "Pending Approval", "Paid", "Awaiting Receipt", "Paid"],
        "Court/Office": ["Johannesburg Magistrate", "Cape Town High", "Durban Regional", "Johannesburg High", "Port Elizabeth Magistrate"]
    }
    df_table = pd.DataFrame(sample_data)
    edited_df = st.data_editor(df_table, num_rows="dynamic", use_container_width=True)
    total_spent = edited_df["Amount Paid (ZAR)"].sum()
    st.metric("Total Spent (from table)", f"R {total_spent:,.2f}")

# FLEET SERVICES tab with 3 vehicle sub-tabs
with tab_fleet:
    st.header("Fleet Services")
    st.markdown("Vehicle tracking and status overview for DOJ&CD fleet in Gauteng.")

    # Sub-tabs for each vehicle
    v1, v2, v3 = st.tabs([
        "Vehicle 1 (JM 45 CY GP)",
        "Vehicle 2 (BW 47 KG GP)",
        "Vehicle 3 (LR 93 VW GP)"
    ])

    # Dummy data function for consistency
    def get_vehicle_status(vehicle_id):
        statuses = {
            1: {"location": "JHB Magistrate Court", "fuel": 65, "odo": 124850, "last_service": "2025-11-15", "alerts": "None"},
            2: {"location": "En Route to CPT", "fuel": 28, "odo": 98740, "last_service": "2025-10-20", "alerts": "Low Fuel Warning"},
            3: {"location": "Parked - PE Office", "fuel": 92, "odo": 156320, "last_service": "2026-01-10", "alerts": "Service Due Soon"}
        }
        return statuses.get(vehicle_id, {"location": "Unknown", "fuel": 0, "odo": 0, "last_service": "N/A", "alerts": "N/A"})

    # Vehicle 1
    with v1:
        status = get_vehicle_status(1)
        st.subheader("Vehicle 1: JM 45 CY GP")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Current Location:** {status['location']}")
            st.markdown(f"**Fuel Level:** {status['fuel']}%")
            st.markdown(f"**Odometer:** {status['odo']:,} km")
        with col2:
            st.markdown(f"**Last Service:** {status['last_service']}")
            alert_class = "status-good" if "None" in status['alerts'] else "status-warning" if "Low" in status['alerts'] else "status-alert"
            st.markdown(f"**Alerts:** <span class='{alert_class}'>{status['alerts']}</span>", unsafe_allow_html=True)

        # Dummy daily mileage chart
        dates = [datetime.now().date() - timedelta(days=i) for i in range(6, -1, -1)]
        mileage = [45, 120, 0, 85, 60, 30, 95]
        df_mileage = pd.DataFrame({"Date": dates, "Daily Mileage (km)": mileage})
        fig = px.line(df_mileage, x="Date", y="Daily Mileage (km)", title="Last 7 Days Mileage")
        st.plotly_chart(fig, use_container_width=True)

        # Recent trips table (editable)
        st.subheader("Recent Trips / Logs")
        trips_data = pd.DataFrame({
            "Date": ["2026-02-15", "2026-02-10", "2026-02-05"],
            "Driver": ["J. Smith", "A. Nkosi", "M. Botha"],
            "Purpose": ["Court Transfer", "Site Visit", "Maintenance"],
            "Start Odo": [124500, 124200, 123900],
            "End Odo": [124850, 124400, 124150],
            "Distance (km)": [350, 200, 250],
            "Notes": ["", "Fuel added", ""]
        })
        st.data_editor(trips_data, num_rows="dynamic", use_container_width=True)

    # Vehicle 2 (similar structure)
    with v2:
        status = get_vehicle_status(2)
        st.subheader("Vehicle 2: BW 47 KG GP")
        # ... (repeat similar columns, chart, table with different dummy data)
        st.info("Vehicle 2 details (similar layout) - customize as needed.")

    # Vehicle 3
    with v3:
        status = get_vehicle_status(3)
        st.subheader("Vehicle 3: LR 93 VW GP")
        # ... (repeat layout)
        st.info("Vehicle 3 details (similar layout) - customize as needed.")

# Footer
st.markdown("---")
st.caption("© Department of Justice and Constitutional Development • 2026")
