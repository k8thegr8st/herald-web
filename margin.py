#!/usr/bin/env python3
"""
Herald - hlídání marže. Jednou denně projde aktivní produkty v Upgates a porovná prodejní cenu s nákupní.

Hlásí (margin_config.json):
  • 🔴 produkty prodávané pod nákupní cenou
  • 🟠 produkty s marží pod `min_pct` % (10)
  • ⚪ počet aktivních produktů bez nákupní ceny (seznam jen v CSV, ať zpráva nezahltí)
Obě ceny bere s DPH (v Upgates je nákupka vedená s DPH, stejně jako u objednávek).
Marže = (prodej - nákup) / prodej. Věrnostní sleva zákazníka (2 až 6 %) se nepočítá, skutečná marže může být nižší.

Kam: kontrolní kanál, s označením lidí z `mention_ids` (a `mention_names`, které Herald dohledá na serveru).
Kdy: hlásí jen nové problémy (produkt, jehož ceny se od posledního hlášení nezměnily, se znovu nehlásí).
Každé pondělí připomene všechny otevřené. ✅ pod zprávou = „je to schválně“: ty produkty už nehlásí,
dokud se jim nezmění cena nebo nákupka.

Úplně první běh nic do kanálu neposílá: pošle Kate do PM přehled s CSV a ✅ pod ním hlídání zapne.
Ruční spuštění: úloha `marze` (s --force projde znovu, i když dnes už proběhlo; --diag vypíše do logu
strukturu cen prvních produktů pro kontrolu). Stav: margin_state.json.
"""
import csv
import json
import os
import sys
from datetime import date, datetime
from urllib.parse import quote

import requests

from upgates_api import Upgates, UpgatesError

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "margin_state.json")
DRY_RUN = os.environ.get("DRY_RUN", "").lower() in ("1", "true", "yes")
FORCE = "--force" in sys.argv
DIAG = "--diag" in sys.argv
with open(os.path.join(HERE, "margin_config.json"), encoding="utf-8") as f:
    CFG = json.load(f)
OK = "✅"
TODAY = date.today()


def _state():
    try:
        with open(STATE, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, ValueError):
        return {}


def _save(st):
    if not DRY_RUN:
        with open(STATE, "w", encoding="utf-8") as f:
            json.dump(st, f, ensure_ascii=False, indent=0)


def _yes(v):
    return v is True or str(v).lower() in ("1", "true", "yes")


def _num(v):
    try:
        x = float(str(v).replace(",", ".").replace(" ", ""))
        return x if x > 0 else None
    except (TypeError, ValueError):
        return None


def _title(p):
    for d in p.get("descriptions") or []:
        if d.get("language") in (None, "cs") and d.get("title"):
            return d["title"]
    return ""


def _url(p):
    for d in p.get("descriptions") or []:
        if d.get("language") in (None, "cs") and d.get("url"):
            return d["url"]
    return ""


def kc(x):
    return f"{x:,.0f} Kč".replace(",", " ")


def prices(obj):
    """(prodej, nákup) s DPH z pole `prices` produktu nebo varianty. Prodej = konečná cena (akční, je-li)."""
    for pr in obj.get("prices") or []:
        if pr.get("language") not in (None, "cs"):
            continue
        buy = _num(pr.get("price_purchase"))
        sale = None
        for pl in pr.get("pricelists") or []:
            sale = (_num(pl.get("price_with_vat")) or _num(pl.get("price_sale"))
                    or _num(pl.get("price_original")))
            if sale:
                break
        return sale, buy
    return None, None


def excluded(title):
    t = title.lower()
    return any(w.lower() in t for w in CFG.get("exclude") or [])


def budget_ok(u, need):
    if u.count + need > u.max_requests:
        return False
    left = u.limits.get("X-Rate-Limit-Hour-Remaining")
    return left is None or int(left) >= need + CFG.get("reserve_requests", 6)


def scan(u, st):
    """Všechny aktivní produkty i s variantami. Pokračuje po stránkách, když dojde limit API. True = hotovo."""
    sc = st.setdefault("scan", {})
    page, buf = sc.get("page", 1), sc.setdefault("buf", {})
    diag = 0
    while True:
        if not budget_ok(u, 2):
            sc["page"] = page
            print(f"Limit API: čtení produktů pokračuje příště od stránky {page}.")
            return False
        res = u.get("/products", {"active_yn": "true", "current_page_items": 100, "page": page})
        for p in res.get("products") or []:
            code = p.get("code")
            title = _title(p)
            if not code or excluded(title):
                continue
            items = [(code, title, p)] + [(v.get("code") or f"{code}-{i}", f"{title} ({v.get('code') or i})", v)
                                         for i, v in enumerate(p.get("variants") or [])]
            for c, t, obj in items:
                if DIAG and diag < 3 and obj.get("prices"):
                    print(f"[diag] {c}: prices = {json.dumps(obj.get('prices'), ensure_ascii=False)[:800]}")
                    diag += 1
                sale, buy = prices(obj)
                if not sale:                          # bez ceny (např. hlavní produkt s variantami): nehodnotit
                    continue
                buf[c] = {"t": t[:90], "s": sale, "b": buy, "u": _url(p)}
        if page >= int(res.get("number_of_pages") or 1):
            break
        page += 1
    st["products"] = buf
    sc.clear()
    return True


def evaluate(prods):
    lim = CFG.get("min_pct", 10)
    loss, low, missing = [], [], []
    for c, d in prods.items():
        s, b = d["s"], d.get("b")
        if not b:
            missing.append(c)
            continue
        pct = (s - b) / s * 100
        if s < b:
            loss.append((c, pct))
        elif pct < lim:
            low.append((c, pct))
    loss.sort(key=lambda x: x[1])
    low.sort(key=lambda x: x[1])
    return loss, low, missing


def sig(d):
    return f"{d['s']:.2f}|{(d.get('b') or 0):.2f}"


def line(c, d, pct):
    name = f"[{d['t']}]({d['u']})" if d.get("u", "").startswith("http") else d["t"]
    diff = d["s"] - d["b"]
    return f"• {name}: prodej {kc(d['s'])}, nákup {kc(d['b'])} ({'+' if diff >= 0 else '-'}{kc(abs(diff))}, {pct:.0f} %)"


def csv_file(prods, loss, low, missing, name):
    path = os.path.join(HERE, name)
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Stav", "Kód", "Název", "Prodej s DPH", "Nákup s DPH", "Marže %"])
        for label, rows in (("pod nákupkou", loss), (f"marže pod {CFG.get('min_pct', 10)} %", low)):
            for c, pct in rows:
                d = prods[c]
                w.writerow([label, c, d["t"], f"{d['s']:.0f}", f"{d['b']:.0f}", f"{pct:.1f}"])
        for c in missing:
            d = prods[c]
            w.writerow(["chybí nákupka", c, d["t"], f"{d['s']:.0f}", "", ""])
    return path


def message(title, prods, loss, low, missing_n, intro=""):
    lim, n = CFG.get("min_pct", 10), CFG.get("list_limit", 15)
    out = [title]
    if intro:
        out += [intro, ""]
    if loss:
        out.append(f"🔴 **Pod nákupní cenou: {len(loss)}**")
        out += [line(c, prods[c], p) for c, p in loss[:n]]
        if len(loss) > n:
            out.append(f"… a dalších {len(loss) - n} v příloze")
        out.append("")
    if low:
        out.append(f"🟠 **Marže pod {lim} %: {len(low)}**")
        out += [line(c, prods[c], p) for c, p in low[:n]]
        if len(low) > n:
            out.append(f"… a dalších {len(low) - n} v příloze")
        out.append("")
    if missing_n:
        out += [f"⚪ **Bez nákupní ceny: {missing_n}** (seznam v příloze), u nich marži hlídat nejde.", ""]
    out.append(f"👉 Uprav cenu v Upgates, nebo dej {OK} pod zprávu, pokud je to schválně (akce, lákadlo). "
               "Produkty pod touhle zprávou pak Herald přestane hlásit, dokud se jim nezmění cena.")
    return "\n".join(out)


# ---------- Discord ----------

def resolve_mentions():
    """ID lidí k označení: mention_ids + dohledání podle jména na serveru (mention_names)."""
    import hrana_bot as hb
    ids = [str(i) for i in CFG.get("mention_ids") or []]
    missing = []
    for name in CFG.get("mention_names") or []:
        try:
            res = hb.api("GET", f"/guilds/{hb.GUILD_ID}/members/search", params={"query": name, "limit": 10})
        except Exception as e:                        # noqa: BLE001 - jen zjištění, nesmí shodit běh
            print(f"! Hledání „{name}“ na serveru selhalo: {e}")
            missing.append(name)
            continue
        hits = [m for m in res or [] if not (m.get("user") or {}).get("bot")]
        exact = [m for m in hits if name.lower() in {str(m.get("nick") or "").lower(),
                                                     str(m["user"].get("username") or "").lower(),
                                                     str(m["user"].get("global_name") or "").lower()}]
        pick = exact or hits
        if len(pick) == 1:
            ids.append(pick[0]["user"]["id"])
            print(f"Označím „{name}“ = {pick[0]['user'].get('username')}")
        else:
            print(f"! „{name}“: na serveru {'nenalezen' if not pick else 'víc shod'} ({len(pick)})")
            missing.append(name)
    return sorted(set(ids)), missing


def channel_id():
    with open(os.path.join(HERE, "control_config.json"), encoding="utf-8") as f:
        return json.load(f)["channel_id"]


def post_channel(text, files, ids):
    import preview
    from nodash import clean
    CH = channel_id()
    tags = " ".join(f"<@{i}>" for i in ids)
    payload = {"content": tags, "allowed_mentions": {"parse": [], "users": ids},
               "embeds": [preview._embed(clean(text))]}
    if DRY_RUN:
        print(f"[DRY RUN] do kanálu {CH}: {tags}\n{text}")
        return CH, "dry-run"
    handles = [open(p, "rb") for p in files]
    try:
        r = requests.post(f"{preview.API}/channels/{CH}/messages", headers=preview._headers(),
                          data={"payload_json": json.dumps(payload)},
                          files={f"files[{i}]": (os.path.basename(p), h, "text/csv")
                                 for i, (p, h) in enumerate(zip(files, handles))}, timeout=60)
    finally:
        for h in handles:
            h.close()
    r.raise_for_status()
    msg = r.json()["id"]
    requests.put(f"{preview.API}/channels/{CH}/messages/{msg}/reactions/{quote(OK)}/@me",
                 headers=preview._headers(), timeout=20)
    return CH, msg


def reacted(ref):
    import preview
    if not ref or ref.get("msg") == "dry-run":
        return False
    try:
        r = requests.get(f"{preview.API}/channels/{ref['ch']}/messages/{ref['msg']}/reactions/{quote(OK)}",
                         headers=preview._headers(), timeout=20)
        return r.ok and any(not x.get("bot") for x in r.json())
    except requests.RequestException:
        return False


# ---------- běh ----------

def main():
    import preview
    st = _state()
    if not FORCE and st.get("day") == TODAY.isoformat():
        return
    if not FORCE and datetime.now().hour < CFG.get("from_hour", 12):
        return

    # 1) ✅ pod minulými zprávami: zapnutí hlídání / „schválně“ u nahlášených produktů
    if st.get("ask") and not st.get("on") and reacted(st["ask"]):
        st["on"] = True
        print("Hlídání marže zapnuto (✅ v PM).")
    for rep in st.get("reports", []):
        if not rep.get("acked") and reacted(rep):
            rep["acked"] = True
            for c, s in rep.get("items", {}).items():
                st.setdefault("ok", {})[c] = s       # schválně: nehlásit, dokud se nezmění ceny
    st["reports"] = [r for r in st.get("reports", []) if not r.get("acked")][-10:]

    global DIAG
    DIAG = DIAG or not st.get("on")                   # dokud není zapnuto: struktura cen do logu pro kontrolu
    u = Upgates(max_requests=CFG.get("max_requests", 60))
    try:
        done = scan(u, st)
    except UpgatesError as e:
        print(f"! Upgates: {e}")
        done = False
    if not done:
        _save(st)
        return
    prods = st.pop("products")
    loss, low, missing = evaluate(prods)
    print(f"Produktů s cenou: {len(prods)}, pod nákupkou: {len(loss)}, marže pod {CFG.get('min_pct', 10)} %: "
          f"{len(low)}, bez nákupky: {len(missing)}")
    st["day"] = TODAY.isoformat()

    # 2) první běh: náhled do PM, nic do kanálu
    if not st.get("on"):
        if not st.get("ask") or FORCE:
            path = csv_file(prods, loss, low, missing, "marze-nahled.csv")
            text = message("💸 **Hlídání marže: náhled** (zatím nic neposílá do kanálu)", prods, loss, low,
                           len(missing), intro=f"Prošel jsem {len(prods)} aktivních produktů a variant s cenou. "
                           f"Tohle by teď hlásil.")
            text = text.rsplit("\n👉", 1)[0] + (f"\n👉 Zkontroluj pár čísel proti Upgates. Sedí-li, dej {OK} "
                                                "pod tuhle zprávu a hlídání se zapne (do kontrolního kanálu, "
                                                "s označením).")
            if not DRY_RUN:
                ch, msg = preview.dm(text[:3900], [path])
                requests.put(f"{preview.API}/channels/{ch}/messages/{msg}/reactions/{quote(OK)}/@me",
                             headers=preview._headers(), timeout=20)
                st["ask"] = {"ch": ch, "msg": msg}
            else:
                print(text)
        _save(st)
        return

    # 3) ostré hlášení: nové problémy každý den, v pondělí všechny otevřené
    okd, seen = st.setdefault("ok", {}), st.setdefault("seen", {})
    for c in list(okd):
        if c in prods and okd[c] != sig(prods[c]):
            okd.pop(c)                                # cena se změnila: schválení už neplatí
    monday = TODAY.weekday() == 0
    open_loss = [(c, p) for c, p in loss if c not in okd]
    open_low = [(c, p) for c, p in low if c not in okd]
    if monday:
        rep_loss, rep_low = open_loss, open_low
    else:
        rep_loss = [(c, p) for c, p in open_loss if seen.get(c) != sig(prods[c])]
        rep_low = [(c, p) for c, p in open_low if seen.get(c) != sig(prods[c])]
    for c, _ in open_loss + open_low:
        seen[c] = sig(prods[c])
    for c in list(seen):
        if c not in dict(open_loss + open_low):
            seen.pop(c)                               # vyřešené: příště se zase hlásí jako nové
    if not rep_loss and not rep_low:
        print("Nic nového k hlášení.")
        _save(st)
        return
    n = len(rep_loss) + len(rep_low)
    title = (f"💸 **Hlídání marže: {n} {'produkt' if n == 1 else 'produkty' if n < 5 else 'produktů'}"
             f"{' (pondělní přehled)' if monday else ''}**")
    path = csv_file(prods, rep_loss, rep_low, missing if monday else [], "marze.csv")
    ids, not_found = resolve_mentions()
    ch, msg = post_channel(message(title, prods, rep_loss, rep_low, len(missing) if monday else 0)[:3900],
                           [path], ids)
    st.setdefault("reports", []).append({"ch": ch, "msg": msg,
                                         "items": {c: sig(prods[c]) for c, _ in rep_loss + rep_low}})
    if not_found and not DRY_RUN and st.get("warned") != TODAY.isoformat():
        preview.dm("⚠️ **Hlídání marže: nevím, koho označit**\n"
                   f"Na serveru jsem nenašel: {', '.join(not_found)}. Zpráva odešla do kontrolního kanálu "
                   "bez označení.\n👉 Napiš Claude, kdo to je, doplní jeho Discord ID.")
        st["warned"] = TODAY.isoformat()
    _save(st)


if __name__ == "__main__":
    main()
