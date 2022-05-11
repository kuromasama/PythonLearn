lin=input().split()
out=[' little, ' ,' little, ',' little Indians', ' little Indian boys.']
m=0
r=int(len(lin)/10)*2 #m
for i in range(0,len(lin)+r,3):
    i-=m
    s=''
    if((i)%10==9):
        s=lin[i]+out[3]
        m+=2 #動態計算r
        i+=1
    else:    
        for j in range(3):
            if(i+j < len(lin)):
                s+=lin[i+j]+out[j]
    print(s)
