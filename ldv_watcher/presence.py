import ldv_dashbot
import logging
import requests
from .utils import sleep
from .hook import process_hooks
def start_presence_loop(cfg):
    logging.info('presence[{}] :: starting.'.format(cfg['email']))
    api = ldv_dashbot.Api(cfg['email'], cfg['pass'])

    appels_ouverts = {}
    profile = api.get_profile()
    if 'ical_token' not in profile:
        message = profile.get('message', profile)
        logging.error('presence[{}] :: Something went wrong: {}. Aborting.'.format(cfg['email'], message))
        return
    ical = ldv_dashbot.API_STUDENT_ICAL.format(profile['ical_token'])
    logging.info("presence[{}] :: ical url : {}".format(cfg['email'], ical))

    while True:
        try:
            presences = api.get_presences()
            for i in presences: 
                if i['etat_ouverture'] and i['etat_ouverture'] != 'fermé':
                    if i['seance_id'] not in appels_ouverts:
                        group = recupGroupFromStartTime(ical, i)
                        
                        process_hooks(cfg, 'presence', 'opened', {
                            'seance_id': i['seance_id'],
                            'group': group,
                            'name': i['nom'],
                            'zoom_url': i.get('zoom_url'),
                        }, render_presence_)

                        appels_ouverts[ i['seance_id'] ] = group
                elif i['seance_id'] in appels_ouverts:
                    group = appels_ouverts[ i['seance_id'] ]


                    process_hooks(cfg, 'presence', 'closed', {
                        'seance_id': i['seance_id'],
                        'group': group,
                        'name': i['nom'],
                        'zoom_url': i.get('zoom_url'),
                    }, render_presence_)

                    del appels_ouverts[ i['seance_id'] ]
            sleep(cfg, 'presence', 5)
        except requests.exceptions.ConnectionError:
            sleep(cfg, 'presence', 5)
            pass
        except:
            import traceback
            traceback.print_exc()
            sleep(cfg, 'error', 120)


def recupGroupFromStartTime(ical, seanceData):
    date = seanceData['date'].split('-')
    start = seanceData['horaire'].split(' ')[0].split(':')
    ts = ''.join(date) + 'T' + ''.join(start)
    attempt = 0
    while attempt < 5:
        try:
            calendar = ldv_dashbot.ICSCalendar(requests.get(ical).text)
            for ev in calendar.data['VEVENT']:
                if ev['DTSTART'] == ts:
                    return ev['GROUPE']

            return '@SEANCE_NOT_FOUND'
        except Exception as e:
            logging.error('recupGroupFromStartTime - {}'.format(e))
            time.sleep(1)
            attempt += 1
    return '@ICAL_FETCH_FAILED'


def render_presence_(tp, op, data, hook):
    group_prefix = hook.get('group_prefix')
    if group_prefix is None or data['group'].startswith('@') or data['group'].startswith(group_prefix):
        if op == 'opened':
            return [
                f":alarm_clock: `{data['name']}` (`{data['group']}`) **Appel ouvert.**",
                f"**Présence : **<https://www.leonard-de-vinci.net/student/presences/{data['seance_id']}>",
                "**Zoom : **<"+data['zoom_url']+">" if data.get('zoom_url') else 'Zoom désactivé.'
            ]
        elif op == 'closed':
            return [
                f":lock: `{data['name']}` **Appel fermé.**"
            ]
        
        