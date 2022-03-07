#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  2 16:38:34 2022

@author: jangri
"""

def getmedian (inlst1,inlst2):
    fulllist=[]
    fulllist = inlst1 +inlst2
    fulllist.sort()
    print(fulllist)
    if len(fulllist)%2!=0:
        median=fulllist[int(len(fulllist)/2)]
    else:
        median=(fulllist[int(len(fulllist)/2)]+fulllist[int(len(fulllist)/2)]-1)/2
    print(median)
    
        
    


def ismatch (instr1, instr2):
    strtochk = instr1
    pattern = instr2
    perpos = strtochk.find('.')
    astpos = strtochk.find('*')
    print(perpos)
    print(pattern[perpos])
    print(strtochk[perpos])
    pattern[perpos]=strtochk[perpos]
    # if "." in pattern:
    #     pattern[perpos]=strtochk[perpos]
    #     if strtochk==pattern:
    #         return(True)
    #     else:
    #         return(False)
    #elif "*" in pattern:
        
    
print(ismatch('ab','a.'))