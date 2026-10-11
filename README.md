# 📯 Herald - manuál

Herald je bot Hrana Store. Sám bere turnaje z kalendáře ligy a novinky z e-shopu a zveřejňuje je na **Discordu, Facebooku a Instagramu**. Běží zdarma na GitHubu, nic se neinstaluje a váš počítač může být vypnutý.

---

## Co a kdy Herald dělá

| Kdy | Co | Kam |
|---|---|---|
| každé 3 hodiny | Synchronizuje kalendář s Discord událostmi (nové založí, změněné upraví, smazané smaže) | Discord - Události |
| denně 10:00 | „Dnes se hraje na Hraně!“ s kartou události a pingem role | Discord - kanál #události dané hry |
| denně 14:00 | Novinky z e-shopu (1 novinka = velká karta, víc = seznam) | Discord - kanál novinek dané hry |
| denně 14:00 | Nové příslušenství bez přiřazené hry (obaly, alba, krabičky…), seskupené podle výrobce | Discord - #eshop-novinky |
| denně 14:00 | Předobjednávky zvlášť („🕐 Nová předobjednávka“) a „✅ Právě naskladněno“, když se předobjednávka nebo vyprodané zboží objeví skladem | Discord - kanál novinek dané hry / #eshop-novinky |
| denně 18:00 | Hlídá změny v měsíčním programu a píše komentář pod příspěvek | Facebook + Instagram |
| denně 9:05 | Kontrolní kanál: chybějící výsledky lig, nesoulad kalendáře a tabulek, 20. a 27. den připomínka doplnit kalendář; v pondělí přehled činnosti a zájmu o akce | Discord - #herald-kontrola (soukromý) |
| při chybě | Hlášení, že některý běh selhal, s odkazem na log | Discord - #herald-kontrola |
| denně 12:00 | Síň slávy: po skončení ligy plakát se stupni vítězů | Facebook + Instagram + Story + Discord #liga |
| denně 12:00 | Souhrn lig: po každém odehraném kole, jakmile jsou výsledky v tabulce ustálené (nezměnily se mezi 9:05 a 12:00); nejvýš 3 ligy denně. Když se výsledky dopíšou až po odeslání, Herald ve 12:00 **upraví už odeslaný souhrn** (nová zpráva nepřibude, v patičce „aktualizováno D. M.“), opět jen s ustálenou tabulkou | Discord - kanál #liga dané karetky |
| neděle 17:00 | Týdenní souhrn na příští týden | Discord - kanál souhrnu |
| neděle 17:00 | Týdenní plakát + Story | Facebook (na šířku) + Instagram (na výšku) |
| poslední den v měsíci 17:05 | Měsíční program: příspěvek Magic + příspěvek ostatní hry + Story | Facebook (na šířku) + Instagram (na výšku) |
| 9, 12, 15, 18, 21 h (se synchronizací) | Bannery do slideru na hlavní stránce: nová edice → prosba o grafiku, grafika ve složce Bannery → hotový banner s textem a odkazem, připomínka „Skladem“ a skrytí starší edice (viz níže) | Soukromá zpráva (PM) |
| 12, 15, 18, 21 h (se synchronizací) | Štítky v e-shopu podle dostupnosti: Předprodej, Připravujeme, Novinka 14 dní od naskladnění (viz níže) | Upgates + PM |

Časy platí v letním i zimním čase, Herald si změnu času hlídá sám.

### Kdo Heralda spouští

Heralda spouští **jen cron-job.org** (záložní plánované běhy GitHubu jsou vypnuté - GitHub je spouštěl se zpožděním i o hodiny). Výpadek spouštění odhalí pondělní kontrola provozu. „Dnes se hraje“ se posílá **jen mezi 9:00 a 12:00** (`announce_window` v config.json) a nikdy u turnaje, který začíná dřív než za hodinu (`announce_min_lead_minutes`).


Plánované spouštění na GitHubu je nespolehlivé (běhy chodí se zpožděním až několik hodin, některé GitHub vynechá). Hlavní spouštění proto dělá **cron-job.org**: v přesný čas pošle GitHubu pokyn „spusť Heralda v režimu X“. Plánované běhy na GitHubu zůstávají jako záloha. Všechny části Heralda mají pojistku, takže když přijde pokyn dvakrát, druhý se jen přeskočí.

Úlohy na cron-job.org (časové pásmo Europe/Prague):

| Úloha | Kdy | `mode` |
|---|---|---|
| Herald - kalendář | každé 3 hodiny | `sync` |
| Herald - kontrola | denně 9:05 | `control` |
| Herald - oznámení | denně 10:00 | `announce` |
| Herald - ligy | denně 12:00 | `league` |
| Herald - e-shop | denně 14:00 | `shop` |
| Herald - týdenní | neděle 17:00 | `weekly` |
| Herald - měsíční | denně 17:05 (vydá jen poslední den v měsíci) | `monthly-auto` |
| Herald - náhled týdne | neděle 15:00 | `weekly-preview` |
| Herald - náhled měsíce | denně 15:05 (pošle jen poslední den v měsíci) | `monthly-preview` |
| Herald - změny | denně 18:00 | `changes` |

Každá úloha posílá **POST** na `https://api.github.com/repos/k8thegr8st/hrana-bot/actions/workflows/main.yml/dispatches` s hlavičkami `Accept: application/vnd.github+json`, `Authorization: Bearer <klíč>`, `X-GitHub-Api-Version: 2022-11-28`, `Content-Type: application/json` a tělem `{"ref":"main","inputs":{"mode":"announce","dry_run":"false"}}` (s příslušným `mode`). Úspěch = odpověď **204**.

**Nová úloha:** v přehledu na cron-job.org u kterékoli úlohy *Clone* → změnit název, čas a v *Advanced → Request body* hodnotu `mode`. URL ani hlavičky (klíč) se nemění. U nových úloh **nedělejte Test run** - spustil by skutečné odeslání.


**Když úloha nefunguje:** cron-job.org → *History* u úlohy. Odpověď **204** = v pořádku. **401** = neplatný klíč (vypršel nebo byl smazán), **404** = špatná adresa nebo klíč nemá přístup k repozitáři, **422** = chyba v těle zprávy (např. neexistující `mode`).

Klíč je GitHub „fine-grained personal access token“ jen pro repozitář hrana-bot s oprávněním **Actions: Read and write**. Platí nejvýš rok - **před vypršením vytvořte nový a vyměňte ho ve všech úlohách** (GitHub pošle e-mail předem).

---

## Soubory v repozitáři

| Soubor | K čemu je |
|---|---|
| `config.json` | Hry, klíčová slova, Discord kanály a role pro turnaje, kanál týdenního souhrnu |
| `shop_config.json` | Kanály a barvy pro novinky z e-shopu, včetně příslušenství (`accessories`) |
| `fb_config.json` | Týdenní plakát: texty příspěvků, barvy her, zapnutí Stories |
| `month_config.json` | Měsíční program: formáty Magicu, názvy her, texty příspěvků |
| `league_config.json` | Souhrn lig: kanály #liga, barvy lig, počet zobrazených hráčů |
| `hrana_bot.py` | Program pro Discord (události, oznámení, souhrn) |
| `eshop_bot.py` | Program pro novinky z e-shopu |
| `fb_weekly.py` | Program pro týdenní plakát a Stories |
| `month_program.py` | Program pro měsíční program a komentáře se změnami |
| `league_bot.py` | Program pro souhrn lig z Google tabulek |
| `control.py` | Program pro kontrolní kanál |
| `control_config.json` | Kontrolní kanál: ID kanálu, jak často připomínat, kdy připomínat kalendář |
| `notify_failure.py` | Hlášení chyby běhu do kontrolního kanálu |
| `activity.py`, `activity.json` | Záznam činnosti Heralda pro pondělní přehled (`activity.json` needitovat) |
| `champions.py` | Program pro síň slávy (šampioni sezóny) |
| `palette.json` | Barvy her - jedna paleta pro všechny výstupy |
| `logo.png` | Logo na plakátech (musí být **na černém pozadí**) |
| `fonts/` | Písma (Bungee, Chakra Petch, Fredoka) |
| `slider.py`, `slider_config.json` | Bannery do slideru z oficiální grafiky edic (`slider_state.json` needitovat) |
| `labels.py`, `labels_config.json` | Automatické štítky Novinka, Předprodej, Připravujeme (`labels_state.json` needitovat) |
| `web/` | Záloha vlastního kódu webu z Upgates (Editor kódu: `_custom.scss`, `@layout.phtml`), Herald ji nepoužívá |
| `.github/workflows/main.yml` | Rozvrh - kdy se co spouští |
| `shop_seen.json`, `weekly_sent.json`, `month_state.json` | Paměť Heralda - **needitovat**, pokud nevíte proč (viz níže) |

Soubory `.py` běžně měnit nepotřebujete. Všechno, co se mění často, je v souborech `.json`.

---

## Jak upravovat soubory `.json`

Na GitHubu otevřete soubor → **tužka** vpravo nahoře → upravit → **Commit changes**.

⚠️ **Pravidla, aby se nic nerozbilo:**

1. **Každý text musí být na jednom řádku.** Nový řádek se píše jako `\n`, prázdný řádek jako `\n\n`. Nikdy nemačkejte Enter uvnitř textu.
2. **Čárky:** za každou položkou je čárka, **kromě poslední** před zavírací závorkou `}` nebo `]`.
3. **Uvozovky:** text je vždy v rovných uvozovkách `"…"`. Uvnitř textu používejte české „takové“.
4. **Hodnoty ve `{složených závorkách}`** (`{od}`, `{akci}`, `{mesic}`…) nechte, Herald je doplňuje sám.

Když si nejste jistá, spusťte po úpravě příslušný běh **nanečisto** (viz Ruční spuštění). Chybu v souboru pak uvidíte v logu dřív, než by se něco pokazilo naostro.

---

## Časté úpravy

### Text příspěvku na Facebooku / Instagramu

**Týdenní plakát** - `fb_config.json`:
- `"caption"` = Facebook
- `"ig_caption"` = Instagram

Značky: `{od}` a `{do}` (datum začátku a konce týdne), `{akci}` (např. „15 akcí“, „3 akce“).

**Měsíční program** - `month_config.json`:
- `"caption_mtg"` / `"ig_caption_mtg"` = příspěvek s Magicem
- `"caption_rest"` / `"ig_caption_rest"` = příspěvek s ostatními hrami
- `"change_header"` = nadpis komentáře se změnami
- `"discord_comment"` = komentář s pozvánkou na Discord, který Herald přidá pod každý nově zveřejněný měsíční program (prázdné = vypnuto)

Značky: `{mesic}` (např. „listopad 2026“), `{hry}` (seznam her v příspěvku).

### Zapnout / vypnout Stories

`fb_config.json` → sekce `"stories"`:

```json
"stories": {"instagram": true, "facebook": true, "weekly": true, "monthly": true}
```

`true` = zapnuto, `false` = vypnuto. Např. `"monthly": false` vypne Stories u měsíčního programu.

### Barvy her

Všechny barvy her jsou v jednom souboru **`palette.json`** a platí všude: plakáty, Stories, novinky z e-shopu, souhrny lig i síň slávy. Změna barvy tady se projeví ve všech výstupech. Barva je ve formátu `#RRGGBB`. Sekce `"_ligy"` jen říká, která liga patří ke které hře (všechny ligy Magicu → `mtg`).

Barvy v `fb_config.json`, `shop_config.json` a `league_config.json` se použijí jen pro hru, která v `palette.json` není.

### Přidat novou hru

Hra se pozná podle klíčového slova v názvu akce v kalendáři.

1. `config.json` → `"games"`: přidat hru s klíčovými slovy, `channel_id` (#události) a `role_id`.
2. `shop_config.json` → `"games"`: přidat `match` (hodnota parametru „Hra“ v e-shopu), `channel_id` pro novinky a `color`.
3. `palette.json`: barva hry (a u ligy přiřazení v `"_ligy"`).
4. `month_config.json` → `"game_names"` (nadpis na plakátu, velkými písmeny) a `"display_names"` (název v textu příspěvku).

Ve všech souborech použijte **stejný klíč hry**, např. `"lorcana"`.

### Formáty Magicu v měsíčním programu

`month_config.json` → `"mtg_formats"`. Každý formát má `label` (nadpis obrázku) a `match` (slova v názvu nebo popisu akce). Pořadí v seznamu = pořadí obrázků v příspěvku. Když se slova překrývají (premodern × modern), vyhraje to přesnější.

### Discord kanály a role

Zjištění ID: Discord → Nastavení → Pokročilé → **Vývojářský režim** zapnout. Pak pravý klik na kanál / roli / server → **Kopírovat ID**.

- kanály #události a role: `config.json`
- kanál týdenního souhrnu: `config.json` → `"weekly_channel_id"`
- kanály novinek: `shop_config.json`

V každém kanálu, kam Herald píše, musí mít **Zobrazit kanál, Posílat zprávy a Vkládat odkazy** (nastavení kanálu → Oprávnění → přidat člena Herald).

### Novinky z e-shopu

`shop_config.json`:
- `"games"` - u každé hry `channel_id` kanálu novinek, `match` (hodnota parametru „Hra“ v e-shopu) a `color`
- `"accessories"` - produkty **bez** parametru „Hra“: `channel_id` (#eshop-novinky), `header` (úvodní věta), `color`. Seskupují se podle výrobce („Nově od Spell Ward“).
- `"preorder_header"` - nadpis zprávy s novými předobjednávkami
- `"restock_header"` - nadpis zprávy „Právě naskladněno“, `"restock": false` ho vypne
- `"big_card_max"` - do kolika novinek najednou se posílají velké karty (výchozí 1, víc = seznam)
- `"remove_from_start"` - slova, která se odstraní ze začátku názvu produktu

Produkt se jako novinka oznámí jen jednou (`shop_seen.json`). Stav skladu každého produktu si Herald pamatuje v `shop_stock.json` - podle něj pozná, kdy se předobjednávka nebo vyprodané zboží změní na skladem.

### Souhrn lig

`league_config.json` → `"leagues"`: u každé ligy `channel_id` kanálu #liga (prázdné = liga se přeskočí) a `color` (barva proužku). Dále:
- Souhrn ligy chodí **po každém odehraném kole**, ale jen když ranní kontrola (9:05) u ligy nenašla žádný problém (chybějící výsledky, nečitelné hodnoty, kolo s jediným hráčem, podezřelé body…) a výsledky jsou ustálené: ráno v 9:05 si Herald tabulku zapamatuje a ve 12:00 souhrn pošle jen tehdy, když se mezitím nezměnila. Když se zrovna zapisuje, počká na další den.
- `"interval_days"` - nejkratší odstup souhrnů jedné ligy ve dnech (výchozí 0 = po každém kole)
- `"max_per_day"` - kolik lig nejvýš za den (výchozí 3). Pořadí lig v souboru rozhoduje, která přijde na řadu dřív.
- `"show_top"` - kolik hráčů zobrazit (výchozí 10)
- `"milestone_tournaments"` / `"milestone_reward"` - kolikátý turnaj v lize se slaví a co hráč dostane (výchozí 10 a „50 Bitů“). Souhrn ligy navíc ukazuje nováčky a nejlepší výsledek posledního kola. Slíbené Bity Herald připomene v #herald-kontrola (označení `bity` v control_config.json) - připsat je musíte ručně. Do `milestones_public_from` chodí milníky jen jako náhled do soukromé zprávy.
- `"headers"` - úvodní věty nad souhrnem podle fáze ligy (`start` po 1. kole, `half` v polovině sezóny, `last_round` před posledním kolem, `finale` po základní části, `regular` se jinak střídají). `{liga}` se nahradí názvem ligy.
- `"first_name_first"` - `true` = „Jméno Příjmení“, `false` = „Příjmení, Jméno“ jako v tabulce

Data se berou ze stejných Google tabulek jako web ligy (hlavní tabulka `master_sheet_id`, list **Ligy** s odkazy na tabulky lig, list **Sezony** s aktuální sezónou). Herald tabulky jen čte, nikdy do nich nezapisuje. Tabulky musí zůstat čitelné pro každého s odkazem, jinak nefunguje ani web, ani Herald.

Nová liga: přidat ji do listu **Ligy** v hlavní tabulce (jako pro web) a do `league_config.json` se stejným ID.

### Síň slávy (šampioni sezóny)

Herald každý den ve 12:00 zkontroluje, jestli některá liga skončila:
- **finále TOP4/TOP8** - jakmile je v tabulce ligy vyplněný sloupec **„Topka“** (aspoň 1., 2. a 3. místo). Plakát ukazuje umístění z finále, bez bodů.
- **formát Žebříček** - den po posledním turnaji sezóny. Plakát ukazuje pořadí podle bodů.

Pak pošle **náhled ke schválení do #herald-kontrola** (oba plakáty a texty). Zveřejní ho až po reakci ✅ (❌ = nezveřejňovat; smazaný náhled = nezveřejňovat). Rozhodnutí si Herald přečte při nejbližším denním běhu ve 12:00 a teprve pak zveřejní plakát na Facebook (na šířku), Instagram (na výšku), do Story a s gratulací do kanálu #liga. Zveřejňují se jen ligy, jejichž finále proběhlo nejvýš před 30 dny a ne dříve než `since` (2026-10-05). Každou ligu a sezónu jen jednou. Hlídá i předchozí sezónu, takže nevadí, když se Topka vyplní až po jejím konci.

Texty lze změnit v `league_config.json` přidáním sekce `"champions"` (`title` = nadpis plakátu, `caption`, `ig_caption`, `discord`, `poster_footer`; značky `{liga}`, `{sezona}`, `{p1}`, `{p2}`, `{p3}`). Vypnutí: `"social_enabled": false` (jen Discord), `"discord_enabled": false`, `"stories": false`.

Ruční spuštění nanečisto (`champions`) vytvoří náhled plakátu z aktuálního pořadí, i když žádná liga ještě neskončila (v Artifacts → plakaty).

### Kontrolní kanál (#herald-kontrola)

Soukromý kanál jen pro vás. Herald hlásí problémy (vyřešení zvlášť nepotvrzuje) a **každé ráno pošle jednu krátkou zprávu „🩺 Ranní kontrola“** se stavem všech kontrol (✅ v pořádku / ⚠️ počet problémů / ❌ nepodařilo se zkontrolovat). Patří do ní i **Provoz Heralda (včera)** - jestli včera proběhly všechny plánované běhy podle cron-job.org (a které chyběly) - a **Feed pro Google** (jestli se feed načetl). Ticho tedy nikdy neznamená „asi dobrý“: každý den přijde výslovně, co je v pořádku. Posílá do něj:
- **Chybějící výsledky lig** - den po ligovém turnaji, pokud v tabulce nejsou body. Opakuje každé 3 dny (`repeat_every_days`), dokud se nezapíšou. Hlídá celou aktuální sezónu (`missing_lookback_days`: 0 = celá sezóna, jiné číslo = jen posledních N dní).
- **Kalendář × tabulky lig** - ligový turnaj je v kalendáři, ale ne v tabulce (nebo naopak). Ozve se jen při nové nebo změněné neshodě. Porovnává jen data do konce aktuálního měsíce (další měsíce hlídá připomínka kalendáře). Za ligový turnaj se v kalendáři považuje akce se slovem „Liga“ nebo „Finále“ v názvu.
- **Doplň kalendář** - 20. a 27. den v měsíci (`calendar_reminder_days`): kolik akcí je na další měsíc a které hry oproti tomuto měsíci chybí.
- **1. den v měsíci** (do #herald-prehledy) - zdraví lig za uplynulý měsíc: průměrná účast a trend proti předchozímu měsíci, noví hráči, kdo přestal chodit (odehrál aspoň 3 kola a poslední 3 vynechal).
- **Pondělí** - co Herald minulý týden udělal (včetně chyb), **kontrola provozu** (zda proběhly všechny plánované běhy podle rozvrhu cron-job.org; když něco chybí, vypíše co a kdy) a zájem o akce v nadcházejícím týdnu („Mám zájem“).
- **Kontrola tabulek lig** - nečitelné hodnoty v bodech (např. „x“), záporné body, body u kola, které se ještě nehrálo, nápadně vysoké body (překlep 60 místo 6), kolo s jediným hráčem, výsledky finále (dvě stejná umístění, vynechané místo, víc finalistů než postupuje, finalista mimo postupující), chybějící další sezóna v listu Sezony (14 dní před koncem), liga bez listu nové sezóny, stejný hráč zapsaný v lize vícekrát (třeba „Toth, Erik“ × „Tóth, Erik“) a hráč zapsaný v různých ligách různě.
- **Kontrola e-shopu** (produkty, které se mají přeskakovat - např. poukazy nebo vstupné prodávané jen na prodejně - patří do `shop_check_ignore` v control_config.json, stačí část názvu) - produkt bez obrázku, bez popisu, bez ceny, předobjednávka s prošlým datem vydání a produkt, který podle názvu patří ke hře, ale nemá parametr „Hra“ (pak se neoznámí ve správném kanálu).
  U obou kontrol: **denně jen nově nalezené** problémy, **v pondělí souhrn všeho neopraveného**.
- **Připraveno k naskladnění** (vypíná se v `control_config.json`: `"restock_report_enabled": false`) - při prvním běhu si Herald zapamatuje vše, co tehdy nebylo skladem, a to už nikdy nehlásí. Pak každé pondělí počet produktů, které jsou v e-shopu připravené, ale ještě nikdy nebyly skladem (z feedu pro Google Nákupy, `google_feed_url`), rozdělený podle kategorie; celý seznam s odkazy je ve vlákně pod zprávou. Vyprodané produkty se nepočítají (Herald je pozná podle toho, že je někdy viděl skladem - pamatuje si to od 4. 10. 2026). Vyloučené produkty: `restock_ignore` (poukaz, občerstvení, nápoje…).
- **✅ = zkontrolováno:** když pod hlášení Kontroly e-shopu nebo Kontroly tabulek lig dá kdokoli z týmu ✅, Herald všechny problémy z té zprávy při dalším běhu vyřadí a už je nikdy nehlásí (ani v pondělním „Stále neopraveno“). Platí to pro opravené věci i pro věci, které jsou správně tak, jak jsou. Fajfku dávejte, až zkontrolujete všechno ve zprávě. Když je potřeba nechat něco hlásit dál, ✅ nedávejte.
- **Kontrola feedu pro Heureku** (`product_rules.py`) - součást kontroly e-shopu, **pro všechny produkty** (`check_all_products: true` v `control_config.json`):
  - 🔢 EAN: chybí, neplatná kontrolní číslice, 14 číslic. Výjimky: `ean_missing_ok` (názvy, které EAN mít nemusí - samotné boostery, Gundam Assemble Color…), `ean_invalid_ok` (Spell Ward), sdílené EANy v `ean_ok`.
  - 🧩 Parametry: produkt bez parametrů, karty bez Druhu / Série / Jazyka / Žánru / Věku od (výjimky podle hry v `card_param_skip_by_serie`), bez Typu balení a Edice, Pokémon bez „Pokémon edice“, deskovky bez Počtu hráčů / Délky / Věku / Typu / Jazyka pravidel.
  - 📝 Název a popis: výrobce v názvu dvakrát, dlouhá pomlčka, nepořádek v popisu (DOPLNIT, h1, class=, data-start), popis kratší než `min_description_chars` (300), odkaz v popisu na produkt, který není ve feedu.
  - 🗂️ Chybí kategorie pro Heureku.
  - **Jen u nových produktů** navíc přísnější pravidla: povolené hodnoty parametrů, Druh podle Typu balení, žánr a věk podle hry, kategorie Heureky podle druhu, „z edice“ v první větě popisu, formáty u deskovek, dostupnost.
  - Z feedu pro Google: výrobce, zdvojený a nesedící výrobce v názvu, neplatný GTIN, dlouhá pomlčka, název nad 150 znaků, chybějící kategorie Google.
  - Co je správně tak, jak je, odfajfkujte ✅ pod hlášením, nebo přidejte výjimku do `control_config.json`.
- **Stejný EAN u více produktů** - součást kontroly e-shopu (obvykle chyba při kopírování produktu). Když je stejný EAN správně (výrobce ho tak opravdu dává, např. Mega Moonlight Tin), přidejte ho do `control_config.json` → `ean_ok` a už se hlásit nebude.
- **Údaje nových produktů** - součást kontroly e-shopu: chybí výrobce, chybí EAN, výrobce nesedí s názvem (např. „Gamegenic Ultra PRO…“), zdvojený výrobce v názvu pro feed (u produktů, jejichž název začíná výrobcem, odškrtnout „zobrazení výrobce v názvu“ na záložkách Heureka a Google) a poznámky v názvu („DOPLNIT“, „TODO“). Kontrolují se jen produkty přidané po prvním spuštění - staré se záměrně nehlásí.
- **Nová edice skladem** - když z předobjednávky dorazí aspoň 3 produkty jedné edice - podle parametru **Série** v e-shopu, u produktů bez Série podle stejné hry a data vydání (`new_edition_min_products`), připomínka napsat článek (do newsletteru se edice dostane sama v nejbližším dvoutýdenním návrhu). Každá edice jen jednou, jednotlivé produkty ji nespustí.
- **Konkurence** - každé ráno Herald projde úvodní stránku konkurence (bannery) i jejich **stránku předprodeje** (`presale_url`) - produkty seskupí podle edice (např. všechny produkty Star Treku) a když se objeví nová edice her, které prodáváte, pošle název, hru, stav a odkaz. Edice se počítá od 2 produktů (`presale_min_products`). První kontrola pošle přehled toho, co tam je teď.
- **Klíč k Facebooku a Instagramu** - denně ověří, že platí. Když přestane fungovat, dá vědět (pak každé 3 dny, dokud se neopraví).
- **Akce, kterým Herald nerozumí** - akce na příštích 14 dní, u kterých nepozná hru (překlep v názvu, nová hra). Ozve se jen při změně. Hry, které záměrně nikam nepatří, jsou v `ignore_unrecognized` (teď Palworld).
- **Oprávnění v kanálech** - každé pondělí spočítá, jestli Herald může psát a vkládat karty do všech nastavených kanálů. Ozve se jen při problému.
- **Připni měsíční program** - hned po jeho zveřejnění, s odkazy na příspěvky.
- **Chyba běhu** - když něco selže, s odkazem na log.

Pondělní přehledy (co Herald dělal, zájem o akce) chodí do samostatného kanálu `reports_channel_id` (#herald-prehledy); když není vyplněný, chodí do kontrolního kanálu.

Nastavení v `control_config.json`. Sekce `mentions` určuje, koho Herald u které zprávy označí (ID uživatelů: vývojářský režim → pravým tlačítkem na jméno → Kopírovat ID uživatele): `missing_results`, `calendar_mismatch`, `sheet_check`, `shop_check`, `new_edition`, `competitor`, `restock_check`, `calendar_reminder`, `pin`, `failure`, `weekly`. Sekce `league_calendar` říká, podle čeho Herald v kalendáři pozná turnaje které ligy (hra a u Magicu slovo formátu).

Ruční spuštění `control` pošle i pondělní přehledy bez ohledu na den.

### Logo na plakátech

Vyměňte `logo.png`. Logo musí být **na černém pozadí** (ne průhledné PNG) - černá se na plakátu „rozpustí“ a zůstane jen neon.

---

## Ruční spuštění

**Actions → Herald → Run workflow** → vybrat, co spustit:

| Volba | Co udělá |
|---|---|
| `sync` | Synchronizace kalendáře s Discord událostmi |
| `announce` | „Dnes se hraje“ (+ synchronizace) |
| `shop` | Novinky z e-shopu |
| `weekly` | Týdenní souhrn na Discord + plakát na FB/IG + Story |
| `facebook` | Jen týdenní plakát na FB + IG (Discord nechá být) |
| `instagram` | Jen týdenní plakát na Instagram |
| `monthly` | Měsíční program na příští měsíc |
| `monthly-auto` | Totéž, ale jen poslední den v měsíci (pro cron-job.org) |
| `changes` | Kontrola změn v měsíčním programu a komentáře |
| `league` | Souhrn lig do kanálů #liga + kontrola šampionů |
| `champions` | Jen kontrola šampionů sezóny |
| `control` | Kontrolní kanál (pondělní přehledy jen v pondělí) |
| `control-full` | Kontrolní kanál včetně pondělních přehledů, kdykoli |
| `control-reset` | Kontrolní kanál „na čisto“: zapomene, co už hlásil, a pošle všechno znovu |
| `slider` | Bannery do slideru hned (jinak běží se synchronizací) |
| `slider-debug` | Jen výpis do logu: jakou hru a edici Herald u produktů vidí (když banner nepozná edici) |
| `labels` | Štítky Novinka / Předprodej / Připravujeme hned (jinak běží se synchronizací od 12 h) |

**„Jen nanečisto“ zaškrtnuté** = nic se nezveřejní, jen se vše vyzkouší. Plakáty si pak stáhnete dole na stránce běhu v sekci **Artifacts → plakaty**.

**„Jen nanečisto“ odškrtnuté** = opravdu se zveřejní.

---

## Paměť Heralda (pojistky proti zdvojení)

| Soubor | Co si pamatuje |
|---|---|
| `shop_seen.json` | Produkty z e-shopu, které už oznámil |
| `shop_stock.json` | Stav skladu produktů (skladem / předobjednávka / vyprodáno) kvůli „Právě naskladněno“ |
| `weekly_sent.json` | Které týdenní a měsíční příspěvky už vyšly a kolik kol měla každá liga při posledním souhrnu |
| `month_state.json` | Obsah zveřejněných měsíčních programů a odkazy na ně (kvůli komentářům se změnami) |

Díky nim se nic nezveřejní dvakrát, ani když se běh spustí znovu.

**Chci příspěvek zveřejnit znovu** (např. jste ho smazala): v `weekly_sent.json` smažte řádek s danou položkou (např. `"facebook"`, `"instagram"`, `"story"`) a spusťte běh znovu. Nezapomeňte na pravidlo s čárkami.

---

## Náhledy do soukromé zprávy

2 hodiny před zveřejněním týdenního plakátu (neděle 15:00) a měsíčního programu (poslední den v měsíci 15:05) pošle Herald **soukromou zprávu** člověku z `control_config.json` → `preview_user_id`: plakáty a text příspěvku.
- **Bez reakce** se v 17:00 / 17:05 normálně zveřejní.
- **Reakce ❌** pod náhledem = nezveřejní se nic (Facebook, Instagram, Story ani týdenní souhrn na Discordu). Herald zrušení potvrdí soukromou zprávou.
- Zkušební náhled kdykoli: Run workflow → `preview-test` (bez zaškrtnutého „Jen nanečisto“). Přijde označený TEST a nic neovlivní.
- Aby mohl Herald soukromou zprávu poslat, musí mít příjemce na serveru povolené soukromé zprávy od členů serveru.

## Když se turnaj nekoná

Do názvu akce v kalendáři přidejte slovo **„ZRUŠENO“** (např. „ZRUŠENO - Sorcery liga“). Herald akci neoznámí, nedá ji na plakát ani do měsíčního programu (pod zveřejněný program napíše „Zrušeno“), smaže ji z Discord událostí a u ligy nebude chtít výsledky v tabulce. Starší zrušená kola lze zapsat i ručně do `control_config.json` → `cancelled_rounds` (klíč je zkratka ligy, např. `"so": ["2026-09-14"]` pro Sorcery).

## Týdenní video (Reels)

Každé pondělí: **13:00 náhled** do soukromé zprávy (`reel-preview`), **15:00 zveřejnění** jako Reel na Facebook a Instagram (`reel`), pokud pod náhled nedáte ❌. Video: program aktuálního týdne → „Takový byl minulý týden“ (z každého příspěvku „Report přímo z Hrany“ z minulého týdne fotka vítěze a dvě fotky z večera, nejvýš 3 turnaje rozložené přes týden) → závěr s logem a adresou. Hudba náhodně z `music/meta` (stejná pro náhled i zveřejnění). Texty a časování v `video.py` (CFG) nebo `video_config.json`. Zkouška kdykoli: `video-test`.

**TikTok a YouTube Shorts (ručně):** po zveřejnění na FB/IG Herald nahraje video s hudbou z `music/free` v plné kvalitě do složky aktuálního měsíce na Google Disku (servisní účet musí mít ke složce právo **Editor**) a hlídač Disku ho při další kontrole ohlásí lidem z `drive_config.json` → `notify_users` i s popiskem pro TikTok a názvem pro YouTube Shorts, každý v samostatné zprávě (texty `tiktok_caption`, `yt_title` v `video.py`). Vlastní video Heralda se do dalšího Reelu nikdy nezařadí. Když nahrání na Disk selže, pošle Herald video a popisky přímo soukromou zprávou lidem z `manual_post_users`. Režim `video-test` pošle ukázku jen do soukromé zprávy z `preview_user_id`. Discord pustí botovi soubor nejvýš 10 MB - větší video Herald do zpráv pošle zmenšené (na FB/IG jde vždy plná kvalita).

**Videa z Google Disku:** Herald do Reelu přidá i videa nahraná do sdílené složky (`drive_config.json`) od minulého pondělí 12:00 do tohoto pondělí 12:00 - stačí je nahrát do složky měsíce (např. `2026 / 10 říjen`, i do podsložek) nejpozději v pondělí do poledne. Zařadí se mezi fotky (po každém turnaji jedno), celá, bez původního zvuku. Video do 6 s jde normální rychlostí, delší zrychleně 1,3×. Kdyby Reel přesáhl 88 s, delší videa se zrychlí víc (nejvýš 2×) a teprve pak se zkrátí. Nejvýš 6 videí za týden (`max_videos`), hudba se v případě potřeby zopakuje. Náhled v soukromé zprávě uvádí počet videí. Když Disk není dostupný, Reel vyjde jen s fotkami.

## Hlídání recenzí (Heureka, Zboží, Google)

Spolu se synchronizací kalendáře (9:00, 12:00, 15:00, 18:00, 21:00) Herald zkontroluje recenze a každou novou pošle do kanálu `reviews_config.json` → `channel_id` (prázdné = soukromou zprávou podle `notify_users`, případně `preview_user_id`). První běh si jen zapamatuje stávající recenze. Ručně: režim `reviews`.

- **Heureka** (recenze obchodu i produktů): secret `HEUREKA_REVIEW_KEY` = tajný klíč služby Ověřeno zákazníky.
- **Zboží.cz** (recenze obchodu i produktů): secret `ZBOZI_API_KEY` = API klíč ze Skliku (Sklik → Nastavení → API), ID provozovny 241766 je v `reviews_config.json` → `zbozi_shop_id`.
- **Google**: secret `GOOGLE_PLACES_KEY` = API klíč z Google Cloud (projekt Hrana-Bot, zapnuté *Places API (New)*, omezit jen na toto API). Provozovnu Herald najde sám podle `google_place_query`. Google ukazuje jen 5 recenzí, proto Herald hlídá i počet hodnocení - nové hodnocení bez textu ohlásí jako „přibylo nové hodnocení“.

Bez nastaveného klíče se daná služba přeskakuje.

## Novinky služeb (Upgates, Heureka, Zboží, Google Merchant)

Každý den v 9:00 (se synchronizací kalendáře) Herald otevře stránky s novinkami z `updates_config.json` → `sources` (Upgates roadmapa, Heureka novinky a Ověřeno zákazníky, blog Sklik pro Zboží/Seznam Nákupy, Google Merchant Center announcements) a co na nich přibylo **a týká se e-shopu**, pošle soukromou zprávou. Filtr je v `updates_config.json`: novinka musí obsahovat aspoň jedno slovo z `include` (feed, recenze, produkty, podmínky, poplatky, doprava, povinné…) a žádné z `exclude` (reklamní kampaně, webináře, soutěže, rozhovory, tiskové zprávy…). Co filtr propustil a co ne, je vidět v logu běhu (✔ / ✘) (`notify_users`, prázdné = `preview_user_id`). První běh si stránky jen zapamatuje. Když se stránka celá předělá, přijde jen jedna zpráva „stránka se výrazně změnila“. Další stránku přidáte do `sources` (název + adresa). Ručně: režim `updates`.

## Týdenní recap e-shopu (Google Analytics)

Každé **úterý** s ranní kontrolou (9:05; v úterý už má Google data za neděli kompletní) pošle Herald **soukromou zprávou** (citlivá data; `control_config.json` → `analytics.user_ids`, prázdné = `preview_user_id`; do kanálu jen když se vyplní `analytics.channel_id`) shrnutí minulého týdne z GA4: tržby, objednávky, návštěvy a změna proti předchozímu týdnu, odkud přišly tržby (Google Ads s útratou a návratností, Heureka, přímo, vyhledávání bez reklamy, e-maily), 5 nejprodávanějších produktů a „Na co se podívat“ (návratnost Ads pod 8x, velká změna tržeb kanálu, kampaň s útratou bez tržeb, produkt často v košíku a málo koupený, produkt často zobrazený a nikdy v košíku). Hranice jsou v `analytics_recap.py` (A) a dají se přepsat v `control_config.json` → `analytics`. Ruční zkouška: režim `analytics-test`.

Nastavení (jednou): v Google Cloud (projekt Hrana-Bot) zapnout **Google Analytics Data API** (zdarma, bez karty); v Analytics → Správce → Správa přístupu ke službě přidat `herald@hrana-bot.iam.gserviceaccount.com` jako **Čtenář**; ID služby (Správce → Podrobnosti o službě) zapsat do `control_config.json` → `analytics.property_id`. Útrata za Google Ads se bere z propojení Ads s Analytics; když chybí, recap to napíše a pošle se bez ní.

## Newsletter jednou za 2 týdny

Každý **druhý čtvrtek ráno** (s ranní kontrolou, poprvé 15. 10. 2026; `newsletter.start`, `newsletter.every_days`) pošle Herald do soukromé zprávy (`control_config.json` → `newsletter.user_ids`, prázdné = `preview_user_id`) **hotový návrh**: předmět, náhledový text a e-mail v HTML jako přílohu. V Upgates založit newsletter, v editoru přepnout na zdrojový kód a vložit. Nic se neodesílá samo.

Co do něj jde (sbírá se průběžně při běhu e-shopu: nové produkty, předobjednávky, naskladněné předobjednávky):
- **Velké karty** (nejvýš 12, vždy sudý počet): nejhodnotnější zboží. Přednost má celá nová edice (aspoň 3 produkty), pak booster boxy, collectory, bundly, ETB, commander a dražší věci.
- **Malá sekce** „Dále nově v e-shopu“ (nejvýš 6): kostky, obaly, krabičky, podložky a věci pod 300 Kč (`newsletter.small_price`). Newsletter na nich nikdy nestojí.
- **Velké akce** (prerelease, PreRift, šampionát…; `newsletter.event_words`) v příštích 3-28 dnech jako „vstupenka“ s datem v barvě hry a fotkou edice.
- Dole nejbližší akce z kalendáře, sociální sítě a odkaz na odhlášení (`{$cancelUrl}`).

Když za 2 týdny nepřibylo nic hodnotného ani se nechystá velká akce, návrh nepřijde. Do e-mailu jdou jen produkty s fotkou na bílém nebo průhledném pozadí, logo se načítá z herald-web/logo.png. Stav v `newsletter_state.json`. Test kdykoli: úloha `newsletter-test` (z posledních produktů e-shopu, jen do PM).

## Stálé zprávy (uvítání)

Uvítací zprávu v `#welcome` posílá Herald (`messages.py`, texty v `messages.json`). Úloha `messages` (ručně na GitHubu → Actions → Run workflow, nebo jednorázově z cron-job.org): když zpráva ještě není, pošle ji **tiše** (nikomu nepřijde upozornění), když už je, **přepíše** ji. Úprava textu = upravit `messages.json` a spustit `messages` znovu. ID zprávy je v `messages_state.json`. Herald (role Hrana Bot) musí mít v kanálu právo psát a vkládat odkazy.

## Obrázky kategorií v menu (Upgates API)

`category_images.py` (+ `upgates_api.py`, nastavení `category_images_config.json`) nastaví obrázek každé podkategorie pod hrami v menu e-shopu podle **nejnovějšího produktu skladem** (aktivní, jde koupit, má fotku; přeskakuje „POŠKOZEN“ a „Vstup “). Mění jen kategorie, které už obrázek mají. Když v kategorii nic skladem není, obrázek zůstane.

Secrets: `UPGATES_API_URL`, `UPGATES_API_LOGIN`, `UPGATES_API_KEY` (API uživatel: Kategorie čtení i zápis, Produkty čtení). Tarif Bronze má limit 100 požadavků denně, jeden běh jich spotřebuje typicky do 15. Po 5 špatných přihlášeních za hodinu Upgates API zablokuje, takže při chybě 401 nespouštět dokola.

Běží samo každý den v 9:00 (se synchronizací): nejdřív zkusí jednu kategorii, ověří, že je obrázek zaškrtnutý jako Hlavní i Seznamový, pak teprve ostatní. Když něco nesedí, vrátí původní obrázek (záloha se ukládá před zápisem do `category_images_state.json`). Fotky .webp a fotky s barevným pozadím přeskakuje. Nakonec zaškrtne případné nezaškrtnuté obrázky. Do PM píše jen při změně nebo chybě.

Kategorie bez obrázku se doplňují jen u her v `include_without_image` (teď Cyberpunk); když tam není fotka na bílém pozadí, vezme se i fotka s pozadím (lepší než prázdné místo). „Další karetky“ mají v menu loga her, ty Herald nemění (nejsou v `parent_categories`). Vypnutí celé automatiky: `"replace_confirmed": false`.

Ruční úlohy: `category-images` (náhled do PM), `category-images-apply` (hned teď), `category-images-fix` (jen zaškrtne Hlavní + Seznamový).

## Kostry aktualit k novým edicím

Když se spustí předobjednávky nové edice (aspoň 3 produkty jedné hry a edice, sbírá se i přes víc dní), pošle Herald do PM kostru aktuality ve stylu hrananetu.cz/news (`aktuality.py`, volá ho `eshop_bot.py`): perex s datem vydání a hotovou sekci Produkty s obrázky a odkazy. Sekce „O čem set je“ a „Chase karta“ se doplní s Claude v chatu (Herald nemá AI), Claude pak připraví i soubor pro import do Upgates (Obsah → Import). Aktuality přes Upgates API zakládat nejde, API je nevrací. Každá edice jen jednou (`aktuality_state.json`).

## Reporty z turnajů jako články na webu

Při synchronizaci (9:00-21:00) projde Herald příspěvky FB stránky za poslední 3 dny (`fb_articles.py`). Z každého turnajového reportu (začíná „Report…🎙️“) udělá článek: nadpis s datem a turnaji, perex, sekce po turnajích (jen česká část před „/ / /“), fotky z příspěvku, odkaz do kalendáře. Nahoře koláž ze 4 náhodných fotek (celé, mírně natočené, stažené z FB v plném rozlišení; koláž 2400 px, ostrá i na kvalitních displejích) s pruhem REPORT Z HRANY, datum, akce, místo; text zarovnaný doleva. Článek rovnou zveřejní v Upgates (Obsah → Články) v kategorii „Turnaje“ (patička → Zajímavosti, hrananetu.cz/turnaje) a pošle info do PM. ❌ pod info do 3 dnů = článek se smaže. Stav v `fb_articles_state.json`. Úplně první běh vezme jen nejnovější report. Ruční spuštění: úloha `fb-articles`. Starší reporty (s koláží v nízkém rozlišení) dostávají postupně novou koláž, 3 články na běh, dokud nejsou všechny (`fb_articles_state.json` → `recollage`; vypnout `recollage_old: false` v CFG).

## Bannery do slideru na hlavní stránce

Upgates API bannery neumí, takže Herald všechno připraví a v Upgates se jen nahraje a přepne (`slider.py`, běží se synchronizací v 9, 12, 15, 18 a 21 h).

1. **Nová edice** (aspoň 3 produkty jedné hry se stejnou Edicí, `slider_config.json` → `min_products`) → PM „Chtělo by to banner“ s odkazem na složku **Bannery** na Disku (v hlavní sdílené složce Heralda).
2. **Grafika do složky Bannery** (oficiální key art, co nejširší, bez textu; JPG/PNG/WebP). Název souboru je jedno: když z něj Herald edici nepozná, pošle seznam edic s písmeny 🇦-🇹 a stačí kliknout. Z grafiky udělá banner 1512 × 672 (2× velikost slideru, WebP): postava doprava, barvy ztlumené do barev webu, levá strana tmavá pro text. Do PM pošle banner + **nadpis** (název edice), **podnadpis** (krátký název karetky a stav, např. „Magic: Skladem“ / „Pokémon: Předprodej“) a **odkaz na celou edici** (stránka edice `/kategorie/p-edice/hodnota`, jinak filtr Edice v kategorii; ⚠️ = odkaz vede jen na kategorii nebo produkt). Má-li stejná hra starší banner, připomene ho skrýt.
3. **Edice dorazí na sklad** → PM: přepnout podnadpis na „Skladem“.

Text nadpisu a podnadpisu vypisuje web sám (Bungee / Chakra Petch), do obrázku se nepíše. Edice a stav bere Herald z **feedu pro Google** (`control_config.json` → `google_feed_url`); feed pro Heureku parametr Edice nemá. Pojistky: první běh a víc než 3 „nové“ edice najednou (`max_new_per_run`) se jen zapamatují, nic se nepíše; při limitu Discordu (429) Herald počká a zkusí znovu. Při změně vzhledu banneru (`BANNER_V` ve `slider.py`) pošle hotové bannery znovu v novém vzhledu. Stav v `slider_state.json`.

## Štítky Novinka, Předprodej a Připravujeme

Herald nastavuje štítky podle **dostupnosti produktu v Upgates** (`labels.py`, se synchronizací ve 12, 15, 18 a 21 h; v 9 h ne, kvůli limitu API s obrázky kategorií):

- dostupnost **Předprodej** → štítek **Předprodej** (jiná dostupnost → štítek se vypne)
- dostupnost **Připravujeme** → štítek **Připravujeme** (jiná dostupnost → štítek se vypne)
- dostupnost **Skladem** → **Novinka** `new_days` dní (14) od prvního naskladnění. Herald nastaví v Upgates platnost štítku (do kdy), takže zmizí sám i bez Heralda. Znovu naskladněné zboží (už někdy skladem bylo) Novinku nedostane, mimo Skladem Novinka nesvítí.
- Ostatní štítky (Sleva, Vánoční slevy…) se nemění, Herald je posílá zpátky beze změny. Názvy štítků a dostupností jsou v `labels_config.json` (prázdný název štítku = Herald na něj nesahá).

**Kategorie Předprodej** (`category_name`): v Upgates má Seznam produktů nastavený na produkty přiřazené ke kategorii (podle štítku by šel jen jeden štítek). Herald do ní řadí produkty s dostupností Předprodej a Připravujeme (`category_avails`) a ostatní z ní vyřazuje (hlavní kategorie produktu se nemění). Zapíná se zvlášť vlastním přehledem a ✅. Kdyby Upgates API neumělo produkt z kategorie odebrat, Herald jen přidává a produkty k ručnímu vyřazení pošle do PM.

Úplně první běh nic nemění: pošle do PM přehled, co by změnil, a automatiku zapne až ✅ pod tou zprávou. Při prvním běhu se u produktů skladem bere jako naskladnění datum založení produktu. Každý zápis nejdřív jde na 1 produkt, Herald ho přečte zpátky a ověří, že se nezměnilo nic jiného (jinak vrátí a zastaví se, přijde zpráva). Dostupnost a štítky všech produktů čte jednou denně (kvůli limitu API klidně ve 2 bězích), jinak jen změněné produkty. Po každé změně přijde do PM krátký přehled (vypnout: `notify_changes: false`).

## Asmodee dropship (feedy ecat.b2btoys.cz)

`asmodee.py`, nastavení `asmodee_config.json`, stav `asmodee_state.json`. Běží při každé synchronizaci 7:00-22:00.

Zboží z vlastního skladu Herald nechává být, i když ho má i Asmodee. Řídí jen dropship produkty, které sám založil.

1. **Katalog:** úloha `asmodee-katalog` pošle do PM xlsx se vším, co Asmodee má (nákup, MOC, marže, jestli už to máme).
2. **Zalistování:** kódy Asmodee napiš Heraldovi do PM (např. `AC01CZ AS7DU01CZ`). Při další synchronizaci je založí **skryté**: další volný kód P0xxxx, cena = MOC (novinky premium max 10 % pod MOC), název, popis, krátký popis a fotky z feedu, EAN, výrobce, nákupní cena. Seznam pošle do PM, **✅ = zveřejnit**. Úplně první produkt zakládá sám. Najednou čeká na ✅ nanejvýš `max_hidden` (4) skrytých produktů. Kategorie podle `category_name` (prázdné = zařadit ručně).
2b. **Novinky:** nová deskovka ve feedu (a při prvním běhu hry před vydáním, které ještě nemáme) → kartička do PM s datem vydání a MOC, **✅ = zalistovat** (do fronty, založí se skryté). Nanejvýš `max_new_cards` (5) kartiček za běh, zbytek jedním seznamem. `watch_new: false` vypne.
3. **Dostupnost:** dropship produkt má **Skladem u dodavatele**, když ho Asmodee má (feed = 100), není víc než 2 dny před vydáním a prodává se po 1 kuse. Hra před vydáním dostane **Předprodej** (`pre_avail`) a 2 dny před vydáním se sama přepne na Skladem u dodavatele (Asmodee neposílá dřív). Jinak „není skladem“. Když ho naskladníš sama (sklad > 0), přepne na Skladem.
4. **Heureka a Google:** dostupnost „Skladem u dodavatele“ musí být v Upgates **typu Skladem** (jinak Herald nic nedělá). Po zveřejnění Herald zkontroluje Heureka feed (DELIVERY_DATE do 3 dnů) a Google feed (in_stock). Když nesedí, napíše a další produkty nezakládá.
5. **Objednávky:** objednávka s dropship produktem → PM: kód Asmodee, kusy, adresa, jestli to pořád mají. Objednává se ručně na b2b.asmodee.cz (API nemají). Adresa jen v PM, ne do logu ani repa.
6. **Discord:** dropship produkty se v #eshop-novinky ani v newsletteru neoznamují (`shop_config.json` → `"announce_dropship": true` to zapne).

- Feed dostupnosti má jen 0 / 100 (ne počet kusů), řádky s `@` v kódu (jiný ceník) se ignorují.
- Ve feedu je `voc` = MOC bez DPH (ne nákupka), pokud `netto_cena` není ANO. Nákupka = voc minus `purchase_discount_pct` (doplnit, až Asmodee řekne slevu).
- Plnění produktu: fotky hlavně z veřejné stránky produktu v B2B portálu (`images.asmodee.cz/api/v2/image/b2b.WxH/ID.jpg`, celá galerie; když ji vyhledávání nenajde, stačí poslat Heraldovi do PM odkaz na produkt v B2B), záloha `images.asmodee.cz` (Asmodee u chybějící fotky vrací ilustrační foťák s kódem 200, Herald ho pozná podle otisku a nepošle; zkusí i EAN; produkty bez fotky hlídá denně a fotku doplní, až ji Asmodee nahraje) (feed má 1. fotku a počet, další se dopočítají a ověří), parametry deskovek z feedu (Počet hráčů, Min/Max, Délka hry, Věk od, Typ, Jazyk pravidel; Jazyk komponent ručně), vlastní pole ze vzorové deskovky `template_code` (P00668 Heat): přepínače zkopíruje, názvy pro feedy = název hry, parametry Zboží přepočítá, texty vázané na vzor vynechá. Výrobce `manufacturer` (Asmodee), kategorie jako vzor. Po založení Herald přečte produkt zpátky a do PM napíše, co se uložilo a co doplnit. Skryté produkty ze starší verze doplní sám (`BODY_V`).
- `only_categories`: jen tenhle sortiment (teď `DESKOVÉ HRY`) v katalogu i při zakládání.
- Ceny se nastaví při založení, později je Herald nemění (fáze 3 po dohodě slevy s Asmodee: `price.discount_pct`).
- API uživatel potřebuje: produkty (čtení, zápis, zakládání), dostupnosti, objednávky (čtení).

## Hlídání Google Disku

Každou hodinu a půl mezi 9:00 a 22:30 (v 9:00, 12:00, 15:00, 18:00 a 21:00 spolu se synchronizací kalendáře, v 10:30, 13:30, 16:30, 19:30 a 22:30 samostatně - úloha `drive` na cron-job.org: `30 10,13,16,19,22 * * *`) Herald projde ve sdílené složce (`drive_config.json` → `folder_id`) jen složku **aktuálního měsíce v aktuálním roce** (např. `2026 / 10 říjen`; pozná ji podle čísla nebo názvu měsíce) včetně podsložek. Prvních 7 dní v měsíci i předchozí měsíc (`previous_month_days`), i přes přelom roku. Vypnutí: `only_current_year: false` (pak celá složka). Když přibude nový soubor, pošle soukromou zprávu všem z `notify_users` v `drive_config.json` s názvem, podsložkou a odkazem. První běh si jen zapamatuje obsah. Přístup přes servisní účet `herald@hrana-bot.iam.gserviceaccount.com` (secret `GOOGLE_SERVICE_ACCOUNT`) - složku s ním stačí sdílet jako Čtenář.

## Rozpracováno: YouTube Shorts (pozastaveno)

Hotovo: Google Cloud projekt **Hrana-Bot**, zapnuté **YouTube Data API v3**, Google Auth Platform (External, publikováno, scope `youtube.upload`), OAuth klient typu Web application s redirect URI `https://developers.google.com/oauthplayground`.

Zbývá:
1. **Vlastník kanálu** projde OAuth Playground (⚙️ vlastní Client ID/secret, Access type Offline, Force prompt Consent) se scope `https://www.googleapis.com/auth/youtube.upload`, vybere kanál Hrany a předá **refresh token**. (Správce v YouTube Studiu to udělat nemůže - musí to být vlastník, nebo správce značkového účtu.)
2. Do GitHub secrets: `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`.
3. Doprogramovat nahrávání (video s hudbou z `music/free`), do schválení auditu Googlu budou videa soukromá; pak žádost o audit.

Rozpracováno také: **Meta katalog a označování produktů** - firemní portfolio Meta „Hrana Netu“ existuje, ale Kate má jen částečný přístup. **Vlastník** musí v business.facebook.com → Nastavení → Uživatelé → Lidé dát Kate **úplnou kontrolu** nad portfoliem a úplný přístup ke stránce a Instagramu. Pak: Commerce Manager → katalog (datový kanál = feed pro Google `feed-google-merchant-…xml`, denní aktualizace) → ověření domény hrananetu.cz meta tagem v hlavičce webu (Upgates) → obchod a propojení s Instagramem.

Rozpracováno také: **TikTok** - zatím jen průzkum (vyžaduje vývojářský účet, stránky s podmínkami a zásadami na webu, ověření domény a audit; riziko zamítnutí plně automatického zveřejňování).

## Nová objednávka (radost do PM)

`order_notify.py`, stav `orders_seen.json`. Při každé synchronizaci se podívá na nové objednávky v Upgates a ke každé pošle do PM zelenou kartu „🛒 Nová objednávka 2026-xxx · zisk X Kč (tržba bez DPH Y Kč)“. Zisk = cena položek bez DPH minus nákupní cena × kusy (doprava a platba se nepočítají). Bez nákupní ceny je zisk „aspoň“. Údaje o zákazníkovi se neposílají ani neukládají. API uživatel potřebuje čtení Objednávek. Upgates eviduje i prodeje v obchodě: hlásí se jen objednávky s e-mailem zákazníka (pokladna ho nemá) a bez slov z `order_notify_config.json` → `ignore` (pokladna, prodejna). Když žádná z nových objednávek e-mail nemá, pošle jednou přehled kanálů k nastavení. Ruční spuštění: úloha `orders`.

## Puls e-shopu (Analytics + Google Ads + objednávky)

`pulse.py`. Dnešek do aktuální hodiny vs medián 4 minulých stejných dnů v týdnu do stejné hodiny (jeden silný den ho nevychýlí): návštěvy, košíky, zahájené objednávky, nákupy a tržby (GA4), kliknutí a útrata Google Ads (propojení v GA4), lidé na webu, posledních 7 dní (návštěvy a nákupy) teď a zdroje návštěv. Napíše, kde se to zadrhává (málo návštěv / nedávají do košíku / nedokončí pokladnu / jen slabší den). Úloha `pulse` = karta vždy. Při synchronizaci od 13:00 `--alarm` = karta jen při podezřele slabém dni, nejvýš jednou denně (`pulse_state.json`).

## Vyprodané produkty (soldout.py)

Produkt, který je **aspoň 30 dní vyprodaný** (dostupnost „Není skladem“ a zároveň sklad 0), Herald sám skryje z webu. Z webu, Heureky i Googlu zmizí, v Upgates zůstane beze změny. Jakmile ho naskladníš (sklad > 0 nebo jiná dostupnost), Herald ho sám vrátí a e-shop bot pošle obvyklé „opět skladem“.

- Nikdy se neskrývá: Předprodej, Připravujeme, dropship Asmodee a cokoliv v `exclude` v `soldout_config.json` (kódy nebo slova v názvu).
- Produkty, které skryješ ty, Herald nikdy nezobrazí. Když produkt, který skryl Herald, ručně zapneš, nechá ho být.
- Od kdy je vyprodáno: Herald si to pamatuje. U produktů vyprodaných už při spuštění bere poslední prodej za posledních 60 dní (e-shop i prodejna), a když se neprodal, datum založení produktu.
- Úplně první běh nic nemění: pošle do PM přehled a CSV se seznamem, ✅ pod ním automatiku zapne (jen jednou).
- Běží jednou denně od 10:00, nejvýš 100 produktů za den (`max_hide_per_run`), přehled do PM. Ruční spuštění: úloha `soldout`.

## Hlídání marže (margin.py)

Jednou denně (od 12:00, dokud nedoběhne) Herald projde aktivní produkty i varianty a porovná prodejní cenu (i akční) s nákupní, obě s DPH.

- 🔴 pod nákupní cenou, 🟠 marže pod `min_pct` % (10). Marže = (prodej - nákup) / prodej. Věrnostní sleva zákazníka (2 až 6 %) se nepočítá.
- Hlásí do #herald-kontrola s označením lidí: `mention_ids` (Discord ID) a `mention_names` (jméno, Herald ho dohledá na serveru; když ho nenajde, napíše do PM).
- Každý den jen nové problémy, v pondělí přehled všech otevřených + počet produktů bez nákupky (seznam v CSV).
- ✅ pod hlášením = „je to schválně“: ty produkty už nehlásí, dokud se jim nezmění cena nebo nákupka.
- Úplně první běh nic do kanálu neposílá: náhled s CSV do PM, ✅ pod ním hlídání zapne.
- Nastavení `margin_config.json`: `min_pct`, `mention_names`, `mention_ids`, `exclude` (slova v názvu, např. poukaz), `from_hour`, `list_limit`.
- Ruční spuštění: úloha `marze` (projde znovu a vypíše do logu strukturu cen prvních produktů). Stav: `margin_state.json`.

## Vzhled soukromých zpráv (PM)

Všechny zprávy od Heralda do PM chodí jako barevné karty (`preview.dm`): první řádek = nadpis, zbytek = obsah, dole „Herald · služba“. Barva podle služby (`preview.SERVICES`): upozornění červená, Asmodee oranžová, štítky a kategorie tyrkysová, bannery růžová, sociální sítě modrá, newsletter fialová, kontrola šedá, Google Disk žlutá, hotovo zelená, ostatní firemní fialová. Jeden obrázek se zobrazí přímo v kartě.

## Bezpečnostní pojistky

Herald nikdy nezveřejní ani nesmaže hromadně něco jen proto, že se data na chvíli načetla špatně. Když data vypadají podezřele, **zastaví se, nic neudělá** a do #herald-kontrola pošle „🛑 Herald se zastavil pro jistotu“ s důvodem:

| Situace | Pojistka |
|---|---|
| Kalendář se načte neúplně (zmizí víc než 30 % budoucích akcí, aspoň 6) | Discord události se nemažou |
| Měsíční program: akcí ubude o polovinu nebo víc než 10 změn naráz | žádný komentář se změnami |
| Feed e-shopu má o 30 % produktů méně než minule | nic se neoznamuje ani neukládá |
| Víc než 25 novinek nebo 15 naskladnění najednou (`max_new_per_run`, `max_restock_per_run` v shop_config.json) | nic se neoznamuje, jen se zapíše stav |
| List sezóny v tabulce ligy neexistuje (Google by potichu vrátil jiný list) | souhrn ani síň slávy se neposílají |
| Síň slávy | jen pro finále od 5. 10. 2026 a nejvýš 30 dní stará; **vždy jen po schválení ✅ v #herald-kontrola** |
| Týdenní souhrn / plakát | jen v neděli 16:30-21:00 (náhled 14:00-16:30), jednou týdně, **nikdy bez náhledu odeslaného aspoň hodinu předem** |
| Měsíční program | jen poslední den v měsíci 16:30-21:00 (náhled 14:00-16:30), jednou, **nikdy bez náhledu odeslaného aspoň hodinu předem** |
| Ranní oznámení | jen 9:00-12:00, jednou denně v každém kanálu, nikdy u turnaje, který začíná dřív než za hodinu |
| Týdenní video (Reel) | jen v pondělí 14:30-20:00 (náhled 12:00-14:30), jednou týdně, **nikdy bez náhledu odeslaného aspoň hodinu předem** |

Když jde o skutečnou hromadnou změnu (např. opravdu zrušíte celý týden akcí), udělejte ji ručně - Herald se k ní nepřidá.

## Když něco nefunguje

Při každém neúspěšném běhu přijde zpráva do **#herald-kontrola** s odkazem na log (a od GitHubu také **e-mail**). Otevřete běh v Actions → krok **Spuštění bota** → sjeďte na konec logu.

| Hláška v logu | Příčina | Řešení |
|---|---|---|
| `JSONDecodeError … Expecting ',' delimiter` | Chybí čárka v souboru `.json` | Na uvedeném řádku (nebo o řádek výš) doplnit čárku |
| `JSONDecodeError … Expecting property name` | Čárka navíc za poslední položkou | Smazat čárku před `}` |
| `JSONDecodeError … Invalid control character` | Enter uvnitř textu | Text dát na jeden řádek, nové řádky psát jako `\n` |
| `Chyba Discord API 403` | Herald nemá oprávnění v kanálu | Kanálu přidat členovi Herald: Zobrazit kanál, Posílat zprávy, Vkládat odkazy |
| `Chyba Discord API 401` | Neplatný token bota | Nový token v Discord Developer Portal → přepsat secret `DISCORD_BOT_TOKEN` |
| `Chyba Meta API 400 … does not exist` | Špatné `FB_PAGE_ID` nebo klíč | Ověřit v Graph API Explorer (dotaz `me` s klíčem stránky) |
| `Chyba Meta API … OAuth` / `token` / `session` | Klíč k Facebooku přestal platit | Obnovit klíč (viz níže) |
| `cannot open resource` | Chybí písmo ve složce `fonts` | Nahrát chybějící soubor do `fonts/` |
| `! Story … se nepovedla` | Story neprošla, zbytek ano | Většinou jednorázové, jinak zkontrolovat klíč |
| `Nepodařilo se načíst Master Sheet` | Hlavní tabulka lig není dostupná | Zkontrolovat, že je tabulka sdílená „kdokoli s odkazem“ |
| `list „…“ nenalezen` | Tabulka ligy nemá list s názvem aktuální sezóny | Pojmenovat list přesně jako v listu Sezony (např. „Podzim 2026“) |
| `! Komentář … se nepovedl` | Komentář neprošel | Zkontrolovat, že klíč má oprávnění `pages_manage_engagement` a `instagram_manage_comments` |

**Plánované běhy se nespouštějí** (v Actions jsou jen „Manually run“): GitHub je u nových repozitářů rozjíždí se zpožděním. Pokud to trvá déle než den, zkontrolujte, že je `main.yml` ve složce `.github/workflows/`.

---

## Obnovení klíče k Facebooku a Instagramu

Klíč sám nevyprší, ale Facebook ho zneplatní, když si změníte heslo, odeberete aplikaci Herald nebo přestanete být správkyní stránky.

1. **developers.facebook.com → Tools → Graph API Explorer**, aplikace **Herald**, **Get User Access Token**.
2. Oprávnění (všech 9):
   `pages_show_list`, `pages_read_engagement`, `pages_manage_posts`, `pages_manage_engagement`, `pages_read_user_content`, `business_management`, `instagram_basic`, `instagram_content_publish`, `instagram_manage_comments`
3. **Generate Access Token** → v okně Facebooku zaškrtnout stránku **i Instagram** → povolit.
4. Modré **„i“** u klíče → **Open in Access Token Tool** → **Extend Access Token** → zkopírovat dlouhý klíč.
5. Zpět v Exploreru vložit dlouhý klíč do pole **Access Token**, dotaz:
   `me/accounts?fields=id,name,access_token,instagram_business_account` → **Submit**.
6. Zkopírovat `access_token` u stránky Hrana Netu → GitHub **Settings → Secrets and variables → Actions → FB_PAGE_TOKEN → tužka → Update secret**.

Když Explorer některé oprávnění nenabízí nebo hlásí „Invalid Scopes“, je potřeba ho nejdřív přidat v aplikaci: **Případy použití → Customize → Permissions and features → Add**.

---

## Secrets (GitHub → Settings → Secrets and variables → Actions)

| Secret | Co to je |
|---|---|
| `DISCORD_BOT_TOKEN` | Token bota Herald (Discord Developer Portal → Bot) |
| `DISCORD_GUILD_ID` | ID Discord serveru |
| `ICS_URL` | Adresa kalendáře ligy ve formátu iCal |
| `SHOP_FEED_URL` | Adresa produktového feedu e-shopu |
| `FB_PAGE_ID` | ID Facebook stránky Hrana Netu |
| `FB_PAGE_TOKEN` | Klíč stránky (Facebook + Instagram) |
| `IG_USER_ID` | ID instagramového účtu |

🔒 **Tokeny a klíče nikdy nikomu neposílejte** a nevkládejte je do souborů ani do chatu. Patří jen do secretů.

---

## Kolik to stojí

**Nic.** GitHub dává k soukromým repozitářům 2 000 minut běhu měsíčně zdarma a Herald spotřebuje zhruba čtvrtinu až třetinu. Discord, Facebook, Instagram ani Google Kalendář si za tohle použití nic neúčtují. Spotřebu najdete na GitHubu: profil → **Settings → Billing and licensing → Usage**.

---

## Co Herald nedělá (záměrně)

- **Nepřipíná příspěvky** - to děláte ručně.
- **Nesdílí do Facebook skupin** - Facebook to aplikacím v roce 2024 zakázal, sdílení je jen ruční.
- **Nemění obrázky po zveřejnění** - změny v měsíčním programu jdou do komentářů.
