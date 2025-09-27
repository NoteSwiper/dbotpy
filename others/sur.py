from datetime import datetime
from time import time


def pi():
  # Wallis' product
  numerator = 2.0
  denominator = 1.0
  while True:
    yield numerator/denominator
    if numerator < denominator:
      numerator += 2
    else:
      denominator += 2

p = pi()

res = 1.0
for i in range(100000000000):
    res *= next(p)

print(res * 2)