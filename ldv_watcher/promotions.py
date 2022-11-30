import ldv_dashbot
import logging
import requests
import json
from .utils import sleep
from .config import config
from .hook import process_hooks

from ldv_dashbot.parsers.promo import PromotionParser


def start_promotions_loop(cfg, bot: ldv_dashbot.Bot):
    logging.info("promotions[{}] :: started.".format(cfg['email']))

    cache_file = config.get(
        'promotions_cache', 'data/promotions_{id}.json').format(id=sanitize(cfg['email']))
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
                old_events = set([
                    (e['hash'] if 'hash' in e else PromotionParser._get_event_hash(e))
                    for e in old])
                for e in new:
                    if e['hash'] not in old_events:
                        process_hooks(cfg, 'promotions', 'created', {
                            'event': e,
                        }, render_promotions_)

            with open(cache_file, 'w') as f:
                f.write(json.dumps(new, indent=2))
            sleep(cfg, 'promotions', 5)
        except requests.exceptions.ConnectionError:
            sleep(cfg, 'promotions', 5)
        except:
            import traceback
            traceback.print_exc()
            sleep(cfg, 'error', 120)


def render_promotions_(_tp, _op, data, hook):
    if hook.get('skip_alumni_events', False) and "ANCIENS UNIQUEMENT" in data['event']['labels']:
        return None
    payload = []
    s = set()
    event = data['event']

    if _op == 'created':
        payload += [
            f"**:gift: NOUVEL EVENEMENT PROMOTION: **{event['type']} :gift:",

            "**Nom**",
            f"> {event['title']}",

            "**Date**",
            f"> {event['meta']['calendar']} - {event['meta']['time']}",

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

        if event['description']:
            payload += [
                "**Description**",
                f"> {event['description']}",
            ]

    return [_.replace('\n', '\n> ') for _ in payload]


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
    return json.dumps({k: v for k, v in u.items() if k not in skiplist}, indent=4, ensure_ascii=False)


def renderPath(d, path):
    p = []
    for k in path:
        if isinstance(d, dict) and k not in d:
            break
        d = d[k]
        if isinstance(d, dict):
            p.append("`{}`".format(
                d['name'] if 'name' in d else f"Semester {d['semester']}"))
    return " > ".join(p)
