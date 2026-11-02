#!/usr/bin/env python3
"""Pick the publish time of day for Dust to Downtown from where the audience lives.

Same idea as The Before Atlas' tools/best_slot.py, adapted to this channel's weekly schedule:

* The WEEKDAYS in config/schedule.json stay as they are (long: TUE + FRI, Shorts: the days between).
  Only the hour changes, and always inside the same UTC day (12:00-23:45 UTC), so "TUE" still means
  Tuesday for a US viewer.
* Each candidate time is scored by how much of the audience is in its 0.5-3 h window after publishing,
  using a typical day of phone video watching by LOCAL hour (low at night, peak 18:00-22:00) and each
  country's time zones, computed for the actual next 14 days (daylight saving moves the slot by itself).
* The audience is a typical English-language history channel (mostly US). This channel has no analytics
  snapshot yet, so there is no learning from real views; when it has, replace DEFAULT_MIX with the real
  country split.
* A slot is kept unless the model moved by 30+ minutes AND the new time scores 2 %+ better (no churn).
* Videos that are already uploaded and scheduled keep their time. Only new uploads use the new hour.

    python3 tools/best_slot.py            # update config/schedule.json + config/best_slot.md
    python3 tools/best_slot.py --print    # only show the decision

"fixed": true inside config/schedule.json stops all changes (owner wants a fixed time).
The hour of the first slot of each kind is the "current" one; a change sets every slot of that kind to the new hour.
Nothing is written (and the weekly Action makes no commit) while the hours stay the same.
"""
import datetime as dt, json, os, sys
from zoneinfo import ZoneInfo

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = os.path.join(REPO, 'config', 'schedule.json')
REPORT = os.path.join(REPO, 'config', 'best_slot.md')

# share of phone video watching by local hour (0-23): a generic curve, an estimate and not channel data
ACTIVITY = [0.40, 0.25, 0.15, 0.10, 0.08, 0.10, 0.18, 0.30, 0.38, 0.40, 0.42, 0.45,
            0.55, 0.52, 0.48, 0.50, 0.58, 0.70, 0.85, 0.97, 1.00, 0.95, 0.80, 0.60]

DEFAULT_MIX = {'US': 0.50, 'GB': 0.13, 'IN': 0.09, 'CA': 0.07, 'AU': 0.06, 'PH': 0.03, 'DE': 0.03, 'NL': 0.02,
               'TR': 0.02, 'ZA': 0.02, 'NZ': 0.01, 'IE': 0.02}

# country -> [(time zone, share of that country's people)]
TZ = {
    'US': [('America/New_York', .47), ('America/Chicago', .29), ('America/Denver', .07), ('America/Los_Angeles', .17)],
    'CA': [('America/Toronto', .62), ('America/Winnipeg', .08), ('America/Edmonton', .12), ('America/Vancouver', .14), ('America/Halifax', .04)],
    'AU': [('Australia/Sydney', .60), ('Australia/Brisbane', .20), ('Australia/Perth', .11), ('Australia/Adelaide', .09)],
    'GB': [('Europe/London', 1)], 'IE': [('Europe/Dublin', 1)], 'DE': [('Europe/Berlin', 1)], 'NL': [('Europe/Amsterdam', 1)],
    'TR': [('Europe/Istanbul', 1)], 'ZA': [('Africa/Johannesburg', 1)], 'IN': [('Asia/Kolkata', 1)],
    'PH': [('Asia/Manila', 1)], 'NZ': [('Pacific/Auckland', 1)],
}

FIRST, LAST, STEP = 12 * 60, 23 * 60 + 45, 15      # candidate times, minutes after 00:00 UTC
MIN_MOVE, MIN_GAIN = 30, 0.02


def activity(h):
    h %= 24
    i = int(h)
    return ACTIVITY[i] + (ACTIVITY[(i + 1) % 24] - ACTIVITY[i]) * (h - i)


def score(minute, day):
    """Share of the audience whose local 0.5-3 h after this UTC time on `day` is prime watching time."""
    base = dt.datetime(day.year, day.month, day.day, tzinfo=dt.timezone.utc) + dt.timedelta(minutes=minute)
    ks = [0.5 + 0.25 * j for j in range(11)]
    total = 0.0
    for country, share in DEFAULT_MIX.items():
        for zone, part in TZ[country]:
            local = base.astimezone(ZoneInfo(zone))
            h = local.hour + local.minute / 60
            total += share * part * sum(activity(h + k) for k in ks) / len(ks)
    return total


def hm(m):
    return f'{m // 60:02d}:{m % 60:02d}'


def parse(slot):
    wd, t = slot.split()
    h, m = map(int, t.split(':'))
    return wd, h * 60 + m


def istanbul(minute):
    d = dt.date.today()
    at = dt.datetime(d.year, d.month, d.day, tzinfo=dt.timezone.utc) + dt.timedelta(minutes=minute)
    return at.astimezone(ZoneInfo('Europe/Istanbul')).strftime('%H:%M')


def decide(cfg, today=None):
    today = today or dt.date.today()
    days = [today + dt.timedelta(days=k) for k in range(14)]
    avg = lambda m: sum(score(m, d) for d in days) / len(days)
    ranked = sorted(((avg(m), m) for m in range(FIRST, LAST + 1, STEP)), reverse=True)
    best_s, best_m = ranked[0]
    out = {}
    for kind in ('long', 'short'):
        cur = parse(cfg[kind]['slots_utc'][0])[1]
        cur_s = avg(cur) if FIRST <= cur <= LAST else 0.0
        keep = abs(cur - best_m) < MIN_MOVE or cur_s >= best_s * (1 - MIN_GAIN)
        out[kind] = {'old': cur, 'new': cur if keep else best_m, 'old_score': cur_s}
    return out, ranked[:5]


def report(cfg, out, top):
    lines = ['# Publish time: how it was chosen', '']
    for kind, label in (('long', 'Long episodes'), ('short', 'Shorts')):
        o = out[kind]
        days = ', '.join(parse(s)[0] for s in cfg[kind]['slots_utc'])
        change = 'unchanged' if o['old'] == o['new'] else f"was {hm(o['old'])} UTC"
        lines.append(f"- **{label}** ({days}): {hm(o['new'])} UTC ({istanbul(o['new'])} Istanbul), {change}")
    lines += ['- **Best candidate times (UTC, score):** ' + ', '.join(f'{hm(m)} {s:.3f}' for s, m in top),
              '- **Audience used:** typical English-language history channel (US 50 %, GB 13 %, IN 9 %, CA 7 %, AU 6 %); '
              'no channel analytics yet, so no learning from real views.',
              '', 'Weekdays are fixed in config/schedule.json. Videos already scheduled keep their time.', '']
    return '\n'.join(lines)


def main():
    cfg = json.load(open(CFG))
    out, top = decide(cfg)
    md = report(cfg, out, top)
    print(md)
    if '--print' in sys.argv:
        return
    if cfg.get('fixed'):
        print('slot fixed by the owner ("fixed": true): not changed')
        return
    if all(out[k]['old'] == out[k]['new'] for k in out):
        if not os.path.exists(REPORT):
            with open(REPORT, 'w', encoding='utf-8') as f:
                f.write(md)
        return                                  # nothing to change: no commit
    for kind in ('long', 'short'):
        new = out[kind]['new']
        cfg[kind]['slots_utc'] = [f'{parse(s)[0]} {hm(new)}' for s in cfg[kind]['slots_utc']]
    cfg['chosen_by'] = f'tools/best_slot.py {dt.date.today().isoformat()}'
    tmp = CFG + '.tmp'
    with open(tmp, 'w') as f:                   # write whole file, then swap: schedule.json is never half written
        json.dump(cfg, f, indent=1)
        f.write('\n')
    os.replace(tmp, CFG)
    with open(REPORT, 'w', encoding='utf-8') as f:
        f.write(md)


if __name__ == '__main__':
    main()
