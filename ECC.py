# -*- coding: utf-8 -*-
"""
Project started on Tue Apr  3 21:00:17 2018
Created on Mon Apr 16 13:21:06 2018

@author: Caleb Reiter

Sources:
    Dr. Tim Gillespie
    Stinson, D. R. (2006). Cryptography: Theory and practice. 
    Yan, S. Y. (2001). Number theory for computing. Berlin: Springer.
"""

from   math   import log
import numpy  as np
import random as rand
import re
import time

O = (0,0)    #the point at infinity
Q = (0,0)    #point for encryption
Pu_a = Q     #your public key (known)
Pu_b = Q     #receiver's public key (known)
Pr_a = 0     #your private key (known)              for the sake of this implementation
Pr_b = 0     #receiver's private key ("not known")  Pr_a, and Pr_b are both known and randomly generated
E = []       #points on the elliptic curve over a finite field
q = 0        #a prime number defining the finite field
p = 0        #order of Elliptic Curve
a = 0        #co-efficient in Elliptic Curve E
b = 0        #co-efficient in Elliptic Curve E
k = 50       #used to decrease chances that a message cannot be embedded in E

def load_elliptic_curve(q0,a0,b0):
    '''
    loads the points from an elliptic curve defined over a
    finite field of integers mod q
    if the file is not found, the elliptic curve is generated
    
    Keyword arguments:
    q0 -- prime number q defining Finite Field
    a0 -- constant a, coefficient in the Elliptic Curve
    b0 -- constant b, coefficient in the Elliptic Curve
    returns E -- the points on the Elliptic Curve
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
        E = np.loadtxt(f, dtype='int64', delimiter=',')
        #   maps 64 bit integer 2-tuples to
        #    python native int 2-tuples of the same value
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
    returns E -- the points on the Elliptic Curve
    '''
    global q, a, b
    q = q0
    a = a0
    b = b0
    #    maps [0, q-1] to points on finite Elliptic Curve
    E =  list(filter(lambda x:x[1]>=0,map(lambda x:(x,quadratic_residue(pow(x,3,q)+a*x+b)),range(q))))
    E += list(map(lambda x:(x[0],q-x[1]),filter(lambda x:x[1] > 0,E)))

    f = './Curves/ECPoints_{}_{}_{}.csv'.format(q,a,b)

    np.savetxt(f, E, delimiter=',', fmt='%d')
    return E

def set_specifications(key_size):
    global q, a, b, p, Q
    '''
    sets q, a, b, p, and Q values depending on the key_size
    q - prime number defining the finite field
    a - first co-efficient of the elliptic curve
    b - second co-efficient of the elliptic curve
    p - the order of the elliptic curve over the finite field
    Q - the point Q shared between sender and receiver
    specifications retrieved from:
        https://tools.ietf.org/html/rfc5639#section-3.1
    '''
    if key_size == 160:
        q = int('E95E4A5F737059DC60DFC7AD95B3D8139515620F', 16)
        a = int('340E7BE2A280EB74E2BE61BADA745D97E8F7C300', 16)
        b = int('1E589A8595423412134FAA2DBDEC95C8D8675E58', 16)
        x = int('BED5AF16EA3F6A4F62938C4631EB5AF7BDBCDBC3', 16)
        y = int('1667CB477A1A8EC338F94741669C976316DA6321', 16)
        p = int('E95E4A5F737059DC60DF5991D45029409E60FC09', 16)
        Q = (x,y)
    elif key_size == 192:
        q = int('C302F41D932A36CDA7A3463093D18DB78FCE476DE1A86297', 16)
        a = int('6A91174076B1E0E19C39C031FE8685C1CAE040E5C69A28EF', 16)
        b = int('469A28EF7C28CCA3DC721D044F4496BCCA7EF4146FBF25C9', 16)
        x = int('C0A0647EAAB6A48753B033C56CB0F0900A2F5C4853375FD6', 16)
        y = int('14B690866ABD5BB88B5F4828C1490002E6773FA2FA299B8F', 16)
        p = int('C302F41D932A36CDA7A3462F9E9E916B5BE8F1029AC4ACC1', 16)
        Q = (x,y)
    elif key_size == 224:
        q = int('D7C134AA264366862A18302575D1D787B09F075797DA89F57EC8C0FF', 16)
        a = int('68A5E62CA9CE6C1C299803A6C1530B514E182AD8B0042A59CAD29F43', 16)
        b = int('2580F63CCFE44138870713B1A92369E33E2135D266DBB372386C400B', 16)
        x = int('0D9029AD2C7E5CF4340823B2A87DC68C9E4CE3174C1E6EFDEE12C07D', 16)
        y = int('58AA56F772C0726F24C6B89E4ECDAC24354B9E99CAA3F6D3761402CD', 16)
        p = int('D7C134AA264366862A18302575D0FB98D116BC4B6DDEBCA3A5A7939F', 16)
        Q = (x,y)
    elif key_size == 256:
        q = int('A9FB57DBA1EEA9BC3E660A909D838D726E3BF623D52620282013481D1F6E5377', 16)
        a = int('7D5A0975FC2C3057EEF67530417AFFE7FB8055C126DC5C6CE94A4B44F330B5D9', 16)
        b = int('26DC5C6CE94A4B44F330B5D9BBD77CBF958416295CF7E1CE6BCCDC18FF8C07B6', 16)
        x = int('8BD2AEB9CB7E57CB2C4B482FFC81B7AFB9DE27E1E3BD23C23A4453BD9ACE3262', 16)
        y = int('547EF835C3DAC4FD97F8461A14611DC9C27745132DED8E545C1D54C72F046997', 16)
        p = int('A9FB57DBA1EEA9BC3E660A909D838D718C397AA3B561A6F7901E0E82974856A7', 16)
        Q = (x,y)
    elif key_size == 320:
        q = int('D35E472036BC4FB7E13C785ED201E065F98FCFA6F6F40DEF4F92B9EC7893EC28FCD412B1F1B32E27', 16)
        a = int('3EE30B568FBAB0F883CCEBD46D3F3BB8A2A73513F5EB79DA66190EB085FFA9F492F375A97D860EB4', 16)
        b = int('520883949DFDBC42D3AD198640688A6FE13F41349554B49ACC31DCCD884539816F5EB4AC8FB1F1A6', 16)
        x = int('43BD7E9AFB53D8B85289BCC48EE5BFE6F20137D10A087EB6E7871E2A10A599C710AF8D0D39E20611', 16)
        y = int('14FDD05545EC1CC8AB4093247F77275E0743FFED117182EAA9C77877AAAC6AC7D35245D1692E8EE1', 16)
        p = int('D35E472036BC4FB7E13C785ED201E065F98FCFA5B68F12A32D482EC7EE8658E98691555B44C59311', 16)
        Q = (x,y)
    elif key_size == 384:
        q = int('8CB91E82A3386D280F5D6F7E50E641DF152F7109ED5456B412B1DA197FB71123ACD3A729901D1A71874700133107EC53', 16)
        a = int('7BC382C63D8C150C3C72080ACE05AFA0C2BEA28E4FB22787139165EFBA91F90F8AA5814A503AD4EB04A8C7DD22CE2826', 16)
        b = int('04A8C7DD22CE28268B39B55416F0447C2FB77DE107DCD2A62E880EA53EEB62D57CB4390295DBC9943AB78696FA504C11', 16)
        x = int('1D1C64F068CF45FFA2A63A81B7C13F6B8847A3E77EF14FE3DB7FCAFE0CBD10E8E826E03436D646AAEF87B2E247D4AF1E', 16)
        y = int('8ABE1D7520F9C2A45CB1EB8E95CFD55262B70B29FEEC5864E19C054FF99129280E4646217791811142820341263C5315', 16)
        p = int('8CB91E82A3386D280F5D6F7E50E641DF152F7109ED5456B31F166E6CAC0425A7CF3AB6AF6B7FC3103B883202E9046565', 16)
        Q = (x,y)
    elif key_size == 512:
        q = int('AADD9DB8DBE9C48B3FD4E6AE33C9FC07CB308DB3B3C9D20ED6639CCA703308717D4D9B009BC66842AECDA12AE6A380E62881FF2F2D82C68528AA6056583A48F3', 16)
        a = int('7830A3318B603B89E2327145AC234CC594CBDD8D3DF91610A83441CAEA9863BC2DED5D5AA8253AA10A2EF1C98B9AC8B57F1117A72BF2C7B9E7C1AC4D77FC94CA', 16)
        b = int('3DF91610A83441CAEA9863BC2DED5D5AA8253AA10A2EF1C98B9AC8B57F1117A72BF2C7B9E7C1AC4D77FC94CADC083E67984050B75EBAE5DD2809BD638016F723', 16)
        x = int('81AEE4BDD82ED9645A21322E9C4C6A9385ED9F70B5D916C1B43B62EEF4D0098EFF3B1F78E2D0D48D50D1687B93B97D5F7C6D5047406A5E688B352209BCB9F822', 16)
        y = int('7DDE385D566332ECC0EABFA9CF7822FDF209F70024A57B1AA000C55B881F8111B2DCDE494A5F485E5BCA4BD88A2763AED1CA2B2FA8F0540678CD1E0F3AD80892', 16)
        p = int('AADD9DB8DBE9C48B3FD4E6AE33C9FC07CB308DB3B3C9D20ED6639CCA70330870553E5C414CA92619418661197FAC10471DB1D381085DDADDB58796829CA90069', 16)
        Q = (x,y)
    else:
        raise Exception('Invalid key size: {}'.format(key_size))

def verify_point(P):
    '''
    verifies the point P is on the chosen Elliptic Curve by checking
    P_x and P_y satisfy the equation y^2 = x^3+ax+b (mod q)
    '''
    return pow(P[1],2,q) == (pow(P[0],3,q)+a*P[0]+b)%q

def mul_inv(a):
    '''
    finds the multiplicative inverse of a number, a mod q
    
    Keyword arguments:
    a -- the number to find the multiplicative inverse of
    raises ZeroDivisionError if a is equivalent to 0 mod q
    returns -- a**-1 the multiplicative inv of a
    '''
    if a % q == 0:
        raise ZeroDivisionError('Impossible Inverse {}'.format(a))
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
        #this is not really a quadratic residue, but I need to be able to
        # distinguish between y^2=a mod(q) where y=0 and when a is a
        # non-quadratic residue
        return 0
    elif legendre_symbol(a) < 0:
        return -1
    elif q == 0:
        return a
    elif q % 4 == 3:
        return pow(a, (q+1)>>2, q)
    
    s = q-1
    e = 0
    while s%2 == 0:
        s >>= 1
        e+=1
    n = 2
    while legendre_symbol(n) != -1:
        n+=1
    x = pow(a, (s+1)>>1,q)
    b = pow(a, s, q)
    g = pow(n, s, q)
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
    takes the congruency y^2 = a mod(q)
    returns -1 if a is a non-quadratic residue
     or returns 1 if a is a quadratic residue
     or returns 0 if a is 0
    from https://eli.thegreenplace.net/2009/03/07/computing-modular-square-roots-in-python
    '''
    ls = pow(a, (q-1)>>1, q)
    return -1 if ls == q-1 else ls

def addition(P, Q):
    '''
    performs pointwise addition on an elliptic curve
    
    Keyword arguments:
    P -- the first point to be added
    Q -- the second point to be added
    return point addition of P and Q
    
    algorithm from Douglas R. Stinson "Cryptography Theory and Practice"
     - page 258 §6.5.2  Elliptic Curves Modulo a Prime
    '''
    if P == O:
        # O + Q - Q = 0
        return Q
    elif Q == O:
        # P + O - P = 0
        return P
    elif (P[0] == Q[0]) and (P[1] == q-Q[1]):
        # P + -P + O = 0
        return O
    else:
        # P + Q + -R = 0
        # P + P - 2P = 0
        # calculate m = (3x**2 + a) * (2y)**-1 if P == Q
        # else      m = (y2-y1) * (x2-x1)**-1
        m = (3 * pow(P[0],2,q) + a)%q * mul_inv(2*P[1]) if P == Q else (Q[1]-P[1]) * mul_inv(Q[0]-P[0])
        x = (m**2 - P[0] - Q[0]) % q
        y = (m * (P[0] - x) - P[1]) % q
        return (x,y)
    
def multiplication(P, l):
    '''
    performs point multiplication on an elliptic curve
    this uses the point double and add method for
    multiplication, by doubling the point and adding
    them based off of the binary representation of l
    
    Keyword arguments:
    P -- the point to be multiplied
    l -- the scalar multiplier
    returns point multiplication l•P
    '''
    if l == p:
        return P
    elif P == O:
        return P
    R = O
    b = list(bin(l)[2:])
    Q = R
    for i in range(len(b)):
        if i == 0:
            R = addition(P,R)
        else:
            R = addition(R,R)
        if int(b[len(b)-i-1]) == 1:
            Q = addition(Q,R)
    return Q

def generate_public_key(Pr, timed=False):
    if timed:
        start = time.time()
        Pu = multiplication(Q, Pr)
        print('Public Key generation time: {} seconds'.format(time.time()-start))
        return Pu
    else:
        return multiplication(Q, Pr)

def generate_private_key():
    return rand.randint(1,p)

def embed(x):
    '''
    embeds plaintext x into Elliptic Curve E
    
    Keyword arguments:
    x -- the plaintext to embed
    returns the plaintext embedded into E
    '''
    #        maps character x to unicode value of x
    stream = list(map(lambda x : ord(x),x))
    stream = list(map(lambda i : (1<<16)*stream[i]+stream[i+1] if i+1 <= len(stream)-1 else (1<<16)*stream[i] ,range(0,len(stream),2)))
    return stream

def extract(x):
    '''
    extracts plaintext from embedded message x
    
    Keyword arguments:
    x -- embedded message to extract
    '''
    return ''.join([str(chr(e>>16)+chr(e%(1<<16))) if e%(2<<16) !=0 else str(chr(e>>16)) for e in x])
    
def encrypt(x, β):
    '''
    encrypts plaintext x with key Pr_a
    e_K(x,k) = (Pr_a•P,x+Pr_a•Pu_b)
    
    Keyword arguments:
    x -- the plaintext to be encrypted
    β -- Pr_a*Pu_b
    returns -- encrypted x
    
    algorithm from Douglas R. Stinson "Cryptography Theory and Practice"
     - page 260 §6.5.2  Elliptic Curves Modulo a Prime
    '''
    β = addition(x,β)
    return (Pu_a,β)

def decrypt(y, t):
    '''
    decrypts ciphertext y with key Pr_b
    d_K(y, t) = y - t
    
    Keyword arguments:
    y -- the ciphertext to be decrypted
    t -- Pr_b*Pu_a
    
    algorithm from Douglas R. Stinson "Cryptography Theory and Practice"
     - page 260 §6.5.2  Elliptic Curves Modulo a Prime
    '''
    return addition(y, (t[0],q-t[1]))

def point_compression(x):
    '''
    compresses point x by approximately 50%
    since y can be calculated from x if it is known
    to be even or odd
    
    Keyword arguments:
    x -- the point to be compressed
    returns x with its y component mod 2
    
    algorithm from Douglas R. Stinson "Cryptography Theory and Practice"
     - page 263 §6.5.4  Point Compression and the ECIES
    '''
    return (x[0],x[1]%2)

def point_decompression(x):
    '''
    decompresses point x
    if sqrt(x^3+a*x+b)mod(q) = y
    then return (x,y) else return (x,q-y)
    
    algorithm from Douglas R. Stinson "Cryptography Theory and Practice"
     - page 263 Algorithm 6.4: Point-Decompress
    '''
    y = quadratic_residue(pow(x[0],3,q)+a*x[0]+b)
    return (x[0],y) if y % 2 == x[1] else (x[0],q-y)

def message_to_point(m):
    '''
    finds a message value from x on E
    there is a 2^-k probability that this will fail on E
    
    Keyword arguments:
    m -- the message
    raises Exception if m fails to be encrypted (probability 2**-k)
    returns m embedded as a point on E
    
    algorithm from Song Y. Yan: Number theory for computing
     - page 380 §3.3.8(II) Elliptic Curve Public-Key Cryptosystems 
    '''
    x = m*k
    y = quadratic_residue(pow(x,3,q)+a*x+b)
    while(y < 0 and x - m*k <= k):
        x += 1
        y = quadratic_residue(pow(x,3,q)+a*x+b)
    if x-m*k > k:
        raise Exception('Failed to encrypt message!')
    return (x,quadratic_residue(pow(x,3,q)+a*x+b))

def point_to_message(x):
    '''
    returns the message value from point x
    
    Keyword arguments:
    x -- the point
    returns x converted to its unicode value.
    
    algorithm from Song Y. Yan: Number theory for computing
     - page 380 §3.3.8(II) Elliptic Curve Public-Key Cryptosystems 
    '''
    return int(x[0]/k)

def points_to_hex_string(L):
    '''
    converts a list of points in the form
    [((a_0,b_0)(c_0,d_0)),((a_0,b_0),(c_1,d_1)),...,((a_0,b_0),(c_n,d_n))]
    into a string of hexadecimal values
    of the format ''.join([hex(c_0),hex(d_0),hex(c_1),hex(d_1),...,hex(c_n),hex(d_n)])
    
    Keyword arguments:
    L -- the list of points to be converted
    returns hexadecimal string
    '''
    r = int(log(q,16))+1  # calculate length of Hexadecimal value
    #convert elements in L to a concatenated hex string
    return ''.join(['{{:0>{}}}'.format(r+1).format(hex(e[0])[2:]+str(e[1])) for e in L])

def hex_string_to_points(h):
    '''
    converts a string of hexadecimal values in the form
    ''.join([hex(c_0),hex(d_0),hex(c_1),hex(d_1),...,hex(c_n),hex_(d_n)])
    into a list of points in the form where (a_0,b_0) = Pu_a
    [((a_0,b_0),(c_0,d_0)),((a_0,b_0),(c_1,d_1)),...,((a_0,b_0),(c_n,d_n))]
    
    Keyword arguments:
    h -- the hex string to be converted
    return the list of points
    '''
    r = int(log(q,16))+1
    l = [(int(h[e:e+r],16),int(h[e+r],16)) for e in range(0,len(h),r+1)]
    return [(Pu_a,e) for e in l]

def crack_private_key(public_key):
    '''
    brute forces a private key, given its public key
    mainly used to show the infeasibility of it given a sufficiently
    large key
    
    Keyword arguments:
    public_key -- the key whose private key to crack
    '''
    global Q
    cycleTime = time.time()
    cycle = [Q]
    S = Q
    while not(S == public_key):
        cycle.append(S)
        S = addition(S, Q)
    private_key = len(cycle)
    endCycleTime = time.time()
    print('Time to crack private key: {} seconds key: {}'.format(endCycleTime-cycleTime, private_key))
    rate = (endCycleTime-cycleTime)/private_key
    print('Time for 160 bit key: {} seconds'.format(rate*(2**160)))
    print('Time for 224 bit key: {} seconds'.format(rate*(2**224)))
    print('Time for 256 bit key: {} seconds'.format(rate*(2**256)))
    print('Time for 384 bit key: {} seconds'.format(rate*(2**384)))
    print('Time for 521 bit key: {} seconds'.format(rate*(2**521)))
    

def encrypt_to_hex_string(plaintext):
    '''
    encrypts the plaintext using Elliptic Curve Cryptography
    
    Keyword arguments:
    plaintext -- the plaintext to be encrypted
    return the ciphertext
    '''
     #much faster to compute here instead of each time encrypt(m, β) is called
     # less secure than using a secure random value in place of Pr_a
    β = multiplication(Pu_b, Pr_a)
    return points_to_hex_string([point_compression(c[1]) for c in [encrypt(m, β) for m in [message_to_point(x) for x in embed(plaintext)]]])

def decrypt_from_hex_string(hexstring):
    '''
    decrypts the encrypted message using Elliptic Curve Cryptography
    
    Keyword arguments:
    hexstring -- the encrypted message to be decrypted
    return the plaintext
    '''
    #much faster to compute here instead of each time decrypt(m, t) is called
    # less secure than using receiving r*Q from Alice in place of Pu_a
    t = multiplication(Pu_a,Pr_b)
    return extract([point_to_message(x) for x in [decrypt(m, t) for m in [point_decompression(c[1]) for c in hex_string_to_points(hexstring)]]])

def encryption_loop(timed=False, see=False):
    loop = True
    while loop:
        plaintext = str(input('Enter plaintext: '))
        publicStart = time.time()
        #encrypt plaintext
        encrypted = encrypt_to_hex_string(plaintext)
        print('encrypt time: {} seconds'.format(time.time() - publicStart))
        print('Encrypted text: {}'.format(encrypted))
        #decrypt plaintext
        publicStart = time.time()
        decrypted = decrypt_from_hex_string(encrypted)
        stop = time.time()
        print('decrypt time: {} seconds'.format(stop - publicStart))
        print('Decrypted: {}'.format(decrypted))
        loop_input = input('Press \'Y\' to encrypt another message\nPress \'k\' to generate new keys\nPress any other key to end:\n')
        loop = loop_input.upper() in ['Y', 'K']
        if loop_input.upper() == 'K':
            key_input_loop(timed, see)
        
def key_input_loop(timed=False, see=False):
    match_key_input = False
    flag = True
    while not (match_key_input):
        key_size = input('Enter key size in bits (160, 192, 224, 256, 320, 384, or 512): ') if flag else input('Please choose from (160, 192, 224, 256, 320, 384, or 512): ')
        if flag: flag == False
        match_key_input = re.match(r'^(160|192|224|256|320|384|512)$', key_size)
        if match_key_input:
            key_size = int(key_size)
    # sets curve specifications based off of key size
    set_specifications(key_size)
    generate_keys(timed, see)
    
def generate_keys(timed=False, see=False):
    global Pu_a, Pu_b, Pr_a, Pr_b
    # generate private and public keys
    #  clearly in an actual implementation a user would only generate their own
    #  private key, and the receiver's public key would be known
    #p is the order of the elliptic curve
    Pr_a = generate_private_key()
    Pr_b = generate_private_key()
    Pu_a = generate_public_key(Pr_a, timed)
    Pu_b = generate_public_key(Pr_b, timed)
    if see:
        print('Q: {}\nPr_a: {}\nPu_a: {}\nPr_b: {}\nPu_b: {}'.format(Q,Pr_a,Pu_a,Pr_b,Pu_b))
    

def main():
    key_input_loop(True, True)
    encryption_loop(True, True)

if __name__ == '__main__':
    main()