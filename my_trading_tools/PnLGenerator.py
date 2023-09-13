# -*- coding: utf-8 -*-
"""
Created on Thu Feb  2 20:18:04 2023

@author: Andy 

/////////////////////////////////
THIS PROGRAM IS TO Take all trades and generate a P/L report and Chart

"""
import pandas as pd
import random

path_orderbookfol = "G:\\andyvoid\\data\\my_orderbook"

trades = pd.read_csv(path_orderbookfol + "\\" + "02_02_2023.csv")
trades['Time'] = pd.to_datetime(trades['Time'], format="%Y-%m-%d %H:%M:%S")
trades.sort_values(by='Time', inplace=True)
trades['Qty.'] = trades['Qty.'].str.split('/').str[0].astype(int)
trades.reset_index(inplace= True)
trades.drop(['index'],axis=1, inplace= True)
print(trades)

#print(type(trades.Time[0]))

def getNewTradeId():
    return random.randint(100000,999999)

def generateProfitAndLoss(trades) : 
     lastTrade = None
     tradeLog = []
     trade = {}
     isNewTrade = False
     tradeId = getNewTradeId()
     
     for i,row in trades.iterrows() :
         orderType = row['Type']
         qty = row['Qty.']
         price = row['Avg. Price']
         
         if lastTrade == None : 
             lastTrade = orderType
             newTrade = True
             trade = {}
             
                
         
         if newTrade : 
             trade['Entry Time'] = row['Time']
             trade['Type'] = row['Type']
             trade['Instrument'] = row['Instrument']
             trade['tradeId'] = getNewTradeId()
             trade['Product'] = row['Product']
             trade['Entry Price'] = row['price']
             trade['qty'] = row['Qty.']
             
         if lastTrade != orderType : 
             if lastTrade == "SELL":
                 trade['Exit Time'] = row['Time']
                 trade['Exit Price'] = price
                 trade['Type'] = row['Type']
                 
                 

             
             
         tradeLog.append(trade)    

             
             


def profit_and_loss(trades):
    pnl = 0
    for trade in trades:
        # Calculate profit or loss for each trade
        # based on the trade type (buy or sell)
        if trade['Type'] == 'BUY':
            pnl -= trade['Avg. price'] * trade['Qty.']
        elif trade['Type'] == 'SELL':
            pnl += trade['Avg. price'] * trade['Qty.']
    return pnl



# # Example trades list
# trades = [
#     {'type': 'buy', 'price': 100, 'quantity': 10},
#     {'type': 'sell', 'price': 120, 'quantity': 10},
#     {'type': 'buy', 'price': 90, 'quantity': 5},
#     {'type': 'sell', 'price': 95, 'quantity': 5},
# ]

# # Calculate the profit and loss
# pnl = profit_and_loss(trades)

# print("Profit and Loss:", pnl)