# Helper functions for our application

# Choose tables to pull verbs, tenses, and conjugations based on the language id
def tenseTable(lang_id):
    if lang_id == 1:
        return "en_tense"
    else:
        pass

def verbTable(lang_id):
    if lang_id == 1:
        return "en_verb"
    else:
        pass

def conjTable(lang_id):
    if lang_id == 1:
        return "en_conj"
    else:
        pass

def subPronouns(lang_id):
    if lang_id == 1:
        return ["I", "You", "He/She/It/One", "We", "You/You all", "They"]
    else:
        pass

def main():
    class Language:
        # Allows us to keep track of number of langs, corresponds with lang_id
        counter = 1

        def __init__(self, lang_id, tenseTable, verbTable, conjTable, subPronouns):
            self.lang_id = lang_id
            self.tenseTable = tenseTable
            self.verbTable = verbTable
            self.conjTable = conjTable
            self.subPronouns = subPronouns

            Language.counter += 1

        def print_info(self):
            print(f"Language ID: {self.lang_id}")
            print(f"Language Tense Table: {self.tenseTable}")
            print(f"Language Verb Table: {self.verbTable}")
            print(f"Language Conjugation Table: {self.conjTable}")
            print(f"Language Subject Pronouns: {self.subPronouns}")

    # Define our instances
    english = Language(lang_id=1, tenseTable="en_tense", verbTable="en_verb", conjTable="en_conj",
            subPronouns = ["I", "You", "He/She/It/One", "We", "You/You all", "They"])

if __name__ == "__main__":
    main()
