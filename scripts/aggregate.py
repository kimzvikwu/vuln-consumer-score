import json,re,sys,os,datetime,collections as C
DATA=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","data")
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from roster import ROSTER, ASSIGNER_FALLBACK
norm=lambda x: re.sub(r"\s+"," ",x.lower().replace("_"," ")).strip()
pats=[(r[1],re.compile(r[5])) for r in ROSTER]
def match(strings):
    out=set()
    for x in strings:
        x=norm(x)
        for t,p in pats:
            if p.search(x): out.add(t)
    return out
YEARS=list(range(2019,datetime.date.today().year+1))
agg={r[1]:{y:[0]*6 for y in YEARS} for r in ROSTER}   # crit,high,med,low,unscored,kev
cve_co={}; universe=C.Counter()
for l in open(os.path.join(DATA,"cves.jsonl")):
    i,y,a,v,c,s=json.loads(l); universe[y]+=1
    cos=match(set(v)|set(c))
    if not cos and all(norm(x) in ("n/a","","unknown") for x in v) and a in ASSIGNER_FALLBACK:
        cos={ASSIGNER_FALLBACK[a]}
    idx={4:0,3:1,2:2,1:3,0:3,None:4}[s]
    for t in cos: agg[t][y][idx]+=1
    if cos: cve_co[i]=cos
kev=json.load(open(os.path.join(DATA,"kev.json")))
kevlist=C.defaultdict(list)
for k in kev["vulnerabilities"]:
    y=int(k["dateAdded"][:4])
    cos=match([k["vendorProject"]]) or cve_co.get(k["cveID"],set())
    for t in cos:
        if y in YEARS: agg[t][y][5]+=1
        kevlist[t].append([k["cveID"],k["dateAdded"],k["product"],k["vulnerabilityName"][:90],k.get("knownRansomwareCampaignUse")=="Known"])
out={"generated":datetime.date.today().isoformat(),"kevCatalogVersion":kev.get("catalogVersion"),"years":YEARS,
 "universe":{y:universe[y] for y in YEARS},"companies":[]}
for r in ROSTER:
    t=r[1]; kl=sorted(kevlist[t],key=lambda z:z[1],reverse=True)
    out["companies"].append({"name":r[0],"ticker":t,"sector":r[2],"employees":r[3],"fy":r[4],
      "years":{y:agg[t][y] for y in YEARS},"kevTotal":len(kl),"kevRecent":kl[:8]})
json.dump(out,open(os.path.join(DATA,"scores.json"),"w"),separators=(",",":"))
for c in out["companies"]:
    tot=[sum(c["years"][y][k] for y in (2024,2025,2026)) for k in range(6)]
    print(f'{c["ticker"]:10} {c["name"][:28]:28} {tot}  kevAll={c["kevTotal"]}')
print(out["kevCatalogVersion"], len(kev["vulnerabilities"]))
