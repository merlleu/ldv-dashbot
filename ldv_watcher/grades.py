import ldv_dashbot
import logging
import requests
import json
from .utils import sleep
from .config import config
from dictdiffer import diff, patch, swap, revert
from .hook import process_hooks

def start_grades_loop(cfg, bot):
    logging.info("grades[{}] :: started.".format(cfg['email']))

    cache_file = config['grades_cache'].format(id = sanitize(cfg['email']))
    while True:
        try:
            new = ldv_dashbot.DataClass.json(bot.get_grades())
            skip = False
            try:
                with open(cache_file) as f:
                    old = json.loads(f.read())
            except:
                # on first run, we don't have a cache file
                # so we only store the new file
                skip = True

            
            if not skip: 
                diffs =  list(diff(old, new))
                process_hooks(cfg, 'grades', 'diff', {
                    'new': new,
                    'old': old,
                    'diffs': diffs
                }, render_grades_)
            
            with open(cache_file,'w') as f:
                f.write(json.dumps(new, indent=2))
            sleep(cfg, 'grades', 5)
        except requests.exceptions.ConnectionError:
            sleep(cfg, 'grades', 5)
        except:
            import traceback
            traceback.print_exc()
            sleep(cfg, 'error', 120)

def render_grades_(_tp, _op, data, hook):
    payload = []
    s = set()
    minor_updates = hook.get('show_minor_updates', False)
    skiplist = hook.get('hidden_fields', [])
    old, new, diffs = data['old'], data['new'], data['diffs']

    for op, path, changes in diffs:
        if isinstance(recget(old, path), list): # if is a member of list !
            for i, d in changes:
                payload.append(
                    f"**---\n{op.upper()}** - {renderPath(new, path + [i])}\n"
                    f"```json\n{renderDict(recget(new, path + [i]), skiplist) if op == 'add' else renderDict(recget(old, path + [i]), skiplist)}```"
                )
        else:
            p = path[:-1] if op == "change" else path
            if str(p) in s:
                continue
            s.add(str(p))
            o = recget(old, p)
            n = recget(new, p)
            if minor_updates or ('promo_average' not in o or 'promo_average' not in n or abs(o['promo_average']-n['promo_average']) > 1):
                payload.append(
                    f"**---\nUPDATE** - {renderPath(new, p)}\n"
                    f"```json\n{renderDict(o, skiplist)}``` "
                    f"```json\n{renderDict(n, skiplist)}```"
                )

    return payload

def sanitize(s):
    return ''.join([(c if c in 'abcdefghijklmnopqrstuvwxyz' else "_") for c in s])


def recget(u, k):
    for i in k:
        if (isinstance(u, dict) and i in u) or (isinstance(u, list) and i < len(u)):
            u = u[i]
        else:
            return None
    return u

def renderDict(u, skiplist=[]):
    return json.dumps({k:v for k,v in u.items() if k not in skiplist}, indent=4, ensure_ascii=False)

def renderPath(d, path):
    p = []
    for k in path:
        if isinstance(d, dict) and k not in d or isinstance(d, list) and k >= len(d):
            break
        d = d[k]
        if isinstance(d, dict):
            p.append("`{}`".format(d['name'] if 'name' in d else f"Semester {d['semester']}"))
    return " > ".join(p)
    