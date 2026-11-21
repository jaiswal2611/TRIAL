# Saves your ElevenLabs API key into a private .env file that sits OUTSIDE the website folder (public_html).
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$envFile = Join-Path $root '.env'
Write-Host ''
Write-Host 'Nandi voice: save your ElevenLabs API key privately'
Write-Host 'The key is typed hidden, saved only in the file named .env next to this script, and never put into any website file.'
Write-Host ''
$secure = Read-Host 'Paste your ElevenLabs API key and press Enter (nothing will show while you type)' -AsSecureString
$bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
try { $plain = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr) } finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr) }
$plain = $plain.Trim()
if ($plain -notmatch '^[A-Za-z0-9_\-]{16,200}$') {
  Write-Host 'That does not look like an ElevenLabs API key. Nothing was saved.' -ForegroundColor Red
  exit 1
}
$lines = @("ELEVENLABS_API_KEY=$plain", 'ELEVENLABS_MODEL=eleven_multilingual_v2')
[System.IO.File]::WriteAllText($envFile, ($lines -join "`r`n") + "`r`n", (New-Object System.Text.UTF8Encoding($false)))
try { icacls $envFile /inheritance:r /grant:r "$($env:USERNAME):(R,W)" | Out-Null } catch { }
$plain = $null
Write-Host 'Saved. You can now run START-NANDI.bat.' -ForegroundColor Green
