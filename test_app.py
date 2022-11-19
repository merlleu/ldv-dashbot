import getpass
import ldv_dashbot
import logging
import json
import time

logging.basicConfig(level=logging.DEBUG)

# app mode
api = ldv_dashbot.Api(input('Email > '), getpass.getpass("Password > "))
api.get_profile()
time.sleep(5)
with open('profile.json', 'wb') as f:
    user = api.get_profile()
    print(f"Connected as {user}")
    f.write(json.dumps(user, indent=2).encode('utf-8'))

with open('absences.json', 'wb') as f:
    a = api.get_absences()
    f.write(json.dumps(a, indent=2).encode('utf-8'))

with open('presences.json', 'wb') as f:
    a = api.get_presences()
    f.write(json.dumps(a, indent=2).encode('utf-8'))
