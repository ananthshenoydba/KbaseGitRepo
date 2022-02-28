# -*- coding: utf-8 -*-
"""
Created on Mon Feb 28 09:31:24 2022

@author: ananth.shenoy
"""

def gettuple(inlist, target):
    worklist = []
    worklist = inlist
    for i in range(0, len(worklist)):
        for j in range (i+1, len(worklist)):
            if worklist[i] + worklist[j] == target:
                return ["position in list ==>", (i,j), "values ==>", (worklist[i], worklist[j])]
    
print(gettuple([0,1,3,-2,9], 7))
