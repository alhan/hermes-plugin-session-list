# install-sl.ps1 — Hermes /sl plugin installer (Windows)
# 
# Single-command install:
#   PowerShell -ExecutionPolicy Bypass -Command "irm https://git.softmediadesign.com/git_alhan/hermes-plugin-session-list/raw/branch/master/install-sl.ps1 | iex"
#
# Or manually:
#   PowerShell -ExecutionPolicy Bypass -File install-sl.ps1

Write-Host "=== Hermes /sl Plugin Installer ===" -ForegroundColor Cyan
Write-Host ""

# Install plugin from Gitea repo
Write-Host "Installing session-list plugin..."
$result = hermes plugins install "https://git.softmediadesign.com/git_alhan/hermes-plugin-session-list.git" --enable 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "[FAIL] Plugin install failed:" -ForegroundColor Red
    Write-Host $result
    exit 1
}
Write-Host "[OK] Plugin installed" -ForegroundColor Green

# Copy default config if not exists
$ConfigFile = "$env:USERPROFILE\.hermes\session_list_config.yaml"
if (-not (Test-Path $ConfigFile)) {
    Write-Host "Creating default config..."
    @'
# Hermes Session List — Column Configuration
# Edit this file to customize /sl output.
#
# Available fields: #, id, source, model, title, started_at, ended_at,
#   message_count, preview, last_active, input_tokens, output_tokens,
#   total_tokens, net_input, net_total, cache_read_tokens,
#   cache_write_tokens, reasoning_tokens
# width: 0 = free-form (only for the last column)

columns:
  - {field: "#", width: 3, label: "#"}
  - {field: title, width: 42, label: Title}
  - {field: message_count, width: 5, label: Msgs}
  - {field: cache_read_tokens, width: 7, label: hit}
  - {field: input_tokens, width: 7, label: miss}
  - {field: output_tokens, width: 7, label: out}
  - {field: model, width: 10, label: Model}
  - {field: source, width: 4, label: Src}
  - {field: last_active, width: 11, label: Active}
'@ | Out-File -FilePath $ConfigFile -Encoding utf8
    Write-Host "[OK] Created $ConfigFile" -ForegroundColor Green
} else {
    Write-Host "[SKIP] Config already exists: $ConfigFile" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "  Done! Restart Hermes, type /sl" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Config: $ConfigFile" -ForegroundColor Yellow
Write-Host "Plugin: ~/.hermes/plugins/session-list/" -ForegroundColor Yellow
