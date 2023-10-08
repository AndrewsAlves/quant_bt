# -*- coding: utf-8 -*-
import pandas as pd
import datetime as datetime
import os
import pandas as pd
import numpy as np
import datetime as dt
from dateutil.relativedelta import relativedelta 
from tabulate import tabulate

import plotly.express as pltEx
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.io as pio
from plotly.colors import n_colors


def CumulativeCapital(lists, capital):
    cu_list = []
    length = len(lists)
    
    cu_list = [capital + sum(lists[0:x:1]) for x in range(0, length+1)]
    roundedCu = [ round(i) for i in cu_list[1:] ]
    return roundedCu

def calculateRunningDrawdown(cum_profit, capital = 3000000) : 
    # We are going to use a trailing 252 trading day window
    window = 252
    # Calculate the max drawdown in the past window days for each day in the series.
    # Use min_periods=1 if you want to let the first 252 days data have an expanding window
    Roll_Max = cum_profit.rolling(window, min_periods=1).max()
    Daily_Drawdown = ((cum_profit/Roll_Max) - 1.0)
    
    # Next we calculate the minimum (negative) daily drawdown in that window.
    # Again, use min_periods=1 if you want to allow the expanding window
    Max_Daily_Drawdown = Daily_Drawdown.rolling(window, min_periods=1).min()
    
    #Daily_Drawdown.plot()
    #Max_Daily_Drawdown.plot()
    #pp.show()
    
    return Daily_Drawdown * 100

def calculateRunningDrawdownBasedInitialCapital(profit, capital = 3000000) : 
    # We are going to use a trailing 252 trading day window
    window = 252
    # Calculate the max drawdown in the past window days for each day in the series.
    # Use min_periods=1 if you want to let the first 252 days data have an expanding window
  
    profit = profit + capital
    Roll_Max = profit.rolling(window, min_periods=1).max()
    Daily_Drawdown = ((profit/capital) - 1.0)
    
    
    # Next we calculate the minimum (negative) daily drawdown in that window.
    # Again, use min_periods=1 if you want to allow the expanding window
    Max_Daily_Drawdown = Daily_Drawdown.rolling(window, min_periods=1).min()
    
    #Daily_Drawdown.plot()
    #Max_Daily_Drawdown.plot()
    #pp.show()
    
    return Daily_Drawdown * 100

class PortfolioReportBuilder :
    
    def __init__(self, portfolioDfDic, capitalAlocDic,totalCapital, year = None) : 
        self.portfolioDic = portfolioDfDic
        self.capitalAlocDic = capitalAlocDic
        self.porfolio = pd.DataFrame()
        self.portfolioCum = pd.DataFrame()
        self.portfolioMontly = pd.DataFrame()
        self.portfolioYearly = pd.DataFrame()
        self.totalCapital = totalCapital
        self.year = year
        #self.startDate = startDate
        #self.endDate = endDate


    def generate(self) :
        
        stgNameList = []
        for stgName,strategy in self.portfolioDic.items() :
            stgNameList.append(stgName)
            capital = self.capitalAlocDic[stgName]

            strategy['Entry Time'] = pd.to_datetime(strategy['Entry Time'])
            strategy['Exit Time'] = pd.to_datetime(strategy['Exit Time'])
            
            dateAndProfitDf = pd.DataFrame()
            dateAndProfitDf['Date'] = strategy['Exit Time']
            dateAndProfitDf[stgName + '_profit'] = strategy['profit']
            
            strategyDaily = dateAndProfitDf.groupby(pd.Grouper(key='Date', axis=0, freq='D')).sum()
            
            dateAndProfitDf['Cum. ' + stgName] =  pd.Series(CumulativeCapital(strategy['profit'].tolist(), capital))
            cumDf = dateAndProfitDf[['Date','Cum. ' + stgName]].groupby(pd.Grouper(key='Date', axis=0, freq='D')).last()
            
            self.porfolio = pd.concat([self.porfolio, strategyDaily], axis=1)
            self.portfolioCum = pd.concat([self.portfolioCum, cumDf], axis=1)

        
        self.porfolio['Daily_Net_Pnl'] = self.porfolio.sum(axis = 1)
        self.porfolio.reset_index(inplace = True)
        
        self.portfolioCum.reset_index(inplace= True)
        self.portfolioCum['Cum. Daily_Net_Pnl'] = pd.Series(CumulativeCapital(self.porfolio['Daily_Net_Pnl'].tolist(), self.totalCapital))
        self.portfolioCum = self.portfolioCum.fillna(method='ffill')
        
        self.portfolioMontly = self.porfolio.groupby(pd.Grouper(key='Date', axis=0, freq='M')).sum()
        self.portfolioMontly['Cum. Profolio'] = self.portfolioCum[['Date', 'Cum. Daily_Net_Pnl']].groupby(pd.Grouper(key='Date', axis=0, freq='M')).last()

        self.portfolioYearly = self.porfolio.groupby(pd.Grouper(key='Date', axis=0, freq='Y')).sum()
        self.portfolioYearly['Cum. Profolio'] = self.portfolioCum[['Date', 'Cum. Daily_Net_Pnl']].groupby(pd.Grouper(key='Date', axis=0, freq='Y')).last()
        
        
        self.portfolioMontly['Com. return per'] = self.portfolioMontly['Daily_Net_Pnl'] / (self.totalCapital / 100.0)
        self.portfolioYearly['Com. return per'] = self.portfolioYearly['Daily_Net_Pnl'] / (self.totalCapital / 100.0)
    
        if self.year != None :
            self.porfolio = self.porfolio.loc[self.porfolio['Date'].dt.year == self.year]
            self.portfolioCum = self.portfolioCum.loc[self.portfolioCum['Date'].dt.year == self.year]
            self.portfolioMontly = self.portfolioMontly.loc[self.portfolioMontly.index.year == self.year]
            self.portfolioYearly = self.portfolioYearly.loc[self.portfolioYearly.index.year == self.year]

    
        #fig = pltEx.line(self.portfolioCum, x="Date", y= self.portfolioCum.columns[1:])
        #fig.show()
        
        ############ TABLE LAOUT ################
        
        headerColor = pltEx.colors.qualitative.Dark24[5]
        cellColor = pltEx.colors.qualitative.Pastel2[7]    
        
        fig = make_subplots(
            rows=1, cols=2,
            shared_xaxes=True,
            vertical_spacing=0.01,
            horizontal_spacing=0.01,
            specs=[[{"type": "table"}, {"type": "table"}]]
        )
        
        columnList = list(self.portfolioMontly.columns)
        columnList.insert(0, 'Date')
        
        listOfSeries = []
        formatList = []
        listOfSeries.append(self.portfolioMontly.index.astype(str))
        formatList.append(None)
        for index in range(1,len(columnList)) :
            listOfSeries.append(self.portfolioMontly[columnList[index]])
            formatList.append('.2f')

        
            
        fig.add_trace(go.Table(header=dict(values= columnList, fill_color=headerColor, align='left', font=dict(color='White')),
                               cells=dict(values= listOfSeries,
                                          fill_color= cellColor, 
                                          align='left',
                                          format = formatList)),
                      row=1, col=1)
        
        columnList = list(self.portfolioYearly.columns)
        columnList.insert(0, 'Date')
        
        listOfSeries = []
        formatList = []
        listOfSeries.append(self.portfolioYearly.index.astype(str))
        formatList.append(None)
        for index in range(1,len(columnList)) :
            listOfSeries.append(self.portfolioYearly[columnList[index]])
            formatList.append('.2f')

        fig.add_trace(go.Table(header=dict(values= columnList, fill_color=headerColor, align='left', font=dict(color='White')),
                               cells=dict(values=listOfSeries,
                                          fill_color= cellColor,
                                          align='left',
                                          format = formatList)),
                      row=1, col=2)
    
        fig.update_layout(
            showlegend=False,
            title_text= "Portfolio Report",
        )
    
        # Plot the figure
        fig.show()
        
         #//////////////////////////////// CHART LAYOUT //////////////////
        
        runningDrawdownDf = pd.DataFrame()
        runningDrawdownDf['drawdown'] = calculateRunningDrawdown(self.portfolioCum['Cum. Daily_Net_Pnl'])
        runningDrawdownDf['Date'] = self.portfolioCum['Date']
        
        figCharts = make_subplots(rows=3, cols=1)
        figCharts.append_trace(go.Scatter(x=self.portfolioCum['Date'], y=self.portfolioCum['Cum. Daily_Net_Pnl'],
                    mode='lines+markers',
                    name='Cum. Profits'), row=1, col=1)
                            
        figCharts.append_trace(go.Scatter(x= runningDrawdownDf['Date'], y=runningDrawdownDf['drawdown'],
                    mode='lines+markers',
                    name='Cum. Drawdown'), row=2, col=1)
        
        figCharts.append_trace(go.Scatter(x = self.porfolio['Date'], y = self.porfolio['Daily_Net_Pnl'],
                    mode='lines+markers',
                    name='Daily PnL'), row=3, col=1)
        
        figCharts.update_layout(title_text="Charts", autosize = True, height = 900*3)
        figCharts.update_xaxes(rangeslider=dict(visible=False)) 
        figCharts.show()
        
        return self.porfolio, self.portfolioCum, self.portfolioMontly, self.portfolioYearly
        

             
             
             
        
        