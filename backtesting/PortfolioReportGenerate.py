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
stg11 = pd.read_csv(backtestReportTradesPath  + '754c514f_Nifty 11 15 25 SL Classic_MAE.csv') # --
#stg1pm = pd.read_csv(backtestReportTradesPath + '5f50a886_Nifty 13 15 25 SL Classic.csv')
bnfstg920 = pd.read_csv(backtestReportTradesPath  + 'ef10ae56_Banknifty 9 20 25 SL Classic_MAE.csv') #--
bnfstg11 = pd.read_csv(backtestReportTradesPath  + '39b7f3e7_Banknifty 11 15 25 SL Classic_MAE.csv') #--
#bnfstg1pm = pd.read_csv(backtestReportTradesPath + '935bcf46_1 15 Classic.csv')
finstg920 = pd.read_csv(backtestReportTradesPath  + '2116b53a_Finnifty 9 20 25 SL Classic_MAE.csv') #--
finstg11 = pd.read_csv(backtestReportTradesPath  + 'f0788de4_Finnifty 11 15 25 SL Classic_MAE.csv') #--
#finstg1pm = pd.read_csv(backtestReportTradesPath + '5d9098a8_finNifty 13 15 25 SL Classic.csv')

#%%
portforlioDic = {}
portforlioDic['NIFTY_9:20'] = pr.getStrategyDic('NIFTY_9:20', 'NIFTY', stg920, 1000000 , onlyExpiryDays=True)
portforlioDic['NIFTY_11:15'] = pr.getStrategyDic('NIFTY_11:15', 'NIFTY', stg11, 1000000, onlyExpiryDays=False)
#portforlioDic['NIFTY_1:15'] = pr.getStrategyDic('NIFTY_1:15', 'NIFTY', stg1pm, 1000000 )
portforlioDic['BANKNIFTY_9:20'] = pr.getStrategyDic('BANKNIFTY_9:20', 'BANKNIFTY', bnfstg920, 1000000 , onlyExpiryDays=True)
portforlioDic['BANKNIFTY_11:15'] = pr.getStrategyDic('BANKNIFTY_11:15', 'BANKNIFTY', bnfstg11, 1000000 , onlyExpiryDays=True)
#portforlioDic['BANKNIFTY_1:15'] = pr.getStrategyDic('BANKNIFTY_1:15', 'BANKNIFTY', bnfstg1pm, 1000000 )
portforlioDic['FINNIFTY_9:20'] = pr.getStrategyDic('FINNIFTY_9:20', 'FINNIFTY', finstg920, 1000000, daysList = ['Monday', 'Tuesday'])
portforlioDic['FINNIFTY_11:15'] = pr.getStrategyDic('FINNIFTY_11:15', 'FINNIFTY', finstg11, 1000000, daysList = ['Monday', 'Tuesday'])
#portforlioDic['FINNIFTY_1:15'] = pr.getStrategyDic('FINNIFTY_1:15', 'FINNIFTY', finstg1pm, 1000000 )
#daysList = ['Monday', 'Tuesday']

#%%

portfolioBuilder = pr.PortfolioReportBuilder("Portfolio 0DTE", portforlioDic, 2000000, 2023)
builderDf, portfolioCum, portfolioMo, portfolioYe = portfolioBuilder.generate()

