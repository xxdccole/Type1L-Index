"""English title-level glosses for non-English leads (Grok Bot, 2026-11-25). Translation of the title only; content not reviewed."""
import json
T={26:'the influence of moisture content on the creep of hardened cement paste',
218:'the ferrite phase in cement and its behaviour during hydration',
219:'development of cement-bound materials using hydrophobising additives: hydration, microstructure development and durability',
220:'the significance of calcium hydroxide in cement for the resistance of cement mortar and concrete to aggressive attack, and its aggression-resistant binding by chemical conversion',
221:'"chemistry that does us good": cement and hydration',
222:'electron-microscope investigations of cement hydration',
223:'the hydration of portland cement',
224:'the influence of fly ash as a partial replacement for portland cement on concrete durability: physical properties, chloride-ion and carbon-dioxide diffusion',
225:'the use of zeolite as a mineral addition to produce pozzolanic cement',
226:'valorisation of silicomanganese (SiMn) slag as a pozzolanic material for cement manufacture',
227:'evaluation of pozzolanic industrial by-products in portland cement binders and the influence of their use on material durability',
228:'an analytical and physico-chemical study of the pozzolanic cement–gypsum–water system',
229:'pozzolanic cements',
230:'designing concrete for a given service life of structures: controlling durability with respect to reinforcement corrosion and alkali-aggregate reaction',
231:'application of a probabilistic approach to the durability of precast concrete products',
232:'the durability of concrete',
233:'a study of concrete durability by a performance-based approach',
234:'durability of self-compacting concretes',
235:'shrinkage and cracking of self-compacting concretes: influence of mix design',
236:'the effect of adding limestone on the compressive strength of portland composite cement',
237:'lightweight concrete from a mixture of styrofoam and sawdust with portland cement at 250, 300 and 350 kg/m3',
238:'compressive strength of hybrid fly-ash geopolymer mortar using portland cement',
239:'durability of portland composite cement (PCC) concrete in the peat environment of Bengkalis Regency',
240:'a study of slag cement as a substitute for portland cement in concrete',
241:'use of rice husk ash as an additive in portland cement at PT Semen Baturaja (Persero)',
242:'the durability of reinforced concrete',
243:'code provisions on the strength and durability of structural concrete',
244:'experimental evaluation of the contribution of cladding/covering elements to concrete durability',
245:'durability assessment of reinforced concrete structures strengthened with carbon-fibre fabrics (CFRP)',
246:'reinforced concrete: the durability challenge',
247:'durability study of a concrete modified with nanoclay and a water-repellent resin',
248:'the mechanism of chloride fixation in mortar pore solution by cement hydrates (corrosion/salt damage)',
249:'analysis of the hydration reaction and strength-development mechanism of cement with added fine limestone powder by X-ray diffraction/Rietveld method',
250:'hydration and moisture loss of cementitious materials subjected to drying during early curing',
251:'the role of the steric-hindrance effect of superplasticisers in the dispersion of cement particles',
252:'a study of the relation between hydration and strength development of cement–silica fume binders (high-strength concrete)',
253:'the effect of early high-temperature history on cement hydration and microstructure formation',
254:'multi-component portland cement CEM II/B-M (V-W) 32,5R: composition, properties and possible uses in construction',
255:'multi-component cement CEM V/A (S-V) 32,5R-LH',
256:'portland slag cement as a constituent of concrete in the construction of the Zimna Wódka–Ujazd road',
257:'portland fly-ash cement CEM II/B-V 32,5 R',
258:'portland slag cement CEM II/B-S 42,5',
259:'the pozzolanic activity of soda-lime glass microparticles (colourless and amber) and their influence on the performance of portland cement composites',
260:'producing self-compacting concrete with marble and granite processing waste and a study of its mechanical properties',
261:'production of self-compacting concrete incorporating red-ceramic industry waste',
262:'a comparison of the properties of self-compacting concrete (SCC) made with fine sand and fly ash',
263:'the influence of viscosity-modifying admixture on the properties of self-compacting concrete',
264:'a comparative study of self-compacting concrete and conventionally vibrated concrete on a high-rise building site',
267:'use of fine recycled construction-demolition aggregate in foam concrete production and determination of the optimum water/cement ratio',
268:'the effect of the pore structure of cement paste on concrete properties in high-strength concretes',
269:'the effectiveness of cement and superplasticising admixtures in producing high-strength concrete',
270:'usability of ground glass-fibre reinforced concrete (GRC) waste as a cement replacement material',
271:'the effect of fly ash partially replacing cement on the properties of ready-mixed concrete',
272:'the effect of fly-ash content partially replacing cement on the properties of high-strength concrete',
273:'the effect of reclaimed asphalt aggregate on the technical properties of roller-compacted cement concrete',
274:'manufacture of lightweight aggregate from fly ash for cement concrete',
275:'a study of porous (drainable) cement-concrete pavement structures for sustainable surface drainage',
276:'strength, plastic-shrinkage cracking resistance and water permeability of cement-concrete pavements using steel-slag aggregate and rubber',
277:'the reaction between nano-SiO2 and Ca(OH)2 in hardened cement paste',
442:'fresh and hardened properties of self-compacting concrete with partial replacement of cement by glass powder',
443:'the effect of sugarcane bagasse ash and an additive abbreviated "Liatligbal" (not expanded in the title) on high-strength concrete'}
LN={'de':'German','es':'Spanish','fr':'French','id':'Indonesian','it':'Italian','ja':'Japanese','pl':'Polish','pt':'Portuguese','tr':'Turkish','vi':'Vietnamese','zh':'Chinese','ca':'Catalan'}
LF={442:'ca'}
h=json.load(open('new-hits.json')); keys=json.load(open('listing-keys.json')); kb=json.load(open('listing-b-keys.json'))
k=lambda i: keys[i] if i<400 else kb[i-400]
TY={'dissertation':'thesis','book':'book','book-chapter':'book chapter','report':'report'}
G={}
for i,t in T.items():
    w=h[k(i)]; l=LF.get(i) or w.get('language')
    G[str(i)]='%s-language %s (%s) on %s. Title-level gloss; content not reviewed.'%(LN[l],TY.get(w.get('type'),'paper'),w.get('publication_year') or 'n.d.',t)
json.dump(G,open('glosses.json','w'),ensure_ascii=False,indent=0); json.dump({'442':'ca','266':'en'},open('langfix.json','w'))
print(len(G)); print(G['443'])
