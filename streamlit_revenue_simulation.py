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

# Sidebar placeholder
sidebar = st.sidebar

with revenue_tab:
    st.header('Revenue Dashboard')
    sidebar.header("Revenue Assumptions")

    months = sidebar.number_input('Projection Period (Months)', min_value=12, max_value=60, value=36)
    simulations = sidebar.number_input('Number of Simulations', min_value=100, max_value=1000, value=250)

    dev_base_fee = sidebar.number_input('Monthly Developer Base Fee ($)', value=5000)
    dev_seat_fee = sidebar.number_input('Monthly Fee per Additional Seat ($)', value=1000)
    avg_seats = sidebar.slider('Average Seats per Developer', 1, 10, 3)
    fin_project_fee = sidebar.number_input('Revenue per Financier Project ($)', value=10000)

    initial_dev = sidebar.number_input('Initial Developer Customers', min_value=0, max_value=20, value=2)
    initial_fin = sidebar.number_input('Initial Financier Customers', min_value=0, max_value=20, value=0)

    dev_growth_median = sidebar.slider('Median Developer Adds', 0.0, 3.0, .7)
    dev_growth_sigma = sidebar.slider('Developer Growth Volatility', 0.1, 2.0, 1.1)
    dev_growth_accel = sidebar.slider('Monthly Developer Growth Acceleration (%)', 0.0, 10.0, 5.0) / 100

    fin_growth_median = sidebar.slider('Median Financier Adds', 0.0, 5.0, .5)
    fin_growth_sigma = sidebar.slider('Financier Growth Volatility', 0.1, 2.0, 1.0)
    fin_growth_accel = sidebar.slider('Monthly Financier Growth Acceleration (%)', 0.0, 10.0, 2.0) / 100

    monthly_churn_median = sidebar.slider('Median Monthly Churn Rate (%)', 0.0, 10.0, 5.0) / 100
    monthly_churn_sigma = sidebar.slider('Churn Rate Volatility', 0.01, 2.0, 1.0)

    rev_results, dev_results, fin_results = [], [], []

    for _ in range(simulations):
        revenue, dev_customers, fin_customers = [], [], []
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

        rev_results.append(revenue)
        dev_results.append(dev_customers)
        fin_results.append(fin_customers)

    shared_data['dev_customers'] = np.array(dev_results)
    shared_data['fin_customers'] = np.array(fin_results)

with costs_tab:
    st.header('Costs Dashboard')
    sidebar.header("Cost Assumptions")

    hosting_initial = sidebar.number_input('Hosting Initial ($)', value=1500)
    hosting_growth = sidebar.slider('Hosting Growth Rate (%)', 0, 100, 50) / 100

    software_initial = sidebar.number_input('Software Subscriptions Initial ($)', value=4000)
    software_growth = sidebar.slider('Software Growth Rate (%)', 0, 100, 20) / 100

    admin_annual = sidebar.number_input('Admin & Legal Annual ($)', value=5000)
    conference_annual = sidebar.number_input('Conference Fees Annual ($)', value=15000)

    salary_initial = sidebar.number_input('Salaries Initial Monthly ($)', value=24000)
    salary_growth = sidebar.slider('Salary Growth Rate (%)', 0, 100, 100) / 100

    benefits_monthly = sidebar.number_input('Monthly Benefits ($)', value=2000)

    support_dev_initial = sidebar.number_input('Support Cost per Developer ($)', value=200)
    support_fin_initial = sidebar.number_input('Support Cost per Financier ($)', value=600)
    support_growth = sidebar.slider('Support Growth Rate (%)', 0, 100, 50) / 100

    monthly_total_costs = []
    for sim in range(simulations):
        monthly_total = []
        for month in range(months):
            factor = month // 12

            fixed = hosting_initial*(1+hosting_growth)**factor + software_initial*(1+software_growth)**factor + admin_annual/12 + conference_annual/12 + benefits_monthly
            salary = salary_initial * (1 + salary_growth)**factor

            dev_cost = support_dev_initial*(1+support_growth)**factor * shared_data['dev_customers'][sim, month]
            fin_cost = support_fin_initial*(1+support_growth)**factor * shared_data['fin_customers'][sim, month]

            monthly_total.append(fixed + salary + dev_cost + fin_cost)
        monthly_total_costs.append(monthly_total)

    cost_df = pd.DataFrame(monthly_total_costs).T
    st.line_chart(cost_df.quantile([0.1, 0.5, 0.9], axis=1).T)

with earnings_tab:
   st.header('Earnings Dashboard')
   st.write("Earnings analysis will be implemented here.")

