"""Zeven extra sfeerfilmpjes uit de kamertjes, met startbeeld en speeldoosmuziek."""
import sys, os, subprocess, shutil
SP = "/tmp/claude-0/-home-user-stijlstudio/f55e38bf-cb55-5076-bedb-49f8c8e8917c/scratchpad/"
exec(open(SP + "film10.py").read().split("FILMS = {")[0])

NIEUW = {
  "sneeuwpret": ([(K("sneeuwtuin"), 3.4, 1.0, 1.18, 0, .2), (K("lantaarnbankje"), 3.2, 1.15, 1.0, .3, 0), (K("bankje"), 3.2, 1.0, 1.15, -.3, 0), (K("dorp"), 3.4, 1.1, 1.0, 0, .2)],
                 [("Sneeuw-pret", "buiten is het koud", .6, 3.8, 380), ("Binnen is het beter.", None, 7.2, 10.5, 230)], True),
  "kerstdorp": ([(K("dorp"), 3.4, 1.0, 1.18, 0, 0), (K("huisje"), 3.2, 1.15, 1.0, .3, 0), (K("rodedeur"), 3.2, 1.0, 1.15, -.3, .2), (K("lantaarntje"), 3.4, 1.1, 1.0, 0, 0)],
                [("Kerst-dorp", "iedereen kent iedereen", .6, 3.8, 380), ("Helaas.", None, 7.2, 10.5, 230)], True),
  "haardcore": ([(K("kachelhoek"), 3.4, 1.0, 1.18, 0, .2), (K("kachelkamer"), 3.2, 1.15, 1.0, .3, 0), (K("houtkamer"), 3.2, 1.0, 1.15, -.3, 0), (K("stoeltjes"), 3.4, 1.1, 1.0, 0, .2)],
                [("Haard-core", "warm worden", .6, 3.8, 380), ("Sokken uit. Of niet.", None, 7.2, 10.5, 230)], False),
  "pakket": ([(K("inpakken"), 3.4, 1.0, 1.18, 0, 0), (K("roodpapier"), 3.2, 1.15, 1.0, .3, 0), (K("cadeauzakjes"), 3.2, 1.0, 1.15, -.3, 0), (K("cadeaus"), 3.4, 1.1, 1.0, 0, .2)],
             [("Pak-ket", "alles moet ingepakt", .6, 3.8, 380), ("Ook wat je niet wilt geven.", None, 7.2, 10.5, 230)], False),
  "slaapzacht": ([(K("bedje"), 3.4, 1.0, 1.18, 0, 0), (K("trapje"), 3.2, 1.15, 1.0, .3, 0), (K("belletje"), 3.2, 1.0, 1.15, -.3, 0), (K("kerstkamer"), 3.4, 1.1, 1.0, 0, .2)],
                 [("Slaap-zacht", "nog even", .6, 3.8, 380), ("Wie het eerst wakker is, wint.", None, 7.2, 10.5, 230)], True),
  "elfie": ([(K("elfendeur"), 3.4, 1.0, 1.2, 0, 0), (K("kastjeskamer"), 3.2, 1.15, 1.0, .3, 0), (K("meelvloer"), 3.2, 1.0, 1.15, -.3, 0), (K("picknick"), 3.4, 1.1, 1.0, 0, .2)],
            [("Elf-ie", "wie woont hier?", .6, 3.8, 380), ("Ze zien alles.", None, 7.2, 10.5, 230)], False),
  "lichtzinnig": ([(K("lantaarntje"), 3.4, 1.0, 1.18, 0, 0), (K("lantaarnbankje"), 3.2, 1.15, 1.0, .3, 0), (K("belletje"), 3.2, 1.0, 1.15, -.3, 0), (K("sneeuwtuin"), 3.4, 1.1, 1.0, 0, .2)],
                  [("Licht-zinnig", "avondwandeling", .6, 3.8, 380), ("Jas aan. Geen discussie.", None, 7.2, 10.5, 230)], True),
}
MUZIEK = {"sneeuwpret": ("jingle", 140, 1, False, True), "kerstdorp": ("wewish", 120, 0, False, True), "haardcore": ("stille", 92, 0, False, False),
          "pakket": ("deck", 128, 0, False, False), "slaapzacht": ("stille", 84, 1, False, False), "elfie": ("godrest", 126, 1, False, True), "lichtzinnig": ("tannenbaum", 100, 0, False, True)}

wil = sys.argv[1:] or list(NIEUW)
for naam in wil:
    shots, titels, sneeuw_ = NIEUW[naam]
    maak("film-" + naam, shots, [(label(t, s), a, b, y) for t, s, a, b, y in titels], met_sneeuw=sneeuw_, bokeh_aan=True)

# afwerken: startbeeld erin, muziek eronder (zelfde als de andere 26)
src = open(SP + "afwerk.py").read().split("doorsturen = ")[0].replace('f"Family Crazy Adventskalender · dag {dag}"', 'f"Family Crazy Adventskalender · {dag}"')
exec(src); maak_muziek = maak
for naam in wil:
    titel = NIEUW[naam][1][0][0]; n = "film-" + naam
    KEUZE[n] = MUZIEK[naam]
    stil = SP + "stil-" + n + ".mp4"; shutil.copy(FILMS + n + ".mp4", stil)
    png = startbeeld(n, titel, "sfeer", stil)
    tmp = SP + "tmp-" + n + ".mp4"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-loop", "1", "-framerate", "24", "-t", "2.5", "-i", png, "-i", stil, "-filter_complex",
                    "[0:v]format=yuv420p,setsar=1[a];[1:v]fps=24,format=yuv420p,setsar=1[b];[a][b]xfade=transition=fade:duration=0.5:offset=2.0[v]",
                    "-map", "[v]", "-c:v", "libx264", "-crf", "25", "-preset", "slow", "-pix_fmt", "yuv420p", tmp], check=True)
    sec = duur(tmp); l, tempo, oc, mi, be = KEUZE[n]
    wav = SP + n + ".wav"; schrijf(wav, maak_muziek(l, sec, tempo, oc, mi, be))
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", tmp, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "96k",
                    "-shortest", "-movflags", "+faststart", FILMS + n + ".mp4"], check=True)
    os.remove(tmp)
    os.makedirs(SP + "doorsturen", exist_ok=True)
    shutil.copy(FILMS + n + ".mp4", f"{SP}doorsturen/Sfeer - {titel}.mp4")
    print("klaar", n, round(sec, 1), "s")
