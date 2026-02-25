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
            key=f"month_selector_vehicle_{vid}"  # ← this prevents the duplicate ID error
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
