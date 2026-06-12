# install-sl.ps1 — Hermes /sl plugin installer
# Run: PowerShell -ExecutionPolicy Bypass -File install-sl.ps1

Write-Host "=== Hermes /sl Plugin Installer ===" -ForegroundColor Cyan
Write-Host ""

# Install from Gitea repo
Write-Host "Installing from Gitea..."
hermes plugins install https://git.softmediadesign.com/git_alhan/hermes-plugin-session-list.git --enable

if ($LASTEXITCODE -ne 0) {
    Write-Host "Gitea failed, trying GitHub..."
    hermes plugins install https://github.com/alhan/hermes-plugin-session-list.git --enable
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "[FAIL] Could not install plugin" -ForegroundColor Red
    exit 1
}

# Default config
$ConfigFile = "$env:USERPROFILE\.hermes\session_list_config.yaml"
if (-not (Test-Path $ConfigFile)) {
    Write-Host "Creating default config..."
    @'
# Hermes Session List — Column Configuration
# Available: #, id, source, model, title, started_at, ended_at,
#   message_count, preview, last_active, input_tokens, output_tokens,
#   total_tokens, net_input, net_total, cache_read_tokens,
#   cache_write_tokens, reasoning_tokens

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
    Write-Host "[OK] Config created" -ForegroundColor Green
}

Write-Host ""
Write-Host "Done! Restart Hermes, type /sl" -ForegroundColor Green
