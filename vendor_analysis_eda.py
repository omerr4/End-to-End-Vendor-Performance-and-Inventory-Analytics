# %% [markdown]
# # Vendor Performance & Profitability Analysis (EDA)
# This notebook analyzes vendor performance, uncovers hidden profit opportunities, 
# and evaluates the efficiency of bulk purchasing and inventory turnover.

# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
import scipy.stats as stats
import warnings
from matplotlib.ticker import PercentFormatter

warnings.filterwarnings('ignore')

# Load the transformed data from the database
conn = sqlite3.connect('inventory.db')
query = """
    SELECT * FROM vendor_sales_summary 
    WHERE Total_Sales_Quantity > 0 
      AND Gross_Profit > 0 
      AND "Profit_Margin_%" > 0
"""
df = pd.read_sql(query, conn)
print(f"Data loaded successfully. Shape: {df.shape}")

# %% [markdown]
# ## 1. Correlation Analysis
# Identifying relationships between numerical variables such as pricing, sales volume, and margins.

# %%
plt.figure(figsize=(10, 8))
numerical_cols = ['Actual_Price', 'Total_Purchase_Quantity', 'Total_Sales_Dollars', 
                  'Gross_Profit', 'Profit_Margin_%', 'Stock_Turnover']

sns.heatmap(df[numerical_cols].corr(), annot=True, cmap='coolwarm', fmt=".2f")
plt.title('Correlation Matrix of Key Metrics', fontsize=14)
plt.tight_layout()
plt.show()

# %% [markdown]
# ## 2. Identifying Target Brands (Promotional Adjustments)
# Discovering "Hidden Gems": Brands with low sales volume but exceptionally high profit margins.

# %%
brand_perf = df.groupby('Brand').agg(
    Total_Sales=('Total_Sales_Dollars', 'sum'),
    Profit_Margin=('Profit_Margin_%', 'mean')
).reset_index()

low_sales_threshold = brand_perf['Total_Sales'].quantile(0.15)
high_margin_threshold = brand_perf['Profit_Margin'].quantile(0.85)

target_brands = brand_perf[(brand_perf['Total_Sales'] < low_sales_threshold) & 
                           (brand_perf['Profit_Margin'] > high_margin_threshold)]

plt.figure(figsize=(10, 6))
sns.scatterplot(data=brand_perf[brand_perf['Total_Sales'] < 10000], x='Total_Sales', y='Profit_Margin', color='blue', alpha=0.3, label='Standard Brands')
sns.scatterplot(data=target_brands, x='Total_Sales', y='Profit_Margin', color='red', s=100, label='Target Brands (High Potential)')
plt.axvline(low_sales_threshold, color='green', linestyle='--')
plt.axhline(high_margin_threshold, color='purple', linestyle='--')
plt.title('Target Brands for Promotional Strategies')
plt.xlabel('Total Sales ($)')
plt.ylabel('Profit Margin (%)')
plt.legend()
plt.show()

# %% [markdown]
# ## 3. Vendor Dependency (Pareto Analysis)
# Assessing procurement risks by analyzing vendor contribution using the 80/20 rule.

# %%
vendor_perf = df.groupby('VendorName')['Total_Purchase_Dollars'].sum().reset_index()
vendor_perf['Contribution_%'] = (vendor_perf['Total_Purchase_Dollars'] / vendor_perf['Total_Purchase_Dollars'].sum()) * 100
top_vendors = vendor_perf.sort_values('Contribution_%', ascending=False).head(10)
top_vendors['Cumulative_%'] = top_vendors['Contribution_%'].cumsum()

fig, ax1 = plt.subplots(figsize=(12, 6))
ax1.bar(top_vendors['VendorName'], top_vendors['Contribution_%'], color='tab:blue')
ax1.set_ylabel('Contribution %', color='tab:blue')
ax1.set_xticklabels(top_vendors['VendorName'], rotation=45, ha='right')

ax2 = ax1.twinx()
ax2.plot(top_vendors['VendorName'], top_vendors['Cumulative_%'], color='tab:red', marker='D')
ax2.set_ylabel('Cumulative %', color='tab:red')
ax2.yaxis.set_major_formatter(PercentFormatter())

plt.title('Pareto Chart: Top 10 Vendors Purchase Contribution')
plt.tight_layout()
plt.show()

# %% [markdown]
# ## 4. Hypothesis Testing
# Testing if there is a statistically significant difference in profit margins between Top and Low performing vendors.

# %%
top_threshold = df['Total_Sales_Dollars'].quantile(0.75)
low_threshold = df['Total_Sales_Dollars'].quantile(0.25)

top_margins = df[df['Total_Sales_Dollars'] >= top_threshold]['Profit_Margin_%']
low_margins = df[df['Total_Sales_Dollars'] <= low_threshold]['Profit_Margin_%']

t_stat, p_value = stats.ttest_ind(top_margins, low_margins, equal_var=False)

print(f"T-Statistic: {t_stat:.4f}")
print(f"P-Value: {p_value:.4e}")
if p_value < 0.05:
    print("Conclusion: Reject Null Hypothesis. There is a significant difference in profit margins.")
else:
    print("Conclusion: Fail to reject Null Hypothesis. No significant difference.")