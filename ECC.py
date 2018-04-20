# -*- coding: utf-8 -*-
"""
Project on Tue Apr  3 21:00:17 2018
Created on Mon Apr 16 13:21:06 2018

@author: Caleb Reiter
"""

import numpy  as electromagneticpulse
import random as rand
from math import log

O = (0,0)    #the point at infinity
Q = (0,0)    #point for encryption
E = []       #points on the elliptic curve over a finite field
q = 0        #a prime number defining the finite field
a = 0        #co-efficient in Elliptic Curve E
b = 0        #co-efficient in Elliptic Curve E
k = 50       #used to decrease chances that a message cannot be embedded in E

def load_elliptic_curve(q0,a0,b0):
    '''
    loads the points from an elliptic curve defined over a
    finite field of integers mod q
    if file not found, the elliptic curve is generated
    
    Keyword arguments:
    q0 -- prime number q defining Finite Field
    a0 -- constant a, coefficient in the Elliptic Curve
    b0 -- constant b, coefficient in the Elliptic Curve
    '''
    if not (isinstance(q0,int) and isinstance(a0,int) and isinstance(b0,int)):
        raise TypeError('Invalid input not type int {}, {}, {}'.format((q0,type(q0)),(a0,type(a0)),(b0,type(b0))))
    global q, a, b
    q = q0
    a = a0
    b = b0
    f = './Curves/ECPoints_{}_{}_{}.csv'.format(q,a,b)
    try:
        print('loading {}'.format(f))
        E = electromagneticpulse.loadtxt(f, dtype='int64', delimiter=',')
        E = list(map(lambda x:(x[0].item(),x[1].item()),E))
        return E
    except IOError:
        print('{} could not be found, creating file'.format(f))
        return create_elliptic_curve(q, a, b)

def create_elliptic_curve(q0,a0,b0):
    '''
    generates the points on an elliptic curve of the form
    y^2=x^3+a*x+b defined over a finite field of integers
    mod q
    
    Keyword arguments:
    q0 -- prime number q defining Finite Field
    a0 -- constant a, coefficient in the Elliptic Curve
    b0 -- constant b, coefficient in the Elliptic Curve
    '''
    global q, a, b
    q = q0
    a = a0
    b = b0
    E =  list(filter(lambda x:x[1]>=0,map(lambda x:(x,modularSquareRoot(pow(x,3,q)+a*x+b)),range(q))))
    E += list(filter(lambda x:x[1]>=0,map(lambda x:(x[0],q-x[1]),filter(lambda x:x[1] > 0,E))))

    f = './Curves/ECPoints_{}_{}_{}.csv'.format(q,a,b)

    electromagneticpulse.savetxt(f, E, delimiter=',', fmt='%d')
    return E

def select_Q(i):
    global Q
    Q = E[i]

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
    returns quadratic residue of a mod q otherwise
            returns -1 if a is a quadratic non-residue
            mod q
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
        m = (3 * pow(P[0],2,q) + a)%q * inv_mod_q(2*P[1]) if P == Q else (Q[1]-P[1]) * inv_mod_q(Q[0]-P[0])
        x = (m**2 - P[0] - Q[0]) % q
        try:
            y = (m * (P[0] - x) - P[1]) % q
        except RuntimeWarning:
            y = (m * (P[0] - x) - P[1]) % q
            print('y = {} P = {} Q = {}'.format(y,P,Q))
        return (x,y)
    
def embed(x):
    '''
    embeds plaintext x into Elliptic Curve E
    
    Keyword arguments:
    x -- the plaintext to embed
    '''
    stream = list(map(lambda x : ord(x),x))
    return stream

def extract(x):
    '''
    extracts plaintext from embedded message x
    
    Keyword arguments:
    x -- embedded message to extract
    '''
    return ''.join([chr(x0) for x0 in x])
    
def encrypt(x, Pu_a, Pu_b):
    '''
    encrypts plaintext x with key Pr_a
    e_K(x,k) = (Pr_a•P,x+Pr_a•Pu_b)
    
    Keyword arguments:
    x -- the plaintext to be encrypted
    Pr_a -- your private key to encrypt with
    Pu_b -- their public key
    '''
    β = Pu_b
    for i in range(Pr_a-1):
        β = addition(β,Pu_b)
    β = addition(x,β)
    return (Pu_a,β)

def decrypt(y, Pr_b):
    '''
    decrypts ciphertext y with key Pr_b
    d_K(t, β) = β - Pr_b•t
    
    Keyword arguments:
    y -- the ciphertext to be decrypted
    Pr_b -- the private key to decrypt with
    '''
    t = y[0]
    for i in range(Pr_b-1):
        t = addition(t,y[0])
    invt = (t[0],q-t[1])
    x = addition(y[1],invt)
    return x

def point_compression(x):
    '''
    compresses point x by approximately 50%
    since y can be calculated from x if it is known
    to be even or odd
    
    Keyword arguments:
    x -- the point to be compressed
    '''
    return (x[0],x[1]%2)

def point_decompression(x):
    '''
    decompresses point x
    if sqrt(x^3+a*x+b)mod(q) = y
    then return (x,y) else return (x,q-y)
    '''
    y = modularSquareRoot(pow(x[0],3,q)+a*x[0]+b)
    return (x[0],y) if y % 2 == x[1] else (x[0],q-y)

def message_to_point(m):
    '''
    finds a message value from x on E
    there is a 2^-k probability that this will fail on E
    
    Keyword arguments:
    m -- the message
    '''
    x = m*k
    y = modularSquareRoot(pow(x,3,q)+a*x+b)
    while(y < 0 and x - m*k <= k):
        x += 1
        y = modularSquareRoot(pow(x,3,q)+a*x+b)    
    return (x,modularSquareRoot(pow(x,3,q)+a*x+b))

def point_to_message(x):
    '''
    returns the message value from point x
    
    Keyword arguments:
    x -- the point
    '''
    return int(x[0]/k)

def points_to_hex_string(L):
    '''
    converts a list of points in the form
    [((a_0,b_0)(c_0,d_0)),((a_0,b_0),(c_1,d_1)),...,((a_0,b_0),(c_n,d_n))]
    into a string of hexadecimal values
    
    Keyword arguments:
    L -- the list of points to be converted
    '''
    l = [e[1] for e in L] # (a_0,b_0) from L
    r = int(log(q,16))+1  # calculate length of Hexadecimal value
    #convert (a_0,b_0) to a hex string in the form <hex(a_0)><hex(b_0)>
    f = '{{:0>{0}}}{{:0>{0}}}'.format(r).format(hex(L[0][0][0])[2:],hex(L[0][0][1])[2:])
    #convert elements in l to a concatenated hex string
    g = ''.join(['{{:0>{}}}'.format(r).format(hex(x)[2:]) for e in l for x in e])
    return f+g

def hex_string_to_points(h):
    '''
    converts a string of hexadecimal values in the form
    <hex(a_0)><hex(b_0)><hex(c_0)><hex(d_0)><hex(c_1)><hex(d_1)>...<hex(c_n)><hex(d_n)>
    into a list of points in the form
    [((a_0,b_0)(c_0,d_0)),((a_0,b_0),(c_1,d_1)),...,((a_0,b_0),(c_n,d_n))]
    
    Keyword arguments:
    h -- the hex string to be converted
    '''
    r = int(log(q,16))+1
    h = h[2*r:]
    l = [(int(h[e:e+r],16),int(h[e+r:e+2*r],16)) for e in range(0,len(h),2*r)]
    return [(Pu_a,e) for e in l]

def encrypt_to_hex_string(plaintext):
    '''
    encrypts the plaintext using Elliptic Curve Cryptography
    
    Keyword arguments:
    plaintext -- the plaintext to be encrypted
    '''
    return points_to_hex_string([encrypt(m, Pu_a, Pu_b) for m in [message_to_point(x) for x in embed(plaintext)]])

def decrypt_from_hex_string(hexstring):
    '''
    decrypts the encrypted message using Elliptic Curve Cryptography
    
    Keyword arguments:
    hexstring -- the encrypted message to be decrypted
    '''
    extract([point_to_message(x) for x in [decrypt(m, Pr_b) for m in hex_string_to_points(hexstring)]])

q0 = int(input('Enter prime number p: ')) # 13381
a0 = int(input('Enter integer a: '))      # 3
b0 = int(input('Enter integer b: '))      # 1
E = load_elliptic_curve(q0,a0,b0)
plaintext = str(input('Enter plaintext: ')) # Hello World!
# generate private and public keys
Pr_a = rand.randint(1,len(E))
Pr_b = rand.randint(1,len(E))
    # select point Q
Q = select_Q(rand.randint(1,len(E)))
Pu_a = Q
Pu_b = Q
for i in range(Pr_a-1):
    Pu_a = addition(Pu_a,Q)
for i in range(Pr_b-1):
    Pu_b = addition(Pu_b,Q)
print('Q: {}, Pr_a: {}, Pu_a: {}, Pr_b: {}, Pu_b: {}'.format(Q,Pr_a,Pu_a,Pr_b,Pu_b))
#encrypt plaintext
encrypted = encrypt_to_hex_string(plaintext)
print('Encrypted text: {}'.format(encrypted))
#decrypt plaintext
decrypted = decrypt_from_hex_string(encrypted)
print('Decrypted: {}'.format(decrypted))
