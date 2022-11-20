from .config import config
import logging
import ldv_dashbot
import threading
from .grades   import start_grades_loop
from .presence import start_presence_loop
from .promotions import start_promotions_loop

def start_account(account):
    logging.info(f"Starting account {account['email']}")
    tasks = set()
    use_scrapper = False
    for hook in account['hooks']:
        for trigger in hook['triggers']:
            if trigger['type'] == 'presence':
                tasks.add('presence')
            elif trigger['type'] == 'grades':
                tasks.add('grades')
                use_scrapper = True
            elif trigger['type'] == 'promotions':
                tasks.add('promotions')
                use_scrapper = True
    
    if 'presence' in tasks:
        threading.Thread(target=start_presence_loop, args=(account,), name = f"presence-{account['email']}").start()
    
    bot = None if not use_scrapper else create_scrapper(account)
    if 'grades' in tasks:
        threading.Thread(target=start_grades_loop, args=(account,bot), name = f"grades-{account['email']}").start()

    if 'promotions' in tasks:
        threading.Thread(target=start_promotions_loop, args=(account,bot), name = f"promotions-{account['email']}").start()

def create_scrapper(cfg):
    logging.info('scrapper[{}] :: starting.'.format(cfg['email']))
    bot = ldv_dashbot.Bot(cfg['email'], cfg['pass'], cookies_cache=config['cookies_cache'].format(id = sanitize(cfg['email'])), )
    return bot

def sanitize(s):
    return ''.join([(c if c in 'abcdefghijklmnopqrstuvwxyz' else "_") for c in s])

for a in config['accounts']:
    start_account(a)