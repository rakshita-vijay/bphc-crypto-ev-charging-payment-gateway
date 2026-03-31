import math
import random

def period(a, n):
    #Objective: Find r such that a^r = 1 mod n
    #This would normally be done with a quantum computer, but I'm doing it classically for demonstration
    r = 1
    value = a % n
    while value != 1:
        value = (value * a) % n
        r += 1
        #Safety limit
        if r > n:
            return None
    return r

def shor_algorithm(n):
    #If we got an even number, just return 2 and n/2 as the factors
    if n % 2 == 0:
        return 2, n // 2
    
    #Giving n retries to factorize, a retry will fail if we can't find a valid period
    for attempt in range(10):
        a = random.randint(2, n-1)

        gcd = math.gcd(a, n)
        if gcd != 1:
            return gcd, n // gcd
        
        r = period(a, n)

        if r is None or r % 2 == 1:
            continue

        factor1 = math.gcd(pow(a, r // 2) - 1, n)
        factor2 = math.gcd(pow(a, r // 2) + 1, n)

        #Make sure the factors we got aren't 1, n
        if factor1 != 1 & factor1 != n:
            return factor1, factor2
        
    return None