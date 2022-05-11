lin=input().split()
out=[' little, ' ,' little, ',' little Indians', ' little Indian boys.']
for i in range(0,len(lin),3):
    s=''
    for j in range(3):
        if(i+j < len(lin)):
            if(i+j==len(lin)-1):
                s+=lin[i+j]+out[3]
            else:
                s+=lin[i+j]+out[j]
    print(s)
