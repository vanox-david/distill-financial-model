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
   # Separate revenue stream tracking
   seat_revenue_results, simulation_revenue_results = [], []

   for _ in range(simulations):
       revenue, customers, churn_total = [], [], []
       seat_revenue, simulation_revenue = [], []
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

           # Calculate individual revenue streams
           monthly_seat_revenue = c * avg_seats * seat_fee
           
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
               
               monthly_simulation_revenue = sim_years_total * revenue_per_sim_year
           else:
               monthly_simulation_revenue = 0

           # Total revenue
           month_rev = monthly_seat_revenue + monthly_simulation_revenue

           revenue.append(month_rev)
           seat_revenue.append(monthly_seat_revenue)
           simulation_revenue.append(monthly_simulation_revenue)
           customers.append(c)
           churn_total.append(churn_c)

       rev_results.append(revenue)
       seat_revenue_results.append(seat_revenue)
       simulation_revenue_results.append(simulation_revenue)
       customer_results.append(customers)
       churn_results.append(churn_total)

   def get_quantiles(data):
       df = pd.DataFrame(data)
       return df.quantile(0.1), df.median(), df.quantile(0.9)

   rev_p10, rev_med, rev_p90 = get_quantiles(rev_results)
   seat_p10, seat_med, seat_p90 = get_quantiles(seat_revenue_results)
   sim_p10, sim_med, sim_p90 = get_quantiles(simulation_revenue_results)
   customer_p10, customer_med, customer_p90 = get_quantiles(customer_results)
   churn_p10, churn_med, churn_p90 = get_quantiles(churn_results)

   def plot_metric(p10, median, p90, title, yaxis):
      fig = go.Figure()
      fig.add_trace(go.Scatter(y=median, mode='lines', name='Median', line=dict(color='blue', width=3)))
      fig.add_trace(go.Scatter(y=p10, mode='lines', name='10th Percentile', line=dict(color='red', width=3)))
      fig.add_trace(go.Scatter(y=p90, mode='lines', name='90th Percentile', line=dict(color='red', width=3, dash='dash')))
      fig.update_layout(title=title, xaxis_title='Month', yaxis_title=yaxis)
      st.plotly_chart(fig)

   # Individual revenue stream charts
   plot_metric(rev_p10, rev_med, rev_p90, 'Total Monthly Revenue', 'Revenue ($)')
   plot_metric(seat_p10, seat_med, seat_p90, 'Seat-Based Revenue', 'Revenue ($)')
   plot_metric(sim_p10, sim_med, sim_p90, 'Simulation-Year Revenue', 'Revenue ($)')
   
   # Customer and churn charts
   plot_metric(customer_p10, customer_med, customer_p90, 'Total Customers', 'Customers')
   plot_metric(churn_p10, churn_med, churn_p90, 'Total Monthly Churn', 'Customers Lost')

   shared_data['months'] = months
   shared_data['simulations'] = simulations
   shared_data['customers'] = customer_results
   shared_data['monthly_revenue'] = rev_results
   shared_data['seat_revenue'] = seat_revenue_results
   shared_data['simulation_revenue'] = simulation_revenue_results
   
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

    hosting_initial = costs_sidebar.number_input('Hosting Initial Monthly ($)', value=1500)
    hosting_growth = costs_sidebar.slider('Hosting Growth Rate (%)', 0, 100, 5) / 100

    software_initial = costs_sidebar.number_input('Software Subscriptions Initial Monthly ($)', value=2000)
    software_growth = costs_sidebar.slider('Software Growth Rate (%)', 0, 100, 5) / 100

    admin_monthly = costs_sidebar.number_input('Admin & Legal Monthly ($)', value=15000/12)
    conference_monthly = costs_sidebar.number_input('Conference Fees Monthly ($)', value=5000/12)

    # Headcount-based salary parameters
    salary_per_person = costs_sidebar.number_input('Monthly Salary per Person ($)', value=15000)
    initial_headcount = costs_sidebar.number_input('Initial Headcount', min_value=1, max_value=20, value=5)
    headcount_delay = costs_sidebar.number_input('Months Delay for Headcount Growth', min_value=0, max_value=months, value=6)
    headcount_growth_median = costs_sidebar.slider('Median Headcount Adds', 0.0, 3.0, 1.0)
    headcount_growth_sigma = 1.0
    headcount_growth_accel = costs_sidebar.slider('Monthly Headcount Growth Acceleration (%)', 0.0, 10.0, 3.0) / 100

    benefits_monthly = costs_sidebar.number_input('Monthly Benefits ($)', value=2000)

    support_customer_initial = costs_sidebar.number_input('Support Cost per Customer Monthly ($)', value=400)
    support_growth = costs_sidebar.slider('Support Growth Rate (%)', 0, 100, 50) / 100

    compute_initial = costs_sidebar.number_input('Compute Initial Monthly ($)', value=2000)
    compute_growth = costs_sidebar.slider('Compute Growth Rate (%)', 0, 100, 100) / 100


    total_costs, fixed_costs, variable_costs, customer_costs, salary_costs, headcount_results = [], [], [], [], [], []
    # Individual cost component tracking
    hosting_costs, software_costs, admin_costs, conference_costs, benefits_costs = [], [], [], [], []
    compute_costs = []

    customers = np.array(shared_data['customers'])

    for sim in range(simulations):
        sim_total, sim_fixed, sim_variable, sim_customer, sim_salary, sim_headcount = [], [], [], [], [], []
        # Individual cost tracking
        sim_hosting, sim_software, sim_admin, sim_conference, sim_benefits = [], [], [], [], []
        sim_compute = []
        
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

            # Individual cost calculations
            hosting_cost = hosting_initial*(1+hosting_growth)**factor
            software_cost = software_initial*(1+software_growth)**factor
            admin_cost = admin_monthly
            conference_cost = conference_monthly
            salary = headcount * salary_per_person
            benefits_cost = benefits_monthly
            
            fixed = hosting_cost + software_cost + admin_cost + conference_cost + benefits_cost + salary
            
            compute_cost = compute_initial * (1 + compute_growth)**factor
            customer_cost = support_customer_initial*(1+support_growth)**factor * customers[sim, month]

            variable = compute_cost  + customer_cost
            total = fixed + variable

            # Store individual components
            sim_total.append(total)
            sim_fixed.append(fixed)
            sim_variable.append(variable)
            sim_customer.append(customer_cost)
            sim_salary.append(salary)
            sim_headcount.append(headcount)
            
            # Individual cost components
            sim_hosting.append(hosting_cost)
            sim_software.append(software_cost)
            sim_admin.append(admin_cost)
            sim_conference.append(conference_cost)
            sim_benefits.append(benefits_cost)
            sim_compute.append(compute_cost)

        total_costs.append(sim_total)
        fixed_costs.append(sim_fixed)
        variable_costs.append(sim_variable)
        customer_costs.append(sim_customer)
        salary_costs.append(sim_salary)
        headcount_results.append(sim_headcount)
        
        # Individual cost results
        hosting_costs.append(sim_hosting)
        software_costs.append(sim_software)
        admin_costs.append(sim_admin)
        conference_costs.append(sim_conference)
        benefits_costs.append(sim_benefits)
        compute_costs.append(sim_compute)

    # Store headcount data for other tabs
    shared_data['headcount'] = headcount_results

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

    # Aggregate cost charts
    st.subheader("Aggregate Cost Views")
    plot_costs(total_costs, 'Total Monthly Costs')
    plot_costs(fixed_costs, 'Fixed Monthly Costs')
    plot_costs(variable_costs, 'Variable Monthly Costs')
    
    # Individual cost component charts
    st.subheader("Individual Cost Components")
    plot_costs(salary_costs, 'Salary Costs')
    plot_costs(hosting_costs, 'Hosting Costs')
    plot_costs(software_costs, 'Software Subscription Costs')
    plot_costs(compute_costs, 'Compute Costs')
    plot_costs(customer_costs, 'Customer Support Costs')
    plot_costs(admin_costs, 'Admin & Legal Costs')
    plot_costs(conference_costs, 'Conference Costs')
    plot_costs(benefits_costs, 'Benefits Costs')
    
    # Headcount chart
    st.subheader("Team Growth")
    plot_headcount(headcount_results, 'Headcount Growth')

    # Summary metrics for costs
    final_month_costs = np.array([sim[-1] for sim in total_costs])
    final_month_headcount = np.array([sim[-1] for sim in headcount_results])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Final Month Median Costs", f"${np.median(final_month_costs):,.0f}")
    with col2:
        st.metric("Final Month Median Headcount", f"{np.median(final_month_headcount):.0f}")
    with col3:
        st.metric("Cost per Employee (Final Month)", f"${np.median(final_month_costs)/np.median(final_month_headcount):,.0f}")

# Updated Earnings Dashboard
with earnings_tab:
    st.header('Earnings Dashboard')

    revenue_simulations = np.array(shared_data['monthly_revenue'])
    seat_revenue_simulations = np.array(shared_data['seat_revenue'])
    simulation_revenue_simulations = np.array(shared_data['simulation_revenue'])
    cost_simulations = np.array(total_costs)
    headcount_simulations = np.array(shared_data['headcount'])

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

    def plot_revenue_costs(data, title, color='blue'):
        p10, med, p90 = np.percentile(data, [10, 50, 90], axis=0)
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=med, name='Median', line=dict(color=color, width=3)))
        fig.add_trace(go.Scatter(y=p10, name='10th Percentile', line=dict(color='red', width=2, dash='dot')))
        fig.add_trace(go.Scatter(y=p90, name='90th Percentile', line=dict(color='red', width=2, dash='dot')))
        fig.update_layout(title=title, xaxis_title='Month', yaxis_title='Amount ($)')
        st.plotly_chart(fig)

    def plot_headcount_earnings(data, title):
        p10, med, p90 = np.percentile(data, [10, 50, 90], axis=0)
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=med, name='Median', line=dict(color='green', width=3)))
        fig.add_trace(go.Scatter(y=p10, name='10th Percentile', line=dict(color='orange', width=2, dash='dot')))
        fig.add_trace(go.Scatter(y=p90, name='90th Percentile', line=dict(color='orange', width=2, dash='dot')))
        fig.update_layout(title=title, xaxis_title='Month', yaxis_title='Headcount')
        st.plotly_chart(fig)

    # Main earnings charts
    st.subheader("Earnings Overview")
    plot_earnings(earnings_simulations, 'Monthly Earnings')
    plot_earnings(cumulative_earnings, 'Cumulative Earnings')
    
    # Revenue breakdown
    st.subheader("Revenue Breakdown")
    plot_revenue_costs(revenue_simulations, 'Total Revenue', 'green')
    plot_revenue_costs(seat_revenue_simulations, 'Seat-Based Revenue', 'darkgreen')
    plot_revenue_costs(simulation_revenue_simulations, 'Simulation-Year Revenue', 'lightgreen')
    
    # Cost breakdown
    st.subheader("Cost Breakdown")
    plot_revenue_costs(cost_simulations, 'Total Costs', 'red')
    plot_revenue_costs(fixed_costs, 'Fixed Costs', 'darkred')
    plot_revenue_costs(variable_costs, 'Variable Costs', 'orange')
    
    # Team and productivity
    st.subheader("Team and Productivity")
    plot_headcount_earnings(headcount_simulations, 'Headcount Evolution')

    # Calculate per-employee metrics
    revenue_per_employee = revenue_simulations / np.maximum(headcount_simulations, 1)  # Avoid division by zero
    earnings_per_employee = earnings_simulations / np.maximum(headcount_simulations, 1)

    plot_earnings(revenue_per_employee, 'Revenue per Employee')
    plot_earnings(earnings_per_employee, 'Earnings per Employee')

    break_even_months = [np.argmax(cum > 0) if np.any(cum > 0) else months for cum in cumulative_earnings]
    median_break_even = np.median(break_even_months)

    # Enhanced metrics
    final_earnings = np.array([sim[-1] for sim in cumulative_earnings])
    final_headcount = np.array([sim[-1] for sim in headcount_simulations])
    final_revenue = np.array([sim[-1] for sim in revenue_simulations])

    st.subheader("Key Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Median Break-even Month", f"{int(median_break_even)}")
    with col2:
        st.metric("Final Month Median Headcount", f"{np.median(final_headcount):.0f}")
    with col3:
        st.metric("Final Cumulative Earnings", f"${np.median(final_earnings):,.0f}")

    col4, col5, col6 = st.columns(3)
    with col4:
        st.metric("Final Revenue per Employee", f"${np.median(final_revenue/np.maximum(final_headcount, 1)):,.0f}")
    with col5:
        final_monthly_earnings = np.array([sim[-1] for sim in earnings_simulations])
        st.metric("Final Monthly Earnings", f"${np.median(final_monthly_earnings):,.0f}")
    with col6:
        st.metric("Final Earnings per Employee", f"${np.median(final_monthly_earnings/np.maximum(final_headcount, 1)):,.0f}")

