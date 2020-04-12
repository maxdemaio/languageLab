import sqlite3
import csv

conn = sqlite3.connect(':memory:')

db = conn.cursor()
db.execute("""CREATE TABLE languages (
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        lang TEXT NOT NULL
        )""")

db.execute("""CREATE TABLE en_tense (
        lang_id INTEGER NOT NULL,
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        tense TEXT NOT NULL,
        FOREIGN KEY(lang_id) REFERENCES en_tense(id)
        )""")

db.execute("""CREATE TABLE en_verb (
        lang_id INTEGER NOT NULL,
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        verb TEXT NOT NULL,
        FOREIGN KEY(lang_id) REFERENCES en_tense(id)
        )""")

db.execute("""CREATE TABLE en_conj (
        lang_id INTEGER NOT NULL,
        verb_id INTEGER NOT NULL,
        tense_id INTEGER NOT NULL,
        "sing_1" TEXT,
        "sing_2" TEXT,
        "sing_3" TEXT,
        "plural_1" TEXT,
        "plural_2" TEXT,
        "plural_3" TEXT,
        FOREIGN KEY(lang_id) REFERENCES en_tense(id),
        FOREIGN KEY(verb_id) REFERENCES en_verb(id),
        FOREIGN KEY(tense_id) REFERENCES en_tense(id)
        )""")

# Insert data into the en_conj table in our db
with open('en_data/en_conjs.csv') as csvFile:
    reader = csv.DictReader(csvFile)
    for row in reader:
        lang_id = row['lang_id']
        verb_id = row['verb_id']
        tense_id = row['tense_id']
        sing_1 = row['sing_1']
        sing_2 = row['sing_2']
        sing_3 = row['sing_3']
        plural_1 = row['plural_1']
        plural_2 = row['plural_2']
        plural_3 = row['plural_3']

        db.execute("""INSERT INTO en_conj (lang_id, verb_id, tense_id, sing_1, sing_2, sing_3, plural_1, plural_2, plural_3)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (lang_id, verb_id, tense_id, sing_1, sing_2, sing_3, plural_1, plural_2, plural_3))

# Insert data into the en_verb table in our db
with open('en_data/en_verbs.csv') as csvFile:
    reader = csv.DictReader(csvFile)
    for row in reader:
        lang_id = row['lang_id']
        en_verb = row['verb']

        db.execute("""INSERT INTO en_verb (lang_id, verb) VALUES(?, ?)""", (lang_id, en_verb))

# Insert data into the en_tense table in our db
with open('en_data/en_tenses.csv') as csvFile:
    reader = csv.DictReader(csvFile)
    for row in reader:
        lang_id = row['lang_id']
        en_tense = row['tense']

        db.execute("""INSERT INTO en_tense (lang_id, tense) VALUES(?, ?)""", (lang_id, en_tense))

# Insert data into the languages table in our db
with open('languages.csv') as csvFile:
    reader = csv.DictReader(csvFile)
    for row in reader:
        lang = row['language']

        db.execute("""INSERT INTO languages (lang) VALUES(?)""", (lang,))

# Practice select
db.execute("""SELECT * FROM en_verb""")
#db.execute("""SELECT * FROM en_conj WHERE tense_id IN (1, 2, 3)""")
print(db.fetchall())


# Commit current transaction
conn.commit()

# Close the connection
conn.close()
