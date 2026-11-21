<?php
/**
 * Router for PHP's built-in development server (START-NANDI.bat). Not used on Hostinger.
 * It hides private files and only lets one PHP file run: api/nandi-voice.php
 */
declare(strict_types=1);

$uri = isset($_SERVER['REQUEST_URI']) ? (string)$_SERVER['REQUEST_URI'] : '/';
$path = rawurldecode((string)parse_url($uri, PHP_URL_PATH));
if ($path === '' || $path[0] !== '/') {
    $path = '/' . $path;
}
if (strpos($path, "\0") !== false || strpos($path, '..') !== false) {
    http_response_code(400);
    echo 'Bad request';
    return true;
}
$blocked = preg_match('#(^|/)\.#', $path) === 1
    || preg_match('#\.(env|ini|log|md|bak|zip|sql|py|bat|ps1|key)$#i', $path) === 1
    || preg_match('#^/(tests|tools|private|php-config)(/|$)#i', $path) === 1
    || (preg_match('#\.php$#i', $path) === 1 && $path !== '/api/nandi-voice.php');
if ($blocked) {
    http_response_code(404);
    header('Content-Type: text/plain; charset=utf-8');
    echo 'Not found';
    return true;
}

// The same protections that .htaccess adds on Hostinger (upgrade-insecure-requests is left out because local testing uses http).
header('X-Content-Type-Options: nosniff');
header('X-Frame-Options: SAMEORIGIN');
header('Referrer-Policy: strict-origin-when-cross-origin');
header('Permissions-Policy: camera=(), geolocation=(), payment=(), usb=(), microphone=(self)');
header("Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com data:; img-src 'self' data:; frame-src https://www.google.com; connect-src 'self'; media-src blob:; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'self'");

return false;
