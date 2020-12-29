See detailed writeup at https://options.cinglein.com/aaplvol.html

aaplvol.py is what I used for the old dataset; it's only there for historical purposes, and no longer works.

aaplvol2.py is what I am currently using for CBOE's eod option data. It gathers data for each option according to the moneyness; currently it is set only to gather data for at-the-money options. 

blackscholes.py contains my Black-Scholes model, as well as the function "nrtest", which is an implementation of the Newton-Raphson method to approximate implied volatility.
