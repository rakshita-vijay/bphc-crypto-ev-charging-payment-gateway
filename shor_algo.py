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

  #Giving 10 retries to factorize, a retry will fail if we can't find a valid period
  for attempt in range(10):
    a = random.randint(2, n-1)

    gcd = math.gcd(a, n)
    if gcd != 1:
      return gcd, n // gcd

    r = period(a, n)

    if r is None or r % 2 != 0:
      continue

    factor1 = math.gcd(pow(a, r // 2) - 1, n)
    factor2 = math.gcd(pow(a, r // 2) + 1, n)

    #Make sure the factors we got aren't 1, n
    if factor1 != 1 and factor1 != n:
      return factor1, factor2

  return None

def generate_rsa_keypair():
  #Generate the keypair, but with small values of p and q.
  #The keypair is intentionally weak to demonstrate Shor's algo
  p, q = 61, 53 #random small primes for now
  N = p * q
  e = 17
  phi = (p-1) * (q-1)
  d = pow(e, -1, phi)

  public_keypair = (e, N)
  private_keypair = (d, N)
  return public_keypair, private_keypair, p, q

def demonstrate_attack():
  public_key, private_key, original_p, original_q = generate_rsa_keypair()
  e, N = public_key

  print(f"RSA Public Key: e={e}, N={N}")
  print(f"Attacker only knows N={N}. Attempting to factor it,")

  result = shor_algorithm(N)

  if result:
    found_p, found_q = result
    print(f"Shor's algorithm recovered factors: p={found_p}, q={found_q}")
    print(f"Original factors were:              p={original_p}, q={original_q}")

    # Reconstruct private key from broken factors
    phi = (found_p - 1) * (found_q - 1)
    recovered_d = pow(e, -1, phi)
    print(f"Private key recovered: d={recovered_d}")
    print(f"Original private key:  d={private_key[0]}")
    print("RSA encryption is BROKEN for this key.")
  else:
    print("Factoring failed.")

if __name__ == "__main__":
  demonstrate_attack()