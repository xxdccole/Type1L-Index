"""Manual selection (by Grok Bot, 2026-11-11) from listing2.txt (harvest2 title-search backfill), listing.txt/new-hits (harvest1) and filtered.txt (current-awareness)."""
import json
L2=[31,33,34,44,37,51,56,88, 99,110,141,158,178,114,107,159,173, 183,184,187,188,195,197,212,217,239,241, 258,265,277,305,283,296,355,356,360,267,
369,370,375,381,395,415,418,421,431,450,454,461,468, 474,477,481,485,505,526,538,575,576, 590,635,640,676,661,694,654,664,681,705,673,670,
707,714,722,739,744,748,750,754,724, 788,791,793,800,808,823,846,847,858,866,869,855, 880,881,902,903,919,922,955,962,971,995,
999,1003,1008,1011,1019,1022,1023,1026,1028,1035, 1042,1043,1061,1070,1079, 1083,1084,1087,1101,1108,1146,1150]
CUR=[100,102,109,134,138,161,168,193,194,208,209,211,215,217,218,240,260,287,295,301,307,321]
k2=json.load(open('listing2-keys.json')); h2=json.load(open('new-hits2.json'))
kf=json.load(open('filtered-keys.json')); hf=json.load(open('filtered.json'))
h1=json.load(open('new-hits.json'))
sel={}
for i in L2: sel[k2[i]]=dict(h2[k2[i]],_src='harvest2',_idx=i)
for i in CUR: sel[kf[i]]=dict(hf[kf[i]],_src='harvest1-current',_idx=i)
# two harvest1 historical cellular items
for k,w in h1.items():
  if w['title'] in ('Structure and properties of aerated concrete: a review','A review of autoclaved aerated concrete products'): sel[k]=dict(w,_src='harvest1',_idx=None)
for w in sel.values(): w.pop('_abs',None)
json.dump(sel,open('selected.json','w'))
print(len(L2),len(CUR),len(sel))
