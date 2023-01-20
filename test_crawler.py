import getpass
import ldv_dashbot
import logging
import json

logging.basicConfig(level=logging.INFO)

# crawler mode
bot = ldv_dashbot.Bot(input('Email > '), getpass.getpass("Password > "), cookies_cache="cookies.cache")
print(f"Connected as {bot.user}")


# Exporting grades 
with open('grades.json', 'wb') as f:
    d = bot.get_grades()
    # src.DataClass.json(d) allows you to transform any kind of data (dict, list, DataClass, and others) to a json-serializable object
    f.write(json.dumps(ldv_dashbot.DataClass.json(d), indent=2).encode('utf-8'))

    # for semester in d:
    #     for unit in semester.units:
    #         for subject in unit.subjects:
    #             if 'evaluation_link' in subject.__dict__:
    #                 print(f"Downloading evaluation for {subject.name}")
    #                 zd = bot.get_evaluation_cours(subject.evaluation_link)
    #                 with open(f'evaluations/{subject.id}.json', 'w') as f:
    #                     f.write(json.dumps(zd))

# with open('promotions.json', 'wb') as f:
#     d = bot.get_promotion_data()
#     f.write(json.dumps(d, indent=2).encode('utf-8'))

# with open('abs.json', 'wb') as f:
#     a = bot.get_abs()
#     f.write(json.dumps(src.DataClass.json(a), indent=2).encode('utf-8'))

# with open('presences.json', 'wb') as f:
#     a = bot.get_day_presences()
#     f.write(json.dumps(src.DataClass.json(a), indent=2).encode('utf-8'))

# for c in a:
#     with open(f'presences_{c.id}.json', 'wb') as f:
#         a = bot.get_seance_presence(c.id)
#         f.write(json.dumps(src.DataClass.json(a), indent=2).encode('utf-8'))