# -*- coding: utf-8 -*-

import pandas as pd 
from backtesting import Backtesting
import plotly.graph_objects as go
from datetime import datetime
from backtesting import PortfolioReport as pr

#%%

backtestReportPath = "G:\\andyvoid\\data\\backtest_report\\"
backtestReportTradesPath = "G:\\andyvoid\\data\\backtest_report\\backtest_trades\\"
path_bnfOptionsdb = "G:\\andyvoid\\data\\quotes\\csv_database\\banknifty\\options"


strategiesDf = pd.read_csv(backtestReportPath + "strategy.csv")
#%%

stg920 = pd.read_csv(backtestReportTradesPath  + '10fc0fa1_9 20 Classic.csv')
stg11 = pd.read_csv(backtestReportTradesPath  + 'c1985225_11 15 Classic.csv')
stg1pm = pd.read_csv(backtestReportTradesPath + '935bcf46_1 15 Classic.csv')

#%%
portforlioDic = {}
portforlioDic['9:20'] = stg920
portforlioDic['11:15'] = stg11
portforlioDic['1:15'] = stg1pm
capitalAloc = {}
capitalAloc['9:20'] = 1000000
capitalAloc['11:15'] = 1000000
capitalAloc['1:15'] = 1000000

#%%

portfolioBuilder = pr.PortfolioReportBuilder(portforlioDic,capitalAloc, 3000000, onlyExpiry=True)
builderDf, portfolioCum, portfolioMo, portfolioYe = portfolioBuilder.generate()

