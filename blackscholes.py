''' Using Newton-Raphson method to approximate implied vol using price.
    Newton-Raphson: x_{n+1} = x_{n} - f(x_{n})/f'(x_{n})
      f(x) in our case is Black-Scholes
      f'(x) is vega, the derivative of price with respect to volatility
    Our initial guess x_{0} is arbitrarily 0.10
'''

# Work in progress!

import math

# test values

ts = 10 # spot
tk = 12 # strike
tt = 2 # time to expiry
tq = 0 # dividend
tr = 0.05 # risk-free
tp = 1.9174 # price
# implied vol should be 0.4

# normal cdf

def cdf(n):
  '''calculates cdf in terms of error function
  '''
  return (1.0 + math.erf(n/(2.0**0.5)))/2.0

# Black-Scholes

def bs(v,s,k,q,r,t,call=True):
  '''Black-Scholes pricing model:
       s = spot
       k = strike
       v = volatility
       q = dividend
       r = risk-free rate
       t = time to expiry
       call = True if call, False if put
  '''  
  d1 = (math.log(s/k) + (r + (0.5)*v*v)*t)/(v*(t**0.5))
  d2 = d1 - v*(t**0.5)
  pvk = k * math.exp(-r*t)

  if call:
    return cdf(d1)*s*math.exp(-q*t) - cdf(d2)*pvk
  else:
    return cdf(-d2)*pvk - cdf(-d1)*s*math.exp(-q*t)

# print('Price:',bs(0.4,ts,tk,tq,tr,tt,True),tp)

# Vega

def bsvega(v,s,k,q,r,t):
  '''Calculates Vega according to Black-Scholes, see above
  '''
  d1 = (math.log(s/k) + (r + (0.5)*v*v)*t)/(v*(t**0.5))
  d2 = d1 - v*(t**0.5)

  return s*math.exp(-q*t)*cdf(d1)*(t**0.5)

# print('Vega:',bsvega(0.4,ts,tk,tq,tr,tt))

# Newton-Raphson

def nr(fx,fpx,x0 = 0.1,e = 0.00001,args = ()):
  '''Implements Newton-Raphson method
       fx = f(x)
       fpx = f'(x)
       x0 = initial guess
       e = error term
       args = other required arguments

     x0 must be the first argument of the function!
  '''
  new_result = x0 - fx(*((x0,)+args))/fpx(*((x0,)+args))

  print(new_result)

  if abs(x0 - new_result) > e:
    return nr(fx,fpx,new_result,e,args)
  else:
    return new_result

# integrating Black-Scholes with Newton-Raphson

def bsvol(v,s,k,q,r,t,p):
  '''first order Taylor polynomial of f(vol)
       where f(vol) is the Black-Scholes function with regard to volatility
       and f'(vol) is Black Scholes vega
  '''
  return (p - bs(v,s,k,q,r,t) + bsvega(v,s,k,q,r,t)*v)/bsvega(v,s,k,q,r,t)
  
def nrtest(fx,x0 = 0.1,e = 0.0001,counter = 0,args = ()):
  '''modified newton-raphson method for the bsvol() function above
     uses the first order Taylor series
       x_{n+1} = (f(x_{n+1}) - f(x_n) + f'(x_n)*x_n)/f'(x_n)
     which should eventually converge
       fx = function that it takes
       x0 = initial guess
       e = error term
       counter = tracks recursion, keeps it from going too long
       args = other required arguments

     x0 must be the first argument of the function!
  '''
  new_result = fx(*(x0,) + args)
  print(new_result)
  if abs(x0 - new_result) > e and counter < 1000:
    return nrtest(fx,new_result,e,counter+1,args)
  elif counter > 1000:
    raise Exception("Doesn't converge within 1000 steps!")
  else:
    return new_result
  
# print('Newton-Raphson Test:',nrtest(bsvol,0.1,0.0001,0,(ts,tk,tq,tr,tt,tp)))