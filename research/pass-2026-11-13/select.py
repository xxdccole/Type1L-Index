"""Manual selection (Grok Bot, 2026-11-13) from listing.txt (title.search backfill, language-filtered, PLC legacy-topic, current-awareness,
backward and forward citation-chase hits). Excluded on screening: book reviews, discussions, off-topic (FRP-only structural, machining, geology
'limestone cement', medical/orthopaedic 'Zement', finance, soil-only, neuroscience), ML-prediction papers in minor venues, a Figshare mirror,
no-DOI items without an inspectable landing page today."""
import json
R=lambda a,b:list(range(a,b+1))
SEL=(R(0,7)+[9,13,14,15,22,25,27,31]+R(32,40)+[44,45]
+[i for i in R(46,292) if i not in (47,52,76,113,188,218,291)]
+[i for i in R(293,349)]
+[350,352,356,357,358,361,367,368,371,372,373,374,379,380,382,385,386,387,391]
+[392,393,394,396,397,401,404,406,409,410,411]+R(413,426)
+[427,428,429,432,433,434,435,436,437,438,439,441,443,445,446,447,450,451,452,453,454,455,457,458,459,460,463,464,465,467,468,469,470,471,473,474]
+R(476,480)+R(483,506)+[508,509,510]
+[511,513,514,517,518,519,520,522,523,525,526,528,529,530]+R(532,541)+[545]
+R(546,550)+[554,556,559,560,563,564,566]+R(567,583)
+R(588,597)+[600,601]+R(602,610)+[613,615]+R(616,622)
+R(623,643)+R(645,664)
+[i for i in R(665,699) if i!=678]
+[i for i in R(700,739) if i not in (714,729,731,735,736)]
+[740,742,750,754,755,756,758,759,760,761,762,763,765,766,768,769,770,784,795,804,816,817,818,820,821,823,826,828,829]
+[839,840,843,844,845,846]+[851,853,854,855,856,857,858,863,864]+[865,867,868,869,870,871]+R(872,877)+[879,880,881]+R(886,892)
+[893,895,896,897,898,899,900,901,902,903,904,905]+R(907,921)+[924,927])
# no-DOI hits whose landing/catalogue page could not be inspected on 2026-11-13 (TRID 503, CiNii 202/500, JS-only DSpace/Primo, ROSA P 403, etc.)
DROPND=[46, 55, 56, 58, 61, 68, 69, 74, 85, 118, 132, 139, 166, 171, 187, 192, 197, 198, 199, 204, 208, 215, 222, 223, 226, 228, 239, 243, 256, 257, 261, 268, 269, 271, 273, 274, 275, 276, 277, 283, 286, 287, 290, 292, 740, 742, 804, 840, 845]
SEL=sorted(set(SEL)-set(DROPND))
keys=json.load(open('listing-keys.json')); h={'h1':json.load(open('new-hits.json')),'h2':json.load(open('new-hits2.json'))}
sel={}
for i in SEL:
  src,k=keys[i]; w=dict(h[src][k]); w['_src']=src; w['_idx']=i; w.pop('referenced_works',None); sel[k]=w
json.dump(sel,open('selected.json','w'))
nod=[(i,sel[keys[i][1]]['title'][:70],(sel[keys[i][1]].get('primary_location') or {}).get('landing_page_url')) for i in SEL if not sel[keys[i][1]].get('doi')]
print(len(SEL),len(sel)); [print(x) for x in nod]
