# Nandi voice: testing checklist

Tick each line yourself. Items marked **YOU** can only be tested by you, because they need your ElevenLabs account and your ears.

## A. Set-up (YOU)
- [ ] PHP installed; `C:\php\php.exe -v` prints a version
- [ ] `php-config\cacert.pem` saved
- [ ] SETUP-KEY.bat finished with "Saved"
- [ ] START-NANDI.bat shows `[OK] PHP found`, `[OK] ElevenLabs key found`, and "No syntax errors detected" twice
- [ ] Chrome opens `http://localhost:8000/`

## B. Voice test page: http://localhost:8000/voice-test.html (YOU)
- [ ] Check set-up shows key_found, curl_available, ca_bundle_found all true
- [ ] **Hindi voice** plays and sounds like the Hindi voice you chose (ID ending ...RqUmb)
- [ ] **English voice** plays and sounds like the English voice you chose (ID ending ...jF053)
- [ ] The two voices are different from each other
- [ ] Browser Hindi / Browser English buttons make a (robotic) sound

## C. Nandi (YOU)
- [ ] Speaker icon on: English question, English ElevenLabs voice reads the answer
- [ ] Switch to Hindi: Hindi question, Hindi ElevenLabs voice reads the answer
- [ ] Switch back to English: English voice again (it follows the page language)
- [ ] Close Nandi while speaking: sound stops
- [ ] New chat button: sound stops and a fresh greeting appears
- [ ] Speaker icon off: Nandi stays silent

## D. Failure behaviour (YOU)
- [ ] Rename `.env` to `.env.off`, restart: Nandi still works, speaks with the plain browser voice, and the test page shows key_found false
- [ ] Turn off your internet, ask Nandi something: the answer still appears and the browser voice speaks
- [ ] Put `.env` back, restart: ElevenLabs works again

## E. Whole website (YOU, 5 minutes)
- [ ] Home, Treatments, Smile Studio and Explore all open and look normal
- [ ] Hindi/English button works on all four pages
- [ ] Booking form, treatment finder, greeting cards and the brushing game still work
- [ ] On your phone (same Wi-Fi) the site is not part of this test; phone behaviour was tested only by browser emulation

## F. Already tested by the assistant (results in VOICE-REPORT.md)
- [x] JavaScript syntax, all pages
- [x] 25 browser tests of Nandi's voice behaviour with a simulated server (success, missing key, rate limit, failures, fallback, mobile size)
- [x] 30 static checks of the PHP file, batch files and key handling
- [x] 47 existing website checks still pass
- [ ] **Not tested by the assistant:** PHP syntax and execution (no PHP in its environment), the real ElevenLabs call, real audio of the two voices, Windows batch files running, Chrome on Windows. START-NANDI.bat makes PHP check its own syntax on your computer.
