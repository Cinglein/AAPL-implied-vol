# Version 2 of implied volatility calculator, for the CBOE dataset

import math, numpy as np, pandas as pd, blackscholes as bs, datetime as dt, matplotlib, os, time, pandas_market_calendars as mcal
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

# CBOE Option/Underlying Data

'''DataFrame structured as:
     Columns: 0 = option price, 1 = underlying price, 2 = placeholder,
              3 = time to expiration in days
     Row Index: (quote date YYYY-MM-DD, expiration YYYY-MM-DD, strike, Call/Put)
'''

aapl = dict()

# currently set up to find ATM options only

if input('Pull new options data from CBOE CSV? (y/n)\n') == 'y':
  cpflag = input('Do you want to look at calls or puts? (c/p)\n').capitalize()
  print('Getting option/underlying price data...')
  for dirName, subdirList,fileList in tqdm(os.walk('eod-options')):
    if fileList != []:
      df = pd.read_csv(dirName + '/' + fileList[0]).set_index(['quote_date','expiration','strike','option_type'])
      for index in df.index:
        if index[3] == cpflag and abs(index[2] - (df['underlying_bid_eod'][index] + df['underlying_ask_eod'][index])/2) < 1:
          aapl[index] = [(df['bid_eod'][index] + df['ask_eod'][index])/2, 
                         (df['underlying_bid_eod'][index] + df['underlying_ask_eod'][index])/2,
                         0,
                         len(nyse.valid_days(start_date=index[0],end_date=index[1]).date)]
  aapl = pd.DataFrame(aapl).transpose()
  aapl.to_csv('aapl.csv')
  print(aapl)
else:
  aapl = pd.read_csv('aapl.csv').set_index(['Unnamed: 0','Unnamed: 1','Unnamed: 2','Unnamed: 3'])
  cpflag = aapl.index[0][2]

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
rfr = pd.read_csv('FRB_H15.csv').set_index('Date').fillna(method='pad')

# Implied Volatility Calculations

print('Computing implied volatility...')
bsvol = np.array([]) # implied volatility
bsm = np.array([]) # spot/strike
bsu = np.array([]) # underlying price
bsk = np.array([]) # strike
bst = np.array([]) # time to expiration
starttime = time.time()

badapples = 0

for i, row in tqdm(aapl.iterrows()):
  try:
    bsvol = np.append(arr=bsvol,values=bs.nrtest(bs.bsvol,1,0.001,(row[1],i[2],
                      (1+(aapldiv['Amount'][str(3*(int(i[0].split('-')[1])//4)+2),i[0].split('-')[0]]/row[1]))**4 - 1,
                      float(rfr['Rate'][i[0]])*0.01,
                      row[3]/252,row[0],i[3] == 'C')))
    bsm = np.append(arr=bsm,values=math.log(row[1]/i[2]))
    bsu = np.append(arr=bsu,values=row[1])
    bsk = np.append(arr=bsk,values=i[2])
    bst = np.append(arr=bst,values=row[3])
  except:
    badapples += 1
  # aapldiv['Amount'][str(3*(int(i[0].split('-')[1])//4)+2),i[0].split('-')[0]]

computetime = time.time() - starttime
print('Time taken to compute implied volatility:',computetime,'s')
print(badapples)

# Graphing

print('Graphing...')


pd.DataFrame({'Implied Vol':bsvol,'ln(spot/strike)':bsm,'Underlying Price':bsu}).plot.scatter(x='ln(spot/strike)',y='Implied Vol',c='Underlying Price',colormap='viridis')
matplotlib.pyplot.savefig('aaplvol-atm1.png')
pd.DataFrame({'Implied Vol':bsvol,'time to expiry':bst,'Underlying Price':bsu}).plot.scatter(x='time to expiry',y='Implied Vol',c='Underlying Price',colormap='viridis')
matplotlib.pyplot.savefig('aaplvol-atm2.png')

'''
x = np.array([])
y = np.array([])
z = np.array([])

for i in range(999):
  x = np.append(arr=x,values=bst[math.floor(np.random.random()*len(bst))])
  y = np.append(arr=y,values=bsm[math.floor(np.random.random()*len(bsm))])
  z = np.append(arr=z,values=bsvol[math.floor(np.random.random()*len(bsvol))])

print(len(x),len(y),len(z))


X, Y = np.meshgrid(x,y)
Z = z

fig = plt.figure()
ax = plt.axes(projection='3d')
ax.plot_trisurf(X, Y, Z,cmap='viridis', edgecolor='none')
ax.set_xlabel('Time to Expiration')
ax.set_ylabel('Spot/Strike')
ax.set_zlabel('Implied Volatility')
plt.title('AAPL Calls 2018-09-04 to 2018-11-30')
plt.savefig('aaplvol3d.png')
'''

# End of Program

print('Done!')
