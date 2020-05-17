# Standard, third party, and local library imports
import os, random, sqlite3
from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from flask_session import Session

from helpers import get_langInfo
import settings

app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Set global db path
DATABASE = "lab.db"

# Set secret key
app.secret_key = os.getenv("SECRET_KEY")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

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
    """ Homepage """

    if request.method == "POST":
        # Grab the user's choice of lang_id
        lang = request.form["lang"]
        lang_id = query_db("""SELECT id FROM languages WHERE lang = (?)""", (lang,))[0][0]
        return redirect(url_for("tense", lang_id=lang_id))

    else:
        # Fetch languages from db and display in dropdown
        langs = query_db("""SELECT lang FROM languages""")
        return render_template("index.html", langs=langs)

@app.route("/Tense/<int:lang_id>", methods=["GET", "POST"])
def tense(lang_id):
    """ Tense selection """

    if request.method == "POST":

        lang = get_langInfo(lang_id)["language"]

        # Return a redirect to the conjugation route, passing a str of the list of tense_ids
        # List of strings ex) ['1', '2'] for English if Present/Future are chosen
        tenses = request.form.getlist("tense-checkbox")

        # Create a comma seperated string from the submitted tense_ids
        # This will be passed to a hidden form to preserve data
        tenseIds = ",".join(tenses)

        # Think of how the user won't be able to manip the string in the URL
        # Idea: store tenseIds from tense route to a user session
        # Once in the conjugation route, if the tenseIds don't equal that, raise an error
        session["user_tenses"] = tenseIds

        return redirect(url_for("conjugate", lang_id=lang_id, tenseIds=tenseIds))

    else:
        # Dynamically display tenses based on language chosen by user
        # Helper function returns the SQL table based on language id

        # Check if language ID exists
        if get_langInfo(lang_id) == None:
            return "Language ID does not exist"

        lang = get_langInfo(lang_id)["language"]

        tenseTable = get_langInfo(lang_id)["tenseTable"]
        tenses = query_db(f"""SELECT id,tense FROM {tenseTable}""")
        return render_template("tense.html", lang_id=lang_id, lang=lang, tenses=tenses)

@app.route("/Conjugate/<int:lang_id>/<tenseIds>", methods = ["GET", "POST"])
def conjugate(lang_id, tenseIds):
    """ Conjugation Practice """

    if request.method == "POST":
        # Obtain information about the random conjugation and user input
        userConj = request.form["conjugation"]
        verb_id = request.form["verb_id"]
        tense_id = request.form["tense_id"]
        randPos = int(request.form["randPos"])

        lang = get_langInfo(lang_id)["language"]
        
        # Query conjugation table for correct answer
        conjTable = get_langInfo(lang_id)["conjTable"]

        row = query_db(f"""SELECT * FROM {conjTable} WHERE tense_id = (?) AND verb_id = (?)""", (tense_id, verb_id))
        correctConj = row[0][randPos]

        error = None
        if userConj.rstrip().lower() != correctConj:
            error = "The correct conjugation is: " +'"'+ correctConj +'"'
        else:
            flash("Correct!")
            return redirect(url_for("conjugate", lang_id=lang_id, tenseIds=tenseIds))

        # Get same subject pronoun again associated with conjugation
        sPronoun = get_langInfo(lang_id)["subPronouns"][randPos-3]

        # Query for same verb
        verbTable = get_langInfo(lang_id)["verbTable"]
        verbs = query_db(f"""SELECT * FROM {verbTable} WHERE id = (?)""", (verb_id,))
        verb = verbs[0][2].title()

        # Query for same tense
        tenseTable = get_langInfo(lang_id)["tenseTable"]
        tenses = query_db(f"""SELECT * FROM {tenseTable} WHERE id = (?)""", (tense_id,))
        tense = tenses[0][2]

        return render_template("conjugate.html", lang=lang, verb_id=verb_id,
                randPos=randPos, tense_id=tense_id,
                sPronoun=sPronoun, verb=verb, tense=tense, error=error)

    else:
        # Check if tenseIDs are correct
        if tenseIds != session.get("user_tenses"):
            return "Wrong tenseIDs"

        # Check if language ID exists
        if get_langInfo(lang_id) == None:
            return "Language ID does not exist"

        # Dynamically display language
        # Dynamically display conjs based on language chosen by user
        lang = get_langInfo(lang_id)["language"]
        conjTable = get_langInfo(lang_id)["conjTable"]

        # Split tenseIds string on commas into list to pass to db query
        tenseIds = tenseIds.split(",")

        # Format db execution w/ amount of ?s for placeholders of tenseIds
        params = ','.join(['?']*len(tenseIds))

        # Query for all conjugations with those tenseIds
        rows = query_db(f"""SELECT * FROM {conjTable} WHERE tense_id IN ({params})""", (tenseIds))

        randRow = rows[random.randint(0,len(rows)-1)]   # Random subset row from rows
        randPos = random.randint(3, len(randRow)-1)     # Pseudo random position for conjugation within subset row
        verb_id = randRow[1]                            # Verb id from subset row
        tense_id = randRow[2]                           # Tense id from subset row

        # Subject pronoun for conjugation
        sPronoun = get_langInfo(lang_id)["subPronouns"][randPos-3]                 
       
        # Query for verb
        verbTable = get_langInfo(lang_id)["verbTable"]
        verbs = query_db(f"""SELECT * FROM {verbTable} WHERE id = (?)""", (verb_id,))
        verb = verbs[0][2].title()

        # Query tense
        tenseTable = get_langInfo(lang_id)["tenseTable"]
        tenses = query_db(f"""SELECT * FROM {tenseTable} WHERE id = (?)""", (tense_id,))
        tense = tenses[0][2]

        # Pass language, verb, subject pronoun, and tense
        return render_template("conjugate.html", lang=lang, verb=verb, tense=tense,
                sPronoun=sPronoun, verb_id=verb_id, tense_id=tense_id, randPos=randPos)

@app.route("/References")
def references():
    """ Works Cited """
    return render_template("references.html")
