"""Simple error model for exact 32-bit recovery. A bit with d differing chips errs with probability Q(sqrt(d)*x), x = chip s/n."""
import math
D=[4,7,4,4,6,4,4,2,8,5,2,8,5,5,4,6,8,6,6,7,3,5,7,7,5,5,6,5,5,7,7,4]
Q=lambda z:.5*math.erfc(z/math.sqrt(2))
def solve(f,target=.8):
    lo,hi=.01,5.
    for _ in range(80):
        m=(lo+hi)/2
        if f(m)<target: lo=m
        else: hi=m
    return hi
cur=lambda x:math.prod(1-Q(math.sqrt(d)*x) for d in D)
mean=sum(math.sqrt(d) for d in D)/32
eq=lambda x:(1-Q(mean*x))**32   # same total chip signal spread so every bit is equally safe (approximation)
anti=lambda x:(1-Q(math.sqrt(10)*x))**32
a,b,c=solve(cur),solve(eq),solve(anti)
print("s/n for P(exact)=.8: current %.3f; equalized %.3f (%.1f dB); all distance 10 %.3f (%.1f dB)"%(a,b,20*math.log10(a/b),c,20*math.log10(a/c)))
