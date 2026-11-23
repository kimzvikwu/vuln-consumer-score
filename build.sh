#!/usr/bin/env bash
# Full refresh: download CVE List + CISA KEV, aggregate, rebuild index.html.
set -euo pipefail
cd "$(dirname "$0")"
if [ -d cvelistV5/.git ]; then git -C cvelistV5 pull -q --depth 1; else git clone -q --depth 1 https://github.com/CVEProject/cvelistV5 cvelistV5; fi
curl -sfL -o data/kev.json https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json \
  || curl -sfL -o data/kev.json https://raw.githubusercontent.com/cisagov/kev-data/main/known_exploited_vulnerabilities.json
python3 scripts/extract.py cvelistV5 data/cves.jsonl
python3 scripts/aggregate.py
python3 scripts/build_site.py
