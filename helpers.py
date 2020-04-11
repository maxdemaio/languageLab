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
