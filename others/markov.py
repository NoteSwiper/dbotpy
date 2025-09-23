import sys
import markovify

with open("./others/markov.txt") as f:
    text = f.read()

model = markovify.Text(text, state_size=2)

if len(sys.argv) > 1 and sys.argv[1] and int(sys.argv[1]):
    for i in range(int(sys.argv[1])):
        print(model.make_sentence())
else:
    print(model.make_sentence())