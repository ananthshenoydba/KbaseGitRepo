#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 10 06:36:24 2022

@author: jangri
"""
def get_sieve(n):
    sieve = [True] * (n+1)
    sieve[0]=False
    sieve[1]=False
    return sieve


def mark_nonprimes(a_list, p):
    for j in range (2, len(a_list)):
        for i in range (p*j, len(a_list), p):
            a_list[i]=False
    return(a_list)

def get_next(b_list, m):
    for k in range (m+1, len(b_list)):
        if b_list[k]==True:
            return k

# primelist = get_sieve(30)
# primelist = mark_nonprimes(primelist, 2)
# n = get_next(primelist, 2)
# print(n)
# primelist = mark_nonprimes(primelist, n)
# m = get_next(primelist, n)
# print(m)

    
def get_primes(n):
    primelist = get_sieve(n)
    jump=2
#    for l in range (jump, len(primelist)):
    while jump < int(len(primelist)/2):
        #print('jump=', jump)
        primelist = mark_nonprimes(primelist, jump)
        #print(primelist)
        jump = get_next(primelist, jump)
    count=0
    for i in range(1, n):
        if primelist[i]==True:
            count=count+1
            print(i)
    print(count)

get_primes(1000)
    

# def getprime(n):
#     listofprime = get_sieve(n)
#     for j in range 