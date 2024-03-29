import ldv_dashbot
import logging
import requests
import json
from .utils import sleep
from .config import config
from dictdiffer import diff, patch, swap, revert
from .hook import process_hooks


def start_grades_loop(cfg, bot):
    logging.info("grades[{}] :: started.".format(cfg['email']))

    cache_file = config['grades_cache'].format(id=sanitize(cfg['email']))
    while True:
        try:
            new = ldv_dashbot.DataClass.json(bot.get_grades())
            skip = False
            try:
                with open(cache_file) as f:
                    old = json.loads(f.read())
            except:
                # on first run, we don't have a cache file
                # so we only store the new file
                skip = True

            if not skip:
                diffs = list(diff(old, new))
                # raw json diff
                process_hooks(cfg, 'grades', 'diff', {
                    'new': new,
                    'old': old,
                    'diffs': diffs
                }, render_grades_diff_)

                if diffs or True:
                    old_grades = {}
                    new_grades = {}
                    for semester in old:
                        for unit in semester['units']:
                            for subject in unit['subjects']:
                                if 'rattrapage_grade' in subject:
                                    old_grades[(unit['name'], subject['name'], '@rattrapage')] = subject['rattrapage_grade']
                                for grade in subject['grades']:
                                    old_grades[(unit['name'], subject['name'], grade['name'])] = grade
                    
                    for semester in new:
                        for unit in semester['units']:
                            for subject in unit['subjects']:
                                for grade in subject['grades']:
                                    new_grades[(unit['name'], subject['name'], grade['name'])] = grade
                                
                                if 'rattrapage_grade' in subject:
                                    new_grades[(unit['name'], subject['name'], '@rattrapage')] = subject['rattrapage_grade']

                    
                    for (sem, sub, exam), new_grade in new_grades.items():
                        if (sem, sub, exam) in old_grades:
                            old_grade = old_grades[(sem, sub, exam)]
                            if exam == '@rattrapage':
                                continue

                            if old_grade.get('grade') is None and new_grade.get('grade') is not None:
                                process_hooks(cfg, 'grades', 'grade:set', {
                                    'new': new_grade,
                                    'path': (sem, sub, exam)
                                }, render_grades_update_)
                            elif old_grade.get('grade') != new_grade.get('grade'):
                                process_hooks(cfg, 'grades', 'grade:updated', {
                                    'path': (sem, sub, exam),
                                    'new': new_grade,
                                    'old': old_grade
                                }, render_grades_update_)
                        else:
                            if exam == '@rattrapage':
                                if new_grade is not None:
                                    process_hooks(cfg, 'grades', 'grade:rattrapage:set', {
                                        'grade': new_grade,
                                        'path': (sem, sub)
                                    }, render_grades_update_)
                                continue
                                
                            process_hooks(cfg, 'grades', 'grade:created', {
                                'new': new_grade,
                                'path': (sem, sub, exam)
                            }, render_grades_update_)

                            if new_grade.get('grade') is not None:
                                process_hooks(cfg, 'grades', 'grade:set', {
                                    'new': new_grade,
                                    'path': (sem, sub, exam)
                                }, render_grades_update_)

            with open(cache_file, 'w') as f:
                f.write(json.dumps(new, indent=2))
            sleep(cfg, 'grades', 5)
        except requests.exceptions.ConnectionError:
            sleep(cfg, 'grades', 5)
        except:
            import traceback
            traceback.print_exc()
            sleep(cfg, 'error', 120)


def render_grades_diff_(_tp, _op, data, hook):
    payload = []
    s = set()
    minor_updates = hook.get('show_minor_updates', False)
    skiplist = hook.get('hidden_fields', [])
    old, new, diffs = data['old'], data['new'], data['diffs']

    for op, path, changes in diffs:
        if isinstance(recget(old, path), list):  # if is a member of list !
            for i, d in changes:
                payload.append(
                    f"**---\n{op.upper()}** - {renderPath(new, path + [i])}\n"
                    f"```json\n{renderDict(recget(new, path + [i]), skiplist) if op == 'add' else renderDict(recget(old, path + [i]), skiplist)}```"
                )
        else:
            p = path[:-1] if op == "change" else path
            if str(p) in s:
                continue
            s.add(str(p))
            o = recget(old, p)
            n = recget(new, p)
            if minor_updates or ('promo_average' not in o or 'promo_average' not in n or abs(o['promo_average']-n['promo_average']) > 1):
                payload.append(
                    f"**---\nUPDATE** - {renderPath(new, p)}\n"
                    f"```json\n{renderDict(o, skiplist)}``` "
                    f"```json\n{renderDict(n, skiplist)}```"
                )

    return payload


def render_grades_update_(_tp, op, data, hook):
    p = " > ".join(list(data['path']))

    if op == "grade:created":  # when an exam is added
        return [
            f"**🕵️ NOTE CRÉÉE** - {p} 🕵️",
        ]
    # when a grade is set for an exam (previous grade was None)
    elif op == "grade:set":
        return [
            f"**🙈 NOTE DISPONIBLE** - {p} 🙈",
            "**Moyenne de promotion**",
            f"> {data['new']['promo_average']}/{data['new']['max_grade']}",
        ]
    elif op == "grade:updated":  # when a grade is updated
        # if hook has a min_update_delta, we only send the update if the delta is greater than the min_update_delta
        if data['new'].get('promo_average') and (hook.get('min_update_delta', 0) <= 0 or abs(data['new']['grade'] - data['old']['grade']) >= hook['min_update_delta']):
            return [
                f"**🤡 NOTE MODIFIÉE** - {p} 🤡",
                "**Moyenne de promotion**",
                f"> {data['old'].get('promo_average', '?')}/{data['old'].get('max_grade', '?')} -> {data['new'].get('promo_average', '?')}/{data['new'].get('max_grade', '?')}",
            ]
    elif op == "grade:rattrapage:set":
        return [
            f"**🥺 NOTE DE RATTRAPAGE DISPONIBLE** - {p} 🥺",
        ]


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
        if isinstance(d, dict) and k not in d or isinstance(d, list) and k >= len(d):
            break
        d = d[k]
        if isinstance(d, dict):
            p.append("`{}`".format(
                d['name'] if 'name' in d else f"Semester {d['semester']}"))
    return " > ".join(p)
