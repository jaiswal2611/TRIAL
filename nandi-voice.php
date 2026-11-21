<?php
/**
 * Nandi voice proxy for Jaiswal Dental Clinic.
 *
 * The browser sends only {"lang":"hi"|"en","text":"..."} to this file. This file adds the
 * ElevenLabs API key on the server side and returns MP3 audio. The key is never sent to the
 * browser and is never written into any website file.
 *
 * Where the key is read from (first one found wins):
 *   1. the environment variable ELEVENLABS_API_KEY  (local testing: set by START-NANDI.bat from the private .env file)
 *   2. a web-server variable of the same name
 *   3. a private file OUTSIDE the public website folder: <project>/private/elevenlabs-key.php  (for shared hosting)
 */
declare(strict_types=1);

@ini_set('display_errors', '0');
@ini_set('html_errors', '0');

// Only these two voices can ever be used. The browser cannot choose a voice ID.
const NANDI_VOICES = ['hi' => '3AMU7jXQuQa3oRvRqUmb', 'en' => '1U02n4nD6AdIZ9CjF053'];
const NANDI_MAX_TEXT_CHARS = 500;          // longest text accepted per request
const NANDI_MAX_BODY_BYTES = 4096;         // largest request body accepted
const NANDI_RATE_REQUESTS = 20;            // requests allowed per visitor per window
const NANDI_RATE_WINDOW_SECONDS = 600;     // window length (10 minutes)
const NANDI_DAILY_CHAR_LIMIT = 20000;      // total characters per day for the whole site (cost guard)
const NANDI_API_HOSTS = ['api.elevenlabs.io', 'api.us.elevenlabs.io', 'api.eu.residency.elevenlabs.io', 'api.in.residency.elevenlabs.io', 'api.sg.residency.elevenlabs.io'];
const NANDI_MODELS = ['eleven_multilingual_v2', 'eleven_flash_v2_5', 'eleven_turbo_v2_5'];

function nandi_fail(int $status, string $code, string $message, array $extraHeaders = []): void
{
    if (!headers_sent()) {
        http_response_code($status);
        header('Content-Type: application/json; charset=utf-8');
        header('Cache-Control: no-store');
        header('X-Content-Type-Options: nosniff');
        foreach ($extraHeaders as $line) {
            header($line);
        }
    }
    echo json_encode(['error' => $message, 'code' => $code]);
    exit;
}

function nandi_allowed_origins(): array
{
    $raw = getenv('NANDI_ALLOWED_ORIGINS');
    if (!is_string($raw) || $raw === '') {
        return [];
    }
    $out = [];
    foreach (explode(',', $raw) as $origin) {
        $origin = strtolower(rtrim(trim($origin), '/'));
        if (preg_match('#^https?://[a-z0-9.\-]+(:[0-9]{1,5})?$#', $origin) === 1) {
            $out[] = $origin;
        }
    }
    return $out;
}

/** Accepts only requests that come from this same website. */
function nandi_same_origin(): bool
{
    $fetchSite = isset($_SERVER['HTTP_SEC_FETCH_SITE']) ? strtolower((string)$_SERVER['HTTP_SEC_FETCH_SITE']) : '';
    if ($fetchSite !== '' && $fetchSite !== 'same-origin' && $fetchSite !== 'none') {
        return false;
    }
    $origin = isset($_SERVER['HTTP_ORIGIN']) ? trim((string)$_SERVER['HTTP_ORIGIN']) : '';
    if ($origin === '') {
        return $fetchSite === 'same-origin';
    }
    $parts = parse_url($origin);
    if (!is_array($parts) || empty($parts['host'])) {
        return false;
    }
    $originHost = strtolower((string)$parts['host']) . (isset($parts['port']) ? ':' . $parts['port'] : '');
    $host = strtolower((string)($_SERVER['HTTP_HOST'] ?? ''));
    if ($host !== '' && hash_equals($host, $originHost)) {
        return true;
    }
    return in_array(strtolower(rtrim($origin, '/')), nandi_allowed_origins(), true);
}

function nandi_api_key(): string
{
    $key = getenv('ELEVENLABS_API_KEY');
    if (!is_string($key) || $key === '') {
        $key = isset($_SERVER['ELEVENLABS_API_KEY']) ? (string)$_SERVER['ELEVENLABS_API_KEY'] : '';
    }
    if ($key === '') {
        $file = dirname(__DIR__, 2) . DIRECTORY_SEPARATOR . 'private' . DIRECTORY_SEPARATOR . 'elevenlabs-key.php';
        if (is_file($file)) {
            $value = include $file;
            if (is_string($value)) {
                $key = $value;
            }
        }
    }
    $key = trim($key);
    return preg_match('/^[A-Za-z0-9_\-]{16,200}$/', $key) === 1 ? $key : '';
}

/** Reads a small JSON counter file under an exclusive lock, lets $modify change it, and saves it if $modify returns true. */
function nandi_counter(string $file, callable $modify): bool
{
    $handle = @fopen($file, 'c+');
    if ($handle === false) {
        return true; // cannot store limits: stay available, the per-request size caps still apply
    }
    try {
        if (!flock($handle, LOCK_EX)) {
            return true;
        }
        $raw = stream_get_contents($handle);
        $data = json_decode(is_string($raw) && $raw !== '' ? $raw : '{}', true);
        if (!is_array($data)) {
            $data = [];
        }
        $allowed = $modify($data);
        if ($allowed) {
            ftruncate($handle, 0);
            rewind($handle);
            fwrite($handle, (string)json_encode($data));
        }
        flock($handle, LOCK_UN);
        return $allowed;
    } finally {
        fclose($handle);
    }
}

function nandi_rate_limit_ok(int $chars): bool
{
    $dir = rtrim(sys_get_temp_dir(), '/\\') . DIRECTORY_SEPARATOR . 'nandi-voice-limits';
    if (!is_dir($dir) && !@mkdir($dir, 0700, true) && !is_dir($dir)) {
        return true;
    }
    if (random_int(1, 50) === 1) {
        foreach (glob($dir . DIRECTORY_SEPARATOR . '*.json') ?: [] as $old) {
            if (@filemtime($old) < time() - 172800) {
                @unlink($old);
            }
        }
    }
    $ip = isset($_SERVER['REMOTE_ADDR']) ? (string)$_SERVER['REMOTE_ADDR'] : 'unknown';
    $id = substr(hash('sha256', $ip . '|' . __DIR__), 0, 32); // the visitor's address is never stored, only a hash
    $now = time();
    $visitorOk = nandi_counter($dir . DIRECTORY_SEPARATOR . 'ip-' . $id . '.json', function (array &$d) use ($now): bool {
        if (!isset($d['start']) || $now - (int)$d['start'] >= NANDI_RATE_WINDOW_SECONDS) {
            $d = ['start' => $now, 'n' => 0];
        }
        if ((int)$d['n'] >= NANDI_RATE_REQUESTS) {
            return false;
        }
        $d['n'] = (int)$d['n'] + 1;
        return true;
    });
    if (!$visitorOk) {
        return false;
    }
    return nandi_counter($dir . DIRECTORY_SEPARATOR . 'day-' . gmdate('Ymd') . '.json', function (array &$d) use ($chars): bool {
        $used = (int)($d['chars'] ?? 0);
        if ($used + $chars > NANDI_DAILY_CHAR_LIMIT) {
            return false;
        }
        $d['chars'] = $used + $chars;
        return true;
    });
}

$method = isset($_SERVER['REQUEST_METHOD']) ? (string)$_SERVER['REQUEST_METHOD'] : 'GET';

// Status check used by voice-test.html. It reveals only yes/no facts, never the key.
if ($method === 'GET' && isset($_GET['check'])) {
    if (!nandi_same_origin()) {
        nandi_fail(403, 'forbidden', 'This request is not allowed.');
    }
    header('Content-Type: application/json; charset=utf-8');
    header('Cache-Control: no-store');
    header('X-Content-Type-Options: nosniff');
    echo json_encode([
        'key_found' => nandi_api_key() !== '',
        'curl_available' => function_exists('curl_init'),
        'ca_bundle_found' => is_string(getenv('NANDI_CA_BUNDLE')) && is_file((string)getenv('NANDI_CA_BUNDLE')),
        'hindi_voice_set' => isset(NANDI_VOICES['hi']),
        'english_voice_set' => isset(NANDI_VOICES['en']),
    ]);
    exit;
}

if ($method !== 'POST') {
    nandi_fail(405, 'method_not_allowed', 'Use POST.', ['Allow: POST']);
}
if (!nandi_same_origin()) {
    nandi_fail(403, 'forbidden', 'This request is not allowed.');
}
$contentType = strtolower((string)($_SERVER['CONTENT_TYPE'] ?? ''));
if (strpos($contentType, 'application/json') !== 0) {
    nandi_fail(415, 'unsupported_type', 'Send JSON.');
}
$declared = isset($_SERVER['CONTENT_LENGTH']) ? (int)$_SERVER['CONTENT_LENGTH'] : 0;
if ($declared > NANDI_MAX_BODY_BYTES) {
    nandi_fail(413, 'too_large', 'Request is too large.');
}
$raw = file_get_contents('php://input', false, null, 0, NANDI_MAX_BODY_BYTES + 1);
if (!is_string($raw) || strlen($raw) > NANDI_MAX_BODY_BYTES) {
    nandi_fail(413, 'too_large', 'Request is too large.');
}
$input = json_decode($raw, true);
if (!is_array($input)) {
    nandi_fail(400, 'bad_request', 'Invalid request.');
}

$lang = $input['lang'] ?? '';
$text = $input['text'] ?? '';
if (!is_string($lang) || !isset(NANDI_VOICES[$lang])) {
    nandi_fail(400, 'invalid_language', 'Language must be hi or en.');
}
if (!is_string($text) || preg_match('//u', $text) !== 1) {
    nandi_fail(400, 'invalid_text', 'Text is not valid.');
}
$text = (string)preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/u', '', $text);
$text = trim((string)preg_replace('/\s+/u', ' ', $text));
$chars = function_exists('mb_strlen') ? mb_strlen($text, 'UTF-8') : strlen($text);
if ($chars < 1) {
    nandi_fail(400, 'empty_text', 'There is nothing to say.');
}
if ($chars > NANDI_MAX_TEXT_CHARS) {
    nandi_fail(413, 'text_too_long', 'Text is too long.');
}

$apiKey = nandi_api_key();
if ($apiKey === '' || !function_exists('curl_init')) {
    nandi_fail(503, 'not_configured', 'Voice is not set up on this server.');
}
if (!nandi_rate_limit_ok($chars)) {
    nandi_fail(429, 'rate_limited', 'Too many voice requests. Please try again in a few minutes.', ['Retry-After: 60']);
}

$model = getenv('ELEVENLABS_MODEL');
if (!is_string($model) || !in_array($model, NANDI_MODELS, true)) {
    $model = 'eleven_multilingual_v2';
}
$apiHost = getenv('ELEVENLABS_API_HOST');
if (!is_string($apiHost) || !in_array($apiHost, NANDI_API_HOSTS, true)) {
    $apiHost = 'api.elevenlabs.io';
}
$url = 'https://' . $apiHost . '/v1/text-to-speech/' . rawurlencode(NANDI_VOICES[$lang]) . '?output_format=mp3_44100_64';
$payload = json_encode([
    'text' => $text,
    'model_id' => $model,
    'voice_settings' => ['stability' => 0.5, 'similarity_boost' => 0.75],
], JSON_UNESCAPED_UNICODE);

$curl = curl_init($url);
curl_setopt_array($curl, [
    CURLOPT_POST => true,
    CURLOPT_POSTFIELDS => $payload,
    CURLOPT_HTTPHEADER => ['xi-api-key: ' . $apiKey, 'Content-Type: application/json', 'Accept: audio/mpeg'],
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_CONNECTTIMEOUT => 5,
    CURLOPT_TIMEOUT => 25,
    CURLOPT_SSL_VERIFYPEER => true,
    CURLOPT_SSL_VERIFYHOST => 2,
    CURLOPT_FOLLOWLOCATION => false,
]);
$caBundle = getenv('NANDI_CA_BUNDLE');
if (is_string($caBundle) && $caBundle !== '' && is_file($caBundle)) {
    curl_setopt($curl, CURLOPT_CAINFO, $caBundle);
}
$audio = curl_exec($curl);
$errno = curl_errno($curl);
$status = (int)curl_getinfo($curl, CURLINFO_RESPONSE_CODE);
$returnedType = strtolower((string)curl_getinfo($curl, CURLINFO_CONTENT_TYPE));
curl_close($curl);
unset($apiKey);

if ($errno !== 0 || !is_string($audio)) {
    error_log('Nandi voice: connection problem (cURL error ' . $errno . ')');
    nandi_fail($errno === 28 ? 504 : 502, $errno === 28 ? 'voice_timeout' : 'voice_unavailable', 'The voice service could not be reached.');
}
if ($status === 401 || $status === 403) {
    error_log('Nandi voice: the voice service refused the API key (HTTP ' . $status . ')');
    nandi_fail(502, 'voice_unavailable', 'The voice service is not available.');
}
if ($status === 429) {
    nandi_fail(503, 'voice_busy', 'The voice service is busy. Please try again shortly.');
}
if ($status !== 200 || strpos($returnedType, 'audio') === false || strlen($audio) < 200 || strlen($audio) > 5000000) {
    error_log('Nandi voice: unexpected reply from the voice service (HTTP ' . $status . ')');
    nandi_fail(502, 'voice_unavailable', 'The voice service is not available.');
}

http_response_code(200);
header('Content-Type: audio/mpeg');
header('Content-Length: ' . strlen($audio));
header('Cache-Control: no-store');
header('X-Content-Type-Options: nosniff');
echo $audio;
exit;
