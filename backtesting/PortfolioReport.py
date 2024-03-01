# -*- coding: utf-8 -*-
import pandas as pd
import datetime as datetime
import os
import pandas as pd
import numpy as np
import datetime as dt
from dateutil.relativedelta import relativedelta 
from tabulate import tabulate
from Utilities import StaticVariables as statics
from backtesting import Backtesting as backtesting
import Utils as util

import plotly.express as pltEx
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.io as pio
from plotly.colors import n_colors

path_bnfOptionsdb = "G:\\andyvoid\\data\\quotes\\csv_database\\banknifty\\options"


def CumulativeCapital(lists, capital):
    cu_list = []
    length = len(lists)
    
    cu_list = [capital + sum(lists[0:x:1]) for x in range(0, length+1)]
    roundedCu = [ round(i) for i in cu_list[1:] ]
    return roundedCu

def calculateProfitFactor(tBook) : 
    wins = tBook['Daily_Net_Pnl'].loc[tBook['Daily_Net_Pnl'] > 0].sum()
    loss = tBook['Daily_Net_Pnl'].loc[tBook['Daily_Net_Pnl'] < 0].sum()
    return wins / abs(loss)

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

def generate_streak_info(shots):
    """
    Parameters
    ----------
    
    shots:
        A dataframe containing data about shots.
        Must contain a `results` column with two
        unique values for made and missed shots.
        Must be homogenous (contain only shots
        that qualify for the streak type you want
        to calculate (eg all FT for a single
        player) and be pre-sorted by time.

    Returns
    -------

    shots_with_streaks:
        The original dataframe with a new column
        `streak_counter` containing integers with 
        counts for each streak.
    """
    
    data = shots['win_loss'].to_frame()
    data['start_of_streak'] = data['win_loss'].ne(data['win_loss'].shift())
    data['streak_id'] = data.start_of_streak.cumsum()
    data['streak_counter'] = data.groupby('streak_id').cumcount() + 1
    shots_with_streaks = pd.concat([shots, data['streak_counter']], axis=1)
    return shots_with_streaks

def getOnlyExpiryDayTrades(tBook, symbol) : 
    
    symbolDf = pd.read_csv(statics.path_db + "\\" + symbol + "\\options\\" + "option_symbols.csv")
    symbolDf['Expiry Date'] = pd.to_datetime(symbolDf['Expiry Date'])
    
    tBook['Entry Time'] = pd.to_datetime(tBook['Entry Time'])
    tBook['Exit Time'] = pd.to_datetime(tBook['Exit Time'])

    expiryDayList = []
    for i, row in tBook.iterrows() : 
        Date = row['Entry Time'].replace(hour=0, minute=0)
        if Date in symbolDf['Expiry Date'].values:
            expiryDayList.append("yes")
        else : 
            expiryDayList.append("no")
        
    tBook['expiry'] = pd.Series(expiryDayList)
    tBook['day'] = tBook['Entry Time'].dt.day_name()
    tBookOnlyExpiry = tBook[tBook['expiry'] == "yes"]

    return tBookOnlyExpiry

def getOnlyTheDays(tBook, dayList = []) : 
    
    daysDf = None
    portfolioDayWise = tBook.groupby(tBook['Entry Time'].dt.day_name())
    
    for day in dayList : 
        dayDf = portfolioDayWise.get_group(day)
        if daysDf is None :
            daysDf = dayDf
        else :
            daysDf =  pd.concat([daysDf, dayDf])
                    
    daysDf['Entry Time'] = pd.to_datetime(daysDf['Entry Time'])
    daysDf['Exit Time'] = pd.to_datetime(daysDf['Exit Time'])        

    daysDf = daysDf.sort_values(by = 'Entry Time', axis=0, ascending=True)
    daysDf.reset_index(inplace = True)
    daysDf = daysDf.drop('index', axis=1)
    
    return daysDf

def getStrategyDic(name,symbol, stgDf, capitalAllocated, daysList = [], onlyExpiryDays = False) :
    strategy = {}
    strategy['name'] = name
    strategy['symbol'] = symbol
    strategy['tbook'] = stgDf
    strategy['capital'] = capitalAllocated
    strategy['daysList'] = daysList
    strategy['onlyExpiryDay'] = onlyExpiryDays
    return strategy
    
class PortfolioReportBuilder :
    
    def __init__(self, portfolioName, portfolioDic, totalCapital, year = None) : 
        self.portfolioName = portfolioName
        self.portfolioDic = portfolioDic
        self.portfolioTradeBook = pd.DataFrame()
        self.porfolio = pd.DataFrame()
        self.portfolioCum = pd.DataFrame()
        self.portfolioMontly = pd.DataFrame()
        self.portfolioYearly = pd.DataFrame()
        self.totalCapital = totalCapital
        self.year = year
        #self.onlyExpiry = onlyExpiry
        #self.startDate = startDate
        #self.endDate = endDate


    def generate(self, toHtml = False, htmlPath = "") :
        
        stgNameList = []
        for stgName,strategyDic in self.portfolioDic.items() :
            
            strategy = strategyDic['tbook']
            symbol = strategyDic['symbol']
            onlyExpiry = strategyDic['onlyExpiryDay']
            daysList = strategyDic['daysList']
            
            strategy['Entry Time'] = pd.to_datetime(strategy['Entry Time'])
            strategy['Exit Time'] = pd.to_datetime(strategy['Exit Time'])
            
            
            if len(daysList) == 0 :
             if onlyExpiry : 
                 strategy = getOnlyExpiryDayTrades(strategy, symbol)
            else :
                 strategy = getOnlyTheDays(strategy, daysList)
                 
            if self.year != None :
                strategy = strategy.loc[(strategy['Entry Time'].dt.year == self.year) & (strategy['Exit Time'].dt.year == self.year)]
                
            
            stgNameList.append(stgName)
            capital = strategyDic['capital']

            dateAndProfitDf = pd.DataFrame()
            dateAndProfitDf['Date'] = strategy['Exit Time']
            dateAndProfitDf[stgName + '_profit'] = strategy['profit']
            
            strategyDaily = dateAndProfitDf.groupby(pd.Grouper(key='Date', axis=0, freq='D')).sum()
            
            dateAndProfitDf['Cum. ' + stgName] =  pd.Series(CumulativeCapital(strategy['profit'].tolist(), capital))
            cumDf = dateAndProfitDf[['Date','Cum. ' + stgName]].groupby(pd.Grouper(key='Date', axis=0, freq='D')).last()
            
            self.portfolioTradeBook = pd.concat([self.portfolioTradeBook, strategy], axis=0)
            self.porfolio = pd.concat([self.porfolio, strategyDaily], axis=1)
            self.portfolioCum = pd.concat([self.portfolioCum, cumDf], axis=1)

        
        self.portfolioTradeBook.sort_values(by='Entry Time', inplace=True)
        self.portfolioTradeBook.reset_index(inplace=True)
        self.portfolioTradeBook = self.portfolioTradeBook.drop(['Unnamed: 0', 'index'], axis=1)
        
        
        self.porfolio['Daily_Net_Pnl'] = self.porfolio.sum(axis = 1)
        self.porfolio.reset_index(inplace = True)
        
        
        ## calculate winning streak on day wise
        self.porfolioStreaks = pd.DataFrame()
        self.porfolioStreaks['win_loss'] = np.sign(self.porfolio['Daily_Net_Pnl'])
        self.porfolioStreaks = self.porfolioStreaks[self.porfolioStreaks['win_loss'] != 0]
        self.porfolioStreaks = generate_streak_info(self.porfolioStreaks['win_loss'].to_frame())
        self.positiveDayStreaks = (self.porfolioStreaks.query('win_loss > 0')).max()['streak_counter']
        self.negativeDayStreaks = (self.porfolioStreaks.query('win_loss < 0')).max()['streak_counter']
        print('Positive Streaks - ' + str(self.positiveDayStreaks))
        print('Negative Streaks - ' + str(self.negativeDayStreaks))

        
        self.portfolioDayWisePnl = self.porfolio.groupby(self.porfolio['Date'].dt.day_name()).sum()

        self.portfolioCum.reset_index(inplace= True)
        self.portfolioCum['Cum. Daily_Net_Pnl'] = pd.Series(CumulativeCapital(self.porfolio['Daily_Net_Pnl'].tolist(), self.totalCapital))
        self.portfolioCum = self.portfolioCum.fillna(method='ffill')
        
        self.portfolioMontly = self.porfolio.groupby(pd.Grouper(key='Date', axis=0, freq='M')).sum()
        self.portfolioMontly['Cum. Profolio'] = self.portfolioCum[['Date', 'Cum. Daily_Net_Pnl']].groupby(pd.Grouper(key='Date', axis=0, freq='M')).last()

        self.portfolioYearly = self.porfolio.groupby(pd.Grouper(key='Date', axis=0, freq='Y')).sum()
        self.portfolioYearly['Cum. Profolio'] = self.portfolioCum[['Date', 'Cum. Daily_Net_Pnl']].groupby(pd.Grouper(key='Date', axis=0, freq='Y')).last()
        
        
        self.portfolioMontly['Com. return per'] = self.portfolioMontly['Daily_Net_Pnl'] / (self.totalCapital / 100.0)
        self.portfolioYearly['Com. return per'] = self.portfolioYearly['Daily_Net_Pnl'] / (self.totalCapital / 100.0)
        
        # if self.year != None :
        #     self.porfolio = self.porfolio.loc[self.porfolio['Date'].dt.year == self.year]
        #     self.portfolioCum = self.portfolioCum.loc[self.portfolioCum['Date'].dt.year == self.year]
        #     self.portfolioMontly = self.portfolioMontly.loc[self.portfolioMontly.index.year == self.year]
        #     self.portfolioYearly = self.portfolioYearly.loc[self.portfolioYearly.index.year == self.year]
        
        ############ BUILD BACKTESTREPORT #########
        
        btreprotBuilder = backtesting.BacktestReportBuilder("Portfolio", 
                                                            self.portfolioName, 
                                                            btTradeBook = self.portfolioTradeBook, 
                                                            startCapital = self.totalCapital,
                                                            generateGraph=False)
        report, dailyReturn, monthlyReturn, yeatlyReturnDf = btreprotBuilder.buildReport()
        

        ############ TABULATE LAYOUT #############
        
        dailyReport = {}
        dailyReport['Profit factor'] = calculateProfitFactor(self.porfolio)
        dailyReport['Winning Streak'] = self.positiveDayStreaks
        dailyReport['Losing Streak'] = self.negativeDayStreaks

        
        print("\\\\\\\\\\\\\ BACKTEST REPORT ///////////////")
        print(tabulate(dailyReport.items(), headers = ['Parameters', 'Result'], tablefmt='grid'))

        
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
        
        """
        subplot_titles=("Daily Cumulative Profits", 
                                                                 "Daily Cumulative Drawdown",
                                                                 "Daily Profit & loss",
                                                                 "Day Wise total Profit & loss",
                                                                 "Distribution of maximum adverse excursion Percentages (Plotly)",
                                                                 "Distribution of maximum favorable excursion Percentages (Plotly)")"""
        
        figCharts = make_subplots(rows=6, cols=1,subplot_titles=("Daily Cumulative Profits", 
                                                                 "Daily Cumulative Drawdown",
                                                                 "Daily Profit & loss",
                                                                 "Day Wise total Profit & loss",
                                                                 "Distribution of maximum adverse excursion Percentages (Plotly)",
                                                                 "Distribution of maximum favorable excursion Percentages (Plotly)"))
        
        figCharts.append_trace(go.Scatter(x=self.portfolioCum['Date'], y=self.portfolioCum['Cum. Daily_Net_Pnl'],
                    mode='lines+markers',
                    name='Cum. Profits'), row=1, col=1)
                            
        figCharts.append_trace(go.Scatter(x= runningDrawdownDf['Date'], y=runningDrawdownDf['drawdown'],
                    mode='lines+markers',
                    name='Cum. Drawdown'), row=2, col=1)
        
        figCharts.append_trace(go.Bar(x = self.porfolio['Date'], y = self.porfolio['Daily_Net_Pnl'],
                    name='Daily PnL'), row=3, col=1)
        
        figCharts.append_trace(go.Bar(x = self.portfolioDayWisePnl.index, y = self.portfolioDayWisePnl['Daily_Net_Pnl'],
                    name='Day wise total PnL'), row=4, col=1)
        
        bin_edges = np.arange(0, 100,5)
        
        
        figCharts.append_trace(go.Histogram(x= report[report['profit'] > 0]['MAE_%'], nbinsx=len(bin_edges)-1, xbins=dict(start=0, end=100), histnorm="percent"), row=5, col=1)
        figCharts.append_trace(go.Histogram(x= report[report['profit'] < 0]['MFE_%'], nbinsx=len(bin_edges)-1, xbins=dict(start=0, end=100), histnorm="percent"), row=6, col=1)

        figCharts.update_layout(title_text="Charts",autosize = True, height = 700*8)
        figCharts.update_xaxes(rangeslider=dict(visible=False)) 
        figCharts.show()
        
        #///////////////////////////////// MAE PERCENTAGE OCCURANCES ///////////////////
        
        """bin_edges = np.arange(0, 100,5)
        histogram_chart = go.Figure()
        
        # Add the histogram trace
        histogram_chart.add_trace(go.Histogram(x=report['MAE_%'], nbinsx=len(bin_edges)-1, xbins=dict(start=0, end=100), histnorm="percent"))
        # Update layout
        histogram_chart.update_layout(
            title='Distribution of maximum adverse excursion Percentages (Plotly)',
            xaxis_title='MAE Percentage (%)',
            yaxis_title='Number of Occurrences',
            xaxis=dict(tickvals = bin_edges, ticktext = [f'{val}%' for val in bin_edges])
        )
        #histogram_chart.show()
        
        histogram_chart = go.Figure()
        
        # Add the histogram trace
        histogram_chart.add_trace(go.Histogram(x=report['MFE_%'], nbinsx=len(bin_edges)-1, xbins=dict(start=0, end=100), histnorm="percent"))
        # Update layout
        histogram_chart.update_layout(
            title='Distribution of maximum favorable excursion Percentages (Plotly)',
            xaxis_title='MFE Percentage (%)',
            yaxis_title='Number of Occurrences',
            xaxis=dict(tickvals = bin_edges, ticktext = [f'{val}%' for val in bin_edges])
        )
        #histogram_chart.show()"""
        
        
        """ WRITE TO HTML """
        if toHtml :
            fig.write_html(htmlPath + "\\charts.html")
            figCharts.write_html(htmlPath + "\\graphs.html")
        
        
        return report, self.portfolioCum, self.portfolioMontly, self.portfolioYearly
        

             
             
             
        
        