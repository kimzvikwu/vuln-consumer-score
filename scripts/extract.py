import json, os, sys, glob
root = sys.argv[1]; out = sys.argv[2]
SEV = {"CRITICAL":4,"HIGH":3,"MEDIUM":2,"MODERATE":2,"LOW":1,"NONE":0}
def score_to_sev(s):
    if s is None: return None
    return 4 if s>=9 else 3 if s>=7 else 2 if s>=4 else 1 if s>0 else 0
def sev_from_metrics(ms):
    best=None
    for m in ms or []:
        for k in ("cvssV4_0","cvssV3_1","cvssV3_0","cvssV2_0"):
            if k in m:
                d=m[k]; s=d.get("baseSeverity")
                v = SEV.get(str(s).upper()) if s else score_to_sev(d.get("baseScore"))
                if v is not None and (best is None or v>best): best=v
                break
        if best is None and "other" in m:
            c=json.dumps(m["other"]).upper()
            for w in ("CRITICAL","HIGH","MODERATE","MEDIUM","LOW"):
                if '"'+w+'"' in c or w in c.split('"'):
                    best=SEV[w]; break
    return best
n=0
with open(out,"w") as fo:
    for y in range(2016,2027):
        for f in glob.iglob(f"{root}/cves/{y}/*/*.json"):
            try: d=json.load(open(f))
            except Exception: continue
            md=d.get("cveMetadata",{})
            if md.get("state")!="PUBLISHED": continue
            pub=(md.get("datePublished") or "")[:4]
            if not pub.isdigit() or int(pub)<2019: continue
            c=d.get("containers",{}); cna=c.get("cna",{})
            sev=sev_from_metrics(cna.get("metrics"))
            if sev is None:
                for a in c.get("adp",[]) or []:
                    s=sev_from_metrics(a.get("metrics"))
                    if s is not None and (sev is None or s>sev): sev=s
            vendors=sorted({(a.get("vendor") or "").strip().lower() for a in cna.get("affected",[]) or [] if a.get("vendor")})
            cpes=set()
            for a in (c.get("adp") or [])+[cna]:
                for af in a.get("affected",[]) or []:
                    for cp in af.get("cpes",[]) or []:
                        p=cp.split(":")
                        if len(p)>4: cpes.add(p[3].lower())
            fo.write(json.dumps([md.get("cveId"),int(pub),(md.get("assignerShortName") or "").lower(),vendors,sorted(cpes),sev])+"\n"); n+=1
print(n)
