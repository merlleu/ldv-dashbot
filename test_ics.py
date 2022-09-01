import requests
import json
t = requests.get(
    input('Calendar URL > ')
    ).text

from ldv_dashbot import ICSCalendar
c = ICSCalendar(t)

with open('calendar.json', 'wb') as f:
    f.write(json.dumps(c.data, indent=2).encode('utf-8'))
