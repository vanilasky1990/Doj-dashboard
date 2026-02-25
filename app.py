import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta, time
from typing import Dict
import io

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
    
    next_by_time = last_date + timedelta(days=180)  # 6 months
    
    km_since_last_service = status["odo"] % 15000
    km_remaining = 15000 - km_since_last_service
    next_by_km = f"+{km_remaining:,} km"
    
    return next_by_time.strftime("%Y-%m-%d"), next_by_km, km_remaining

# ────────────────────────────────────────────────
# Header with fixed coat of arms URL
# ────────────────────────────────────────────────
st.markdown('<div class="header">', unsafe_allow_html=True)
st.image(
    "https://upload.wikimedia.org/wikipedia/commons/e/e9/Coat_of_arms_of_South_Africa.svg",
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
# HOME TAB
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

    # Fleet Health & Service Overview
    st.markdown("---")
    st.subheader("🚗 Fleet Health & Service Overview")
    st.markdown("Current status and estimated next service (6 months **or** 15,000 km interval).")

    vehicles = [
        {"id": 1, "reg": "JM 45 CY GP"},
        {"id": 2, "reg": "BW 47 KG GP"},
        {"id": 3, "reg": "LR 93 VW GP"},
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

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Vehicles", len(vehicles))
    avg_fuel = sum(get_vehicle_status(i)["fuel"] for i in range(1, 4)) / len(vehicles)
    col2.metric("Avg Fuel Level", f"{avg_fuel:.0f}%")
    total_odo = sum(get_vehicle_status(i)["odo"] for i in range(1, 4))
    col3.metric("Total Fleet Odometer", f"{total_odo:,} km")
    due_soon = len([r for r in summary_data if "Due Soon" in r["Status"]])
    col4.metric("Vehicles Needing Attention", due_soon)

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

    st.caption("Next service triggered by whichever comes first: 6 months or 15,000 km since last service.")

# ================================================
# SUNDRY TAB
# ================================================
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

# ================================================
# FLEET SERVICES TAB – with auto-calculated Distance (read-only)
# ================================================
with tab_fleet:
    st.subheader("Fleet Services – Gauteng Region")
    st.markdown("Vehicle tracking, fuel status, odometer, alerts & recent trips/logs (multiple tolls per day supported).")

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

        session_key = f"trips_vehicle_{vid}"
        if session_key not in st.session_state:
            st.session_state[session_key] = pd.DataFrame({
                "Date": pd.to_datetime(["2026-02-20", "2026-02-20", "2026-02-20", "2026-02-20", "2026-02-15"]),
                "Time": [time(8, 45), time(10, 15), time(13, 40), time(15, 20), None],
                "Driver": ["J. Smith", "J. Smith", "J. Smith", "J. Smith", "A. Nkosi"],
                "Purpose": ["Court transfer JHB-DBN", "Toll", "Toll", "Toll", "Site inspection"],
                "Start Odo": [124600, 124700, 124820, 124900, 124500],
                "End Odo": [124950, 124700, 124820, 124900, 124850],
                "Distance (km)": [350, 0, 0, 0, 350],
                "Fuel Added (L)": [0.0, 0.0, 0.0, 0.0, 40.0],
                "Fuel Cost (R)": [0.00, 0.00, 0.00, 0.00, 880.00],
                "Odo at Refuel": [0, 0, 0, 0, 124520],
                "Toll Amount (R)": [0.00, 45.00, 28.50, 17.00, 0.00],
                "Toll Plaza / Notes": ["", "N3 Mariannhill", "N3 Cedara", "N3 Westville", ""]
            })

        current_trips = st.session_state[session_key].copy()

        # Auto-calculate Distance before displaying (read-only)
        current_trips["Distance (km)"] = current_trips.apply(
            lambda row: max(0, row["End Odo"] - row["Start Odo"])
            if pd.notna(row["Start Odo"]) and pd.notna(row["End Odo"])
            else row.get("Distance (km)", 0),
            axis=1
        )

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

            # Mileage Trend – real data from table
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

            # Trip Logs + Monthly Report sub-tabs
            subtab_logs, subtab_report = st.tabs(["Trip Logs", "Monthly Report"])

            with subtab_logs:
                st.subheader(f"Recent trips / logs – {reg}")
                st.caption("Distance is auto-calculated from End Odo - Start Odo (read-only). Add multiple toll rows for the same day with different times.")

                column_config = {
                    "Date": st.column_config.DateColumn("Date", format="YYYY-MM-DD", required=True),
                    "Time": st.column_config.TimeColumn("Time", format="HH:mm", step=60, help="Approximate time of toll payment"),
                    "Driver": st.column_config.TextColumn("Driver", required=True),
                    "Purpose": st.column_config.TextColumn("Purpose"),
                    "Start Odo": st.column_config.NumberColumn("Start Odo", min_value=0, format="%d km"),
                    "End Odo": st.column_config.NumberColumn("End Odo", min_value=0, format="%d km"),
                    "Distance (km)": st.column_config.NumberColumn(
                        "Distance (km)",
                        min_value=0,
                        format="%d km",
                        disabled=True,  # Read-only & auto-calculated
                        help="Automatically calculated as End Odo - Start Odo"
                    ),
                    "Fuel Added (L)": st.column_config.NumberColumn("Fuel Added (L)", min_value=0.0, format="%.1f L"),
                    "Fuel Cost (R)": st.column_config.NumberColumn("Fuel Cost (R)", min_value=0.0, format="R %.2f"),
                    "Odo at Refuel": st.column_config.NumberColumn("Odo at Refuel", min_value=0, format="%d km"),
                    "Toll Amount (R)": st.column_config.NumberColumn("Toll Amount (R)", min_value=0.0, format="R %.2f"),
                    "Toll Plaza / Notes": st.column_config.TextColumn("Toll Plaza / Notes")
                }

                # Manual pagination (20 rows per page)
                rows_per_page = 20
                total_rows = len(current_trips)
                total_pages = max(1, (total_rows + rows_per_page - 1) // rows_per_page)

                # Page selector
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

                # Slice data for current page
                start_idx = (page - 1) * rows_per_page
                end_idx = start_idx + rows_per_page
                page_data = current_trips.iloc[start_idx:end_idx]

                edited_page = st.data_editor(
                    page_data,
                    column_config=column_config,
                    num_rows="dynamic",
                    use_container_width=True,
                    hide_index=True,
                    key=f"trips_editor_page_{vid}_{page}"
                )

                # Update full data from edited page (only current page)
                if not edited_page.empty:
                    current_trips.iloc[start_idx:end_idx] = edited_page
                    st.session_state[session_key] = current_trips

                st.caption(f"Showing rows {start_idx+1}–{min(end_idx, total_rows)} of {total_rows}")
                st.metric("Total log entries", total_rows, delta=None)

                if total_rows > 0:
                    total_distance = current_trips["Distance (km)"].sum()
                    total_fuel_cost = current_trips["Fuel Cost (R)"].sum()
                    total_tolls = current_trips["Toll Amount (R)"].sum()

                    colA, colB, colC = st.columns(3)
                    colA.metric("Total Distance", f"{total_distance:,} km")
                    colB.metric("Total Fuel Cost", f"R {total_fuel_cost:,.2f}")
                    colC.metric("Total Tolls Paid", f"R {total_tolls:,.2f}")

                with st.expander("➕ Add Fuel Slip", expanded=False):
                    with st.form(key=f"add_fuel_form_{vid}"):
                        col_date, col_odo = st.columns(2)
                        fuel_date = col_date.date_input("Refuelling date", value=datetime.now().date())
                        fuel_odo = col_odo.number_input("Odometer at refuel (km)", min_value=0, value=status["odo"], step=1)

                        col_litres, col_cost = st.columns(2)
                        fuel_litres = col_litres.number_input("Litres added", min_value=0.0, step=0.1, format="%.1f")
                        fuel_cost = col_cost.number_input("Total fuel cost (R)", min_value=0.0, step=1.0, format="%.2f")

                        fuel_notes = st.text_input("Fuel station / Notes", "")

                        if st.form_submit_button("Add Fuel Slip", type="primary"):
                            new_row = pd.DataFrame([{
                                "Date": pd.to_datetime(fuel_date),
                                "Time": None,
                                "Driver": "—",
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

                            st.session_state[session_key] = pd.concat(
                                [st.session_state[session_key], new_row],
                                ignore_index=True
                            )
                            st.success("Fuel slip added!")
                            st.rerun()

                with st.expander("➕ Add Toll Slip", expanded=False):
                    st.caption("For multiple tolls on the same day → submit the form multiple times with different times.")
                    
                    with st.form(key=f"add_toll_form_{vid}"):
                        col_date, col_time = st.columns(2)
                        toll_date = col_date.date_input("Toll date", value=datetime.now().date())
                        toll_time = col_time.time_input("Approximate toll time", value=time(8, 0), step=60)

                        col_amount, _ = st.columns([1, 1])
                        toll_amount = col_amount.number_input("Toll amount (R)", min_value=0.0, step=1.0, format="%.2f")

                        toll_plaza = st.text_input("Toll plaza / Route", "")
                        toll_notes = st.text_input("Additional notes / Invoice nr", "")

                        if st.form_submit_button("Add Toll Slip", type="primary"):
                            new_row = pd.DataFrame([{
                                "Date": pd.to_datetime(toll_date),
                                "Time": toll_time,
                                "Driver": "—",
                                "Purpose": "Toll payment",
                                "Start Odo": status["odo"],
                                "End Odo": status["odo"],
                                "Distance (km)": 0,
                                "Fuel Added (L)": 0.0,
                                "Fuel Cost (R)": 0.0,
                                "Odo at Refuel": 0,
                                "Toll Amount (R)": toll_amount,
                                "Toll Plaza / Notes": f"{toll_plaza} – {toll_notes}".strip(" – ")
                            }])

                            st.session_state[session_key] = pd.concat(
                                [st.session_state[session_key], new_row],
                                ignore_index=True
                            )
                            st.success("Toll slip added!")
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

                    # Summary aggregates
                    monthly_summary = monthly_trips.agg({
                        'Distance (km)': 'sum',
                        'Fuel Cost (R)': 'sum',
                        'Toll Amount (R)': 'sum',
                        'Fuel Added (L)': 'sum'
                    }).to_frame(name='Total').T

                    st.markdown("#### Monthly Summary")
                    st.dataframe(monthly_summary, use_container_width=True)

                    # All trips for the month
                    st.markdown("#### All Trips & Slips in Selected Month")
                    st.dataframe(
                        monthly_trips,
                        use_container_width=True,
                        column_config=column_config,
                        hide_index=False
                    )

                    # Bar chart
                    fig_month = px.bar(monthly_summary.T.reset_index(),
                                       x='index', y='Total',
                                       title=f"Summary for {selected_month_str}",
                                       labels={'index': 'Category', 'Total': 'Amount'})
                    st.plotly_chart(
                        fig_month,
                        use_container_width=True,
                        key=f"monthly_report_chart_vehicle_{vid}_{selected_month_str}"
                    )

                    # CSV Export
                    csv_buffer = io.StringIO()
                    monthly_trips.to_csv(csv_buffer, index=False)
                    csv_data = csv_buffer.getvalue()

                    filename_csv = f"Trips_{reg.replace(' ', '_')}_{selected_month_str}.csv"

                    st.download_button(
                        label="📥 Download Full Monthly Trips (CSV)",
                        data=csv_data,
                        file_name=filename_csv,
                        mime="text/csv",
                        key=f"download_csv_{vid}_{selected_month_str}"
                    )

                    # Excel Export
                    excel_buffer = io.BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                        monthly_trips.to_excel(writer, sheet_name='Trips & Slips', index=False)
                        monthly_summary.to_excel(writer, sheet_name='Summary')

                    excel_buffer.seek(0)

                    filename_excel = f"Monthly_Report_{reg.replace(' ', '_')}_{selected_month_str}.xlsx"

                    st.download_button(
                        label="📊 Download Monthly Report (Excel .xlsx)",
                        data=excel_buffer,
                        file_name=filename_excel,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key=f"download_excel_{vid}_{selected_month_str}"
                    )

                else:
                    st.info("No trip data yet. Add entries in the Trip Logs tab.")

# ────────────────────────────────────────────────
# Footer
# ────────────────────────────────────────────────
st.markdown("---")
st.caption(f"© Department of Justice and Constitutional Development • {datetime.now().year} • Internal use only")
