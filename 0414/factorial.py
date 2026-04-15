import time

def factorial(n):
    ans = 1
    for i in range(1, n+1):
        ans *= i
    return ans

start = time.time()

for n in range(1,1001):
    print(f"결과: {factorial(n)}")
    
end = time.time()
print(f"실행 시간: {(end - start)*1000}ms")
