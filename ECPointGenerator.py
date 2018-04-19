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
    finds the square root of a number, a mod q
    
    Keyword arguments:
    a -- the number to find the square root of
    returns -1 if there is no square root of a in Z_q
    '''
    for i in range(int((q+1)/2)):
        if (pow(i,2,q) == a % q):
            return i
    return -1

start_E = time.time()
D =  list(filter(lambda x:x[1]>=0,map(lambda x:(x,modularSquareRoot(pow(x,3,q)+a*x+b)),range(q))))
D += list(filter(lambda x:x[1]>=0,map(lambda x:(x[0],q-x[1]),filter(lambda x:x[1] > 0,D))))
print('E point generation time {} seconds'.format(time.time()-start_E))

f = './Curves/ECPoints_{}_{}_{}.csv'.format(q,a,b)

electromagneticpulse.savetxt(f, D, delimiter=',', fmt='%d')