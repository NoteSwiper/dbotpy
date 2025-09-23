import re


def file_to_list(fpath):
    with open(fpath, 'r') as f:
        lines = f.readlines()
    
    cleand = [line.strip() for line in lines]
    
    return cleand

data = file_to_list("./others/censored_words.profanity")

def censor(text: str):
    for profanity in data:
        text = re.sub(profanity, "*", text, flags=re.IGNORECASE)
    
    return text