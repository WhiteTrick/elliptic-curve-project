# -*- coding: utf-8 -*-
"""
Created on Mon Apr 16 11:19:01 2018

@author: ctr02
"""

import time
import numpy as electromagneticpulse

start = time.time()

O = (0,0) # a point at infinity
q = int(input('Enter prime number p: '))#12911      # a prime number chosen p > 30•m where m is a message number - Yans pg. 380
# 4a**3 + 27b**2 != 0 mod(q)
a = int(input('Enter integer a: '))#3       # 2nd coefficient of elliptic curve
b = int(input('Enter integer b: '))#1        # 3rd coefficient of elliptic curve

def inv_mod_q(a):
    '''
    finds the multiplicative inverse of a number, a mod q
    
    Keyword arguments:
    a -- the number to find the multiplicative inverse of
    raises ZeroDivisionError if a is equivalent to 0 mod q
    '''
    if a % q == 0:
        print('impossible inverse: {}'.format(a))
        raise ZeroDivisionError('Impossible Inverse')
    return pow(a,q-2,q)

def modularSquareRoot(a):
    '''
    finds quadratic residue of a mod p
    using tonelli-shanks algorithm
    
    Keyword arguments:
    a -- the number to find the quadratic residue of
    returns -1 if a is a non-quadratic residue mod p
        otherwise returns the quadratic residue mod p
    from https://eli.thegreenplace.net/2009/03/07/computing-modular-square-roots-in-python
    '''
    if legendre_symbol(a) == -1:
        return -1
    elif a%q == 0:
        return 0
    elif q == 0:
        return a
    elif q % 4 == 3:
        return pow(a, int((q+1)/4), q)
    
    s = q-1
    e = 0
    while s%2 == 0:
        s/=2
        e+=1
    n = 2
    while legendre_symbol(n) != -1:
        n+=1
    x = pow(a, int((s+1)/2),q)
    b = pow(a, int(s), q)
    g = pow(n, int(s), q)
    r = e
    while True:
        t = b
        m = 0
        for m in range(r):
            if t == 1:
                break
            t = pow(t, 2, q)
        if m == 0:
            return x if x > 0 else -1
        gs = pow(g, 2**(r-m-1), q)
        g = (gs*gs)%q
        x = (x*gs)%q
        b = (b*g)%q
        r = m

def legendre_symbol(a):
    ls = pow(a, int((q-1)/2), q)
    return -1 if ls == q-1 else ls

start_E = time.time()
D =  list(filter(lambda x:x[1]>=0,map(lambda x:(x,modularSquareRoot(pow(x,3,q)+a*x+b)),range(q))))
D += list(map(lambda x:(x[0],q-x[1]),filter(lambda x:x[1] > 0,D)))
print('E point generation time {} seconds'.format(time.time()-start_E))

f = './Curves/ECPoints_{}_{}_{}.csv'.format(q,a,b)

electromagneticpulse.savetxt(f, D, delimiter=',', fmt='%d')