import numpy as np
from numpy.polynomial import polynomial as p
import sys

n = 1024
q = 2**32-1
hlpr = [1] + [0] * (n-1) + [1]

def bool_to_int(b): return (1 if b else 0)
def norm_poly(q,poly):
    # this is not exactly correct, as we should take the modulo uniformly,
    # but that doesn't work as expected...
    ret = p.polydiv(np.int_(poly),hlpr)[1]
    return ret

def gen_poly(n,q):
    l = 0 #Gamma Distribution Location (Mean "center" of dist.)
    while True:
        poly = norm_poly(q, np.floor(np.random.normal(l,size=(n))))
        if len(poly) == n:
            return poly

def gen_seb(n, q, A):
    s = gen_poly(n, q)
    e = gen_poly(n, q)
    b = norm_poly(q,p.polyadd(p.polymul(A,s),e))
    return s, e, b

def compute_u(b):
    u = np.asarray([False] * n)
    q2 = q/2
    q4 = q/4
    for i in range(0,n):
        if len(b) <= i: break
        bi = b[i] % q
        if bi < q4: u[i] = False
        elif bi < q2: u[i] = True
        elif bi < 3*q4: u[i] = False
        elif bi < q: u[i] = True
        else:
            print("FATAL ERROR@compute_u: ", bi, " > ", q)
            sys.exit()
    return u

def compute_shared(u, sC, bD):
    shared = norm_poly(q, p.polymul(sC,bD))

    for i, ui in enumerate(iter(u)):
        # Region 0 (0 --- q/4 and q/2 --- 3q/4)
        if not ui:
            shared[i] = bool_to_int(shared[i] >= q*0.125 and shared[i] < q*0.625)
        # Region 1 (q/4 --- q/2 and 3q/4 --- q)
        else:
            shared[i] = 1 - bool_to_int(shared[i] >= q*0.875 and shared[i] < q*0.375)

    return shared

#Generate A
A = np.random.random(size=(n))*q
A = norm_poly(q,A)

#Alice (Secret & Error)
sA, eA, bA = gen_seb(n, q, A)

#Bob
sB, eB, bB = gen_seb(n, q, A)

# Adversary: Eve
sE, eE, bE = gen_seb(n, q, A)

#Error Rounding
u = compute_u(bB)

# shared secret + rounding
sharedAlice = compute_shared(u, sA, bB)
sharedBob   = compute_shared(u, sB, bA)

# Adversary: Eve
# Eve is MITM, can access only (bA, u)
sharedEve   = compute_shared(u, sE, bA)


print("A:",len(A),"|",A)
print("\n-Alice---")
print(" s:",len(sA),"|",sA)
print(" e:",len(eA),"|",eA)
print(" b:",len(bA),"|",bA)
print("\n-Bob---")
print(" s':",len(sB),"|",sB)
print(" e':",len(eB),"|",eB)
print(" b':",len(bB),"|",bB)
print(" u :",len(u),"|",u)
print("\n-Eve---")
print(" s':",len(sB),"|",sE)
print(" e':",len(eB),"|",eE)
print(" b':",len(bB),"|",bE)
print("\n")
print("Shared Secret Alice:",len(sharedAlice),"|",sharedAlice)
print("Shared Secret Bob:",len(sharedBob),"|",sharedBob)
print("Shared Secret Eve:",len(sharedEve),"|",sharedEve)

print("\n\n--Verification--")
i = 0
while (i < len(sharedBob)):
    if (sharedAlice[i] != sharedBob[i]):
        print("Error at index",i)
    if (sharedAlice[i] != sharedEve[i]):
        print("Adv.Error at index", i)
    i+=1
