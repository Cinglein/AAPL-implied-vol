import numpy as np, time

'''Implementation of the Cox-Ross-Rubinsten model
   for binomial pricing of options, optimized with Brent's method

'''

# test values

ts = 10 # spot
tk = 12 # strike
tt = 504 # time to expiry
tq = 0 # dividend
tr = 0.05 # risk-free
tp = 1.9174 # price
# implied vol should be 0.4

def crr(v,n,s,k,q,r,t):
  '''Cox-Ross-Rubenstein Model
       v = volatility
       n = max number of steps
       s = spot
       k = strike
       q = dividend (in dollars)
       r = interest rate (as a decimal)
       t = time until expiry (in days)
       call = True if call, False if put
  '''
  u = np.exp(v*((t/252)/n)**0.5)
  d = 1/max(u,0.0000001)
  rhat = (r+1)**((t/252)/n)
  p = (rhat-d)/max(u-d,0.0000001)
  # print(u,d,rhat,p)

  return crrprice(crrtree(u,d,n,s),k,q,rhat,t,n,p)

def cantor(l,r):
  '''cantor pairing function
       l = number of left branches
       r = number of right branches
  '''
  return 0.5 * (l+r) * (l+r+1) + r

def inv_cantor(z,left=True):
  '''inverse cantor pairing function
       z = value of cantor(l,r)
       left = True if left, False if right
     left is y-coordinate, right is x-coordinate
  '''
  w = ((8*z+1)**0.5 - 1)//2
  t = (w*w + w)/2
  if left:
    return z - t
  else:
    return w - z + t

def crrgen(i,u,d,s):
  '''function for value of tree node, where value = price of underlying
       u^L * d^R * s
  '''
  return u**inv_cantor(i,True) * d**inv_cantor(i,False) * s

def crrtree(u,d,n,s):
  '''makes a binomial tree for the price of the underlying
  '''
  tree = np.fromfunction(crrgen,(int(0.5*n*(n+1)),),dtype=float,u=u,d=d,s=s)
  # print(tree,len(tree))
  return tree

def crrprice(tree,k,q,rhat,t,n,p,i=1,j=0):
  '''works backward through the tree to find the price at i = 0
  '''
  div = (1-(q/tree[j]))**((t*((n-i)/n))//62.5)
  # print(tree[j] - k)
  if i == n:
    return max(0,div*tree[j]-k)
  else:
    return max(div*tree[j]-k,
               (p*crrprice(tree,k,q,rhat,t,n,p,i+1,j+i+1) + 
                (1-p)*crrprice(tree,k,q,rhat,t,n,p,i+1,j+i))
               /rhat)

def oliveira_takahashi(f,n0,a0,b0,e=0.001,args=()):
  '''Implements the Oliveira-Takahashi root-finding method
     to find the implied volatility, given the price, using
     and ITP (Interpolation, Truncation, Projection) strategy:
       a = the value a of the starting interval [a,b]
       b = the value b of the starting interval [a,b]
       e = error term, 0 < e
       n0 = , 0 <= n0
       f = the function that we are testing
  '''
  # starting constants
  g = lambda x: f(*(x,) + args) - n0
  a = a0
  b = b0
  ya = g(a)
  yb = g(b)
  n_half = np.ceil(np.log2( (b-a)/(2*e) ))
  n_max = n0 + n_half
  k = 0
  k1 = 0.1
  k2 = 2.5656733 # roughly 0.98*(1 + golden ratio)

  while b - a > 2 * e and k < 35:
    # interpolation
    x_f = (yb * a - ya * b)/(yb - ya)

    # truncation
    x_half = (a+b)/2
    sigma = np.sign(x_half - x_f)
    delta = k1 * abs(b-a)**k2

    if delta <= abs(x_half - x_f):
      x_t = x_f + sigma*delta
    else:
      x_t = x_half

    # projection
    r = e * 2**(n_max - k) - (b-a)/2
    if abs(x_t - x_half) <= r:
      x_guess = x_t
    else:
      x_guess = x_half - sigma*delta

    # updating
    y_guess = g(x_guess)
    if y_guess > 0:
      b = x_guess
      yb = y_guess
    elif y_guess < 0:
      a = x_guess
      ya = y_guess
    else:
      a = x_guess
      b = x_guess
    k += 1
    # print(k,a,b)

  out = ((a+b)/2)
  if a0 < out < b0:
    return (out,k)
  else: 
    return (0.,k)
    

# test

'''
mytime = time.time()
print("value",oliveira_takahashi(crr,1.9,0.3,0.5,e=0.0001,args=(15,ts,tk,tq,tr,tt)))
print("time",time.time()-mytime)
'''