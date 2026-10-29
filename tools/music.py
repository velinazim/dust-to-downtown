"""Generative ambient soundtrack (original, no third-party audio → no copyright claims).

  python3 tools/music.py <seconds> <out.wav> [seed]

Slow minor-key chord progression on soft additive pads, a low drone, sparse bell plucks,
and a synthetic reverb. Each seed gives a different key/progression so episodes don't sound identical.
"""
import sys
import numpy as np
from scipy import signal
from scipy.io import wavfile

SR = 32000
PROGS = [[0, 8, 3, 10], [0, 5, 8, 7], [0, 3, 8, 10, 5, 7], [0, 10, 8, 7], [0, 8, 5, 10]]


def chord(root, minor_shape):
    return [root, root + (3 if minor_shape else 4), root + 7, root + 12]


def main(sec, out, seed=7):
    rng = np.random.default_rng(seed)
    n = int(sec * SR)
    t = np.arange(n) / SR
    key = 45 + int(rng.integers(0, 7))          # A2..D#3
    prog = PROGS[int(rng.integers(0, len(PROGS)))]
    clen = float(rng.choice([10.0, 12.0, 14.0]))
    L = np.zeros(n, np.float32); R = np.zeros(n, np.float32)
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)
    nch = int(np.ceil(sec / clen)) + 1
    for ci in range(nch):
        deg = prog[ci % len(prog)]
        minor = deg in (0, 5)
        notes = chord(key + deg, minor)
        a = int(max(0, (ci * clen - 2.5)) * SR); b = int(min(sec, (ci + 1) * clen + 2.5) * SR)
        if a >= n:
            break
        seg = np.arange(a, b) / SR
        env = np.clip((seg - ci * clen + 2.5) / 2.5, 0, 1) * np.clip(((ci + 1) * clen + 2.5 - seg) / 2.5, 0, 1)
        env = env * env * (3 - 2 * env)
        for k, m in enumerate(notes):
            f = hz(m + (12 if k == 3 else 0))
            vib = 1 + 0.0025 * np.sin(2 * np.pi * (0.13 + 0.03 * k) * seg + k)
            ph = 2 * np.pi * f * seg * vib
            tone = (np.sin(ph) + 0.35 * np.sin(2 * ph + 0.3) + 0.12 * np.sin(3 * ph + 1.1)) * (0.11 if k < 3 else 0.05)
            pan = 0.3 + 0.4 * (k / 3)
            L[a:b] += (tone * env * (1 - pan)).astype(np.float32); R[a:b] += (tone * env * pan).astype(np.float32)
    # drone on the tonic, breathing slowly
    dr = 0.07 * np.sin(2 * np.pi * hz(key - 12) * t) * (0.7 + 0.3 * np.sin(2 * np.pi * t / 23))
    L += dr.astype(np.float32); R += dr.astype(np.float32)
    # sparse bell plucks from the current chord
    tp = 3.0
    while tp < sec - 3:
        ci = int(tp // clen); deg = prog[ci % len(prog)]
        m = chord(key + deg, deg in (0, 5))[int(rng.integers(0, 4))] + 24
        dur = 3.5; a = int(tp * SR); b = min(n, a + int(dur * SR)); s = np.arange(b - a) / SR
        pl = (np.sin(2 * np.pi * hz(m) * s) + 0.25 * np.sin(2 * np.pi * hz(m) * 2.01 * s)) * np.exp(-s * 1.6) * 0.045
        p = float(rng.uniform(0.2, 0.8)); L[a:b] += (pl * (1 - p)).astype(np.float32); R[a:b] += (pl * p).astype(np.float32)
        tp += float(rng.choice([1.6, 2.4, 3.2, 4.8]))
    # gentle low-pass + reverb
    bl, al = signal.butter(2, 3200 / (SR / 2))
    L = signal.lfilter(bl, al, L).astype(np.float32); R = signal.lfilter(bl, al, R).astype(np.float32)
    ir_t = np.arange(int(3.2 * SR)) / SR
    irL = (rng.standard_normal(ir_t.size) * np.exp(-ir_t * 2.2)).astype(np.float32); irR = (rng.standard_normal(ir_t.size) * np.exp(-ir_t * 2.2)).astype(np.float32)
    irL /= np.sqrt((irL ** 2).sum()); irR /= np.sqrt((irR ** 2).sum())
    wetL = signal.oaconvolve(L, irL)[:n]; wetR = signal.oaconvolve(R, irR)[:n]
    L = 0.65 * L + 0.55 * wetL; R = 0.65 * R + 0.55 * wetR
    fade = np.minimum(1, np.minimum(t / 3.0, (sec - t) / 4.0)).clip(0, 1)
    st = np.stack([L * fade, R * fade], 1)
    st = st / (np.abs(st).max() + 1e-9) * 0.6
    wavfile.write(out, SR, (st * 32767).astype(np.int16))


if __name__ == '__main__':
    main(float(sys.argv[1]), sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 7)
