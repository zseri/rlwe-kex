import numpy as np
from numpy.polynomial import polynomial as p

n = 1024
q = 2**32-1
hlpr = [1] + [0] * (n-1) + [1]

def gen_poly(n,q):
    global hlpr
    l = 0 #Gamma Distribution Location (Mean "center" of dist.)
    poly = np.floor(np.random.normal(l,size=(n)))
    while (len(poly) != n):
        poly = np.floor(np.random.normal(l,size=(n)))
        poly = np.floor(p.polydiv(poly,hlpr)[1]%q)
    return poly

def bool_to_int(b):
    return (1 if b else 0)

def gen_seb(n, q, A):
    s = gen_poly(n, q)
    e = gen_poly(n, q)
    b = p.polymul(A,s)%q
    b = np.floor(p.polydiv(s,hlpr)[1])
    b = p.polyadd(b,e)%q
    return s, e, b

def compute_shared(u, sC, bD):
    shared = np.floor(p.polymul(sC,bD)%q)
    shared = np.floor(p.polydiv(shared,hlpr)[1])%q

    for i, ui in enumerate(iter(u)):
        # Region 0 (0 --- q/4 and q/2 --- 3q/4)
        if not ui:
            shared[i] = bool_to_int(shared[i] >= q*0.125 and shared[i] < q*0.625)
        else:
            shared[i] = 1 - bool_to_int(shared[i] >= q*0.875 and shared[i] < q*0.375)

    return shared

#Generate A
A = np.floor(np.random.random(size=(n))*q)%q
A = np.floor(p.polydiv(A,hlpr)[1])

#Alice (Secret & Error)
sA, eA, bA = gen_seb(n, q, A)

#Bob
sB, eB, bB = gen_seb(n, q, A)

# Adversary: Eve
sE, eE, bE = gen_seb(n, q, A)

#Error Rounding
#--Bob
u = np.asarray([False] * n)
i = 0

while (i < len(u)):
    if (len(bB) <= i): break;
    if (int(bB[i]/(q/4)) == 0): u[i] = False
    elif (int(bB[i]/(q/2)) == 0): u[i] = True
    elif (int(bB[i]/(3*q/4)) == 0): u[i] = False
    elif (int(bB[i]/(q)) == 0): u[i] = True
    else:
        print("error! (1)")
    i+=1

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
