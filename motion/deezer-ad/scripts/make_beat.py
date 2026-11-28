# Génère une prod trap originale (808, hi-hats roulés, snare) de 30 s, 120 BPM,
# calée sur les coupes de la vidéo (multiples de 0,5 s). Aucun sample protégé.
import wave
import numpy as np

SR = 44100
DUR = 30.0
N = int(SR * DUR)
BPM = 120
BEAT = 60 / BPM  # 0,5 s
rng = np.random.default_rng(7)
out = np.zeros(N)

def add(sig, t0, gain=1.0):
    i = int(t0 * SR)
    if i >= N:
        return
    end = min(N, i + len(sig))
    out[i:end] += gain * sig[: end - i]

def kick808(length=0.9, f0=110, f1=38):
    t = np.arange(int(SR * length)) / SR
    freq = f1 + (f0 - f1) * np.exp(-t * 18)
    phase = 2 * np.pi * np.cumsum(freq) / SR
    env = np.exp(-t * 3.2)
    return np.tanh(np.sin(phase) * env * 1.8) * 0.9

def snare(length=0.22):
    t = np.arange(int(SR * length)) / SR
    noise = rng.uniform(-1, 1, len(t))
    body = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30)
    return (noise * np.exp(-t * 22) * 0.5 + body * 0.5) * 0.6

def hat(length=0.06, gain=0.25):
    t = np.arange(int(SR * length)) / SR
    n = rng.uniform(-1, 1, len(t))
    hp = np.diff(n, prepend=0)  # filtre passe-haut grossier
    return hp * np.exp(-t * 90) * gain

def bass_note(freq, length):
    t = np.arange(int(SR * length)) / SR
    drive = np.tanh(np.sin(2 * np.pi * freq * t) * 2.2)
    return drive * np.exp(-t * 1.6) * 0.45

def riser(length=2.0):
    t = np.arange(int(SR * length)) / SR
    f = 200 + 2400 * (t / length) ** 2
    sig = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.15
    noise = rng.uniform(-1, 1, len(t)) * 0.25 * (t / length) ** 2
    return (sig + noise) * np.linspace(0, 1, len(t))

# Grille : 4 mesures de 2 s = 16 temps, boucle sur 30 s
bars = int(DUR // 2)
progression = [45, 41, 48, 43]  # A, F, C, G (en demi-tons depuis A1 = 33 Hz base)
def midi_freq(m):
    return 440 * 2 ** ((m - 69) / 12)

for b in range(bars + 1):
    t_bar = b * 4 * BEAT
    root = progression[b % 4]
    # 808 : coups sur 1 et syncopé
    for pos in (0, 2.5, 3.25) if b % 2 else (0, 2.75):
        add(kick808(), t_bar + pos * BEAT, 0.95)
    # snare / clap sur 2 et 4
    add(snare(), t_bar + 1 * BEAT, 0.8)
    add(snare(), t_bar + 3 * BEAT, 0.8)
    # hi-hats roulés (croches et doubles croches, volume variable)
    for k in range(16):
        g = 0.18 + 0.12 * rng.random()
        if k % 4 == 3 and b % 2:
            g *= 0.4
        add(hat(gain=g), t_bar + k * BEAT / 4)
    # 808 mélodique
    add(bass_note(midi_freq(root), 1.8), t_bar + 0.0, 0.55)
    add(bass_note(midi_freq(root + 3), 0.9), t_bar + 2.0 * BEAT, 0.45)

# Moments forts alignés sur les coupes de la vidéo
for t in (0.0, 3.0, 7.0, 12.0, 18.0, 23.0, 27.0):
    add(kick808(1.2, 90, 30) * 1.1, t, 0.9)
for t in (3.0, 7.0, 12.0, 18.0, 23.0):
    add(riser(0.5 * 2), t - 1.0, 0.25)  # montée avant chaque coupe
add(riser(2.0), 26.0, 0.35)

# Fade-in court et fade-out final
fade_in = int(0.05 * SR)
out[:fade_in] *= np.linspace(0, 1, fade_in)
fade_out = int(1.2 * SR)
out[-fade_out:] *= np.linspace(1, 0, fade_out)

# Normalisation douce et stéréo léger
peak = np.max(np.abs(out))
out = out / peak * 0.85
left = out * 0.98
right = np.roll(out, int(0.012 * SR)) * 1.0
stereo = np.stack([left, right], axis=1)
pcm = (np.clip(stereo, -1, 1) * 32767).astype('<i2')

with wave.open('/home/user/cat.exe-osint/motion/deezer-ad/public/beat.wav', 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print('beat.wav ok', round(DUR, 1), 's')
