# Vulnerability Consumer Score

A static web app that grades publicly traded companies on the vulnerabilities disclosed in their products. It weights each CVE by severity, adds extra weight when a CVE has been exploited in the wild (CISA KEV), and divides by employee headcount.

**Live site:** open `index.html` in a browser, or enable GitHub Pages (below). The page has no backend: the data is inlined as JSON.

## Scoring

```
risk points = Σ CVEs × severity points   (Critical 10, High 5, Medium 2, Low 1, unscored 2)
            + KEV additions × 50
density     = risk points ÷ (employees ÷ 1,000)
score       = 100 ÷ (1 + density ÷ cohort median density)      → median company = 50
grade       = A ≥ 80, B ≥ 65, C ≥ 50, D ≥ 35, F < 35
```

In the app you can change the year range, every weight, and the normalization (per employee or raw), and you can edit any company's headcount.

## Data sources

| Source | Used for |
|---|---|
| [CVE List V5](https://github.com/CVEProject/cvelistV5) (CVE Program) | CVE records, the affected vendor, and CVSS severity (from the CNA, or from CISA's ADP enrichment) |
| [CISA KEV catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) | Known-exploited CVEs and ransomware use |
| Company annual reports | Employee counts (approximate; set in `scripts/roster.py`) |

**Attribution:** a CVE counts against a company when the record's CNA "affected" vendor, or the CPE vendor, matches one of the company's regexes in `scripts/roster.py`. If a company's own CNA publishes a record with no vendor named (Intel does this), the assigner is used instead (`ASSIGNER_FALLBACK`). Acquired brands roll up to the parent: VMware, Brocade and Symantec into Broadcom; Splunk into Cisco; Juniper and Aruba into HPE; Red Hat and HashiCorp into IBM; Axis into Canon; CyberArk into Palo Alto Networks.

## Repo layout

```
index.html               built site (template + inlined data); this is what GitHub Pages serves
src/template.html        app source; __DATA__ placeholder is replaced at build time
data/scores.json         aggregated per-company, per-year counts [crit, high, med, low, unscored, kev]
scripts/roster.py        companies, tickers, headcounts, vendor regexes  ← edit this to add or fix companies
scripts/extract.py       CVE List → data/cves.jsonl (one line per CVE: id, year, assigner, vendors, CPE vendors, severity)
scripts/aggregate.py     cves.jsonl + kev.json → data/scores.json
scripts/build_site.py    template + scores.json → index.html
scripts/build_pdf.py     optional one-page landscape PDF summary (needs Playwright)
build.sh                 full refresh: clone/pull CVE List, fetch KEV, run the pipeline
.github/workflows/       nightly refresh + GitHub Pages deploy
```

## Run locally

Requires Python 3.9+ and git. The pipeline uses only the Python standard library.

```bash
./build.sh                 # first run shallow-clones the CVE List (~300k JSON files; a few minutes)
open index.html
```

After editing `src/template.html` or `scripts/roster.py`, rerun the relevant steps:

```bash
python3 scripts/aggregate.py && python3 scripts/build_site.py
```

Optional PDF:

```bash
pip install playwright && playwright install chromium
python3 scripts/build_pdf.py   # → pdf/Vulnerability_Consumer_Score.pdf
```

## Deploy on GitHub Pages

1. Push this repo to GitHub.
2. Go to **Settings → Pages → Build and deployment → Source: GitHub Actions**.
3. Go to **Settings → Actions → General → Workflow permissions** and choose **Read and write**, so the nightly job can commit refreshed data.
4. Run the **Refresh data and deploy** workflow once from the Actions tab. After that it runs daily, and on every push to `main`.

## Adding a company

Add a row to `ROSTER` in `scripts/roster.py`:

```python
("Company Name", "TICKER", "Sector", employees, "FY2025", r"^(vendor string|other brand)( inc\.?)?$"),
```

To see which vendor strings exist in the data, check `data/cves.jsonl` after a build. Vendor strings are lowercased, and underscores become spaces, before matching.

## Caveats

- **Disclosure is not insecurity.** Companies with mature PSIRTs, bug bounties and their own CNA publish more CVEs. The KEV weight is there because exploitation in the wild is a better signal of consumer harm.
- **SaaS rarely gets CVEs.** Cloud-first companies fix issues server-side and look clean by construction.
- **Dividing by headcount** favors conglomerates and penalizes small device makers with large fleets.
- **Red Hat's CNA** records many upstream open-source flaws as Red Hat-affected, so much of IBM's count is open-source components.
- **Headcounts are approximate.** Verify them against current filings before relying on the scores.
- **CVE volume in 2026 roughly doubled** program-wide. Compare companies within the same window, not across years.

This is a screening tool, not a security audit or investment advice.
