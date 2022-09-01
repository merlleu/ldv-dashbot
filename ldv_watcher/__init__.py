from .config import config
import logging

import threading
from .grades   import start_grades_loop
from .presence import start_presence_loop

def start_account(account):
    logging.info(f"Starting account {account['email']}")
    tasks = set()
    for hook in account['hooks']:
        for trigger in hook['triggers']:
            if trigger['type'] == 'presence':
                tasks.add('presence')
            elif trigger['type'] == 'grades':
                tasks.add('grades')
    
    if 'presence' in tasks:
        threading.Thread(target=start_presence_loop, args=(account,), name = f"presence-{account['email']}").start()
    
    if 'grades' in tasks:
        threading.Thread(target=start_grades_loop, args=(account,), name = f"presence-{account['email']}").start()

for a in config['accounts']:
    start_account(a)