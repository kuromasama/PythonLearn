lin=input().split()
out=[' little, ' ,' little Indians ',' little Indian boys.']
s=''
for i in range(len(lin)):
    if((i+1)%10==0):
        s+=lin[i]+out[2]
    elif((i+1)%3==0):
        s+=lin[i]+out[1]
    else:
        s+=lin[i]+out[0]
print(s)