# -*- coding: utf-8 -*-

import pandas as pd 
from backtesting import Backtesting
import plotly.graph_objects as go
from datetime import datetime
from backtesting import PortfolioReport as pr

#%%

backtestReportPath = "G:\\andyvoid\\data\\backtest_report\\"
backtestReportTradesPath = "G:\\andyvoid\\data\\backtest_report\\backtest_trades\\"

strategiesDf = pd.read_csv(backtestReportPath + "strategy.csv")
#%%

stg920 = pd.read_csv(backtestReportTradesPath  + 'e31c5b01_9 20 am dynamic SL 3M.csv')
stg11 = pd.read_csv(backtestReportTradesPath  + 'a79384bf_11 30 am dynamic SL 3M.csv')
stg1pm = pd.read_csv(backtestReportTradesPath + '50b804a3_13 00 am dynamic SL 3M.csv')

#%%
portforlioDic = {}
portforlioDic['9:20'] = stg920
portforlioDic['11:30'] = stg11
portforlioDic['1pm'] = stg1pm
capitalAloc = {}
capitalAloc['9:20'] = 1000000
capitalAloc['11:30'] = 1000000
capitalAloc['1pm'] = 1000000

#%%

portfolioBuilder = pr.PortfolioReportBuilder(portforlioDic,capitalAloc, 3000000)
builderDf, portfolioCum, portfolioMo, portfolioYe = portfolioBuilder.generate()