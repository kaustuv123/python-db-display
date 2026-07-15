# Restart: Port Containers Pie Charts (First Principles)

## Plan location (your rule)

**Going forward, plans live in the project:**

| Role | Path |
|------|------|
| **Canonical (after approval)** | `C:\Users\kaust\OneDrive\Desktop\python-db-display\plans\plan.md` |
| Future plans | `python-db-display\plans\<short-name>.md` |
| Grok session mirror | This file (plan mode can only write here until you approve) |

**First implementation step after you approve:** create `plans/` in the project and **copy this entire document** to `plans/plan.md`. That file becomes the source of truth you open day-to-day. Do not rely on `.grok\sessions\...` for reading.

### How to open `plans/plan.md` once it exists

```powershell
cd C:\Users\kaust\OneDrive\Desktop\python-db-display
explorer .\plans
Invoke-Item .\plans\plan.md
```

- **VS Code / Cursor:** open project → `plans/plan.md` → preview with `Ctrl+Shift+V` (or `Ctrl+K` then `V` for side-by-side).
- **Explorer:** Desktop → `python-db-display` → `plans` → double-click `plan.md`.

Until approval, you can still open **this** session plan via Grok’s plan UI, or:

```powershell
Invoke-Item "C:\Users\kaust\.grok\sessions\C%3A%5CUsers%5Ckaust%5COneDrive%5CDesktop%5Cpython-db-display\019f6481-f94f-7a80-b07b-ed0cd074dbdb\plan.md"
```

---

## Context

You want to **throw away the existing application code** and rebuild on the **same SQLite data**, understanding each piece from first principles—not by pasting black-box code.

**What you already have (keep):**
- `ports.db` — SQLite file with table `port_containers` (**55 rows**)
  - Columns: `id`, `port_terminal` (unique text), `containers` (int), `updated_at`
  - Example top rows: MUN-CT 14230, MUN-NT 13680, JNPT-CT 12540, …

**What you are dropping (delete on implement):**
- SVG rendering path (`chart_render` SVG, `/api/charts/pies`)
- FastAPI backend and API surface
- Plotly + Kaleido stack
- Docker/compose/start scripts tied to the old API (optional recreate later)
- `add_data.py`, `backend.py`, `chart_render.py`, `png_export.py`, `requirements.txt` contents as they stand

**What you are building (decided):**
| Decision | Choice |
|----------|--------|
| Process shape | **Watcher only** (no web API in v1) |
| Charts | **matplotlib → PNG files** |
| Views | **3 pies**: all-share, top-5, top-5-vs-rest |
| Cadence | Poll every **2 minutes**; regenerate **only when data changed** |
| Data | Keep `ports.db` (and same schema) |
| Output location | **Local Downloads** — default `C:\Users\kaust\Downloads\pie` |
| Filenames | **Fixed names, overwrite in place** — always the same three files; each update replaces the previous image |
| Docs | **`plans/` in the project** — not only under `.grok` |

---

## First principles: what problem are we solving?

```
Real world          Computer model              Artifact
─────────────       ─────────────────           ──────────
Port terminals  →   Rows in a table         →   Pictures that
with container      (name + count)              show proportions
counts                                          (pie slices)
```

A pie chart answers: **“Of the total, what fraction is each slice?”**

For each slice:

\[
\text{angle}_i = \frac{\text{value}_i}{\sum_j \text{value}_j} \times 360^\circ
\]

matplotlib does that math for you when you call `ax.pie(values, labels=...)`, then writes pixels to a PNG file. Your job is the **pipeline around it**: load data → decide if anything changed → transform into the three views → draw → save.

---

## Architecture (layers)

Keep modules thin and single-purpose so each file teaches one idea.

```
┌─────────────────────────────────────────────────────────────┐
│  watcher.py  (orchestrator / process entrypoint)            │
│  - loop forever                                             │
│  - every 120s: load → fingerprint → maybe render → sleep    │
└───────────────┬─────────────────────────────┬───────────────┘
                │                             │
                ▼                             ▼
┌───────────────────────────┐   ┌─────────────────────────────┐
│  db.py                    │   │  charts.py                  │
│  - open SQLite            │   │  - rows → 3 pie “recipes”   │
│  - read all terminals     │   │  - matplotlib draw + save   │
│  - (optional) path config │   │  - fixed output filenames   │
└───────────────┬───────────┘   └──────────────▲──────────────┘
                │                              │
                ▼                              │
┌───────────────────────────┐                  │
│  change.py                │  if changed ─────┘
│  - fingerprint(rows)      │
│  - compare to last hash   │
└───────────────────────────┘

ports.db  (persistent data — DO NOT delete)
Downloads/pie/  — PNG output on the host
plans/plan.md   — architecture doc (project-local, after step 0)
```

### Output: Downloads folder, same names, replace previous

Charts land on your machine so you can open them in Explorer / Photos without Docker.

| Setting | Value |
|---------|--------|
| Default directory | `C:\Users\kaust\Downloads\pie` |
| Env override | `PNG_EXPORT_DIR` (if set, use that instead) |
| Create dir if missing | yes |

**Fixed filenames (always overwrite the same three files):**

| Chart | File path (default) |
|-------|---------------------|
| All terminals | `...\Downloads\pie\containers-share.png` |
| Top 5 only | `...\Downloads\pie\containers-top5.png` |
| Top 5 vs rest | `...\Downloads\pie\containers-top5-vs-rest.png` |

**How replace works (safe overwrite):**

1. Write `containers-share.png.tmp` in the same folder.
2. `Path.replace(...)` renames the temp file onto `containers-share.png`.
3. Result: the **filename never changes** — latest image always at the same path. No `chart-1.png` spam.

Refresh/re-open the image after a DB change cycle if a viewer cached the old pixels.

### Data flow (one cycle)

1. **Connect** to `ports.db` (read-only is enough for the watcher).
2. **SELECT** `port_terminal, containers` ordered by count (and name as tie-break).
3. **Fingerprint** the result (stable hash of sorted pairs).
4. If fingerprint **equals** last run → log “no change”, sleep 120s.
5. If **different** → for each of 3 chart recipes:
   - build labels + values
   - `matplotlib` pie → write fixed name under Downloads/pie (atomic `.tmp` then replace).
6. Store new fingerprint in memory; sleep 120s.

### Why poll every 2 minutes (not “on every write”)?

SQLite does not push “row changed” events by default.

| Approach | How it works | Trade-off |
|----------|--------------|-----------|
| **Poll + fingerprint (chosen)** | Every 120s re-read rows and hash them | Simple, reliable; up to 2 min lag |
| File watch / triggers | OS watch or SQLite hooks | Harder (WAL, multi-connection); overkill for learning |

“After every update” means: **next poll that sees new data redraws**. Max lag ≈ 2 minutes.

### Fingerprint (change detection)

Prefer a **content fingerprint** (not only DB file mtime):

```text
sort by (port_terminal, containers) → canonical string → SHA-256
```

### Three pie “recipes”

| Chart id | Title idea | Slice logic |
|----------|------------|-------------|
| `share` | Container share by terminal | One slice per terminal |
| `top5` | Top 5 terminal share | Only the 5 largest |
| `top5-vs-rest` | Top 5 vs rest | Top 5 + **Other** = sum of the rest |

Non-negative counts; skip empty names; sort largest-first.

### Config (env vars)

| Variable | Default | Role |
|----------|---------|------|
| `PORTS_DB_PATH` | project `./ports.db` | Where data lives |
| `PNG_EXPORT_DIR` | `C:\Users\kaust\Downloads\pie` | Local PNG folder |
| `PNG_EXPORT_INTERVAL_SEC` | `120` | Poll interval |

### Out of scope for v1

- FastAPI / HTTP / SVG / Plotly / Kaleido / Docker  
- Interactive insert CLI (optional later)  
- Web UI, auth, real-time push, historical charts  

---

## Proposed file layout (after clean slate)

```
python-db-display/
  ports.db                  # KEEP
  plans/
    plan.md                 # THIS DOC (copied on implement step 0)
  requirements.txt
  db.py
  change.py
  charts.py
  watcher.py
  README.md

C:\Users\kaust\Downloads\pie\
  containers-share.png
  containers-top5.png
  containers-top5-vs-rest.png
```

**Delete on implement:** `backend.py`, `chart_render.py`, `png_export.py`, `add_data.py`, `Dockerfile`, `docker-compose.yml`, `start.sh`, `__pycache__/`, unused wheels.  
**Never delete:** `ports.db`, `plans/`.

---

## Learning path — docs to read

### 1. SQLite + Python
- [sqlite3 module](https://docs.python.org/3/library/sqlite3.html)
- [SQLite datatypes](https://www.sqlite.org/datatype3.html)
- [SQLite one-file DB](https://www.sqlite.org/onefile.html)

### 2. Pie math
- [Pie chart (Wikipedia)](https://en.wikipedia.org/wiki/Pie_chart)
- Mentally: top terminal / total ≈ slice percent

### 3. matplotlib
- [Quick start](https://matplotlib.org/stable/users/explain/quick_start.html)
- [Pie gallery](https://matplotlib.org/stable/gallery/pie_and_polar_charts/pie_features.html)
- [savefig](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.savefig.html)
- [Backends (use Agg)](https://matplotlib.org/stable/users/explain/figure/backends.html)

### 4. Hashing
- [hashlib](https://docs.python.org/3/library/hashlib.html)

### 5. Loop / sleep
- [time.sleep](https://docs.python.org/3/library/time.html#time.sleep)

### 6. Paths / atomic replace
- [pathlib](https://docs.python.org/3/library/pathlib.html)

---

## Implementation order (after approval)

0. **Write full plan to** `plans/plan.md` in the project (canonical copy).
1. Backup `ports.db` → `ports.db.bak`.
2. Delete old application modules (keep DB + `plans/`).
3. `db.py` — load rows; smoke-test count/top 5.
4. `change.py` — fingerprint equal/unequal checks.
5. `charts.py` — write 3 fixed PNGs to Downloads/pie.
6. `watcher.py` — 120s loop; write only on change.
7. `requirements.txt` + root `README.md`.
8. End-to-end verification.

**Teach while coding:** job → data shape → smallest code → run → next layer. No dump-and-run.

---

## Critical paths

| Path | Action |
|------|--------|
| `ports.db` | Preserve |
| `plans/plan.md` | Create/sync as canonical docs |
| `db.py`, `change.py`, `charts.py`, `watcher.py` | Create |
| `requirements.txt`, `README.md` | Rewrite |
| Old backend/chart/docker modules | Remove |

---

## Verification

1. Row count still correct after cleanup.  
2. Install deps; run once-off and/or watcher.  
3. Three PNGs under `C:\Users\kaust\Downloads\pie` with fixed names.  
4. Unchanged data → no rewrite on next poll.  
5. `UPDATE` one row → within 2 minutes, same filenames refresh.  
6. Ctrl+C stops cleanly.

---

## How we teach while coding

1. State the job in one sentence.  
2. Show data shape (rows → labels/values).  
3. Smallest working version.  
4. Run and inspect.  
5. Add fingerprint, then loop, then atomic write.
