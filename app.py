# app.py - Minimal DOJ&CD Dashboard with Official Color Scheme
import streamlit as st

# Page config
st.set_page_config(
    page_title="DOJ&CD Internal Dashboard",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Clean CSS with DOJ&CD / Government green scheme
# Solid orange banner header
st.markdown("""
    <style>
    .tsakane-banner {
        background-color: #FFB612;  /* Solid orange - change to #FF7A01 if you want brighter */
        color: #000000;             /* Black text for strong contrast, or #FFFFFF for white */
        padding: 40px 20px;
        text-align: center;
        border-radius: 0 0 15px 15px;  /* Rounded bottom corners for modern look */
        box-shadow: 0 6px 12px rgba(0,0,0,0.2);
        margin-bottom: 30px;
        font-family: 'Arial Black', sans-serif;
    }
    .tsakane-title {
        margin: 0;
        font-size: 3.2rem;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .tsakane-subtitle {
        margin: 10px 0 0;
        font-size: 1.4rem;
        opacity: 0.9;
    }
    </style>

    <div class="tsakane-banner">
        <h1 class="tsakane-title">Tsakane Dashboard</h1>
        <p class="tsakane-subtitle">Joy in Every Operation • Ekurhuleni Internal Tool 🇿🇦</p>
    </div>
""", unsafe_allow_html=True)

# Header with Logo & Official Colors
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

# Tabs
tab_home, tab_sundry = st.tabs(["HOME", "SUNDRY"])

# HOME tab
with tab_home:
    st.markdown("<h2 style='text-align: center; color: #005c28; margin-top: 40px;'>Welcome to the DOJ&CD Internal Dashboard</h2>", unsafe_allow_html=True)
    
    st.markdown("""
        <p style='text-align: center; font-size: 1.2rem; color: #555; max-width: 700px; margin: 20px auto;'>
            This secure portal supports key administrative and financial operations.<br>
            Start by selecting a section above.
        </p>
    """, unsafe_allow_html=True)
    
    if st.button("Go to Sundry Section"):
        st.success("Switch to the **SUNDRY** tab above to continue.")
    
    st.markdown("<hr style='margin: 50px 0;'>", unsafe_allow_html=True)
    st.caption("Confidential • DOJ&CD Internal Use Only")

# SUNDRY tab
with tab_sundry:
    st.header("Sundry Section")
    st.markdown("This is the dedicated **Sundry** page – now in official DOJ&CD green scheme.")
    st.info("Content coming soon — suggestions: submission form for sundry payments, list of recent transactions, or status tracker?")
    
    st.markdown("""
        <p style='color: #666;'>
            Back to <strong>HOME</strong> tab for overview.
        </p>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption("© Department of Justice and Constitutional Development • 2026")
