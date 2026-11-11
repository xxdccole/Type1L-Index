import json,re
h=json.load(open('new-hits.json'))
def ab(w):
  ii=w.get('abstract_inverted_index')
  if not ii: return ''
  pos=[]
  for word,ps in ii.items():
    for p in ps: pos.append((p,word))
  return ' '.join(x for _,x in sorted(pos))
gen=re.compile(r'cement|concrete|mortar|clinker|pozzol|geopolymer|alkali.activ|shotcrete|grout|binder|masonry',re.I)
T={
'concrete-cellular':r'aerated|foam|cellular|\bAAC\b',
'concrete-heavyweight':r'shield|heavyweight|heavy.weight|high.density|barite|magnetite|hematite|nuclear|irradiat|gamma|neutron|radiation',
'concrete-mass-rcc':r'roller.compacted|\bRCC\b|mass concrete|\bdams?\b|adiabatic|heat of hydration|thermal (crack|stress)|temperature',
'cross-failure-repair':r'collapse|failure|forensic|deteriorat|repair|case study|survey|damage|distress|parking|field',
'binder-specialty':r'expansi|shrinkage.compensat|rapid|sulfoaluminate|type k|MgO|early.strength',
'binder-white-masonry':r'\blime\b|mortar|white|masonry|photocataly|TiO2|plaster|stucco',
'binder-international':r'CEM|blast.furnace|JIS|EN 197|composite cement|Japan|slag cement',
'binder-well':r'well|slurry|oil|gas migration|wellbore|geotherm|CO2',
'scm-natural':r'pumice|diatom|pozzol|zeolite|volcanic',
'concrete-shotcrete':r'shotcrete|sprayed|accelerat|tunnel',
'cross-supply-region':r'cement (industry|production|market|plant|sector)|sand|aggregate|clinker|kiln|industry',
'pll-mix':r'limestone',
'current-2026':r'.',
}
sel={}
for k,w in h.items():
  t=w['queries'][0][0]; ti=w['title'] or ''; a=ab(w)
  if not gen.search(ti) and not (t=='cross-supply-region' and gen.search(a)): continue
  if not re.search(T[t],ti+(' '+a[:600] if t in('current-2026','cross-supply-region') else ''),re.I): continue
  if w.get('is_retracted'): continue
  sel[k]=w; w['_abs']=a
json.dump(sel,open('filtered.json','w'))
rows=sorted(sel.items(),key=lambda x:(x[1]['queries'][0][0],-(x[1].get('cited_by_count') or 0)))
with open('filtered.txt','w') as f:
  for i,(k,w) in enumerate(rows):
    f.write(f"{i}|{w['queries'][0][0]}|{w.get('publication_year')}|{w.get('cited_by_count')}|{w.get('type')}|{'A' if w['_abs'] else '-'}|{w['title'][:140]}|{w.get('language')}\n")
json.dump([k for k,_ in rows],open('filtered-keys.json','w'))
print(len(sel))
