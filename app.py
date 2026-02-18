import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="Tsakane Dashboard", layout="wide", page_icon="🇿🇦")

# ================== CUSTOM STYLING ==================
st.markdown("""
    <style>
    .tsakane-banner {
        background-color: #FFB612;
        color: #000000;
        padding: 40px 20px;
        text-align: center;
        border-radius: 0 0 15px 15px;
        box-shadow: 0 6px 12px rgba(0,0,0,0.2);
        margin-bottom: 30px;
    }
    .tsakane-title { font-size: 3.5rem; font-weight: bold; margin: 0; }
    .tsakane-subtitle { font-size: 1.5rem; margin: 10px 0 0; }
    .kpi-card {
        background: #ffffff;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# ================== ORANGE BANNER ==================
st.markdown("""
    <div class="tsakane-banner">
        <h1 class="tsakane-title">Tsakane Dashboard</h1>
        <p class="tsakane-subtitle">Joy in Every Operation • Internal Tool 🇿🇦</p>
    </div>
""", unsafe_allow_html=True)

# ================== SIDEBAR NAV ==================
st.sidebar.title("NAVIGATION")
nav_options = [
    "Sundry", "Fleet Services", "Receipts", "Invoices", "MOJAPAY",
    "TWF", "Registers", "Checklists", "Circulars", "Subsistence"
]
selected_section = st.sidebar.radio("Main Sections", nav_options)

# ================== DASHBOARD OVERVIEW (always visible) ==================
st.subheader("Dashboard Overview")
kpi_cols = st.columns(4)
with kpi_cols[0]: st.metric("Pending Invoices", "1,342", "+48 today")
with kpi_cols[1]: st.metric("Receipts This Month", "R 2.8M", "↑ 12%")
with kpi_cols[2]: st.metric("Upcoming CIT Collections", "18", "Next: Tomorrow JHB")
with kpi_cols[3]: st.metric("Subsistence Claims Pending", "92", "Total: 456")

# ================== SUNDRY TABLE (your requested table) ==================
if selected_section == "Sundry":
    st.subheader("🧾 Sundry – Witness Fees & Transport Claims")
    st.caption("Fill the form below → Return Trip, PAYE and Gross calculate automatically")

    # Initialize table in session state
    if "sundry_df" not in st.session_state:
        st.session_state.sundry_df = pd.DataFrame(columns=[
            "#", "DATE", "DISTRICT VOUCHER", "REGIONAL VOUCHER", "PAYEE",
            "CASE NUMBER", "SINGLE TRIP", "RETURN TRIP", "MODE OF TRANSP",
            "VOUCHER", "PAYE", "LUNCH", "GROSS"
        ])

    # Add new entry form
    with st.form("sundry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            entry_date = st.date_input("DATE", value=date.today())
            dist_voucher = st.text_input("DISTRICT VOUCHER")
            reg_voucher = st.text_input("REGIONAL VOUCHER")
            payee = st.text_input("PAYEE")
            case_number = st.text_input("CASE NUMBER")
        with col2:
            single_trip = st.number_input("SINGLE TRIP (R)", min_value=0.0, step=10.0, format="%.2f")
            mode_transport = st.selectbox("MODE OF TRANSP", ["Private", "Taxi", "Bus"])
            lunch = st.number_input("LUNCH (R)", min_value=0.0, step=10.0, format="%.2f")
            voucher = st.text_input("VOUCHER")

        submitted = st.form_submit_button("✅ Add Entry")

        if submitted:
            return_trip = single_trip * 2
            paye_amount = return_trip * 0.25 if mode_transport == "Private" else 0.0
            gross_amount = lunch + return_trip - paye_amount

            new_row = {
                "#": len(st.session_state.sundry_df) + 1,
                "DATE": entry_date,
                "DISTRICT VOUCHER": dist_voucher,
                "REGIONAL VOUCHER": reg_voucher,
                "PAYEE": payee,
                "CASE NUMBER": case_number,
                "SINGLE TRIP": single_trip,
                "RETURN TRIP": return_trip,
                "MODE OF TRANSP": mode_transport,
                "VOUCHER": voucher,
                "PAYE": paye_amount,
                "LUNCH": lunch,
                "GROSS": gross_amount
            }

            st.session_state.sundry_df = pd.concat(
                [st.session_state.sundry_df, pd.DataFrame([new_row])],
                ignore_index=True
            )
            st.success("Entry added successfully!")

    # Display the live table
    if not st.session_state.sundry_df.empty:
        # Nice currency formatting
        styled_df = st.session_state.sundry_df.style.format({
            "SINGLE TRIP": "R{:,.2f}",
            "RETURN TRIP": "R{:,.2f}",
            "PAYE": "R{:,.2f}",
            "LUNCH": "R{:,.2f}",
            "GROSS": "R{:,.2f}"
        }).set_properties(**{'text-align': 'right'}, subset=["SINGLE TRIP", "RETURN TRIP", "PAYE", "LUNCH", "GROSS"])

        st.dataframe(styled_df, use_container_width=True, height=400)

        # Total summary
        total_gross = st.session_state.sundry_df["GROSS"].sum()
        st.metric("💰 TOTAL MONEY SPENT ON WITNESS FEES (Gross)", f"R {total_gross:,.2f}")

        # Download button
        csv = st.session_state.sundry_df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV (Excel)",
            data=csv,
            file_name="Tsakane_Sundry_Witness_Fees.csv",
            mime="text/csv"
        )

        if st.button("🗑️ Clear All Entries"):
            st.session_state.sundry_df = pd.DataFrame(columns=st.session_state.sundry_df.columns)
            st.rerun()
    else:
        st.info("No entries yet. Use the form above to start adding witness fees.")

else:
    st.subheader(f"{selected_section} Section")
    st.info("This section is coming soon. Tell me what you want to add next!")

# Footer
st.markdown("---")
st.caption("Tsakane Dashboard • Internal Use Only • Ekurhuleni / Gauteng • © 2026")
