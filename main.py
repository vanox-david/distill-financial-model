#!/usr/bin/env python3
"""
Main Streamlit application for Distill Financial Model.

This is the entry point for the financial modeling dashboard. It orchestrates
the UI components, runs simulations, and displays results.

Run with: streamlit run main.py
"""

import streamlit as st
import numpy as np

# Direct imports - no src directory needed
from models import FinancialModel
from ui_components import (
    display_app_header, create_tabs, display_tab_headers,
    create_simulation_controls, create_revenue_controls, 
    create_cost_controls, create_export_button
)
from visualization import (
    plot_revenue_breakdown_charts, plot_cost_breakdown_charts,
    plot_earnings_charts, display_summary_metrics, 
    display_cost_summary_metrics
)


def main():
    """Main application function."""
    
    # Configure Streamlit page with dark theme
    st.set_page_config(
        page_title="Distill Financial Model",
        page_icon="🏢",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Inject custom CSS for cohesive slate theme matching charts
    st.markdown("""
    <style>
    /* Cohesive slate theme - Tufte principles: minimal, elegant, data-focused */
    .main .block-container {
        background-color: #0f172a;  /* slate-900 - slightly darker main area */
        color: white;
        border-radius: 0.375rem;  /* Smaller radius - less "boxy" */
        border: none;  /* Remove border - Tufte: remove unnecessary ink */
        padding: 1rem 2rem;  /* Tighter padding */
    }
    
    /* Sidebar styling - matches chart background exactly */
    .css-1d391kg {
        background-color: #1e293b;  /* slate-800 - same as charts */
        border-right: 1px solid rgba(51, 65, 85, 0.3);  /* Much more subtle border */
    }
    
    /* Sidebar headers and labels - more refined typography */
    .css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3, .css-1d391kg label {
        color: #e2e8f0 !important;  /* slate-200 - softer than pure white */
        font-weight: 500 !important;  /* Medium weight, not bold */
    }
    
    /* Metric styling - minimal, elegant (Tufte: let data speak) */
    [data-testid="metric-container"] {
        background: rgba(30, 41, 59, 0.3);  /* Very subtle background */
        border: 1px solid rgba(71, 85, 105, 0.2);  /* Barely visible border */
        padding: 1rem;  /* More space for breathing */
        border-radius: 0.5rem;  /* Subtle rounding */
        color: white;
        box-shadow: none;  /* Remove shadow - Tufte: avoid decorative elements */
        backdrop-filter: blur(10px);  /* Subtle modern effect */
    }
    
    /* Metric values - clean, readable */
    [data-testid="metric-container"] [data-testid="metric-value"] {
        color: #f1f5f9 !important;  /* slate-100 */
        font-weight: 600 !important;  /* Slightly less bold */
        font-size: 1.5rem !important;  /* Readable but not overwhelming */
    }
    
    /* Metric labels - subtle but readable */
    [data-testid="metric-container"] [data-testid="metric-label"] {
        color: #cbd5e1 !important;  /* slate-300 */
        font-size: 0.875rem !important;
        font-weight: 400 !important;
    }
    
    /* Headers - clean, minimal (Tufte: reduce visual noise) */
    h1 {
        color: #f8fafc !important;  /* slate-50 */
        font-weight: 600 !important;  /* Less bold */
        font-size: 2rem !important;  /* Smaller, more proportional */
        margin-bottom: 1rem !important;
        text-shadow: none !important;  /* Remove shadow */
    }
    
    h2 {
        color: #e2e8f0 !important;  /* slate-200 */
        font-weight: 500 !important;
        font-size: 1.5rem !important;
        margin: 1.5rem 0 0.75rem 0 !important;
    }
    
    h3 {
        color: #cbd5e1 !important;  /* slate-300 */
        font-weight: 500 !important;
        font-size: 1.25rem !important;
        margin: 1rem 0 0.5rem 0 !important;
    }
    
    /* Text elements - better hierarchy */
    .stMarkdown, .stText {
        color: #cbd5e1 !important;  /* slate-300 */
        line-height: 1.6 !important;  /* Better readability */
    }
    
    /* Streamlit app background - cleaner gradient */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }
    
    /* Tab styling - minimal, clean */
    .stTabs [data-baseweb="tab-list"] {
        background-color: rgba(30, 41, 59, 0.5);  /* More subtle */
        border-radius: 0.375rem;
        padding: 0.25rem;
        border: 1px solid rgba(51, 65, 85, 0.3);  /* Subtle border */
        margin-bottom: 1.5rem;
    }
    
    .stTabs [data-baseweb="tab-list"] button {
        background-color: transparent !important;
        color: #94a3b8 !important;  /* slate-400 */
        border-radius: 0.25rem !important;
        border: none !important;
        font-weight: 500 !important;
        padding: 0.5rem 1rem !important;
    }
    
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background-color: rgba(51, 65, 85, 0.5) !important;  /* More subtle active state */
        color: #f1f5f9 !important;  /* slate-100 */
    }
    
    /* Input styling - clean, minimal */
    .stNumberInput input, .stSlider, .stSelectbox select {
        background-color: rgba(51, 65, 85, 0.3) !important;  /* More subtle */
        color: white !important;
        border: 1px solid rgba(71, 85, 105, 0.3) !important;  /* Lighter border */
        border-radius: 0.25rem !important;
        transition: border-color 0.2s ease !important;
    }
    
    .stNumberInput input:focus, .stSelectbox select:focus {
        border-color: rgba(59, 130, 246, 0.5) !important;  /* Subtle focus state */
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1) !important;
    }
    
    /* Dividers - minimal */
    .stMarkdown hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, rgba(71, 85, 105, 0.3), transparent) !important;
        margin: 2rem 0 !important;
    }
    
    /* Button styling - minimal, functional */
    .stButton button {
        background: rgba(59, 130, 246, 0.8) !important;  /* More subtle */
        color: white !important;
        border: 1px solid rgba(59, 130, 246, 0.3) !important;
        border-radius: 0.375rem !important;
        font-weight: 500 !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.2s ease !important;
        backdrop-filter: blur(10px) !important;
    }
    
    .stButton button:hover {
        background: rgba(59, 130, 246, 1) !important;
        border-color: rgba(59, 130, 246, 0.8) !important;
        transform: none !important;  /* Remove animation - Tufte: avoid unnecessary movement */
        box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2) !important;
    }
    
    /* Download button - distinguished but not flashy */
    .stDownloadButton button {
        background: rgba(16, 185, 129, 0.8) !important;
        border: 1px solid rgba(16, 185, 129, 0.3) !important;
    }
    
    .stDownloadButton button:hover {
        background: rgba(16, 185, 129, 1) !important;
        border-color: rgba(16, 185, 129, 0.8) !important;
        box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2) !important;
    }
    
    /* Hide Streamlit elements that add clutter (Tufte: remove non-essential elements) */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Spinner - minimal */
    .stSpinner > div {
        border-top-color: rgba(59, 130, 246, 0.8) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Display header
    display_app_header()
    
    # Create main simulation controls
    months, simulations = create_simulation_controls()
    
    # Create parameter controls based on current tab
    revenue_params = create_revenue_controls(months)
    cost_params = create_cost_controls(months)
    
    # Create and run financial model
    with st.spinner('Running financial simulation...'):
        financial_model = FinancialModel(revenue_params, cost_params)
        results = financial_model.run_simulation(months, simulations)
    
    # Create tabs
    revenue_tab, costs_tab, earnings_tab = create_tabs()
    
    # Revenue Tab
    with revenue_tab:
        display_tab_headers("Revenue")
        
        # Display revenue analysis
        plot_revenue_breakdown_charts(results, months)
        
        # Add export functionality
        st.divider()
        st.subheader("📋 Export Data")
        create_export_button(results, months)
        
        # Display quick stats
        st.divider()
        st.subheader("📊 Quick Statistics")
        
        total_revenue = np.array([result.total_revenue for result in results])
        customers = np.array([result.customers for result in results])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            final_revenue = np.median(total_revenue[:, -1])
            st.metric("Final Month Median Revenue", f"${final_revenue:,.0f}")
        with col2:
            final_customers = np.median(customers[:, -1])
            st.metric("Final Month Median Customers", f"{final_customers:.0f}")
        with col3:
            revenue_per_customer = final_revenue / max(final_customers, 1)
            st.metric("Revenue per Customer (Final Month)", f"${revenue_per_customer:,.0f}")
    
    # Costs Tab
    with costs_tab:
        display_tab_headers("Costs")
        
        # Display cost analysis
        plot_cost_breakdown_charts(results, months)
        
        # Display cost summary metrics
        st.divider()
        display_cost_summary_metrics(results, months)
        
        # Additional cost insights
        st.divider()
        st.subheader("💡 Cost Insights")
        
        total_costs = np.array([result.total_costs for result in results])
        headcount = np.array([result.headcount for result in results])
        salary_costs = np.array([result.salary_costs for result in results])
        
        col1, col2 = st.columns(2)
        with col1:
            salary_percentage = np.median(salary_costs[:, -1] / total_costs[:, -1]) * 100
            st.metric("Salary % of Total Costs (Final Month)", f"{salary_percentage:.1f}%")
        with col2:
            cost_growth = np.median(total_costs[:, -1] / total_costs[:, 0])
            st.metric("Cost Growth Multiple", f"{cost_growth:.1f}x")
    
    # Earnings Tab
    with earnings_tab:
        display_tab_headers("Earnings")
        
        # Display earnings analysis
        plot_earnings_charts(results, months)
        
        # Display summary metrics
        st.divider()
        display_summary_metrics(results, months)
        
        # Additional business insights
        st.divider()
        st.subheader("🎯 Business Insights")
        
        total_revenue = np.array([result.total_revenue for result in results])
        total_costs = np.array([result.total_costs for result in results])
        
        earnings = total_revenue - total_costs
        cumulative_earnings = np.cumsum(earnings, axis=1)
        
        # Calculate some business metrics
        positive_months = np.sum(earnings > 0, axis=1)
        median_positive_months = np.median(positive_months)
        
        margin_final = np.median(earnings[:, -1] / total_revenue[:, -1]) * 100
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Median Profitable Months", f"{median_positive_months:.0f} of {months}")
        with col2:
            st.metric("Final Month Profit Margin", f"{margin_final:.1f}%")
        with col3:
            max_drawdown = np.median(np.min(cumulative_earnings, axis=1))
            st.metric("Median Max Drawdown", f"${max_drawdown:,.0f}")


if __name__ == "__main__":
    main() 