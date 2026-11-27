"""Teaser 2 (20 s, 4:5), show don't tell: startscherm, raampje 2 (waslijn + wasbon), raampje 20 (Groningen), eindkaart."""
import json, glob
HIER = "/tmp/claude-0/-home-user/f55e38bf-cb55-5076-bedb-49f8c8e8917c/scratchpad/teaser/"
_bron = open(HIER + "teaser.py").read()
exec(_bron.split("# ---------- beeld ----------")[0])
exec("# ---------- sneeuw" + _bron.split("# ---------- sneeuw")[1].split("# ---------- onderschriften")[0])
DUUR = 20.0; N = int(DUUR * FPS)
SPEL = json.load(open(HIER + "spel.json"))

# ---------- tijdlijn ----------
T_START, T_A, T_B, T_C, T_G, T_K, T_P, T_B2, T_C2, T_GR, T_PO, T_E = 0, 2.2, 4.2, 5.2, 5.9, 8.9, 10.9, 12.7, 13.6, 14.2, 16.6, 18.0

# ---------- het huis in een grote scène ----------
huis = Image.open(HIER + "huis.png").convert("RGBA")
for hoek in [(2, 2), (huis.width - 3, 2)]: ImageDraw.floodfill(huis, hoek, (0, 0, 0, 0), thresh=40)
masker = np.asarray(Image.open(HIER + "huis-masker.png").convert("RGB")).astype(int)
glasmasker = Image.fromarray((((masker[..., 0] > 200) & (masker[..., 1] < 80) & (masker[..., 2] > 200)) * 255).astype(np.uint8))
SW, SH = 5600, 7000
scene = Image.new("RGB", (SW, SH), CREME); dots = ImageDraw.Draw(scene)
for i in range(3000): x, y = random.randrange(SW), random.randrange(SH); dots.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(236, 226, 206))
HX, HY = (SW - huis.width) // 2, SH - huis.height - 160
scene.paste(huis, (HX, HY), huis)
RAMEN = {int(k): (HX + v[0], HY + v[1], v[2], v[3]) for k, v in json.load(open(HIER + "ramen.json")).items()}
MASK = {d: glasmasker.crop((int(r[0] - HX), int(r[1] - HY), int(r[0] - HX + r[2]), int(r[1] - HY + r[3]))) for d, r in RAMEN.items()}
def zw(d): return 400 / (RAMEN[d][2] * W / SW)
def midden(d): r = RAMEN[d]; return r[0] + r[2] / 2, r[1] + r[3] / 2

def huisbeeld(z, cx, cy):
    cw, ch = SW / z, SH / z
    cx = min(max(cx, cw / 2), SW - cw / 2); cy = min(max(cy, ch / 2), SH - ch / 2)
    box = (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)
    im = scene.crop(tuple(int(v) for v in box)).resize((W, H), Image.BICUBIC if z > 2.5 else Image.LANCZOS)
    return im.convert("RGBA"), box
def in_beeld(d, box):
    sx = W / (box[2] - box[0]); r = RAMEN[d]
    return (r[0] - box[0]) * sx, (r[1] - box[1]) * sx, r[2] * sx, r[3] * sx

def open_raam(img, d, box, inhoud, o, gloed, t, dicht):
    """Teken raampje d: inhoud achter het glas, luikjes die openzwaaien (o 0..1), gloed en glinsters."""
    rx, ry, rw, rh = in_beeld(d, box)
    iw, ih = max(2, int(rw)), max(2, int(rh)); m = MASK[d].resize((iw, ih))
    bin_ = cover(inhoud, iw, ih).convert("RGBA"); bin_ = ImageEnhance.Brightness(bin_).enhance(.8 + .3 * o); bin_.putalpha(m)
    img.alpha_composite(bin_, (int(rx), int(ry)))
    if o < 1 and dicht is not None:
        dl = dicht.resize((iw, ih)); dl.putalpha(m)
        L = dl.crop((0, 0, iw // 2, ih)); R = dl.crop((iw // 2, 0, iw, ih))
        bw = max(1, int(L.width * math.cos(o * math.pi / 2)))
        Ls = L.resize((bw, ih)); Rs = R.resize((bw, ih))
        Ls = Image.alpha_composite(Ls, Image.new("RGBA", Ls.size, (60, 30, 20, int(90 * o)))); Ls.putalpha(L.resize((bw, ih)).split()[3])
        Rs = Image.alpha_composite(Rs, Image.new("RGBA", Rs.size, (60, 30, 20, int(90 * o)))); Rs.putalpha(R.resize((bw, ih)).split()[3])
        img.alpha_composite(Ls, (int(rx), int(ry))); img.alpha_composite(Rs, (int(rx + rw - bw), int(ry)))
    if gloed > 0:
        gl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(gl).ellipse((rx - rw * .5, ry - rh * .4, rx + rw * 1.5, ry + rh * 1.4), fill=(255, 205, 120, int(110 * gloed)))
        img.alpha_composite(gl.filter(ImageFilter.GaussianBlur(60)))
        dd = ImageDraw.Draw(img)
        for gx, gy, gf, gs in GLINST:
            a = max(0, math.sin(t * 4 + gf * 6.28)) * gloed
            if a > .05: ster(dd, rx + rw / 2 + gx * rw * 1.2, ry + rh / 2 + gy * rh * 1.1, gs, a)
    return rx, ry, rw, rh

# ---------- beelden: spelletje, bon, Groningen ----------
SPELF = [Image.open(f).convert("RGB") for f in sorted(glob.glob(HIER + "spel/*.png"))]
BON1, BON2 = Image.open(HIER + "bon1.png").convert("RGBA"), Image.open(HIER + "bon2.png").convert("RGBA")
def frames_uit(mp4, van, tot, naam):
    d = HIER + naam; shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(van), "-t", str(tot - van), "-i", mp4, "-vf", "fps=24", f"{d}/%03d.png"], check=True)
    return [Image.open(f).convert("RGB") for f in sorted(glob.glob(d + "/*.png"))]
GRON = frames_uit(OUD + "stil-film-groningen.mp4", 5.9, 7.45, "gron")
POLA = frames_uit(OUD + "stil-stop-groningen.mp4", 6.9, 8.4, "pola")

def vulling(im):   # het beeld op breedte, met een wazige, warme versie ervan als achtergrond
    bg = cover(im, W, H).filter(ImageFilter.GaussianBlur(22)); bg = ImageEnhance.Brightness(bg).enhance(.85).convert("RGBA")
    v = im.resize((W, int(im.height * W / im.width)), Image.LANCZOS).convert("RGBA")
    sch = Image.new("RGBA", (W, H), (0, 0, 0, 0)); y = (H - v.height) // 2
    ImageDraw.Draw(sch).rectangle((10, y + 14, W - 10, y + v.height + 14), fill=(40, 20, 10, 120)); bg.alpha_composite(sch.filter(ImageFilter.GaussianBlur(16)))
    bg.alpha_composite(v, (0, y)); return bg, y, v.height
def spelbeeld(u):
    return SPELF[min(len(SPELF) - 1, int(u * len(SPELF)))]
def tik(img, x, y, a):   # vinger-tik: een zachte witte stip met een kring die uitdijt
    if not (0 <= a <= 1): return
    l = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(l)
    r = 18 + 40 * a; d.ellipse((x - r, y - r, x + r, y + r), outline=(255, 255, 255, int(230 * (1 - a))), width=5)
    s = 20 * (1 - a * .4); d.ellipse((x - s, y - s, x + s, y + s), fill=(255, 255, 255, int(170 * (1 - a))))
    img.alpha_composite(l.filter(ImageFilter.GaussianBlur(1.2)))

# ---------- start- en eindkaart ----------
def kaart_met_huis(met_link):
    e = Image.new("RGBA", (W, H), CREME + (255,)); d = ImageDraw.Draw(e)
    for i in range(500): x, y = random.randrange(W), random.randrange(H); d.ellipse((x - 1, y - 1, x + 1, y + 1), fill=(232, 220, 196, 255))
    hh = 420 if not met_link else 380; klein = huis.resize((int(huis.width * hh / huis.height), hh), Image.LANCZOS)
    e.alpha_composite(klein, ((W - klein.width) // 2, 60 if not met_link else 70))
    y0 = 60 + hh + 70 if not met_link else 520
    d.text((W // 2, y0), "Family Crazy", font=SERIF(58), fill=BORDEAUX + (255,), anchor="mm")
    d.text((W // 2, y0 + 70), "Adventskalender", font=HAND(78), fill=ROOD + (255,), anchor="mm")
    d.line((W // 2 - 80, y0 + 132, W // 2 + 80, y0 + 132), fill=GOUD + (255,), width=3)
    if met_link:
        d.rounded_rectangle((W // 2 - 220, y0 + 175, W // 2 + 220, y0 + 245), 35, fill=BORDEAUX + (255,))
        d.text((W // 2, y0 + 210), "adventscalender.app", font=SERIF(32), fill=(250, 244, 232, 255), anchor="mm")
    else:
        d.text((W // 2, y0 + 175), "1 december", font=HAND(48), fill=(120, 100, 90, 255), anchor="mm")
    return e, klein.width, hh, 60
START, KB_, KH_, KY_ = kaart_met_huis(False)
ACHTERSTIP = [(random.randrange(W), random.randrange(H)) for i in range(500)]
EIND_, *_ = kaart_met_huis(True)

# ---------- frames ----------
map_ = HIER + "frames2"; shutil.rmtree(map_, ignore_errors=True); os.makedirs(map_)
dicht2 = dicht20 = None
Z2, Z20 = zw(2), zw(20); C2, C20 = midden(2), midden(20)
for f in range(N):
    t = f / FPS
    if t < T_A + .6:
        # startscherm; dan groeit het huisje zelf door tot het grote huis (geen overvloei, dus geen dubbel huis)
        a = ease(seg(t, T_A - .3, T_A + .5))
        sc = W / SW; h0, h1 = KH_, huis.height * sc
        hh_ = h0 + (h1 - h0) * a; ww_ = huis.width * hh_ / huis.height
        y_ = KY_ + (HY * sc - KY_) * a; x_ = (W - ww_) / 2
        img = Image.new("RGBA", (W, H), CREME + (255,)); dd = ImageDraw.Draw(img)
        for gx, gy in ACHTERSTIP: dd.ellipse((gx - 1, gy - 1, gx + 1, gy + 1), fill=(232, 220, 196, 255))
        tekst = START.copy(); tekst.paste(CREME + (255,), (0, 0, W, KY_ + KH_ + 10))   # alleen de tekst van de startkaart
        tekst.putalpha(tekst.split()[3].point(lambda v: int(v * (1 - seg(t, T_A - .4, T_A)))))
        img.alpha_composite(tekst)
        img.alpha_composite(huis.resize((max(2, int(ww_)), max(2, int(hh_))), Image.LANCZOS), (int(x_), int(y_)))
        if t > T_A + .4: img = Image.blend(img, huisbeeld(1, SW / 2, SH / 2)[0], seg(t, T_A + .4, T_A + .6))
        sneeuw(img, t, .6)
    elif t < T_C + .7:
        # inzoomen op raampje 2, openen, erin duiken
        if t < T_B:
            u = ease(seg(t, T_A + .6, T_B)); z = 1 + (Z2 - 1) * u ** 1.5
            cx, cy = SW / 2 + (C2[0] - SW / 2) * u, SH / 2 + (C2[1] - SH / 2) * u
        elif t < T_C: z, (cx, cy) = Z2 * (1 + .04 * seg(t, T_B, T_C)), C2
        else: z, (cx, cy) = Z2 * 1.04 * (1 + 5 * ease(seg(t, T_C, T_C + .7)) ** 2), C2
        img, box = huisbeeld(z, cx, cy)
        if t >= T_B:
            if dicht2 is None: r = in_beeld(2, box); dicht2 = img.crop((int(r[0]), int(r[1]), int(r[0] + r[2]), int(r[1] + r[3])))
            open_raam(img, 2, box, SPELF[0], ease(seg(t, T_B + .1, T_C - .1)), seg(t, T_B + .1, T_B + .7) * (1 - seg(t, T_C + .2, T_C + .7)), t, dicht2)
        if t > T_C + .35: img = Image.blend(img, vulling(SPELF[0])[0], seg(t, T_C + .35, T_C + .7))
        sneeuw(img, t, .7)
    elif t < T_K:
        # het spelletje: kleertjes aan de lijn
        u = seg(t, T_G + .2, T_K - .4); im = spelbeeld(u); img, y0, hh = vulling(im)
        for tk in SPEL["tikken"]:
            ut = tk["frame"] / len(SPELF); tt = T_G + .2 + ut * (T_K - .4 - T_G - .2)
            tik(img, tk["x"] * W, y0 + tk["y"] * hh, (t - tt + .25) / .55)
        sneeuw(img, t, .4)
    elif t < T_P + .3:
        # de wasbon: komt omhoog, tik op inwisselen, stempel
        img, _, _ = vulling(SPELF[-1]); img = Image.alpha_composite(img, Image.new("RGBA", (W, H), (30, 15, 8, int(110 * seg(t, T_K, T_K + .4)))))
        a = ease(seg(t, T_K, T_K + .6)); bon = BON2 if t >= T_K + 1.15 else BON1
        bw = int(W * .86); bh = int(bon.height * bw / bon.width)
        dreun = 1 + .07 * max(0, 1 - (t - T_K - 1.15) / .25) if t >= T_K + 1.15 else 1
        s = (.6 + .4 * a) * dreun; b2 = bon.resize((max(2, int(bw * s)), max(2, int(bh * s))), Image.LANCZOS)
        x = (W - b2.width) // 2; y = int((H - b2.height) / 2 + (1 - a) * 300)
        sch = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sch).rounded_rectangle((x + 8, y + 16, x + b2.width + 8, y + b2.height + 16), 12, fill=(20, 10, 5, int(130 * a)))
        img.alpha_composite(sch.filter(ImageFilter.GaussianBlur(14)))
        b2.putalpha(b2.split()[3].point(lambda v: int(v * min(1, a * 1.5)))); img.alpha_composite(b2, (x, y))
        tik(img, x + SPEL["tikBon"]["x"] * b2.width, y + SPEL["tikBon"]["y"] * b2.height, (t - T_K - .9) / .55)
        if t >= T_K + 1.15:
            g = 1 - seg(t, T_K + 1.15, T_K + 1.9); dd = ImageDraw.Draw(img)
            for gx, gy, gf, gs in GLINST[:14]:
                if g > 0: ster(dd, W / 2 + gx * W * .8, H / 2 + gy * 300, gs, g * max(0, math.sin(gf * 6.28 + t * 5)))
        sneeuw(img, t, .5)
        if t > T_P: img = Image.blend(img, huisbeeld(Z2 * 1.04, *C2)[0], seg(t, T_P, T_P + .3))
    elif t < T_C2 + .6:
        # terug naar buiten, door het huis naar raampje 20, openen, erin
        if t < T_B2:
            u = ease(seg(t, T_P + .3, T_B2)); zm = 1.9
            z = (Z2 * 1.04) * (1 - u) ** 2 + zm * 2 * u * (1 - u) + Z20 * u ** 2   # eerst uit, dan weer in
            cx = C2[0] + (C20[0] - C2[0]) * ease(seg(t, T_P + .5, T_B2 - .2)); cy = C2[1]
        elif t < T_C2: z, (cx, cy) = Z20 * (1 + .04 * seg(t, T_B2, T_C2)), C20
        else: z, (cx, cy) = Z20 * 1.04 * (1 + 5 * ease(seg(t, T_C2, T_C2 + .6)) ** 2), C20
        img, box = huisbeeld(z, cx, cy)
        open_raam(img, 2, box, SPELF[-1], 1, 0, t, None)   # raampje 2 blijft open
        if t >= T_B2:
            if dicht20 is None: r = in_beeld(20, box); dicht20 = img.crop((int(r[0]), int(r[1]), int(r[0] + r[2]), int(r[1] + r[3])))
            open_raam(img, 20, box, GRON[0], ease(seg(t, T_B2 + .1, T_C2 - .05)), seg(t, T_B2 + .1, T_B2 + .6) * (1 - seg(t, T_C2 + .1, T_C2 + .6)), t, dicht20)
        if t > T_C2 + .3: img = Image.blend(img, cover(GRON[0], W, H).convert("RGBA"), seg(t, T_C2 + .3, T_C2 + .6))
        sneeuw(img, t, .7)
    elif t < T_PO:
        u = seg(t, T_GR, T_PO); fr = GRON[min(len(GRON) - 1, int(u * len(GRON)))]
        img = kenburns(fr, u, 1.0, 1.08).convert("RGBA"); twinkel(img, t); sneeuw(img, t)
    elif t < T_E:
        u = seg(t, T_PO, T_E); fr = POLA[min(len(POLA) - 1, int(u * len(POLA)))]
        img = cover(fr, W, H).convert("RGBA")
        if t < T_PO + .3: img = Image.blend(kenburns(GRON[-1], 1, 1.0, 1.08).convert("RGBA"), img, seg(t, T_PO, T_PO + .3))
        sneeuw(img, t, .6)
    else:
        a = ease(seg(t, T_E, T_E + .6))
        img = Image.blend(cover(POLA[-1], W, H).convert("RGBA"), EIND_, a) if a < 1 else EIND_.copy()
        sneeuw(img, t, .5)
    out = img.convert("RGB")
    if f > N - 12: out = Image.blend(Image.new("RGB", (W, H), (20, 10, 6)), out, (N - f) / 12)
    out.save(f"{map_}/{f:04d}.jpg", quality=92)
    if f % 48 == 0: print("frame", f, round(t, 1), flush=True)

exec(open(OUD + "muziek.py").read().split("KEUZE = {")[0])
wav = HIER + "teaser2.wav"; schrijf(wav, maak("jingle", DUUR, 140, 1, False, True))
uit = HIER + "Family Crazy Adventskalender - teaser 2.mp4"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{map_}/%04d.jpg", "-i", wav, "-map", "0:v", "-map", "1:a",
                "-c:v", "libx264", "-crf", "21", "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", uit], check=True)
print("klaar", uit, os.path.getsize(uit) // 1024, "kB")
