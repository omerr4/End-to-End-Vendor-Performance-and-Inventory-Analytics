"""
ETL Pipeline & Feature Engineering Module
-----------------------------------------
This script extracts aggregated data from multiple SQLite tables using optimized SQL queries (CTEs).
It performs data cleaning, engineers business KPIs (Gross Profit, Margins, Stock Turnover), 
and loads the final master table back into the database for downstream visualization.
"""

import sqlite3
import pandas as pd
import numpy as np
import logging
import time

logging.basicConfig(
    filename='logs/etl_pipeline.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def extract_vendor_summary(conn):
    """
    Executes an optimized SQL query using Common Table Expressions (CTEs) 
    to aggregate sales, purchases, and freight data efficiently.
    """
    query = """
    WITH Freight_Summary AS (
        SELECT VendorNumber, SUM(Freight) AS Total_Freight
        FROM vendor_invoice GROUP BY VendorNumber
    ),
    Sales_Summary AS (
        SELECT VendorNo AS VendorNumber, Brand,
               SUM(SalesQuantity) AS Total_Sales_Quantity,
               SUM(SalesDollars) AS Total_Sales_Dollars,
               SUM(SalesPrice) AS Total_Sales_Price
        FROM sales GROUP BY VendorNo, Brand
    ),
    Purchase_Summary AS (
        SELECT p.VendorNumber, p.VendorName, p.Brand,
               pp.Price AS Actual_Price, pp.PurchasePrice,
               SUM(p.Quantity) AS Total_Purchase_Quantity,
               SUM(p.Dollars) AS Total_Purchase_Dollars
        FROM purchases p
        LEFT JOIN purchase_prices pp ON p.Brand = pp.Brand
        WHERE p.PurchasePrice > 0
        GROUP BY p.VendorNumber, p.VendorName, p.Brand, pp.Price, pp.PurchasePrice
    )
    SELECT ps.VendorNumber, ps.VendorName, ps.Brand, ps.Actual_Price, ps.PurchasePrice,
           ps.Total_Purchase_Quantity, ps.Total_Purchase_Dollars,
           ss.Total_Sales_Quantity, ss.Total_Sales_Dollars, ss.Total_Sales_Price,
           fs.Total_Freight
    FROM Purchase_Summary ps
    LEFT JOIN Sales_Summary ss ON ps.VendorNumber = ss.VendorNumber AND ps.Brand = ss.Brand
    LEFT JOIN Freight_Summary fs ON ps.VendorNumber = fs.VendorNumber
    """
    return pd.read_sql(query, conn)

def transform_data(df):
    """
    Cleans the aggregated dataframe and engineers new KPIs.
    """
    # Data Cleaning
    df.fillna(0, inplace=True)
    df['VendorName'] = df['VendorName'].str.strip()
    
    # Feature Engineering (KPIs)
    df['Gross_Profit'] = df['Total_Sales_Dollars'] - df['Total_Purchase_Dollars']
    
    df['Profit_Margin_%'] = np.where(
        df['Total_Sales_Dollars'] > 0, 
        (df['Gross_Profit'] / df['Total_Sales_Dollars']) * 100, 0
    )
    
    df['Stock_Turnover'] = np.where(
        df['Total_Purchase_Quantity'] > 0,
        df['Total_Sales_Quantity'] / df['Total_Purchase_Quantity'], 0
    )
    
    return df

def run_pipeline(db_name='inventory.db'):
    """Main execution function for the ETL pipeline."""
    start_time = time.time()
    conn = sqlite3.connect(db_name)
    
    try:
        logging.info("Starting data extraction...")
        raw_summary_df = extract_vendor_summary(conn)
        
        logging.info("Starting data transformation and feature engineering...")
        clean_summary_df = transform_data(raw_summary_df)
        
        logging.info("Loading final data into the database...")
        clean_summary_df.to_sql('vendor_sales_summary', con=conn, if_exists='replace', index=False)
        print("ETL Pipeline executed successfully! Final table 'vendor_sales_summary' created.")
        
    except Exception as e:
        logging.error(f"Pipeline failed: {e}")
        print(f"Error: {e}")
    finally:
        conn.close()
        
    logging.info(f"Pipeline execution time: {time.time() - start_time:.2f} seconds.")

if __name__ == '__main__':
    run_pipeline()