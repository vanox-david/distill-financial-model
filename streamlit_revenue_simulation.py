# streamlit_revenue_simulation.py
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import io

st.title('Distill Probabilistic Revenue Model')

st.sidebar.header("Set Your Assumptions")

months = st.sidebar.number_input('Projection Period (Months)', min_value=12, max_value=120, value=36)
simulations = st.sidebar.number_input('Number of Simulations', min_value=100, max_value=10000, value=1000)

dev_base_fee = st.sidebar.number_input('Monthly Developer Base Fee ($)', value=5000)
dev_seat_fee = st.sidebar.number_input('Monthly Fee per Additional Seat ($)', value=1000)
avg_seats = st.sidebar.slider('Average Seats per Developer', 1, 10, 3)
fin_project_fee = st.sidebar.number_input('Revenue per Financier Project ($)', value=10000)

initial_dev = st.sidebar.number_input('Initial Developer Customers', min_value=0, max_value=20, value=3)
initial_fin = st.sidebar.number_input('Initial Financier Customers', min_value=0, max_value=20, value=2)

dev_growth_median = st.sidebar.slider('Median Developer Adds', 0.0, 5.0, 2.0)
dev_growth_sigma = st.sidebar.slider('Developer Growth Volatility', 0.1, 2.0, 0.5)
dev_growth_accel = st.sidebar.slider('Monthly Developer Growth Acceleration (%)', 0.0, 10.0, 1.0) / 100

fin_growth_median = st.sidebar.slider('Median Financier Adds', 0.0, 5.0, 1.5)
fin_growth_sigma = st.sidebar.slider('Financier Growth Volatility', 0.1, 2.0, 0.5)
fin_growth_accel = st.sidebar.slider('Monthly Financier Growth Acceleration (%)', 0.0, 10.0, 1.0) / 100

monthly_churn_median = st.sidebar.slider('Median Monthly Churn Rate (%)', 0.0, 5.0, 1.0) / 100
monthly_churn_sigma = st.sidebar.slider('Churn Rate Volatility', 0.01, 1.0, 0.2)

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

def plot_metric(p10, median, p90, title, yaxis):
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=median, mode='lines', name='Median', line=dict(color='blue', width=3)))
    fig.add_trace(go.Scatter(y=p10, mode='lines', name='10th Percentile', line=dict(color='red', width=3)))
    fig.add_trace(go.Scatter(y=p90, mode='lines', name='90th Percentile', line=dict(color='red', width=3, dash='dash')))
    fig.update_layout(title=title, xaxis_title='Month', yaxis_title=yaxis)
    st.plotly_chart(fig)

fig = go.Figure()
for sim in rev_results:
    fig.add_trace(go.Scatter(y=sim, mode='lines', line=dict(color='lightgrey'), opacity=0.1, showlegend=False))
fig.add_trace(go.Scatter(y=rev_med, mode='lines', name='Median', line=dict(color='blue', width=3)))
fig.add_trace(go.Scatter(y=rev_p10, mode='lines', name='10th Percentile', line=dict(color='red', width=3)))
fig.add_trace(go.Scatter(y=rev_p90, mode='lines', name='90th Percentile', line=dict(color='red', width=3, dash='dash')))
fig.update_layout(title='Monthly Revenue Projection', xaxis_title='Month', yaxis_title='Revenue ($)')
st.plotly_chart(fig)

plot_metric(dev_p10, dev_med, dev_p90, 'Total Developer Customers', 'Developers')
plot_metric(fin_p10, fin_med, fin_p90, 'Total Financier Customers', 'Financiers')
plot_metric(churn_p10, churn_med, churn_p90, 'Total Monthly Churn', 'Customers Lost')