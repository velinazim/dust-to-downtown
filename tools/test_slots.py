#!/usr/bin/env python3
"""Checks for the slot logic (no network, no secrets):  python3 tools/test_slots.py"""
import datetime as dt, importlib.util, os, sys, types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.modules.setdefault('requests', types.ModuleType('requests'))   # yt_api imports it; the logic under test does not use it


def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + '.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


yt, shorts, bs = load('yt_api'), load('shorts'), load('best_slot')
utc = lambda s: dt.datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=dt.timezone.utc)
CFG = {'long': {'slots_utc': ['TUE 23:30', 'FRI 23:30'], 'min_lead_hours': 3},
       'short': {'slots_utc': ['MON 23:30', 'WED 23:30', 'THU 23:30', 'SAT 23:30', 'SUN 23:30'], 'min_lead_hours': 3}}

# Shorts budget: same count whatever hour the episode was scheduled at (old 15:00 slots, new 23:30 slots)
for hour in ('15:00', '23:30', '22:00'):
    assert shorts.budget(utc(f'2026-11-03T{hour}:00Z'), CFG) == 2, ('Tuesday episode', hour)
    assert shorts.budget(utc(f'2026-11-06T{hour}:00Z'), CFG) == 3, ('Friday episode', hour)

# next_slot: a day with a video at an old hour counts as taken; the new hour is used on free days
now = utc('2026-11-02T12:00:00Z')
taken_long = ['2026-11-03T15:00:00Z', '2026-11-06T15:00:00Z', '2026-11-10T15:00:00Z']
assert yt.next_slot(CFG['long'], taken_long, now=now) == '2026-11-13T23:30:00Z'
taken_short = ['2026-11-04T16:00:00Z', '2026-11-05T16:00:00Z', '2026-11-07T16:00:00Z', '2026-11-08T16:00:00Z',
               '2026-11-09T16:00:00Z', '2026-11-11T16:00:00Z', '2026-11-12T16:00:00Z']
assert yt.next_slot(CFG['short'], taken_short, now=now, not_before='2026-11-13T23:30:00Z') == '2026-11-14T23:30:00Z'
assert yt.next_slot(CFG['short'], [], now=now) == '2026-11-02T23:30:00Z'            # lead time respected
assert yt.next_slot(CFG['short'], [], now=utc('2026-11-02T22:00:00Z')) == '2026-11-04T23:30:00Z'   # < 3 h away: skipped

# best_slot: stays inside the UTC day window and keeps a good slot
real = {'long': {'slots_utc': ['TUE 23:30']}, 'short': {'slots_utc': ['MON 23:30']}}
out, top = bs.decide(real, today=dt.date(2026, 11, 2))
assert all(o['new'] == o['old'] for o in out.values()), out
old_hours = {'long': {'slots_utc': ['TUE 15:00']}, 'short': {'slots_utc': ['MON 16:00']}}
out, top = bs.decide(old_hours, today=dt.date(2026, 11, 2))
assert all(bs.FIRST <= o['new'] <= bs.LAST and o['new'] > o['old'] for o in out.values()), out
print('ok')
