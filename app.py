import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta, time
import io
import os
import sqlite3
import shutil
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ────────────────────────────────────────────────
# Configuration
# ────────────────────────────────────────────────
VEHICLES = [
    {"id": 1, "reg": "LR 93 VW GP", "short": "Vehicle 1"},
    {"id": 2, "reg": "BW 47 KG GP", "short": "Vehicle 2"},
    {"id": 3, "reg": "JM 45 CY GP", "short": "Vehicle 3"}
]

DRIVERS = ["MF Neludi", "SA Ndlela", "S Mothoa", "J Ndou", "FV Mkhwanazi", "ML Kgakatsi"]

APP_SETTINGS = {
    "app_name": "DOJ&CD - MC Tsakane Dashboard",
    "rows_per_page": 20,
    "max_daily_distance": 2000,
    "backup_enabled": True,
    "backup_interval_days": 7
}

ALERT_THRESHOLDS = {
    "fuel_low": 20,
    "service_km_warning": 5000,
    "service_days_warning": 90,
    "service_km_due": 2000,
    "service_days_due": 30
}

# ────────────────────────────────────────────────
# Page config
# ────────────────────────────────────────────────
st.set_page_config(
    page_title=APP_SETTINGS["app_name"],
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ────────────────────────────────────────────────
# Simple Authentication
# ────────────────────────────────────────────────
def check_password():
    """Simple password check for demo"""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    
    if not st.session_state["authenticated"]:
        st.title("🔐 Login - DOJ&CD Fleet Management")
        with st.form("login_form"):
            password = st.text_input("Password", type="password")
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                submitted = st.form_submit_button("Login", use_container_width=True)
            
            if submitted:
                if password == "admin123":  # Demo password
                    st.session_state["authenticated"] = True
                    st.session_state["user"] = "admin"
                    st.rerun()
                else:
                    st.error("❌ Invalid password")
        
        st.info("👆 Demo password: admin123")
        return False
    return True

# ────────────────────────────────────────────────
# Database Functions
# ────────────────────────────────────────────────
def init_database():
    """Initialize SQLite database"""
    try:
        conn = sqlite3.connect('fleet_management.db')
        c = conn.cursor()
        
        # Create trips table
        c.execute('''CREATE TABLE IF NOT EXISTS trips
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      vehicle_id INTEGER,
                      date TEXT,
                      time TEXT,
                      driver TEXT,
                      purpose TEXT,
                      start_odo INTEGER,
                      end_odo INTEGER,
                      distance INTEGER,
                      fuel_added REAL,
                      fuel_cost REAL,
                      odo_at_refuel INTEGER,
                      toll_amount REAL,
                      toll_plaza_notes TEXT,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        # Create audit log table
        c.execute('''CREATE TABLE IF NOT EXISTS audit_log
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user TEXT,
                      action TEXT,
                      vehicle_id INTEGER,
                      details TEXT,
                      timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Database init error: {e}")
        return False

# Initialize database
init_database()

# ────────────────────────────────────────────────
# Data Persistence
# ────────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_trips(vid: int) -> pd.DataFrame:
    """Load trips from CSV file"""
    file_path = f"trips_vehicle_{vid}.csv"
    columns = [
        "Date", "Time", "Driver", "Purpose", "Start Odo", "End Odo", "Distance (km)",
        "Fuel Added (L)", "Fuel Cost (R)", "Odo at Refuel", "Toll Amount (R)", "Toll Plaza / Notes"
    ]
    
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path, parse_dates=["Date"])
            # Ensure all columns exist
            for col in columns:
                if col not in df.columns:
                    df[col] = pd.NA
            return df[columns]
        except:
            return pd.DataFrame(columns=columns)
    else:
        return pd.DataFrame(columns=columns)

def save_trips(vid: int, df: pd.DataFrame):
    """Save trips to CSV file"""
    file_path = f"trips_vehicle_{vid}.csv"
    df.to_csv(file_path, index=False)
    st.cache_data.clear()

def log_audit(action, vehicle_id=None, details=None):
    """Log user actions"""
    try:
        conn = sqlite3.connect('fleet_management.db')
        c = conn.cursor()
        user = st.session_state.get("user", "unknown")
        c.execute('''INSERT INTO audit_log (user, action, vehicle_id, details)
                     VALUES (?, ?, ?, ?)''', (user, action, vehicle_id, str(details)[:200]))
        conn.commit()
        conn.close()
    except:
        pass

# ────────────────────────────────────────────────
# Vehicle Status
# ────────────────────────────────────────────────
def get_vehicle_status(vehicle_id: int) -> dict:
    """Get current vehicle status"""
    # Try to get latest odometer from trips
    trips = load_trips(vehicle_id)
    latest_odo = 0
    if not trips.empty and 'End Odo' in trips.columns:
        valid_odos = pd.to_numeric(trips[trips['End Odo'] > 0]['End Odo'], errors='coerce')
        if not valid_odos.empty:
            latest_odo = int(valid_odos.max())
    
    data = {
        1: {"location": "JHB Magistrate Court", "fuel": 65, "odo": max(124850, latest_odo), 
            "last_service": "2025-11-15", "alerts": "None"},
        2: {"location": "En Route to CPT", "fuel": 28, "odo": max(98740, latest_odo), 
            "last_service": "2025-10-20", "alerts": "Low Fuel Warning"},
        3: {"location": "Parked - PE Office", "fuel": 92, "odo": max(156320, latest_odo), 
            "last_service": "2026-01-10", "alerts": "Service Due Soon"}
    }
    return data.get(vehicle_id, {"location": "Unknown", "fuel": 0, "odo": 0, 
                                 "last_service": "N/A", "alerts": "N/A"})

def estimate_next_service(status: dict):
    """Estimate next service date and km remaining"""
    last_date = datetime.strptime(status["last_service"], "%Y-%m-%d").date()
    next_date = last_date + timedelta(days=180)
    km_since = status["odo"] % 15000
    km_rem = 15000 - km_since
    return next_date.strftime("%Y-%m-%d"), f"+{km_rem:,} km", km_rem

# ────────────────────────────────────────────────
# Utility Functions
# ────────────────────────────────────────────────
def calc_distance(row):
    """Calculate distance from odometer readings"""
    if pd.notna(row.get("Start Odo")) and pd.notna(row.get("End Odo")):
        try:
            return max(0, float(row["End Odo"]) - float(row["Start Odo"]))
        except:
            return 0
    return row.get("Distance (km)", 0)

def validate_odometer(start_odo, end_odo):
    """Validate odometer readings"""
    if end_odo < start_odo:
        return False, "End odometer must be greater than start"
    if end_odo - start_odo > APP_SETTINGS["max_daily_distance"]:
        return False, f"Distance exceeds {APP_SETTINGS['max_daily_distance']} km limit"
    return True, "Valid"

def check_alerts(vehicle_id, status, trips_df):
    """Check for active alerts"""
    alerts = []
    
    # Fuel alert
    if status["fuel"] < ALERT_THRESHOLDS["fuel_low"]:
        alerts.append({"type": "warning", "message": f"Low fuel: {status['fuel']}%"})
    
    # Service alert
    next_date, _, km_rem = estimate_next_service(status)
    try:
        days_to_service = (datetime.strptime(next_date, "%Y-%m-%d").date() - datetime.now().date()).days
        if km_rem < ALERT_THRESHOLDS["service_km_due"] or days_to_service < ALERT_THRESHOLDS["service_days_due"]:
            alerts.append({"type": "critical", "message": f"Service due! {km_rem} km remaining"})
        elif km_rem < ALERT_THRESHOLDS["service_km_warning"] or days_to_service < ALERT_THRESHOLDS["service_days_warning"]:
            alerts.append({"type": "warning", "message": f"Service soon: {km_rem} km remaining"})
    except:
        pass
    
    return alerts

# ────────────────────────────────────────────────
# Mobile CSS
# ────────────────────────────────────────────────
st.markdown("""
    <style>
        .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
        button, .stButton>button { min-height: 48px; font-size: 16px; }
        .stAlert { font-size: 16px; }
        div[data-testid="stMetricValue"] { font-size: 24px; }
        .reportview-container { background: #f5f7f9; }
    </style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────
# Authentication Check
# ────────────────────────────────────────────────
if not check_password():
    st.stop()

# ────────────────────────────────────────────────
# Header
# ────────────────────────────────────────────────
col1, col2, col3 = st.columns([1, 3, 1])
with col1:
    st.image("https://upload.wikimedia.org/wikipedia/commons/e/e9/Coat_of_arms_of_South_Africa.svg", width=120)
with col2:
    st.markdown(f"""
        <h1 style='margin-bottom:0;'>MC Tsakane Dashboard</h1>
        <h3 style='margin-top:0; color: #666;'>Department of Justice and Constitutional Development</h3>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"👤 **{st.session_state.get('user', 'User')}**")
    if st.button("🚪 Logout", key="logout"):
        st.session_state["authenticated"] = False
        st.rerun()

st.markdown("---")

# ────────────────────────────────────────────────
# Main Tabs
# ────────────────────────────────────────────────
tab_home, tab_sundry, tab_fleet, tab_admin = st.tabs(["🏠 HOME", "💰 SUNDRY", "🚗 FLEET", "⚙️ ADMIN"])

# ==================== HOME TAB ====================
with tab_home:
    st.subheader("📊 Witness Fees – Monthly Expenditure")
    
    # Sample data
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    amounts = [45000, 62000, 38000, 75000, 51000, 89000, 42000, 67000, 93000, 55000, 48000, 72000]
    df_fees = pd.DataFrame({"Month": months, "Amount (ZAR)": amounts})

    fig = px.bar(df_fees, x="Month", y="Amount (ZAR)", 
                 title="Monthly Witness Fees Expenditure",
                 color="Amount (ZAR)", color_continuous_scale="Greens",
                 text_auto=",.0f")
    fig.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("🚗 Fleet Health Overview")

    # Fleet summary
    summary_data = []
    all_alerts = []
    
    for v in VEHICLES:
        status = get_vehicle_status(v["id"])
        trips = load_trips(v["id"])
        next_date, km_str, km_rem = estimate_next_service(status)
        
        # Calculate status
        days_to_service = (datetime.strptime(next_date, "%Y-%m-%d").date() - datetime.now().date()).days
        if days_to_service < 30 or km_rem < 2000:
            health = "🔴 Due Soon"
        elif days_to_service < 90 or km_rem < 5000:
            health = "🟠 Approaching"
        else:
            health = "🟢 Good"
        
        summary_data.append({
            "Vehicle": v["reg"],
            "Location": status["location"],
            "Fuel": f"{status['fuel']}%",
            "Odometer": f"{status['odo']:,} km",
            "Next Service": next_date,
            "Status": health
        })
        
        # Collect alerts
        alerts = check_alerts(v["id"], status, trips)
        for alert in alerts:
            all_alerts.append(f"{v['reg']}: {alert['message']}")

    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Vehicles", len(VEHICLES))
    with col2:
        avg_fuel = sum(get_vehicle_status(v['id'])['fuel'] for v in VEHICLES) / len(VEHICLES)
        st.metric("Avg Fuel Level", f"{avg_fuel:.0f}%")
    with col3:
        total_km = sum(get_vehicle_status(v['id'])['odo'] for v in VEHICLES)
        st.metric("Total Fleet KM", f"{total_km:,}")
    with col4:
        attention = len([s for s in summary_data if "Due Soon" in s["Status"]])
        st.metric("Need Attention", attention)

    # Display summary table
    st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)
    
    # Display alerts
    if all_alerts:
        with st.expander("🚨 Active Alerts", expanded=True):
            for alert in all_alerts:
                st.warning(alert)

# ==================== SUNDRY TAB ====================
with tab_sundry:
    st.subheader("💰 Witness Fees Register")
    
    # Sample data
    sample_data = {
        "Date": ["2026-01-15", "2026-01-22", "2026-02-05", "2026-02-10", "2026-02-18"],
        "Witness": ["A. Nkosi", "B. Mthembu", "C. v/d Merwe", "D. Pillay", "E. Sithole"],
        "Case No": ["JHB/001", "CPT/045", "DBN/112", "JHB/078", "PE/023"],
        "Amount": [1200.00, 850.00, 1500.00, 950.00, 1100.00],
        "Status": ["Paid", "Pending", "Paid", "Awaiting", "Paid"],
        "Court": ["JHB Magistrate", "CPT High", "DBN Regional", "JHB High", "PE Magistrate"]
    }
    
    df_sundry = pd.DataFrame(sample_data)
    
    # Editable table
    edited_sundry = st.data_editor(
        df_sundry,
        column_config={
            "Amount": st.column_config.NumberColumn("Amount (R)", min_value=0, format="R %.2f"),
            "Status": st.column_config.SelectboxColumn("Status", options=["Paid", "Pending", "Awaiting", "Rejected"])
        },
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True
    )
    
    # Summary
    total = edited_sundry["Amount"].sum()
    pending = edited_sundry[edited_sundry["Status"].isin(["Pending", "Awaiting"])]["Amount"].sum()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Spent", f"R {total:,.2f}")
    col2.metric("Pending", f"R {pending:,.2f}")
    
    # Budget alert
    budget = 100000
    if total > budget * 0.9:
        st.warning(f"⚠️ Budget usage: {total/budget*100:.1f}%")

# ==================== FLEET TAB ====================
with tab_fleet:
    st.subheader("🚗 Fleet Management")
    
    # Vehicle tabs
    vehicle_tabs = st.tabs([f"{v['short']} ({v['reg']})" for v in VEHICLES])
    
    for idx, tab in enumerate(vehicle_tabs):
        veh = VEHICLES[idx]
        vid = veh["id"]
        reg = veh["reg"]
        
        with tab:
            # Load data
            status = get_vehicle_status(vid)
            trips_df = load_trips(vid)
            
            # Calculate distances
            if not trips_df.empty:
                trips_df["Distance (km)"] = trips_df.apply(calc_distance, axis=1)
            
            # Status cards
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"**📍 Location**  \n{status['location']}")
            with col2:
                fuel_color = "green" if status["fuel"] > 50 else "orange" if status["fuel"] > 20 else "red"
                st.markdown(f"**⛽ Fuel**  \n<span style='color:{fuel_color}'>{status['fuel']}%</span>", 
                          unsafe_allow_html=True)
                st.progress(status["fuel"] / 100)
            with col3:
                st.markdown(f"**📊 Odometer**  \n{status['odo']:,} km")
            with col4:
                st.markdown(f"**🔧 Last Service**  \n{status['last_service']}")
            
            # Alerts
            alerts = check_alerts(vid, status, trips_df)
            if alerts:
                for alert in alerts:
                    if alert["type"] == "critical":
                        st.error(f"🚨 {alert['message']}")
                    else:
                        st.warning(f"⚠️ {alert['message']}")
            
            # Sub-tabs
            sub_tabs = st.tabs(["📋 Trip Logs", "📊 Reports", "📈 Analytics"])
            
            # ===== TRIP LOGS SUBTAB =====
            with sub_tabs[0]:
                st.subheader("Trip Logs")
                
                # Import section
                with st.expander("📤 Import Data"):
                    st.info("Upload CSV or Excel file with trip data")
                    uploaded = st.file_uploader("Choose file", type=["csv", "xlsx"], 
                                               key=f"upload_{vid}")
                    
                    if uploaded:
                        try:
                            if uploaded.name.endswith('csv'):
                                new_data = pd.read_csv(uploaded)
                            else:
                                new_data = pd.read_excel(uploaded)
                            
                            if not new_data.empty:
                                trips_df = pd.concat([trips_df, new_data], ignore_index=True)
                                save_trips(vid, trips_df)
                                st.success(f"Imported {len(new_data)} rows!")
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                
                # Data editor
                column_config = {
                    "Date": st.column_config.DateColumn("Date", format="YYYY-MM-DD", required=True),
                    "Driver": st.column_config.SelectboxColumn("Driver", options=DRIVERS, required=True),
                    "Purpose": st.column_config.TextColumn("Purpose"),
                    "Start Odo": st.column_config.NumberColumn("Start (km)", min_value=0),
                    "End Odo": st.column_config.NumberColumn("End (km)", min_value=0),
                    "Distance (km)": st.column_config.NumberColumn("Distance", disabled=True),
                    "Fuel Added (L)": st.column_config.NumberColumn("Fuel (L)", min_value=0.0, format="%.1f"),
                    "Fuel Cost (R)": st.column_config.NumberColumn("Fuel Cost", format="R %.2f"),
                    "Toll Amount (R)": st.column_config.NumberColumn("Toll", format="R %.2f")
                }
                
                # Ensure required columns exist
                for col in ["Date", "Driver", "Purpose", "Start Odo", "End Odo", "Fuel Added (L)", 
                           "Fuel Cost (R)", "Toll Amount (R)", "Toll Plaza / Notes"]:
                    if col not in trips_df.columns:
                        trips_df[col] = "" if col == "Toll Plaza / Notes" else 0
                
                # Pagination
                rows_per_page = APP_SETTINGS["rows_per_page"]
                total_rows = len(trips_df)
                if total_rows > 0:
                    total_pages = (total_rows + rows_per_page - 1) // rows_per_page
                    page = st.number_input(f"Page (1-{total_pages})", min_value=1, 
                                         max_value=total_pages, value=1, key=f"page_{vid}")
                    
                    start = (page - 1) * rows_per_page
                    end = min(start + rows_per_page, total_rows)
                    
                    edited = st.data_editor(
                        trips_df.iloc[start:end],
                        column_config=column_config,
                        num_rows="dynamic",
                        use_container_width=True,
                        hide_index=True,
                        key=f"editor_{vid}"
                    )
                    
                    # Save changes
                    if not edited.empty:
                        trips_df.iloc[start:end] = edited.values
                        trips_df["Distance (km)"] = trips_df.apply(calc_distance, axis=1)
                        save_trips(vid, trips_df)
                    
                    st.caption(f"Showing {start+1}-{end} of {total_rows} entries")
                
                # Add new entry forms
                with st.expander("➕ Add New Entry"):
                    form_type = st.radio("Entry type", ["Trip", "Fuel", "Toll"], horizontal=True)
                    
                    if form_type == "Trip":
                        with st.form(f"trip_form_{vid}"):
                            col1, col2 = st.columns(2)
                            date = col1.date_input("Date", datetime.now())
                            driver = col2.selectbox("Driver", DRIVERS)
                            
                            col1, col2 = st.columns(2)
                            start_odo = col1.number_input("Start ODO", min_value=0, step=1)
                            end_odo = col2.number_input("End ODO", min_value=0, step=1)
                            
                            purpose = st.text_input("Purpose")
                            
                            if st.form_submit_button("Add Trip"):
                                valid, msg = validate_odometer(start_odo, end_odo)
                                if valid:
                                    new_row = pd.DataFrame([{
                                        "Date": date, "Driver": driver, "Purpose": purpose,
                                        "Start Odo": start_odo, "End Odo": end_odo,
                                        "Distance (km)": end_odo - start_odo,
                                        "Fuel Added (L)": 0, "Fuel Cost (R)": 0,
                                        "Odo at Refuel": 0, "Toll Amount (R)": 0,
                                        "Toll Plaza / Notes": ""
                                    }])
                                    trips_df = pd.concat([trips_df, new_row], ignore_index=True)
                                    save_trips(vid, trips_df)
                                    log_audit("trip_added", vid, f"{driver} - {purpose}")
                                    st.success("Trip added!")
                                    st.rerun()
                                else:
                                    st.error(msg)
                    
                    elif form_type == "Fuel":
                        with st.form(f"fuel_form_{vid}"):
                            col1, col2 = st.columns(2)
                            date = col1.date_input("Date", datetime.now())
                            odo = col2.number_input("Odometer", value=status["odo"], step=1)
                            
                            col1, col2 = st.columns(2)
                            litres = col1.number_input("Litres", min_value=0.0, step=0.1)
                            cost = col2.number_input("Cost (R)", min_value=0.0, step=10.0)
                            
                            notes = st.text_input("Station / Notes")
                            
                            if st.form_submit_button("Add Fuel"):
                                new_row = pd.DataFrame([{
                                    "Date": date, "Driver": "", "Purpose": "Refuel",
                                    "Start Odo": odo, "End Odo": odo, "Distance (km)": 0,
                                    "Fuel Added (L)": litres, "Fuel Cost (R)": cost,
                                    "Odo at Refuel": odo, "Toll Amount (R)": 0,
                                    "Toll Plaza / Notes": notes
                                }])
                                trips_df = pd.concat([trips_df, new_row], ignore_index=True)
                                save_trips(vid, trips_df)
                                log_audit("fuel_added", vid, f"{litres}L - R{cost}")
                                st.success("Fuel added!")
                                st.rerun()
                    
                    else:  # Toll
                        with st.form(f"toll_form_{vid}"):
                            col1, col2 = st.columns(2)
                            date = col1.date_input("Date", datetime.now())
                            driver = col2.selectbox("Driver", DRIVERS)
                            
                            col1, col2 = st.columns(2)
                            amount = col1.number_input("Toll Amount (R)", min_value=0.0, step=10.0)
                            plaza = col2.text_input("Toll Plaza")
                            
                            notes = st.text_input("Notes")
                            
                            if st.form_submit_button("Add Toll"):
                                new_row = pd.DataFrame([{
                                    "Date": date, "Driver": driver, "Purpose": "Toll",
                                    "Start Odo": 0, "End Odo": 0, "Distance (km)": 0,
                                    "Fuel Added (L)": 0, "Fuel Cost (R)": 0,
                                    "Odo at Refuel": 0, "Toll Amount (R)": amount,
                                    "Toll Plaza / Notes": f"{plaza} - {notes}"
                                }])
                                trips_df = pd.concat([trips_df, new_row], ignore_index=True)
                                save_trips(vid, trips_df)
                                log_audit("toll_added", vid, f"R{amount} at {plaza}")
                                st.success("Toll added!")
                                st.rerun()
            
            # ===== REPORTS SUBTAB =====
            with sub_tabs[1]:
                st.subheader("Monthly Reports")
                
                if not trips_df.empty and "Date" in trips_df.columns:
                    # Create month selector
                    trips_df["Month"] = pd.to_datetime(trips_df["Date"]).dt.to_period("M")
                    months = sorted(trips_df["Month"].unique(), reverse=True)
                    
                    selected = st.selectbox("Select Month", options=months, 
                                          format_func=lambda x: str(x), key=f"month_{vid}")
                    
                    # Filter data
                    monthly = trips_df[trips_df["Month"] == selected].copy()
                    
                    # Summary metrics
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Total KM", f"{monthly['Distance (km)'].sum():,.0f}")
                    col2.metric("Fuel Cost", f"R {monthly['Fuel Cost (R)'].sum():,.2f}")
                    col3.metric("Tolls", f"R {monthly['Toll Amount (R)'].sum():,.2f}")
                    col4.metric("Trips", len(monthly))
                    
                    # Detailed view
                    st.dataframe(monthly.drop(columns=["Month"]), use_container_width=True)
                    
                    # Export
                    csv = monthly.to_csv(index=False)
                    st.download_button("📥 Download CSV", data=csv, 
                                     file_name=f"report_{reg}_{selected}.csv",
                                     mime="text/csv", use_container_width=True)
                else:
                    st.info("No data available")
            
            # ===== ANALYTICS SUBTAB =====
            with sub_tabs[2]:
                st.subheader("Analytics")
                
                if not trips_df.empty and len(trips_df) > 0:
                    # Daily mileage chart
                    daily = trips_df.groupby(trips_df["Date"].dt.date)["Distance (km)"].sum().reset_index()
                    fig = px.line(daily, x="Date", y="Distance (km)", 
                                 title="Daily Mileage Trend")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Driver performance
                    if "Driver" in trips_df.columns:
                        driver_stats = trips_df.groupby("Driver").agg({
                            "Distance (km)": "sum",
                            "Fuel Cost (R)": "sum",
                            "Toll Amount (R)": "sum"
                        }).round(2)
                        st.dataframe(driver_stats, use_container_width=True)
                else:
                    st.info("Add trip data to see analytics")

# ==================== ADMIN TAB ====================
with tab_admin:
    st.subheader("⚙️ Administration")
    
    admin_tabs = st.tabs(["📦 Backup", "📋 Audit Log", "ℹ️ System Info"])
    
    with admin_tabs[0]:
        st.markdown("### Backup Management")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Create Backup", use_container_width=True):
                backup_dir = f"backups/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                os.makedirs(backup_dir, exist_ok=True)
                
                for vid in range(1, 4):
                    src = f"trips_vehicle_{vid}.csv"
                    if os.path.exists(src):
                        shutil.copy2(src, f"{backup_dir}/trips_vehicle_{vid}.csv")
                
                shutil.copy2("fleet_management.db", f"{backup_dir}/fleet_management.db")
                st.success(f"✅ Backup created: {backup_dir}")
                log_audit("backup_created", details=backup_dir)
        
        with col2:
            # List backups
            if os.path.exists("backups"):
                backups = sorted(os.listdir("backups"), reverse=True)[:5]
                if backups:
                    selected = st.selectbox("Select backup to restore", backups)
                    if st.button("🔄 Restore", type="primary", use_container_width=True):
                        if st.checkbox("Confirm overwrite"):
                            backup_path = f"backups/{selected}"
                            for vid in range(1, 4):
                                src = f"{backup_path}/trips_vehicle_{vid}.csv"
                                if os.path.exists(src):
                                    shutil.copy2(src, f"trips_vehicle_{vid}.csv")
                            
                            db_src = f"{backup_path}/fleet_management.db"
                            if os.path.exists(db_src):
                                shutil.copy2(db_src, "fleet_management.db")
                            
                            st.success("Restore complete!")
                            st.cache_data.clear()
                            log_audit("backup_restored", details=selected)
                            st.rerun()
    
    with admin_tabs[1]:
        st.markdown("### Audit Log")
        
        try:
            conn = sqlite3.connect('fleet_management.db')
            audit = pd.read_sql_query("SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT 100", conn)
            conn.close()
            
            if not audit.empty:
                st.dataframe(audit, use_container_width=True)
                
                csv = audit.to_csv(index=False)
                st.download_button("📥 Download Audit Log", data=csv,
                                 file_name=f"audit_{datetime.now().strftime('%Y%m%d')}.csv",
                                 mime="text/csv")
            else:
                st.info("No audit records")
        except:
            st.info("Audit log not available")
    
    with admin_tabs[2]:
        st.markdown("### System Information")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Storage**")
            total_size = 0
            for f in os.listdir("."):
                if f.endswith(".csv") or f.endswith(".db"):
                    size = os.path.getsize(f) if os.path.exists(f) else 0
                    total_size += size
                    st.text(f"{f}: {size/1024:.1f} KB")
            st.metric("Total", f"{total_size/1024:.1f} KB")
        
        with col2:
            st.markdown("**Cache**")
            st.metric("Cache Items", len(st.cache_data.keys()) if hasattr(st.cache_data, 'keys') else 0)
            if st.button("Clear Cache"):
                st.cache_data.clear()
                st.success("Cache cleared!")

# ────────────────────────────────────────────────
# Footer
# ────────────────────────────────────────────────
st.markdown("---")
st.markdown(f"""
    <div style='text-align: center; color: #666;'>
        © Department of Justice and Constitutional Development • {datetime.now().year} • v1.0
    </div>
""", unsafe_allow_html=True)
