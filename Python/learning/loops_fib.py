# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

# def doit(x):
#     print((x**2 + 2)**2)
    
# doit(4)

def firstnfib(n):
    firstfib = 0
    secfib = 1
    count = 2
    newfib = 0

    if n < 0:
        print("no negetive Fibs")
    elif n == 0:
        print(firstfib)
    elif ( n > 0 and n <= 2):
        print(firstfib)
        print(secfib)
    else:
        print(firstfib)
        print(secfib)
        while count < n:
            newfib=firstfib+secfib
            firstfib=secfib
            secfib=newfib
            count=count+1
            print(newfib)
               
#firstnfib(10)

def fiblessthan(n):
    firstfib = 0 
    secfib = 1
    newfib = 0

    if n < 0:
        print("no negetive Fibs")
    elif n == 0:
        print(firstfib)
    elif ( n > 0 and n <= 2):
        print(firstfib)
        print(secfib)
    else:
        print(firstfib)
        print(secfib)
        while (newfib  < n):
            newfib=firstfib+secfib
            print(newfib)
            firstfib=secfib
            secfib=newfib
            

# fiblessthan(30)
            
        

