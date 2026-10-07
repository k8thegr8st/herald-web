# herald-web

Veřejný web aplikace **Herald** (automatizace Hrana Store). Běží zdarma na GitHub Pages:
**https://k8thegr8st.github.io/herald-web/**

## Proč existuje

Web byl založen kvůli **týdennímu videu (Reel)**, aby ho Herald mohl sám zveřejňovat na **TikTok** a na **YouTube Shorts**.
Obě platformy chtějí, aby aplikace měla veřejný web s podmínkami použití, zásadami ochrany soukromí, ověřenou doménou
a adresou, kam se člověk vrátí po přihlášení. Jinak aplikaci Herald nepovolí zveřejňovat videa.

- Facebook a Instagram tento web nepotřebují (Reel tam jde přes Meta, už funguje).
- Dokud TikTok a YouTube nejsou dokončené, web jen leží a nic nedělá. **Nerušit**, bez něj se dokončit nedají.
- Web neslouží zákazníkům. Samotný Herald (bot) je v repozitáři **hrana-bot**, tady žádný kód bota není.

## Co tu je

| Soubor | Adresa | K čemu je |
|---|---|---|
| `index.html` | …/herald-web/ | Úvodní stránka: co je Herald a kdo ho provozuje (Hrana Stolu s.r.o.). Odkaz „web aplikace“ v TikTok/Google formulářích. |
| `terms.html` | …/herald-web/terms.html | Terms of Service, podmínky použití aplikace (anglicky, jak chce TikTok). |
| `privacy.html` | …/herald-web/privacy.html | Privacy Policy, jaká data Herald zpracovává (anglicky). |
| `callback.html` | …/herald-web/callback.html | Stránka, kam TikTok/Google vrátí po přihlášení. Ukáže jednorázový kód (`code`), který se pak použije pro získání přístupu. Zadává se jako **Redirect URI**. |
| `style.css` | | Vzhled všech stránek (barvy Hrany). |
| `tiktok….txt` | …/herald-web/tiktok….txt | Ověřovací soubor od TikToku, že web patří nám. **Nemazat**, jinak TikTok ověření zruší. |

## Kde se adresy používají

- **TikTok for Developers** (aplikace Herald): Web/Desktop URL, Terms of Service URL, Privacy Policy URL, Redirect URI (`callback.html`), ověření domény (`.txt` soubor).
- **Google Cloud – projekt Hrana-Bot** (YouTube): stránka aplikace, podmínky, soukromí v Google Auth Platform → Branding.

Když adresu změníte nebo stránku smažete, musí se změnit i tam, jinak přestane fungovat přihlášení.

## Úpravy

- Texty se mění přímo v `.html` souborech (Add file → Upload files, přepsat). Web se aktualizuje do pár minut.
- Nastavení publikování: Settings → Pages → Deploy from a branch → `main` / `(root)`. Soubory musí být přímo v kořeni repozitáře, ne ve složce.
- Česká verze pravidel pro zákazníky je v obchodních podmínkách a ochraně osobních údajů na hrananetu.cz (článek „Aplikace Herald“). Při změně jednoho je dobré upravit i druhé.

## Stav (říjen 2026)

- TikTok: web ověřený, aplikace čeká na dokončení (zamčený TikTok profil Hrany).
- YouTube: čeká na vlastníka kanálu (refresh token).
