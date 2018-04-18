# -*- coding: utf-8 -*-
"""
Created on Tue Apr  3 21:00:17 2018

@author: ctr02
"""
'''
research material: look into Sage for programming
 - Stinson
 - Yenz
 References:
     Dr. Tim Gillespie
'''
import time
import numpy as np
import matplotlib.pyplot as plt # used for plotting points

start = time.time()

O = (0,0) # a point at infinity
q = 13381      # a prime number chosen p > k•m where m is a message number - Yans pg. 380
# 4a**3 + 27b**2 != 0 mod(q)
a = 3       # 2nd coefficient of elliptic curve
b = 1        # 3rd coefficient of elliptic curve

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

def addition(P, Q):
    '''
    performs pointwise addition on an elliptic curve
    
    Keyword arguments:
    P -- the first point to be added
    Q -- the second point to be added
    return pointwise addition of P and Q
    '''
    if P == O:
        # P + O - P = 0
        return Q
    elif Q == O:
        # O + Q - Q = 0
        return P
    elif (P[0] == Q[0]) and (P[1] == q-Q[1]):
        # P + -P + O = 0
        return O
    else:
        # P + Q + -R = 0
        # calculate m = (3x**2 + a) * (2y)**-1 if P == Q
        # else      m = (y2-y1) * (x2-x1)**-1
        m = (3 * P[0]**2 + a) * inv_mod_q(2*P[1]) if P == Q else (Q[1]-P[1]) * inv_mod_q(Q[0]-P[0])
        x = (m**2 - P[0] - Q[0]) % q
        y = (m * (P[0] - x) - P[1]) % q
        return (x,y)
    
def encrypt(x, k):
    #TODO
    return 0

def decrypt(y, k):
    #TODO
    return 0

def point_compression(x):
    #TODO
    return 0

def point_decompression(x, i):
    #TODO
    return 0
    
def plot_line(P, Q):
    '''
    y - y1 = m(x - x1)
    m = (y2-y1)/(x2-x1)
    '''
    R    = addition(P,Q)
    invR = (R[0],q-R[1])
    if not(P == Q):
        plt.annotate('Q',xy=Q,xytext=(Q[0]+.5,Q[1]+.5))
    plt.annotate('P', xy=P, xytext = (P[0]+.5,P[1]+.5))
    plt.annotate('R', xy=R, xytext = (R[0]+.5,R[1]+.5))
    plt.annotate('-R', xy=invR, xytext = (invR[0]+.5,invR[1]+.5))
    rise    = (3 * pow(P[0],2,q) + a)%q if P == Q else (Q[1]-P[1])%q
    run     = 2*P[1]%q if P == Q else (Q[0]-P[0])%q
    m = rise*inv_mod_q(run)%q
    L = list(map(lambda x:(x,(m*(x-P[0])+P[1])%q),np.arange(0,q-1,.001)))
    L = list(filter(lambda x:x[1]>q-.05,L))
    partitions = []
    for i in range(len(L)):
        if i == 0:
            x1 = 0
            x2 = L[0][0]
        elif i+1 == len(L):
            x1 = L[i][0]
            x2 = q-1
        else:
            x1 = L[i][0]
            x2 = L[i+1][0]
            i+=1
        partitions.append((x1,x2))
    partitions = list(filter(lambda x:x[1]-x[0]>.5,partitions))
    o = .05
    for i in partitions:
        L = list(map(lambda x:(x,(m*(x-P[0])+P[1])%q),np.arange(i[0]+o,i[1],.001)))
        plt.plot(*zip(*L),'r--',linewidth=.5,zorder=0)
    
def plot_labels():
    plt.xlabel('x')
    plt.ylabel('y')
    title = r'$y^{2}$ $\equiv$ $x^{3}$'
    title += '+{}x+{} mod({})'.format(a,b,q)
    plt.title(title)

def plot_ECC(data):
    plt.scatter(*data, s=7)
    plot_labels()
    plt.show()
    
    
start_E = time.time()
D =  list(filter(lambda x:x[1]>=0,map(lambda x:(x,modularSquareRoot(pow(x,3,q)+a*x+b)),range(q))))
D += list(filter(lambda x:x[1]>=0,map(lambda x:(x[0],q-x[1]),filter(lambda x:x[1] > 0,D))))
print('E point generation time {} seconds'.format(time.time()-start_E))
#with plt.xkcd():
#    scatman = zip(*D)
#    plot_ECC(scatman)
P = D[1]
Q = P
#scatman = zip(*D)
#with plt.xkcd():
#    plot_line(P, Q)
#    plot_ECC(scatman)
#print('initial plot with line')
cyclicP = [addition(P,Q)]
flag = True
start_addition = time.time()
while not(Q == cyclicP[0]):# or Q == O)):
    if flag:
        Q = addition(Q,P)
        flag = False
    else:
        cyclicP.append(Q)
#    if(not addition(Q,P) == O):
#        print('plotting {}+{}'.format(P,Q))
#        scatman = zip(*D)
#        with plt.xkcd():
#            plot_line(P, Q)
#            plot_ECC(scatman)
    Q = addition(Q,P)
    
print('addition time {} seconds'.format(time.time()-start_addition))
print('|<P>| = {}'.format(len(cyclicP)))
print('|D| = {}'.format(len(D)+1))
end = time.time()
print('Running Time: {} seconds'.format(end-start))