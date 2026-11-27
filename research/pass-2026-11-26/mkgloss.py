"""pass-2026-11-26 English title-level glosses (Grok Bot, from the titles only; content not reviewed) for non-English records.
Discovery records -> glosses.json (by listing idx); retry-list records -> glossT.json (by record title); language fixes -> langfix.json."""
import json
T={230:'precast elements made with recycled concrete — results of the SeRaMCo research project',
231:'durable, sustainable bridge parapet caps with non-metallic reinforcement and recycled concrete',
232:'the Ludwigsburg district office building (Kreishaus) — new approaches to using recycled concrete',
237:'a technical, economic and environmental analysis of making concrete blocks with recycled PET',
240:'properties of recycled-aggregate concrete made with active and inert additions',
242:'plastic shrinkage of recycled-aggregate concretes, measuring the influence of the aggregates\' degree of saturation',
244:'controlling the effective water content in recycled-aggregate concretes',
245:'upgrading fines and aggregates from recycled concrete as cementitious materials',
246:'experimental characterisation and multi-scale modelling of the mechanical and durability properties of recycled-aggregate concretes',
248:'compressive strength and porosity of porous (pervious) concrete with a Styrofoam filler',
249:'the effect of varying the coarse aggregate in porous concrete on compressive strength and porosity',
250:'the relationship between porous-concrete properties and coarse-aggregate composition',
251:'adding varying amounts of Sikacim (an admixture) to porous concrete',
252:'designing hollow/porous concrete with varying water-cement ratio as an environmentally friendly concrete',
253:'using recycled concrete aggregate in porous concrete',
270:'the performance of concretes with recycled red-ceramic (brick) aggregates',
273:'producing lightweight concrete with recycled aggregates',
405:'a prototype pervious-concrete design for recreational areas at the University of Milagro (UNEMI), Ecuador',
406:'the effect of slab compaction and base-course fines on the flexural-tensile strength and permeability of porous concrete for permeable parking pavements',
431:'a detailed study of the shape and size effect for the widespread use of small cube specimens in concrete compressive-strength testing',
435:'decision-tree-algorithm concrete mix design for low, medium and high strength',
436:'an experimental study of how the recycled coarse-aggregate ratio affects the development of compressive strength and elastic modulus of concrete over time',
437:'the effect of recycled aggregate from construction waste on the properties of pervious (drainage) concrete',
439:'the effect of recycled lightweight aggregate from demolition waste on selected physical and mechanical properties of lightweight concrete',
441:'an experimental study using fine recycled aggregate from red-brick masonry in self-compacting concrete with high fly-ash content',
442:'using recycled red brick as coarse aggregate in self-compacting concrete with high fly-ash content',
236:'the effect of recycled aggregate on the properties of concrete',
247:'characterisation of recycled concrete aggregates',
254:'SFRC (steel-fibre-reinforced concrete) paving on steel bridge decks — a new relationship between steel and concrete',
255:'how the type and dosage of set accelerator affect the quality of sprayed concrete (shotcrete)',
256:'aggregate distribution and compaction characteristics of very stiff (roller-compacted-type) concrete studied by X-ray CT',
257:'fresh properties and rebound of sprayed concrete as mix-design factors change',
258:'a field construction trial of high-strength, high-toughness sprayed concrete',
259:'a full-scale demonstration test of concrete for high-performance underground diaphragm walls',
269:'the technical feasibility of concretes with recycled construction and demolition waste aggregates',
401:'pervious concrete as a sustainable alternative',
408:'an economic evaluation of concrete versus conventional (bituminous) pavements on the French national road network',
410:'pumping (hydraulic erosion) in concrete pavements and the erodibility of subbase and formation materials',
413:'concrete pavements — problems caused by water in their structure',
415:'concrete pavements — porous-concrete emergency stopping lanes, a study of the material',
416:'industrial concrete floors/pavements',
417:'recycled concrete with high recycled-aggregate contents — practical aspects and case studies',
420:'recycled concrete with steel slag',
421:'recycled concrete for Hundertwasser\'s Waldspirale residential complex (Darmstadt)',
422:'developing a heating-and-rubbing method to recover high-quality aggregate from concrete rubble',
423:'trials recovering high-quality recycled aggregate from demolished concrete',
424:'aggregate recycling from concrete waste using a new processing system',
425:'a study of aggregate recycling methods for concrete waste',
426:'field application cases of concrete with two kinds of recycled coarse aggregate',
427:'full-scale use of 12,500 m3 of recycled-aggregate concrete in a building frame (Heiwajima warehouse A-1 reconstruction, Tokyo Danchi Soko)',
428:'how the physical properties of recycled fine aggregate affect concrete properties',
429:'mechanical properties of porous concrete made with low-quality recycled aggregate',
430:'improving concrete compressive-strength prediction with the wavelet transform'}
LN={'de':'German','es':'Spanish','fr':'French','id':'Indonesian','it':'Italian','ja':'Japanese','pl':'Polish','pt':'Portuguese','tr':'Turkish','vi':'Vietnamese','zh':'Chinese','ro':'Romanian','nl':'Dutch'}
TY={'Paper':'paper','Thesis':'thesis','Book':'book','Book chapter':'book chapter','Report':'report'}
P=json.load(open('plan.json'))
G={}
for r in P['recs']:
    i=r.get('_idx')
    if i in T: G[str(i)]='%s-language %s (%s) on %s. Title-level gloss; content not reviewed.'%(LN[r['lang']],TY.get(r['type'],'paper'),(r['date'] or 'n.d.')[:4],T[i])
json.dump(G,open('glosses.json','w'),ensure_ascii=False,indent=0)
RT={"Contribution à l'étude du rôle de fibres dispersées anisotropiquement dans le mortier de ciment sur les lois de comportement, les critères de résistance et la fissuration du matériau":'French-language doctoral thesis (1988) on the role of anisotropically dispersed fibres in cement mortar: constitutive laws, strength criteria and cracking of the material. Catalogue-level gloss; content not reviewed.',
'CERCETAREA EXPERIMENTALĂ, COMPONENTĂ ESENŢIALĂ ÎN APLICAREA DIFERITELOR METODE DE STABILIRE A DURATEI DE SERVICIU A CONSTRUCŢIILOR DIN BETON EXPERIMENTAL RESEARCH, ESSENTIAL COMPONENT IN THE APPLICATION OF DIFFERENT METHODS TO ESTABLISH THE SERVICE LIFE DESIGN OF CONCRETE STRUCTURES':'Romanian-language paper (2011, Romanian Journal of Materials) on experimental research as an essential part of the different methods for service-life design of concrete structures (bilingual title). Title-level gloss; content not reviewed.',
'Microstructure Formation in Cement Mortars Modified With Water-Soluble Polymers (Microstructuuropbouw bij cementmortels gemodificeerd met wateroplosbare polymeren)':'KU Leuven doctoral thesis (2007) on microstructure formation in cement mortars modified with water-soluble polymers (English title with Dutch subtitle). Title-level description; content not reviewed.',
'PEMANFAATAN BAHAN ADDITIVE ABU SEKAM PADI PADA CEMENT PORTLAND PT SEMEN BATURAJA (PERSERO)':'Indonesian-language paper (2012) on using rice-husk ash as an additive in Portland cement at PT Semen Baturaja (Persero). Title-level gloss; content not reviewed.',
'YÜKSEK DAYANIMLI BETON ÜRETİMİNDE ÇİMENTO ve SÜPERAKIŞKANLAŞTIRICI BETON KATKI MADDELERİNİN ETKİNLİĞİ':'Turkish-language paper (2002, Sakarya University Journal of Science) on the effectiveness of cement and superplasticizing admixtures in producing high-strength concrete. Title-level gloss; content not reviewed.',
'セメントの水和反応および微細組織形成に及ぼす初期高温履歴の影響':'Japanese-language paper (2001) on how an early high-temperature history affects cement hydration and microstructure formation. Catalogue-level gloss; content not reviewed.',
'石灰石微粉末を添加したセメントのX線回折/リートベルト法による水和反応解析と強度発現機構に関する検討':'Japanese-language paper (2006) analysing the hydration of cement with added fine limestone powder by X-ray diffraction/Rietveld analysis and examining its strength-development mechanism. Catalogue-level gloss; content not reviewed.',
"Conception des bétons pour une durée de vie donnée des ouvrages : maîtrise de la durabilité vis-à-vis de la corrosion des armatures et de l'alcali-réaction : état de l'art et guide pour la mise en oeuvre d'une approche performantielle et prédictive sur la base d'indicateurs de durabilité":'French-language AFGC guide (2004) on designing concrete for a specified structural service life: controlling durability against reinforcement corrosion and alkali-aggregate reaction; state of the art and guide to a performance-based, predictive approach using durability indicators. Catalogue-level gloss; content not reviewed.',
'La influencia de las cenizas volantes como sustituto parcial del cemento Pórtland en la durabilidad del hormigón: propiedades físicas, difusión del ión cloruro y del dióxido de carbono':'Spanish-language paper (2008) on fly ash as a partial Portland-cement replacement and concrete durability: physical properties, chloride-ion and carbon-dioxide diffusion. Title-level gloss; content not reviewed.',
'Nowe dodatki mineralne do betonu':'Polish-language paper (2011, Budownictwo i Inżynieria Środowiska) on new mineral additions for concrete. Title-level gloss; content not reviewed.',
'MODEL EXPERIMENTAL DE RECICLARE A UNUI DEŞEU DIN INDUSTRIA HÂRTIEI CA MATERIE PRIMĂ SECUNDARĂ ÎN BETON AN EXPERIMENTAL MODEL OF WASTE RECYCLING FROM PAPER INDUSTRY AS SECONDARY RAW MATERIAL IN CONCRETE':'Romanian-language paper (2014, Romanian Journal of Materials) on an experimental model for recycling a paper-industry waste as a secondary raw material in concrete (bilingual title). Title-level gloss; content not reviewed.',
'FLY ASH SEBAGAI BAHAN PENGGANTI SEMEN PADA BETON':'Indonesian-language paper (2018) on fly ash as a cement replacement in concrete. Title-level gloss; content not reviewed.'}
json.dump(RT,open('glossT.json','w'),ensure_ascii=False,indent=0)
json.dump({'296':'en','298':'en','299':'en','300':'en','301':'en','302':'en','304':'en'},open('langfix.json','w'))
print(len(G),len(RT))
