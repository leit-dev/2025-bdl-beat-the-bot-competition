import os
import streamlit as st
import pandas as pd
import snowflake.connector
from datetime import date

# Load .env if available (optional)
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

REQUIRED_ENV_VARS = ['SNOWFLAKE_USER', 'SNOWFLAKE_PASSWORD', 'SNOWFLAKE_ACCOUNT']


def _read_config():
    missing = [k for k in REQUIRED_ENV_VARS if not os.getenv(k)]
    if missing:
        st.error(
            "Missing required environment variables: " + ", ".join(missing) +
            "\nSet them in your environment or a .env file. See .env_template for reference."
        )
        st.stop()
    return {
        'user': os.getenv('SNOWFLAKE_USER'),
        'password': os.getenv('SNOWFLAKE_PASSWORD'),
        'account': os.getenv('SNOWFLAKE_ACCOUNT'),
        'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE', 'WH_RETAIL_COMPETITION'),
        'database': os.getenv('SNOWFLAKE_DATABASE', 'RETAIL_COMPETITION'),
        'schema': os.getenv('SNOWFLAKE_SCHEMA', 'MART'),
        'role': os.getenv('SNOWFLAKE_ROLE')
    }


# Connection helper
@st.cache_resource
def get_connection():
    cfg = _read_config()
    try:
        con = snowflake.connector.connect(
            user=cfg['user'],
            password=cfg['password'],
            account=cfg['account'],
            warehouse=cfg['warehouse'],
            database=cfg['database'],
            schema=cfg['schema'],
            role=cfg['role']
        )
        # Ensure context explicitly
        cur = con.cursor()
        try:
            if cfg['database']:
                cur.execute(f"USE DATABASE {cfg['database']}")
            if cfg['schema']:
                cur.execute(f"USE SCHEMA {cfg['schema']}")
            if cfg['warehouse']:
                cur.execute(f"USE WAREHOUSE {cfg['warehouse']}")
        finally:
            try:
                cur.close()
            except Exception:
                pass
        return con
    except Exception as e:
        st.error(f"Failed to connect to Snowflake: {e}\nCheck your SNOWFLAKE_* environment variables and network access.")
        st.stop()


@st.cache_data(show_spinner=False)
def run_query(sql, params=None):
    con = get_connection()
    try:
        cur = con.cursor()
        cur.execute(sql, params or {})
        columns = [c[0] for c in cur.description]
        rows = cur.fetchall()
        return pd.DataFrame(rows, columns=columns)
    finally:
        try:
            cur.close()
        except Exception:
            pass

st.set_page_config(page_title='Retail Analytics', layout='wide')

st.title('Retail Analytics Dashboard')

# Filters
with st.sidebar:
    st.header('Filters')
    date_range = st.date_input('Date range', value=(date(2024, 3, 1), date(2024, 6, 30)))
    segment = st.selectbox('Customer segment', options=['All','Consumer','SMB','Enterprise'], index=0)
    category = st.selectbox('Product category', options=['All','Electronics','Apparel','Home'], index=0)

start_date, end_date = date_range if isinstance(date_range, tuple) else (date_range, date_range)

# Build filter predicates
where_clauses = ["1=1"]
params = {}
if start_date:
    where_clauses.append("DATE >= %(start_date)s")
    params['start_date'] = start_date
if end_date:
    where_clauses.append("DATE <= %(end_date)s")
    params['end_date'] = end_date

segment_clause = ""
if segment != 'All':
    segment_clause = "AND SEGMENT = %(segment)s"
    params['segment'] = segment

category_clause = ""
if category != 'All':
    category_clause = "AND CATEGORY = %(category)s"
    params['category'] = category

# KPI tiles
kpi_cols = st.columns(4)

rev_df = run_query(f"""
    SELECT SUM(TOTAL_REVENUE) AS TOTAL_REVENUE, SUM(TOTAL_PROFIT) AS TOTAL_PROFIT
    FROM MART.V_REVENUE_DAILY
    WHERE {' AND '.join(where_clauses)}
""", params)

seg_df = run_query(f"""
    SELECT SEGMENT, SUM(REVENUE) AS REV
    FROM (
      SELECT c.SEGMENT, f.GROSS_REVENUE AS REVENUE, f.ORDER_DATE AS DATE
      FROM CURATED.FACT_SALES f
      JOIN CURATED.DIM_CUSTOMER c USING (CUSTOMER_ID)
    )
    WHERE {' AND '.join(where_clauses)} {segment_clause}
    GROUP BY 1
    ORDER BY REV DESC
""", params)

with kpi_cols[0]:
    st.metric('Total Revenue', f"${rev_df['TOTAL_REVENUE'].iloc[0]:,.2f}" if not rev_df.empty else "$0.00")
with kpi_cols[1]:
    st.metric('Total Profit', f"${rev_df['TOTAL_PROFIT'].iloc[0]:,.2f}" if not rev_df.empty else "$0.00")
with kpi_cols[2]:
    st.metric('Top Segment', seg_df.iloc[0]['SEGMENT'] if not seg_df.empty else '—')
with kpi_cols[3]:
    st.metric('Segments', len(seg_df) if not seg_df.empty else 0)

# Revenue trend
trend_df = run_query(f"""
    SELECT DATE, TOTAL_REVENUE, TOTAL_PROFIT
    FROM MART.V_REVENUE_DAILY
    WHERE {' AND '.join(where_clauses)}
    ORDER BY DATE
""", params)

st.subheader('Revenue Trend')
if trend_df.empty:
    st.info('No data for selected filters.')
else:
    st.line_chart(trend_df.set_index('DATE')[['TOTAL_REVENUE','TOTAL_PROFIT']])

# Revenue by product/category with filters
prod_df = run_query(f"""
    SELECT CATEGORY, SUBCATEGORY, PRODUCT_NAME, REVENUE, PROFIT, UNITS
    FROM MART.V_REVENUE_BY_PRODUCT
    WHERE 1=1 {category_clause}
    ORDER BY REVENUE DESC
""", params)

st.subheader('Revenue by Product')
st.dataframe(prod_df, use_container_width=True)

# Revenue by segment
seg_breakdown = run_query(f"""
    SELECT SEGMENT, REVENUE, PROFIT
    FROM MART.V_REVENUE_BY_SEGMENT
    WHERE 1=1 {segment_clause}
    ORDER BY REVENUE DESC
""", params)

left, right = st.columns(2)
with left:
    st.subheader('Revenue by Segment')
    if seg_breakdown.empty:
        st.info('No data.')
    else:
        st.bar_chart(seg_breakdown.set_index('SEGMENT')['REVENUE'])
with right:
    st.subheader('Profit by Segment')
    if seg_breakdown.empty:
        st.info('No data.')
    else:
        st.bar_chart(seg_breakdown.set_index('SEGMENT')['PROFIT'])

# Customer KPIs
ltv_df = run_query("SELECT * FROM MART.V_CUSTOMER_LTV ORDER BY REALIZED_LTV DESC LIMIT 20")
ret_df = run_query("SELECT * FROM MART.V_RETENTION_RATE")
churn_df = run_query("SELECT * FROM MART.V_CHURN_RATE")
sat_df = run_query("SELECT * FROM MART.V_CUSTOMER_SATISFACTION")

st.subheader('Customer Metrics')
cols = st.columns(3)
with cols[0]:
    st.metric('Retention Rate', f"{ret_df.iloc[0,0]*100:.1f}%" if not ret_df.empty and pd.notnull(ret_df.iloc[0,0]) else '—')
with cols[1]:
    st.metric('Churn Rate', f"{churn_df.iloc[0,0]*100:.1f}%" if not churn_df.empty and pd.notnull(churn_df.iloc[0,0]) else '—')
with cols[2]:
    st.metric('Avg Satisfaction', f"{sat_df.iloc[0,0]:.2f}" if not sat_df.empty and pd.notnull(sat_df.iloc[0,0]) else '—')

st.write('Top Customers by Realized LTV')
st.dataframe(ltv_df, use_container_width=True)

# Orders summary (drill-down)
order_df = run_query("""
    SELECT * FROM MART.V_ORDER_SUMMARY ORDER BY ORDER_DATE DESC
""")

st.subheader('Orders Summary')
st.dataframe(order_df, use_container_width=True)

st.caption('Tip: Use .env (see .env_template) or export SNOWFLAKE_USER, SNOWFLAKE_PASSWORD, SNOWFLAKE_ACCOUNT, SNOWFLAKE_WAREHOUSE, SNOWFLAKE_DATABASE, SNOWFLAKE_SCHEMA, SNOWFLAKE_ROLE.')
