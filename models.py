"""
Core models for financial simulation.

This module contains the business logic for revenue and cost calculations,
separated from the UI and simulation orchestration.
"""

import numpy as np
from typing import List, Tuple, Dict, NamedTuple
from dataclasses import dataclass

from config import REVENUE_CONFIG, COST_CONFIG, SIMULATION_CONFIG


class RevenueParameters(NamedTuple):
    """Parameters for revenue model simulation."""
    seat_fee: float
    avg_seats: int
    sim_year_revenue_mean: float
    sim_year_revenue_sigma: float
    revenue_per_sim_year: float
    customer_delay: int
    customer_growth_median: float
    customer_growth_sigma: float
    customer_growth_accel: float
    monthly_churn_median: float
    monthly_churn_sigma: float


class CostParameters(NamedTuple):
    """Parameters for cost model simulation."""
    hosting_initial: float
    hosting_growth: float
    software_initial: float
    software_growth: float
    admin_monthly: float
    conference_monthly: float
    salary_per_person: float
    initial_headcount: int
    headcount_delay: int
    headcount_growth_median: float
    headcount_growth_sigma: float
    headcount_growth_accel: float
    support_customer_initial: float
    support_growth: float
    compute_initial: float
    compute_growth: float
    compute_per_sim_year: float


@dataclass
class SimulationResults:
    """Results from a single simulation run."""
    # Revenue streams
    total_revenue: List[float]
    seat_revenue: List[float]
    simulation_revenue: List[float]
    
    # Customer metrics
    customers: List[int]
    churn: List[int]
    
    # Cost components
    total_costs: List[float]
    fixed_costs: List[float]
    variable_costs: List[float]
    salary_costs: List[float]
    hosting_costs: List[float]
    software_costs: List[float]
    admin_costs: List[float]
    conference_costs: List[float]
    compute_costs: List[float]
    customer_support_costs: List[float]
    
    # Headcount
    headcount: List[int]


class RevenueModel:
    """Revenue calculation model using Monte Carlo simulation."""
    
    def __init__(self, params: RevenueParameters):
        """
        Initialize revenue model with parameters.
        
        Args:
            params: Revenue model parameters
        """
        self.params = params
    
    def simulate_single_run(self, months: int) -> Tuple[List[float], List[float], List[float], List[int], List[int], List[float]]:
        """
        Run a single revenue simulation.
        
        Args:
            months: Number of months to simulate
            
        Returns:
            Tuple of (total_revenue, seat_revenue, simulation_revenue, customers, churn, simulation_years)
        """
        revenue, seat_revenue, simulation_revenue = [], [], []
        customers, churn_total = [], []
        simulation_years_total = []
        
        customer_count = 0
        customer_growth = self.params.customer_growth_median
        
        for month in range(months):
            # Customer acquisition
            if month >= self.params.customer_delay:
                new_customers = int(np.random.lognormal(
                    mean=np.log(customer_growth + SIMULATION_CONFIG.epsilon), 
                    sigma=self.params.customer_growth_sigma
                ))
            else:
                new_customers = 0
            
            customer_count += new_customers
            
            # Customer churn
            churn_rate = np.random.lognormal(
                mean=np.log(self.params.monthly_churn_median + SIMULATION_CONFIG.epsilon), 
                sigma=self.params.monthly_churn_sigma
            )
            churn_rate = min(churn_rate, 0.5)  # Cap churn at 50%
            month_churn = int(np.random.binomial(customer_count, churn_rate))
            customer_count = max(0, customer_count - month_churn)
            
            # Update growth rate
            customer_growth *= (1 + self.params.customer_growth_accel)
            
            # Calculate revenue streams
            monthly_seat_revenue = customer_count * self.params.avg_seats * self.params.seat_fee
            
            # Simulation-year revenue (random per customer)
            if customer_count > 0:
                sim_years_total = 0
                for _ in range(customer_count):
                    customer_sim_years = np.random.lognormal(
                        mean=np.log(self.params.sim_year_revenue_mean + SIMULATION_CONFIG.epsilon),
                        sigma=self.params.sim_year_revenue_sigma
                    )
                    sim_years_total += customer_sim_years
                
                monthly_simulation_revenue = sim_years_total * self.params.revenue_per_sim_year
            else:
                sim_years_total = 0
                monthly_simulation_revenue = 0
            
            # Total revenue
            total_monthly_revenue = monthly_seat_revenue + monthly_simulation_revenue
            
            # Store results
            revenue.append(total_monthly_revenue)
            seat_revenue.append(monthly_seat_revenue)
            simulation_revenue.append(monthly_simulation_revenue)
            customers.append(customer_count)
            churn_total.append(month_churn)
            simulation_years_total.append(sim_years_total)
        
        return revenue, seat_revenue, simulation_revenue, customers, churn_total, simulation_years_total


class CostModel:
    """Cost calculation model using Monte Carlo simulation."""
    
    def __init__(self, params: CostParameters):
        """
        Initialize cost model with parameters.
        
        Args:
            params: Cost model parameters
        """
        self.params = params
    
    def simulate_single_run(self, months: int, customers: List[int], simulation_years: List[float]) -> Tuple[
        List[float], List[float], List[float], List[float], List[float],
        List[float], List[float], List[float], List[float], List[float],
        List[int]
    ]:
        """
        Run a single cost simulation.
        
        Args:
            months: Number of months to simulate
            customers: Customer count for each month
            simulation_years: Total simulation-years for each month
            
        Returns:
            Tuple of cost components and headcount
        """
        total_costs, fixed_costs, variable_costs = [], [], []
        salary_costs, hosting_costs, software_costs = [], [], []
        admin_costs, conference_costs = [], []
        compute_costs, customer_support_costs = [], []
        headcount_results = []
        
        headcount = self.params.initial_headcount
        headcount_growth = self.params.headcount_growth_median
        
        for month in range(months):
            # Headcount growth simulation
            if month >= self.params.headcount_delay:
                # Apply slowdown for larger teams
                if headcount >= COST_CONFIG.headcount_slowdown_threshold:
                    adjusted_growth = headcount_growth * COST_CONFIG.headcount_slowdown_factor
                else:
                    adjusted_growth = headcount_growth
                
                new_headcount = int(np.random.lognormal(
                    mean=np.log(adjusted_growth + SIMULATION_CONFIG.epsilon),
                    sigma=self.params.headcount_growth_sigma
                ))
            else:
                new_headcount = 0
            
            headcount += new_headcount
            headcount_growth *= (1 + self.params.headcount_growth_accel)
            
            # Calculate individual cost components
            year_factor = month // 12  # Annual growth factor
            
            hosting_cost = self.params.hosting_initial * (1 + self.params.hosting_growth) ** year_factor
            software_cost = self.params.software_initial * (1 + self.params.software_growth) ** year_factor
            admin_cost = self.params.admin_monthly
            conference_cost = self.params.conference_monthly
            salary_cost = headcount * self.params.salary_per_person
            
            # Variable costs
            # Compute cost now depends on simulation-years
            base_compute_cost = self.params.compute_initial * (1 + self.params.compute_growth) ** year_factor
            sim_year_compute_cost = simulation_years[month] * self.params.compute_per_sim_year
            compute_cost = base_compute_cost + sim_year_compute_cost
            customer_support_cost = (
                self.params.support_customer_initial * 
                (1 + self.params.support_growth) ** year_factor * 
                customers[month]
            )
            
            # Aggregate costs
            fixed_cost = (
                hosting_cost + software_cost + admin_cost + 
                conference_cost + salary_cost
            )
            variable_cost = compute_cost + customer_support_cost
            total_cost = fixed_cost + variable_cost
            
            # Store results
            total_costs.append(total_cost)
            fixed_costs.append(fixed_cost)
            variable_costs.append(variable_cost)
            salary_costs.append(salary_cost)
            hosting_costs.append(hosting_cost)
            software_costs.append(software_cost)
            admin_costs.append(admin_cost)
            conference_costs.append(conference_cost)
            compute_costs.append(compute_cost)
            customer_support_costs.append(customer_support_cost)
            headcount_results.append(headcount)
        
        return (
            total_costs, fixed_costs, variable_costs, salary_costs,
            hosting_costs, software_costs, admin_costs, conference_costs,
            compute_costs, customer_support_costs, headcount_results
        )


class FinancialModel:
    """Complete financial model combining revenue and cost models."""
    
    def __init__(self, revenue_params: RevenueParameters, cost_params: CostParameters):
        """
        Initialize financial model.
        
        Args:
            revenue_params: Revenue model parameters
            cost_params: Cost model parameters
        """
        self.revenue_model = RevenueModel(revenue_params)
        self.cost_model = CostModel(cost_params)
    
    def run_simulation(self, months: int, num_simulations: int) -> List[SimulationResults]:
        """
        Run complete financial simulation.
        
        Args:
            months: Number of months to simulate
            num_simulations: Number of Monte Carlo simulations
            
        Returns:
            List of simulation results
        """
        results = []
        
        for _ in range(num_simulations):
            # Run revenue simulation
            (total_revenue, seat_revenue, simulation_revenue, 
             customers, churn, simulation_years) = self.revenue_model.simulate_single_run(months)
            
            # Run cost simulation
            (total_costs, fixed_costs, variable_costs, salary_costs,
             hosting_costs, software_costs, admin_costs, conference_costs,
             compute_costs, customer_support_costs, 
             headcount) = self.cost_model.simulate_single_run(months, customers, simulation_years)
            
            # Create result object
            result = SimulationResults(
                total_revenue=total_revenue,
                seat_revenue=seat_revenue,
                simulation_revenue=simulation_revenue,
                customers=customers,
                churn=churn,
                total_costs=total_costs,
                fixed_costs=fixed_costs,
                variable_costs=variable_costs,
                salary_costs=salary_costs,
                hosting_costs=hosting_costs,
                software_costs=software_costs,
                admin_costs=admin_costs,
                conference_costs=conference_costs,
                compute_costs=compute_costs,
                customer_support_costs=customer_support_costs,
                headcount=headcount
            )
            
            results.append(result)
        
        return results 