import time
import random
import matplotlib.pyplot as plt

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