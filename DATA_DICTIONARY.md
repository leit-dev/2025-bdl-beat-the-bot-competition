# Data Dictionary

This document describes the datasets created for the Online Retail competition in Snowflake. Objects are organized by layer: RAW (source/landing), CURATED (modeled), and MART (presentation/analytics).

## RAW Schema

### CUSTOMERS
- `CUSTOMER_ID` (NUMBER, IDENTITY): Surrogate key.
- `CUSTOMER_EXTERNAL_KEY` (STRING): Source system customer identifier.
- `FIRST_NAME` (STRING), `LAST_NAME` (STRING): Customer names.
- `EMAIL` (STRING): Email address.
- `PHONE` (STRING): Phone number.
- `GENDER` (STRING): Gender.
- `BIRTH_DATE` (DATE): Date of birth.
- `ADDRESS_LINE1` (STRING), `ADDRESS_LINE2` (STRING): Street address.
- `CITY` (STRING), `STATE` (STRING), `POSTAL_CODE` (STRING), `COUNTRY` (STRING): Location.
- `SEGMENT` (STRING): Customer segment (Consumer/SMB/Enterprise).
- `CREATED_AT` (TIMESTAMP_NTZ): Record creation time.
- `UPDATED_AT` (TIMESTAMP_NTZ): Last update time.

### PRODUCTS
- `PRODUCT_ID` (NUMBER, IDENTITY): Surrogate key.
- `SKU` (STRING): Stock keeping unit.
- `PRODUCT_NAME` (STRING): Name.
- `CATEGORY` (STRING), `SUBCATEGORY` (STRING): Product classification.
- `BRAND` (STRING): Brand.
- `UNIT_PRICE` (NUMBER(10,2)): Current list price.
- `COST_PRICE` (NUMBER(10,2)): Unit cost.
- `ACTIVE_FLAG` (BOOLEAN): Availability flag.
- `CREATED_AT`, `UPDATED_AT` (TIMESTAMP_NTZ): Audit timestamps.

### SUPPLIERS
- `SUPPLIER_ID` (NUMBER, IDENTITY): Surrogate key.
- `SUPPLIER_NAME` (STRING): Supplier name.
- `CONTACT_NAME`, `CONTACT_EMAIL`, `CONTACT_PHONE` (STRING): Contact info.
- `COUNTRY` (STRING): Country.
- `RATING` (NUMBER(3,2)): Internal supplier rating (0–5).
- `CREATED_AT`, `UPDATED_AT` (TIMESTAMP_NTZ): Audit timestamps.

### EMPLOYEES
- `EMPLOYEE_ID` (NUMBER, IDENTITY): Surrogate key.
- `FIRST_NAME`, `LAST_NAME`, `EMAIL` (STRING): Identity.
- `TITLE` (STRING), `DEPARTMENT` (STRING): Role info.
- `HIRE_DATE` (DATE): Hire date.
- `MANAGER_ID` (NUMBER): Manager (employee) id; may be null.
- `STATUS` (STRING): Employment status.
- `CREATED_AT`, `UPDATED_AT` (TIMESTAMP_NTZ): Audit timestamps.

### ORDERS (CLUSTER BY ORDER_DATE, CUSTOMER_ID)
- `ORDER_ID` (NUMBER, IDENTITY): Surrogate key.
- `ORDER_EXTERNAL_KEY` (STRING): Source order id.
- `CUSTOMER_ID` (NUMBER): FK → `CUSTOMERS.CUSTOMER_ID`.
- `ORDER_DATE` (TIMESTAMP_NTZ): Order timestamp.
- `ORDER_STATUS` (STRING): Created/Paid/Shipped/Delivered/Cancelled/Returned.
- `CHANNEL` (STRING): Web/Mobile/Support.
- `PAYMENT_METHOD` (STRING): Card/PayPal/COD.
- `SHIPPING_ADDRESS`, `SHIPPING_CITY`, `SHIPPING_STATE`, `SHIPPING_POSTAL_CODE`, `SHIPPING_COUNTRY` (STRING): Shipping location.
- `EMPLOYEE_ID` (NUMBER): FK → `EMPLOYEES.EMPLOYEE_ID` (when assisted sale).
- `CREATED_AT`, `UPDATED_AT` (TIMESTAMP_NTZ): Audit timestamps.

### ORDER_ITEMS (CLUSTER BY ORDER_ID, PRODUCT_ID)
- `ORDER_ITEM_ID` (NUMBER, IDENTITY): Surrogate key.
- `ORDER_ID` (NUMBER): FK → `ORDERS.ORDER_ID`.
- `PRODUCT_ID` (NUMBER): FK → `PRODUCTS.PRODUCT_ID`.
- `QUANTITY` (NUMBER): Units purchased.
- `UNIT_PRICE_AT_ORDER` (NUMBER(10,2)): Price at order time.
- `DISCOUNT_AMOUNT` (NUMBER(10,2)): Absolute discount at line level.
- `CREATED_AT`, `UPDATED_AT` (TIMESTAMP_NTZ): Audit timestamps.

### CUSTOMER_INTERACTIONS (CLUSTER BY INTERACTION_TS, CUSTOMER_ID)
- `INTERACTION_ID` (NUMBER, IDENTITY): Surrogate key.
- `CUSTOMER_ID` (NUMBER): Related customer; may be null for anonymous.
- `INTERACTION_TS` (TIMESTAMP_NTZ): Event timestamp.
- `CHANNEL` (STRING): Web/Mobile/Support.
- `EVENT_TYPE` (STRING): PageView/AddToCart/Checkout/Ticket/Rating.
- `EVENT_PROPERTIES` (VARIANT): JSON payload (e.g., `{ "path": "/home" }`, `{ "score": 5 }`).
- `SESSION_ID` (STRING): Session identifier.
- `CAMPAIGN_ID` (NUMBER): Optional link to marketing campaign.

### MARKETING_CAMPAIGNS
- `CAMPAIGN_ID` (NUMBER, IDENTITY): Surrogate key.
- `CAMPAIGN_NAME` (STRING): Campaign name.
- `CHANNEL` (STRING): Channel (Web/Email/… ).
- `START_DATE`, `END_DATE` (DATE): Campaign window.
- `BUDGET` (NUMBER(12,2)): Planned spend.
- `TARGET_SEGMENT` (STRING): Intended audience segment.
- `CREATED_AT`, `UPDATED_AT` (TIMESTAMP_NTZ): Audit timestamps.

---

## CURATED Schema

### DIM_CUSTOMER
Conformed customer dimension derived from RAW.
- `CUSTOMER_ID`, `CUSTOMER_EXTERNAL_KEY`, `FIRST_NAME`, `LAST_NAME`, `EMAIL`, `GENDER`, `BIRTH_DATE`, `CITY`, `STATE`, `COUNTRY`, `SEGMENT`, `CREATED_AT`, `UPDATED_AT`.

### DIM_PRODUCT
Conformed product dimension derived from RAW.
- `PRODUCT_ID`, `SKU`, `PRODUCT_NAME`, `CATEGORY`, `SUBCATEGORY`, `BRAND`, `UNIT_PRICE`, `COST_PRICE`, `ACTIVE_FLAG`.

### DIM_DATE
Calendar date dimension.
- `DATE_KEY` (DATE), `YEAR` (NUMBER), `MONTH` (NUMBER), `DAY` (NUMBER), `DOW_SHORT` (STRING), `MONTH_SHORT` (STRING).

### FACT_SALES
Order line-level facts filtered to Paid/Shipped/Delivered orders.
- `ORDER_ITEM_ID` (NUMBER): Line surrogate key.
- `ORDER_ID` (NUMBER): Order identifier.
- `ORDER_DATE` (DATE): Order date.
- `CUSTOMER_ID` (NUMBER): Buyer.
- `PRODUCT_ID` (NUMBER): Product sold.
- `QUANTITY` (NUMBER): Units.
- `UNIT_PRICE_AT_ORDER` (NUMBER(10,2)): Line unit price at purchase.
- `DISCOUNT_AMOUNT` (NUMBER(10,2)): Line discount.
- `GROSS_REVENUE` (NUMBER(12,2)): `QUANTITY * UNIT_PRICE_AT_ORDER - DISCOUNT_AMOUNT`.
- `COST_OF_GOODS` (NUMBER(12,2)): `QUANTITY * COST_PRICE` from product.
- `PROFIT` (NUMBER(12,2)): `GROSS_REVENUE - COST_OF_GOODS`.
- `CHANNEL` (STRING): Sales channel.
- `ORDER_STATUS` (STRING): Order status.

### FACT_INTERACTIONS
Customer interaction events.
- `INTERACTION_ID`, `CUSTOMER_ID`, `INTERACTION_DATE` (DATE), `CHANNEL`, `EVENT_TYPE`, `EVENT_PROPERTIES` (VARIANT), `CAMPAIGN_ID`.

---

## MART Schema (Views)

### V_REVENUE_DAILY
- `DATE` (DATE): Order date.
- `TOTAL_REVENUE` (NUMBER): Sum of `GROSS_REVENUE`.
- `TOTAL_PROFIT` (NUMBER): Sum of `PROFIT`.

### V_REVENUE_BY_PRODUCT
- `CATEGORY`, `SUBCATEGORY`, `PRODUCT_NAME` (STRING): Product attributes.
- `REVENUE` (NUMBER): Revenue by product.
- `PROFIT` (NUMBER): Profit by product.
- `UNITS` (NUMBER): Units sold.

### V_REVENUE_BY_SEGMENT
- `SEGMENT` (STRING): Customer segment.
- `REVENUE` (NUMBER): Revenue by segment.
- `PROFIT` (NUMBER): Profit by segment.

### V_CUSTOMER_LTV
- `CUSTOMER_ID`, `FIRST_NAME`, `LAST_NAME`, `SEGMENT`: Customer attributes.
- `REALIZED_LTV` (NUMBER): Sum of realized profit per customer (proxy for LTV).

### V_CAMPAIGN_CAC
- `CAMPAIGN_ID`, `CAMPAIGN_NAME`, `CHANNEL`, `BUDGET`.
- `DISTINCT_CUSTOMERS` (NUMBER): Distinct customers with interactions.
- `CAC` (NUMBER): `BUDGET / DISTINCT_CUSTOMERS` (null when denominator is 0).

### V_RETENTION_RATE
- `RETENTION_RATE` (NUMBER [0–1]): Fraction of customers with 2+ orders.

### V_CHURN_RATE
- `CHURN_RATE` (NUMBER [0–1]): `1 - RETENTION_RATE`.

### V_CUSTOMER_SATISFACTION
- `AVG_RATING` (NUMBER): Average rating from `EVENT_PROPERTIES:score` (0–5) for `EVENT_TYPE = 'Rating'`.

### V_ORDER_SUMMARY
- `ORDER_ID` (NUMBER), `ORDER_DATE` (DATE), `CHANNEL` (STRING), `ORDER_STATUS` (STRING).
- `TOTAL_ITEMS` (NUMBER): Items per order.
- `ORDER_REVENUE` (NUMBER): Revenue per order.
- `ORDER_PROFIT` (NUMBER): Profit per order.

---

## Notes & Assumptions
- Constraints in RAW are primarily informational in Snowflake; referential integrity should be validated via DQ checks.
- Prices and costs are simplified; taxes, shipping, returns, and refunds are not modeled in detail.
- Supplier-to-product mapping is not included; `V_SUPPLIER_PERFORMANCE` uses a placeholder join and should be replaced if a mapping table is added.
