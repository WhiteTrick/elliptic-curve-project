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
q = 3276803      # a prime number chosen p > k•m where m is a message number - Yans pg. 380
# 4a**3 + 27b**2 != 0 mod(q)
a = 5       # 2nd coefficient of elliptic curve
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

def quadratic_residue(a):
    '''
    finds quadratic residue of a mod p
    using tonelli-shanks algorithm
    
    Keyword arguments:
    a -- the number to find the quadratic residue of
    returns -1 if a is a non-quadratic residue mod p
        otherwise returns the quadratic residue mod p
    from https://eli.thegreenplace.net/2009/03/07/computing-modular-square-roots-in-python
    '''
    if a%q == 0:
        return 0
    if legendre_symbol(a) < 0:
        return -1
    elif a == 0:
        return 0
#    elif a == 1:
#        return 1
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
            return x if x != 0 else -1
        gs = pow(g, 2**(r-m-1), q)
        g = (gs*gs)%q
        x = (x*gs)%q
        b = (b*g)%q
        r = m

def legendre_symbol(a):
    '''
    The Legendre Symbol
    '''
    ls = pow(a, int((q-1)/2), q)
    return -1 if ls == q-1 else ls

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
    title += '+{}x+{} (mod{})'.format(a,b,q)
    plt.title(title)

def plot_ECC(data):
    size = plt.rcParams['figure.figsize']
    size[0] = 12
    size[1] = 8
    plt.scatter(*data, s=12)
#    plt.axis('off')
#    plt.grid(False)
    plot_labels()
    plt.show()
    
    
start_E = time.time()
D1 =  list(filter(lambda x:x[1]!=-1,map(lambda x:(x,quadratic_residue(pow(x,3,q)+a*x+b)),range(q))))
lenD = len(D1)
print(lenD)
C = list(map(lambda x:(x[0],q-x[1]),filter(lambda x:x[1] > 0,D1)))
D = D1+C

print(len(D)-lenD)
print(len(D))
print('E point generation time {} seconds'.format(time.time()-start_E))
#with plt.xkcd():
#scatman = zip(*D)
#plot_ECC(scatman)
i=0
print('i: {} P: {}'.format(i, D[i]))
P = D[i]
Q = P
#scatman = zip(*D)
#with plt.xkcd():
#    plot_line(P, Q)
#    plot_ECC(scatman)
#print('initial plot with line')
#cyclicP = [O]#addition(P,Q)]

start_addition = time.time()
while not(Q == O):#cyclicP[):
    if flag:
        Q = addition(Q,P)
        flag = False
    else:
        cyclicP.append(Q)
    cyclicP.append(Q)
    if(not addition(Q,P) == O):
        print('plotting {}+{}'.format(P,Q))
        scatman = zip(*D)
        with plt.xkcd():
            plot_line(P, Q)
            plot_ECC(scatman)
    Q = addition(Q,P)
    
#    print('addition time {} seconds'.format(time.time()-start_addition))
#    print('|<P>| = {}'.format(len(cyclicP)))
#    print('|{{<P>}}| = {}'.format(len(set(cyclicP))))
#    print('|D| = {}'.format(len(D)+1))
#    print('|{{D}}| = {}'.format(len(set(D))))
end = time.time()
print('Running Time: {} seconds'.format(end-start))