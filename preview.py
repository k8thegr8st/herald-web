"""
Náhled příspěvků do soukromé zprávy (DM) 2 hodiny před zveřejněním.

Týdenní plakát (neděle 15:00) a měsíční program (poslední den v měsíci 15:05) přijdou
jako soukromá zpráva člověku z control_config.json → "preview_user_id".
Reakce ❌ pod náhledem = v 17:00 se nezveřejní nic (Facebook, Instagram, Story, souhrn na Discordu).
Bez reakce se zveřejní normálně. Když preview_user_id není vyplněné, náhledy se neposílají.
"""
import json
import os
from urllib.parse import quote

import requests

API = "https://discord.com/api/v10"
HERE = os.path.dirname(os.path.abspath(__file__))
NO = "❌"
STATE = os.path.join(HERE, "weekly_sent.json")


def _headers():
    return {"Authorization": f"Bot {os.environ.get('DISCORD_BOT_TOKEN', '')}"}


def user_id():
    try:
        with open(os.path.join(HERE, "control_config.json"), encoding="utf-8") as f:
            return json.load(f).get("preview_user_id", "")
    except (FileNotFoundError, ValueError):
        return ""


def _state():
    try:
        with open(STATE, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, ValueError):
        return {}


def _save(key, value):
    s = _state()
    s[key] = value
    with open(STATE, "w", encoding="utf-8") as f:
        json.dump(s, f, indent=2, ensure_ascii=False)


def _dm_channel(uid=None):
    r = requests.post(f"{API}/users/@me/channels", headers=_headers(), json={"recipient_id": uid or user_id()}, timeout=20)
    r.raise_for_status()
    return r.json()["id"]


# barva karty podle služby (první shoda v nadpisu vyhrává); varování a úspěch mají přednost
SERVICES = [
    (("⚠️", "🚫", "chyba", "nepodařilo"), "#ED4245", "Upozornění"),
    (("nová objednávka", "nové objednávky"), "#57F287", "E-shop"),
    (("marž", "💸"), "#FFC83D", "Hlídání marže"),
    (("vyprodan", "🙈"), "#7189AC", "Vyprodané produkty"),
    (("naskladn", "kontrola e-shopu"), "#FF9A3D", "E-shop"),
    (("puls",), "#009AF9", "Puls e-shopu"),
    (("asmodee", "objednávka", "📦", "🛒", "🆕", "📷"), "#F28C28", "Asmodee"),
    (("na disku", "disk"), "#FBBC04", "Google Disk"),
    (("štítk", "kategori", "🏷️"), "#3DFFB5", "Štítky a kategorie"),
    (("banner", "slider", "🖼️"), "#C81EF9", "Bannery"),
    (("facebook", "instagram", "video", "reel", "týden", "měsíc", "🎬", "📘", "📸"), "#1877F2", "Sociální sítě"),
    (("newsletter", "📰"), "#9D4DFF", "Newsletter"),
    (("kontrola", "článk", "milník", "🔎", "👀"), "#8C86A8", "Kontrola"),
    (("✅", "zapnut", "hotovo"), "#57F287", "Hotovo"),
]
DEFAULT_COLOR = "#9B17C4"                              # firemní fialová


def _style(title):
    t = title.lower()
    for keys, color, name in SERVICES:
        if any(k in t for k in keys):
            return int(color.lstrip("#"), 16), name
    return int(DEFAULT_COLOR.lstrip("#"), 16), "Herald"


def _embed(text):
    """Text zprávy → karta: první řádek = nadpis, zbytek = obsah, barva podle služby."""
    first, _, rest = text.partition("\n")
    title = first.replace("**", "").strip()
    color, name = _style(first)
    if len(title) > 250:                               # dlouhý první řádek: celé do obsahu
        title, rest = "", text
    emb = {"color": color, "description": rest.strip()[:4000], "footer": {"text": f"Herald · {name}"}}
    if title:
        emb["title"] = title[:256]
    if not emb["description"]:
        emb.pop("description")
    return emb


def dm(text, files=(), uid=None):
    """Pošle soukromou zprávu jako barevnou kartu (embed), obrázky po 10 na zprávu. Vrací (kanál, id první zprávy).
    uid = komu (jinak preview_user_id)."""
    from nodash import clean
    text = clean(text)
    ch = _dm_channel(uid)
    first = None
    files = list(files) or [None]
    for k in range(0, len(files), 10):
        part = [f for f in files[k:k + 10] if f]
        payload = {"content": "", "allowed_mentions": {"parse": []}}
        if k == 0:
            emb = _embed(text)
            imgs = [p for p in part if os.path.splitext(p)[1].lower() in (".png", ".jpg", ".jpeg", ".webp")]
            if len(imgs) == 1:                          # jeden obrázek rovnou do karty
                emb["image"] = {"url": f"attachment://{os.path.basename(imgs[0])}"}
            payload["embeds"] = [emb]
        handles = [open(p, "rb") for p in part]
        try:
            r = requests.post(f"{API}/channels/{ch}/messages", headers=_headers(),
                              data={"payload_json": json.dumps(payload)},
                              files={f"files[{i}]": (os.path.basename(p), h, {".mp4": "video/mp4", ".html": "text/html", ".txt": "text/plain", ".webp": "image/webp", ".jpg": "image/jpeg", ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", ".csv": "text/csv"}
                                                          .get(os.path.splitext(p)[1].lower(), "image/png"))
                                     for i, (p, h) in enumerate(zip(part, handles))},
                              timeout=60)
        finally:
            for h in handles:
                h.close()
        r.raise_for_status()
        first = first or r.json()["id"]
    return ch, first


def send(kind, for_date, text, files):
    """Pošle náhled a zapamatuje si ho. kind = 'weekly' / 'monthly', for_date = týden/měsíc (iso)."""
    if not user_id():
        print("Náhledy nejsou zapnuté (chybí preview_user_id), nic neposílám.")
        return
    if os.environ.get("PREVIEW_TEST"):
        # zkušební náhled: jen ukázka, nic se neukládá a reakce na něj nic neovlivní
        dm("🧪 **TEST náhledu** - jen ukázka, jak náhled vypadá. Reakce na tuhle zprávu nic neovlivní.\n\n" + text, files)
        print("Zkušební náhled odeslán do soukromé zprávy.")
        return
    ch, msg = dm(text + f"\n\nReaguj {NO} pod touto zprávou = **nezveřejňovat**. Bez reakce se zveřejní normálně.", files)
    requests.put(f"{API}/channels/{ch}/messages/{msg}/reactions/{quote(NO)}/@me", headers=_headers(), timeout=20)
    from datetime import datetime, timezone
    _save(f"preview_{kind}", {"for": for_date, "ch": ch, "msg": msg, "done": False,
                              "t": datetime.now(timezone.utc).isoformat(timespec="seconds")})
    print(f"Náhled ({kind}) odeslán do soukromé zprávy.")


def cancelled(kind, for_date):
    """True, pokud je pod náhledem pro tento týden/měsíc ❌ od člověka. Zruší jen jednou a potvrdí to."""
    p = _state().get(f"preview_{kind}")
    if not p or p.get("for") != for_date or not user_id():
        return False
    if p.get("done") == "cancelled":
        return True
    try:
        r = requests.get(f"{API}/channels/{p['ch']}/messages/{p['msg']}/reactions/{quote(NO)}", headers=_headers(), timeout=20)
        if not r.ok:
            return False
        if any(not u.get("bot") for u in r.json()):
            _save(f"preview_{kind}", {**p, "done": "cancelled"})
            what = {"weekly": "Týdenní příspěvek je zrušený", "monthly": "Měsíční program je zrušený",
                    "reel": "Týdenní video je zrušené"}.get(kind, "Příspěvek je zrušený")
            dm(f"🚫 {what} - na Facebook, Instagram ani Discord nic nevyšlo.")
            return True
    except Exception as e:
        print(f"! Náhled se nepodařilo zkontrolovat ({e}), pokračuji normálně.")
    return False


def ready(kind, for_date, min_minutes=60):
    """Smí se zveřejnit? Jen když byl náhled pro tento týden/měsíc odeslán aspoň před min_minutes.
    Když náhledy nejsou zapnuté (bez preview_user_id), platí jen ostatní pojistky."""
    if not user_id():
        return True, ""
    from datetime import datetime, timezone, timedelta
    p = _state().get(f"preview_{kind}")
    if not p or p.get("for") != for_date or not p.get("t"):
        return False, "náhled pro toto období nebyl odeslán"
    age = datetime.now(timezone.utc) - datetime.fromisoformat(p["t"])
    if age < timedelta(minutes=min_minutes):
        return False, f"náhled byl odeslán teprve před {int(age.total_seconds() // 60)} min"
    return True, ""


def in_window(now, weekday, frm, to):
    """Je teď správný den (0=po … 6=ne, None = libovolný) a čas mezi frm a to (HH:MM)?"""
    return (weekday is None or now.weekday() == weekday) and frm <= f"{now:%H:%M}" < to
