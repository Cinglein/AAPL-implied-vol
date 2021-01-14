# Version 3 of implied volatility calculator, for the CBOE dataset

'''This uses the Cox-Ross-Rubenstein model, 
   unlike Version 2, which used Black-Scholes
'''

import math, numpy as np, pandas as pd, american as am, datetime as dt, matplotlib, os, time, pandas_market_calendars as mcal
from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
from tqdm import tqdm

'''We need three sets of data:
     1. AAPL Option Price and Underlying Price
        (in CBOE CSVs sorted by day, from 2018-09-04 to 2018-11-30)
     2. AAPL Dividend
        (in CSV made from Seeking Alpha data, dividends sorted by quarter)
     3. Risk-Free Rate
        (4-week T-Bills in Federal Reserve CSV, sorted by day from 2015 to 2020)
'''

# Setting up a calendar

nyse = mcal.get_calendar('NYSE')

# AAPL Dividend Data

'''DataFrame structured as:
     Columns: Amount = dividend amount
     Row Index: [Month, Day, Year]
'''

print('Getting dividend data...')
aapldiv = pd.read_csv('aapl-dividends.csv')
aapldiv['Pay Date'] = aapldiv['Pay Date'].apply(lambda a: tuple(a.split('-')[::2]))
aapldiv = aapldiv.set_index('Pay Date')

# Risk-Free Rate Data

'''DataFrame structured as:
     Columns: Rate = interest rate for 4-week T-Bill
     Row Index: Date in YYYY-MM-DD
'''

print('Getting risk-free rate data...')
rfr = pd.read_csv('FRB_H15.csv').set_index('Date').fillna(method='pad').applymap(lambda x: x*0.01)

# CBOE Option/Underlying Data

'''DataFrame structured as:
     Columns: 0 = option price, 1 = underlying price, 2 = strike, 3 = dividend, 
              4 = risk-free rate, 5 = time to expiration in days
     Row Index: (quote date YYYY-MM-DD, expiration YYYY-MM-DD, strike, Call/Put)
'''

aapl = dict()

'''Change moneyness to change the range of options we will look at, with 0 being atm
      0 = at the money
      10 = +/- $10
      50 = +/- $50
      ...etc
'''
moneyness = 10000

if input('Pull new options data from CBOE CSV? (y/n)\n') == 'y':
  cpflag = input('Do you want to look at calls or puts? (c/p)\n').capitalize()
  print('Getting option/underlying price data...')
  for dirName, subdirList,fileList in tqdm(os.walk('eod-options')):
    if fileList != []:
      df = pd.read_csv(dirName + '/' + fileList[0]).set_index(['quote_date','expiration','strike','option_type'])
      for index in df.index:
        if index[3] == cpflag and abs(index[2] - (df['underlying_bid_eod'][index] + df['underlying_ask_eod'][index])/2) < moneyness:
          aapl[index] = [(df['bid_eod'][index] + df['ask_eod'][index])/2, 
                         (df['underlying_bid_eod'][index] + df['underlying_ask_eod'][index])/2,
                         index[2],
                         aapldiv['Amount'][ str( 3*(int( index[0].split('-')[1] )//4)+2 ),index[0].split('-')[0] ],
                         rfr['Rate'][index[0]],
                         len(nyse.valid_days(start_date=index[0],end_date=index[1]).date),
                         np.log(((df['underlying_bid_eod'][index] + df['underlying_ask_eod'][index])/2)/index[2])]
  aapl = pd.DataFrame(aapl).transpose()
  aapl.to_csv('aapl.csv')
  print(aapl)
else:
  aapl = pd.read_csv('aapl.csv').set_index(['Unnamed: 0','Unnamed: 1','Unnamed: 2','Unnamed: 3'])
  cpflag = aapl.index[0][2]

# Implied Volatility Calculations

print('Computing implied volatility...')
starttime = time.time()

crrmap = lambda x: am.oliveira_takahashi(am.crr,tuple(x)[0],0,3,e=0.0001,args=(10,) + tuple(x)[1:-1])

testy = lambda y: print(y)

crr_iv = pd.DataFrame(aapl.apply(crrmap,result_type='reduce',raw=False,axis=1).tolist())

print("crr iv\n",crr_iv[0].describe(),"\nsteps\n",crr_iv[1].describe())

computetime = time.time() - starttime
print('Time taken to compute implied volatility:',computetime)

# Graphing

print('Graphing...')

av = 0.05

aapl = aapl.reset_index()


pd.DataFrame({'Implied Vol':crr_iv[0],'ln(spot/strike)':aapl[6],'Underlying Price':aapl[1]}).plot.scatter(x='ln(spot/strike)',y='Implied Vol',c='Underlying Price',alpha=av,colormap='viridis')
matplotlib.pyplot.savefig('aaplvol-crr-mega-2d1.png')
pd.DataFrame({'Implied Vol':crr_iv[0],'time to expiry':aapl[5],'Underlying Price':aapl[1]}).plot.scatter(x='time to expiry',y='Implied Vol',c='Underlying Price',alpha=av,colormap='viridis')
matplotlib.pyplot.savefig('aaplvol-crr-mega-2d2.png')

fig = plt.figure()
ax = plt.axes(projection='3d')
ax.plot_trisurf(aapl[5], aapl[6], crr_iv[0], cmap='viridis', edgecolor='none', linewidth = 0, antialiased=True)
ax.set_xlabel('Time to Expiration')
ax.set_ylabel('ln(Spot/Strike)')
ax.set_zlabel('Implied Volatility')
plt.title('AAPL ATM Calls 2018-09-04 to 2018-11-30')
plt.savefig('aaplvol-crr-mega-3d.png')



# End of Program

print('Done!')
