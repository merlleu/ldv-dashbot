import logging
import time
import requests
import json
def send_webhook(url, c):
    while c:
        if len(c[0]) >= 1900: return logging.error('payload too long !')
        buff = []
        length = 0
        while c and length + len(c[0]) < 2000:
            length += len(c[0])
            buff.append(c.pop(0))
        logging.info('send_webhook : {}'.format(requests.post(url, json = {
            'content': '\n'.join(buff)
        })))
        if c: time.sleep(1)

def process_hooks(cfg, tp, op, data, renderer):
    logging.debug("processing hook {}.".format(json.dumps({'tp': tp, 'op': op, 'data': data})))
    for hook in cfg['hooks']:
        for trigger in hook['triggers']:
            if trigger['type'] == tp and (op in trigger['events'] or '*' in trigger['events']):
                rendered = renderer(tp, op, data, trigger)
                
                if rendered:
                    send_webhook(hook['url'], rendered)

def are_rules_matched(s, rules):
    for i in rules:
        if i == s or (i.endswith('*') and s.startswith(i[:-1])): return True
    return False
