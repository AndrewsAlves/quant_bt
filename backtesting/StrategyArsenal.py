# -*- coding: utf-8 -*-

import pandas as pd 
from backtesting import Backtesting
import plotly.graph_objects as go
from datetime import datetime
from backtesting import PortfolioReport as pr
import os
import uuid
from backtesting import Backtesting as bt

strategyArsenalFile = 'G:\\andyvoid\\data\\backtest_report\\strategy.csv'
strategyArsenalWebviewFile = 'G:\\andyvoid\\data\\backtest_report\\webviews\\'
strategyArsenalTradesFile = 'G:\\andyvoid\\data\\backtest_report\\backtest_trades\\'


class StrategyArsenal() :
    
    def __init__(self) :
        isFileExist = os.path.exists(strategyArsenalFile)
        if not isFileExist:
            strategies = pd.DataFrame(columns=['id','strategy_name','start_date', 'end_date','desc', 'stars'])
            strategies.to_csv(strategyArsenalFile, index = False)
        self.strategies = pd.read_csv(strategyArsenalFile)

    def getNewStrategyId(self) :
        return uuid.uuid4().hex[:8] # Might reduce uniqueness because of slicing

    def addStrategy(self,flags, tradesbookDf : bt.TradeBook) :
                
        tradesbookDf.addAllTradertoDf()
        tradesbookDf.exportTradebookToCSV(flags['id'], flags['strategy_name'])
        
        flagsDf = pd.DataFrame([flags])
        #print(flagsDf)
        self.strategies = pd.concat([self.strategies, flagsDf], axis=0)
        self.strategies.to_csv(strategyArsenalFile, index = False )
        return flags['id'], self.strategies
        
    def generateReport(self, ids) :
        fileName = self.strategies.loc[self.strategies['id'] == ids,'strategy_name'].iloc[0]
        tradesDf = pd.read_csv(strategyArsenalTradesFile + str(ids) + "_" + fileName + '.csv')
        btreprotBuilder = Backtesting.BacktestReportBuilder(fileName, btTradeBook = tradesDf, startCapital = 1000000)
        report, dailyReturn, monthlyReturn, yeatlyReturnDf = btreprotBuilder.buildReport()
        

        
        
        
        
    
