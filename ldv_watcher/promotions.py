import ldv_dashbot
import logging
import requests
import json
from .utils import sleep
from .config import config
from .hook import process_hooks

def start_promotions_loop(cfg, bot: ldv_dashbot.Bot):
    logging.info("promotions[{}] :: started.".format(cfg['email']))

    cache_file = config.get('promotions_cache', 'data/promotions_{id}.json').format(id = sanitize(cfg['email']))
    while True:
        try:
            new = bot.get_promotion_data()
            skip = False
            try:
                with open(cache_file) as f:
                    old = json.loads(f.read())
            except:
                # on first run, we don't have a cache file
                # so we only store the new file
                skip = True

            if not skip: 
                # v1: only track new events
                old_events = set([e['id'] for e in old['events']])
                for e in new['events']:
                    if e['id'] not in old_events:
                        process_hooks(cfg, 'promotions', 'created', {
                            'event': e,
                        }, render_promotions_)
            
            with open(cache_file,'w') as f:
                f.write(json.dumps(new, indent=2))
            sleep(cfg, 'promotions', 5)
        except requests.exceptions.ConnectionError:
            sleep(cfg, 'promotions', 5)
        except:
            import traceback
            traceback.print_exc()
            sleep(cfg, 'error', 120)

def render_promotions_(_tp, _op, data, hook):
    payload = []
    s = set()
    event = data['event']

    if _op == 'created':
        payload += [
            "**:gift: NOUVEL EVENT PROMOTION**",

            "**Nom**",
            f"> {event['title']}",
            "**Description**",
            f"> {event['description']}",
            "**Date**",
            f"> {event['meta']['calendar']}",

            "**Places restantes**",
            f"> {event['registrations']['students']['remaining']} / {event['registrations']['students']['total']}",

            "**Lieu**",
            f"> {event['meta']['map']}"
        ]

        if event['audience']:
            payload += [
                "**Public rencontré**",
                f"> {', '.join(event['audience'])}"
            ]

        if event['labels']:
            payload += [
                "**Labels**",
                f"> {', '.join(event['labels'])}"
            ]

        

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
        if isinstance(d, dict) and k not in d:
            break
        d = d[k]
        if isinstance(d, dict):
            p.append("`{}`".format(d['name'] if 'name' in d else f"Semester {d['semester']}"))
    return " > ".join(p)
    