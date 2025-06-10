#!/usr/bin/env python3
"""
Main Streamlit application for Distill Financial Model.

This is the entry point for the financial modeling dashboard. It orchestrates
the UI components, runs simulations, and displays results.

Run with: streamlit run main.py
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Add src directory to path for imports - more robust approach
current_dir = Path(__file__).parent.absolute()
src_dir = current_dir / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Also add the parent directory to ensure relative imports work
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

try:
    from src.models import FinancialModel
    from src.ui_components import (
        display_app_header, create_tabs, display_tab_headers,
        create_simulation_controls, create_revenue_controls, 
        create_cost_controls, create_export_button
    )
    from src.visualization import (
        plot_revenue_breakdown_charts, plot_cost_breakdown_charts,
        plot_earnings_charts, display_summary_metrics, 
        display_cost_summary_metrics
    )
except ImportError as e:
    st.error(f"Import error: {e}")
    st.error("Please ensure you're running this from the correct directory and all dependencies are installed.")
    st.stop()

import numpy as np


def main():
    """Main application function."""
    
    # Configure Streamlit page with dark theme
    st.set_page_config(
        page_title="Distill Financial Model",
        page_icon="🏢",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Inject custom CSS for dark theme
    st.markdown("""
    <style>
    /* Dark theme styling - exact match to reference */
    .main .block-container {
        background-color: #0F172A;
        color: white;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #111827;
    }
    
    /* Metric styling */
    [data-testid="metric-container"] {
        background-color: #111827;
        border: 1px solid #374151;
        padding: 1rem;
        border-radius: 0.5rem;
        color: white;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: white !important;
    }
    
    /* Text elements */
    .stMarkdown, .stText {
        color: white !important;
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