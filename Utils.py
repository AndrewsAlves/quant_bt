# -*- coding: utf-8 -*-
import datetime as dt
from Utilities import StaticVariables as statics

def Cumulative(lists):
    cu_list = []
    length = len(lists)
    cu_list = [sum(lists[0:x:1]) for x in range(0, length+1)]
    roundedCu = [ round(i) for i in cu_list[1:] ]
    return roundedCu

def CumulativeCapital(lists, capital):
    cu_list = []
    length = len(lists)
    cu_list = [capital + sum(lists[0:x:1]) for x in range(0, length+1)]
    roundedCu = [ round(i) for i in cu_list[1:] ]
    return roundedCu

def getChangePercent(current, previous):
    """ To calcualte the percentage of capital vs total return """
    if current == previous:
        return 0
    try:
        return (abs(current - previous) / previous) * 100.0
    except ZeroDivisionError:
        return float('inf')
    
def CAGR(start, end, periods):
    return ((end/start)**(1/periods)-1) * 100.0

def calculateRunningDrawdown(cum_profit) : 
    # We are going to use a trailing 252 trading day window
    window = 252
    # Calculate the max drawdown in the past window days for each day in the series.
    # Use min_periods=1 if you want to let the first 252 days data have an expanding window
    Roll_Max = cum_profit.rolling(window, min_periods=1).max()
    Daily_Drawdown = (cum_profit/Roll_Max - 1.0)
    
    
    # Next we calculate the minimum (negative) daily drawdown in that window.
    # Again, use min_periods=1 if you want to allow the expanding window
    Max_Daily_Drawdown = Daily_Drawdown.rolling(window, min_periods=1).min()
    
    #Daily_Drawdown.plot()
    #Max_Daily_Drawdown.plot()
    #pp.show()
    
    return Daily_Drawdown * 100

def getWin_LoseRate(tBook) :
    wins = tBook[tBook['profit'] > 0]
    loss = tBook[tBook['profit'] < 0]
    neutral = tBook[tBook['profit'] == 0]
    return [wins.shape[0], loss.shape[0], neutral.shape[0]]

def calculateProfitFactor(tBook) : 
    wins = tBook['profit'].loc[tBook['profit'] > 0].sum()
    loss = tBook['profit'].loc[tBook['profit'] < 0].sum()
    return wins / abs(loss)


def getPriceDataFromDataframe(df, datetime, ohlc) :
    ltp = 0
    try : 
        ltp = df.loc(axis = 0)[datetime, ohlc]
        return ltp
    except :
        raise Exception("Price Data not found " + df['Ticker'].iloc[0] + " " + datetime + " " + ohlc)

def getPositionsSizing(stoplossPoints, risk_per_trade, lotSize, debug = True) :

    if debug :
        # min lot size to test 
        return lotSize
    # calculate risk per option
    if stoplossPoints == 0 :
        return 0

    noOfUnitsPossible = risk_per_trade / stoplossPoints
    # calculate number of options
    position_size = (int(noOfUnitsPossible) // lotSize) * lotSize

    if position_size > 800: position_size = 800

    #print("Position size:", position_size)
    return position_size

def getPositionsSizingForSelling(stoplossPoints, risk_per_trade, lotSize, marginPerLot = 100000, capital = 100000, capitalCap = True, debug = True) :

    maxPosPosible = (capital / marginPerLot) * lotSize
    maxPosPosible = (int(maxPosPosible) // lotSize) * lotSize
    
    if debug :
        # min lot size to test 
        return lotSize
    # calculate risk per option
    if stoplossPoints == 0 :
        return 0

    noOfUnitsPossible = risk_per_trade / stoplossPoints
    # calculate number of options
    position_size = (int(noOfUnitsPossible) // lotSize) * lotSize
    
    if not capitalCap : return position_size

    if position_size > maxPosPosible: position_size = maxPosPosible

    #print("Position size:", position_size)
    return position_size

def convertPositionSizing(stgTradeBook,symbol, totalCapital = 1000000, hedged = False, capitalCap = True) :
    
    ## Margin Nifty 145000 / 50 lot size
    ## Margin banknifty 110500 - 15 LS / 141000 - 25LS
    ## Margin finnifty 132577
    
    if (symbol == statics.NIFTY) :
        lotSize = 50
        straddleMarginPerLot = 145000
        if (hedged) : 
            straddleMarginPerLot = 65414
    elif (symbol == statics.BANKNIFTY) :
        lotSize = 25
        straddleMarginPerLot = 141000
        if (hedged) : 
            straddleMarginPerLot = 65414
    elif (symbol == statics.FINNIFTY) :
        lotSize = 40
        straddleMarginPerLot = 132577
        if (hedged) : 
            straddleMarginPerLot = 51778
        
    capital = totalCapital
    riskPerTrade = 1
    stg = stgTradeBook
    entryTime = 0;
    qty = 0;
    
    circularBanknifty = dt.datetime(2023,7,1)
    
    for index, row in stg.iterrows(): 
        
        if symbol == statics.BANKNIFTY and dt.datetime.strptime(row['Entry Time'],'%Y-%m-%d %H:%M:%S') >= circularBanknifty and lotSize != 15: 
              print("Changed lot size")
              lotSize = 15
              straddleMarginPerLot = 110500
              if (hedged) : 
                  straddleMarginPerLot = 39249
        
        if (entryTime != row['Entry Time']):  
            entryTime = row['Entry Time']
            slPoints = round(row['SL price'] - row['Entry Price'],2)
            qty = getPositionsSizingForSelling(abs(slPoints), ((capital / 100) * riskPerTrade),
                                                lotSize,
                                                straddleMarginPerLot,
                                                capital,
                                                capitalCap,
                                                False)
        stg.at[index,'quantity'] = qty
        stg.at[index,'profit'] = (row['Entry Price'] - row['Exit Price']) * qty
        stg.at[index,'MAE Pnl'] = (row['Entry Price'] - row['MAE Price']) * qty
        stg.at[index,'MFE Pnl'] = (row['Entry Price'] - row['MFE Price']) * qty