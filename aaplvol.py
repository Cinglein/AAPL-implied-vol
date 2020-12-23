import math, numpy as np, pandas as pd, blackscholes as bs, datetime, matplotlib
from iexfinance.stocks import Stock, get_historical_data

# Getting the data 

'''We want to calculate implied volatility. For this we need:
     1. Option prices and dates (we have a csv)
     2. Underlying prices, dividends, and dates (IEX calls)
     3. Risk-Free Rate (IEX calls)
'''

# Getting IEX data

iex_price = None
iex_dividends = None
iexq = None

if input('Get new data from IEX? (y/n)\n') == 'y':
  iex_sk = input('What is your IEX token?')

  start = datetime.datetime(2020,10,30) # the range of the csv I'm using
  end = datetime.datetime(2020,12,8)

  iex_price = get_historical_data('AAPL', start, end, output_format='pandas',token=iex_sk)
  iex_price.to_csv('iexprice.csv')
  iex_dividends = Stock('AAPL',token=iex_sk).get_dividends() # the most recent dividend works for my date range
  iex_dividends.to_csv('iexdividends.csv')
  print('Data retrieved.')
else:
  print('Using existing IEX data...')
  iex_price = pd.read_csv('iexprice.csv')
  iex_dividends = pd.read_csv('iexdividends.csv')
  print('Files opened.')

iexq = iex_dividends['amount'][0]

# Getting T-Bill data

tbills = pd.read_csv('tbills.csv').set_index('DATE') # from the Treasury.gov website

# Pulling options data from the CSV

dtp = None

if input('Pull new options data from CSV? (y/n)\n') == 'y':
  df = pd.read_csv('aaplvol.csv',low_memory=False)
  print('file opened...')
  datetime = df['Date-Time'].apply(pd.Timestamp)
  price = (df['Bid Price'] + df['Ask Price'])/2 # we assume the fair price is the midpoint
  dtp = pd.DataFrame({'Date-Time':datetime.apply(pd.Timestamp),'Price':price})
  print('dataframe formatted...')
  dtp = dtp.set_index('Date-Time').resample('6h').mean().dropna()
  dtp.to_csv('dtp.csv')
  print('index set and dates resampled. file saved.')
else:
  dtp = pd.read_csv('dtp.csv').set_index('Date-Time')

# Calculating with Black-Scholes

bsout = []
dateout = []

for open, close, date in zip(iex_price['open'],iex_price['close'],iex_price['Unnamed: 0']):
  dateout += [date,date]
  bsout += [bs.nrtest(bs.bsvol,0.1,0.0001,(open,60,iexq,
          0.01*tbills['4 WEEKS BANK DISCOUNT'].get(date,0.07),
          ((datetime.datetime(2020,12,11) - datetime.datetime.strptime(date,'%Y-%m-%d')).days/365),
          30+dtp['Price'][date+' 12:00:00+00:00'])), bs.nrtest(bs.bsvol,0.1,0.0001,(close,60,iexq,
          0.01*tbills['4 WEEKS BANK DISCOUNT'].get(date,0.07),
          ((datetime.datetime(2020,12,11) - datetime.datetime.strptime(date,'%Y-%m-%d')).days/365),
          30+dtp['Price'][date+' 18:00:00+00:00']))]
  # it's 30 + option price, because the dataset I got doesn't work with Black-Scholes :(
  # basically, the option prices are too low, so Black-Scholes can't get there no matter what volatility is used

# Drawing graphs

pd.DataFrame({'Implied Volatility':bsout,'Date':dateout}).set_index('Date').plot()
matplotlib.pyplot.savefig('aaplvol.png')
dtp.plot()
matplotlib.pyplot.savefig('dtp.png')
