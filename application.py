# Standard library imports
import os
import random
import sqlite3

# Third party imports
from flask import Flask, flash, g, redirect, render_template, request, url_for

# Local application imports
from helpers import conjTable, subPronouns, tenseTable, verbTable

app = Flask(__name__)
app.secret_key = b'\xfb\xf63g\x81p\x99\xbe\x92T\x84\xaf\xa1\x0c\x85\x8a\x08\xd3\x9a\xb9\x99\x8d\x83'

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Set global db path
DATABASE = "lab.db"

# Open db connection on demand
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# Close db when context dies
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Query function that combines getting the cursor, executing and fetching all results
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Grab the user's choice of lang_id/language, redirect
        lang_id = query_db("""SELECT id FROM languages WHERE lang = (?)""", (request.form["lang"],))[0][0]
        lang = request.form["lang"]

        return redirect(url_for("tense", lang_id=lang_id, lang=lang))
    else:
        # Fetch languages from db
        langs = query_db("""SELECT * FROM languages""")

        return render_template("index.html", langs=langs)

@app.route("/<lang_id>/<lang>", methods=["GET", "POST"])
def tense(lang_id, lang):
    if request.method == "POST":
        # Return a redirect to the conjugation route, passing a str of the list of tense_ids
        # List of strings ex) ['1', '2'] when first two are checked
        tenses = request.form.getlist("tense-checkbox")

        # Create a comma seperated string from the submitted tense_ids
        commaSeperated = ",".join(tenses)

        return redirect(url_for("conjugate", lang_id=lang_id, lang=lang, tenseIds=commaSeperated))
    else:
        # Dynamically display tenses based on language chosen by user
        langTenses = tenseTable(int(lang_id))
        tenses = query_db(f"""SELECT * FROM {langTenses}""")

        return render_template("tense.html", lang_id=lang_id, lang=lang, tenses=tenses)

@app.route("/<lang_id>/<lang>/Conjugate/<tenseIds>", methods = ["GET", "POST"])
def conjugate(lang_id, lang, tenseIds):
    if request.method == "POST":
        # Obtain information about the random conjugation and user input
        userConj = request.form["conjugation"]
        verb_id = request.form["verb_id"]
        tense_id = request.form["tense_id"]
        sPronounPos = request.form["sPronounPos"]

        # Query conjugation table for correct answer
        langConjs = conjTable(int(lang_id))
        row = query_db(f"""SELECT * FROM {langConjs} WHERE tense_id = (?) AND verb_id = (?)""", (tense_id, verb_id))
        correctConj = row[0][int(sPronounPos)]

        error = None
        print(userConj)
        print(correctConj)

        if userConj.rstrip().lower() != correctConj:
            error = "The correct conjugation is " + correctConj
        else:
            flash("Correct!")
            return redirect(url_for("conjugate", lang=lang, lang_id=lang_id, tenseIds=tenseIds))

        # basically another GET right here
        # Repeat info so user can practice

        # Get same subject pronoun again
        sPronoun = subPronouns(int(lang_id))[int(sPronounPos) - 3]

        # Query for same verb
        langVerbs = verbTable(int(lang_id))
        verbs = query_db(f"""SELECT * FROM {langVerbs} WHERE id = (?)""", (verb_id,))
        verb = verbs[0][2].title()

        # Query for same tense
        langTenses = tenseTable(int(lang_id))
        tenses = query_db(f"""SELECT * FROM {langTenses} WHERE id = (?)""", (tense_id,))
        tense = tenses[0][2]

        return render_template("conjugate.html", lang=lang, verb_id=verb_id,
                sPronounPos=sPronounPos, tense_id=tense_id,
                sPronoun=sPronoun, verb=verb, tense=tense, error=error)

    else:
        # Dynamically display conjs based on language chosen by user
        langConjs = conjTable(int(lang_id))

        # Split tenseIds string on commas into list to pass to db query
        tenseIds = tenseIds.split(",")

        # Format db execution w/ amount of ?s we will need so there will be no injections
        params = ','.join(['?']*len(tenseIds))

        # We can then do a SQL query using the IN specifier to grab those tense rows
        rows = query_db(f"""SELECT * FROM {langConjs} WHERE tense_id IN ({params})""", (tenseIds))

        # Note SQL starts id arrays at 1
        randRow = rows[random.randint(0,len(rows)-1)]   # Random subset row from rows
        randPos = random.randint(3, len(randRow[3:]))   # Pseudo random position for conj within subset row
        randConj = randRow[randPos]                     # Random conj from subset row
        verb_id = randRow[1]                            # Verb id from subset row
        tense_id = randRow[2]                           # Tense id from subset row
        sPronouns = subPronouns(int(lang_id))           # List of subject pronouns based on lang_id
        sPronoun = sPronouns[randPos-3]                 # Subject pronoun for conjugation

        # Query for verb
        langVerbs = verbTable(int(lang_id))
        verbs = query_db(f"""SELECT * FROM {langVerbs} WHERE id = (?)""", (verb_id,))
        verb = verbs[0][2].title()

        # Query  tense
        langTenses = tenseTable(int(lang_id))
        tenses = query_db(f"""SELECT * FROM {langTenses} WHERE id = (?)""", (tense_id,))
        tense = tenses[0][2]

        # Pass language, verb, subject pronoun, and tense
        return render_template("conjugate.html", lang=lang, verb=verb, tense=tense,
                sPronoun=sPronoun, verb_id=verb_id, tense_id=tense_id, sPronounPos=randPos)
