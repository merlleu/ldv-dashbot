import getpass
import logging
import json
import time
import os
import sys
import ldv_dashbot
import requests
from dictdiffer import diff, patch, swap, revert

logging.basicConfig(level=logging.INFO)

webhook_url = input("Webhook url > ")
bot = ldv_dashbot.Bot(input('Email > '), getpass.getpass("Password > "), cookies_cache="cookies.cache", )
print(f"Connected as {bot.user}")

def send_webhook(c):
    while c:
        buff = []
        length = 0
        while c and length + len(c[0]) < 2000:
            length += len(c[0])
            buff.append(c.pop(0))

        print(requests.post(webhook_url, json = {
            'content': '\n'.join(buff)
        }))
        if c: time.sleep(1)

def recget(u, k):
    for i in k:
        if (isinstance(u, dict) and i in u) or (isinstance(u, list) and i < len(u)):
            u = u[i]
        else:
            return None
    return u

def renderDict(u):
    # return "\n".join([
    #     f"{k}: {v.__repr__() if not (isinstance(v, dict) or isinstance(v, list)) else '[...]'}" for k,v in u.items()
    # ])
    return json.dumps({k:v for k,v in u.items() if not isinstance(v, list)}, indent=4)

def renderPath(d, path):
    p = []
    for k in path:
        d = d[k]
        if isinstance(d, dict):
            p.append("`{}`".format(d['name'] if 'name' in d else f"Semester {d['semester']}"))
    return " > ".join(p)

# Exporting grades 
while True:
    try:
        new = ldv_dashbot.DataClass.json(bot.get_grades())
        with open('grades.json') as f:
            old = json.loads(f.read())

        payload = []

        s = set()
        for op, path, changes in diff(old, new):
            if isinstance(recget(old, path), list): # if is a member of list !
                for i, d in changes:
                    payload.append(
                        f"**---\n{op.upper()}** - {renderPath(new, path + [i])}\n"
                        f"```json\n{renderDict(recget(new, path + [i])) if op == 'add' else renderDict(recget(old, path + [i]))}```"
                    )
            else:
                p = path[:-1] if op == "change" else path
                if str(p) in s:
                    continue
                s.add(str(p))
                payload.append(
                    f"**---\nUPDATE** - {renderPath(new, p)}\n"
                    f"```json\n{renderDict(recget(old, p))}``` "
                    f"```json\n{renderDict(recget(new, p))}```"
                )
        
        # with open('export.md', 'wb') as f:
        #     f.write("\n".join(payload).encode('utf-8'))
        if payload:
            send_webhook(payload)
        with open('grades.json','w') as f:
            f.write(json.dumps(new, indent=2))
        time.sleep(30)
        
    except:
        import traceback
        traceback.print_exc()

        time.sleep(120)