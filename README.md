# 🏢 Distill Financial Model

A comprehensive financial modeling dashboard built with Streamlit that uses Monte Carlo simulation to project revenue, costs, and earnings with uncertainty modeling.

## 📋 Features

### 🎲 Monte Carlo Simulation
- Probabilistic forecasting with confidence intervals
- Customizable simulation parameters (100-1000 runs)
- Projection periods from 12-72 months

### 📈 Revenue Modeling
- **Seat-based Revenue**: Monthly fees per customer seat
- **Usage-based Revenue**: Simulation-year computational usage with random variation
- **Customer Growth**: Configurable acquisition rates with acceleration
- **Churn Modeling**: Realistic customer loss simulation

### 💰 Cost Analysis
- **Headcount Simulation**: Dynamic team growth with slowdown above 15 people
- **Individual Cost Components**: 
  - Salary costs (per-person basis)
  - Hosting and infrastructure
  - Software subscriptions
  - Compute resources
  - Customer support
  - Admin & legal
  - Conference & events
  - Employee benefits

### 📊 Earnings & Analytics
- Break-even analysis
- Per-employee productivity metrics
- Cumulative earnings tracking
- Profit margin analysis
- Revenue mix breakdown

### 📋 Export & Analysis
- Excel export with detailed projections
- Comprehensive metrics dashboard
- Visual charts with percentile ranges

## 🏗️ Architecture

The application is organized into modular components for better maintainability:

```
distill-financial-model/
├── main.py                 # Main Streamlit application
├── src/
│   ├── __init__.py        # Package initialization
│   ├── config.py          # Configuration and constants
│   ├── models.py          # Core business logic and simulation
│   ├── ui_components.py   # Streamlit UI components
│   └── visualization.py   # Chart generation and plotting
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

### 🧩 Module Breakdown

- **`config.py`**: Default values, parameter ranges, and styling configuration
- **`models.py`**: Revenue and cost calculation models with Monte Carlo simulation
- **`ui_components.py`**: Streamlit interface elements and input controls
- **`visualization.py`**: Chart generation and metrics display functions
- **`main.py`**: Application orchestration and tab management

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip package manager

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/vanox-david/distill-financial-model.git
   cd distill-financial-model
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   streamlit run main.py
   ```

4. **Open in browser:**
   The app will automatically open at `http://localhost:8501`

## 🎛️ Usage

### 📊 Dashboard Navigation

The dashboard has three main tabs:

1. **📈 Revenue Tab**: Revenue projections and customer metrics
2. **💰 Costs Tab**: Cost breakdown and headcount analysis  
3. **💹 Earnings Tab**: Profitability analysis and per-employee metrics

### ⚙️ Configuration

Use the sidebar controls to adjust model parameters:

#### Simulation Parameters
- **Projection Period**: 12-72 months
- **Number of Simulations**: 100-1000 Monte Carlo runs

#### Revenue Parameters
- **Seat Fees**: Monthly recurring revenue per seat
- **Simulation Usage**: Computational usage revenue with volatility
- **Customer Growth**: Acquisition rates and acceleration
- **Churn Rates**: Customer loss modeling

#### Cost Parameters
- **Infrastructure**: Hosting, software, compute costs
- **Headcount**: Team growth simulation with realistic scaling
- **Fixed Costs**: Admin, legal, benefits, conferences
- **Variable Costs**: Customer support scaling

### 📈 Interpreting Results

Charts display three key lines:
- **Blue (Median)**: 50th percentile projection
- **Red (10th/90th)**: Confidence interval bounds

Key metrics include:
- Break-even timing
- Final month projections
- Per-employee efficiency ratios
- Cost composition analysis

## 🛠️ Development

### Code Structure

The codebase follows clean architecture principles:

- **Separation of Concerns**: UI, business logic, and visualization are separated
- **Type Hints**: Full type annotations for better code quality
- **Documentation**: Comprehensive docstrings and comments
- **Configuration**: Centralized default values and constants

### Adding New Features

1. **Models**: Add new calculation logic to `src/models.py`
2. **UI Controls**: Add input components to `src/ui_components.py`
3. **Visualizations**: Add charts to `src/visualization.py`
4. **Configuration**: Update defaults in `src/config.py`

### Running Tests

```bash
# Add test framework in future iterations
python -m pytest tests/
```

## 📋 Dependencies

- `streamlit`: Web application framework
- `numpy`: Numerical computing
- `pandas`: Data manipulation
- `plotly`: Interactive charts
- `xlsxwriter`: Excel export functionality

## 🔧 Configuration

Default parameters can be modified in `src/config.py`:

```python
# Example: Change default projection period
SIMULATION_CONFIG.months_default = 36

# Example: Modify default customer growth
REVENUE_CONFIG.customer_growth_median_default = 1.0
```

## 📊 Model Details

### Revenue Streams

1. **Seat-based Revenue**: `customers × seats × monthly_fee`
2. **Usage Revenue**: `sum(random_usage_per_customer) × price_per_unit`

### Cost Components

- **Fixed Costs**: Hosting, software, admin, benefits
- **Variable Costs**: Compute, customer support
- **Headcount Costs**: Salary scaling with team growth simulation

### Simulation Methodology

- **Lognormal Distributions**: For growth rates and usage patterns
- **Binomial Churn**: Realistic customer loss modeling
- **Growth Acceleration**: Increasing rates over time
- **Team Scaling**: Slower hiring above 15 people threshold

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For questions or support:
- Create an issue in the GitHub repository
- Review the code documentation
- Check the configuration options in `src/config.py`

## 🎯 Future Enhancements

- [ ] Scenario comparison tools
- [ ] Sensitivity analysis
- [ ] Database integration
- [ ] API endpoints
- [ ] Unit tests
- [ ] Docker deployment
- [ ] Real-time data integration 