# -*- coding: utf-8 -*-
"""
Created on Thu Sep 22 16:02:21 2022

@author: Andrews
"""

import pandas as pd 
from backtesting import Backtesting
import plotly.graph_objects as go
from datetime import datetime
from backtesting import PortfolioReport as pr

tradesFolder = 'G:\\andyvoid\\data\\backtested_trades\\'

#%%

folderName = "920 Whole\\"
tradesDf = pd.read_csv(tradesFolder + folderName + '920_40sl_2022-Aug2023.csv')

btreprotBuilder = Backtesting.BacktestReportBuilder("920_40sl_2022", btTradeBook = tradesDf)
report, dailyReturn, monthlyReturn, yeatlyReturnDf = btreprotBuilder.buildReport()

#%%
folderName = "portfolio_920_1130_1\\"
stg920 = pd.read_csv(tradesFolder + folderName + '920_Straddle_trades.csv')
stg11 = pd.read_csv(tradesFolder + folderName + '11.35_Straddle_trades.csv')
stg1pm = pd.read_csv(tradesFolder + folderName + '1.05_Straddle_trades.csv')

portforlioDic = {}
portforlioDic['9:20'] = stg920
portforlioDic['11:30'] = stg11
portforlioDic['1pm'] = stg1pm
capitalAloc = {}
capitalAloc['9:20'] = 200000
capitalAloc['11:30'] = 200000
capitalAloc['1pm'] = 200000

portfolioBuilder = pr.PortfolioReportBuilder(portforlioDic,capitalAloc, 600000)
builderDf, portfolioCum, portfolioMo, portfolioYe = portfolioBuilder.generate()

#%%
"""Data Visualization"""

import pandas as pd

df = pd.read_csv('G:\\andyvoid\\data\\quotes\\csv_database\\banknifty\\options\\2023\\BANKNIFTY02FEB2340200PE.csv')

fig = go.Figure(data=[go.Candlestick(x=df['Date'],
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'])])

fig.show()

