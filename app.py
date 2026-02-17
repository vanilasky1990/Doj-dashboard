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
st.markdown("""
    <style>
    .stApp { 
        background-color: #f9fbfd; 
        font-family: 'Helvetica Neue', Arial, sans-serif;
    }
    .header { 
        background-color: #005c28;  /* Official dark green (Pantone 349C inspired) */
        color: white; 
        padding: 30px 20px; 
        text-align: center; 
        margin-bottom: 30px;
        border-bottom: 4px solid #FFB612;  /* SA gold accent */
    }
    .header-logo {
        max-width: 180px;
        margin-bottom: 15px;
    }
    .header h1 { 
        margin: 0; 
        font-size: 2.4rem; 
        font-weight: 600;
    }
    .header h3 { 
        margin: 10px 0 0; 
        font-size: 1.4rem; 
        font-weight: 400;
    }
    .header p { 
        margin: 10px 0 0; 
        font-size: 1.1rem; 
        opacity: 0.95;
    }
    /* Tabs - green theme */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #ffffff;
        border-bottom: 2px solid #e0e0e0;
        padding: 0 20px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f4f8;
        border-radius: 8px 8px 0 0;
        font-size: 1.1rem;
        font-weight: 500;
        color: #333;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        border-bottom: 3px solid #005c28;  /* Selected tab green */
        color: #005c28 !important;
    }
    /* Buttons - SA gold/orange accent */
    .stButton > button {
        background-color: #FFB612;
        color: black;
        border: none;
        font-weight: bold;
        padding: 10px 20px;
        border-radius: 6px;
    }
    .stButton > button:hover {
        background-color: #e6a000;
    }
    </style>
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
