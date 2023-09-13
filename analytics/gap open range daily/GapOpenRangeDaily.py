"""
authour Andrews
Date 22-08-2023

Description : A analysis of how much gap up or gap down happened from previous day close. 

"""



import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import os, os.path
from tqdm import tqdm
import math
import traceback
import logging
from backtesting import LocalCsvDatabase as csv_database
import numpy as np
from scipy.stats import norm
import webbrowser
import plotly.graph_objs as go
from tabulate import tabulate


#%%


tf_1D = "1D"

start_date = '2010-01'
end_date = '2021-12'


bnfResampled = csv_database.get_banknifty_data(start_date, end_date, tf_1D)
vixRaw = pd.read_csv("G:\\andyvoid\\data\\quotes\\csv_database\\india_vix\\INDIA_VIX_2010_2023.csv")
vixRaw["Date"] = pd.to_datetime(vixRaw["Date"], format = "%Y-%m-%d")

#%%

bnfResampled['Prev_Close'] = bnfResampled['Close'].shift(1)
bnfResampled['Gap'] = bnfResampled['Open'] - bnfResampled['Prev_Close']
bnfResampled['Gap_Percentage'] = round((bnfResampled['Gap'] / bnfResampled['Prev_Close']) * 100, 2)

bnfResampled['Gap_Status'] = ['Gap Up' if gap > 0.10 else 'Gap Down' if gap < -0.10 else 'No Gap' for gap in bnfResampled['Gap_Percentage']]
# Handling NaN or infinite values
bnfResampled.dropna(subset=['Gap_Percentage'], inplace=True)
bnfResampled['gap_per'] = bnfResampled['Gap_Percentage'].abs()

#%% 

""" CALCULATE GAP DISTRUBUTION AND ITS PERCENTAGE """

interval = 1
bin_edges = np.arange(-10, 10, interval)
print(bin_edges)

# Creating the histogram data
hist_data, bin_edges = np.histogram(bnfResampled['Gap_Percentage'], bins=bin_edges)
gap_dist = pd.DataFrame()
bin_series = pd.Series(bin_edges)
hist_data_series = pd.Series(hist_data)
gap_dist['gaps dist'] = bin_series.astype(str) + " to " + (bin_series + interval).astype(str)
gap_dist['gap counts'] = hist_data_series
gap_dist['gap count %'] = round((gap_dist['gap counts'] / len(bnfResampled.index)) * 100, 2)


#%%

bnfResampled['Year'] = bnfResampled['Date'].dt.year

# Calculate gap distribution and percentage per year
gap_dist_per_year = []

for year, year_data in bnfResampled.groupby('Year'):
    hist_data, bin_edges = np.histogram(year_data['Gap_Percentage'], bins=bin_edges)
    bin_series = pd.Series(bin_edges)
    hist_data_series = pd.Series(hist_data)
    
    year_gap_dist = pd.DataFrame()
    year_gap_dist['Year'] = [year] * len(bin_series)
    year_gap_dist['gaps dist'] = bin_series.astype(str) + " to " + (bin_series + interval).astype(str)
    year_gap_dist['gap counts'] = hist_data_series
    year_gap_dist['gap count %'] = round((year_gap_dist['gap counts'] / len(year_data)) * 100, 2)
    
    gap_dist_per_year.append(year_gap_dist)

# Concatenate the per-year dataframes into a single dataframe
gap_dist_per_year = pd.concat(gap_dist_per_year, ignore_index=True)

gap_years = gap_dist_per_year.groupby('Year')

table = tabulate(gap_dist_per_year, headers='keys', tablefmt='grid')

print(gap_years.get_group(2012)['gap counts'])

pivot_df = df.pivot(index='Year', columns='Metric', values='Value')



#%%
""" Simple Gapup and Gapdown plot """
plt.figure(figsize=(10, 6))
plt.plot(bnfResampled['Date'], bnfResampled['Gap_Percentage'], marker='o')
plt.title('Percentage Gap Up/Down')
plt.xlabel('Date')
plt.ylabel('Gap Percentage (%)')
plt.grid(True)
plt.show()

#%%

""" Gapup and Gapdown bar plot """

gap_counts = bnfResampled['Gap_Status'].value_counts()

# Plotting the gap category distribution
plt.figure(figsize=(8, 6))
gap_counts.plot(kind='bar', color=['green', 'red', 'blue'])
plt.title('Distribution of Gap Categories')
plt.xlabel('Gap Category')
plt.ylabel('Number of Occurrences')
plt.xticks(rotation=0)
plt.grid(True)
plt.show()

#%%
""" Gapup and Gapdown Distribution Histogram """


# Creating a distribution chart
plt.figure(figsize=(10, 6))
bin_edges = np.arange(-10, 10,.2)
bin_edges2 = np.arange(-10, 10,1)

# Plotting the histogram of gap percentages
plt.hist(bnfResampled['Gap_Percentage'], bins=bin_edges, color='skyblue', edgecolor='black')
plt.title('Distribution of Gap Percentages')
plt.xlabel('Gap Percentage (%)')
plt.xticks(bin_edges2)
plt.ylabel('Number of Occurrences')
plt.grid(True)
plt.show()

#%%
""" Gapup and Gapdown Distribution Histogram Plotyl """


bin_edges = np.arange(-10, 10,0.5)
histogram_chart = go.Figure()

# Add the histogram trace
histogram_chart.add_trace(go.Histogram(x=bnfResampled['Gap_Percentage'], nbinsx=len(bin_edges)-1, xbins=dict(start=-20, end=20)))

# Update layout
histogram_chart.update_layout(
    title='Distribution of Gap Percentages (Plotly)',
    xaxis_title='Gap Percentage (%)',
    yaxis_title='Number of Occurrences',
    xaxis=dict(tickvals=bin_edges, ticktext=[f'{val}%' for val in bin_edges])
)

histogram_chart.write_html('histogram_chart.html')
# Show the Plotly chart
histogram_chart.show()

#%%
"""COMBINE VIX AND GAP PERCENTAGE """

gap_df = pd.DataFrame()
gap_df['Date'] = bnfResampled['Date']
gap_df['Gap_Percentage'] = bnfResampled['Gap_Percentage']

combined_df = pd.merge(vixRaw, gap_df, on='Date')

# Creating a scatter plot to visualize VIX vs Gap Percentage
plt.figure(figsize=(10, 6))
plt.scatter(combined_df['Close'], combined_df['Gap_Percentage'], color='blue')
plt.title('Effects in GAP Percentage on VIX')
plt.xlabel('India VIX Close Price')
plt.ylabel('Daily Gap Percentage')
plt.grid(True)
plt.show()


#%% 

# Create a Plotly table chart
table_chart = go.Figure(data=[go.Table(
    header=dict(values=['Gap Percentage', 'Count']),
    cells=dict(values=[gap_dist['gaps dist'][:-1], hist_data])
)])

# Update layout
table_chart.update_layout(
    title='Histogram Data as Table',
    xaxis_title='Gap Percentage (%)',
    yaxis_title='Count'
)
table_chart.write_html('histogram_chart_table.html')

webbrowser.open('histogram_chart_table.html')

#%%


