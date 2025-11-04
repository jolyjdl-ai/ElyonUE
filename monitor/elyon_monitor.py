# -*- coding: utf-8 -*-
"""
Moniteur console (type mainframe) pour ElyonEU
- Affiche /self et les derniers /events
- Commandes clavier :
    Q : Quitter
    P : Pause heartbeat
    R : Resume heartbeat
    + : Intervalle +1s
    - : Intervalle -1s (min 1s)
    U : Rafraîchir (Update)
- Dépendances : uniquement stdlib (urllib, json, time, os, msvcrt, shutil)
"""
import os, sys, time, json, urllib.request, urllib.error, shutil, msvcrt

API = os.environ.get("ELYON_API_URL", "http://127.0.0.1:8000")

def _get(path):
    try:
        with urllib.request.urlopen(API + path, timeout=2.5) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception:
        return None

def _post(path, payload):
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(API + path, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=2.5) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception:
        return None

def clear():
    os.system("cls")

def draw_box(title, body_lines, width):
    bar = "═" * (width - 2)
    print("╔" + bar + "╗")
    title_line = f" {title} "
    print("║" + title_line.ljust(width - 2) + "║")
    print("╟" + ("─" * (width - 2)) + "╢")
    for ln in body_lines:
        print("║" + ln.ljust(width - 2) + "║")
    print("╚" + bar + "╝")

def format_self(s):
    out = []
    if not s:
        return ["(indisponible)"]
    ident = s.get("identity", {})
    out.append(f"Name : {ident.get('name', '?')}")
    out.append(f"Ver. : {ident.get('version', '?')}")
    gov = s.get("governance", "?")
    modes = ", ".join(s.get("modes", [])) or "(modes non définis)"
    out.append(f"Gouvernance : {gov}")
    out.append(f"Modes : {modes}")
    return out

def format_events(evs, max_lines):
    lines = []
    if not evs or "events" not in evs:
        return ["(aucun événement)"]
    for e in evs["events"][-max_lines:][::-1]:
        ts = e.get("ts","")
        typ = e.get("type","")
        data = e.get("data",{})
        d = (json.dumps(data, ensure_ascii=False) if data else "")
        ln = f"{ts}  {typ:<8} {d}"
        if len(ln) > 120:
            ln = ln[:117] + "..."
        lines.append(ln)
    if not lines:
        lines = ["(aucun événement)"]
    return lines

def show_help(width):
    lines = [
        "Commandes :  Q=Quit  P=Pause  R=Resume  +=+1s  -=-1s  U=Update",
        f"API: {API}",
    ]
    draw_box("Aide / Raccourcis", lines, width)

def show_status(width):
    ctl = _get("/control") or {}
    st  = f"Pings: {'ON' if ctl.get('run_pings') else 'OFF'} • interval={ctl.get('interval_sec','?')}s"
    draw_box("Statut Heartbeat", [st], width)

def adjust_interval(delta):
    ctl = _get("/control") or {}
    iv = int(ctl.get("interval_sec", 1) or 1)
    iv = max(1, min(3600, iv + delta))
    _post("/control", {"interval_sec": iv})

def main():
    cols = shutil.get_terminal_size((120, 30)).columns
    width = max(80, cols)
    last_draw = 0
    refresh_every = 1.0  # secondes

    while True:
        now = time.time()
        if now - last_draw >= refresh_every:
            s = _get("/self")
            e = _get("/events")
            clear()
            draw_box("ÉlyonEU — Moniteur (Console)", [], width)
            show_status(width)
            draw_box("Identité", format_self(s), width)
            draw_box("Derniers événements", format_events(e, max_lines=20), width)
            show_help(width)
            print("⟶ Tape une commande (Q/P/R/+/-/U) ...")
            last_draw = now

        if msvcrt.kbhit():
            ch = msvcrt.getch()
            if not ch:
                continue
            c = ch.decode("utf-8", errors="ignore").upper()
            if c == "Q":
                clear(); print("Fermeture du moniteur..."); break
            elif c == "P":
                _post("/control", {"run_pings": False})
            elif c == "R":
                _post("/control", {"run_pings": True})
            elif c == "+":
                adjust_interval(+1)
            elif c == "-":
                adjust_interval(-1)
            elif c == "U":
                last_draw = 0  # force redraw
        time.sleep(0.05)

if __name__ == "__main__":
    main()
