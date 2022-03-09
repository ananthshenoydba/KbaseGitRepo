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
    perpos = pattern.find('.')
    astpos = pattern.find('*')
    if perpos == -1 and astpos == -1:
        if strtochk == pattern:
            return True
        else:
            return False
    elif perpos != -1 and astpos == -1:
        if perpos == 0 and strtochk[perpos+1:]==pattern[perpos+1:]:
            return True
        elif strtochk[0:perpos-1]==pattern[0:perpos-1] and strtochk[perpos+1:]==pattern[perpos+1:]:
            return True
        else:
            return False
    elif perpos == -1 and astpos != -1:
        if astpos == 0:
            return True
        elif strtochk[0:astpos-1]==pattern[0:astpos-1]:
            return True
        else:
            return False
    elif perpos != -1 and astpos != -1:
        if perpos == 0 and strtochk[perpos+1:astpos]==pattern[perpos+1:astpos]:
            return True
        elif strtochk[0:perpos-1]==pattern[0:perpos-1] and strtochk[perpos+1:astpos]==pattern[perpos+1:astpos]:
            return True
        else:
            return False
        
        
#print(ismatch('abcdefg','.bcde*'))
