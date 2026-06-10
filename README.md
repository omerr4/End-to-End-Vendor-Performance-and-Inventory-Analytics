# End-to-End Vendor Performance and Inventory Analytics

## Project Overview

This repository presents an end-to-end data analytics and data engineering pipeline developed to evaluate vendor performance and optimize inventory management within large-scale retail and wholesale environments.

The project processes millions of transactional records through a structured workflow that includes data ingestion, ETL operations, statistical analysis, predictive modeling, and business intelligence reporting. The objective is to identify inefficiencies in procurement and inventory strategies, improve profitability, reduce capital lock-up, and support data-driven supply chain decisions.

## Key Business Insights

### Bulk Purchasing Efficiency

Analysis confirmed that bulk procurement strategies substantially reduce unit purchase costs. Large-volume purchasing tiers achieved average unit costs of $10.77 compared to $39.05 for smaller purchasing tiers, representing a cost reduction of up to 72.4%.

### Capital Lock-up Identification

The analysis revealed $13,993,308.64 in capital tied up in low-turnover inventory (turnover rate below 1.0). A significant portion of this critical exposure was concentrated among the top 10 vendors, led by Diageo North America (~$1.9M) and Martignetti Companies (~$1.3M).

### High-Margin Opportunity Brands ("Hidden Gems")

A total of 233 brands were identified with profit margins exceeding 63.41% (top 15%) while maintaining sales below $562.67 (bottom 15%). These products represent potential growth opportunities through targeted marketing instead of price liquidation.

### Niche vs. High-Volume Vendor Performance

Hypothesis testing using an independent two-sample t-test (Welch's T-Test) indicated a statistically significant difference ($p < 0.05$) between vendor categories:

- Low-volume vendors average margin: 41.55% (Specialized / Premium Niche Products).
- High-volume vendors average margin: 31.17% (Volume-Driven Bulk Sales).

## Technology Stack

### Data Engineering

- Python
- SQLite
- SQLAlchemy
- SQL (CTEs, Advanced Joins)

### Data Analytics & Statistics

- Pandas
- NumPy
- SciPy (scipy.stats)

### Data Visualization

- Matplotlib
- Seaborn

### Predictive Modeling

- Scikit-Learn (Random Forest Regressor for Demand Forecasting)

## Core Pipeline Implementation Details

### 1. Memory-Efficient Ingestion (`data_ingestion.py`)

To process millions of rows without causing an out-of-memory error (RAM Crash), the pipeline utilizes chunked data loading to stream records into a local SQLite database.

```python
# Streaming chunk processing pattern
for chunk in pd.read_csv(csv_file_path, chunksize=100000, low_memory=False):
    if first_chunk:
        chunk.to_sql(table_name, con=engine, if_exists='replace', index=False)
        first_chunk = False
    else:
        chunk.to_sql(table_name, con=engine, if_exists='append', index=False)
```

### 2. Optimized SQL Feature Engineering (`etl_pipeline.py`)

Leverages Common Table Expressions (CTEs) natively inside the database layer to aggregate multi-table transactional streams (Sales, Purchases, Invoices) into a consolidated analytical master table (`vendor_sales_summary`) containing 10,692 unique records.

```sql
WITH Freight_Summary AS (
    SELECT VendorNumber, SUM(Freight) AS Total_Freight
    FROM vendor_invoice
    GROUP BY VendorNumber
),
Sales_Summary AS (
    SELECT
        VendorNo AS VendorNumber,
        Brand,
        SUM(SalesQuantity) AS Total_Sales_Quantity,
        SUM(SalesDollars) AS Total_Sales_Dollars
    FROM sales
    GROUP BY VendorNo, Brand
)
SELECT
    ps.VendorNumber,
    ps.VendorName,
    ps.Brand,
    ps.Actual_Price,
    ss.Total_Sales_Quantity,
    fs.Total_Freight
FROM Purchase_Summary ps
LEFT JOIN Sales_Summary ss
    ON ps.VendorNumber = ss.VendorNumber
   AND ps.Brand = ss.Brand
LEFT JOIN Freight_Summary fs
    ON ps.VendorNumber = fs.VendorNumber
```

## Project Structure

```plaintext
├── data/                      # Raw transactional CSV datasets (Sales, Purchases, Invoices)
├── logs/                      # Automated pipeline execution logs (data_ingestion.log, etl_pipeline.log)
├── data_ingestion.py          # Memory-efficient CSV-to-SQLite automated database loader
├── etl_pipeline.py            # Automated SQL CTEs feature engineering & KPI transformation engine
├── eda_notebook.ipynb         # Statistical EDA, Welch's T-Test, and Random Forest Forecasting
└── README.md                  # Project documentation
```

## Analytical Visualizations Included

*(Note: Visuals are generated and documented inside the `eda_notebook.ipynb`.)*

### Correlation Matrix Heatmap

Uncovers interactions between unit pricing, purchase volumes, and gross margins.

### Target Brands Scatter Plot

Isolates high-potential niche brands using adaptive statistical quantile thresholds.

### Pareto Chart Analysis

Visualizes supply chain vulnerability, showing that 66% of the procurement budget is concentrated among just 10 vendors.

### Confidence Interval Histogram

Illustrates the margin distribution variance between top and low-performing vendor bases.

### Feature Importance & Fit Plots

Details the Random Forest Regressor's accuracy in automated future inventory replenishment planning.
