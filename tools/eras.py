""""Time-travel" soundtrack: the music changes its instruments and scale with the era on screen.

  python3 tools/eras.py <slug> <out.wav> [--plan]

city.json: "music": {"style": "eras", "flavor": "ottoman"}   (flavor optional; picks the early-modern palette)

Owner, 12.11.2026: "always the same music getting louder and quieter" is not enough — make it bolder. So the sound
itself travels through time with the city (all synthesised here, nothing licensed):

  ancient     (< 500)        plucked lyre + frame drum, Dorian pentatonic
  medieval    (500–1450)     "choir" vowel chords in open fifths/octaves + slow lyre, Dorian
  early modern (1450–1800)   flavor "ottoman": ney-like breathy flute + oud plucks + darbuka (doum/tek), Hijaz scale
                             default (Europe): harpsichord-like pluck arpeggios, major
  industrial  (1800–1945)    mechanical piano ostinato + clock tick + low strings
  modern      (1945–)        synth arpeggio, soft kick on every beat, airy pad, major

The event plan from tools/score.py still drives density (calm / boom / tense) and the drum hits; tension switches
every era to its minor colour. Era changes crossfade over ~2 bars. The cold open plays the MODERN palette on today's
city, then the rewind is a tape-stop (pitch falling) into the first era.
"""
import argparse, json, math, os, sys
import numpy as np
from scipy import signal
from scipy.io import wavfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import music as M  # noqa: E402
import score as S  # noqa: E402

SR = M.SR
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RNG = np.random.default_rng(11)
_c = {}

# ------------------------------------------------------------------ instruments (all cached by args)
def cache(fn):
    def w(*a):
        k = (fn.__name__,) + tuple(round(x, 3) if isinstance(x, float) else x for x in a)
        if k not in _c:
            _c[k] = fn(*a).astype(np.float32)
        return _c[k]
    return w


@cache
def pluck(m, dur, bright):
    """Lyre/oud/harpsichord: bright harmonics dying fast, a little noise in the attack."""
    s = np.arange(int(dur * SR)) / SR; f = M.hz(m); x = np.zeros_like(s)
    for h in range(1, 12):
        fh = f * h * (1 + 0.0004 * h * h)
        if fh > 7000: break
        x += np.sin(2 * np.pi * fh * s + h) * h ** -(1.6 - 0.5 * bright) * np.exp(-s * (2.5 + h * (1.2 + 1.5 * bright)))
    x += RNG.standard_normal(s.size) * np.exp(-s * 300) * 0.15
    return x * np.minimum(1, s / 0.003)


@cache
def choir(m, dur):
    """Vowel 'aah': harmonic stack shaped by two formants, slow swell, light vibrato."""
    s = np.arange(int(dur * SR)) / SR; f = M.hz(m); x = np.zeros_like(s)
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.2 * s) * np.minimum(1, s / 1.0)
    for h in range(1, 24):
        fh = f * h
        if fh > 4500: break
        g = np.exp(-((fh - 750) / 260) ** 2) + 0.6 * np.exp(-((fh - 1200) / 320) ** 2) + 0.25 / h
        x += np.sin(2 * np.pi * fh * np.cumsum(vib) / SR + h * 0.7) * g
    env = np.minimum(1, s / 0.9) * np.clip((dur - s) / 1.2, 0, 1)
    return x * env / 4


@cache
def ney(m, dur):
    """Breathy flute: sine + 2nd harmonic + band-passed breath noise, slow attack, vibrato that grows."""
    s = np.arange(int(dur * SR)) / SR; f = M.hz(m)
    vib = 1 + 0.006 * np.sin(2 * np.pi * 4.8 * s) * np.clip(s / 0.8, 0, 1)
    ph = 2 * np.pi * f * np.cumsum(vib) / SR
    tone = np.sin(ph) + 0.18 * np.sin(2 * ph) + 0.06 * np.sin(3 * ph)
    b, a = signal.butter(2, [max(60, f * 0.8) / (SR / 2), min(f * 3.5, 9000) / (SR / 2)], 'band')
    breath = signal.lfilter(b, a, RNG.standard_normal(s.size)) * 0.9
    env = np.minimum(1, s / 0.25) * np.clip((dur - s) / 0.5, 0, 1)
    return (tone * 0.7 + breath * (0.18 + 0.2 * np.exp(-s * 3))) * env


@cache
def synth(m, dur, cutoff):
    """Modern pluck synth: detuned saws through a low-pass with a short filter envelope."""
    s = np.arange(int(dur * SR)) / SR; f = M.hz(m)
    x = sum(signal.sawtooth(2 * np.pi * f * (1 + d) * s + d * 50) for d in (-0.004, 0, 0.005)) / 3
    b, a = signal.butter(2, min(cutoff, 0.45 * SR) / (SR / 2))
    x = signal.lfilter(b, a, x)
    return x * np.exp(-s * 3.5) * np.minimum(1, s / 0.004)


@cache
def pad(m, dur):
    s = np.arange(int(dur * SR)) / SR; f = M.hz(m)
    x = sum(np.sin(2 * np.pi * f * (1 + d) * h * s) / h ** 1.5 for d in (-0.002, 0.002) for h in (1, 2, 3, 4))
    return x * np.minimum(1, s / 1.5) * np.clip((dur - s) / 1.5, 0, 1) / 5


@cache
def hit(kind):
    """Percussion: frame drum, darbuka doum / tek, clock tick, soft kick, shaker."""
    n = int({'tick': 0.05, 'shaker': 0.12}.get(kind, 0.6) * SR); s = np.arange(n) / SR
    nz = RNG.standard_normal(n)
    if kind == 'frame':
        return np.sin(2 * np.pi * (95 + 40 * np.exp(-s * 30)) * s) * np.exp(-s * 9) + nz * np.exp(-s * 60) * 0.2
    if kind == 'doum':
        return np.sin(2 * np.pi * (78 + 25 * np.exp(-s * 25)) * s) * np.exp(-s * 7)
    if kind == 'tek':
        b, a = signal.butter(2, [1800 / (SR / 2), 6000 / (SR / 2)], 'band')
        return signal.lfilter(b, a, nz) * np.exp(-s * 45) * 0.8 + np.sin(2 * np.pi * 640 * s) * np.exp(-s * 40) * 0.3
    if kind == 'tick':
        b, a = signal.butter(2, 3000 / (SR / 2), 'high')
        return signal.lfilter(b, a, nz) * np.exp(-s * 150) * 0.5
    if kind == 'kick':
        return np.sin(2 * np.pi * (48 + 70 * np.exp(-s * 35)) * s) * np.exp(-s * 8)
    if kind == 'shaker':
        b, a = signal.butter(2, 6000 / (SR / 2), 'high')
        return signal.lfilter(b, a, nz) * np.sin(np.pi * s / s[-1]) * 0.25
    raise ValueError(kind)


# ------------------------------------------------------------------ eras
DORIAN = [0, 2, 3, 5, 7, 9, 10]; HIJAZ = [0, 1, 4, 5, 7, 8, 10]; MAJOR = [0, 2, 4, 5, 7, 9, 11]; MINOR = [0, 2, 3, 5, 7, 8, 10]


def era_of(year, flavor):
    if year < 500: return 'ancient'
    if year < 1450: return 'medieval'
    if year < 1800: return 'ottoman' if flavor == 'ottoman' else 'baroque'
    if year < 1945: return 'industrial'
    return 'modern'


def year_at(tl, t):
    """Year on screen at output time t (engine yearAt, cold open → today)."""
    if t < tl.cos:
        return tl.segs[-1]['to']
    e = t - tl.cos
    for s in tl.segs:
        if e < s['_t1']:
            return s['from'] + (s['to'] - s['from']) * max(0, min(1, (e - s['_t0']) / s['seconds']))
    return tl.segs[-1]['to']


def render(city, out, seed=7):
    flavor = (city.get('music') or {}).get('flavor')
    tl, total, inten, tense, boom, hits = S.plan(city)
    rng = np.random.default_rng(seed)
    n = int((total + 4) * SR)
    L = np.zeros(n, np.float32); R = np.zeros(n, np.float32)
    key = 50 + int(rng.integers(0, 5))   # D3..F#3
    beat = 60 / 72; bar = 4 * beat

    def put(w, t0, vel, pan=0.5):
        a = int(t0 * SR)
        if a >= n or vel <= 0 or a + w.size <= 0: return
        lo = max(0, -a); a = max(0, a); b = min(n, a + w.size - lo)
        L[a:b] += w[lo:lo + b - a] * vel * (1 - pan) * 2; R[a:b] += w[lo:lo + b - a] * vel * pan * 2

    def sc(scale, deg, octv=0):
        return key + scale[deg % len(scale)] + 12 * (deg // len(scale) + octv)

    start = tl.cos
    nb = int(math.ceil((total - start) / bar)) + 1
    plan_rows = []
    prev_era = None
    for bi in range(-int(math.ceil(start / bar)) if tl.cos else 0, nb):
        t0 = start + bi * bar
        if t0 > total: break
        cold = t0 < tl.cos
        if cold and t0 + bar > tl.hold:          # the rewind bar is handled separately
            continue
        mid = min(len(inten) - 1, max(0, int(t0 + bar / 2)))
        I = float(inten[mid]); ten = bool(tense[max(0, int(t0)):int(t0 + bar) + 1].any()); bm = bool(boom[mid])
        era = 'modern' if cold else era_of(year_at(tl, t0 + bar / 2), flavor)
        v = 0.55 + 0.7 * I
        sparse = I < 0.3
        chord = [0, 5, 3, 4][bi % 4] if not ten else [0, 5, 6, 0][bi % 4]   # scale degrees of chord roots
        plan_rows.append((round(t0, 1), era, 'tense' if ten else 'calm' if sparse else 'boom' if bm else 'normal'))
        fresh = era != prev_era; prev_era = era
        xin = 0.5 if fresh and bi > 0 else 1.0   # soft entry on an era change
        if era == 'ancient':
            scale = MINOR if ten else DORIAN
            pent = [0, 2, 3, 4, 6]
            for i in range(8 if not sparse else 4):
                st = beat / 2 if not sparse else beat
                deg = pent[int(rng.integers(0, 5))] if i % 2 else chord
                put(pluck(sc(scale, deg, 1), 1.6, 0.4), t0 + i * st, 0.11 * v * xin, 0.3 + 0.05 * i)
            put(pluck(sc(scale, chord, -1), 2.5, 0.2), t0, 0.16 * v, 0.5)
            for b4 in range(4):
                if not sparse or b4 == 0:
                    put(hit('frame'), t0 + b4 * beat, (0.22 if b4 in (0, 2) else 0.1) * v, 0.5)
        elif era == 'medieval':
            scale = MINOR if ten else DORIAN
            r = sc(scale, chord)
            for m in (r - 12, r - 5, r):          # open fifths + octave, sung
                put(choir(m, bar + 1.2), t0 - 0.2, 0.10 * v * xin, 0.4 + 0.1 * (m - r + 12) / 12)
            for i in range(4 if not sparse else 2):
                put(pluck(sc(scale, chord + [0, 2, 4, 2][i], 1), 2.0, 0.2), t0 + i * beat * (1 if not sparse else 2), 0.08 * v, 0.6)
            if ten:
                put(hit('frame'), t0, 0.25 * v); put(hit('frame'), t0 + 2 * beat, 0.18 * v)
        elif era == 'ottoman':
            scale = HIJAZ
            # usul: düm . tek tek | düm . tek .
            for b8, kind, g in [(0, 'doum', .30), (2, 'tek', .09), (3, 'tek', .06), (4, 'doum', .26), (6, 'tek', .09)]:
                if not sparse or kind == 'doum':
                    put(hit(kind), t0 + b8 * beat / 2, g * v, 0.45 + (0.15 if kind == 'tek' else 0))
            put(pluck(sc(scale, 0, -1), 2.4, 0.3), t0, 0.15 * v, 0.4)
            for i in (0, 3, 4, 6) if not sparse else (0, 4):
                put(pluck(sc(scale, [0, 1, 2, 4, 3, 2, 1, 0][(bi * 2 + i) % 8], 0), 1.2, 0.5), t0 + i * beat / 2, 0.09 * v, 0.35)
            if bi % 2 == 0:                       # ney phrase every other bar: rise to the 5th, fall through the 2nd
                phrase = [4, 5, 4, 3, 2, 1, 0] if not ten else [4, 5, 6, 5, 4, 2, 1, 0]
                tt = t0
                for j, d in enumerate(phrase):
                    du = beat * (1.5 if j in (0, len(phrase) - 1) else 0.5)
                    put(ney(sc(scale, d, 1), du + 0.4), tt, 0.10 * v * xin, 0.55); tt += du
        elif era == 'baroque':
            scale = MINOR if ten else MAJOR
            for i in range(16 if not sparse else 8):
                st = beat / 4 if not sparse else beat / 2
                d = chord + [0, 2, 4, 7, 4, 2, 4, 2][i % 8]
                put(pluck(sc(scale, d, 1), 0.9, 0.9), t0 + i * st, 0.07 * v * xin, 0.3 + 0.03 * (i % 8))
            put(pluck(sc(scale, chord, -1), 2.0, 0.6), t0, 0.14 * v)
        elif era == 'industrial':
            scale = MINOR if ten else MAJOR
            for i in range(8):                    # mechanical ostinato, very even
                d = chord + [0, 4, 7, 4][i % 4]
                put(M.piano(sc(scale, d, 1), 1.4), t0 + i * beat / 2, 0.075 * v * xin, 0.35 + 0.05 * (i % 4))
            put(M.piano(sc(scale, chord, -1), 2.5), t0, 0.2 * v, 0.5)
            for i in range(8):
                put(hit('tick'), t0 + i * beat / 2, (0.12 if i % 2 == 0 else 0.07), 0.7)
            if I > 0.55:
                put(pad(sc(scale, chord, -1), bar + 1.5), t0 - 0.2, 0.12 * v, 0.5)
        else:  # modern
            scale = MINOR if ten else MAJOR
            cut = 900 + 3000 * I
            for i in range(16 if not sparse else 8):
                st = beat / 4 if not sparse else beat / 2
                d = chord + [0, 2, 4, 7, 9, 7, 4, 2][i % 8]
                put(synth(sc(scale, d, 1), 0.5, cut), t0 + i * st, 0.06 * v * xin, 0.25 + 0.06 * (i % 8))
            put(synth(sc(scale, chord, -1), 1.6, 500.0), t0, 0.12 * v)
            for b4 in range(4):
                put(hit('kick'), t0 + b4 * beat, 0.22 * v * (1 if not sparse else 0.5))
                put(hit('shaker'), t0 + b4 * beat + beat / 2, 0.12 * v, 0.6)
            for m in (0, 2, 4):
                put(pad(sc(scale, chord + m, 0), bar + 1.5), t0 - 0.2, 0.05 * v, 0.5)
    # rewind: the last cold-open bars, played backwards with the pitch falling (tape stop)
    if tl.cos:
        a, b = int(max(0, tl.hold - 3.0) * SR), int(tl.hold * SR)
        seg = np.stack([L[a:b], R[a:b]], 1)[::-1]
        rw = int((tl.cos - tl.hold) * SR)
        idx = np.cumsum(np.linspace(1.0, 0.15, rw)); idx = (idx / idx[-1] * (seg.shape[0] - 1)).astype(int)
        tape = seg[idx] * np.linspace(1, 0, rw)[:, None] ** 0.7
        L[int(tl.hold * SR):int(tl.hold * SR) + rw] += tape[:, 0]; R[int(tl.hold * SR):int(tl.hold * SR) + rw] += tape[:, 1]
    for t, s in hits:
        if tl.cos <= t < total:
            put(S.drum(0.25 * s), t, 1.0)
    L = L[:int(total * SR)]; R = R[:int(total * SR)]
    b, a = signal.butter(2, 9000 / (SR / 2)); L = signal.lfilter(b, a, L); R = signal.lfilter(b, a, R)
    ir_t = np.arange(int(2.0 * SR)) / SR
    for ch in (0, 1):
        ir = rng.standard_normal(ir_t.size) * np.exp(-ir_t * 3.2)
        bi_, ai_ = signal.butter(1, 4000 / (SR / 2)); ir = signal.lfilter(bi_, ai_, ir); ir /= np.sqrt((ir ** 2).sum())
        if ch == 0: L = 0.82 * L + 0.3 * signal.oaconvolve(L, ir)[:L.size]
        else: R = 0.82 * R + 0.3 * signal.oaconvolve(R, ir)[:R.size]
    t = np.arange(L.size) / SR
    fade = np.minimum(1, np.minimum(t / 0.5, (total - t) / 5.0)).clip(0, 1)
    st = np.stack([L * fade, R * fade], 1)
    try:
        li, tp = M.loudness(st); gain = min(10 ** ((M.TARGET_LUFS - li) / 20), 10 ** ((-2.0 - tp) / 20))
    except (FileNotFoundError, OSError):
        rms = float(np.sqrt((st ** 2).mean())) or 1e-9
        gain = min(10 ** ((M.TARGET_LUFS + 0.7) / 20) / rms, 0.79 / float(np.abs(st).max() or 1))
    st = np.concatenate([np.clip(st * gain, -1, 1), np.zeros((SR, 2))])
    wavfile.write(out, SR, (st * 32767).astype(np.int16))
    return plan_rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('slug'); ap.add_argument('out', nargs='?'); ap.add_argument('--plan', action='store_true')
    ap.add_argument('--flavor', help='override music.flavor (e.g. ottoman) for a test')
    a = ap.parse_args()
    city = json.load(open(os.path.join(ROOT, 'cities', a.slug, 'city.json'), encoding='utf-8'))
    if a.flavor: city.setdefault('music', {})['flavor'] = a.flavor
    if a.plan:
        flavor = (city.get('music') or {}).get('flavor'); tl = S.Timeline(city); last = None
        for t in np.arange(0, tl.cos + tl.dur, 1.0):
            e = 'modern (cold open)' if t < tl.cos else era_of(year_at(tl, t), flavor)
            if e != last: print(f'{int(t) // 60}:{int(t) % 60:02d}  {e}'); last = e
        return
    rows = render(city, a.out, city.get('seed', 7))
    from collections import Counter
    print('bars per era:', dict(Counter(r[1] for r in rows)))


if __name__ == '__main__':
    main()
