# -*- coding: utf-8 -*-
"""
Spyder Editor

This module is for Scalp M16 Trade analytics

"""
import pandas as pd
import datetime as dt
import os
from TradeReport import TradeReportBuilder

""" 
Backtested report 

Start Date *
End Date *
Duration *
Exposure Time 
Equity Final *
Equity Peak *
Total Return [%] *
com Return (Ann.) (%) *
STD / Volatality (Ann.) (%) 
Sharpe Ratio 
Sortino Ratio 
Calmar Ratio 
-Max. Drawdown *
-Avg. Drawdown 
-Max. Drawdown Duration 
Avg. Drawdown Duration 
-# Trades *
-Win Rate [%] *
-Best Trade *
-Wrost Trade *
-Avg. Trade *
-Max Trade Duration *
-Avg. Trade Duration *
Profit Factor *
Expectancy [%]
SQN
_Strategy *
No. of days Traded
"""



folder_path = 'G://andyvoid//projects//andyvoid_tools//options_rifle//database//virtual_trades_logs'  # Replace with the path to your folder
files = os.listdir(folder_path)
tradesDf = None
dfList = []
for file in files:
    filepath = folder_path + "//" + file
    df1 = pd.read_csv(filepath)
    dfList.append(df1)
    
df = pd.concat(dfList)
df = df.sort_values(by='entry_time', ascending=True)

startDate = '2023-04-01'
endDate = '2023-04-25'
df_filtered = df.loc[(df['entry_time'] >= startDate) & (df['entry_time'] <= endDate)]


btreprotBuilder = TradeReportBuilder("1m Scalping", btTradeBook = df_filtered, startCapital = 750000)
report, dailyReturn, monthlyReturn, yeatlyReturnDf, avgPnl = btreprotBuilder.buildReport()


totalPnl = df_filtered['pnl'].sum()









        
    
