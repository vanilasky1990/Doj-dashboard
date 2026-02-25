# app.py - DOJ&CD Dashboard: HOME + SUNDRY + FLEET SERVICES (with vehicle sub-tabs)
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="MC Tsakane - Dashboard",
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
    <h1>My Dashboard</h1>
    <h3>ACCESS TO JUSTICE FOR ALL</h3>
    <p>Internal Dashboard</p>
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
    st.header("Fleet Services – Gauteng DOJ&CD")
    st.markdown("Real-time vehicle tracking, fuel, service status & trip logging.")

    vehicle_list = [
        {"id": 1, "reg": "JM 45 CY GP", "name": "Vehicle 1"},
        {"id": 2, "reg": "BW 47 KG GP", "name": "Vehicle 2"},
        {"id": 3, "reg": "LR 93 VW GP", "name": "Vehicle 3"},
    ]

    # Create sub-tabs dynamically
    tab_names = [f"{v['name']} ({v['reg']})" for v in vehicle_list]
    vehicle_tabs = st.tabs(tab_names)

    for idx, tab in enumerate(vehicle_tabs):
        vehicle = vehicle_list[idx]
        v_id = vehicle["id"]
        status = get_vehicle_status(v_id)

        with tab:
            st.subheader(f"{vehicle['name']}: {vehicle['reg']}")

            # Status cards in columns
            col1, col2, col3 = st.columns([2, 2, 1.2])
            with col1:
                st.markdown(f"**📍 Current Location**  \n{status['location']}")
            with col2:
                fuel_color = "green" if status['fuel'] > 50 else "orange" if status['fuel'] > 20 else "red"
                st.markdown(f"**⛽ Fuel Level**  \n<span style='color:{fuel_color};font-weight:bold;'>{status['fuel']}%</span>", unsafe_allow_html=True)
                st.markdown(f"**🛣 Odometer**  \n{status['odo']:,} km")
            with col3:
                st.markdown(f"**🛠 Last Service**  \n{status['last_service']}")
                if "None" in status['alerts']:
                    cls = "status-good"
                elif "Low" in status['alerts']:
                    cls = "status-warning"
                else:
                    cls = "status-alert"
                st.markdown(f"**Alerts**  \n<span class='{cls}'>{status['alerts']}</span>", unsafe_allow_html=True)

            # Mileage chart (you can later parameterize per vehicle)
            dates = [datetime.now().date() - timedelta(days=i) for i in range(13, -1, -1)]   # last 14 days example
            mileage = [45, 0, 120, 85, 0, 60, 30, 95, 110, 20, 75, 0, 55, 140]              # dummy – replace with real data
            df_mileage = pd.DataFrame({"Date": dates, "Daily Mileage (km)": mileage[-len(dates):]})
            fig = px.line(df_mileage, x="Date", y="Daily Mileage (km)", title="Last 14 Days Mileage Trend")
            fig.update_traces(line_color='#005c28')
            st.plotly_chart(fig, use_container_width=True)

            # Recent trips (per vehicle – in real app load from DB/CSV)
            st.subheader("Recent Trips & Logs")
            # Example – customize per vehicle later
            trips_data = pd.DataFrame({
                "Date": ["2026-02-20", "2026-02-15", "2026-02-10", "2026-02-05"],
                "Driver": ["J. Smith", "A. Nkosi", "M. Botha", "S. Naidoo"],
                "Purpose": ["Court Appearance", "Site Inspection", "Maintenance", "Transfer"],
                "Start Odo": [124600, 124500, 124200, 123900],
                "End Odo": [124950, 124850, 124400, 124150],
                "Distance (km)": [350, 350, 200, 250],
                "Fuel Used (L)": [48.2, 47.5, 26.8, 34.1],
                "Notes": ["", "Refuelled 40L", "", "Tyre pressure checked"]
            })
            edited_trips = st.data_editor(trips_data, num_rows="dynamic", use_container_width=True)

            # Quick stats from edited table
            if not edited_trips.empty:
                total_km = edited_trips["Distance (km)"].sum()
                st.metric("Total Distance (recent trips)", f"{total_km:,} km")
# Footer
st.markdown("---")
st.caption("© Department of Justice and Constitutional Development • 2026")
