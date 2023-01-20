import getpass
import ldv_dashbot
import logging
import json

logging.basicConfig(level=logging.INFO)

# crawler mode
bot = ldv_dashbot.Bot(input('Email > '), getpass.getpass("Password > "), cookies_cache="cookies.cache")
print(f"Connected as {bot.user}")


grades = bot.get_grades()

niveaux="""
Niveaux: (par défaut: {})
0: Pas du tout
1: Non
2: Plutôt pas
3: Plutôt
4: Oui
5: Tout à fait
"""

last = 3 # 0-5

def get_lvl():
    global last
    print(niveaux.format(last))
    lvl = input("Niveau > ")
    if lvl == "":
        lvl = last
    lvl = int(lvl)
    if lvl < 0 or lvl > 5:
        print("Niveau invalide")
        return get_lvl()
    last = lvl
    return lvl


for semester in grades:
    for unit in semester.units:
        for subject in unit.subjects:
            if 'evaluation_link' in subject.__dict__:
                print(f"Downloading evaluation for [S{semester.semester}] {subject.name}")
                zd = bot.get_evaluation_cours(subject.evaluation_link)
                inputs = {}
                l = get_lvl()
                for question in zd:
                    if question['type'] == 'radio':
                        
                        inputs[question['name']] = question['options'][l]
                    else:
                        inputs[question['name']] = question['value']
                print(inputs)
                r = bot.send_cours_upload_raw(inputs)
                print(r)