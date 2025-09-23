
from datetime import datetime
import time
import random
import matplotlib.pyplot as plt

import stuff

"""
def approach_target(target: float):
    current = random.uniform(target-1,target+1)
    history = [current]
    iterations = 0
    
    while  iterations < 50:
        diff = target - current
        
        step = diff*random.uniform(0.1,0.9)*3.5
        current+= step
        
        history.append(current)
        iterations += 1
    
    return history

histories = [approach_target(20) for _ in range(10)]

plt.figure(figsize=(12,8))
for i, his in enumerate(histories):
    plt.plot(his, label=f'Attempt {i+1}')

plt.axhline(y=20, color='r', label="Target")
plt.title("Varience")
plt.xlabel('Steps')
plt.ylabel('Value')
plt.legend(loc='lower right')
plt.grid(True)
plt.savefig('output.png')
"""

"""
concurrents = 16
target_value = 20

conc = stuff.clamp(concurrents or 1, 1, 20)
histories = [stuff.approach_target(target_value or 20) for _ in range(conc)]

plt.figure(figsize=(12,8))
for i, his in enumerate(histories):
    plt.plot(his, label=f"Attempt {i+1}")

plt.axhline(y=target_value or 20, color='r', linestyle='--', label="Target")
plt.title(f"Target close algorithm on {datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}, with {conc} parallels")
plt.xlabel("Steps")
plt.ylabel("Value")
plt.legend(loc='lower right')
plt.grid(True)

plt.savefig('output.png')

plt.close()
"""

total = 1
delay = 10

delay2 = delay / 1000

iterations = int(total/delay2)

print(iterations)

results = stuff.get_latency_from_uhhh_time(delay, iterations)

plt.style.use('dark_background')
plt.figure(figsize=(12,8))

plt.plot(results,linestyle='-', color='b', label="Estimated")

plt.axhline(y=(sum(results)/len(results)), color='r', linestyle='--', label="Avg.")
plt.title(f"Computer Latency on {datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}")
plt.xlabel("Steps")
plt.ylabel("Milliseconds")
plt.legend(loc='lower right')
plt.grid(True)
plt.tight_layout()
plt.savefig('output.png')