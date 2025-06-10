"""
UI components for Streamlit interface.

This module contains all UI-related functions for creating input controls,
sidebars, and organizing the user interface.
"""

import streamlit as st
import io
import pandas as pd
from typing import Tuple

from config import REVENUE_CONFIG, COST_CONFIG, SIMULATION_CONFIG
from models import RevenueParameters, CostParameters


def create_simulation_controls() -> Tuple[int, int]:
    """
    Create main simulation control inputs.
    
    Returns:
        Tuple of (months, simulations)
    """
    st.sidebar.header("Simulation Parameters")
    
    months = st.sidebar.number_input(
        'Projection Period (Months)', 
        min_value=SIMULATION_CONFIG.months_min, 
        max_value=SIMULATION_CONFIG.months_max, 
        value=SIMULATION_CONFIG.months_default
    )
    
    simulations = st.sidebar.number_input(
        'Number of Simulations', 
        min_value=SIMULATION_CONFIG.simulations_min, 
        max_value=SIMULATION_CONFIG.simulations_max, 
        value=SIMULATION_CONFIG.simulations_default
    )
    
    return months, simulations


def create_revenue_controls(months: int) -> RevenueParameters:
    """
    Create revenue model input controls.
    
    Args:
        months: Maximum months for delay validation
        
    Returns:
        RevenueParameters object with user inputs
    """
    st.sidebar.header("Revenue Assumptions")
    
    # Seat-based revenue controls
    seat_fee = st.sidebar.number_input(
        'Monthly Fee per Seat ($)', 
        value=REVENUE_CONFIG.seat_fee_default
    )
    
    avg_seats = st.sidebar.slider(
        'Average Seats per Customer', 
        REVENUE_CONFIG.avg_seats_min, 
        REVENUE_CONFIG.avg_seats_max, 
        REVENUE_CONFIG.avg_seats_default
    )
    
    # Simulation-year revenue controls
    st.sidebar.subheader("Simulation Usage Revenue")
    
    sim_year_revenue_mean = st.sidebar.number_input(
        'Mean Simulation-Years per Customer per Month',
        min_value=REVENUE_CONFIG.sim_year_revenue_mean_min,
        max_value=REVENUE_CONFIG.sim_year_revenue_mean_max,
        value=REVENUE_CONFIG.sim_year_revenue_mean_default
    )
    
    sim_year_revenue_sigma = st.sidebar.slider(
        'Simulation-Year Usage Volatility',
        REVENUE_CONFIG.sim_year_revenue_sigma_min,
        REVENUE_CONFIG.sim_year_revenue_sigma_max,
        REVENUE_CONFIG.sim_year_revenue_sigma_default
    )
    
    revenue_per_sim_year = st.sidebar.number_input(
        'Revenue per Simulation-Year ($)',
        value=REVENUE_CONFIG.revenue_per_sim_year_default
    )
    
    # Customer growth controls
    st.sidebar.subheader("Customer Growth")
    
    customer_delay = st.sidebar.number_input(
        'Months Delay for Customer Acquisition',
        min_value=0,
        max_value=months,
        value=REVENUE_CONFIG.customer_delay_default
    )
    
    customer_growth_median = st.sidebar.slider(
        'Median Customer Adds',
        REVENUE_CONFIG.customer_growth_median_min,
        REVENUE_CONFIG.customer_growth_median_max,
        REVENUE_CONFIG.customer_growth_median_default
    )
    
    customer_growth_accel = st.sidebar.slider(
        'Monthly Customer Growth Acceleration (%)',
        REVENUE_CONFIG.customer_growth_accel_min,
        REVENUE_CONFIG.customer_growth_accel_max,
        REVENUE_CONFIG.customer_growth_accel_default,
        step=0.1
    ) / 100
    
    # Churn controls
    st.sidebar.subheader("Customer Churn")
    
    monthly_churn_median = st.sidebar.slider(
        'Median Monthly Churn Rate (%)',
        REVENUE_CONFIG.monthly_churn_median_min,
        REVENUE_CONFIG.monthly_churn_median_max,
        REVENUE_CONFIG.monthly_churn_median_default
    ) / 100
    
    return RevenueParameters(
        seat_fee=seat_fee,
        avg_seats=avg_seats,
        sim_year_revenue_mean=sim_year_revenue_mean,
        sim_year_revenue_sigma=sim_year_revenue_sigma,
        revenue_per_sim_year=revenue_per_sim_year,
        customer_delay=customer_delay,
        customer_growth_median=customer_growth_median,
        customer_growth_sigma=REVENUE_CONFIG.customer_growth_sigma,
        customer_growth_accel=customer_growth_accel,
        monthly_churn_median=monthly_churn_median,
        monthly_churn_sigma=REVENUE_CONFIG.monthly_churn_sigma
    )


def create_cost_controls(months: int) -> CostParameters:
    """
    Create cost model input controls.
    
    Args:
        months: Maximum months for delay validation
        
    Returns:
        CostParameters object with user inputs
    """
    st.sidebar.header("Cost Assumptions")
    
    # Infrastructure costs
    st.sidebar.subheader("Infrastructure Costs")
    
    hosting_initial = st.sidebar.number_input(
        'Hosting Initial Monthly ($)',
        value=COST_CONFIG.hosting_initial_default
    )
    
    hosting_growth = st.sidebar.slider(
        'Hosting Growth Rate (%)',
        COST_CONFIG.hosting_growth_min,
        COST_CONFIG.hosting_growth_max,
        COST_CONFIG.hosting_growth_default
    ) / 100
    
    software_initial = st.sidebar.number_input(
        'Software Subscriptions Initial Monthly ($)',
        value=COST_CONFIG.software_initial_default
    )
    
    software_growth = st.sidebar.slider(
        'Software Growth Rate (%)',
        COST_CONFIG.software_growth_min,
        COST_CONFIG.software_growth_max,
        COST_CONFIG.software_growth_default
    ) / 100
    
    # Fixed costs
    st.sidebar.subheader("Fixed Costs")
    
    admin_monthly = st.sidebar.number_input(
        'Admin & Legal Monthly ($)',
        value=COST_CONFIG.admin_monthly_default
    )
    
    conference_monthly = st.sidebar.number_input(
        'Conference Fees Monthly ($)',
        value=COST_CONFIG.conference_monthly_default
    )
    
    benefits_monthly = st.sidebar.number_input(
        'Monthly Benefits ($)',
        value=COST_CONFIG.benefits_monthly_default
    )
    
    # Headcount-based salary parameters
    st.sidebar.subheader("Headcount & Salaries")
    
    salary_per_person = st.sidebar.number_input(
        'Monthly Salary per Person ($)',
        value=COST_CONFIG.salary_per_person_default
    )
    
    initial_headcount = st.sidebar.number_input(
        'Initial Headcount',
        min_value=COST_CONFIG.initial_headcount_min,
        max_value=COST_CONFIG.initial_headcount_max,
        value=COST_CONFIG.initial_headcount_default
    )
    
    headcount_delay = st.sidebar.number_input(
        'Months Delay for Headcount Growth',
        min_value=0,
        max_value=months,
        value=COST_CONFIG.headcount_delay_default
    )
    
    headcount_growth_median = st.sidebar.slider(
        'Median Headcount Adds',
        COST_CONFIG.headcount_growth_median_min,
        COST_CONFIG.headcount_growth_median_max,
        COST_CONFIG.headcount_growth_median_default
    )
    
    headcount_growth_accel = st.sidebar.slider(
        'Monthly Headcount Growth Acceleration (%)',
        COST_CONFIG.headcount_growth_accel_min,
        COST_CONFIG.headcount_growth_accel_max,
        COST_CONFIG.headcount_growth_accel_default,
        step=0.1
    ) / 100
    
    # Variable costs
    st.sidebar.subheader("Variable Costs")
    
    support_customer_initial = st.sidebar.number_input(
        'Support Cost per Customer Monthly ($)',
        value=COST_CONFIG.support_customer_initial_default
    )
    
    support_growth = st.sidebar.slider(
        'Support Growth Rate (%)',
        COST_CONFIG.support_growth_min,
        COST_CONFIG.support_growth_max,
        COST_CONFIG.support_growth_default
    ) / 100
    
    compute_initial = st.sidebar.number_input(
        'Compute Initial Monthly ($)',
        value=COST_CONFIG.compute_initial_default
    )
    
    compute_growth = st.sidebar.slider(
        'Compute Growth Rate (%)',
        COST_CONFIG.compute_growth_min,
        COST_CONFIG.compute_growth_max,
        COST_CONFIG.compute_growth_default
    ) / 100
    
    compute_per_sim_year = st.sidebar.slider(
        'Compute Cost per Simulation-Year ($)',
        COST_CONFIG.compute_per_sim_year_min,
        COST_CONFIG.compute_per_sim_year_max,
        COST_CONFIG.compute_per_sim_year_default,
        step=0.5,
        help="Cost per simulation-year executed"
    )
    
    return CostParameters(
        hosting_initial=hosting_initial,
        hosting_growth=hosting_growth,
        software_initial=software_initial,
        software_growth=software_growth,
        admin_monthly=admin_monthly,
        conference_monthly=conference_monthly,
        salary_per_person=salary_per_person,
        initial_headcount=initial_headcount,
        headcount_delay=headcount_delay,
        headcount_growth_median=headcount_growth_median,
        headcount_growth_sigma=COST_CONFIG.headcount_growth_sigma,
        headcount_growth_accel=headcount_growth_accel,
        benefits_monthly=benefits_monthly,
        support_customer_initial=support_customer_initial,
        support_growth=support_growth,
        compute_initial=compute_initial,
        compute_growth=compute_growth,
        compute_per_sim_year=compute_per_sim_year
    )


def create_export_button(results: list, months: int) -> None:
    """
    Create Excel export functionality.
    
    Args:
        results: Simulation results
        months: Number of months simulated
    """
    from visualization import create_export_dataframe
    
    export_df = create_export_dataframe(results, months)
    
    # Create Excel file
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        export_df.to_excel(writer, sheet_name='Projections', index=False)
    
    st.download_button(
        label="Export All Projections to Excel",
        data=output.getvalue(),
        file_name="detailed_revenue_projections.xlsx",
        mime="application/vnd.ms-excel"
    )


def display_app_header() -> None:
    """Display the main application header and description."""
    st.title('🏢 Distill Financials Dashboard')
    
    st.markdown("""
    ### Comprehensive Financial Modeling with Monte Carlo Simulation
    
    This dashboard provides detailed financial projections using Monte Carlo simulation 
    to model uncertainty in revenue, costs, and business growth. Use the sidebar controls 
    to adjust model parameters and explore different scenarios.
    
    **Key Features:**
    - 📈 **Revenue Modeling**: Seat-based and usage-based revenue streams
    - 💰 **Cost Analysis**: Individual cost component tracking with headcount simulation
    - 📊 **Earnings Projections**: Break-even analysis and per-employee metrics
    - 🎲 **Monte Carlo Simulation**: Probabilistic forecasting with confidence intervals
    - 📋 **Excel Export**: Download detailed projections for further analysis
    """)
    
    st.divider()


def create_tabs() -> Tuple:
    """
    Create the main application tabs.
    
    Returns:
        Tuple of tab objects
    """
    return st.tabs(["📈 Revenue", "💰 Costs", "💹 Earnings"])


def display_tab_headers(tab_name: str) -> None:
    """
    Display header for each tab.
    
    Args:
        tab_name: Name of the current tab
    """
    headers = {
        "Revenue": "📈 Revenue Analysis & Projections",
        "Costs": "💰 Cost Structure & Team Growth",
        "Earnings": "💹 Earnings, Profitability & Efficiency"
    }
    
    if tab_name in headers:
        st.header(headers[tab_name])
        st.markdown("---") 