"""
Configuration and constants for the Distill Financial Model.

This module contains default values, constants, and configuration settings
used throughout the financial modeling application.
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class RevenueConfig:
    """Configuration for revenue model parameters."""
    
    # Seat-based revenue
    seat_fee_default: float = 1000.0
    avg_seats_default: int = 1
    avg_seats_min: int = 1
    avg_seats_max: int = 10
    
    # Simulation-year revenue
    sim_year_revenue_mean_default: float = 250.0
    sim_year_revenue_mean_min: float = 100.0
    sim_year_revenue_mean_max: float = 15000.0
    sim_year_revenue_sigma_default: float = 1.0
    sim_year_revenue_sigma_min: float = 0.1
    sim_year_revenue_sigma_max: float = 2.0
    revenue_per_sim_year_default: float = 87.60
    
    # Customer growth
    customer_delay_default: int = 3
    customer_growth_median_default: float = 0.7
    customer_growth_median_min: float = 0.0
    customer_growth_median_max: float = 3.0
    customer_growth_sigma: float = 1.1
    customer_growth_accel_default: float = 5.0
    customer_growth_accel_min: float = 0.0
    customer_growth_accel_max: float = 10.0
    
    # Churn
    monthly_churn_median_default: float = 5.0
    monthly_churn_median_min: float = 0.0
    monthly_churn_median_max: float = 10.0
    monthly_churn_sigma: float = 1.0


@dataclass
class CostConfig:
    """Configuration for cost model parameters."""
    
    # Infrastructure costs
    hosting_initial_default: float = 1500.0
    hosting_growth_default: float = 15.0
    hosting_growth_min: float = 0.0
    hosting_growth_max: float = 100.0
    
    software_initial_default: float = 2000.0
    software_growth_default: float = 15.0
    software_growth_min: float = 0.0
    software_growth_max: float = 100.0
    
    # Fixed costs
    admin_monthly_default: float = 15000.0 / 12
    conference_monthly_default: float = 5000.0 / 12
    
    # Headcount costs
    salary_per_person_default: float = 20000.0
    initial_headcount_default: int = 5
    initial_headcount_min: int = 1
    initial_headcount_max: int = 20
    headcount_delay_default: int = 0
    headcount_growth_median_default: float = 1.0
    headcount_growth_median_min: float = 0.0
    headcount_growth_median_max: float = 3.0
    headcount_growth_sigma: float = 0.2
    headcount_growth_accel_default: float = 1.0
    headcount_growth_accel_min: float = 0.0
    headcount_growth_accel_max: float = 10.0
    headcount_slowdown_threshold: int = 10
    headcount_slowdown_factor: float = .8
    
    # Variable costs
    support_customer_initial_default: float = 400.0
    support_growth_default: float = 50.0
    support_growth_min: float = 0.0
    support_growth_max: float = 100.0
    
    compute_initial_default: float = 2000.0
    compute_growth_default: float = 100.0
    compute_growth_min: float = 0.0
    compute_growth_max: float = 100.0
    compute_per_sim_year_default: float = 5.0
    compute_per_sim_year_min: float = 1.0
    compute_per_sim_year_max: float = 25.0


@dataclass
class SimulationConfig:
    """Configuration for simulation parameters."""
    
    # Simulation parameters
    months_default: int = 24
    months_min: int = 12
    months_max: int = 36
    
    simulations_default: int = 500
    simulations_min: int = 100
    simulations_max: int = 1000
    
    # Quantiles for analysis
    quantiles: tuple = (0.1, 0.5, 0.9)
    
    # Small value to prevent log(0)
    epsilon: float = 1e-9


# Create global configuration instances
REVENUE_CONFIG = RevenueConfig()
COST_CONFIG = CostConfig()
SIMULATION_CONFIG = SimulationConfig()

# Chart styling configuration - Semantic colors aligned with data meaning
# Professional financial dashboard palette with semantic color associations
CHART_COLORS = {
    # Core semantic colors - aligned with financial meaning
    'primary': '#3B82F6',        # Blue - general primary data
    'secondary': '#6B7280',      # Gray - supporting elements
    'success': '#10B981',        # Green - positive metrics
    'warning': '#F59E0B',        # Amber - caution/warnings
    'danger': '#EF4444',         # Red - alerts/negative metrics
    'info': '#8B5CF6',           # Purple - informational content
    
    # Revenue colors - GREEN spectrum (positive financial flow)
    'revenue': '#10B981',        # Green - total revenue (primary)
    'revenue_secondary': '#059669',   # Dark green - subscription revenue
    'revenue_tertiary': '#34D399',    # Light green - usage revenue
    
    # Cost colors - RED spectrum (negative financial flow)
    'cost': '#EF4444',           # Red - total costs (primary)
    'cost_secondary': '#DC2626',  # Dark red - fixed costs
    'cost_tertiary': '#F87171',   # Light red - variable costs
    
    # Specific cost types - RED variations
    'hosting': '#EF4444',        # Red - hosting costs
    'software': '#DC2626',       # Dark red - software costs  
    'compute': '#F87171',        # Light red - compute costs
    'support': '#FCA5A5',        # Very light red - support costs
    'admin': '#B91C1C',          # Very dark red - admin costs
    'conference': '#7F1D1D',     # Darkest red - conference costs
    
    # People/Headcount - PURPLE spectrum
    'headcount': '#8B5CF6',      # Purple - headcount/team metrics
    'salary': '#7C3AED',         # Dark purple - salary costs
    
    # Performance metrics - BLUE spectrum
    'earnings': '#3B82F6',       # Blue - profitability
    'efficiency': '#06B6D4',     # Cyan - productivity metrics
    
    # Customer metrics - TEAL/CYAN spectrum  
    'customers': '#14B8A6',      # Teal - customer count
    'churn': '#F59E0B'           # Amber - churn (warning)
}

CHART_STYLE = {
    'median_width': 4,           # Thicker median line for visibility
    'percentile_width': 2,       # Standard percentile width
    'percentile_dash': 'dash',   # Dashed lines for percentiles
    'opacity_background': 0.15   # Slightly more opacity for dark theme
} 