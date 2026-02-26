import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta, time
import io
import os
import sqlite3
import shutil
import hashlib
import hmac
from pathlib import Path
import time as time_module
from functools import lru_cache
import warnings
warnings.filterwarnings('ignore')

# Handle optional imports gracefully
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    st.warning("⚠️ PyYAML not installed. Using default configuration.")

# ────────────────────────────────────────────────
# Configuration Management (with fallback)
# ────────────────────────────────────────────────
def load_config():
    """Load configuration from YAML file or use defaults"""
    default_config = {
        "vehicles": [
            {"id": 1, "reg": "LR 93 VW GP", "short": "Vehicle 1", "service_interval_km": 15000, "service_interval_days": 180, "fuel_capacity": 60},
            {"id": 2, "reg": "BW 47 KG GP", "short": "Vehicle 2", "service_interval_km": 15000, "service_interval_days": 180, "fuel_capacity": 60},
            {"id": 3, "reg": "JM 45 CY GP", "short": "Vehicle 3", "service_interval_km": 15000, "service_interval_days": 180, "fuel_capacity": 60}
        ],
        "drivers": ["MF Neludi", "SA Ndlela", "S Mothoa", "J Ndou", "FV Mkhwanazi", "ML Kgakatsi"],
        "app_settings": {
            "app_name": "DOJ&CD - MC Tsakane Dashboard",
            "rows_per_page": 20,
            "max_daily_distance": 2000,
            "backup_enabled": True,
            "backup_interval_days": 7
        },
        "alert_thresholds": {
            "fuel_low": 20,
            "service_km_warning": 5000,
            "service_days_warning": 90,
            "service_km_due": 2000,
            "service_days_due": 30
        }
    }
    
    if YAML_AVAILABLE:
        config_path = Path("config.yaml")
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                st.warning(f"Error loading config: {e}. Using defaults.")
                return default_config
        else:
            # Create default config file
            try:
                with open(config_path, 'w') as f:
                    yaml.dump(default_config, f)
            except:
                pass
            return default_config
    else:
        return default_config

config = load_config()
vehicles = config["vehicles"]
drivers_list = config["drivers"]
app_settings = config["app_settings"]
alert_thresholds = config["alert_thresholds"]

# ────────────────────────────────────────────────
# Authentication (simplified for Streamlit Cloud)
# ────────────────────────────────────────────────
def check_password():
    """Simple authentication for demo purposes"""
    
    # For demo - simple password check
    # In production, use proper authentication
    def login_clicked():
        if st.session_state["password"] == "admin123":  # Demo password
            st.session_state["authenticated"] = True
            st.session_state["user"] = "admin"
        else:
            st.session_state["authenticated"] = False
            st.error("😕 Invalid password")

    if "authenticated" not in st.session_state:
        st.title("Login - DOJ&CD Fleet Management")
        with st.form("login_form"):
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Login", on_click=login_clicked)
        st.info("Demo password: admin123")
        return False
    
    if not st.session_state["authenticated"]:
        st.title("Login - DOJ&CD Fleet Management")
        with st.form("login_form"):
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Login", on_click=login_clicked)
        st.info("Demo password: admin123")
        return False
    
    return True

# ────────────────────────────────────────────────
# Database Integration
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
                      date DATE,
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
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        # Create audit log table
        c.execute('''CREATE TABLE IF NOT EXISTS audit_log
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user TEXT,
                      action TEXT,
                      vehicle_id INTEGER,
                      details TEXT,
                      timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        # Create backups table
        c.execute('''CREATE TABLE IF NOT EXISTS backups
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      backup_path TEXT,
                      size_bytes INTEGER,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Database init error: {e}")
        return False

# Initialize database on startup
init_database()

# ────────────────────────────────────────────────
# Audit Logging
# ────────────────────────────────────────────────
def log_audit(action, vehicle_id=None, details=None):
    """Log user actions for audit trail"""
    try:
        conn = sqlite3.connect('fleet_management.db')
        c = conn.cursor()
        user = st.session_state.get("user", "unknown")
        c.execute('''INSERT INTO audit_log (user, action, vehicle_id, details)
                     VALUES (?, ?, ?, ?)''', (user, action, vehicle_id, details))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Audit log error: {e}")

# ────────────────────────────────────────────────
# Data Backup
# ────────────────────────────────────────────────
def backup_data():
    """Create backup of all CSV files"""
    try:
        backup_dir = f"backups/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(backup_dir, exist_ok=True)
        total_size = 0
        
        for vid in range(1, 4):
            src = f"trips_vehicle_{vid}.csv"
            if os.path.exists(src):
                dst = f"{backup_dir}/trips_vehicle_{vid}.csv"
                shutil.copy2(src, dst)
                total_size += os.path.getsize(dst)
        
        # Log backup to database
        try:
            conn = sqlite3.connect('fleet_management.db')
            c = conn.cursor()
            c.execute('''INSERT INTO backups (backup_path, size_bytes)
                         VALUES (?, ?)''', (backup_dir, total_size))
            conn.commit()
            conn.close()
        except:
            pass
        
        log_audit("backup_created", details=f"Backup size: {total_size} bytes")
        return True, backup_dir, total_size
    except Exception as e:
        return False, str(e), 0

def restore_backup(backup_path):
    """Restore data from backup"""
    try:
        for vid in range(1, 4):
            src = f"{backup_path}/trips_vehicle_{vid}.csv"
            dst = f"trips_vehicle_{vid}.csv"
            if os.path.exists(src):
                shutil.copy2(src, dst)
        
        log_audit("backup_restored", details=f"Restored from: {backup_path}")
        return True, "Restore successful"
    except Exception as e:
        return False, str(e)

# ────────────────────────────────────────────────
# Validation Functions
# ────────────────────────────────────────────────
def validate_odometer_readings(start_odo, end_odo, vehicle_id=None):
    """Validate odometer readings with business rules"""
    warnings = []
    
    if end_odo < start_odo:
        warnings.append("End odometer reading should be greater than start reading")
        return False, warnings
    
    distance = end_odo - start_odo
    if distance > app_settings["max_daily_distance"]:
        warnings.append(f"Unusually high distance detected ({distance} km). Please verify readings.")
    
    # Check against last known odometer
    if vehicle_id:
        status = get_vehicle_status(vehicle_id)
        if start_odo < status["odo"] and start_odo > 0:
            warnings.append(f"Start odometer ({start_odo}) is less than last recorded ({status['odo']})")
    
    return len(warnings) == 0, warnings

def sanitize_input(text):
    """Sanitize user input"""
    if pd.isna(text):
        return ""
    return str(text).strip()

# ────────────────────────────────────────────────
# Caching for Performance
# ────────────────────────────────────────────────
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_trips_cached(vid: int) -> pd.DataFrame:
    """Cached version of load_trips for better performance"""
    return load_trips(vid)

def load_trips(vid: int) -> pd.DataFrame:
    """Load trips from database with CSV fallback"""
    try:
        # Try to load from database first
        conn = sqlite3.connect('fleet_management.db')
        query = "SELECT * FROM trips WHERE vehicle_id = ? ORDER BY date DESC, time DESC"
        df = pd.read_sql_query(query, conn, params=[vid])
        conn.close()
        
        if not df.empty:
            # Rename columns to match CSV format
            column_map = {
                'date': 'Date',
                'time': 'Time',
                'driver': 'Driver',
                'purpose': 'Purpose',
                'start_odo': 'Start Odo',
                'end_odo': 'End Odo',
                'distance': 'Distance (km)',
                'fuel_added': 'Fuel Added (L)',
                'fuel_cost': 'Fuel Cost (R)',
                'odo_at_refuel': 'Odo at Refuel',
                'toll_amount': 'Toll Amount (R)',
                'toll_plaza_notes': 'Toll Plaza / Notes'
            }
            df = df.rename(columns=column_map)
            df['Date'] = pd.to_datetime(df['Date'])
            return df
    except Exception as e:
        print(f"Database load error: {e}")
    
    # Fallback to CSV
    file_path = f"trips_vehicle_{vid}.csv"
    columns = [
        "Date", "Time", "Driver", "Purpose", "Start Odo", "End Odo", "Distance (km)",
        "Fuel Added (L)", "Fuel Cost (R)", "Odo at Refuel", "Toll Amount (R)", "Toll Plaza / Notes"
    ]
    
    if os.path.exists(file_path):
        df = pd.read_csv(file_path, parse_dates=["Date"])
        for col in columns:
            if col not in df.columns:
                df[col] = pd.NA
        return df[columns]
    else:
        return pd.DataFrame(columns=columns)

def save_trips(vid: int, df: pd.DataFrame):
    """Save trips to both CSV and database"""
    # Save to CSV
    file_path = f"trips_vehicle_{vid}.csv"
    df.to_csv(file_path, index=False)
    
    # Save to database
    try:
        conn = sqlite3.connect('fleet_management.db')
        for _, row in df.iterrows():
            # Check if record exists
            cursor = conn.cursor()
            cursor.execute('''SELECT id FROM trips WHERE 
                            vehicle_id = ? AND date = ? AND driver = ? AND start_odo = ?''',
                         (vid, row['Date'].strftime('%Y-%m-%d'), row['Driver'], row['Start Odo']))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing record
                cursor.execute('''UPDATE trips SET
                                time = ?, purpose = ?, end_odo = ?, distance = ?,
                                fuel_added = ?, fuel_cost = ?, odo_at_refuel = ?,
                                toll_amount = ?, toll_plaza_notes = ?, updated_at = CURRENT_TIMESTAMP
                                WHERE id = ?''',
                             (row['Time'], row['Purpose'], row['End Odo'], row['Distance (km)'],
                              row['Fuel Added (L)'], row['Fuel Cost (R)'], row['Odo at Refuel'],
                              row['Toll Amount (R)'], row['Toll Plaza / Notes'], existing[0]))
            else:
                # Insert new record
                cursor.execute('''INSERT INTO trips 
                                (vehicle_id, date, time, driver, purpose, start_odo, end_odo,
                                 distance, fuel_added, fuel_cost, odo_at_refuel, toll_amount, toll_plaza_notes)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                             (vid, row['Date'].strftime('%Y-%m-%d'), row['Time'], row['Driver'],
                              row['Purpose'], row['Start Odo'], row['End Odo'], row['Distance (km)'],
                              row['Fuel Added (L)'], row['Fuel Cost (R)'], row['Odo at Refuel'],
                              row['Toll Amount (R)'], row['Toll Plaza / Notes']))
        
        conn.commit()
        conn.close()
        
        # Clear cache
        st.cache_data.clear()
        
        # Log the save action
        log_audit("data_saved", vid, f"Saved {len(df)} records")
        
    except Exception as e:
        print(f"Database save error: {e}")

# ────────────────────────────────────────────────
# Enhanced Analytics Functions
# ────────────────────────────────────────────────
def calculate_fuel_efficiency(df):
    """Calculate average fuel consumption per vehicle"""
    if df.empty:
        return 0
    
    total_distance = df['Distance (km)'].sum()
    total_fuel = df['Fuel Added (L)'].sum()
    
    if total_fuel > 0:
        return total_distance / total_fuel  # km per liter
    return 0

def predict_maintenance(df, current_odo, last_service_odo):
    """Predict next maintenance based on usage patterns"""
    if df.empty:
        return 15000, None
    
    km_since_service = current_odo - last_service_odo
    km_remaining = 15000 - km_since_service
    
    # Calculate average daily usage
    if len(df) > 1:
        date_range = (df['Date'].max() - df['Date'].min()).days
        if date_range > 0:
            avg_daily_km = df['Distance (km)'].sum() / date_range
            if avg_daily_km > 0:
                days_remaining = km_remaining / avg_daily_km
                return km_remaining, days_remaining
    
    return km_remaining, None

def analyze_driver_performance(df):
    """Analyze driver performance metrics"""
    if df.empty:
        return pd.DataFrame()
    
    driver_stats = df.groupby('Driver').agg({
        'Distance (km)': ['sum', 'mean', 'count'],
        'Fuel Cost (R)': 'sum',
        'Toll Amount (R)': 'sum'
    }).round(2)
    
    driver_stats.columns = ['Total Distance', 'Avg Trip Distance', 'Trip Count', 'Total Fuel Cost', 'Total Tolls']
    return driver_stats

# ────────────────────────────────────────────────
# Notification System
# ────────────────────────────────────────────────
def check_alerts(vehicle_id, status, df):
    """Check for various alerts and return notifications"""
    alerts = []
    
    # Fuel level alert
    if status["fuel"] < alert_thresholds["fuel_low"]:
        alerts.append({
            "type": "warning",
            "message": f"⚠️ Low fuel: {status['fuel']}% remaining",
            "icon": "⛽"
        })
    
    # Service alerts
    next_date, km_remaining_str, km_remaining = estimate_next_service(status)
    try:
        next_date_obj = datetime.strptime(next_date, "%Y-%m-%d").date()
        days_to_service = (next_date_obj - datetime.now().date()).days
        
        if km_remaining < alert_thresholds["service_km_due"] or days_to_service < alert_thresholds["service_days_due"]:
            alerts.append({
                "type": "critical",
                "message": f"🔴 Service due! {km_remaining:,} km or {days_to_service} days remaining",
                "icon": "🚨"
            })
        elif km_remaining < alert_thresholds["service_km_warning"] or days_to_service < alert_thresholds["service_days_warning"]:
            alerts.append({
                "type": "warning",
                "message": f"🟠 Service approaching: {km_remaining:,} km or {days_to_service} days left",
                "icon": "⚠️"
            })
    except:
        pass
    
    # Unusual driving patterns
    if not df.empty and len(df) > 5:
        avg_distance = df['Distance (km)'].mean()
        max_distance = df['Distance (km)'].max()
        if max_distance > avg_distance * 3:
            alerts.append({
                "type": "info",
                "message": f"📊 Unusual trip detected: {max_distance} km trip (avg: {avg_distance:.0f} km)",
                "icon": "ℹ️"
            })
    
    return alerts

# ────────────────────────────────────────────────
# Page config & mobile/PWA support
# ────────────────────────────────────────────────
st.set_page_config(
    page_title=app_settings["app_name"],
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Check authentication
if not check_password():
    st.stop()

# Mobile viewport + larger touch targets
st.markdown("""
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
    <style>
        .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
        button, .stButton>button { min-height: 48px; font-size: 16px; padding: 12px; min-width: 120px; }
        input, .stTextInput>div>div>input, .stNumberInput>div>div>input { font-size: 16px; }
        .stSelectbox>div>div>div, .stExpander { font-size: 16px; }
        /* Alert styling */
        .alert-critical { color: #dc3545; font-weight: bold; }
        .alert-warning { color: #ffc107; font-weight: bold; }
        .alert-info { color: #17a2b8; }
        .stExpander:has(.stSuccess) > div > div > div:first-child {
            color: #006400 !important;
            font-weight: bold !important;
        }
    </style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────
# Vehicle status (enhanced)
# ────────────────────────────────────────────────
def get_vehicle_status(vehicle_id: int) -> dict:
    # Try to get latest odometer from trips
    trips = load_trips_cached(vehicle_id)
    latest_odo = 0
    if not trips.empty and 'End Odo' in trips.columns:
        valid_odos = trips[trips['End Odo'] > 0]['End Odo']
        if not valid_odos.empty:
            latest_odo = valid_odos.max()
    
    data = {
        1: {"location": "JHB Magistrate Court", "fuel": 65, "odo": max(124850, latest_odo), "last_service": "2025-11-15", "alerts": "None"},
        2: {"location": "En Route to CPT",      "fuel": 28, "odo": max(98740, latest_odo),  "last_service": "2025-10-20", "alerts": "Low Fuel Warning"},
        3: {"location": "Parked - PE Office",   "fuel": 92, "odo": max(156320, latest_odo), "last_service": "2026-01-10", "alerts": "Service Due Soon"}
    }
    return data.get(vehicle_id, {"location": "Unknown", "fuel": 0, "odo": 0, "last_service": "N/A", "alerts": "N/A"})

# ────────────────────────────────────────────────
# Next service estimate
# ────────────────────────────────────────────────
def estimate_next_service(status: dict):
    last_date = datetime.strptime(status["last_service"], "%Y-%m-%d").date()
    next_date = last_date + timedelta(days=180)
    km_since = status["odo"] % 15000
    km_rem = 15000 - km_since
    return next_date.strftime("%Y-%m-%d"), f"+{km_rem:,} km", km_rem

# ────────────────────────────────────────────────
# Header with user info
# ────────────────────────────────────────────────
st.markdown('<div class="header">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 3, 1])
with col1:
    st.image("https://upload.wikimedia.org/wikipedia/commons/e/e9/Coat_of_arms_of_South_Africa.svg", width=160)
with col2:
    st.markdown(f"""
        <h1>MC Tsakane Dashboard</h1>
        <h3>Department of Justice and Constitutional Development</h3>
        <p>Internal Use • {datetime.now().year}</p>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"👤 **{st.session_state.get('user', 'User')}**")
    if st.button("🚪 Logout"):
        for key in ['authenticated', 'user']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# Automatic backup check
if app_settings["backup_enabled"]:
    try:
        conn = sqlite3.connect('fleet_management.db')
        c = conn.cursor()
        c.execute('''SELECT MAX(created_at) FROM backups''')
        last_backup = c.fetchone()[0]
        conn.close()
        
        if last_backup:
            last_backup_date = datetime.strptime(last_backup, '%Y-%m-%d %H:%M:%S')
            days_since_backup = (datetime.now() - last_backup_date).days
            if days_since_backup >= app_settings["backup_interval_days"]:
                with st.spinner("Creating automatic backup..."):
                    success, path, size = backup_data()
                    if success:
                        st.success(f"✅ Automatic backup created: {path}")
    except Exception as e:
        pass

# ────────────────────────────────────────────────
# Helper function for distance calculation
# ────────────────────────────────────────────────
def calc_distance(row):
    if row.get("Purpose") == "Toll payment":
        return 0
    if pd.notna(row.get("Start Odo")) and pd.notna(row.get("End Odo")):
        return max(0, row["End Odo"] - row["Start Odo"])
    return row.get("Distance (km)", 0)

# ────────────────────────────────────────────────
# Tabs
# ────────────────────────────────────────────────
tab_home, tab_sundry, tab_fleet, tab_admin = st.tabs(["HOME", "SUNDRY", "FLEET SERVICES", "ADMIN"])

# ────────────────────────────────────────────────
# HOME (enhanced)
# ────────────────────────────────────────────────
with tab_home:
    st.subheader("Witness Fees – Monthly Expenditure Overview")

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    amounts = [45000, 62000, 38000, 75000, 51000, 89000, 42000, 67000, 93000, 55000, 48000, 72000]
    df = pd.DataFrame({"Month": months, "Amount (ZAR)": amounts})

    fig = px.bar(df, x="Month", y="Amount (ZAR)", title=f"Monthly Witness Fees {datetime.now().year}",
                 color="Amount (ZAR)", color_continuous_scale="Greens", text_auto=",.0f")
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("🚗 Fleet Health & Service Overview")

    summary_data = []
    alerts_summary = []
    
    for v in vehicles:
        s = get_vehicle_status(v["id"])
        trips = load_trips_cached(v["id"])
        next_d, next_k, km_r = estimate_next_service(s)
        days_left = (datetime.strptime(next_d, "%Y-%m-%d").date() - datetime.now().date()).days
        
        # Enhanced status calculation
        if days_left < 30 or km_r < 2000:
            status = "🔴 Due Soon"
        elif days_left < 90 or km_r < 5000:
            status = "🟠 Approaching"
        else:
            status = "🟢 On Track"
        
        # Get alerts
        vehicle_alerts = check_alerts(v["id"], s, trips)
        alerts_summary.extend([(v["reg"], alert) for alert in vehicle_alerts])

        summary_data.append({
            "Vehicle": v["reg"], 
            "Location": s["location"], 
            "Fuel": f"{s['fuel']}%", 
            "Odometer": f"{s['odo']:,} km",
            "Last Service": s["last_service"], 
            "Next Service (Date)": next_d, 
            "Km Remaining": next_k, 
            "Status": status
        })

    summary_df = pd.DataFrame(summary_data)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Vehicles", len(vehicles))
    col2.metric("Avg Fuel Level", f"{sum(get_vehicle_status(v['id'])['fuel'] for v in vehicles)/len(vehicles):.0f}%")
    col3.metric("Total Fleet Odometer", f"{sum(get_vehicle_status(v['id'])['odo'] for v in vehicles):,} km")
    col4.metric("Vehicles Needing Attention", len([r for r in summary_data if "Due Soon" in r["Status"]]))

    st.dataframe(summary_df, use_container_width=True, hide_index=True)
    
    # Display alerts
    if alerts_summary:
        st.markdown("### 🚨 Active Alerts")
        for reg, alert in alerts_summary:
            st.markdown(f"**{reg}**: {alert['icon']} {alert['message']}")
    
    st.caption("Next service: earlier of 6 months or 15,000 km since last service.")

# ────────────────────────────────────────────────
# SUNDRY (enhanced with validation)
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
    
    # Add validation for amounts
    column_config_sundry = {
        "Amount Paid (ZAR)": st.column_config.NumberColumn(
            "Amount Paid (ZAR)",
            min_value=0,
            max_value=100000,
            format="R %.2f",
            required=True,
            step=50.0
        ),
        "Status": st.column_config.SelectboxColumn(
            "Status",
            options=["Paid", "Pending Approval", "Awaiting Receipt", "Rejected"],
            required=True
        )
    }
    
    edited_df = st.data_editor(df, column_config=column_config_sundry, num_rows="dynamic", use_container_width=True)

    total_spent = edited_df["Amount Paid (ZAR)"].sum()
    pending = edited_df[edited_df["Status"].isin(["Pending Approval", "Awaiting Receipt"])]["Amount Paid (ZAR)"].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Spent", f"R {total_spent:,.2f}")
    col2.metric("Pending / Awaiting", f"R {pending:,.2f}")
    
    # Budget alert
    monthly_budget = 100000
    if total_spent > monthly_budget * 0.9:
        st.warning(f"⚠️ Monthly budget usage: {total_spent/monthly_budget*100:.1f}% (R{total_spent:,.2f} of R{monthly_budget:,.2f})")

# ────────────────────────────────────────────────
# FLEET SERVICES (enhanced)
# ────────────────────────────────────────────────
with tab_fleet:
    st.subheader("Fleet Services – Gauteng Region")
    st.markdown("Vehicle tracking, fuel status, odometer, alerts & recent trips/logs.")

    vehicle_tabs = st.tabs([f"{v['short']} ({v['reg']})" for v in vehicles])

    for idx, tab in enumerate(vehicle_tabs):
        veh = vehicles[idx]
        vid = veh["id"]
        reg = veh["reg"]
        status = get_vehicle_status(vid)

        current_trips = load_trips_cached(vid)

        # Recalculate distances
        current_trips["Distance (km)"] = current_trips.apply(calc_distance, axis=1)

        with tab:
            st.markdown(f"### {reg}")

            # Display alerts
            alerts = check_alerts(vid, status, current_trips)
            if alerts:
                with st.expander("🚨 Vehicle Alerts", expanded=True):
                    for alert in alerts:
                        alert_class = f"alert-{alert['type']}"
                        st.markdown(f"<div class='{alert_class}'>{alert['icon']} {alert['message']}</div>", 
                                  unsafe_allow_html=True)

            c1, c2, c3 = st.columns([2, 2, 1.4])
            c1.markdown(f"**Current location**  \n{status['location']}")
            fuel_color = "green" if status["fuel"] > 50 else "orange" if status["fuel"] > 20 else "red"
            c2.markdown(f"**Fuel level**  \n<span style='color:{fuel_color}'>{status['fuel']}%</span>", unsafe_allow_html=True)
            c2.progress(status["fuel"] / 100)
            c2.markdown(f"**Odometer**  \n{status['odo']:,} km")
            alert_cls = "status-good" if "None" in status["alerts"] else "status-warning" if "Low" in status["alerts"] else "status-alert"
            c3.markdown(f"**Last service**  \n{status['last_service']}")
            c3.markdown(f"**Alerts**  \n<span class='{alert_cls}'>{status['alerts']}</span>", unsafe_allow_html=True)

            # Mileage Trend
            st.subheader("Mileage Trend (last 14 days)")
            if not current_trips.empty:
                df_trips = current_trips.copy()
                df_trips['DateOnly'] = df_trips['Date'].dt.date
                daily_km = df_trips.groupby('DateOnly')['Distance (km)'].sum().reset_index()
                daily_km = daily_km.sort_values('DateOnly')

                start_date = datetime.now().date() - timedelta(days=13)
                all_dates = pd.date_range(start=start_date, end=datetime.now().date()).date
                df_daily = pd.DataFrame({'Date': all_dates})
                df_daily = df_daily.merge(daily_km, left_on='Date', right_on='DateOnly', how='left').fillna(0)
                df_daily = df_daily[['Date', 'Distance (km)']]
            else:
                dates = [datetime.now().date() - timedelta(days=x) for x in range(13, -1, -1)]
                df_daily = pd.DataFrame({"Date": dates, "Distance (km)": [0]*14})

            fig = px.line(df_daily, x="Date", y="Distance (km)", title="Mileage Trend (from logged trips)")
            fig.update_traces(line_color="#005c28")
            fig.update_layout(margin=dict(l=20, r=20, t=40, b=20), height=300)
            st.plotly_chart(fig, use_container_width=True, key=f"mileage_chart_vehicle_{vid}")

            subtab_logs, subtab_report, subtab_analytics = st.tabs(["Trip Logs", "Monthly Report", "Analytics"])

            with subtab_logs:
                st.subheader(f"Recent trips / logs – {reg}")
                st.caption("Distance is auto-calculated from End Odo - Start Odo for trips (read-only). Tolls have 0 distance.")

                column_config = {
                    "Date": st.column_config.DateColumn("Date", format="YYYY-MM-DD", required=True),
                    "Time": st.column_config.TimeColumn("Time", format="HH:mm", step=60),
                    "Driver": st.column_config.SelectboxColumn(
                        "Driver",
                        options=drivers_list,
                        required=True
                    ),
                    "Purpose": st.column_config.TextColumn("Purpose"),
                    "Start Odo": st.column_config.NumberColumn("Start Odo", min_value=0, format="%d km"),
                    "End Odo": st.column_config.NumberColumn("End Odo", min_value=0, format="%d km"),
                    "Distance (km)": st.column_config.NumberColumn(
                        "Distance (km)",
                        min_value=0,
                        format="%d km",
                        disabled=True,
                        help="Auto-calculated for trips; 0 for tolls"
                    ),
                    "Fuel Added (L)": st.column_config.NumberColumn("Fuel Added (L)", min_value=0.0, format="%.1f L"),
                    "Fuel Cost (R)": st.column_config.NumberColumn("Fuel Cost (R)", min_value=0.0, format="R %.2f"),
                    "Odo at Refuel": st.column_config.NumberColumn("Odo at Refuel", min_value=0, format="%d km"),
                    "Toll Amount (R)": st.column_config.NumberColumn("Toll Amount (R)", min_value=0.0, format="R %.2f"),
                    "Toll Plaza / Notes": st.column_config.TextColumn("Toll Plaza / Notes")
                }

                # ────────────────────────────────────────────────
                # IMPORT DATA FEATURE
                # ────────────────────────────────────────────────
                with st.expander("📤 Import trips from CSV or Excel", expanded=False):
                    st.info("""
                    **Expected file format** (columns can be in any order, case-insensitive):
                    - Date (YYYY-MM-DD)
                    - Driver
                    - Purpose
                    - Start Odo / Start km
                    - End Odo / End km
                    - (optional) Distance (km), Fuel Added (L), Fuel Cost (R), Toll Amount (R), Notes
                    """)

                    uploaded_file = st.file_uploader(
                        "Choose a CSV or Excel file",
                        type=["csv", "xlsx", "xls"],
                        accept_multiple_files=False,
                        help="Upload your trip log file. New rows will be appended.",
                        key=f"import_uploader_vehicle_{vid}"
                    )

                    if uploaded_file is not None:
                        try:
                            if uploaded_file.name.endswith('.csv'):
                                new_data = pd.read_csv(uploaded_file, parse_dates=["Date"], dayfirst=True, errors='coerce')
                            else:
                                new_data = pd.read_excel(uploaded_file, parse_dates=["Date"], dayfirst=True)

                            # Standardize column names
                            column_map = {
                                "date": "Date", "trip date": "Date", "date of trip": "Date",
                                "driver": "Driver", "name": "Driver",
                                "purpose": "Purpose", "reason": "Purpose", "description": "Purpose",
                                "start odo": "Start Odo", "start km": "Start Odo", "start": "Start Odo",
                                "end odo": "End Odo", "end km": "End Odo", "end": "End Odo",
                                "distance": "Distance (km)", "km": "Distance (km)",
                                "fuel added": "Fuel Added (L)", "litres": "Fuel Added (L)",
                                "fuel cost": "Fuel Cost (R)", "cost": "Fuel Cost (R)",
                                "toll": "Toll Amount (R)", "toll amount": "Toll Amount (R)",
                                "notes": "Toll Plaza / Notes", "comments": "Toll Plaza / Notes"
                            }

                            new_data.columns = new_data.columns.str.lower().str.strip()
                            new_data = new_data.rename(columns=column_map)

                            known_cols = load_trips(vid).columns
                            new_data = new_data[[c for c in new_data.columns if c in known_cols]]

                            if not new_data.empty:
                                # Validate imported data
                                valid_rows = []
                                for _, row in new_data.iterrows():
                                    if pd.notna(row.get('Start Odo')) and pd.notna(row.get('End Odo')):
                                        is_valid, warnings = validate_odometer_readings(
                                            row['Start Odo'], row['End Odo'], vid
                                        )
                                        if is_valid:
                                            valid_rows.append(row)
                                        else:
                                            for warning in warnings:
                                                st.warning(f"Skipped row: {warning}")
                                    else:
                                        valid_rows.append(row)
                                
                                if valid_rows:
                                    valid_df = pd.DataFrame(valid_rows)
                                    current_trips = pd.concat([current_trips, valid_df], ignore_index=True)
                                    current_trips["Distance (km)"] = current_trips.apply(calc_distance, axis=1)
                                    save_trips(vid, current_trips)
                                    st.success(f"Imported {len(valid_df)} rows successfully! Data saved.")
                                    st.rerun()
                                else:
                                    st.warning("No valid data rows found.")
                            else:
                                st.warning("No valid data columns found in the file.")

                        except Exception as e:
                            st.error(f"Error reading file: {str(e)}")

                # ────────────────────────────────────────────────
                # Table display + edit + pagination
                # ────────────────────────────────────────────────
                st.subheader(f"Recent trips / logs – {reg}")

                # Pagination
                rows_per_page = app_settings["rows_per_page"]
                total_rows = len(current_trips)
                total_pages = max(1, (total_rows + rows_per_page - 1) // rows_per_page)

                col_left, col_center, col_right = st.columns([1, 4, 1])
                with col_center:
                    page = st.number_input(
                        f"Page (1–{total_pages}) – Total {total_rows} entries",
                        min_value=1,
                        max_value=total_pages,
                        value=1,
                        step=1,
                        format="%d",
                        key=f"page_selector_{vid}"
                    )

                start_idx = (page - 1) * rows_per_page
                end_idx = min(start_idx + rows_per_page, total_rows)

                page_data = current_trips.iloc[start_idx:end_idx].copy()

                edited_page = st.data_editor(
                    page_data,
                    column_config=column_config,
                    num_rows="dynamic",
                    use_container_width=True,
                    hide_index=True,
                    key=f"trips_editor_page_{vid}_{page}"
                )

                # Safe update + save
                if not edited_page.empty:
                    original_slice_index = current_trips.index[start_idx:end_idx]
                    edited_page = edited_page.reindex(original_slice_index)
                    current_trips.loc[original_slice_index] = edited_page.values
                    current_trips["Distance (km)"] = current_trips.apply(calc_distance, axis=1)
                    save_trips(vid, current_trips)

                st.caption(f"Showing rows {start_idx+1}–{end_idx} of {total_rows}")
                st.metric("Total log entries", total_rows, key=f"metric_entries_{vid}")

                if total_rows > 0:
                    total_distance = current_trips["Distance (km)"].sum()
                    total_fuel_cost = current_trips["Fuel Cost (R)"].sum()
                    total_tolls = current_trips["Toll Amount (R)"].sum()
                    fuel_efficiency = calculate_fuel_efficiency(current_trips)

                    colA, colB, colC, colD = st.columns(4)
                    colA.metric("Total Distance", f"{total_distance:,} km", key=f"metric_dist_{vid}")
                    colB.metric("Total Fuel Cost", f"R {total_fuel_cost:,.2f}", key=f"metric_fuel_{vid}")
                    colC.metric("Total Tolls Paid", f"R {total_tolls:,.2f}", key=f"metric_tolls_{vid}")
                    colD.metric("Fuel Efficiency", f"{fuel_efficiency:.1f} km/L", key=f"metric_eff_{vid}")

                # Add Trip (with validation)
                with st.expander("➕ Add Trip", expanded=False):
                    with st.form(key=f"add_trip_form_{vid}"):
                        col_date, col_driver = st.columns(2)
                        trip_date = col_date.date_input("Trip date", value=datetime.now().date(), key=f"trip_date_{vid}")
                        driver = col_driver.selectbox("Driver", options=drivers_list, key=f"trip_driver_{vid}")

                        col_start, col_end = st.columns(2)
                        start_odo = col_start.number_input("Start Odometer (km)", min_value=0, step=1, key=f"trip_start_odo_{vid}")
                        end_odo = col_end.number_input("End Odometer (km)", min_value=0, step=1, key=f"trip_end_odo_{vid}")

                        purpose = st.text_input("Purpose of trip", key=f"trip_purpose_{vid}")

                        if st.form_submit_button("Add Trip", type="primary"):
                            # Validate
                            is_valid, warnings = validate_odometer_readings(start_odo, end_odo, vid)
                            
                            if not is_valid:
                                for warning in warnings:
                                    st.warning(warning)
                            
                            distance = max(0, end_odo - start_odo) if end_odo >= start_odo else 0
                            new_row = pd.DataFrame([{
                                "Date": pd.to_datetime(trip_date),
                                "Time": None,
                                "Driver": driver,
                                "Purpose": purpose,
                                "Start Odo": start_odo,
                                "End Odo": end_odo,
                                "Distance (km)": distance,
                                "Fuel Added (L)": 0.0,
                                "Fuel Cost (R)": 0.0,
                                "Odo at Refuel": 0,
                                "Toll Amount (R)": 0.0,
                                "Toll Plaza / Notes": ""
                            }])

                            current_trips = pd.concat([current_trips, new_row], ignore_index=True)
                            current_trips["Distance (km)"] = current_trips.apply(calc_distance, axis=1)
                            save_trips(vid, current_trips)
                            log_audit("trip_added", vid, f"Trip added: {driver}, {distance} km")

                            st.success(
                                f"Trip added successfully!\n"
                                f"Driver: {driver} | Date: {trip_date} | Distance: {distance} km"
                            )
                            st.rerun()

                # Add Fuel Slip
                with st.expander("➕ Add Fuel Slip", expanded=False):
                    with st.form(key=f"add_fuel_form_{vid}"):
                        col_date, col_odo = st.columns(2)
                        fuel_date = col_date.date_input("Refuelling date", value=datetime.now().date(), key=f"fuel_date_{vid}")
                        fuel_odo = col_odo.number_input("Odometer at refuel (km)", min_value=0, value=status["odo"], step=1, key=f"fuel_odo_{vid}")

                        col_driver, col_litres = st.columns(2)
                        driver = col_driver.selectbox("Driver", options=drivers_list, key=f"fuel_driver_{vid}")
                        fuel_litres = col_litres.number_input("Litres added", min_value=0.0, step=0.1, format="%.1f", key=f"fuel_litres_{vid}")

                        col_cost, _ = st.columns([1, 1])
                        fuel_cost = col_cost.number_input("Total fuel cost (R)", min_value=0.0, step=1.0, format="%.2f", key=f"fuel_cost_{vid}")

                        fuel_notes = st.text_input("Fuel station / Notes", key=f"fuel_notes_{vid}")

                        if st.form_submit_button("Add Fuel Slip", type="primary"):
                            new_row = pd.DataFrame([{
                                "Date": pd.to_datetime(fuel_date),
                                "Time": None,
                                "Driver": driver,
                                "Purpose": "Refuelling",
                                "Start Odo": fuel_odo,
                                "End Odo": fuel_odo,
                                "Distance (km)": 0,
                                "Fuel Added (L)": fuel_litres,
                                "Fuel Cost (R)": fuel_cost,
                                "Odo at Refuel": fuel_odo,
                                "Toll Amount (R)": 0.00,
                                "Toll Plaza / Notes": fuel_notes
                            }])

                            current_trips = pd.concat([current_trips, new_row], ignore_index=True)
                            save_trips(vid, current_trips)
                            log_audit("fuel_added", vid, f"Fuel: {fuel_litres}L, Cost: R{fuel_cost}")

                            st.success("Fuel slip added successfully!")
                            st.rerun()

                # Add Toll Slip
                with st.expander("➕ Add Toll Slip", expanded=False):
                    st.caption("Toll payments do not require odometer readings.")
                    
                    with st.form(key=f"add_toll_form_{vid}"):
                        col_date, col_time = st.columns(2)
                        toll_date = col_date.date_input("Toll date", value=datetime.now().date(), key=f"toll_date_{vid}")
                        toll_time = col_time.time_input("Approximate toll time", value=time(8, 0), step=60, key=f"toll_time_{vid}")

                        col_driver, col_amount = st.columns(2)
                        driver = col_driver.selectbox("Driver", options=drivers_list, key=f"toll_driver_{vid}")
                        toll_amount = col_amount.number_input("Toll amount (R)", min_value=0.0, step=1.0, format="%.2f", key=f"toll_amount_{vid}")

                        toll_plaza = st.text_input("Toll plaza / Route", key=f"toll_plaza_{vid}")
                        toll_notes = st.text_input("Additional notes / Invoice nr", key=f"toll_notes_{vid}")

                        if st.form_submit_button("Add Toll Slip", type="primary"):
                            new_row = pd.DataFrame([{
                                "Date": pd.to_datetime(toll_date),
                                "Time": toll_time,
                                "Driver": driver,
                                "Purpose": "Toll payment",
                                "Start Odo": 0,
                                "End Odo": 0,
                                "Distance (km)": 0,
                                "Fuel Added (L)": 0.0,
                                "Fuel Cost (R)": 0.0,
                                "Odo at Refuel": 0,
                                "Toll Amount (R)": toll_amount,
                                "Toll Plaza / Notes": f"{toll_plaza} – {toll_notes}".strip(" – ")
                            }])

                            current_trips = pd.concat([current_trips, new_row], ignore_index=True)
                            save_trips(vid, current_trips)
                            log_audit("toll_added", vid, f"Toll: R{toll_amount} at {toll_plaza}")

                            st.success("Toll slip added successfully!")
                            st.rerun()

            with subtab_report:
                st.subheader(f"Monthly Report – {reg}")

                if not current_trips.empty:
                    df_report = current_trips.copy()
                    df_report['Month'] = df_report['Date'].dt.to_period('M')
                    available_months = sorted(df_report['Month'].unique().astype(str), reverse=True)

                    selected_month_str = st.selectbox(
                        "Select month to view",
                        options=available_months,
                        index=0,
                        key=f"month_selector_vehicle_{vid}"
                    )

                    selected_month = pd.Period(selected_month_str)
                    monthly_trips = df_report[df_report['Month'] == selected_month].copy()
                    monthly_trips = monthly_trips.drop(columns=['Month'])

                    monthly_summary = monthly_trips.agg({
                        'Distance (km)': 'sum',
                        'Fuel Cost (R)': 'sum',
                        'Toll Amount (R)': 'sum',
                        'Fuel Added (L)': 'sum'
                    }).to_frame(name='Total').T

                    st.markdown("#### Monthly Summary")
                    st.dataframe(monthly_summary, use_container_width=True)

                    st.markdown("#### All Trips & Slips in Selected Month")
                    st.dataframe(monthly_trips, use_container_width=True, hide_index=False)

                    fig_month = px.bar(monthly_summary.T.reset_index(),
                                       x='index', y='Total',
                                       title=f"Summary for {selected_month_str}")
                    st.plotly_chart(fig_month, use_container_width=True, key=f"monthly_chart_{vid}_{selected_month_str}")

                    # Export options
                    col1, col2 = st.columns(2)
                    
                    # CSV export
                    csv_buffer = io.StringIO()
                    monthly_trips.to_csv(csv_buffer, index=False)
                    csv_data = csv_buffer.getvalue()

                    with col1:
                        st.download_button(
                            label="📥 Download Trips (CSV)",
                            data=csv_data,
                            file_name=f"Trips_{reg.replace(' ', '_')}_{selected_month_str}.csv",
                            mime="text/csv",
                            key=f"csv_download_{vid}_{selected_month_str}",
                            use_container_width=True
                        )

                    # Excel export
                    excel_buffer = io.BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                        monthly_trips.to_excel(writer, sheet_name='Trips & Slips', index=False)
                        monthly_summary.to_excel(writer, sheet_name='Summary')

                    excel_buffer.seek(0)

                    with col2:
                        st.download_button(
                            label="📊 Download Report (Excel)",
                            data=excel_buffer,
                            file_name=f"Monthly_Report_{reg.replace(' ', '_')}_{selected_month_str}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"excel_download_{vid}_{selected_month_str}",
                            use_container_width=True
                        )

                else:
                    st.info("No trip data yet. Add entries in Trip Logs.")

            with subtab_analytics:
                st.subheader(f"Advanced Analytics – {reg}")
                
                if not current_trips.empty:
                    # Driver performance
                    st.markdown("#### Driver Performance")
                    driver_stats = analyze_driver_performance(current_trips)
                    st.dataframe(driver_stats, use_container_width=True)
                    
                    # Fuel efficiency trend
                    st.markdown("#### Fuel Efficiency Trend")
                    fuel_data = current_trips[current_trips['Fuel Added (L)'] > 0].copy()
                    if not fuel_data.empty:
                        fuel_data['Efficiency'] = fuel_data['Distance (km)'] / fuel_data['Fuel Added (L)']
                        fuel_data = fuel_data.sort_values('Date')
                        
                        fig_fuel = px.line(fuel_data, x='Date', y='Efficiency',
                                         title='Fuel Efficiency Over Time (km/L)')
                        fig_fuel.update_traces(line_color='#28a745')
                        st.plotly_chart(fig_fuel, use_container_width=True)
                    
                    # Cost analysis
                    st.markdown("#### Cost Analysis")
                    cost_cols = ['Fuel Cost (R)', 'Toll Amount (R)']
                    cost_data = current_trips[cost_cols].sum()
                    if cost_data.sum() > 0:
                        fig_costs = px.pie(values=cost_data.values, names=cost_data.index,
                                          title='Cost Breakdown')
                        st.plotly_chart(fig_costs, use_container_width=True)
                    
                    # Maintenance prediction
                    last_service_km = current_trips[current_trips['Purpose'] == 'Service']['End Odo'].max() if 'Service' in current_trips['Purpose'].values else 0
                    if last_service_km > 0:
                        km_remaining, days_remaining = predict_maintenance(current_trips, status['odo'], last_service_km)
                        st.info(f"**Maintenance Prediction**: {km_remaining:.0f} km remaining until next service" + 
                               (f" (approx {days_remaining:.0f} days)" if days_remaining else ""))
                else:
                    st.info("Add trip data to view analytics.")

# ────────────────────────────────────────────────
# ADMIN Tab
# ────────────────────────────────────────────────
with tab_admin:
    st.subheader("System Administration")
    
    admin_tabs = st.tabs(["Backup & Restore", "Audit Log", "Configuration", "System Health"])
    
    with admin_tabs[0]:  # Backup & Restore
        st.markdown("### Data Backup")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Create Manual Backup", use_container_width=True):
                with st.spinner("Creating backup..."):
                    success, path, size = backup_data()
                    if success:
                        st.success(f"✅ Backup created successfully!\nPath: {path}\nSize: {size/1024:.2f} KB")
                    else:
                        st.error(f"❌ Backup failed: {path}")
        
        with col2:
            # List available backups
            try:
                conn = sqlite3.connect('fleet_management.db')
                backups_df = pd.read_sql_query('''SELECT * FROM backups ORDER BY created_at DESC LIMIT 10''', conn)
                conn.close()
                
                if not backups_df.empty:
                    selected_backup = st.selectbox(
                        "Select backup to restore",
                        options=backups_df['backup_path'].tolist(),
                        format_func=lambda x: f"{Path(x).name} ({pd.to_datetime(backups_df[backups_df['backup_path']==x]['created_at'].iloc[0]).strftime('%Y-%m-%d %H:%M')})"
                    )
                    
                    if st.button("🔄 Restore Selected Backup", type="primary", use_container_width=True):
                        if st.checkbox("I understand this will overwrite current data"):
                            with st.spinner("Restoring backup..."):
                                success, message = restore_backup(selected_backup)
                                if success:
                                    st.success(f"✅ {message}")
                                    st.cache_data.clear()
                                    st.rerun()
                                else:
                                    st.error(f"❌ {message}")
            except Exception as e:
                st.info("No backups available yet.")
    
    with admin_tabs[1]:  # Audit Log
        st.markdown("### Audit Log")
        
        try:
            conn = sqlite3.connect('fleet_management.db')
            audit_df = pd.read_sql_query('''SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT 100''', conn)
            conn.close()
            
            if not audit_df.empty:
                st.dataframe(audit_df, use_container_width=True)
                
                # Export audit log
                csv = audit_df.to_csv(index=False)
                st.download_button(
                    "📥 Download Audit Log",
                    data=csv,
                    file_name=f"audit_log_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No audit records yet.")
        except Exception as e:
            st.error(f"Error loading audit log: {e}")
    
    with admin_tabs[2]:  # Configuration
        st.markdown("### System Configuration")
        
        # Display current config
        st.json(config)
        
        if st.button("Reload Configuration"):
            st.cache_data.clear()
            st.success("Configuration reloaded!")
            st.rerun()
    
    with admin_tabs[3]:  # System Health
        st.markdown("### System Health")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Storage")
            # Check storage usage
            total_size = 0
            for vid in range(1, 4):
                if os.path.exists(f"trips_vehicle_{vid}.csv"):
                    total_size += os.path.getsize(f"trips_vehicle_{vid}.csv")
            
            if os.path.exists("fleet_management.db"):
                total_size += os.path.getsize("fleet_management.db")
            
            st.metric("Total Data Size", f"{total_size/1024:.2f} KB")
            
            # Database status
            try:
                conn = sqlite3.connect('fleet_management.db')
                c = conn.cursor()
                c.execute("SELECT COUNT(*) FROM trips")
                trip_count = c.fetchone()[0]
                c.execute("SELECT COUNT(*) FROM audit_log")
                audit_count = c.fetchone()[0]
                conn.close()
                
                st.metric("Trip Records", trip_count)
                st.metric("Audit Records", audit_count)
            except:
                st.warning("Database not initialized")
        
        with col2:
            st.markdown("#### Cache Status")
            st.metric("Cache Items", len(st.cache_data.keys()) if hasattr(st.cache_data, 'keys') else 0)
            
            if st.button("Clear Cache"):
                st.cache_data.clear()
                st.success("Cache cleared!")

# ────────────────────────────────────────────────
# Unit Tests (hidden by default)
# ────────────────────────────────────────────────
def run_tests():
    """Run unit tests"""
    st.markdown("### Running Tests")
    
    tests_passed = 0
    tests_failed = 0
    
    # Test calc_distance
    test_row1 = {"Start Odo": 1000, "End Odo": 1200, "Purpose": "Trip"}
    result1 = calc_distance(test_row1)
    if result1 == 200:
        st.success("✅ calc_distance test 1 passed")
        tests_passed += 1
    else:
        st.error(f"❌ calc_distance test 1 failed: got {result1}, expected 200")
        tests_failed += 1
    
    test_row2 = {"Start Odo": 1200, "End Odo": 1000, "Purpose": "Trip"}
    result2 = calc_distance(test_row2)
    if result2 == 0:
        st.success("✅ calc_distance test 2 passed")
        tests_passed += 1
    else:
        st.error(f"❌ calc_distance test 2 failed: got {result2}, expected 0")
        tests_failed += 1
    
    # Test fuel efficiency
    test_df = pd.DataFrame({
        'Distance (km)': [100, 200],
        'Fuel Added (L)': [10, 20]
    })
    result3 = calculate_fuel_efficiency(test_df)
    if abs(result3 - 10.0) < 0.01:
        st.success("✅ fuel efficiency test passed")
        tests_passed += 1
    else:
        st.error(f"❌ fuel efficiency test failed: got {result3}, expected 10.0")
        tests_failed += 1
    
    st.metric("Tests Passed", tests_passed)
    st.metric("Tests Failed", tests_failed)

# Add test runner in admin tab (hidden by default)
if st.sidebar.checkbox("🧪 Run Tests", value=False):
    run_tests()

st.markdown("---")
st.caption(f"© Department of Justice and Constitutional Development • {datetime.now().year} • Internal use only")
