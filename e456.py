lin=input().split()
out=[' little, ' ,' little Indians']
s=''
for i in range(len(lin)):
    if(i==len(lin)-1):
        s+=lin[i]+out[1]
    else:
        s+=lin[i]+out[0]
print(s)