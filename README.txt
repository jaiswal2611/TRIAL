This folder holds two things that PHP needs on Windows. Neither contains a secret.

1) cacert.pem  (you add this once)
   PHP on Windows does not know which websites to trust until you give it a certificate list.
   - Open https://curl.se/ca/cacert.pem in Chrome
   - Press Ctrl+S and save it into this folder with the exact name:  cacert.pem

2) php-local.ini  (created automatically each time you run START-NANDI.bat; do not edit)
   php-errors.log (PHP writes problems here; it never contains your key or what people typed)
