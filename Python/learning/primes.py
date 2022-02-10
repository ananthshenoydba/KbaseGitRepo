#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  9 06:04:30 2022

@author: jangri
"""
def mersenne_number(p):
    return 2**p-1

#print(mersenne_number(2))

def is_prime_slow(p):
    if p <= 1 or p%2==0:
        return False
    elif p == 2 or p == 3:
        return True
    elif p > 3:
        for i in range(2, p):
            if p % i == 0:
                return False
    return True

def is_prime(n):
    if n==2 or n==3: return True
    if n%2==0 or n<2: return False
    for i in range(3,int(n**0.5)+1,2):   # only odd numbers
        if n%i==0:
            return False    
    return True

def get_primes(a,b):
    primelist = []
    lower=0
    upper=0
    if a < b:
        lower=a
        upper=b
    else:
        lower=b
        upper=a
    for i in range (lower,upper):
        if is_prime(i)==True:
            primelist.append(i)
    return primelist

# mersennes = []
# for i in (primelist):
#     mersennes.append(mersenne_number(i))

    
def lucas_lehmer(p):
    ll=[4]
    for i in range(1,p-1):
        ll.append((ll[i-1]**2-2)%mersenne_number(p))
    return ll

# print(lucas_lehmer(17))

        
prime_list=get_primes(3, 65)

is_mer=[]
for i in prime_list:
    print(prime_list)
    print(is_mer)
    if is_prime(mersenne_number(i)) == True:
        is_mer.append(1)
    else:
        is_mer.append(0)
print(is_mer)
    
