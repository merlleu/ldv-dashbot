import logging
import time
import requests
import json



def process_hooks(cfg, tp, op, data, renderer):
    logging.debug("processing hook {}.".format(json.dumps({'tp': tp, 'op': op, 'data': data})))
    for hook in cfg['hooks']:
        for trigger in hook['triggers']:
            if trigger['type'] == tp and (op in trigger['events'] or '*' in trigger['events']):
                rendered = renderer(tp, op, data, trigger)
                
                if rendered:
                    if hook['mode'] == 'DiscordWebHookV1':
                        send_discord_webhook(hook['url'], rendered)
                    elif hook['mode'] == 'TelegramBotV1':
                        send_telegram_bot(hook['telegram'], rendered)
                    else:
                        logging.error(
                            'unknown hook mode : {}, expected '
                            'DiscordWebHookV1 or TelegramBotV1'.format(hook['mode']))

def are_rules_matched(s, rules):
    for i in rules:
        if i == s or (i.endswith('*') and s.startswith(i[:-1])): return True
    return False


def send_discord_webhook(url, c):
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

def send_telegram_bot(tg, c):
    c = preprocess_message_for_telegram(c)
    while c:
        if len(c[0]) >= 1900: return logging.error('payload too long !')
        buff = []
        length = 0
        while c and length + len(c[0]) < 2000:
            length += len(c[0])
            buff.append(c.pop(0))
        
        url = 'https://api.telegram.org/bot{}/sendMessage'.format(tg['token'])
        j = {
            'chat_id': tg['chat_id'],
            'text': '\n'.join(buff),
            'parse_mode': 'MarkdownV2'
        }
        logging.debug('send_telegram_bot : {}'.format(url))
        logging.debug('send_telegram_bot : {}'.format(json.dumps(j)))
        r = requests.post(url, json=j)
        if r.status_code != 200:
            logging.error('send_webhook : ({}) - {}'.format(r.status_code, r.text))
        time.sleep(1)

def preprocess_message_for_telegram(c):
    rp = {
        '**': '*',
        '>': '\\>',
        '_': '\\_',
        '-': '\\-',
        '<': '\\<',
        '#': '\\#',
        '+': '\\+',
        '=': '\\=',
        '/': '\\/',
        '.': '\\.',
    }
    for i in range(len(c)):
        s = c[i]
        for k,v in rp.items():
            s = s.replace(k, v)
        c[i] = s
    return c