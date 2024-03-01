# -*- coding: utf-8 -*-

import pandas as pd 
from backtesting import Backtesting
import plotly.graph_objects as go
from datetime import datetime
from backtesting import PortfolioReport as pr
import Utils as util
from Utilities import StaticVariables as statics
import datetime as dt


#%%

backtestReportPath = "G:\\andyvoid\\data\\backtest_report\\"
backtestReportTradesPath = "G:\\andyvoid\\data\\backtest_report\\backtest_trades\\"
path_bnfOptionsdb = "G:\\andyvoid\\data\\quotes\\csv_database\\banknifty\\options"

strategiesDf = pd.read_csv(backtestReportPath + "strategy.csv")
#%%

stg920 = pd.read_csv(backtestReportTradesPath  + '2bcadcad_Nifty 9 20 25 SL Classic, Strike fix, Target.csv') #--
stg11 = pd.read_csv(backtestReportTradesPath  + 'd44f8c97_Nifty 11 15 25 SL Classic, Strike fix, Target.csv') # --
#stg1pm = pd.read_csv(backtestReportTradesPath + '5f50a886_Nifty 13 15 25 SL Classic.csv')
bnfstg920 = pd.read_csv(backtestReportTradesPath  + '06cd4a0b_Banknifty 9 20 25 SL Classic, Strike fix, Target.csv') #--
bnfstg11 = pd.read_csv(backtestReportTradesPath  + '0e456fa9_Banknifty 11 15 25 SL Classic, Strike fix, Target.csv') #--
#bnfstg1pm = pd.read_csv(backtestReportTradesPath + '935bcf46_1 15 Classic.csv')
finstg920 = pd.read_csv(backtestReportTradesPath  + '356f53af_finnifty 9 20 25 SL Classic, Strike fix, Target.csv') #--
finstg11 = pd.read_csv(backtestReportTradesPath  + '50b40594_finnifty 11 15 25 SL Classic, Strike fix, Target.csv') #--
#finstg1pm = pd.read_csv(backtestReportTradesPath + '5d9098a8_finNifty 13 15 25 SL Classic.csv')


#%%
hedge = True
capitalCap = True
capital = 450000
util.convertPositionSizing(stg920, statics.NIFTY,capital,hedge, capitalCap)
util.convertPositionSizing(stg11, statics.NIFTY,capital, hedge, capitalCap)
util.convertPositionSizing(bnfstg920, statics.BANKNIFTY,capital, hedge, capitalCap)
util.convertPositionSizing(bnfstg11, statics.BANKNIFTY,capital, hedge, capitalCap)
util.convertPositionSizing(finstg920, statics.FINNIFTY,capital, hedge, capitalCap)
util.convertPositionSizing(finstg11, statics.FINNIFTY,capital, hedge, capitalCap)

#%%
""" Diversified 9 20 an 11 15 Strategy only on Expirydays Nifty, Banknifty, Finnifty All days"""
portforlioDic = {}
portforlioDic['NIFTY_9:20'] = pr.getStrategyDic('NIFTY_9:20', 'NIFTY', stg920, 1375000 , onlyExpiryDays=True)
portforlioDic['NIFTY_11:15'] = pr.getStrategyDic('NIFTY_11:15', 'NIFTY', stg11, 1375000, onlyExpiryDays=True )
#portforlioDic['NIFTY_1:15'] = pr.getStrategyDic('NIFTY_1:15', 'NIFTY', stg1pm, 1000000 )
portforlioDic['BANKNIFTY_9:20'] = pr.getStrategyDic('BANKNIFTY_9:20', 'BANKNIFTY', bnfstg920, 1375000 , onlyExpiryDays=True)
portforlioDic['BANKNIFTY_11:15'] = pr.getStrategyDic('BANKNIFTY_11:15', 'BANKNIFTY', bnfstg11, 1375000 ,onlyExpiryDays=True)
#portforlioDic['BANKNIFTY_1:15'] = pr.getStrategyDic('BANKNIFTY_1:15', 'BANKNIFTY', bnfstg1pm, 1000000 )
portforlioDic['FINNIFTY_9:20'] = pr.getStrategyDic('FINNIFTY_9:20', 'FINNIFTY', finstg920, 1375000, daysList=['Monday', 'Tuesday'])
portforlioDic['FINNIFTY_11:15'] = pr.getStrategyDic('FINNIFTY_11:15', 'FINNIFTY', finstg11, 1375000, daysList=['Monday', 'Tuesday'])
#portforlioDic['FINNIFTY_1:15'] = pr.getStrategyDic('FINNIFTY_1:15', 'FINNIFTY', finstg1pm, 1000000 )
#daysList = ['Monday', 'Tuesday']

#%%
""" Diversified 9 20 an 11 15 Strategy across Nifty, Banknifty, Finnifty All days"""
portforlioDic = {}
portforlioDic['NIFTY_9:20'] = pr.getStrategyDic('NIFTY_9:20', 'NIFTY', stg920, 450000)
portforlioDic['NIFTY_11:15'] = pr.getStrategyDic('NIFTY_11:15', 'NIFTY', stg11, 450000)
#portforlioDic['NIFTY_1:15'] = pr.getStrategyDic('NIFTY_1:15', 'NIFTY', stg1pm, 1000000 )
portforlioDic['BANKNIFTY_9:20'] = pr.getStrategyDic('BANKNIFTY_9:20', 'BANKNIFTY', bnfstg920, 450000)
portforlioDic['BANKNIFTY_11:15'] = pr.getStrategyDic('BANKNIFTY_11:15', 'BANKNIFTY', bnfstg11, 450000)
#portforlioDic['BANKNIFTY_1:15'] = pr.getStrategyDic('BANKNIFTY_1:15', 'BANKNIFTY', bnfstg1pm, 1000000 )
portforlioDic['FINNIFTY_9:20'] = pr.getStrategyDic('FINNIFTY_9:20', 'FINNIFTY', finstg920, 450000)
portforlioDic['FINNIFTY_11:15'] = pr.getStrategyDic('FINNIFTY_11:15', 'FINNIFTY', finstg11, 450000)
#portforlioDic['FINNIFTY_1:15'] = pr.getStrategyDic('FINNIFTY_1:15', 'FINNIFTY', finstg1pm, 1000000 )
#daysList = ['Monday', 'Tuesday']


#%%

portfolioBuilder = pr.PortfolioReportBuilder("Portfolio 0DTE", portforlioDic, 2750000)
builderDf, portfolioCum, portfolioMo, portfolioYe = portfolioBuilder.generate(toHtml=False,
                                                                              htmlPath="G:\\andyvoid\\data\\backtest_report\\webviews\\920_11_20_Classic")

