# Port containers → pie charts

Watcher-only project (no FastAPI): read port-terminal counts from **SQLite or Oracle**, and every **2 minutes** rewrite chart **PNG + WebP** files (fixed names, overwrite in place).

## Pipeline

```
DB (SQLite or Oracle)
   → db.py (load_rows — same dict shape either way)
   → charts.py (matplotlib)
   → watcher.py (every 2 minutes)
   → PNG/WebP on disk
```

| Module | Job |
|--------|-----|
| `db.py` | Toggle `DB_BACKEND=sqlite\|oracle`; return `[{port_terminal, containers}, …]` |
| `charts.py` | Bar + top-25 pies → fixed filenames |
| `watcher.py` | Loop every 120s; always rewrite |
| `sql/*.sql` | One-time Oracle CREATE + seed (you run on the server) |

**Demo data:** 60 CONCOR-style terminals with full names — `seed_data.py` (SQLite) and `sql/oracle_seed.sql` (Oracle).

Full Oracle steps: [`plans/oracle.md`](plans/oracle.md)

---

## Toggle: SQLite vs Oracle

| Env | Values | Use |
|-----|--------|-----|
| `DB_BACKEND` | `sqlite` | Local Python on laptop (default if unset) |
| `DB_BACKEND` | `oracle` | Docker on server (`docker-compose.yml`) |

Oracle also needs credentials plus **either** DSN-less host fields **or** `ORACLE_DSN`:

| Env | Example | Notes |
|-----|---------|--------|
| `ORACLE_USER` | schema user | required |
| `ORACLE_PASSWORD` | password | required |
| `ORACLE_HOST` | `10.0.0.5` or hostname | **DSN-less** |
| `ORACLE_PORT` | `1521` | default 1521 |
| `ORACLE_SERVICE_NAME` | `ORCLPDB1` | **DSN-less** (not SID unless you only have SID) |
| `ORACLE_DSN` | `host:1521/ORCLPDB1` | optional if HOST+SERVICE set |
| `ORACLE_TABLE` | `port_containers` | optional |

**DSN-less** = no `tnsnames.ora`, no TNS alias. Thin mode needs no Instant Client.

```bash
# .env example (DSN-less)
ORACLE_USER=myuser
ORACLE_PASSWORD=secret
ORACLE_HOST=dbserver.company.com
ORACLE_PORT=1521
ORACLE_SERVICE_NAME=ORCLPDB1
```

---

## Oracle on the server (recommended flow)

### Step 1 — Create table + seed (once)

On a machine that can reach Oracle (SQL\*Plus, SQLcl, or SQL Developer), as the **app schema user**:

```bash
sqlplus your_user/your_password@//dbhost:1521/ORCLPDB1 @sql/oracle_schema.sql
sqlplus your_user/your_password@//dbhost:1521/ORCLPDB1 @sql/oracle_seed.sql
```

Or open and run:

1. `sql/oracle_schema.sql` — `CREATE TABLE port_containers …`
2. `sql/oracle_seed.sql` — `DELETE` + 60 `INSERT`s + `COMMIT`

Verify:

```sql
SELECT COUNT(*) FROM port_containers;   -- 60
```

If you change `seed_data.py` later:

```bash
python scripts/generate_oracle_sql.py
# re-run oracle_seed.sql on the server
```

### Step 2 — Docker watcher (only compose file: `docker-compose.yml`)

```bash
cp .env.oracle.example .env
# set ORACLE_USER, ORACLE_PASSWORD, ORACLE_HOST, ORACLE_SERVICE_NAME, PNG_EXPORT_HOST_PATH

docker compose --env-file .env up -d --build
docker compose logs -f
docker compose down
```

The container only **SELECTs** rows and writes charts to the mounted export folder.  
It does **not** create the Oracle table.

---

## Local SQLite (no Docker)

For laptop/dev without Oracle, run Python directly (`DB_BACKEND` defaults to `sqlite`):

```powershell
cd C:\Users\kaust\OneDrive\Desktop\python-db-display
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

python db.py              # ensure + list rows
python db.py --reseed     # reload seed into ports.db
python charts.py          # write charts once
python watcher.py         # loop every 2 minutes
```

Default export (Windows): `%USERPROFILE%\Downloads\pie`

---

## Chart files

| File | Meaning |
|------|---------|
| `containers-share.png` / `.webp` | All terminals (vertical bar) |
| `containers-top25.png` / `.webp` | Top 25 pie |
| `containers-top25-vs-rest.png` / `.webp` | Top 25 + Other pie |

---

## Config summary

| Variable | Default | Meaning |
|----------|---------|---------|
| `DB_BACKEND` | `oracle` in Docker; `sqlite` for local Python | Backend |
| `ORACLE_USER` / `ORACLE_PASSWORD` | from `.env` | Login |
| `ORACLE_HOST` / `ORACLE_PORT` / `ORACLE_SERVICE_NAME` | from `.env` | DSN-less connect |
| `ORACLE_DSN` | optional | Easy Connect string if not using HOST |
| `ORACLE_TABLE` | `port_containers` | Table name |
| `PNG_EXPORT_HOST_PATH` | `./exports` | Host chart folder (compose) |
| `PNG_EXPORT_DIR` | `/exports` in container | Chart path inside container |
| `PNG_EXPORT_INTERVAL_SEC` | `120` | Poll interval |
| `PORTS_DB_PATH` | `./ports.db` | SQLite only (local Python) |

---

## What this is not

No FastAPI, no SVG — only a DB reader + chart writer loop.
