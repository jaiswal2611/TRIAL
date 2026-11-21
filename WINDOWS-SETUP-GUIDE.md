# Nandi voice on your Windows computer: simple setup guide

You do not need Hostinger, a domain or any public website for this. Everything runs on your own computer and stays private.

**What you will do:** install PHP once, add one certificate file, save your ElevenLabs key privately, double-click one file, and talk to Nandi in Chrome.

## Step 1. Extract the ZIP
Right-click `jaiswal-dental-website.zip`, choose **Extract All**, and pick a simple place such as `C:\Users\YourName\Desktop`. You will get a folder called `jaiswal-dental-website`. Open it. You should see `START-NANDI.bat`, `SETUP-KEY.bat`, a folder `public_html`, and others.

## Step 2. Install PHP (one time)
1. Open https://windows.php.net/download/ in Chrome.
2. Under the newest PHP 8 version (8.2 or newer), click **Zip** next to **Non Thread Safe, x64**.
3. Create the folder `C:\php`, and extract the zip into it, so that the file `C:\php\php.exe` exists.
4. Check it: press the Windows key, type `cmd`, press Enter, type `C:\php\php.exe -v` and press Enter. It should print a PHP version.

## Step 3. Add the certificate file (one time)
PHP needs this to connect to ElevenLabs safely.
1. Open https://curl.se/ca/cacert.pem in Chrome.
2. Press **Ctrl+S** and save it into the folder `jaiswal-dental-website\php-config\` with the exact name `cacert.pem`.

## Step 4. Save your ElevenLabs key privately
1. Double-click **SETUP-KEY.bat**.
2. Paste your ElevenLabs API key and press Enter. Nothing shows while you type or paste, and that is normal.
3. It saves the key in a private file called `.env`, outside the website folder. **Never paste your key into any website file, chat or email.**

## Step 5. Start Nandi
1. Double-click **START-NANDI.bat**. A black window opens and shows checks. It should say `[OK] PHP found`, `[OK] ElevenLabs key found` and `No syntax errors detected` for two PHP files.
2. Chrome opens the website at `http://localhost:8000/`. Keep the black window open while you test. Close it to stop.

## Step 6. Test the voices
**First, the test page:** go to `http://localhost:8000/voice-test.html`.
1. Press **Check set-up**. You want `key_found: true`, `curl_available: true`, `ca_bundle_found: true`.
2. Press **Play Hindi voice**. You should hear the Hindi ElevenLabs voice say the Nandi greeting.
3. Press **Play English voice**. You should hear the English ElevenLabs voice.

**Then, Nandi herself (he):**
1. On the home page, click **Chat with Nandi**.
2. In Nandi's header, click the **speaker icon** to turn spoken replies on.
3. Ask: `What are your timings today?` You should hear the English voice read the answer.
4. Click the language button at the top (**हिन्दी**), then ask in Hindi: `क्लिनिक कहाँ है`. You should hear the Hindi voice.

## If something does not work
| What you see | What it means and what to do |
|---|---|
| Black window says PHP was not found | Do Step 2 again. `C:\php\php.exe` must exist |
| `[!] No ElevenLabs key yet` | Run SETUP-KEY.bat, then START-NANDI.bat again |
| Test page: `key_found false` | The `.env` file is missing or the key was not saved. Run SETUP-KEY.bat |
| Test page: `curl_available false` | PHP could not load its connection part. Make sure you extracted the full PHP zip to `C:\php` (the `ext` folder must be there) |
| Test page: `ca_bundle_found false`, or error `voice_unavailable` | Do Step 3. Then open `php-config\php-errors.log` and look for "cURL error 60" (certificate problem) |
| Error code `voice_unavailable` and the log says HTTP 401 | ElevenLabs refused the key. Create a new key in your ElevenLabs account and run SETUP-KEY.bat again |
| Log says HTTP 404 or "unexpected reply" | Make sure both voices are added to **My Voices** in your ElevenLabs account, and the key is allowed to use Text to Speech |
| Error code `rate_limited` | The safety limit (20 voice requests per 10 minutes) was reached. Wait ten minutes |
| You hear a robotic voice instead | That is the browser fallback. It means ElevenLabs was not available. Check the voice test page for the reason. For Hindi, Windows may need the Hindi language pack to be audible |
| Nandi is silent | Make sure the speaker icon in Nandi's header is on, your computer volume is up, and click anywhere on the page once (Chrome allows sound after you interact) |
| Port busy | The black window picks the next free port and shows it. Use the address it prints |

## Keeping it safe
- The key lives only in `.env` (and in the black window's memory while running). Nobody on the website can read it.
- Set a **monthly spending limit** in your ElevenLabs account. The website also stops after 20,000 characters a day.
- If you ever think the key was exposed, delete it in ElevenLabs and make a new one.
- **Delete `public_html\voice-test.html` before you publish the website.**
- When you publish on Hostinger, the key is stored differently (see `private\elevenlabs-key.example.php`). Ask before you publish.
