import time

def sleep(cfg, op, default):
    duration = cfg.get('freq', {}).get(op, default)
    time.sleep(duration)