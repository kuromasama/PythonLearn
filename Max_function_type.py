def my_max(a :list) -> int:
    M = int(a[0])
    for i in a:
        if(int(i) > M):
            M=int(i)
    return M

A=input().split()
print(max(A))
print(my_max(A))

