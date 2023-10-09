"""
Created on Wed Aug 22 15:15:17 2022

###########################################
### 920 STRADLE BACKTESTING BNF  ##########
###########################################


@author: AndyAlves
"""
#%%
import pandas as pd
import talib as ta
import datetime as dt
from tqdm import tqdm
import math
from backtesting import Backtesting as bt
import traceback
import logging
from backtesting import LocalCsvDatabase as csv_database
from backtesting import Backtesting
from backtesting import StrategyArsenal as sa
import Utils
#%%
# Variables
tf_1Min = "1Min"
tf_5Min = "5Min"
tf_15Min = "15Min"
tf_1H = "H"
tf_1D = "1D"
strTimeformat = "%Y/%m/%d - %H:%M:%S"

#start_date = '2017-01'
#end_date = '2023-08'
start_date = '2022-01'
end_date = '2023-08'
O = "Open"
H = "High"
L = "Low"
C = "Close"
bnf_op_path = "G:\\andyvoid\data\quotes\After_cleaned\Banknifty\BNF_options"


#%%

bnfResampled = csv_database.get_banknifty_data(start_date, end_date, tf_5Min)

#%%
help(ta.supertrend)
bnfResampled = bnfResampled.ta.supertrend(length = 14)
bnfResampled['atr'].fillna(method = 'bfill', inplace = True)
bnfResampled['atr_multiplied'] = bnfResampled['atr'] * 3