# Hermes Plugin: Session List (/sl)

Custom slash command for [Hermes Agent](https://github.com/NousResearch/hermes-agent) that replaces the built-in `/sessions` with configurable columns.

## Features

- Configurable columns (field, width, label) via `~/.hermes/session_list_config.yaml`
- Token stats: cache hit, cache miss, output tokens
- 1-based row numbers for `/resume <#>`
- Survives `hermes update` (lives in `~/.hermes/plugins/`)

## Install

**Linux/macOS:**
```bash
hermes plugins install https://git.softmediadesign.com/git_alhan/hermes-plugin-session-list.git --enable
```

**Windows (one-liner):**
```powershell
PowerShell -ExecutionPolicy Bypass -Command "irm https://git.softmediadesign.com/git_alhan/hermes-plugin-session-list/raw/branch/master/install-sl.ps1 | iex"
```

Then `/new` (or restart Hermes) to reload.

## Usage

```
/sl        # last 20 sessions
/sl 5      # last 5 sessions
```

## Column Config

Copy `session_list_config.example.yaml` to `~/.hermes/session_list_config.yaml` and customize:

```yaml
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
```

Available fields: `#`, `id`, `source`, `model`, `title`, `started_at`, `ended_at`, `message_count`, `preview`, `last_active`, `input_tokens`, `output_tokens`, `total_tokens`, `net_input`, `net_total`, `cache_read_tokens`, `cache_write_tokens`, `reasoning_tokens`

Set `width: 0` on the **last** column for free-form (no truncation).
