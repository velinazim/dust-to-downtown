"""Event-driven soundtrack ("score") — the music follows the episode's story.

  python3 tools/score.py <slug> <out.wav> [--from S --to S] [--plan]

Used instead of tools/music.py when city.json has "music": {"style": "score"} (tools/assemble.py). Same soft
documentary piano as music.py (owner, 9.11.2026: warm, major key, no drones, no high 'ping' notes), but its
intensity is driven by the timeline in city.json:

  calm   untitled "time passes" segments            sparse piano, quiet
  normal titled segments                            the music.py arpeggio
  boom   fast population growth                     denser arpeggio (16ths), soft string pad
  tense  fires, sieges (camps), and titles with siege/fall/plague/earthquake/riot/fire/crusade/razed/war
                                                    relative-minor chords, low pulse, pad, a low drum hit at the start
  finale the last segment ("<city> today")          full chords + pad, resolves on the tonic
  cold open (city.json "cold_open")                 full theme on today's city, then a reversed swell and a fast
                                                    falling arpeggio over the rewind, silence-to-calm on the first year

A chapter start gets a soft low "boom". Each bar is planned from the intensity at its middle; the tempo is fixed so
chapters do not drift. --plan prints the bar plan only (no audio). Loudness: -23 LUFS like music.py.
"""
import argparse, json, math, os, re, sys
import numpy as np
from scipy import signal
from scipy.io import wavfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import music as M  # noqa: E402

SR = M.SR
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TENSE_WORDS = re.compile(r'\b(siege|sieges|besieged|fall|falls|plague|earthquake|riot|riots|fire|fires|burn|burns|burned|'
                         r'crusade|razed|sack|sacked|war|wars|bomb|bombed|blitz|massacre|revolt|revolution|invasion)\b', re.I)
TONIC, MAJ_PROG, MIN_PROG = 0, [(0, 1), (7, 1), (9, 0), (5, 1)], [(9, 0), (5, 1), (0, 1), (7, 1)]
MIN_PROG_DARK = [(9, 0), (5, 1), (7, 1), (9, 0)]   # vi IV V vi — stays in the minor colour


def T(o):
    return o if isinstance(o, str) else (o or {}).get('en', '')


class Timeline:
    """Segment times exactly as the engine computes them (engine/index.html tOf), plus the cold-open offset."""
    def __init__(self, city):
        self.segs = city['segments']; acc = 0.0
        for s in self.segs:
            s['_t0'] = acc; acc += s['seconds']; s['_t1'] = acc
        self.dur = acc
        co = city.get('cold_open')
        self.cos = float(co.get('seconds', 7)) if co else 0.0
        self.hold = float(co.get('hold', self.cos - 2.5)) if co else 0.0

    def t_of(self, y):
        S = self.segs
        if y <= S[0]['from']:
            return self.cos
        for i, s in enumerate(S):
            if s['from'] <= y <= s['to']:
                return self.cos + (s['_t0'] if s['to'] == s['from'] else s['_t0'] + (y - s['from']) / (s['to'] - s['from']) * s['seconds'])
            if i + 1 < len(S) and s['to'] < y < S[i + 1]['from']:
                return self.cos + S[i + 1]['_t0']
        return self.cos + self.dur


def plan(city):
    """Per-second intensity (0..1), tension flag, and event times (output seconds)."""
    tl = Timeline(city); total = tl.cos + tl.dur
    n = int(math.ceil(total)) + 1
    inten = np.full(n, 0.45); tense = np.zeros(n, bool); boom = np.zeros(n, bool)
    hits = []   # (t, strength)
    rates = []
    for s in tl.segs:
        p = s.get('population')
        if isinstance(p, list) and p[0] and p[1] and p[1] > p[0]:
            rates.append(math.log(p[1] / p[0]) / s['seconds'])
    hi_rate = float(np.percentile(rates, 75)) if rates else 1e9
    for i, s in enumerate(tl.segs):
        a, b = int(tl.cos + s['_t0']), int(math.ceil(tl.cos + s['_t1']))
        if not s.get('title'):
            inten[a:b] = 0.22
        p = s.get('population')
        if isinstance(p, list) and p[0] and p[1] and p[1] > p[0] and math.log(p[1] / p[0]) / s['seconds'] >= hi_rate:
            boom[a:b] = True; inten[a:b] = np.maximum(inten[a:b], 0.68)
        if TENSE_WORDS.search(T(s.get('title')) + ' ' + T(s.get('sub'))):
            tense[a:b] = True; inten[a:b] = np.maximum(inten[a:b], 0.78)
        if s.get('chapter') and i:
            hits.append((tl.cos + s['_t0'], 0.6))
    for f in city.get('fires', []):
        t0 = tl.t_of(f['year']); a = int(t0); b = int(t0 + f.get('duration_s', 4) + 4)
        tense[a:b] = True; inten[a:b] = np.maximum(inten[a:b], 0.9); hits.append((t0, 1.0))
    for c in city.get('camps', []):
        a, b = int(tl.t_of(c['from'])), int(math.ceil(tl.t_of(c['to'])))
        tense[a:b + 1] = True; inten[a:b + 1] = np.maximum(inten[a:b + 1], 0.85)
        hits.append((tl.t_of(c['from']), 0.9))
    last = tl.segs[-1]
    inten[int(tl.cos + last['_t0']):] = 0.8
    if tl.cos:
        inten[:int(tl.hold)] = 0.75; inten[int(tl.hold):int(math.ceil(tl.cos))] = 0.5
    # smooth so the music swells into events instead of jumping (but never smear tension backwards much)
    k = np.hanning(7); k /= k.sum()
    inten = np.convolve(np.pad(inten, 3, mode='edge'), k, mode='valid')[:n]
    hits = sorted({round(t, 2): s for t, s in hits}.items())
    return tl, total, inten.clip(0, 1), tense, boom, hits


def pad_tone(m, dur, att=1.2, rel=1.5):
    """Soft string pad: a few detuned harmonic stacks, slow attack and release, low-passed later."""
    s = np.arange(int(dur * SR)) / SR; f = M.hz(m); x = np.zeros_like(s)
    for det in (-0.0012, 0.0, 0.0013):
        for h in range(1, 7):
            x += np.sin(2 * np.pi * f * (1 + det) * h * s + h) / h ** 1.3
    env = np.minimum(1, s / att) * np.clip((dur - s) / rel, 0, 1)
    return (x * env / 6).astype(np.float32)


def drum(strength):
    s = np.arange(int(2.5 * SR)) / SR
    body = np.sin(2 * np.pi * (52 + 30 * np.exp(-s * 18)) * s) * np.exp(-s * 2.8)
    noise = np.random.default_rng(3).standard_normal(s.size) * np.exp(-s * 22) * 0.25
    b, a = signal.butter(2, 400 / (SR / 2)); noise = signal.lfilter(b, a, noise)
    return ((body + noise) * strength).astype(np.float32)


def render(city, out, seed=7, t_from=0.0, t_to=None):
    tl, total, inten, tense, boom, hits = plan(city)
    rng = np.random.default_rng(seed)
    n = int(total * SR) + SR * 4
    L = np.zeros(n, np.float32); R = np.zeros(n, np.float32); P = np.zeros(n, np.float32)
    key = 48 + int(rng.integers(0, 7))
    beat = 60.0 / 70; bar = 4 * beat

    def add(buf_l, buf_r, w, t0, pan, vel):
        a = int(t0 * SR)
        if a >= n or a + w.size <= 0:
            return
        lo = max(0, -a); a = max(0, a); b = min(n, a + w.size - lo)
        buf_l[a:b] += w[lo:lo + b - a] * vel * (1 - pan)
        if buf_r is not None:
            buf_r[a:b] += w[lo:lo + b - a] * vel * pan

    def note(m, t0, dur, vel, pan):
        add(L, R, M.piano(m, dur), t0, pan, vel)

    # bars start after the cold open hold so the rewind gets its own gesture
    start = tl.hold if tl.cos else 0.0
    if tl.cos:   # cold open: confident tonic chords on today's city
        for i, t0 in enumerate(np.arange(0, tl.hold - 0.5, beat * 2)):
            deg, maj = MAJ_PROG[i % 4]
            root = key + deg
            for j, m in enumerate([root - 12, root + 7, root + 12, root + 12 + (4 if maj else 3)]):
                note(m, t0 + j * 0.03, 3.0, 0.16 if j else 0.24, 0.4 + 0.07 * j)
            add(P, None, pad_tone(root + 12 + (4 if maj else 3), beat * 2 + 1.5), t0, 0, 0.05)
        # reversed swell into the rewind start ... then a falling arpeggio during the rewind
        rev = sum(M.piano(m, 2.5) for m in (key, key + 7, key + 12, key + 16))[::-1]
        add(L, R, rev.astype(np.float32), tl.hold - 2.5 + 0.2, 0.5, 0.18)
        rw = tl.cos - tl.hold
        seq = [key + 31, key + 28, key + 24, key + 19, key + 16, key + 12, key + 7, key + 4, key, key - 5]
        for j, m in enumerate(seq):
            note(min(m, 76), tl.hold + j * rw / len(seq) * 0.9, 1.6, 0.11 * (1 - j / len(seq) * 0.5), 0.3 + 0.04 * j)
        start = tl.cos
    nb = int(math.ceil((total - start) / bar)) + 1
    pat = M.PATTERNS[int(rng.integers(0, len(M.PATTERNS)))]
    rows = []
    for bi in range(nb):
        t0 = start + bi * bar
        if t0 > total:
            break
        mid = min(len(inten) - 1, int(t0 + bar / 2))
        I = float(inten[mid]); ten = bool(tense[int(t0):int(t0 + bar) + 1].any()); bm = bool(boom[mid])
        fin = t0 >= tl.cos + tl.segs[-1]['_t0']
        prog = (MIN_PROG_DARK if I > 0.85 else MIN_PROG) if ten else MAJ_PROG
        if fin and t0 + bar >= total - 0.5:
            prog = [(0, 1)] * 4                     # resolve on the tonic
        deg, maj = prog[bi % 4]
        root = key + deg
        tones = [root + 7, root + 12, root + 12 + (4 if maj else 3), root + 19]
        mode = 'calm' if I < 0.3 else 'tense' if ten else 'finale' if fin else 'boom' if bm else 'normal'
        rows.append((t0, mode, round(I, 2), deg))
        vscale = 0.6 + 0.7 * I
        note(root - 12, t0, bar * 1.1, 0.22 * vscale, 0.45)
        if mode == 'calm':
            for i in (0, 3, 5):
                note(tones[pat[i]], t0 + i * beat / 2, 2.6, 0.07, 0.4 + 0.08 * pat[i])
        else:
            step = beat / 4 if mode in ('boom', 'finale') and I > 0.6 else beat / 2
            k = int(round(bar / step))
            for i in range(k):
                ti = pat[i % len(pat)]
                vel = (0.085 if i % 2 == 0 else 0.06) * vscale * float(rng.uniform(0.85, 1.1))
                note(tones[ti], t0 + i * step + float(rng.uniform(0, 0.01)), 2.0, vel, 0.35 + 0.1 * ti)
            if mode in ('tense',):                   # low pulse on every beat
                for b4 in range(4):
                    note(root - 12, t0 + b4 * beat, 0.9, 0.12 * vscale, 0.5)
            if mode in ('normal', 'finale') and rng.random() < 0.5:   # occasional melody note, as in music.py
                m = key + 24 + M.PENTA[int(rng.integers(0, 5))]
                note(m - 12 if m > 76 else m, t0 + int(rng.integers(0, 4)) * beat, 2.8, 0.065 * vscale, 0.55)
        if I > 0.6 or fin:                           # string pad under the big moments
            for m in (root, root + 7, root + (4 if maj else 3) + 12):
                add(P, None, pad_tone(m, bar + 1.6), t0 - 0.3, 0, 0.045 * (I - 0.4) / 0.6 * (1.3 if fin else 1))
    for t, s in hits:
        if t >= (tl.cos if tl.cos else 0) and t < total:
            add(L, R, drum(0.22 * s), t, 0.5, 1.0)
    L = L[:int(total * SR)]; R = R[:int(total * SR)]; P = P[:int(total * SR)]
    b, a = signal.butter(2, 1800 / (SR / 2)); P = signal.lfilter(b, a, P).astype(np.float32)
    L += P * 0.9; R += P * 1.1
    bl, al = signal.butter(2, 3000 / (SR / 2))
    L = signal.lfilter(bl, al, L).astype(np.float32); R = signal.lfilter(bl, al, R).astype(np.float32)
    ir_t = np.arange(int(2.4 * SR)) / SR
    irs = []
    for _ in range(2):
        ir = rng.standard_normal(ir_t.size) * np.exp(-ir_t * 2.8)
        bi_, ai_ = signal.butter(1, 3000 / (SR / 2)); ir = signal.lfilter(bi_, ai_, ir); irs.append((ir / np.sqrt((ir ** 2).sum())).astype(np.float32))
    L = 0.8 * L + 0.38 * signal.oaconvolve(L, irs[0])[:L.size]; R = 0.8 * R + 0.38 * signal.oaconvolve(R, irs[1])[:R.size]
    t = np.arange(L.size) / SR
    fade = np.minimum(1, np.minimum(t / 0.8, (total - t) / 5.0)).clip(0, 1)
    st = np.stack([L * fade, R * fade], 1)
    try:
        li, tp = M.loudness(st)
        gain = min(10 ** ((M.TARGET_LUFS - li) / 20), 10 ** ((-2.0 - tp) / 20))
    except (FileNotFoundError, OSError):     # no ffmpeg (local preview): RMS approximation of -23 LUFS
        rms = float(np.sqrt((st ** 2).mean())) or 1e-9
        gain = min(10 ** ((M.TARGET_LUFS + 0.7) / 20) / rms, 0.79 / float(np.abs(st).max() or 1))
    st = np.clip(st * gain, -1, 1)
    a = int(t_from * SR); b = int((t_to if t_to else total) * SR)
    wavfile.write(out, SR, (st[a:b] * 32767).astype(np.int16))
    return rows, hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('slug'); ap.add_argument('out', nargs='?')
    ap.add_argument('--from', dest='t_from', type=float, default=0.0); ap.add_argument('--to', dest='t_to', type=float)
    ap.add_argument('--seed', type=int); ap.add_argument('--plan', action='store_true')
    a = ap.parse_args()
    city = json.load(open(os.path.join(ROOT, 'cities', a.slug, 'city.json'), encoding='utf-8'))
    seed = a.seed if a.seed is not None else city.get('seed', 7)
    if a.plan:
        tl, total, inten, tense, boom, hits = plan(city)
        for s in range(0, int(total), 5):
            print(f'{s // 60}:{s % 60:02d}  {"#" * int(inten[s] * 30):<30} {"TENSE" if tense[s] else ""}{"BOOM" if boom[s] else ""}')
        return
    rows, hits = render(city, a.out, seed, a.t_from, a.t_to)
    from collections import Counter
    print('bars:', dict(Counter(r[1] for r in rows)), 'hits:', len(hits))


if __name__ == '__main__':
    main()
