---
name: domdb
description: >
  Use when downloading, querying, citing, or converting Danish judicial
  verdicts from domsdatabasen.dk. Triggers: domdb, domsdatabasen, cases.bib,
  Hayagriva cases.yml, j2e, query count/list/index, straffeloven §, Danish
  verdicts. Use when the user runs /domdb.
---

# domdb

Danish verdicts → cite. JSON cache; convert on demand.

## Prior
- schema → `domdb -j` / `domdb <path> -h` — disclose that path only; after install/upgrade/parse fail, rediscover
- this repo → `uv run domdb`; else `uv tool install git+https://github.com/evidlabel/domdb.git`
- creds: `DOMDB_USER_ID` `DOMDB_PASSWORD` (apply at [domsdatabasen.dk](https://domsdatabasen.dk/spoergsmaal-og-svar/api-adgang-til-domsdatabasen/))
- cache: `-d` (default `~/domdatabasen/cases`; `~/.domdb/config.toml`)
- verbatim → **evid** / **precise-quoter**. Keys and exports; never retype judgment text
- no legal advice; spot-check `https://domsdatabasen.dk/#sag/<id>`

## Loop
download → index → query | output

1. `domdb -d <cache> download` — next page (`cases_<n>.json`, batch 25). Re-run until 0
2. `domdb -d <cache> query index` — rebuilds `<cache>/.domdb-query.sqlite`
3. query or output, same `-d`

## Query
No index → JSON scan. `-p` matches HTML body; `-k` metadata unless `--full-text` (PDF, slow). Keywords AND. `-p "straffeloven § 237"` / `"§ 117 stk. 1"`. `list --format json` for scripts.

## Output

| Goal | Leaf |
|------|------|
| Typst cite | `output hay` → `type: Case` |
| LaTeX cite | `output bib` |
| skim | `output md` (`-s` by year, `-k`, `--full-text`) |
| label | `output j2e` → flat UUID dirs; then **evid** |

j2e: uuid5(OID, case id); skip existing; scanned PDFs logged-and-skipped. Seed only — copy into `./evid/sets/<slug>/docs/<uuid>/`, then evid label/quote/gather.

## Downstream
- hay/bib → Typst `#bibliography` / LaTeX `\cite`
- labelled set → evid → **notat**
- **output-table** last

## Trap
- cwd as cache — default is `~/domdatabasen/cases`
- `-k` without `--full-text` misses body-only hits
- stale index after download
- error text `USER_ID`/`PASSWORD` — vars are `DOMDB_*`
- download with empty env
- j2e dump treated as an evid set
- pasted verdict body

## Done
- argv matches `-j`
- `-d` names the cache used
- index rebuilt if queried after download
- cites are keys/exports
