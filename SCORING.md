# Scoring  (100 points + 10 bonus)

Use this to evaluate submissions consistently. Partial credit is allowed. Provide brief notes per section.

## 1) Database Setup & Modeling (15)
- Schema design reflects RAW/CURATED/MART separation (5)
- Appropriate keys, relationships, and data types (5)
- Snowflake features used appropriately (clustering, warehouses, context) (5)

## 2) ETL/ELT Pipeline (15)
- Clear orchestration/sequence RAW → CURATED → MART (5)
- Idempotent, modular SQL and/or Python steps (5)
- Handles edge cases and reruns safely (5)

## 3) Data Quality (10)
- Row counts, null checks, referential checks implemented (5)
- Actionable outcomes/logging and explanation of thresholds (5)

## 4) Analytical Models (15)
- Dimensions and facts correctly constructed from sources (5)
- Business-friendly views/materializations for analysis (5)
- Correctness validated against sample scenarios (5)

## 5) Metric Calculation (15)
- Revenue analytics: total/by product/by segment (5)
- Customer metrics: LTV, CAC, retention/churn, satisfaction (5)
- Order/product metrics: clear, consistent, and documented (5)

## 6) Dashboard & Visualization (15)
- Clean UI with filters (date, segment, category) and drill-down (5)
- Trend and comparative analysis implemented (5)
- Performance considerations (query efficiency, caching) (5)

## 7) Performance & Cost (10)
- Warehouse sizing, auto-suspend/resume, clustering strategy (5)
- Evidence of optimization choices or measurement (5)

## 8) Documentation (5)
- Readme, explanations, and data dictionary/assumptions (5)

## 9) Presentation of Insights (10)
- Clear narrative of findings and business implications (5)
- Visuals/tables support conclusions; limitations noted (5)

---

## Bonus: Extension – Predictive Analytics (+10)
- Formulates a predictive task (e.g., churn/CLV) and rationale (3)
- Builds baseline model or features using available data (4)
- Evaluation method and next steps articulated (3)

---

## Scoring Guidance
- Excellent: fully meets criteria; production-ready quality
- Good: minor gaps; meets intent
- Partial: some components present but incomplete or incorrect
- None: missing or not attempted

Provide overall comments and suggested improvements with priority ordering.
