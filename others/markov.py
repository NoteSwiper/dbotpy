import sys
import markovify

data = []

class poopers(markovify.Text):
    def word_split(self, sentence):
        return list(sentence)
    
    def word_join(self, words):
        return "".join(words)

with open("./markov-texts/2.txt") as f:
    text = f.read()
    data = f.readlines()

model = markovify.Text(text, state_size=2)

if len(sys.argv) > 1 and sys.argv[1] and int(sys.argv[1]):
    for i in range(int(sys.argv[1])):
        while True:
            temp = model.make_sentence()
            if not temp in data:
                print(temp)
                break
            print("Found existing line. regenerating...")
else:
    while True:
        temp = model.make_sentence()
        if not temp in data:
            print(temp)
            break
        print("the line exists. regenerating...")