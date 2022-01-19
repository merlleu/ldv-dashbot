import getpass
import src
import logging
import json

logging.basicConfig(level=logging.INFO)

bot = src.Bot(input('Email > '), getpass.getpass("Password > "), cookies_cache="cookies.cache")
print(f"Connected as {bot.user}")



# Exporting grades 
with open('grades.json', 'wb') as f:
    d = bot.get_grades()
    # src.DataClass.json(d) allows you to transform any kind of data (dict, list, DataClass, and others) to a json-serializable object
    f.write(json.dumps(src.DataClass.json(d), indent=2).encode('utf-8'))

with open('abs.json', 'wb') as f:
    a = bot.get_abs()
    f.write(json.dumps(src.DataClass.json(a), indent=2).encode('utf-8'))
