"""One-page landscape PDF summary (default Balanced weights, last 3 years). Needs: pip install playwright && playwright install chromium"""
import json,statistics as S,html,os,sys,asyncio,datetime
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..")
d=json.load(open(os.path.join(ROOT,"data","scores.json")));W=[10,5,2,1,2,50];Y=datetime.date.today().year;YS=[str(y) for y in (Y-2,Y-1,Y)]
rows=[]
for c in d["companies"]:
    t=[sum(c["years"][y][k] for y in YS) for k in range(6)]
    pts=sum(a*b for a,b in zip(t,W));den=pts/(c["employees"]/1000)
    rows.append(dict(name=c["name"],tk=c["ticker"],sec=c["sector"],emp=c["employees"],cves=sum(t[:5]),crit=t[0],high=t[1],kev=t[5],den=den))
med=S.median(r["den"] for r in rows)
for r in rows:
    r["score"]=round(100/(1+r["den"]/med)); s=r["score"]
    r["g"]="A" if s>=80 else "B" if s>=65 else "C" if s>=50 else "D" if s>=35 else "F"
rows.sort(key=lambda r:(-r["score"],r["den"]))
for i,r in enumerate(rows):r["rank"]=i+1
tc=sum(r["cves"] for r in rows);tk=sum(r["kev"] for r in rows)
gc={"A":"#0f7a43","B":"#4f8a12","C":"#a07a00","D":"#c0560a","F":"#c4162a"}
def tr(r):
    return f'<tr><td class=n>{r["rank"]}</td><td><b>{html.escape(r["name"])}</b> <span class=m>{r["tk"]}</span></td><td class=n>{r["emp"]:,}</td><td class=n>{r["cves"]:,}</td><td class=n>{r["crit"]:,}</td><td class=n>{r["kev"]}</td><td class=n>{r["den"]:,.1f}</td><td><div class=bar><i style="width:{r["score"]*0.62}px;background:{gc[r["g"]]}"></i><em>{r["score"]}</em></div></td><td><span class=g style="background:{gc[r["g"]]}">{r["g"]}</span></td></tr>'
head='<tr><th class=n>#</th><th>Company</th><th class=n>Employees</th><th class=n>CVEs</th><th class=n>Crit</th><th class=n>KEV</th><th class=n>Pts/1k</th><th>Score</th><th></th></tr>'
h=len(rows)//2+len(rows)%2
tbl=lambda rs:f'<table><thead>{head}</thead><tbody>{"".join(tr(r) for r in rs)}</tbody></table>'
worst,best=rows[-1],rows[0]
page=f'''<!DOCTYPE html><html><head><meta charset=utf-8>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@600;700&family=Inter:wght@400;600&display=swap" rel=stylesheet>
<style>
@page{{size:letter landscape;margin:0.28in}}
*{{box-sizing:border-box}}body{{margin:0;font:7.4pt/1.25 Inter,sans-serif;color:#0b0d14}}
.strip{{background:#1240e0;color:#fff;padding:7px 10px;display:flex;justify-content:space-between;align-items:baseline;gap:12px}}
h1{{font:700 17pt/1 "Space Grotesk",sans-serif;margin:0}}.strip p{{margin:0;font-size:7.6pt;max-width:60%;text-align:right}}
.top{{display:flex;gap:10px;align-items:stretch;margin:5px 0}}
.find{{flex:1;font:600 10.5pt/1.2 "Space Grotesk",sans-serif;align-self:center}}
.k{{border:1px solid #d5dcf0;padding:3px 8px;min-width:92px}}.k b{{display:block;font:600 12.5pt/1.1 "Space Grotesk",sans-serif}}.k span{{color:#566078;font-size:6.8pt}}
.cols{{display:grid;grid-template-columns:1fr 1fr;gap:14px}}
table{{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}}
th{{text-align:left;font-weight:600;color:#566078;font-size:6.8pt;border-bottom:1.2px solid #0b0d14;padding:1.5px 3px}}
td{{padding:0.6px 3px;border-bottom:0.5px solid #e3e8f5;white-space:nowrap}}.n{{text-align:right}}.m{{color:#566078;font-size:6.4pt}}
.bar{{display:flex;align-items:center;gap:4px}}.bar i{{display:block;height:6px;border-radius:1px}}.bar em{{font-style:normal;font-weight:600}}
.g{{display:inline-block;width:12px;text-align:center;color:#fff;font-weight:700;border-radius:2px;font-size:6.8pt}}
.foot{{display:grid;grid-template-columns:1.05fr 1.6fr;gap:14px;margin-top:6px;background:#eef2ff;padding:6px 9px;font-size:6.9pt}}
.foot h3{{font:600 8pt "Space Grotesk",sans-serif;margin:0 0 2px}}.foot p{{margin:0 0 3px}}.foot ul{{margin:0;padding-left:11px}}.foot li{{margin-bottom:1.5px}}
.src{{font-size:6.4pt;color:#566078;margin-top:4px}}
</style></head><body>
<div class=strip><h1>Vulnerability Consumer Score</h1><p>Public companies graded on CVEs disclosed in their products, weighted by severity and active exploitation, per 1,000 employees. Higher score = fewer serious vulnerabilities for its size. Window: CVEs published {YS[0]}–{YS[-1]} ({YS[-1]} year-to-date).</p></div>
<div class=top><div class=find>{html.escape(worst["name"])} carries the heaviest vulnerability load for its size ({worst["den"]:,.0f} points per 1,000 employees); {html.escape(best["name"])} the lightest.</div>
<div class=k><b>{len(rows)}</b><span>companies scored</span></div><div class=k><b>{tc:,}</b><span>CVEs attributed</span></div><div class=k><b>{tk}</b><span>CISA KEV additions</span></div><div class=k><b>{med:.0f}</b><span>median pts/1k (score 50)</span></div></div>
<div class=cols>{tbl(rows[:h])}{tbl(rows[h:])}</div>
<div class=foot><div><h3>Method</h3>
<p><b>Risk points</b> = CVEs × severity points (Critical 10, High 5, Medium 2, Low 1, unscored 2) + 50 per CISA KEV addition. <b>Density</b> = points ÷ (employees ÷ 1,000). <b>Score</b> = 100 ÷ (1 + density ÷ median density). Grades: A ≥80, B ≥65, C ≥50, D ≥35, F &lt;35.</p>
<p>CVEs are attributed by the vendor named in the CVE record (CNA "affected" or CISA ADP CPE). Severity is the highest CVSS base rating in the record. Acquisitions are rolled up: VMware, Brocade and Symantec into Broadcom; Splunk into Cisco; Juniper and Aruba into HPE; Red Hat and HashiCorp into IBM; Axis into Canon; CyberArk into Palo Alto Networks.</p></div>
<div><h3>Read with care</h3><ul>
<li><b>Disclosure is not insecurity.</b> Mature PSIRTs, bug bounties and vendor CNAs publish more CVEs; a low count can mean fewer bugs or fewer disclosed. KEV weight reflects real-world exploitation.</li>
<li><b>SaaS rarely gets CVEs.</b> Cloud-heavy firms (Salesforce, ServiceNow, Shopify, Meta) fix server-side and look clean by construction.</li>
<li><b>Headcount favors conglomerates</b> (Siemens, Hitachi, Samsung) and penalizes small device makers with large fleets (D-Link, Netgear, Ubiquiti).</li>
<li><b>Employee counts are approximate</b> (latest annual report, mostly FY2024) and not individually verified. IBM includes Red Hat, whose CNA records many upstream open-source flaws as Red Hat-affected.</li>
<li><b>2026 CVE volume roughly doubled</b> program-wide ({d["universe"][YS[1]]:,} in {YS[1]} vs {d["universe"][YS[2]]:,} in {YS[2]} YTD); compare companies within a window, not across years.</li></ul></div></div>
<div class=src>Sources: CVE List V5 (CVE Program), snapshot {d["generated"]}; CISA Known Exploited Vulnerabilities catalog v{d["kevCatalogVersion"]}; company annual reports. Screening tool, not a security audit or investment advice.</div>
</body></html>'''
HTML=os.path.join(ROOT,"pdf","onepage.html");os.makedirs(os.path.dirname(HTML),exist_ok=True)
open(HTML,"w").write(page)
async def render():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page()
        await pg.goto("file://"+os.path.abspath(HTML)); await pg.wait_for_timeout(1500)
        out=os.path.join(ROOT,"pdf","Vulnerability_Consumer_Score.pdf")
        await pg.pdf(path=out,format="Letter",landscape=True,print_background=True,prefer_css_page_size=True,scale=0.96)
        await b.close(); print("wrote",out)
asyncio.run(render())
