# -*- coding: utf-8 -*-
"""
Created on Thu Sep 22 16:02:21 2022

@author: Andrews
"""

import pandas as pd 
from backtesting import Backtesting

tradesFolder = 'G:\\andyvoid\\data\\backtested_trades\\'
tradesDf = pd.read_csv(tradesFolder + '1pm_Straddle_trades.csv')

btreprotBuilder = Backtesting.BacktestReportBuilder("1pm_Straddle_trades", btTradeBook = tradesDf)
report, dailyReturn, monthlyReturn, yeatlyReturnDf = btreprotBuilder.buildReport()


