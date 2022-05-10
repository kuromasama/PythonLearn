inp=input()
s=""
for i in range(len(inp)):
    if(i==0 or (i==len(inp)-1)):
        s+=inp[i]
    else:
        s+='_'
print(s)
