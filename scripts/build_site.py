"""Inline data/scores.json into src/template.html -> index.html"""
import os
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..")
data=open(os.path.join(ROOT,"data","scores.json")).read().replace("</","<\\/")
tpl=open(os.path.join(ROOT,"src","template.html")).read()
open(os.path.join(ROOT,"index.html"),"w").write(tpl.replace("__DATA__",data))
print("wrote index.html")
