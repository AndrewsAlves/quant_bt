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

stg920 = pd.read_csv(backtestReportTradesPath  + '87730c8f_Nifty 9 20 25 SL Classic_MAE.csv') #--
stg920_old = pd.read_csv(backtestReportTradesPath  + '615718df_Nifty 9 20 25 SL Classic.csv')