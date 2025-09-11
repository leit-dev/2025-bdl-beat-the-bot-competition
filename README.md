# Beat the Bot: Online Retail Data Engineering Competition

This repository contains an end-to-end Snowflake-based data engineering competition for an online retail company. Participants will build data pipelines, analytical models, and a dashboard to deliver business insights.

## Contents
- `00_Setup.sql`: Snowflake database/schema creation, RAW tables with sample data, CURATED models, MART views.
- `01_DataEngineeringPipeline.ipynb`: End-to-end pipeline notebook with connection, extraction, DQ checks, transformations, and metrics.
- `02_Dashboard.py`: Streamlit dashboard connecting to Snowflake with filters, trends, and KPIs.
- `SCORING.md`: Detailed rubric and point allocations.

## Prerequisites
- Snowflake account with permissions to create database/warehouse/schema. A Snowflake Trail account can be easily created at https://signup.snowflake.com/
- Python 3.9+ with `pip`.
- Optional: `venv` for isolation.

## Quick Start
1) Run setup in Snowflake
- Open `00_Setup.sql` in Snowflake Worksheets and run it.
- This creates database `RETAIL_COMPETITION`, schemas (`RAW`, `CURATED`, `MART`), loads sample data, and materializes curated/mart objects.

2) Configure local environment
Set Snowflake credentials as environment variables:

```bash
export SNOWFLAKE_USER=your_user
export SNOWFLAKE_PASSWORD=your_password
export SNOWFLAKE_ACCOUNT=your_account
export SNOWFLAKE_WAREHOUSE=WH_RETAIL_COMPETITION
export SNOWFLAKE_DATABASE=RETAIL_COMPETITION
export SNOWFLAKE_SCHEMA=MART
 export SNOWFLAKE_ROLE=YOUR_ROLE   # optional
```

3) Install dependencies
```bash
python -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install streamlit snowflake-connector-python pandas numpy dotenv
```

4) Run the pipeline notebook
- Open `01_DataEngineeringPipeline.ipynb` in VS Code/Jupyter and run all cells.

5) Launch the dashboard
```bash
streamlit run 02_Dashboard.py
```

## Competition Structure (Suggested)
1. Database setup and data modeling (DDL design, constraints, Snowflake features)
2. ETL/ELT pipeline development (RAW → CURATED → MART)
3. Data quality implementation (tests, assertions, monitoring)
4. Analytical model creation (dimensions, facts)
5. Metric calculation (revenue, LTV, CAC, retention/churn, satisfaction, product/order analytics)
6. Dashboard development (filters, drill-down, trend and comparative analysis)
7. Performance optimization (clustering, caching, warehouse sizing, materialized views)
8. Documentation (README, data dictionary, decisions)
9. Presentation of insights (executive summary, key findings)
10. Extension challenge: predictive analytics (CLV/churn propensity, campaign optimization)

## Sample Business Questions
- Which product categories drive the most revenue and margin?
- Which customer segments are most valuable (LTV) and what is their retention?
- What campaigns have the best CAC and ROI?
- Are there notable trends by channel or geography?

## Notes
- Provided data is small for demo. Teams may extend with synthetic data generators to stress-test.
- Replace placeholder supplier-product mapping with a true mapping table if needed.

## Support
Open issues or propose enhancements via pull requests.
