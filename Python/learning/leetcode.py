# -*- coding: utf-8 -*-
"""
Created on Mon Feb 28 09:31:24 2022

@author: ananth.shenoy
"""

def gettuple(inlist, target):
    worklist = []
    outlist = []
    worklist = inlist
    for i in range(0, len(worklist)):
        for j in range (i+1, len(worklist)):
            if worklist[i] + worklist[j] == target:
                outlist.append((i,j))
    return outlist
                #return ["position in list ==>", (i,j), "values ==>", (worklist[i], worklist[j])]
    
#print(gettuple([-2,1,2,3,4,5,9], 7))

def list_2_int_rev(lst1):
    number=''
    for i in lst1[::-1]:
        number+=str(i)
    return(int(number))

def int_2_list_rev(numbr):
    revstr=str(numbr)
    lst1=[]
    for i in revstr[::-1]:
        lst1.append(int(i))
    return(lst1)

#print(int_2_list_rev(542))        
    
def addlist(lst1, lst2):
    num1=list_2_int_rev(lst1)
    num2=list_2_int_rev(lst2)
    num3=num1+num2
    return(int_2_list_rev(num3))
    
#print(addlist([2,4,3,4], [7,5,6,6]))

a_string = "abccdesgertgbjagewrawrgzdgsjhtarnzffgh"
def getlongestnonrepeat(instr):
    longest_string = 0
    resultset = []
    a_string = instr
    for i in range(0,len(a_string)):
        for j in range(1,len(a_string)+1-i):
            if len(set(a_string[i:i+j])) == len(a_string[i:i+j]):
                resultset.append(a_string[i:i+j])
    resultset=set(resultset)
    longest_string = len(max(resultset, key=len))
    return(longest_string)


#print(getlongestnonrepeat("abccdeffgh"))

def getlongestpalin(instr):
    longest_palin = ''
    resultset = []
    palin=''
    a_string = instr
    for i in range(0,len(a_string)):
        for j in range(1,len(a_string)+1-i):
            palin=a_string[i:i+j]
            if palin == palin [::-1]:
                resultset.append(a_string[i:i+j])
    resultset=set(resultset)
    longest_palin = max(resultset, key=len)
    return(longest_palin)

print(getlongestpalin("jkexvzsqshsxyytjmmhauoyrbxlgvdovlhzivkeixnoboqlfemfzytbolixqzwkfvnpacemgpotjtqokrqtnwjpjdiidduxdprngvitnzgyjgreyjmijmfbwsowbxtqkfeasjnujnrzlxmlcmmbdbgryknraasfgusapjcootlklirtilujjbatpazeihmhaprdxoucjkynqxbggruleopvdrukicpuleumbrgofpsmwopvhdbkkfncnvqamttwyvezqzswmwyhsontvioaakowannmgwjwpehcbtlzmntbmbkkxsrtzvfeggkzisxqkzmwjtbfjjxndmsjpdgimpznzojwfivgjdymtffmwtvzzkmeclquqnzngazmcfvbqfyudpyxlbvbcgyyweaakchxggflbgjplcftssmkssfinffnifsskmsstfclpjgblfggxhckaaewyygcbvblxypduyfqbvfcmzagnznquqlcemkzzvtwmfftmydjgvifwjoznzpmigdpjsmdnxjjfbtjwmzkqxsizkggefvztrsxkkbmbtnmzltbchepwjwgmnnawokaaoivtnoshywmwszqzevywttmaqvncnfkkbdhvpowmspfogrbmuelupcikurdvpoelurggbxqnykjcuoxdrpahmhiezaptabjjulitrilkltoocjpasugfsaarnkyrgbdbmmclmxlzrnjunjsaefkqtxbwoswbfmjimjyergjygzntivgnrpdxuddiidjpjwntqrkoqtjtopgmecapnvfkwzqxilobtyzfmeflqobonxiekvizhlvodvglxbryouahmmjtyyxshsqszvxekj"))