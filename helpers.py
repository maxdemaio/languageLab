# Helper functions for our application

# Choose tables to pull verbs, tenses, and conjugations based on the language id
def get_langInfo(lang_id):
    if lang_id == 1:
        return {"language": "English", "tenseTable": "en_tense", "verbTable": "en_verb", 
        "conjTable": "en_conj", "subPronouns": ["I", "You", "He/She/It/One", "We", "You/You all", "They"]}
    else:
        return None

def main():
    class Language:

        counter = 1

        def __init__(self, language, lang_id, tenseTable, verbTable, conjTable, subPronouns):
            self.language = language
            self.lang_id = lang_id
            self.tenseTable = tenseTable
            self.verbTable = verbTable
            self.conjTable = conjTable
            self.subPronouns = subPronouns

            Language.counter += 1

        def print_info(self):
            print(f"Language: {self.language}")
            print(f"Language ID: {self.lang_id}")
            print(f"Language Tense Table: {self.tenseTable}")
            print(f"Language Verb Table: {self.verbTable}")
            print(f"Language Conjugation Table: {self.conjTable}")
            print(f"Language Subject Pronouns: {self.subPronouns}")
            print()

    # Language instances
    english = Language(lang_id=1, language= "English", tenseTable="en_tense", 
        verbTable="en_verb", conjTable="en_conj", 
        subPronouns = ["I", "You", "He/She/It/One", "We", "You/You all", "They"])

    english.print_info()

if __name__ == "__main__":
    main()
