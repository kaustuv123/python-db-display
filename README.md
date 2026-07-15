# Port containers → pie charts

Watcher-only project: read port-terminal counts from SQLite and **every 2 minutes** rewrite three **PNG pie charts** into your Downloads folder (same filenames, overwrite in place).

## Pipeline

```
ports.db  →  db.py (load rows)
          →  charts.py (matplotlib pies → PNG)
          →  watcher.py (every 2 minutes, always redraw)
```

| Module | Job |
|--------|-----|
| `db.py` | Open SQLite, return `[{port_terminal, containers}, …]` |
| `charts.py` | Three pie recipes → fixed PNG filenames |
| `watcher.py` | Loop every 120s; **always** rewrite the three PNGs |

**Data:** `ports.db` table `port_containers`  
**Architecture notes:** [`plans/plan.md`](plans/plan.md)

## The three charts

| File (same basename, PNG + WebP, overwritten) | Chart type | Meaning |
|------------------------------------------------|------------|---------|
| `containers-share.png` / `.webp` | **Vertical bar** (terminals on X, count on Y) | All terminals |
| `containers-top5.png` / `.webp` | Donut pie | Top 5 only |
| `containers-top5-vs-rest.png` / `.webp` | Donut pie | Top 5 + Other |

Folder: `%USERPROFILE%\Downloads\pie\`

Safe write: `*.png.tmp` then replace the final name.

---

## Run on your system (normal / venv)

```powershell
cd C:\Users\kaust\OneDrive\Desktop\python-db-display

# One-time setup
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Once-off: write the three PNGs now
python charts.py

# Long-running: redraw every 2 minutes
python watcher.py
```

Optional smoke tests:

```powershell
python db.py
```

Optional faster interval for testing:

```powershell
$env:PNG_EXPORT_INTERVAL_SEC = "30"
python watcher.py
```

Stop the watcher with **Ctrl+C**.

Open charts:

```powershell
explorer $env:USERPROFILE\Downloads\pie
```

---

## Run with Docker

Requires [Docker Desktop](https://www.docker.com/products/docker-desktop/) running on Windows.

```powershell
cd C:\Users\kaust\OneDrive\Desktop\python-db-display

# Build image + start watcher in the background
docker compose up -d --build

# Follow logs
docker compose logs -f

# Stop
docker compose down
```

What compose mounts:

| Host | Container | Purpose |
|------|-----------|---------|
| `.\ports.db` | `/data/ports.db` | Live database |
| `C:\Users\kaust\Downloads\pie` | `/exports` | PNG output |

Equivalent one-shot without compose (after `docker build -t pie-watcher .`):

```powershell
docker run --rm `
  -e PORTS_DB_PATH=/data/ports.db `
  -e PNG_EXPORT_DIR=/exports `
  -e PNG_EXPORT_INTERVAL_SEC=120 `
  -v "${PWD}/ports.db:/data/ports.db" `
  -v "C:/Users/kaust/Downloads/pie:/exports" `
  pie-watcher
```

---

## Config (env vars)

| Variable | Default (local) | Default (Docker) | Meaning |
|----------|-----------------|------------------|---------|
| `PORTS_DB_PATH` | `./ports.db` | `/data/ports.db` | SQLite file |
| `PNG_EXPORT_DIR` | `%USERPROFILE%\Downloads\pie` | `/exports` | PNG folder |
| `PNG_EXPORT_INTERVAL_SEC` | `120` | `120` | Seconds between redraws |

---

## Update the data

```powershell
python -c "import sqlite3; c=sqlite3.connect('ports.db'); c.execute('UPDATE port_containers SET containers=15000, updated_at=CURRENT_TIMESTAMP WHERE port_terminal=?', ('MUN-CT',)); c.commit(); print('ok')"
```

Within the next interval (≤ 2 minutes), the watcher overwrites the three PNGs. Refresh the image viewer if needed.

---

## What this is not

No web API, no SVG, no change-hash skip — every cycle redraws the same three files from current DB data.
