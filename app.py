# ────────────────────────────────────────────────
# FLEET SERVICES – one tab per vehicle
# ────────────────────────────────────────────────
with tab_fleet:
    st.subheader("Fleet Services – Gauteng Region")

    vehicles = [
        {"id":1, "reg":"JM 45 CY GP", "short":"Vehicle 1"},
        {"id":2, "reg":"BW 47 KG GP", "short":"Vehicle 2"},
        {"id":3, "reg":"LR 93 VW GP", "short":"Vehicle 3"},
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

            # No key on markdown
            c1.markdown(f"**Location**  \n{status['location']}")
            
            fuel_color = "green" if status["fuel"] > 50 else "orange" if status["fuel"] > 20 else "red"
            with c2:
                # No key on markdown
                c2.markdown(f"**Fuel**  \n<span style='color:{fuel_color}'>{status['fuel']}%</span>", unsafe_allow_html=True)
                # Progress DOES support key
                c2.progress(status["fuel"] / 100, key=f"fuel_prog_{vid}")
                # No key on markdown
                c2.markdown(f"**Odometer**  \n{status['odo']:,} km")

            alert_cls = "status-good" if "None" in status["alerts"] else "status-warning" if "Low" in status["alerts"] else "status-alert"
            # No key on markdown
            c3.markdown(f"**Last service**  \n{status['last_service']}")
            # No key on markdown
            c3.markdown(f"**Alerts**  \n<span class='{alert_cls}'>{status['alerts']}</span>", unsafe_allow_html=True)

            # ────────────────────────────────
            # Mileage chart – key IS allowed
            dates = [datetime.now().date() - timedelta(days=x) for x in range(13, -1, -1)]
            km = [45, 0, 120, 85, 0, 60, 30, 95, 110, 20, 75, 0, 55, 140]  # dummy
            df_m = pd.DataFrame({"Date": dates, "km": km})
            fig = px.line(df_m, x="Date", y="km", title="Last 14 days mileage")
            fig.update_traces(line_color="#005c28")
            st.plotly_chart(fig, use_container_width=True, key=f"mileage_chart_{vid}")

            # ────────────────────────────────
            # Trips table – key IS allowed
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
                key=f"trips_{vid}"
            )

            if not edited_trips.empty:
                tot_km = edited_trips["Distance"].sum()
                st.metric("Total distance (shown trips)", f"{tot_km:,} km", key=f"total_km_{vid}")
