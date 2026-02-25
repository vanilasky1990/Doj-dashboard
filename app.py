# ────────────────────────────────────────────────
# Updated CSS for solid orange header
# ────────────────────────────────────────────────
st.markdown("""
    <style>
    .stApp { background-color: #f9fbfd; }
    .header { 
        background-color: #FFB612;          /* solid orange/yellow */
        color: #1a1a1a;                     /* dark text for contrast */
        padding: 25px 20px; 
        text-align: center; 
        border-bottom: 4px solid #005c28;   /* green bottom border for contrast */
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .header h1 { 
        margin: 0; 
        font-size: 2.5rem; 
        font-weight: 700; 
    }
    .header h3 { 
        margin: 8px 0 0; 
        font-size: 1.4rem; 
        font-weight: 400; 
    }
    .header p { 
        margin: 8px 0 0; 
        font-size: 1.1rem; 
        opacity: 0.9; 
    }
    </style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────
# Header with solid orange background
# ────────────────────────────────────────────────
st.markdown('<div class="header">', unsafe_allow_html=True)
st.image(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Coat_of_arms_of_South_Africa.svg/200px-Coat_of_arms_of_South_Africa.svg.png",
    width=140
)
st.markdown(f"""
    <h1>MC Tsakane Dashboard</h1>
    <h3>Department of Justice and Constitutional Development</h3>
    <p>Internal Use • {datetime.now().year}</p>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
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
# Header
# ────────────────────────────────────────────────
st.markdown('<div class="header">', unsafe_allow_html=True)
st.image(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Coat_of_arms_of_South_Africa.svg/200px-Coat_of_arms_of_South_Africa.svg.png",
    width=140
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
# HOME – Witness Fees chart
# ────────────────────────────────────────────────
with tab_home:
    st.subheader("Witness Fees – Monthly Expenditure")
    
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    amounts = [45000, 62000, 38000, 75000, 51000, 89000, 42000, 67000, 93000, 55000, 48000, 72000]
    
    df = pd.DataFrame({"Month": months, "Amount (ZAR)": amounts})
    
    fig = px.bar(
        df,
        x="Month",
        y="Amount (ZAR)",
        title=f"Monthly Witness Fees {datetime.now().year}",
        color="Amount (ZAR)",
        color_continuous_scale="Greens",
        text_auto=",.0f"
    )
    fig.update_layout(showlegend=False)
    
    st.plotly_chart(fig, use_container_width=True, key="home_witness_chart")

    if st.button("Go to detailed table →"):
        st.info("Switch to the SUNDRY tab above")

# ────────────────────────────────────────────────
# SUNDRY – Witness fees table
# ────────────────────────────────────────────────
with tab_sundry:
    st.subheader("Witness Fees Register")

    sample = {
        "Date": ["2026-01-15", "2026-01-22", "2026-02-05", "2026-02-10", "2026-02-18"],
        "Witness Name": ["A. Nkosi", "B. Mthembu", "C. v/d Merwe", "D. Pillay", "E. Sithole"],
        "Case Number": ["JHB/2026/001", "CPT/2026/045", "DBN/2026/112", "JHB/2026/078", "PE/2026/023"],
        "Amount Paid (ZAR)": [1200.00, 850.00, 1500.00, 950.00, 1100.00],
        "Status": ["Paid", "Pending Approval", "Paid", "Awaiting Receipt", "Paid"],
        "Court/Office": ["JHB Magistrate", "CPT High", "DBN Regional", "JHB High", "PE Magistrate"]
    }

    df = pd.DataFrame(sample)
    edited = st.data_editor(df, num_rows="dynamic", use_container_width=True, key="sundry_witness_editor")

    total = edited["Amount Paid (ZAR)"].sum()
    pending = edited[edited["Status"].isin(["Pending Approval", "Awaiting Receipt"])]["Amount Paid (ZAR)"].sum()

    col1, col2 = st.columns(2)
    col1.metric("Total Spent", f"R {total:,.2f}")
    col2.metric("Pending / Awaiting", f"R {pending:,.2f}")

with tab_fleet:
    st.subheader("Fleet Services – Gauteng Region")

    vehicles = [
        {"id": 1, "reg": "JM 45 CY GP", "short": "Vehicle 1"},
        {"id": 2, "reg": "BW 47 KG GP", "short": "Vehicle 2"},
        {"id": 3, "reg": "LR 93 VW GP", "short": "Vehicle 3"},
    ]

    tabs = st.tabs([f"{v['short']} ({v['reg']})" for v in vehicles])

    for i, tab in enumerate(tabs):
        veh = vehicles[i]
        vid = veh["id"]
        reg = veh["reg"]
        status = get_vehicle_status(vid)

        with tab:
            st.markdown(f"### {reg}")

            c1, c2, c3 = st.columns([2, 2, 1.4])

            c1.markdown(f"**Location**  \n{status['location']}")

            fuel_color = "green" if status["fuel"] > 50 else "orange" if status["fuel"] > 20 else "red"
            with c2:
                c2.markdown(f"**Fuel**  \n<span style='color:{fuel_color}'>{status['fuel']}%</span>", unsafe_allow_html=True)
                c2.progress(status["fuel"] / 100)
                c2.markdown(f"**Odometer**  \n{status['odo']:,} km")

            alert_cls = "status-good" if "None" in status["alerts"] else "status-warning" if "Low" in status["alerts"] else "status-alert"
            c3.markdown(f"**Last service**  \n{status['last_service']}")
            c3.markdown(f"**Alerts**  \n<span class='{alert_cls}'>{status['alerts']}</span>", unsafe_allow_html=True)

            # Mileage chart – this one usually works with key
            dates = [datetime.now().date() - timedelta(days=x) for x in range(13, -1, -1)]
            km = [45, 0, 120, 85, 0, 60, 30, 95, 110, 20, 75, 0, 55, 140]
            df_m = pd.DataFrame({"Date": dates, "km": km})
            fig = px.line(df_m, x="Date", y="km", title="Last 14 days mileage")
            fig.update_traces(line_color="#005c28")
            st.plotly_chart(fig, use_container_width=True, key=f"mileage_chart_{vid}")

            # Trips
            st.subheader("Recent trips")
            trips = pd.DataFrame({
                "Date":      ["2026-02-20", "2026-02-15", "2026-02-10", "2026-02-05"],
                "Driver":    ["J. Smith", "A. Nkosi", "M. Botha", "S. Naidoo"],
                "Purpose":   ["Court", "Inspection", "Maintenance", "Transfer"],
                "Start Odo": [124600, 124500, 124200, 123900],
                "End Odo":   [124950, 124850, 124400, 124150],
                "Distance":  [350, 350, 200, 250],
            })
            edited_trips = st.data_editor(
                trips,
                num_rows="dynamic",
                use_container_width=True,
                key=f"trips_editor_{vid}"           # this should be safe
            )

            if not edited_trips.empty:
                tot_km = edited_trips["Distance"].sum()
                st.metric("Total distance (shown trips)", f"{tot_km:,} km")   # no key here
# Footer
# ────────────────────────────────────────────────
st.markdown("---")
st.caption(f"© DOJ&CD • {datetime.now().year} • Internal use only")
