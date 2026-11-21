# Nandi voice (ElevenLabs): report of changes, tests and limits

## Short version
The voice code is written and the browser side is tested in a real browser against a simulated server. **The PHP file and the real ElevenLabs call have not been run by me**, because my environment has no PHP and no access to your ElevenLabs account. The set-up is built so that **your own computer checks the PHP syntax** every time you start it, and so that you can confirm both voices in about five minutes using the voice test page.

## Important correction
Your instructions mention an "existing PHP endpoint `/api/nandi-voice.php`". **No such file existed in the project I was given** (the site was static HTML/JavaScript). I created it, following the security rules you listed.

## What changed
| File | Change |
|---|---|
| `public_html/api/nandi-voice.php` | **New.** Server-side voice proxy. Browser sends only `lang` (hi or en) and `text`. Hindi uses voice `3AMU7jXQuQa3oRvRqUmb`, English uses `1U02n4nD6AdIZ9CjF053`. The browser cannot pick any other voice. Key read from environment variable `ELEVENLABS_API_KEY` |
| `public_html/assets/nandi.js` (built into the 4 pages) | Spoken replies now try ElevenLabs first through the endpoint, then fall back to the browser's own voice on any problem. Stops audio when Nandi closes, resets, or voice is turned off. Stops asking the server for the rest of the visit when the key is missing or PHP is absent |
| `public_html/router.php` | **New.** Local server rules: hides `.env`, dotfiles, tests, and every PHP file except the voice endpoint |
| `public_html/voice-test.html` | **New.** Local test page (check set-up, play each voice, test the browser voice). Blocked on the live site by `.htaccess`; delete it before publishing |
| `public_html/.htaccess` | One security-policy change: `media-src 'none'` became `media-src blob:`, which is required to play the audio. Nothing else loosened. Also blocks `router.php` and `voice-test.html` on the live site |
| `START-NANDI.bat`, `SETUP-KEY.bat`, `setup-key.ps1` | **New.** Windows launcher and a hidden-input key saver |
| `.env.example`, `.gitignore`, `php-config/README.txt`, `private/elevenlabs-key.example.php` | **New.** Placeholders and notes only. No real key anywhere |
| Guides | `WINDOWS-SETUP-GUIDE.md`, `TESTING-CHECKLIST.md`, this report |
No pages, images, animations or Nandi features were removed. The pages' design was not changed.

## How the API key is protected
- Never in HTML, JavaScript or any file inside `public_html`. The browser never receives it.
- Lives in `.env` next to `START-NANDI.bat` (outside `public_html`), written by a hidden-input prompt. The launcher puts it in the PHP process's environment and never prints it. The local server serves only `public_html`.
- The PHP file never logs the key or the spoken text. Errors log only a number such as the HTTP status.
- Server-side safeguards: same-website requests only; JSON only; 4 KB request limit; 500-character text limit; only `hi`/`en`; UTF-8 and control-character cleaning; 20 requests per visitor per 10 minutes; 20,000 characters per day for the whole site; fixed lists for the ElevenLabs host and model; certificate checking on; no redirects; visitor addresses stored only as hashes.

## Tests actually run (all pass)
| Test | Result |
|---|---|
| JavaScript syntax: 4 pages' scripts and 3 asset files (32 scripts) | OK |
| Nandi voice behaviour in Chromium with a **simulated** server (`tests/voice_frontend_test.py`) | **25 of 25** |
| Static review of PHP, batch files, key handling (`tests/check_voice_static.py`) | **30 of 30** |
| Existing website checks (`tests/check_site.py`, served with the real security headers) | **47 of 47** (no regressions, no policy violations) |

What the 25 browser tests prove: English requests ask for `en` and Hindi requests ask for `hi`; the request contains only `lang` and `text` (no voice ID, no key); audio that comes back is played and the browser voice is not used; a missing key (503), rate limit (429), server failure (502), network failure, a host without PHP (404) and a reply that is not audio all end in the browser voice; after "not configured" it stops calling the server; closing Nandi stops playing audio; voice off makes no calls; the phone-sized screen works; opening the pages as plain files (no PHP) uses the browser voice; no JavaScript or policy errors on any page.

Name of the checks that look at the PHP file only **read** it. They do not run it.

## NOT tested (please test: see TESTING-CHECKLIST.md)
1. **PHP syntax and execution.** Not run. Mitigation: `START-NANDI.bat` runs `php -l` on both PHP files on your computer and stops if there is a problem. A rough lexer check (balanced braces and no lexing errors) was the only automated look.
2. **The real ElevenLabs request, and the two voices.** Not called, not heard. The request shape (address, `xi-api-key` header, `eleven_multilingual_v2`, `output_format=mp3_44100_64`) follows ElevenLabs' published documentation, which I read, but it is unproven against your account. Whether each voice ID is accessible to your account (voices must be in **My Voices**) is unknown.
3. **Windows specifics:** the `.bat` files actually running, PHP's cURL certificate set-up with `cacert.pem`, the `php-local.ini` the launcher writes, Chrome opening. Written with care, not executed.
4. **Hindi pronunciation quality**, and whether `eleven_multilingual_v2` suits your Hindi voice. Try `eleven_flash_v2_5` in `.env` if you want faster replies.
5. **Real phones.** Mobile was tested only as a small browser window. iPhone/Safari audio rules were not tested; the fallback exists for blocked audio.
6. PHP's built-in server adding the security headers to *static* files was not verified.

## Known limitations
- Costs: each spoken reply uses ElevenLabs characters. Set a monthly limit in your ElevenLabs account.
- Only scripted Nandi answers are spoken. The longest is 273 characters, so nothing is cut today.
- The rate limiter keeps counters in the computer's temporary folder. On shared hosting that may be cleared or shared; the per-request caps still apply.
- Live hosting needs PHP with cURL and a safe place for the key outside `public_html` (see `private/elevenlabs-key.example.php`). Hostinger's current settings were not checked.
- Opening the HTML files by double-clicking (no server) cannot reach PHP, so only the browser voice works. Use START-NANDI.bat.
- This is a careful implementation, not an independent security audit.
