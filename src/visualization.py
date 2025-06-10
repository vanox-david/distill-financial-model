"""
Visualization utilities for financial charts and plots.

This module contains all chart generation functions, separated from
business logic for better maintainability.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import List, Tuple, Optional

from .config import CHART_COLORS, CHART_STYLE, SIMULATION_CONFIG


def get_quantiles(data: List[List[float]]) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate quantiles for simulation data.
    
    Args:
        data: List of simulation results (each item is a time series)
        
    Returns:
        Tuple of (10th percentile, median, 90th percentile) series
    """
    df = pd.DataFrame(data)
    return df.quantile(0.1), df.median(), df.quantile(0.9)


def create_basic_chart(
    p10: pd.Series, 
    median: pd.Series, 
    p90: pd.Series,
    title: str,
    yaxis_title: str,
    color: str = CHART_COLORS['primary']
) -> go.Figure:
    """
    Create a basic line chart with percentiles and quarterly x-axis labels.
    
    Args:
        p10: 10th percentile data
        median: Median data
        p90: 90th percentile data
        title: Chart title
        yaxis_title: Y-axis label
        color: Primary color for median line
        
    Returns:
        Plotly figure object
    """
    # Keep monthly data resolution but create quarterly labels for x-axis
    months = len(median)
    monthly_indices = list(range(months))
    
    # Generate quarterly labels and their positions
    quarterly_labels = generate_quarterly_labels(months)
    quarterly_positions = list(range(0, months, 3))  # Every 3 months
    quarterly_labels_display = [quarterly_labels[i] for i in quarterly_positions if i < len(quarterly_labels)]
    
    fig = go.Figure()
    
    # Add median line (using monthly indices for full resolution)
    fig.add_trace(go.Scatter(
        x=monthly_indices,
        y=median, 
        mode='lines', 
        name='Median',
        line=dict(color=color, width=CHART_STYLE['median_width'])
    ))
    
    # Add percentile lines (using monthly indices for full resolution)
    fig.add_trace(go.Scatter(
        x=monthly_indices,
        y=p10, 
        mode='lines', 
        name='10th Percentile',
        line=dict(
            color=CHART_COLORS['secondary'], 
            width=CHART_STYLE['percentile_width'],
            dash=CHART_STYLE['percentile_dash']
        )
    ))
    
    fig.add_trace(go.Scatter(
        x=monthly_indices,
        y=p90, 
        mode='lines', 
        name='90th Percentile',
        line=dict(
            color=CHART_COLORS['secondary'], 
            width=CHART_STYLE['percentile_width'],
            dash=CHART_STYLE['percentile_dash']
        )
    ))
    
    # Calculate y-axis range using median as upper limit
    max_median = median.max()
    y_range = [p10.min()*1.1, max_median * 1.1]  # Add 10% padding above median
    
    # Update layout with dark theme and quarterly x-axis labels - MUCH LARGER FONTS
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(color='white', size=24)  # Much larger title
        ),
        xaxis_title='Quarter',
        yaxis_title=yaxis_title,
        hovermode='x unified',
        # Dark theme styling - exact match to reference
        plot_bgcolor='#1e293b',  # bg-slate-800 background
        paper_bgcolor='#0F172A',  # Nearly black background
        font=dict(color='white', size=20),  # Much larger base font
        xaxis=dict(
            gridcolor='#374151',
            color='white',
            title_font=dict(color='white', size=22),  # Much larger axis title
            tickfont=dict(color='white', size=18),    # Much larger tick labels
            tickangle=0,
            # Set custom tick positions and labels for quarterly display
            tickmode='array',
            tickvals=quarterly_positions[:len(quarterly_labels_display)],
            ticktext=quarterly_labels_display,
            range=[-0.5, months - 0.5]  # Show full range with slight padding
        ),
        yaxis=dict(
            gridcolor='#374151',
            color='white',  
            title_font=dict(color='white', size=22),  # Much larger axis title
            tickfont=dict(color='white', size=18),    # Much larger tick labels
            range=y_range
        ),
        legend=dict(
            font=dict(color='white', size=18),  # Much larger legend text
            bgcolor='rgba(15, 23, 42, 0.8)'
        )
    )
    
    return fig


def plot_metric_chart(
    data: List[List[float]], 
    title: str, 
    yaxis_title: str, 
    color: str = CHART_COLORS['primary'],
    key: str = None
) -> None:
    """
    Plot a metric chart with quantiles using Streamlit.
    
    Args:
        data: Simulation results data
        title: Chart title
        yaxis_title: Y-axis label
        color: Primary color for the chart
        key: Unique key for the plotly chart element
    """
    p10, median, p90 = get_quantiles(data)
    fig = create_basic_chart(p10, median, p90, title, yaxis_title, color)
    st.plotly_chart(fig, key=key)


def plot_revenue_breakdown_charts(results: List, months: int) -> None:
    """
    Plot all revenue breakdown charts.
    
    Args:
        results: List of simulation results
        months: Number of months simulated
    """
    st.subheader("Revenue Streams")
    
    # Extract revenue data
    total_revenue = [result.total_revenue for result in results]
    seat_revenue = [result.seat_revenue for result in results]
    simulation_revenue = [result.simulation_revenue for result in results]
    customers = [result.customers for result in results]
    churn = [result.churn for result in results]
    
    # Plot charts
    plot_metric_chart(total_revenue, 'Total Monthly Revenue', 'Revenue ($)', CHART_COLORS['revenue'], key='revenue_total')
    plot_metric_chart(seat_revenue, 'Seat-Based Revenue', 'Revenue ($)', CHART_COLORS['revenue_secondary'], key='revenue_seat')
    plot_metric_chart(simulation_revenue, 'Simulation-Year Revenue', 'Revenue ($)', CHART_COLORS['revenue_tertiary'], key='revenue_simulation')
    
    st.subheader("Customer Metrics")
    plot_metric_chart(customers, 'Total Customers', 'Customers', CHART_COLORS['info'], key='customers_total')
    plot_metric_chart(churn, 'Monthly Churn', 'Customers Lost', CHART_COLORS['warning'], key='customers_churn')


def plot_cost_breakdown_charts(results: List, months: int) -> None:
    """
    Plot all cost breakdown charts.
    
    Args:
        results: List of simulation results
        months: Number of months simulated
    """
    # Extract cost data
    total_costs = [result.total_costs for result in results]
    fixed_costs = [result.fixed_costs for result in results]
    variable_costs = [result.variable_costs for result in results]
    
    # Individual cost components
    salary_costs = [result.salary_costs for result in results]
    hosting_costs = [result.hosting_costs for result in results]
    software_costs = [result.software_costs for result in results]
    compute_costs = [result.compute_costs for result in results]
    customer_support_costs = [result.customer_support_costs for result in results]
    admin_costs = [result.admin_costs for result in results]
    conference_costs = [result.conference_costs for result in results]
    benefits_costs = [result.benefits_costs for result in results]
    headcount = [result.headcount for result in results]
    
    # Aggregate cost charts
    st.subheader("Aggregate Cost Views")
    plot_metric_chart(total_costs, 'Total Monthly Costs', 'Cost ($)', CHART_COLORS['cost'], key='costs_total')
    plot_metric_chart(fixed_costs, 'Fixed Monthly Costs', 'Cost ($)', CHART_COLORS['cost_secondary'], key='costs_fixed')
    plot_metric_chart(variable_costs, 'Variable Monthly Costs', 'Cost ($)', CHART_COLORS['cost_tertiary'], key='costs_variable')
    
    # Individual cost component charts
    st.subheader("Individual Cost Components")
    plot_metric_chart(salary_costs, 'Salary Costs', 'Cost ($)', CHART_COLORS['primary'], key='costs_salary')
    plot_metric_chart(hosting_costs, 'Hosting Costs', 'Cost ($)', CHART_COLORS['info'], key='costs_hosting')
    plot_metric_chart(software_costs, 'Software Subscription Costs', 'Cost ($)', CHART_COLORS['success'], key='costs_software')
    plot_metric_chart(compute_costs, 'Compute Costs', 'Cost ($)', CHART_COLORS['warning'], key='costs_compute')
    plot_metric_chart(customer_support_costs, 'Customer Support Costs', 'Cost ($)', CHART_COLORS['danger'], key='costs_support')
    plot_metric_chart(admin_costs, 'Admin & Legal Costs', 'Cost ($)', CHART_COLORS['headcount'], key='costs_admin')
    plot_metric_chart(conference_costs, 'Conference Costs', 'Cost ($)', CHART_COLORS['secondary'], key='costs_conference')
    plot_metric_chart(benefits_costs, 'Benefits Costs', 'Cost ($)', CHART_COLORS['info'], key='costs_benefits')
    
    # Headcount chart
    st.subheader("Team Growth")
    plot_metric_chart(headcount, 'Headcount Growth', 'Headcount', CHART_COLORS['headcount'], key='costs_headcount')


def plot_earnings_charts(results: List, months: int) -> None:
    """
    Plot earnings analysis charts.
    
    Args:
        results: List of simulation results
        months: Number of months simulated
    """
    # Calculate earnings
    total_revenue = np.array([result.total_revenue for result in results])
    total_costs = np.array([result.total_costs for result in results])
    seat_revenue = np.array([result.seat_revenue for result in results])
    simulation_revenue = np.array([result.simulation_revenue for result in results])
    headcount = np.array([result.headcount for result in results])
    
    earnings = total_revenue - total_costs
    cumulative_earnings = np.cumsum(earnings, axis=1)
    
    # Main earnings charts
    st.subheader("Earnings Overview")
    plot_metric_chart(earnings.tolist(), 'Monthly Earnings', 'Earnings ($)', CHART_COLORS['earnings'], key='earnings_monthly')
    plot_metric_chart(cumulative_earnings.tolist(), 'Cumulative Earnings', 'Earnings ($)', CHART_COLORS['earnings'], key='earnings_cumulative')
    
    # Revenue breakdown in earnings context
    st.subheader("Revenue Breakdown")
    plot_metric_chart(total_revenue.tolist(), 'Total Revenue', 'Revenue ($)', CHART_COLORS['revenue'], key='earnings_revenue_total')
    plot_metric_chart(seat_revenue.tolist(), 'Seat-Based Revenue', 'Revenue ($)', CHART_COLORS['revenue_secondary'], key='earnings_revenue_seat')
    plot_metric_chart(simulation_revenue.tolist(), 'Simulation-Year Revenue', 'Revenue ($)', CHART_COLORS['revenue_tertiary'], key='earnings_revenue_simulation')
    
    # Cost breakdown in earnings context
    st.subheader("Cost Breakdown")
    fixed_costs = np.array([result.fixed_costs for result in results])
    variable_costs = np.array([result.variable_costs for result in results])
    
    plot_metric_chart(total_costs.tolist(), 'Total Costs', 'Cost ($)', CHART_COLORS['cost'], key='earnings_costs_total')
    plot_metric_chart(fixed_costs.tolist(), 'Fixed Costs', 'Cost ($)', CHART_COLORS['cost_secondary'], key='earnings_costs_fixed')
    plot_metric_chart(variable_costs.tolist(), 'Variable Costs', 'Cost ($)', CHART_COLORS['cost_tertiary'], key='earnings_costs_variable')
    
    # Team and productivity
    st.subheader("Team and Productivity")
    plot_metric_chart(headcount.tolist(), 'Headcount Evolution', 'Headcount', CHART_COLORS['headcount'], key='earnings_headcount')
    
    # Per-employee metrics (avoid division by zero)
    revenue_per_employee = total_revenue / np.maximum(headcount, 1)
    earnings_per_employee = earnings / np.maximum(headcount, 1)
    
    plot_metric_chart(revenue_per_employee.tolist(), 'Revenue per Employee', 'Revenue per Employee ($)', CHART_COLORS['efficiency'], key='earnings_revenue_per_employee')
    plot_metric_chart(earnings_per_employee.tolist(), 'Earnings per Employee', 'Earnings per Employee ($)', CHART_COLORS['earnings'], key='earnings_per_employee')


def display_summary_metrics(results: List, months: int) -> None:
    """
    Display summary metrics in a dashboard format.
    
    Args:
        results: List of simulation results
        months: Number of months simulated
    """
    # Calculate key metrics
    total_revenue = np.array([result.total_revenue for result in results])
    total_costs = np.array([result.total_costs for result in results])
    headcount = np.array([result.headcount for result in results])
    
    earnings = total_revenue - total_costs
    cumulative_earnings = np.cumsum(earnings, axis=1)
    
    # Break-even analysis
    break_even_months = [
        np.argmax(cum > 0) if np.any(cum > 0) else months 
        for cum in cumulative_earnings
    ]
    median_break_even = np.median(break_even_months)
    
    # Final month metrics
    final_earnings = cumulative_earnings[:, -1]
    final_headcount = headcount[:, -1]
    final_revenue = total_revenue[:, -1]
    final_monthly_earnings = earnings[:, -1]
    
    st.subheader("Key Metrics")
    
    # First row of metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Median Break-even Month", f"{int(median_break_even)}")
    with col2:
        st.metric("Final Month Median Headcount", f"{np.median(final_headcount):.0f}")
    with col3:
        st.metric("Final Cumulative Earnings", f"${np.median(final_earnings):,.0f}")
    
    # Second row of metrics
    col4, col5, col6 = st.columns(3)
    with col4:
        revenue_per_employee = np.median(final_revenue / np.maximum(final_headcount, 1))
        st.metric("Final Revenue per Employee", f"${revenue_per_employee:,.0f}")
    with col5:
        st.metric("Final Monthly Earnings", f"${np.median(final_monthly_earnings):,.0f}")
    with col6:
        earnings_per_employee = np.median(final_monthly_earnings / np.maximum(final_headcount, 1))
        st.metric("Final Earnings per Employee", f"${earnings_per_employee:,.0f}")


def display_cost_summary_metrics(results: List, months: int) -> None:
    """
    Display cost-specific summary metrics.
    
    Args:
        results: List of simulation results
        months: Number of months simulated
    """
    total_costs = np.array([result.total_costs for result in results])
    headcount = np.array([result.headcount for result in results])
    
    final_month_costs = total_costs[:, -1]
    final_month_headcount = headcount[:, -1]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Final Month Median Costs", f"${np.median(final_month_costs):,.0f}")
    with col2:
        st.metric("Final Month Median Headcount", f"{np.median(final_month_headcount):.0f}")
    with col3:
        cost_per_employee = np.median(final_month_costs / np.maximum(final_month_headcount, 1))
        st.metric("Cost per Employee (Final Month)", f"${cost_per_employee:,.0f}")


def create_export_dataframe(results: List, months: int) -> pd.DataFrame:
    """
    Create DataFrame for Excel export.
    
    Args:
        results: List of simulation results
        months: Number of months simulated
        
    Returns:
        DataFrame with summary statistics
    """
    # Extract data
    total_revenue = [result.total_revenue for result in results]
    customers = [result.customers for result in results]
    churn = [result.churn for result in results]
    
    # Calculate quantiles
    rev_p10, rev_med, rev_p90 = get_quantiles(total_revenue)
    customer_p10, customer_med, customer_p90 = get_quantiles(customers)
    churn_p10, churn_med, churn_p90 = get_quantiles(churn)
    
    # Create export DataFrame
    export_df = pd.DataFrame({
        'Month': np.arange(1, months + 1),
        'Median Revenue': rev_med,
        '10th Percentile Revenue': rev_p10,
        '90th Percentile Revenue': rev_p90,
        'Median Customers': customer_med.astype(int),
        'Median Churn': churn_med.astype(int)
    })
    
    return export_df


def generate_quarterly_labels(months: int, start_year: int = 2025, start_quarter: int = 4) -> List[str]:
    """
    Generate quarterly labels for x-axis.
    
    Args:
        months: Number of months to generate labels for
        start_year: Starting year (default 2025)
        start_quarter: Starting quarter (default Q4)
        
    Returns:
        List of quarterly labels like ['2025Q4', '2026Q1', '2026Q2', ...]
    """
    labels = []
    current_year = start_year
    current_quarter = start_quarter
    
    for month in range(months):
        labels.append(f"{current_year}Q{current_quarter}")
        
        # Move to next quarter every 3 months
        if (month + 1) % 3 == 0:
            current_quarter += 1
            if current_quarter > 4:
                current_quarter = 1
                current_year += 1
    
    return labels 