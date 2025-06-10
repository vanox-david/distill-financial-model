# streamlit_revenue_simulation.py
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import io

st.title('Distill Financials Dashboard')
revenue_tab, costs_tab, earnings_tab = st.tabs(["Revenue", "Costs", "Earnings"])

# Shared data dictionary
shared_data = {}

# Sidebar placeholder
sidebar = st.sidebar

with revenue_tab:
   st.header('Revenue Dashboard')

   sidebar.header("Revenue Assumptions")

   months = sidebar.number_input('Projection Period (Months)', min_value=12, max_value=72, value=48)
   simulations = sidebar.number_input('Number of Simulations', min_value=100, max_value=1000, value=250)

   seat_fee = sidebar.number_input('Monthly Fee per Seat ($)', value=1000)
   avg_seats = sidebar.slider('Average Seats per Customer', 1, 10, 3)
   
   # Simulation-year revenue parameters
   sim_year_revenue_mean = sidebar.number_input('Mean Simulation-Years per Customer per Month', min_value=500.0, max_value=15000.0, value=2000.0)
   sim_year_revenue_sigma = sidebar.slider('Simulation-Year Usage Volatility', 0.1, 2.0, 1.0)
   revenue_per_sim_year = sidebar.number_input('Revenue per Simulation-Year ($)', value=0.10)

   customer_delay = sidebar.number_input('Months Delay for Customer Acquisition', min_value=0, max_value=months, value=9)

   customer_growth_median = sidebar.slider('Median Customer Adds', 0.0, 3.0, .7)
   customer_growth_sigma = 1.1
   customer_growth_accel = sidebar.slider('Monthly Customer Growth Acceleration (%)', 0.0, 10.0, 5.0) / 100

   monthly_churn_median = sidebar.slider('Median Monthly Churn Rate (%)', 0.0, 10.0, 5.0) / 100
   monthly_churn_sigma = 1.0

   rev_results, customer_results, churn_results = [], [], []

   for _ in range(simulations):
       revenue, customers, churn_total = [], [], []
       c = 0
       customer_growth = customer_growth_median

       for m in range(months):
           if m >= customer_delay:
              new_customers = int(np.random.lognormal(mean=np.log(customer_growth + 1e-9), sigma=customer_growth_sigma))
           else:
              new_customers = 0
          
           c += new_customers

           churn_rate = np.random.lognormal(mean=np.log(monthly_churn_median + 1e-9), sigma=monthly_churn_sigma)
           churn_rate = min(churn_rate, 0.5)
           churn_c = int(np.random.binomial(c, churn_rate))
           c = max(0, c - churn_c)

           customer_growth *= (1 + customer_growth_accel)

           # Calculate simulation-year revenue with random process
           if c > 0:
               # Each customer has random simulation usage
               sim_years_total = 0
               for _ in range(c):
                   customer_sim_years = np.random.lognormal(
                       mean=np.log(sim_year_revenue_mean + 1e-9), 
                       sigma=sim_year_revenue_sigma
                   )
                   sim_years_total += customer_sim_years
               
               simulation_revenue = sim_years_total * revenue_per_sim_year
           else:
               simulation_revenue = 0

           # Revenue calculation: seat fees + simulation revenue
           month_rev = (c * avg_seats * seat_fee) + simulation_revenue

           revenue.append(month_rev)
           customers.append(c)
           churn_total.append(churn_c)

       rev_results.append(revenue)
       customer_results.append(customers)
       churn_results.append(churn_total)

   def get_quantiles(data):
       df = pd.DataFrame(data)
       return df.quantile(0.1), df.median(), df.quantile(0.9)

   rev_p10, rev_med, rev_p90 = get_quantiles(rev_results)
   customer_p10, customer_med, customer_p90 = get_quantiles(customer_results)
   churn_p10, churn_med, churn_p90 = get_quantiles(churn_results)

   fig = go.Figure()
   for sim in rev_results:
      fig.add_trace(go.Scatter(y=sim, mode='lines', line=dict(color='lightgrey'), opacity=0.1, showlegend=False))
   fig.add_trace(go.Scatter(y=rev_med, mode='lines', name='Median', line=dict(color='blue', width=3)))
   fig.add_trace(go.Scatter(y=rev_p10, mode='lines', name='10th Percentile', line=dict(color='red', width=3)))
   fig.add_trace(go.Scatter(y=rev_p90, mode='lines', name='90th Percentile', line=dict(color='red', width=3, dash='dash')))
   fig.update_layout(title='Monthly Revenue Projection', xaxis_title='Month', yaxis_title='Revenue ($)')
   st.plotly_chart(fig)

   def plot_metric(p10, median, p90, title, yaxis):
      fig = go.Figure()
      fig.add_trace(go.Scatter(y=median, mode='lines', name='Median', line=dict(color='blue', width=3)))
      fig.add_trace(go.Scatter(y=p10, mode='lines', name='10th Percentile', line=dict(color='red', width=3)))
      fig.add_trace(go.Scatter(y=p90, mode='lines', name='90th Percentile', line=dict(color='red', width=3, dash='dash')))
      fig.update_layout(title=title, xaxis_title='Month', yaxis_title=yaxis)
      st.plotly_chart(fig)

   plot_metric(customer_p10, customer_med, customer_p90, 'Total Customers', 'Customers')
   plot_metric(churn_p10, churn_med, churn_p90, 'Total Monthly Churn', 'Customers Lost')

   shared_data['months'] = months
   shared_data['simulations'] = simulations
   shared_data['customers'] = customer_results
   shared_data['monthly_revenue'] = rev_results
   
   export_df = pd.DataFrame({
       'Month': np.arange(1, months + 1),
       'Median Revenue': rev_med,
       '10th Percentile Revenue': rev_p10,
       '90th Percentile Revenue': rev_p90,
       'Median Customers': customer_med.astype(int),
       'Median Churn': churn_med.astype(int)
   })
   
   output = io.BytesIO()
   with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
       export_df.to_excel(writer, sheet_name='Projections', index=False)
   
   st.download_button(
       label="Export All Projections to Excel",
       data=output.getvalue(),
       file_name="detailed_revenue_projections.xlsx",
       mime="application/vnd.ms-excel"
   )

# Updated Costs Dashboard
with costs_tab:
    st.header('Costs Dashboard')
    costs_sidebar = st.sidebar
    costs_sidebar.header("Cost Assumptions")

    hosting_initial = costs_sidebar.number_input('Hosting Initial ($)', value=1500)
    hosting_growth = costs_sidebar.slider('Hosting Growth Rate (%)', 0, 100, 50) / 100

    software_initial = costs_sidebar.number_input('Software Subscriptions Initial Monthly ($)', value=2000)
    software_growth = costs_sidebar.slider('Software Growth Rate (%)', 0, 100, 20) / 100

    admin_annual = costs_sidebar.number_input('Admin & Legal Annual ($)', value=15000)
    conference_annual = costs_sidebar.number_input('Conference Fees Annual ($)', value=5000)

    # Headcount-based salary parameters
    salary_per_person = costs_sidebar.number_input('Monthly Salary per Person ($)', value=8000)
    initial_headcount = costs_sidebar.number_input('Initial Headcount', min_value=1, max_value=20, value=5)
    headcount_delay = costs_sidebar.number_input('Months Delay for Headcount Growth', min_value=0, max_value=months, value=6)
    headcount_growth_median = costs_sidebar.slider('Median Headcount Adds', 0.0, 3.0, 1)
    headcount_growth_sigma = 1.0
    headcount_growth_accel = costs_sidebar.slider('Monthly Headcount Growth Acceleration (%)', 0.0, 10.0, 3.0) / 100

    benefits_monthly = costs_sidebar.number_input('Monthly Benefits ($)', value=2000)

    support_customer_initial = costs_sidebar.number_input('Support Cost per Customer ($)', value=400)
    support_growth = costs_sidebar.slider('Support Growth Rate (%)', 0, 100, 50) / 100

    compute_initial = costs_sidebar.number_input('Compute Initial Monthly ($)', value=2000)
    compute_growth = costs_sidebar.slider('Compute Growth Rate (%)', 0, 100, 100) / 100

    api_initial = costs_sidebar.number_input('API Initial ($)', value=200)
    api_growth = costs_sidebar.slider('API Growth Rate (%)', 0, 100, 50) / 100

    total_costs, fixed_costs, variable_costs, customer_costs, salary_costs, headcount_results = [], [], [], [], [], []

    customers = np.array(shared_data['customers'])

    for sim in range(simulations):
        sim_total, sim_fixed, sim_variable, sim_customer, sim_salary, sim_headcount = [], [], [], [], [], []
        headcount = initial_headcount
        headcount_growth = headcount_growth_median

        for month in range(months):
            # Headcount growth simulation
            if month >= headcount_delay:
                # Slow down growth above 15 people
                if headcount >= 15:
                    # Apply 50% reduction in growth rate for larger teams
                    adjusted_growth = headcount_growth * 0.5
                else:
                    adjusted_growth = headcount_growth
                
                new_headcount = int(np.random.lognormal(mean=np.log(adjusted_growth + 1e-9), sigma=headcount_growth_sigma))
            else:
                new_headcount = 0
            
            headcount += new_headcount
            headcount_growth *= (1 + headcount_growth_accel)

            factor = month // 12

            salary = headcount * salary_per_person
            fixed = (hosting_initial*(1+hosting_growth)**factor + software_initial*(1+software_growth)**factor +
                     admin_annual/12 + conference_annual/12 + benefits_monthly + salary)
            
            compute = compute_initial * (1 + compute_growth)**factor
            api = api_initial * (1 + api_growth)**factor

            customer_cost = support_customer_initial*(1+support_growth)**factor * customers[sim, month]

            variable = compute + api + customer_cost

            total = fixed + variable

            sim_total.append(total)
            sim_fixed.append(fixed)
            sim_variable.append(variable)
            sim_customer.append(customer_cost)
            sim_salary.append(salary)
            sim_headcount.append(headcount)

        total_costs.append(sim_total)
        fixed_costs.append(sim_fixed)
        variable_costs.append(sim_variable)
        customer_costs.append(sim_customer)
        salary_costs.append(sim_salary)
        headcount_results.append(sim_headcount)

    def plot_costs(data, title):
        p10, med, p90 = np.percentile(data, [10, 50, 90], axis=0)
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=med, name='Median', line=dict(color='blue', width=3)))
        fig.add_trace(go.Scatter(y=p10, name='10th Percentile', line=dict(color='red', width=2, dash='dot')))
        fig.add_trace(go.Scatter(y=p90, name='90th Percentile', line=dict(color='red', width=2, dash='dot')))
        fig.update_layout(title=title, xaxis_title='Month', yaxis_title='Cost ($)')
        st.plotly_chart(fig)

    def plot_headcount(data, title):
        p10, med, p90 = np.percentile(data, [10, 50, 90], axis=0)
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=med, name='Median', line=dict(color='blue', width=3)))
        fig.add_trace(go.Scatter(y=p10, name='10th Percentile', line=dict(color='red', width=2, dash='dot')))
        fig.add_trace(go.Scatter(y=p90, name='90th Percentile', line=dict(color='red', width=2, dash='dot')))
        fig.update_layout(title=title, xaxis_title='Month', yaxis_title='Headcount')
        st.plotly_chart(fig)

    plot_costs(total_costs, 'Total Monthly Costs')
    plot_costs(fixed_costs, 'Fixed Monthly Costs')
    plot_costs(variable_costs, 'Variable Monthly Costs')
    plot_costs(customer_costs, 'Customer Support Costs')
    plot_costs(salary_costs, 'Salary Costs')
    plot_headcount(headcount_results, 'Headcount Growth')

# Updated Earnings Dashboard
with earnings_tab:
    st.header('Earnings Dashboard')

    revenue_simulations = np.array(shared_data['monthly_revenue'])
    cost_simulations = np.array(total_costs)

    earnings_simulations = revenue_simulations - cost_simulations
    cumulative_earnings = np.cumsum(earnings_simulations, axis=1)

    def plot_earnings(data, title):
        p10, med, p90 = np.percentile(data, [10, 50, 90], axis=0)
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=med, name='Median', line=dict(color='blue', width=3)))
        fig.add_trace(go.Scatter(y=p10, name='10th Percentile', line=dict(color='red', width=2, dash='dot')))
        fig.add_trace(go.Scatter(y=p90, name='90th Percentile', line=dict(color='red', width=2, dash='dot')))
        fig.update_layout(title=title, xaxis_title='Month', yaxis_title='Earnings ($)')
        st.plotly_chart(fig)

    plot_earnings(earnings_simulations, 'Monthly Earnings')
    plot_earnings(cumulative_earnings, 'Cumulative Earnings')

    break_even_months = [np.argmax(cum > 0) if np.any(cum > 0) else months for cum in cumulative_earnings]
    median_break_even = np.median(break_even_months)

    st.metric(label="Median Break-even Month", value=int(median_break_even))

