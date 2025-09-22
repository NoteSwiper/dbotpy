import time
import random
import matplotlib.pyplot as plt

target = random.uniform(20,50)
current = random.uniform(-50,50)

history = []

while abs(current - target) > 0.1:
    diff = target - current
    step = diff * random.uniform(0.1,0.9)
    current += step
    
    history.append(current)
    
    time.sleep(0.5)

plt.figure(figsize=(10,6))
plt.plot(history, label="Current")
plt.axhline(y=target, color='r', label="target")
plt.title("Variance")
plt.xlabel("Steps")
plt.ylabel("Value")
plt.legend()
plt.grid(True)
plt.savefig("output.png")