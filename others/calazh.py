import re

# --- Calazh Lexicon and Grammar Rules ---
# EXPANDED LEXICON with support for SVOC structure elements.
# Calazh is defined by the following characters: e̊, ṅ, p̅, ō, ẽ, ī, ū, ā, ñ, t̃, r̃, ć.

ENGLISH_TO_CALAZH = {
    # Greetings & Articles
    "hi": "e̊lcan",
    "hello": "e̊lcanol",
    "the": "", "a": "", "an": "",

    # Pronouns & Subjects
    "i": "zē", "me": "zē", "you": "lū", "we": "mūr",
    "they": "sūt", "he": "fē", "she": "fī", "it": "yān",
    "person": "côza", "people": "côza",

    # Nouns & Objects
    "tv": "côsōl", "phone": "lalcolp̅an", "water": "niṅa", "screen": "côs",
    "sun": "dērā", "moon": "luna", "sky": "niṅān", "wind": "gāl",
    "mountain": "cālīp", "tree": "ṅan", "stone": "pal", "star": "tīr",
    "idea": "lēca", "time": "zōl", "color": "mūrīn", "day": "cōst", "night": "cāst",

    # Verbs (Tense/Aspect specific mapping)
    # Watching/Seeing
    "watch": "dẽlsiṅca", "watching": "dẽlsiṅpau", "watched": "dẽlsiṅrū",
    "see": "cēna", "seeing": "cēnpau", "saw": "cēnrū",

    # Action
    "eat": "målca", "eating": "målpau", "ate": "målrů",
    "go": "tãca", "going": "tãpau", "went": "tãrū",
    "run": "rũsca", "running": "rũspau", "ran": "rũsrū",
    "speak": "fãca", "speaking": "fãpau", "spoke": "fãrū",
    "sleep": "ćēca", "sleeping": "ćēpau", "slept": "ćērū",

    # SVOC Verbs (New)
    "consider": "mārīca", "considering": "mārīpau", "considered": "mārīrū",
    "make": "ñīca", "making": "ñīpau", "made": "ñīrū",

    # Helping verbs/Copulas (Dropped in Calazh)
    "am": "", "is": "", "are": "", "was": "", "were": "", "to": "",

    # Adjectives/Complements (New set)
    "big": "col", "small": "sîng", "fast": "ēdan", "slow": "mūlan",
    "bright": "fīr", "dark": "nīr", "good": "būl", "bad": "cūl",
    "happy": "rīnt", "strong": "t̃āl", "cold": "r̃ēd", "warm": "ćūn",

    # Numbers
    "one": "dal", "1": "dal", "two": "vẽn", "2": "vẽn",
    "three": "tī", "3": "tī", "four": "ćar", "five": "mū",

    # Prepositions (simple)
    "in": "dēl", "on": "tãn", "with": "lī",
}

# Generate the reverse dictionary for Calazh -> English translation
CALAZH_TO_ENGLISH = {v: k for k, v in ENGLISH_TO_CALAZH.items() if v}


# Define sets of common parts of speech for simple parsing (updated)
SUBJECTS = {"i", "you", "person", "people", "we", "they", "he", "she", "it",
            "zē", "lū", "côza", "mūr", "sūt", "fē", "fī", "yān"}
VERBS = {"watch", "watching", "watched", "eat", "eating", "ate", "see", "seeing", "saw",
         "go", "going", "went", "run", "running", "ran", "speak", "speaking", "spoke",
         "sleep", "sleeping", "slept", "consider", "considering", "considered", "make", "making", "made",
         "dẽlsiṅca", "dẽlsiṅpau", "dẽlsiṅrū", "målca", "målpau", "målrů", "tãca", "tãpau",
         "tãrū", "rũsca", "rũspau", "rũsrū", "cēna", "cēnpau", "cēnrū", "fãca", "fãpau", "fãrū",
         "ćēca", "ćēpau", "ćērū", "mārīca", "mārīpau", "mārīrū", "ñīca", "ñīpau", "ñīrū"}
OBJECTS = {"tv", "phone", "water", "côsōl", "lalcolp̅an", "niṅa", "dērā", "luna", "niṅān",
           "gāl", "cālīp", "ṅan", "pal", "tīr", "lēca", "zōl", "cōst", "cāst", "mūrīn"}
COMPLEMENTS = {"big", "small", "fast", "slow", "bright", "dark", "good", "bad",
               "happy", "strong", "cold", "warm", "col", "sîng", "ēdan", "mūlan",
               "fīr", "nīr", "būl", "cūl", "rīnt", "t̃āl", "r̃ēd", "ćūn"}
GREETINGS = {"hi", "hello", "e̊lcan", "e̊lcanol"}


def clean_and_tokenize(text):
    """
    Converts input text to a list of lowercase tokens, stripping punctuation.
    """
    calazh_chars = 'e̊ṅp̅ōẽīūāñt̃r̃ć'
    pattern = r'[^\w\s' + re.escape(calazh_chars) + r']'
    text = re.sub(pattern, '', text).lower()
    return text.split()


def translate_english_to_calazh(english_text):
    """
    Translates English (SVO or SVOC) to Calazh (OVS or OVCS) by reordering.
    """
    tokens = clean_and_tokenize(english_text)

    if not tokens:
        return "..."

    if tokens[0] in GREETINGS:
        return ENGLISH_TO_CALAZH.get(tokens[0], tokens[0])

    # 2. Attempt to parse SVOC
    subject, verb, obj, complement = None, None, None, None
    remaining_words = []

    for token in tokens:
        if token in SUBJECTS and not subject:
            subject = token
        elif token in VERBS and not verb:
            verb = token
        elif token in OBJECTS and not obj:
            obj = token
        elif token in COMPLEMENTS and not complement:
            complement = token
        elif token in ENGLISH_TO_CALAZH:
            # Drop articles or helping verbs
            if ENGLISH_TO_CALAZH[token] != "":
                remaining_words.append(ENGLISH_TO_CALAZH[token])
        else:
            remaining_words.append(token) # Keep unknown words as is

    # Translate the identified S, V, O, C
    c_s = ENGLISH_TO_CALAZH.get(subject, subject) if subject else None
    c_v = ENGLISH_TO_CALAZH.get(verb, verb) if verb else None
    c_o = ENGLISH_TO_CALAZH.get(obj, obj) if obj else None
    c_c = ENGLISH_TO_CALAZH.get(complement, complement) if complement else None

    # Apply O V C S structure if SVOC parts are found
    if c_s and c_v and c_o and c_c:
        # Calazh SVOC equivalent: Object Verb Complement Subject
        calazh_sentence = [c_o, c_v, c_c, c_s] + remaining_words
        return " ".join([word for word in calazh_sentence if word])

    # Apply O V S structure if only SVO parts are found
    elif c_s and c_v and c_o:
        # Calazh SVO equivalent: Object Verb Subject
        calazh_sentence = [c_o, c_v, c_s] + remaining_words
        return " ".join([word for word in calazh_sentence if word])

    # If parsing failed, fall back to simple word-by-word translation
    else:
        translated_words = [ENGLISH_TO_CALAZH.get(token, token) for token in tokens if ENGLISH_TO_CALAZH.get(token, token) != ""]
        return " ".join(translated_words)


def translate_calazh_to_english(calazh_text):
    """
    Translates Calazh to English using direct word-by-word lookup.
    """
    tokens = clean_and_tokenize(calazh_text)

    translated_words = []
    for token in tokens:
        english_word = CALAZH_TO_ENGLISH.get(token, token)
        translated_words.append(english_word)

    # Attempt to improve readability by capitalizing the start
    output = " ".join(translated_words)
    return output.capitalize()


def translate_calazh(text):
    """Main function to determine translation direction."""
    if not text:
        return "Please enter text to translate!"

    # Check for Calazh's unique characters to guess the source language
    is_calazh = any(char in text for char in 'e̊ṅp̅ōẽīūāñt̃r̃ć')

    if is_calazh:
        print("Translating Calazh -> English...")
        result = translate_calazh_to_english(text)
    else:
        print("Translating English -> Calazh (Applying OVS/OVCS rule)...")
        result = translate_english_to_calazh(text)

    return result


if __name__ == "__main__":
    print("--- Calazh Simple Translator (SVOC/OVS Support) ---")
    print("Try English SVOC: 'I consider the phone good'")
    print("Expected OVCS: 'lalcolp̅an mārīca būl zē'")
    print("Try English SVO: 'He ate two trees'")
    print("Expected OVS: 'ṅan målrů fē'")
    print("--------------------------------")

    while True:
        user_input = input("\nEnter text (or 'quit' to exit): ").strip()
        if user_input.lower() == 'quit':
            print("\nGoodbye! e̊lcanol! :3")
            break

        # Display the result
        translation = translate_calazh(user_input)
        print(f"Calazh/English: {translation}")
