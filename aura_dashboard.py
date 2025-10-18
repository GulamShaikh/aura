import streamlit as st
import pandas as pd
import numpy as np
import time

# --- Configuration ---
st.set_page_config(
    page_title="AURA Agent Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Data Simulation ---
# In a real application, this data would come from your live database and ML model.
@st.cache_data
def generate_synthetic_data():
    """Creates a synthetic dataset simulating a loan portfolio."""
    num_users = 100
    data = {
        'user_id': [f'USR{1000 + i}' for i in range(num_users)],
        'loan_amount': np.random.randint(5000, 50000, num_users),
        'default_probability': np.random.uniform(0.01, 0.45, num_users),
        'network_usage_stability': np.random.uniform(0.2, 0.98, num_users),
        'utility_payment_timeliness': np.random.uniform(0.3, 0.99, num_users),
        'mobility_score': np.random.uniform(0.4, 0.95, num_users),
        'last_active_location': ['Bandra', 'Andheri', 'Thane', 'Dadar', 'Navi Mumbai'] * (num_users // 5),
        'last_ecommerce_category': ['Groceries', 'Electronics', 'Fashion', 'Transport', 'Bills'] * (num_users // 5),
    }
    df = pd.DataFrame(data)

    # Assign statuses based on default probability (before formatting)
    conditions = [
        (df['default_probability'] > 0.35),
        (df['default_probability'] > 0.20) & (df['default_probability'] <= 0.35),
        (df['default_probability'] <= 0.20)
    ]
    statuses = ['Defaulted', 'At Risk', 'Active']
    df['status'] = np.select(conditions, statuses, default='Unknown')
    
    # Clean up formatting for display (do this AFTER creating status column)
    df['default_probability'] = df['default_probability'].astype(float).apply(lambda x: f"{x:.2%}")
    df['loan_amount'] = df['loan_amount'].astype(int).apply(lambda x: f"₹{x:,}")
    return df

# --- UI Layout ---

# Header
st.title("🤖 AURA: Risk-Management Agent Dashboard")
st.markdown("Proactive monitoring and intelligent intervention for your loan portfolio.")

# Load Data
portfolio_df = generate_synthetic_data()

# Key Metrics
st.markdown("---")
st.header("Portfolio Health Overview")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Loans", f"{len(portfolio_df)}")
at_risk_count = portfolio_df[portfolio_df['status'] == 'At Risk'].shape[0]
col2.metric("Borrowers At Risk", f"{at_risk_count}")
defaulted_count = portfolio_df[portfolio_df['status'] == 'Defaulted'].shape[0]
col3.metric("Defaulted Loans", f"{defaulted_count}")
active_count = portfolio_df[portfolio_df['status'] == 'Active'].shape[0]
col4.metric("Active & Healthy", f"{active_count}")
st.markdown("---")


# Agent's Workspace
st.header("Agent's Workspace: Live Alerts & Intelligence")
tab1, tab2 = st.tabs(["🚨 Proactive Alerts (At Risk)", "🎯 Defaulter Intelligence"])

with tab1:
    st.subheader("Agent's Recommended Interventions")
    st.info("AURA has identified the following borrowers with an increasing risk of default. Proactive intervention is recommended.")
    
    at_risk_borrowers = portfolio_df[portfolio_df['status'] == 'At Risk'].sort_values('default_probability', ascending=False)

    if at_risk_borrowers.empty:
        st.success("No borrowers are currently flagged as 'At Risk'. The portfolio is healthy.")
    else:
        for index, row in at_risk_borrowers.iterrows():
            with st.container():
                st.warning(f"**Alert for User: {row['user_id']}**")
                col1, col2, col3 = st.columns(3)
                col1.text(f"Current Default Risk: {row['default_probability']}")
                col2.text(f"Loan Amount: {row['loan_amount']}")
                col3.text(f"Key Risk Factor: Network Usage Stability ({row['network_usage_stability']:.2f})")
                
                recommendation = f"**AURA Recommendation:** Proactively offer a 7-day payment extension via personalized SMS to prevent default. Emphasize that this will not negatively affect their credit profile."
                st.markdown(recommendation)
                st.markdown("---")


with tab2:
    st.subheader("Actionable Intelligence for Recovery")
    st.info("AURA has compiled the following intelligence for defaulted accounts to assist in ethical and efficient recovery.")

    defaulted_borrowers = portfolio_df[portfolio_df['status'] == 'Defaulted'].sort_values('default_probability', ascending=False)
    
    if defaulted_borrowers.empty:
        st.success("No borrowers are currently in default.")
    else:
        for index, row in defaulted_borrowers.iterrows():
            with st.container():
                st.error(f"**Intelligence Report for User: {row['user_id']}**")
                
                intelligence = f"""
                - **Last Known Area of Activity:** High probability ({row['mobility_score']:.0%}) of activity within a 5km radius of **{row['last_active_location']}**.
                - **Recent Financial Activity:** The last recorded e-commerce transaction was for **{row['last_ecommerce_category']}.**
                - **Suggested Contact Time:** Based on usage patterns, optimal contact window is between 6 PM - 8 PM IST.
                """
                st.markdown(intelligence)
                st.markdown("---")


# Full Data View
with st.expander("View Full Portfolio Data"):
    st.dataframe(portfolio_df)
