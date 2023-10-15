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

stg920 = pd.read_csv(backtestReportTradesPath  + '615718df_Nifty 9 20 25 SL Classic.csv')
stg11 = pd.read_csv(backtestReportTradesPath  + '90aa6b50_Nifty 11 15 25 SL Classic.csv')
#stg1pm = pd.read_csv(backtestReportTradesPath + '5f50a886_Nifty 13 15 25 SL Classic.csv')
bnfstg920 = pd.read_csv(backtestReportTradesPath  + '10fc0fa1_9 20 Classic.csv')
bnfstg11 = pd.read_csv(backtestReportTradesPath  + 'c1985225_11 15 Classic.csv')
#bnfstg1pm = pd.read_csv(backtestReportTradesPath + '935bcf46_1 15 Classic.csv')
finstg920 = pd.read_csv(backtestReportTradesPath  + '8164be89_Finnifty 9 20 25 SL Classic.csv')
finstg11 = pd.read_csv(backtestReportTradesPath  + '38671782_Finnifty 11 15 25 SL Classic.csv')
#finstg1pm = pd.read_csv(backtestReportTradesPath + '5d9098a8_finNifty 13 15 25 SL Classic.csv')

#%%
portforlioDic = {}
#portforlioDic['NIFTY_9:20'] = pr.getStrategyDic('NIFTY_9:20', 'NIFTY', stg920, 1000000 , ['Friday'])
#portforlioDic['NIFTY_11:15'] = pr.getStrategyDic('NIFTY_11:15', 'NIFTY', stg11, 1000000, ['Friday'])
#portforlioDic['NIFTY_1:15'] = pr.getStrategyDic('NIFTY_1:15', 'NIFTY', stg1pm, 1000000 )
#portforlioDic['BANKNIFTY_9:20'] = pr.getStrategyDic('BANKNIFTY_9:20', 'BANKNIFTY', bnfstg920, 1000000 , ['Friday'])
#portforlioDic['BANKNIFTY_11:15'] = pr.getStrategyDic('BANKNIFTY_11:15', 'BANKNIFTY', bnfstg11, 1000000 ,   ['Friday'])
#portforlioDic['BANKNIFTY_1:15'] = pr.getStrategyDic('BANKNIFTY_1:15', 'BANKNIFTY', bnfstg1pm, 1000000 )
portforlioDic['FINNIFTY_9:20'] = pr.getStrategyDic('FINNIFTY_9:20', 'FINNIFTY', finstg920, 1000000 , daysList = ['Friday'])
portforlioDic['FINNIFTY_11:15'] = pr.getStrategyDic('FINNIFTY_11:15', 'FINNIFTY', finstg11, 1000000, daysList = ['Friday'])
#portforlioDic['FINNIFTY_1:15'] = pr.getStrategyDic('FINNIFTY_1:15', 'FINNIFTY', finstg1pm, 1000000 )
#daysList = ['Monday', 'Tuesday']

#%%

portfolioBuilder = pr.PortfolioReportBuilder(portforlioDic, 2000000)
builderDf, portfolioCum, portfolioMo, portfolioYe = portfolioBuilder.generate()

