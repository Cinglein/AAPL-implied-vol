See detailed writeup at https://options.cinglein.com/aaplvol.html

aaplvol.py is what I used for the old dataset; it's only there for historical purposes, and no longer works.

aaplvol2.py is how I analyze CBOE's eod option data, which uses Black-Scholes. It gathers data for each option according to the moneyness; currently it is set only to gather data for at-the-money options. 

blackscholes.py contains my Black-Scholes model, as well as the function "nrtest", which is an implementation of the Newton-Raphson method to approximate implied volatility.

aaplvol3.py is the third iteration of the project, which uses the Cox-Ross-Rubenstein model instead. 

american.py is my implementation of Cox-Ross-Rubenstein, and uses Oliveira and Takahashi's new (Dec 2020) method for root-finding (interpolation, truncation, projection).
