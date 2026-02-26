import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import sqlite3
import shutil
import os
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ────────────────────────────────────────────────
# Configuration
# ────────────────────────────────────────────────
APP_NAME = "DOJ&CD - MC Tsakane Dashboard"
DB_FILE = "fleet_management.db"
BACKUP_DIR = "backups"
os.makedirs(BACKUP_DIR, exist_ok=True)

VEHICLES = [
    {"id": 1, "reg": "LR 93 VW GP", "short": "Vehicle 1"},
    {"id": 2, "reg": "BW 47 KG GP", "short": "Vehicle 2"},
    {"id": 3, "reg": "JM 45 CY GP", "short": "Vehicle 3"},
]

DRIVERS = ["MF Neludi", "SA Ndlela", "S Mothoa", "J Ndou", "FV Mkhwanazi", "ML Kgakatsi"]

ROWS_PER_PAGE = 20
MAX_DAILY_DISTANCE = 2000
ALERT_THRESHOLDS = {
    "fuel_low": 20,
    "service_km_warning": 5000,
    "service_days_warning": 90,
    "service_km_due": 2000,
    "service_days_due": 30
}

# ────────────────────────────────────────────────
# Database Setup
# ────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Trips table
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
    
    # Audit log
    c.execute('''CREATE TABLE IF NOT EXISTS audit_log
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user TEXT,
                  action TEXT,
                  vehicle_id INTEGER,
                  details TEXT,
                  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Backups log
    c.execute('''CREATE TABLE IF NOT EXISTS backups
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  backup_path TEXT,
                  size_bytes INTEGER,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.commit()
    conn.close()

init_db()

# ────────────────────────────────────────────────
# Helper Functions
# ────────────────────────────────────────────────
def log_audit(user, action, vehicle_id=None, details=None):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''INSERT INTO audit_log (user, action, vehicle_id, details)
                 VALUES (?, ?, ?, ?)''', (user, action, vehicle_id, details))
    conn.commit()
    conn.close()

def create_backup():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"backup_{timestamp}")
    os.makedirs(backup_path, exist_ok=True)
    
    total_size = 0
    for file in [DB_FILE] + [f"trips_vehicle_{v['id']}.csv" for v in VEHICLES if os.path.exists(f"trips_vehicle_{v['id']}.csv")]:
        if os.path.exists(file):
            shutil.copy2(file, backup_path)
            total_size += os.path.getsize(file)
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''INSERT INTO backups (backup_path, size_bytes) VALUES (?, ?)''', (backup_path, total_size))
    conn.commit()
    conn.close()
    
    log_audit(st.session_state.get("user", "system"), "backup_created", details=f"Size: {total_size} bytes")
    return backup_path, total_size

def load_trips(vid):
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM trips WHERE vehicle_id = ? ORDER BY date DESC, time DESC", conn, params=(vid,))
    conn.close()
    
    if not df.empty:
        df = df.rename(columns={
            'date': 'Date', 'time': 'Time', 'driver': 'Driver', 'purpose': 'Purpose',
            'start_odo': 'Start Odo', 'end_odo': 'End Odo', 'distance': 'Distance (km)',
            'fuel_added': 'Fuel Added (L)', 'fuel_cost': 'Fuel Cost (R)',
            'odo_at_refuel': 'Odo at Refuel', 'toll_amount': 'Toll Amount (R)',
            'toll_plaza_notes': 'Toll Plaza / Notes'
        })
        df['Date'] = pd.to_datetime(df['Date'])
    else:
        df = pd.DataFrame(columns=["Date", "Time", "Driver", "Purpose", "Start Odo", "End Odo", "Distance (km)",
                                   "Fuel Added (L)", "Fuel Cost (R)", "Odo at Refuel", "Toll Amount (R)", "Toll Plaza / Notes"])
    
    return df

def save_trip(vid, row_dict):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute('''INSERT INTO trips 
                 (vehicle_id, date, time, driver, purpose, start_odo, end_odo, distance,
                  fuel_added, fuel_cost, odo_at_refuel, toll_amount, toll_plaza_notes)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (vid, row_dict['Date'].strftime('%Y-%m-%d'), row_dict.get('Time'), row_dict['Driver'],
               row_dict['Purpose'], row_dict['Start Odo'], row_dict['End Odo'], row_dict['Distance (km)'],
               row_dict['Fuel Added (L)'], row_dict['Fuel Cost (R)'], row_dict['Odo at Refuel'],
               row_dict['Toll Amount (R)'], row_dict['Toll Plaza / Notes']))
    
    conn.commit()
    conn.close()
    log_audit(st.session_state.get("user", "system"), "trip_added", vid, f"Added trip: {row_dict['Driver']}")

# ────────────────────────────────────────────────
# Authentication
# ────────────────────────────────────────────────
def check_auth():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.title("Login – DOJ&CD Fleet Dashboard")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if password == "admin123":  # Change in production!
                st.session_state.authenticated = True
                st.session_state.user = "admin"
                st.rerun()
            else:
                st.error("Invalid password")
        st.stop()

check_auth()

# ────────────────────────────────────────────────
# Header
# ────────────────────────────────────────────────
st.markdown('<div class="header">', unsafe_allow_html=True)
col1, col2 = st.columns([1, 5])
with col1:
    st.image("https://upload.wikimedia.org/wikipedia/commons/e/e9/Coat_of_arms_of_South_Africa.svg", width=120)
with col2:
    st.markdown(f"<h1>{APP_NAME}</h1><h3>Department of Justice and Constitutional Development</h3>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ────────────────────────────────────────────────
# Tabs
# ────────────────────────────────────────────────
tab_home, tab_sundry, tab_fleet, tab_admin = st.tabs(["HOME", "SUNDRY", "FLEET", "ADMIN"])

# ────────────────────────────────────────────────
# HOME
# ────────────────────────────────────────────────
with tab_home:
    st.subheader("Witness Fees – Monthly Overview")
    # ... (keep your existing witness fees chart code here)

# ────────────────────────────────────────────────
# SUNDRY (witness fees register)
# ────────────────────────────────────────────────
with tab_sundry:
    st.subheader("Witness Fees Register")
    # ... (keep your existing witness fees code here)

# ────────────────────────────────────────────────
# FLEET SERVICES
# ────────────────────────────────────────────────
with tab_fleet:
    st.subheader("Fleet Services – Gauteng Region")
    vehicle_tabs = st.tabs([f"{v['short']} ({v['reg']})" for v in VEHICLES])

    for idx, vtab in enumerate(vehicle_tabs):
        veh = VEHICLES[idx]
        vid = veh["id"]
        reg = veh["reg"]
        status = get_vehicle_status(vid)
        current_trips = load_trips(vid)

        with vtab:
            st.markdown(f"### {reg}")
            
            # Status cards
            c1, c2, c3 = st.columns([2, 2, 1.4])
            c1.markdown(f"**Location:** {status['location']}")
            fuel_color = "green" if status["fuel"] > 50 else "orange" if status["fuel"] > 20 else "red"
            c2.markdown(f"**Fuel:** <span style='color:{fuel_color}'>{status['fuel']}%</span>", unsafe_allow_html=True)
            c2.progress(status["fuel"] / 100)
            c2.markdown(f"**Odometer:** {status['odo']:,} km")
            c3.markdown(f"**Last Service:** {status['last_service']}")
            c3.markdown(f"**Alerts:** {status['alerts']}")

            # Import section
            with st.expander("📤 Import trips from CSV/Excel"):
                uploaded = st.file_uploader("Upload file", type=["csv", "xlsx", "xls"], key=f"upload_{vid}")
                if uploaded:
                    try:
                        if uploaded.name.endswith("csv"):
                            df_new = pd.read_csv(uploaded)
                        else:
                            df_new = pd.read_excel(uploaded)
                        
                        # Append logic here (similar to before)
                        # Validate, clean, save_trip for each row...
                        st.success("Imported successfully!")
                    except Exception as e:
                        st.error(f"Import failed: {e}")

            # Rest of your fleet UI (trip logs, add forms, report, etc.)
            # ... paste the remaining fleet code with unique keys ...

# ────────────────────────────────────────────────
# ADMIN
# ────────────────────────────────────────────────
with tab_admin:
    st.subheader("Admin Panel")
    # Backup, audit, config, health sections...

st.markdown("---")
st.caption(f"© DOJ&CD • {datetime.now().year} • Internal use only")
