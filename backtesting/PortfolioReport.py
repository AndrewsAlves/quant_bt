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

class PortfolioReportBuilder :
    
    def __init__(self, portfolioDfDic, capitalAlocDic, totalCapital) : 
        self.portfolioDic = portfolioDfDic
        self.capitalAlocDic = capitalAlocDic
        self.porfolio = pd.DataFrame()
        self.portfolioCum = pd.DataFrame()
        self.portfolioMontly = pd.DataFrame()
        self.portfolioYearly = pd.DataFrame()
        self.totalCapital = totalCapital

        
        
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
        print(columnList)
        
        fig.add_trace(go.Table(header=dict(values= columnList, fill_color=headerColor, align='left', font=dict(color='White')),
                               cells=dict(values=self.portfolioYearly.columns, 
                                          fill_color= cellColor, 
                                          align='left')),
                      row=1, col=1)
        
        fig.add_trace(go.Table(header=dict(values= columnList, fill_color=headerColor, align='left', font=dict(color='White')),
                               cells=dict(values=self.portfolioMontly.columns, 
                                          fill_color= cellColor,
                                          align='left')),
                      row=1, col=2)
    
        fig.update_layout(
            showlegend=False,
            title_text= "Portfolio Report",
        )
    
                                        
                                        # Plot the figure
        fig.show()
        
        return self.porfolio, self.portfolioCum, self.portfolioMontly, self.portfolioYearly
        

             
             
             
        
        