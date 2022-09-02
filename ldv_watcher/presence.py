import ldv_dashbot
import logging
import requests
from .utils import sleep
from .hook import process_hooks
from .config import config
import time
import dateutil.parser
import dateutil.tz

def start_presence_loop(cfg):
    logging.info('presence[{}] :: starting.'.format(cfg['email']))
    api = ldv_dashbot.Api(cfg['email'], cfg['pass'])

    seances = {}
    profile = api.get_profile()
    if 'ical_token' not in profile:
        message = profile.get('message', profile)
        logging.error('presence[{}] :: Something went wrong: {}. Aborting.'.format(
            cfg['email'], message))
        return
    ical = ldv_dashbot.API_STUDENT_ICAL.format(profile['ical_token'])
    cal_ = None

    while True:
        try:
            presences = api.get_presences()

            calendar_refreshed_ = False
            for i in presences:
                if i['seance_id'] not in seances:
                    if not calendar_refreshed_:
                        calendar_refreshed_ = True
                        cal_ = refresh_calendar(ical, cfg)
                    
                    start_time, end_time = convert_horaire(i)
                    seances[i['seance_id']] = {
                        'group': recupGroupFromStartTime(cal_, i),
                        'appel_ouvert': False,
                        'presence_state': None,
                        'time_state': None,
                        '_h': i['horaire'],
                        'start_time': start_time,
                        'end_time': end_time,
                        '_zoom_sent': False,
                    }

                seance = seances[i['seance_id']]
                payload = {
                    'seance': seance,
                    'presence': i,
                }
                if i['etat_ouverture'] and i['etat_ouverture'] != 'fermé':
                    if not seance['appel_ouvert']:
                        process_hooks(cfg, 'presence', 'opened',
                                      payload, render_presence_)
                        seance['appel_ouvert'] = True
                        seance['_zoom_sent'] = True

                elif seance['appel_ouvert']:
                    process_hooks(cfg, 'presence', 'closed',
                                  payload, render_presence_)
                    seance['appel_ouvert'] = False
                    if i['etat_presence'] != 'présent':
                        process_hooks(
                            cfg, 'presence', 'student:absent', payload, render_presence_)

                if seance['presence_state'] != i['etat_presence'] and i['etat_presence'] == 'présent' and time.time() <= seance['end_time']:
                    process_hooks(cfg, 'presence', 'student:ok',
                                  payload, render_presence_)
                    seance['presence_state'] = i['etat_presence']

                if seance['_h'] == i['horaire']:
                    start_time, end_time = convert_horaire(i)
                    seance.update({
                        '_h': i['horaire'],
                        'start_time': start_time,
                        'end_time': end_time
                    })

                if seance['time_state'] is None and seance['start_time'] <= time.time() <= seance['end_time']:
                    seance['time_state'] = 'started'
                    process_hooks(cfg, 'presence', 'course:started',
                                  payload, render_presence_)
                    seance['_zoom_sent'] = True

                elif seance['time_state'] == 'started' and seance['end_time'] <= time.time():
                    seance['time_state'] = 'ended'
                    process_hooks(cfg, 'presence', 'course:ended',
                                  payload, render_presence_)

            # cleanup
            for z in list(seances):
                found = False
                for i in presences:
                    if i['seance_id'] == z:
                        found = True
                        break
                if not found:
                    del seances[z]

            sleep(cfg, 'presence', 5)
        except requests.exceptions.ConnectionError:
            sleep(cfg, 'presence', 5)
            pass
        except:
            import traceback
            traceback.print_exc()
            sleep(cfg, 'error', 120)


def recupGroupFromStartTime(calendar, seanceData):
    date = seanceData['date'].split('-')
    start = seanceData['horaire'].split(' ')[0].split(':')
    ts = ''.join(date) + 'T' + ''.join(start)
    for ev in calendar.data['VEVENT']:
        if ev['DTSTART'] == ts:
            return ev['GROUPE']

    return '@SEANCE_NOT_FOUND'


def refresh_calendar(ical, cfg):
    for i in range(1, 200):
        try:
            calendar = ldv_dashbot.ICSCalendar(requests.get(ical).text)
            logging.info("presence[{}] :: ical downloaded ({} events).".format(cfg['email'], len(calendar.data['VEVENT'])))
            return calendar
        except Exception as e:
            logging.error('recupGroupFromStartTime - {}'.format(e))
            time.sleep(i * 10)

    ldv_dashbot.ICSCalendar(requests.get(ical).text)


def render_presence_(tp, op, data, hook):
    group_prefix = hook.get('group_prefix')
    seance = data['seance']
    presence = data['presence']
    if group_prefix is None or seance['group'].startswith('@') or seance['group'].startswith(group_prefix):
        if op == 'opened':
            return [
                f":alarm_clock: `{presence['nom']}` (`{seance['group']}`) **Appel ouvert.**",
                f"**Présence : **<https://www.leonard-de-vinci.net/student/presences/{presence['seance_id']}>",
            ] + ([
                "**Zoom : **<"+presence['zoom_url'] +
                ">" if presence.get('zoom_url') else 'Zoom désactivé.'
            ] if not seance['_zoom_sent'] else [])
        elif op == 'closed':
            return [
                f":lock: `{presence['nom']}` (`{seance['group']}`) **Appel fermé.**"
            ]
        elif op == 'student:ok':
            return [
                f":white_check_mark: `{presence['nom']}` (`{seance['group']}`) **Appel validé.**"
            ]
        elif op == 'student:absent':
            return [
                f":x: `{presence['nom']}` (`{seance['group']}`) **Appel non validé ({presence['etat_presence']}).**"
            ]

        elif op == 'course:started':
            return [
                f":runner: `{presence['nom']}` (`{seance['group']}`) **Séance commencée.**"
            ] + ([
                "**Zoom : **<"+presence['zoom_url'] +
                ">" if presence.get('zoom_url') else 'Zoom désactivé.'
            ] if not seance['_zoom_sent'] else [])

        elif op == 'course:ended':
            return [
                f":beers: `{presence['nom']}` (`{seance['group']}`) **Séance terminée.**"
            ]


def convert_horaire(seance):
    date = seance['date']
    start, end = seance['horaire'].split(' - ')
    BST = dateutil.tz.gettz(config.get('timezone', 'Europe/Paris'))
    s = dateutil.parser.parse(f"{date} {start} BST", tzinfos={
                              'BST': BST}).timestamp()
    e = dateutil.parser.parse(f"{date} {end} BST", tzinfos={
                              'BST': BST}).timestamp()
    return s, e
