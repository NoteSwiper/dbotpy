import markovify

with open("./others/test.txt") as f:
    text = f.read()

model = markovify.Text(text, state_size=2)

print(model.make_sentence())