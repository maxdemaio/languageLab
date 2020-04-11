from flask import Flask, render_template, request, redirect, url_for, g
import random
import sqlite3
from helpers import tenseTable, verbTable, conjTable

app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Set db path
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

# Query function that combines getting the cursor, executing and fetching the results
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
        print(lang_id)
        print(lang)
        return redirect(url_for("tense", lang_id=lang_id, lang=lang))
    else:
        # Fetch languages from db
        langs = query_db("""SELECT * FROM languages""")

        return render_template("index.html", langs=langs)

@app.route("/<lang_id>/<lang>", methods=["GET", "POST"])
def tense(lang_id, lang):
    if request.method == "POST":
        print(request.form.getlist("tense-checkbox"))
        # Return a redirect to the conjugation route, passing in the list of chosen tenses
        # We can then do a SQL query using the IN specifier to grab those tense rows
        return "TODO"
    else:
        # Dynamically display tenses based on language chosen by user
        langTenses = tenseTable(int(lang_id))
        tenses = query_db(f"""SELECT * FROM {langTenses}""")
        print(tenses)
        return render_template("tense.html", tenses=tenses, lang=lang)
