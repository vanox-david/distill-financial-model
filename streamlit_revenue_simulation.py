# streamlit_revenue_simulation.py
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import io

st.title('Distill Financial Dashboard')
revenue_tab, costs_tab, earnings_tab = st.tabs(["Revenue", "Costs", "Earnings"])

# Shared data dictionary
shared_data = {}

with revenue_tab:
   st.header('Revenue Dashboard')

   st.sidebar.header("Set Your Assumptions")

   months = st.sidebar.number_input('Projection Period (Months)', min_value=12, max_value=60, value=36)
   simulations = st.sidebar.number_input('Number of Simulations', min_value=100, max_value=1000, value=250)

   dev_base_fee = st.sidebar.number_input('Monthly Developer Base Fee ($)', value=5000)
   dev_seat_fee = st.sidebar.number_input('Monthly Fee per Additional Seat ($)', value=1000)
   avg_seats = st.sidebar.slider('Average Seats per Developer', 1, 10, 3)
   fin_project_fee = st.sidebar.number_input('Revenue per Financier Project ($)', value=10000)

   initial_dev = st.sidebar.number_input('Initial Developer Customers', min_value=0, max_value=20, value=2)
   initial_fin = st.sidebar.number_input('Initial Financier Customers', min_value=0, max_value=20, value=0)

   dev_growth_median = st.sidebar.slider('Median Developer Adds', 0.0, 3.0, .7)
   dev_growth_sigma = st.sidebar.slider('Developer Growth Volatility', 0.1, 2.0, 1.1)
   dev_growth_accel = st.sidebar.slider('Monthly Developer Growth Acceleration (%)', 0.0, 10.0, 5.0) / 100

   fin_growth_median = st.sidebar.slider('Median Financier Adds', 0.0, 5.0, .5)
   fin_growth_sigma = st.sidebar.slider('Financier Growth Volatility', 0.1, 2.0, 1.0)
   fin_growth_accel = st.sidebar.slider('Monthly Financier Growth Acceleration (%)', 0.0, 10.0, 2.0) / 100

   monthly_churn_median = st.sidebar.slider('Median Monthly Churn Rate (%)', 0.0, 10.0, 5.0) / 100
   monthly_churn_sigma = st.sidebar.slider('Churn Rate Volatility', 0.01, 2.0, 1.0)

   rev_results, dev_results, fin_results, churn_results = [], [], [], []

   for _ in range(simulations):
       revenue, dev_customers, fin_customers, churn_total = [], [], [], []
       d, f = initial_dev, initial_fin
       dev_growth = dev_growth_median
       fin_growth = fin_growth_median

       for m in range(months):
           new_dev = int(np.random.lognormal(mean=np.log(dev_growth + 1e-9), sigma=dev_growth_sigma))
           new_fin = int(np.random.lognormal(mean=np.log(fin_growth + 1e-9), sigma=fin_growth_sigma))
           d += new_dev
           f += new_fin

           churn_rate = np.random.lognormal(mean=np.log(monthly_churn_median + 1e-9), sigma=monthly_churn_sigma)
           churn_rate = min(churn_rate, 0.5)
           churn_d = int(np.random.binomial(d, churn_rate))
           churn_f = int(np.random.binomial(f, churn_rate))
           d = max(0, d - churn_d)
           f = max(0, f - churn_f)

           dev_growth *= (1 + dev_growth_accel)
           fin_growth *= (1 + fin_growth_accel)

           month_rev = (d * (dev_base_fee + avg_seats * dev_seat_fee)) + (f * fin_project_fee)

           revenue.append(month_rev)
           dev_customers.append(d)
           fin_customers.append(f)
           churn_total.append(churn_d + churn_f)

       rev_results.append(revenue)
       dev_results.append(dev_customers)
       fin_results.append(fin_customers)
       churn_results.append(churn_total)

   def get_quantiles(data):
       df = pd.DataFrame(data)
       return df.quantile(0.1), df.median(), df.quantile(0.9)

   rev_p10, rev_med, rev_p90 = get_quantiles(rev_results)
   dev_p10, dev_med, dev_p90 = get_quantiles(dev_results)
   fin_p10, fin_med, fin_p90 = get_quantiles(fin_results)
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

   plot_metric(dev_p10, dev_med, dev_p90, 'Total Developer Customers', 'Developers')
   plot_metric(fin_p10, fin_med, fin_p90, 'Total Financier Customers', 'Financiers')
   plot_metric(churn_p10, churn_med, churn_p90, 'Total Monthly Churn', 'Customers Lost')


   shared_data['months'] = months
   shared_data['simulations'] = simulations
   shared_data['dev_customers'] = dev_med
   shared_data['fin_customers'] = fin_med
   shared_data['monthly_revenue'] = rev_med
   
   export_df = pd.DataFrame({
       'Month': np.arange(1, months + 1),
       'Median Revenue': rev_med,
       '10th Percentile Revenue': rev_p10,
       '90th Percentile Revenue': rev_p90,
       'Median Developers': dev_med.astype(int),
       'Median Financiers': fin_med.astype(int),
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
   
with costs_tab:
    st.header('Costs Dashboard')

    st.subheader('Fixed Monthly Costs')
    hosting_initial = st.number_input('Hosting Initial ($)', value=1500)
    hosting_growth = st.slider('Hosting Growth Rate (%)', 0, 100, 50) / 100

    software_initial = st.number_input('Software Subscriptions Initial ($)', value=4000)
    software_growth = st.slider('Software Growth Rate (%)', 0, 100, 20) / 100

    admin_annual = st.number_input('Admin & Legal Annual ($)', value=5000)
    conference_annual = st.number_input('Conference Fees Annual ($)', value=15000)

    salary_initial = st.number_input('Salaries Initial Monthly ($)', value=24000)
    salary_growth = st.slider('Salary Growth Rate (%)', 0, 100, 100) / 100

    benefits_monthly = st.number_input('Monthly Benefits ($)', value=2000)

    st.subheader('Variable Costs per Customer')
    support_dev_initial = st.number_input('Support Cost per Developer ($)', value=200)
    support_fin_initial = st.number_input('Support Cost per Financier ($)', value=600)
    support_growth = st.slider('Support Growth Rate (%)', 0, 100, 50) / 100

    compute_initial = st.number_input('Compute Initial ($)', value=500)
    compute_growth = st.slider('Compute Growth Rate (%)', 0, 100, 100) / 100

    api_initial = st.number_input('API Initial ($)', value=200)
    api_growth = st.slider('API Growth Rate (%)', 0, 100, 50) / 100

    # Cost calculations
    monthly_fixed, monthly_variable, fin_costs, dev_costs, salary_costs, total_costs = [], [], [], [], [], []

    for month in range(months):
        factor = month // 12

        fixed = (hosting_initial*(1+hosting_growth)**factor + software_initial*(1+software_growth)**factor +
                 admin_annual/12 + conference_annual/12 + benefits_monthly)
        salary = salary_initial * (1 + salary_growth)**factor
        variable = (compute_initial*(1+compute_growth)**factor + api_initial*(1+api_growth)**factor)
        dev_cost = support_dev_initial*(1+support_growth)**factor * shared_data['dev_customers'][month]
        fin_cost = support_fin_initial*(1+support_growth)**factor * shared_data['fin_customers'][month]

        total = fixed + salary + variable + dev_cost + fin_cost

        monthly_fixed.append(fixed)
        monthly_variable.append(variable + dev_cost + fin_cost)
        dev_costs.append(dev_cost)
        fin_costs.append(fin_cost)
        salary_costs.append(salary)
        total_costs.append(total)

    # Plot total and breakdown
    cost_df = pd.DataFrame({
        'Total Cost': total_costs,
        'Fixed Cost': monthly_fixed,
        'Variable Cost': monthly_variable,
        'Dev Customer Cost': dev_costs,
        'Fin Customer Cost': fin_costs,
        'Salary Cost': salary_costs
    })

    st.line_chart(cost_df)
with earnings_tab:
   st.header('Earnings Dashboard')
   st.write("Earnings analysis will be implemented here.")

