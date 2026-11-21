# Security and reliability review: Jaiswal Dental Clinic website

Reviewed: the four pages (`index.html`, `treatments.html`, `studio.html`, `explore.html`), `assets/fx.js`, `assets/nandi.js`, `assets/nandi-brain.js`, `.htaccess`, `robots.txt`, `sitemap.xml`.
This is a review by the assistant that built the site. It is not an independent audit or a certification. See "Before real launch" at the end.

## What this website is (and is not)
- A **static site**: HTML, CSS and JavaScript files that run in the visitor's browser. It has **no server code, no database, no login, no OTP, no admin area and no API keys**.
- Appointment requests leave the site only as a **WhatsApp message the visitor chooses to send** (to 99283 00175). Nothing is stored by the site.
- Because of that, most items in the long "backend / database / OTP / admin" security brief **do not apply today**. They are listed below as "Not applicable" so nobody assumes they exist. Building them would add risk (stored patient data, DPDP Act duties) and should be a separate, deliberate project.

## Evidence of tests actually run
`tests/check_site.py` (kept outside `public_html`, so it is never published) served the site over HTTP **with the exact headers from `.htaccess`** (including the Content Security Policy) and checked all four pages in a real Chromium browser. Result of the last run (`tests/last-run.txt`): **47 checks, 47 passed, 0 failed**. They cover: no JavaScript errors, no CSP violations, current footer text, internal links and anchors, `rel=noopener` on external links, no unexpected third-party scripts, Nandi's emergency answer (call 99283 00175 / 112, no diagnosis), Nandi quoting no prices, markup typed into Nandi or the greeting form shown as text, 64 greeting occasions with descriptions and messages, the treatment finder's WhatsApp link, the Nandi-to-booking-form hand-off, no horizontal scroll on a phone, and no API keys or passwords in shipped files.
Not tested: real devices, screen readers, Hostinger's live servers, the live Google Maps and Fonts content (the test machine had no internet).

## Findings and what was done
| # | Finding | Severity | Status |
|---|---------|----------|--------|
| 1 | No security headers or HTTPS rule | Medium | Fixed in `.htaccess`: HTTPS redirect, nosniff, frame protection, referrer policy, permissions policy, CSP |
| 2 | Chat history was stored as HTML in `sessionStorage` and re-inserted as HTML | Low | Fixed: Nandi now stores and shows plain text only |
| 3 | Optional AI server hook did not exist | Info | Added `NANDI_ENDPOINT` (off by default). A reply is accepted only if it is short text plus up to 3 buttons whose links match a strict allow-list (phone, WhatsApp 91-number, clinic maps, own pages). Any failure falls back to the local brain |
| 4 | CSP must allow `'unsafe-inline'` scripts because each page contains inline JavaScript | Medium (residual) | **Open.** Fix later by moving inline scripts to files, then removing `'unsafe-inline'` |
| 5 | Hidden/backup files could be served | Low | Fixed in `.htaccess` (denies dotfiles, `.bak`, `.zip`, `.sql`, etc.) |
| 6 | Third parties are used: Google Fonts, Google Maps embed, WhatsApp links | Low | Accepted. Listed in the CSP. They see the visitor's IP like any website they load |
| 7 | No privacy notice page | Medium (legal) | **Open.** Recommended before launch; needs review by a qualified Indian lawyer (DPDP Act 2023). No legal compliance is claimed |

No secrets, credentials or API keys exist in any file. No `eval`. User text is inserted into the page only through `textContent`, or HTML-escaped values.

## Nandi safety rules (as built)
- Answers only from the editable list in `assets/nandi-brain.js`; unknown topics go to the clinic team.
- No diagnosis, no prescriptions, no prices. Bleeding that will not stop, spreading swelling, fever or trouble breathing: tells the visitor to call 99283 00175 the same day, or go to hospital / call 112.
- Chat is kept only in the visitor's own tab (`sessionStorage`) and cleared with the New chat button. Only the language, sound and voice choices use `localStorage`.
- It has no tools: it cannot read files, run code or reach clinic records, because none are connected.

## Not applicable today (do not exist in this site)
Database encryption and access rules, automated database backups, OTP checks, owner/staff accounts and MFA, audit logs, an admin portal, an `/api/nandi` server, four separate server environments. If any of these are added later, they need their own design, testing and an independent review first.

## Backups and rollback for a static site
- Keep every released ZIP (for example `jaiswal-dental-website-2026-11-19.zip`) in two places: the clinic's Google Drive and an offline copy.
- Turn on Hostinger's automatic backups and test one restore into a spare folder.
- **Rollback:** re-upload the previous ZIP's `public_html` contents over the live files. Test by doing this once on a test subdomain.
- Do not claim backups work until a restore has been tried.

## Hosting checklist (the real risk is the accounts, not the code)
1. Strong, unique password and **two-step login** on the Hostinger account, the domain registrar, the clinic Gmail and the Google Business Profile.
2. Turn on Hostinger SSL, then check every page loads on https. **Only then** remove the `#` before the `Strict-Transport-Security` line in `.htaccess`.
3. Enable Hostinger's firewall / DDoS protection (or put the domain behind Cloudflare's free plan).
4. Keep FTP/SSH passwords private; delete accounts of anyone who no longer works on the site.
5. After upload, open https://securityheaders.com and https://observatory.mozilla.org for the live domain and fix anything they flag.

## Environment variables
None needed. The only setting is the optional `window.NANDI_ENDPOINT` (empty by default).

## Unresolved risks
- CSP still allows inline scripts (finding 4).
- No privacy notice (finding 7).
- Medical wording in Nandi, the aftercare guides and the finder has not been reviewed by Dr. Jaiswal.
- Ratings and review quotes come from Practo, Justdial and Google as of November 2026 and can go out of date.
- Hindi text has not been proof-read by a native speaker.

## Before real launch
Have a **qualified independent security professional** review the live, deployed site, and a lawyer review the privacy notice, before any real patient records or a server-side feature are added. The clinic owner should approve the launch.

## Addendum: Nandi voice (ElevenLabs)
- New file `api/nandi-voice.php` is the only PHP in the site. It holds no secrets; the key comes from the server environment or a private file outside `public_html`.
- Only two fixed voices can be used; requests are same-origin, size-limited, validated and rate-limited.
- One CSP change: `media-src blob:` (was `'none'`), needed to play the returned audio.
- Not tested by the assistant: PHP execution and the real ElevenLabs call (see `VOICE-REPORT.md`).
- `router.php` and `voice-test.html` are local-testing files and are blocked by `.htaccess` on the live site; delete `voice-test.html` before publishing.
