"""Teaser (18 s, 4:5): het adventshuis, raampje 1 gaat open, een kerstdorpje komt tot leven, eindkaart."""
import math, random, os, subprocess, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance

OUD = "/tmp/claude-0/-home-user-stijlstudio/f55e38bf-cb55-5076-bedb-49f8c8e8917c/scratchpad/"
HIER = "/tmp/claude-0/-home-user/f55e38bf-cb55-5076-bedb-49f8c8e8917c/scratchpad/teaser/"
UP = "/root/.claude/uploads/f55e38bf-cb55-5076-bedb-49f8c8e8917c/"
W, H, FPS = 720, 900, 24
DUUR = 18.0
N = int(DUUR * FPS)
HAND = lambda n: ImageFont.truetype(OUD + "Caveat.ttf", n)
SERIF = lambda n: ImageFont.truetype(OUD + "Fraunces.ttf", n)
CREME, BORDEAUX, GOUD, ROOD = (246, 239, 225), (124, 29, 38), (184, 146, 74), (194, 42, 51)
random.seed(7)

ease = lambda t: 0 if t <= 0 else 1 if t >= 1 else t * t * (3 - 2 * t)
def seg(t, a, b): return 0 if t <= a else 1 if t >= b else (t - a) / (b - a)

def warm(im, kleur=.92):
    im = ImageEnhance.Color(im).enhance(kleur)
    a = np.asarray(im).astype(np.float32) / 255; a = a * .92 + .04; a[..., 0] *= 1.05; a[..., 2] *= .9
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
def foto(n, box): return warm(Image.open(UP + n + "-image.jpg").convert("RGB").crop(box))

def cover(img, w, h):
    s = max(w / img.width, h / img.height); im = img.resize((math.ceil(img.width * s), math.ceil(img.height * s)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2; return im.crop((x, y, x + w, y + h))
def kenburns(img, t, z0, z1, px=0, py=0):
    base = cover(img, int(W * 1.25), int(H * 1.25)); z = z0 + (z1 - z0) * ease(t)
    cw, ch = base.width / z / 1.25 * 1.0, base.height / z / 1.25
    cx = base.width / 2 + px * (base.width - cw) / 2 * t; cy = base.height / 2 + py * (base.height - ch) / 2 * t
    return base.crop((int(cx - cw / 2), int(cy - ch / 2), int(cx + cw / 2), int(cy + ch / 2))).resize((W, H), Image.BICUBIC)

# ---------- beeld ----------
SHOTS = [  # (foto, uitsnede, z0, z1, px, py, onderschrift)
    (foto("35106959", (0, 450, 735, 1560)), 1.0, 1.12, .2, 0, "Elke dag één raampje."),
    (foto("ce956c30", (0, 330, 870, 1560)), 1.12, 1.0, 0, -.2, "Voor iedereen iets anders."),
    (foto("839938e6", (0, 570, 1080, 1875)), 1.0, 1.15, -.2, 0, "Spelletjes. Filmpjes. Bonnen."),
    (foto("29668888", (90, 450, 990, 1665)), 1.15, 1.0, 0, .2, "Niet tot vanavond wachten."),
]
D0, SHOT, OVER = 6.0, 2.4, .5   # tafereel begint op 6 s; elk beeld 2,4 s; overvloei 0,5 s
EIND = D0 + len(SHOTS) * (SHOT - OVER) + OVER   # ~13,9 s

# het huis: groot, zodat inzoomen scherp blijft
huis = Image.open(HIER + "huis.png").convert("RGBA")
for hoek in [(2, 2), (huis.width - 3, 2)]:   # de achtergrond van de app rond het dak weghalen
    ImageDraw.floodfill(huis, hoek, (0, 0, 0, 0), thresh=40)
SW, SH = 5600, 7000
scene = Image.new("RGB", (SW, SH), CREME)
dots = ImageDraw.Draw(scene)
for i in range(2600): x, y = random.randrange(SW), random.randrange(SH); dots.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(236, 226, 206))
HX, HY = (SW - huis.width) // 2, SH - huis.height - 160
scene.paste(huis, (HX, HY), huis)
RAAM = (HX + 1134, HY + 3535, 465, 620)   # raampje 1 (x, y, b, h) in de scène
RCX, RCY = RAAM[0] + RAAM[2] / 2, RAAM[1] + RAAM[3] / 2
ZW = 432 / (RAAM[2] * W / SW)              # zoom waarbij het raampje 432 px breed is

def huisbeeld(z, cx, cy):
    cw, ch = SW / z, SH / z
    cx = min(max(cx, cw / 2), SW - cw / 2); cy = min(max(cy, ch / 2), SH - ch / 2)
    box = (int(cx - cw / 2), int(cy - ch / 2), int(cx + cw / 2), int(cy + ch / 2))
    return scene.crop(box).resize((W, H), Image.BICUBIC if z > 3 else Image.LANCZOS), box
def raam_in_beeld(box):
    sx, sy = W / (box[2] - box[0]), H / (box[3] - box[1])
    return (RAAM[0] - box[0]) * sx, (RAAM[1] - box[1]) * sy, RAAM[2] * sx, RAAM[3] * sy

# ---------- sneeuw, glinsters, gloed ----------
vlok = {r: Image.new("RGBA", (r * 4, r * 4), (255, 255, 255, 0)) for r in (2, 3, 4)}
for r, v in vlok.items(): ImageDraw.Draw(v).ellipse((r, r, 3 * r, 3 * r), fill=(255, 255, 255, 220)); vlok[r] = v.filter(ImageFilter.GaussianBlur(r * .45))
SNEEUW = [(random.choice((2, 2, 3, 4)), random.uniform(0, W), random.uniform(0, H), random.uniform(25, 70)) for _ in range(130)]
def sneeuw(img, t, sterk=1.0):
    for r, x, y, v in SNEEUW[:int(len(SNEEUW) * sterk)]:
        yy = (y + v * t) % (H + 20) - 10; xx = x + math.sin(t * .8 + y) * 10
        img.alpha_composite(vlok[r], (int(xx - r * 2), int(yy - r * 2)))
def ster(d, x, y, s, a):
    c = (255, 236, 180, int(255 * a))
    d.polygon([(x, y - s), (x + s * .22, y - s * .22), (x + s, y), (x + s * .22, y + s * .22), (x, y + s), (x - s * .22, y + s * .22), (x - s, y), (x - s * .22, y - s * .22)], fill=c)
GLINST = [(random.uniform(-.6, .6), random.uniform(-.7, .7), random.uniform(0, 1), random.uniform(8, 20)) for _ in range(26)]
TWINKEL = [(random.uniform(0, W), random.uniform(0, H * .75), random.uniform(0, 6.28), random.uniform(3, 7)) for _ in range(30)]
def twinkel(img, t):
    d = ImageDraw.Draw(img)
    for x, y, f, s in TWINKEL:
        a = max(0, math.sin(t * 3.1 + f)) ** 3
        if a > .05: ster(d, x, y, s, a * .8)

# ---------- onderschriften ----------
def kaart(tekst, sub=None):
    f = HAND(58); br = max(int(f.getlength(tekst)) + 90, 300); h = 150 if sub else 110
    t = Image.new("RGBA", (br + 30, h + 30), (0, 0, 0, 0)); d = ImageDraw.Draw(t)
    sh = Image.new("RGBA", t.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((18, 22, br + 18, h + 22), 26, fill=(30, 15, 10, 110))
    t.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    d.rounded_rectangle((12, 12, br + 12, h + 12), 26, fill=(255, 253, 246, 255), outline=GOUD + (255,), width=3)
    d.text((br // 2 + 12, (62 if sub else h // 2 + 12)), tekst, font=f, fill=BORDEAUX + (255,), anchor="mm")
    if sub: d.text((br // 2 + 12, 120), sub, font=SERIF(22), fill=(120, 100, 90, 255), anchor="mm")
    if t.width > W - 30: t = t.resize((W - 30, int(t.height * (W - 30) / t.width)), Image.LANCZOS)
    return t
def toon(img, lab, t, a0, a1, y):
    if not (a0 <= t <= a1): return
    al = min(1, (t - a0) / .5, (a1 - t) / .5)
    l2 = lab.copy(); l2.putalpha(l2.split()[3].point(lambda v: int(v * al)))
    img.alpha_composite(l2, ((W - lab.width) // 2, int(y - 10 * (1 - al) + math.sin(t * 1.3) * 3)))
LAB_START = kaart("26 raampjes.", "vanaf 1 december")
LAB_SHOT = [kaart(s[-1]) for s in SHOTS]

# ---------- het sleetje als stopmotion (uitgeknipt van de witte achtergrond) ----------
def knip_slee():
    im = Image.open(UP + "391e3feb-image.jpg").convert("RGB").crop((200, 1000, 880, 1500))
    v = im.copy()
    for hoek in [(0, 0), (v.width - 1, 0), (0, v.height - 1), (v.width - 1, v.height - 1)]:
        ImageDraw.floodfill(v, hoek, (255, 0, 255), thresh=22)
    a = np.asarray(v).astype(int); bg = (a[..., 0] == 255) & (a[..., 1] == 0) & (a[..., 2] == 255)
    m = Image.fromarray(((~bg) * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.0))
    ys, xs = np.where(~bg); box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    s = warm(im).convert("RGBA"); s.putalpha(m); s = s.crop(box)
    return s.resize((170, int(s.height * 170 / s.width)), Image.LANCZOS)
SLEE = knip_slee()
def sleetje(img, t):   # 8 beeldjes per seconde, met een schokje: echt stopmotion
    if not (D0 + .5 <= t <= D0 + SHOT + .2): return
    j = int((t - D0 - .5) * 8); u = j / (8 * (SHOT - .3))
    rj = random.Random(j); x = -170 + u * (W + 200) + rj.randint(-3, 3); y = H * .70 - 18 * abs(math.sin(j * .9)) + rj.randint(-2, 2)
    img.alpha_composite(SLEE.rotate(rj.uniform(-3, 3), expand=True, resample=Image.BICUBIC), (int(x), int(y)))

# ---------- eindkaart ----------
def eindkaart():
    e = Image.new("RGBA", (W, H), CREME + (255,)); d = ImageDraw.Draw(e)
    for i in range(500): x, y = random.randrange(W), random.randrange(H); d.ellipse((x - 1, y - 1, x + 1, y + 1), fill=(232, 220, 196, 255))
    klein = huis.resize((int(huis.width * 380 / huis.height), 380), Image.LANCZOS)
    e.alpha_composite(klein, ((W - klein.width) // 2, 70))
    d.text((W // 2, 520), "Family Crazy", font=SERIF(58), fill=BORDEAUX + (255,), anchor="mm")
    d.text((W // 2, 590), "Adventskalender", font=HAND(74), fill=ROOD + (255,), anchor="mm")
    d.line((W // 2 - 80, 650, W // 2 + 80, 650), fill=GOUD + (255,), width=3)
    d.text((W // 2, 700), "Elke dag een raampje. Vanaf 1 december.", font=SERIF(26), fill=(110, 92, 84, 255), anchor="mm")
    d.rounded_rectangle((W // 2 - 220, 760, W // 2 + 220, 830), 35, fill=BORDEAUX + (255,))
    d.text((W // 2, 795), "adventscalender.app", font=SERIF(32), fill=(250, 244, 232, 255), anchor="mm")
    return e
EINDKAART = eindkaart()

# ---------- frames ----------
map_ = HIER + "frames"; shutil.rmtree(map_, ignore_errors=True); os.makedirs(map_)
dicht = None
for f in range(N):
    t = f / FPS
    if t < 6.4:
        # A: van het hele huis naar raampje 1;  B: luikjes open;  C: het raampje in
        if t < 3.4:
            u = ease(seg(t, 1.0, 3.4)); z = 1 + (ZW - 1) * u ** 1.6
            cx = SW / 2 + (RCX - SW / 2) * u; cy = SH / 2 + (RCY - SH / 2) * u
        elif t < 5.2:
            z = ZW * (1 + .05 * seg(t, 3.4, 5.2)); cx, cy = RCX, RCY
        else:
            z = ZW * 1.05 * (1 + 5.5 * ease(seg(t, 5.2, 6.4)) ** 2); cx, cy = RCX, RCY
        img, box = huisbeeld(z, cx, cy); img = img.convert("RGBA")
        rx, ry, rw, rh = raam_in_beeld(box)
        if t >= 3.4:
            if dicht is None: dicht = img.crop((int(rx), int(ry), int(rx + rw), int(ry + rh)))   # het dichte raampje, voor de luikjes
            binnen = kenburns(SHOTS[0][0], 0, 1.0, 1.0).resize((max(2, int(rw)), max(2, int(rh))), Image.BICUBIC)
            lichter = ImageEnhance.Brightness(binnen).enhance(.75 + .35 * ease(seg(t, 3.6, 5.0)))
            img.paste(lichter, (int(rx), int(ry)))
            o = ease(seg(t, 3.6, 4.9))
            if o < 1:
                L = dicht.crop((0, 0, dicht.width // 2, dicht.height)); R = dicht.crop((dicht.width // 2, 0, dicht.width, dicht.height))
                bw = max(1, int(L.width * math.cos(o * math.pi / 2) * (rw / dicht.width)))
                hh = max(1, int(rh))
                Ls = ImageEnhance.Brightness(L.resize((bw, hh))).enhance(1 - .35 * o); Rs = ImageEnhance.Brightness(R.resize((bw, hh))).enhance(1 - .35 * o)
                img.alpha_composite(Ls, (int(rx), int(ry))); img.alpha_composite(Rs, (int(rx + rw - bw), int(ry)))
            # warme gloed en glinsters rond het raampje
            g = seg(t, 3.7, 4.6) * (1 - seg(t, 5.4, 6.2))
            if g > 0:
                gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dg = ImageDraw.Draw(gl)
                dg.ellipse((rx - rw * .5, ry - rh * .4, rx + rw * 1.5, ry + rh * 1.4), fill=(255, 205, 120, int(120 * g)))
                img.alpha_composite(gl.filter(ImageFilter.GaussianBlur(60)))
                d = ImageDraw.Draw(img)
                for gx, gy, gf, gs in GLINST:
                    a = max(0, math.sin((t - 3.7) * 4 + gf * 6.28)) * g
                    if a > .05: ster(d, rx + rw / 2 + gx * rw * 1.2, ry + rh / 2 + gy * rh * 1.1, gs, a)
        # vloeiend over in het eerste tafereel
        if t > 5.9:
            a = seg(t, 5.9, 6.4); img = Image.blend(img, kenburns(SHOTS[0][0], 0, SHOTS[0][1], SHOTS[0][2], SHOTS[0][3], SHOTS[0][4]).convert("RGBA"), a)
        sneeuw(img, t, .7)
        toon(img, LAB_START, t, .3, 2.9, 14)
    elif t < EIND:
        beeld = None
        for i, (im, z0, z1, px, py, _) in enumerate(SHOTS):
            s = D0 + i * (SHOT - OVER)
            if s - .001 <= t < s + SHOT:
                fr = kenburns(im, (t - s) / SHOT, z0, z1, px, py)
                a = 1 if i == 0 else min(1, (t - s) / OVER)
                beeld = fr if beeld is None or a >= 1 else Image.blend(beeld, fr, a)
        img = beeld.convert("RGBA")
        lek = Image.new("RGBA", (W, H), (0, 0, 0, 0)); lx = W * (.2 + .6 * (.5 + .5 * math.sin(t * .5)))
        ImageDraw.Draw(lek).ellipse((lx - 260, -220, lx + 260, 220), fill=(255, 190, 120, 50)); img.alpha_composite(lek.filter(ImageFilter.GaussianBlur(80)))
        twinkel(img, t); sleetje(img, t); sneeuw(img, t)
        for i, lab in enumerate(LAB_SHOT):
            s = D0 + i * (SHOT - OVER); toon(img, lab, t, s + .3, s + SHOT - .25, H - 190)
    else:
        a = seg(t, EIND, EIND + .6)
        laatste = kenburns(SHOTS[-1][0], 1, *SHOTS[-1][1:5]).convert("RGBA")
        img = Image.blend(laatste, EINDKAART, a) if a < 1 else EINDKAART.copy()
        sneeuw(img, t, .5)
    # vignet, en in/uit faden
    out = img.convert("RGB")
    if f < 10: out = Image.blend(Image.new("RGB", (W, H), (20, 10, 6)), out, f / 10)
    if f > N - 12: out = Image.blend(Image.new("RGB", (W, H), (20, 10, 6)), out, (N - f) / 12)
    out.save(f"{map_}/{f:04d}.jpg", quality=92)
    if f % 48 == 0: print("frame", f, round(t, 1), flush=True)

# ---------- muziek en film ----------
exec(open(OUD + "muziek.py").read().split("KEUZE = {")[0])
wav = HIER + "teaser.wav"; schrijf(wav, maak("jingle", DUUR, 140, 1, False, True))
uit = HIER + "Family Crazy Adventskalender - teaser.mp4"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{map_}/%04d.jpg", "-i", wav, "-map", "0:v", "-map", "1:a",
                "-c:v", "libx264", "-crf", "21", "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", uit], check=True)
print("klaar", uit, os.path.getsize(uit) // 1024, "kB")
