from py_vollib.black_scholes import black_scholes as bs
from py_vollib.black_scholes.greeks.analytical import vega
import numpy as np
import mibian
import time
import math

def implied_vol(S0, K, T, r, market_price, flag='c', tol=0.00001):
    """Compute the implied volatility of a European Option
        S0: initial stock price
        K:  strike price
        T:  maturity
        r:  risk-free rate
        market_price: market observed price
        tol: user choosen tolerance
    """
    max_iter = 200 #max number of iterations
    vol_old = 0.30 #initial guess
    for k in range(max_iter):
        bs_price = bs(flag, S0, K, T, r, vol_old)
        Cprime =  vega(flag, S0, K, T, r, vol_old)*100
        C = bs_price - market_price
        if Cprime == 0:
            vol_new = (vol_old + 1.0) / 2.0
        else:
            vol_new = vol_old - C / Cprime
        bs_new = bs(flag, S0, K, T, r, vol_new)
        if (abs(vol_old - vol_new) < tol or abs(bs_new - market_price) < tol):
            break
        vol_old = vol_new
    implied_vol = vol_old
    return implied_vol


S0, K, T, r = 40606.00, 40300.00, 0.010958, 0.065
market_price = 300.000
#implied_vol_est = implied_vol(S0, K, T, r, market_price, flag='c')

start_time = time.time()
# Your for loop goes here
for i in range(1):
    SL = 57
    c = mibian.BS([39915, 39900, 6.5, 7], callPrice= 344)
    iv = c.impliedVolatility
    print(iv)
    c = mibian.BS([39915, 39900, 6.5, 7], volatility = iv)
    print(c.callDelta)
    
    SlDelta = SL * float(c.callDelta)
    
    print("SL without IV varaible : " + str(SlDelta))
    print("SL IV drop buffer : " + str(((c.vega / 100) * 25)))
    print("Final SL : " + str((SlDelta + ((c.vega / 100) * 25))))    
    
#mibian.BS([Underlying Price, Call / Price Strike Price, Interest Rate, Days To Expiration], Call / Put Price)
end_time = time.time()
time_taken = end_time - start_time
print(f"Time taken: {time_taken} seconds")



""" 
Get last three ITM strkes 

Find the first ITM strik which has above 55 delta

Find the SL value for strike which doesnt got affect by IV

Find the IV of previous Strike 

Find the epected IV drop percentage = (given_number / reference_number) * 100

Find the value of IV drop value = (percentage / 100) * total_value

Calculate the Value of the IV drop and add it to the delta to get the Final SL

"""


def getPositionsSizing(stoploss, ltp, risk_per_trade, lotSize) :
    # calculate risk per option
    noOfUnitsPossible = risk_per_trade / stoploss
    # calculate number of options
    position_size = (int(noOfUnitsPossible) // lotSize) * lotSize
    print("Position size:", position_size)
    return position_size

def getStrikePrice(ltp,CeOrPe, ItmOTmStrikeLevel = 1, optionStrikeInterval = 100) :
    rounded_ltp = round(ltp / 100) * 100
    strikeSelectionPoint = ItmOTmStrikeLevel * optionStrikeInterval

    if CeOrPe == "CE" :
        itm_strike_price = rounded_ltp + strikeSelectionPoint
    else :
        itm_strike_price = rounded_ltp - strikeSelectionPoint
        
    # if ItmOTmStrikeLevel < 0 :
        
    #     itm_strike_price = rounded_ltp + strikeSelectionPoint
    # else :
    #     itm_strike_price = rounded_ltp - strikeSelectionPoint

    print("Strike :", itm_strike_price)
    return itm_strike_price

getStrikePrice(41134,"CE", ItmOTmStrikeLevel = -5)

#getPositionsSizing(120, 334, 10000, 25)



#print("Implied Volatility is : ", round(implied_vol_est,2)*100, "%")


#print(implied_vol(40606, 40500, 0.010958, 0.065, 300)*100)