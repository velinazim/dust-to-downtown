"""Episode soundtrack.

  python3 tools/music.py <seconds> <out.wav> [seed]

If music/library/ holds audio files (tracks downloaded by the owner from the YouTube Audio Library,
"no attribution required" only), the seed shuffles them and they are joined with crossfades until the
video is covered, then levelled to a soft background loudness. Otherwise the generator below is used.

Style (9.11.2026 — owner found the old drone/pad ambience oppressive): a calm, warm documentary piano in a
major key: gentle arpeggiated chords over a soft bass, an occasional pentatonic melody note, ~70 BPM, no
sustained drones. Each seed picks a different key, progression, tempo and arpeggio patterns.
"""
import json, os, subprocess, sys, tempfile
import numpy as np
from scipy import signal
from scipy.io import wavfile

SR = 32000


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB = os.path.join(ROOT, 'music', 'library')
EXTS = ('.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac')
TARGET_LUFS = -23.0      # soft background level (owner request 9.11.2026)
XFADE = 4.0


def library():
    if not os.path.isdir(LIB):
        return []
    return sorted(os.path.join(LIB, f) for f in os.listdir(LIB) if f.lower().endswith(EXTS))


def credit(lang):
    """Music credit line for video descriptions."""
    if library():
        return {'en': 'Music: YouTube Audio Library.', 'tr': 'Müzik: YouTube Ses Kitaplığı.'}[lang]
    return {'en': 'Music: original.', 'tr': 'Müzik: özgün.'}[lang]


def decode(path):
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', path, '-f', 's16le', '-ac', '2', '-ar', str(SR), '-'],
                         check=True, capture_output=True).stdout
    return (np.frombuffer(raw, np.int16).reshape(-1, 2).astype(np.float32) / 32768)


def loudness(st):
    with tempfile.NamedTemporaryFile(suffix='.wav') as f:
        wavfile.write(f.name, SR, (np.clip(st, -1, 1) * 32767).astype(np.int16))
        err = subprocess.run(['ffmpeg', '-hide_banner', '-i', f.name, '-af', 'loudnorm=print_format=json', '-f', 'null', '-'],
                             capture_output=True, text=True).stderr
    js = json.loads(err[err.rindex('{'):err.rindex('}') + 1])
    return float(js['input_i']), float(js['input_tp'])


def from_library(sec, out, seed, files):
    rng = np.random.default_rng(seed)
    order = list(rng.permutation(len(files)))
    n = int(sec * SR); xf = int(XFADE * SR)
    st = np.zeros((0, 2), np.float32); k = 0
    while st.shape[0] < n:
        tr = decode(files[order[k % len(order)]]); k += 1
        if k % len(order) == 0:          # whole library used: reshuffle for the next pass
            order = list(rng.permutation(len(files)))
        if st.shape[0] >= xf and tr.shape[0] > 2 * xf:
            ramp = np.linspace(0, 1, xf, dtype=np.float32)[:, None]
            st[-xf:] = st[-xf:] * (1 - ramp) + tr[:xf] * ramp
            tr = tr[xf:]
        st = np.concatenate([st, tr])
    st = st[:n]
    t = np.arange(n) / SR
    fade = np.minimum(1, np.minimum(t / 3.0, (sec - t) / 4.0)).clip(0, 1).astype(np.float32)[:, None]
    st = st * fade
    li, tp = loudness(st)
    gain = 10 ** ((TARGET_LUFS - li) / 20)
    gain = min(gain, 10 ** ((-2.0 - tp) / 20))     # keep true peak under -2 dBFS
    st = np.clip(st * gain, -1, 1)
    wavfile.write(out, SR, (st * 32767).astype(np.int16))
    print(f'music: library ({len(files)} tracks, {k} used), {li:.1f} -> ~{TARGET_LUFS} LUFS')

# progressions as (semitones above the key, major?) — bright, consonant pop/documentary changes
PROGS = [[(0, 1), (7, 1), (9, 0), (5, 1)],      # I  V  vi IV
         [(0, 1), (9, 0), (5, 1), (7, 1)],      # I  vi IV V
         [(9, 0), (5, 1), (0, 1), (7, 1)],      # vi IV I  V
         [(0, 1), (5, 1), (9, 0), (7, 1)],      # I  IV vi V
         [(0, 1), (4, 0), (5, 1), (7, 1)]]      # I  iii IV V
PATTERNS = [[0, 1, 2, 3, 2, 1, 2, 1], [0, 2, 1, 2, 3, 2, 1, 2], [0, 1, 2, 1, 3, 1, 2, 1], [0, 2, 3, 2, 1, 2, 3, 2]]
PENTA = [0, 2, 4, 7, 9]
_cache = {}


def hz(m):
    return 440 * 2 ** ((m - 69) / 12)


def piano(m, dur):
    """Soft felt-piano tone: few harmonics, upper ones dying faster, gentle attack, slight inharmonicity."""
    key = (m, round(dur, 2))
    if key in _cache:
        return _cache[key]
    s = np.arange(int(dur * SR)) / SR
    f = hz(m); x = np.zeros_like(s)
    for h in range(1, 6):
        fh = f * h * np.sqrt(1 + 0.0003 * h * h)
        if fh > 5000:
            break
        x += np.sin(2 * np.pi * fh * s) * (h ** -1.8) * np.exp(-s * (0.9 + 0.9 * h) * (f / 260) ** 0.3)
    x *= np.minimum(1, s / 0.02)   # softer hammer * np.minimum(1, (dur - s) / 0.25).clip(0, 1)
    _cache[key] = x.astype(np.float32)
    return _cache[key]


def main(sec, out, seed=7):
    files = library()
    if files:
        return from_library(sec, out, seed, files)
    rng = np.random.default_rng(seed)
    n = int(sec * SR) + SR * 4
    L = np.zeros(n, np.float32); R = np.zeros(n, np.float32)
    key = 48 + int(rng.integers(0, 7))                  # C3..F#3
    prog = PROGS[int(rng.integers(0, len(PROGS)))]
    beat = 60.0 / float(rng.choice([66, 70, 74]))
    bar = 4 * beat

    def add(m, t0, dur, vel, pan):
        a = int(t0 * SR); w = piano(m, dur) * vel; b = min(n, a + w.size)
        L[a:b] += w[:b - a] * (1 - pan); R[a:b] += w[:b - a] * pan

    nb = int(np.ceil(sec / bar)) + 1
    pat = PATTERNS[int(rng.integers(0, len(PATTERNS)))]
    for bi in range(nb):
        t0 = bi * bar
        if t0 > sec:
            break
        if bi % 8 == 0 and bi:
            pat = PATTERNS[int(rng.integers(0, len(PATTERNS)))]
        deg, major = prog[bi % len(prog)]
        root = key + deg
        tones = [root + 7, root + 12, root + 12 + (4 if major else 3), root + 19]   # mid register only: no high 'ping' notes (owner, 9.11)
        phase = (bi // 16) % 4                          # every 16 bars: a quieter, sparser section
        sparse = phase == 3
        add(root - 12, t0, bar * 1.1, 0.22, 0.45)       # soft bass
        if not sparse:
            add(root - 12 + 7, t0 + 2 * beat, bar * 0.6, 0.12, 0.45)
        for i, ti in enumerate(pat):
            if sparse and i % 2:
                continue
            vel = (0.09 if i % 2 == 0 else 0.065) * float(rng.uniform(0.85, 1.1))
            add(tones[ti], t0 + i * beat / 2 + float(rng.uniform(0, 0.012)), 2.2, vel, 0.35 + 0.1 * ti)
        if phase in (1, 2):                             # simple melody, only in the middle sections
            for b4 in range(4):
                if rng.random() < 0.22:
                    m = key + 24 + PENTA[int(rng.integers(0, 5))]
                    m = m - 12 if m > 76 else m   # keep the melody below ~E5
                    add(m, t0 + b4 * beat, 2.8, 0.07, 0.55)
    L = L[:int(sec * SR)]; R = R[:int(sec * SR)]
    t = np.arange(L.size) / SR
    bl, al = signal.butter(2, 3000 / (SR / 2))
    L = signal.lfilter(bl, al, L).astype(np.float32); R = signal.lfilter(bl, al, R).astype(np.float32)
    ir_t = np.arange(int(2.2 * SR)) / SR
    irL = (rng.standard_normal(ir_t.size) * np.exp(-ir_t * 3.0)).astype(np.float32); irR = (rng.standard_normal(ir_t.size) * np.exp(-ir_t * 3.0)).astype(np.float32)
    bi_, ai_ = signal.butter(1, 3000 / (SR / 2)); irL = signal.lfilter(bi_, ai_, irL); irR = signal.lfilter(bi_, ai_, irR)
    irL /= np.sqrt((irL ** 2).sum()); irR /= np.sqrt((irR ** 2).sum())
    wetL = signal.oaconvolve(L, irL)[:L.size]; wetR = signal.oaconvolve(R, irR)[:R.size]
    L = 0.8 * L + 0.35 * wetL; R = 0.8 * R + 0.35 * wetR
    fade = np.minimum(1, np.minimum(t / 3.0, (sec - t) / 5.0)).clip(0, 1)
    st = np.stack([L * fade, R * fade], 1)
    li, tp = loudness(st)
    gain = min(10 ** ((TARGET_LUFS - li) / 20), 10 ** ((-2.0 - tp) / 20))
    wavfile.write(out, SR, (np.clip(st * gain, -1, 1) * 32767).astype(np.int16))


if __name__ == '__main__':
    main(float(sys.argv[1]), sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 7)
