# Cement reaction stoichiometry table

Generated 2026-11-20 from `data/reactions.json`. 40 reactions; 163 sourced values, 589 derived values, 64 unknown fields.

> Idealised end-state stoichiometry for orientation. Real hydrate compositions, especially C-S-H, AFm, AFt and gels, vary with composition, temperature, w/c and age. Not a substitute for testing or thermodynamic modelling (e.g. GEMS with Cemdata18).

Each number is tagged **sourced** (copied from a source opened and read on 2026-11-20), **derived** (computed from sourced numbers and CIAAW atomic weights), or **unknown** (left blank instead of guessed). Index R numbers point to records in `data/site-data.json`; `NEW-*` sources are recorded in `research/reactions-candidates.jsonl` for the daily run to verify and number.

Notation: C = CaO, S = SiO2, A = Al2O3, F = Fe2O3, s = SO3, c = CO2, H = H2O, M = MgO, CH = Ca(OH)2.

## Sources

- **R210** (index): W. Lerch, R.H. Bogue (1934). *Heat of hydration of portland cement pastes (NBS RP684)*. https://doi.org/10.6028/jres.012.057 — inspected at https://nvlpubs.nist.gov/nistpubs/jres/12/jresv12n5p645_A2b.pdf. Used for: Heats of complete hydration of C3S, beta-C2S, C3A, C4AF (Table 1 and summary); MgO and free CaO values the authors took from the literature; 149 cal/g SO3 for sulfoaluminate formation; 3.7 and 2.7 kcal/mol for hemihydrate and soluble anhydrite to gypsum; clinker test cases (Table 1, series K-3).
- **R334** (index): B. Lothenbach, D.A. Kulik, T. Matschei, M. Balonis, L. Baquerizo, B. Dilnesa, G.D. Miron, R.J. Myers (2019). *Cemdata18: A chemical thermodynamic database for hydrated Portland cements and alkali-activated materials*. https://doi.org/10.1016/j.cemconres.2018.04.018 — inspected at https://www.dora.lib4ri.ch/psi/dload/psi:25804/PDF2/view (accepted manuscript). Used for: Standard molar volumes V° (cm3/mol) and enthalpies of formation ΔfH° (kJ/mol) at 25 °C, Tables 1, 3 and 4; statement that calcium carbonate prevents destabilisation of ettringite to monosulfate.
- **R880** (index): S.-H. Shim, T.-H. Lee, S.-J. Yang, N.B.Md. Noor, J.-H.-J. Kim (2021). *Calculation of Cement Composition Using a New Model Compared to the Bogue Model*. https://doi.org/10.3390/ma14164663 — inspected at https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8401079/fullTextXML. Used for: Bogue equations as given for ASTM C150 including SO3 and CO2 terms, Eqs. (5)-(8).
- **R330** (index): F. Winnefeld, B. Lothenbach (2010). *Hydration of calcium sulfoaluminate cements — Experimental findings and thermodynamic modelling*. https://doi.org/10.1016/j.cemconres.2009.08.014 — inspected at https://www.dora.lib4ri.ch/empa/dload/empa:3987/PDF2/view (accepted manuscript). Used for: Ye'elimite hydration with and without calcium sulfate (Eqs. 1-2) and strätlingite formation from belite and AH3 (Eq. 3); strätlingite only stable without portlandite.
- **R372** (index): S. Shirani, A. Cuesta, A.G. De la Torre, A. Diaz, P. Trtik, M. Holler, M.A.G. Aranda (2020). *Calcium aluminate cement conversion analysed by ptychographic nanotomography*. https://doi.org/10.1016/j.cemconres.2020.106201 — inspected at https://www.dora.lib4ri.ch/psi/dload/psi:34224/PDF2/view (submitted manuscript). Used for: CA hydration and conversion reactions (1)-(5) with molar masses, densities, molar volumes and theoretical chemical shrinkage / secondary porosity (Tables 1-2).
- **R1882** (index): Huang Cheng-yi, R.F. Feldman (1985). *Hydration reactions in portland cement-silica fume blends*. https://doi.org/10.1016/0008-8846(85)90056-0 — inspected at https://nrc-publications.canada.ca/eng/view/ft/?id=d6e9dce9-a723-44fc-92a1-1e3e46143b6c. Used for: Cement, silica fume and fly ash oxide analyses and Bogue phases (Table I); Ca(OH)2 contents of plain and silica-fume pastes (test cases).
- **R3883** (index): P.D. Tennis, H.M. Jennings (2000). *A model for two types of calcium silicate hydrate in the microstructure of Portland cement pastes*. https://doi.org/10.1016/s0008-8846(00)00257-x — inspected at https://web.archive.org/web/20240413122239/https://hal.science/hal-03680316/document. Used for: Hydration reactions Eqs. (1)-(6) with C3.4S2H8 (=C1.7SH4) C-S-H; densities and molar masses (Table 1); saturated C-S-H density 1990 kg/m3; Avrami constants for degree of hydration by phase (Table 2).
- **R3079** (index): M.A.G. Aranda, ... (review) (2019). *Advances in understanding ye'elimite-rich cements*. https://doi.org/10.1016/j.cemconres.2019.105778 — inspected at https://web.archive.org/web/20240414205653/https://hal.science/hal-02386829/document. Used for: Context only: CAH10 can form with ettringite and AH3 when calcium sulfate is low; AH3 gel density about 1.5 g/cm3 in CSA paste versus 2.40 g/cm3 for gibbsite.
- **NEW-BENTZ-2005** (new-candidate): D.P. Bentz (2005). *CEMHYD3D: A Three-Dimensional Cement Hydration and Microstructure Development Modeling Package. Version 3.0 (NIST IR 7232)*. https://doi.org/10.6028/NIST.IR.7232 — inspected at https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nistir7232.pdf. Used for: Molar volumes, specific gravities and heats of formation of cement phases and hydrates as coded in disrealnew.c (Appendix B, after Fukuhara et al. 1981); pozzolanic C1.1SH3.9 product; 780 J/g silica fume, 800 J/g slag, 800 J/g AS heats; slag hydration product stoichiometries (Table 2) and slagchar.dat example.
- **NEW-BENTZ-2009** (new-candidate): D.P. Bentz, E.F. Irassar, B.E. Bucher, W.J. Weiss (2009). *Limestone Fillers Conserve Cement; Part 1: An analysis based on Powers' model*. https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=901137 — inspected at https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=923437 (manuscript) and pub_id=901137 (Concrete International 31(11) 41-46). Used for: Powers' model volume fractions with Jensen & Hansen parameters (non-evaporable water 0.23, chemical shrinkage 0.064, gel water 0.19 g/g), inert limestone filler, and worked results (w/c 0.356, 0.42, 8.7 % porosity, w/cm 0.338-0.267).
- **NEW-LEON-CHEN-2021** (new-candidate): G. Leon, H.-L. Chen (2021). *Thermal Analysis of Mass Concrete Containing Ground Granulated Blast Furnace Slag*. https://doi.org/10.3390/civileng2010014 — inspected at https://www.mdpi.com/2673-4109/2/1/14. Used for: Secondary citation of Schindler & Folliard (2005): ultimate heat of GGBFS 461 J/g (Grade 100) and 550 J/g (Grade 120).
- **NEW-NIST-WEBBOOK-CO2** (new-candidate): NIST (n.d.). *Carbon dioxide — Gas phase thermochemistry data (NIST Chemistry WebBook, SRD 69)*. https://webbook.nist.gov/cgi/cbook.cgi?ID=C124389&Mask=1 — inspected at https://webbook.nist.gov/cgi/cbook.cgi?ID=C124389&Mask=1. Used for: ΔfH° CO2(g) = -393.51 kJ/mol (CODATA).
- **NEW-CIAAW** (new-candidate): IUPAC Commission on Isotopic Abundances and Atomic Weights (CIAAW) (n.d.). *Abridged Standard Atomic Weights*. https://www.ciaaw.org/abridged-atomic-weights.htm — inspected at https://www.ciaaw.org/abridged-atomic-weights.htm. Used for: Atomic weights for all derived molar masses.

## Reactions

### RX01 · Alite (C3S) hydration

- Family: Clinker silicates
- Chemical: Ca3SiO5 + 5.3 H2O → (CaO)1.7·SiO2·(H2O)4 + 1.3 Ca(OH)2
- Cement notation: `C3S + 5.3H → C1.7SH4 + 1.3CH`
- Scheme basis: sourced
- C-S-H assumed: C1.7SH4 (Ca/Si 1.7, H/Si 4.0, saturated) — Tennis & Jennings write 2 Si as C3.4S2H8; Bentz CEMHYD3D uses C1.7SH4.0 with 108 cm3/mol.
  - alternative C3.4S2H8 (Ca/Si 1.7, H/Si 4.0): Same stoichiometry per Si (Tennis & Jennings Eq. 1-2). [R3883]
  - alternative C3.4S2H3 (D-dried) (Ca/Si 1.7, H/Si 1.5): Dried composition, density 1440 (LD) / 1750 (HD) kg/m3. [R3883]
  - alternative C1.67SH2.1 (CSH-II 'Jen' end member) (Ca/Si 1.67, H/Si 2.1): Thermodynamic end member, V° 78 cm3/mol; not saturated-gel water. [R334]
  - alternative C2SHx (Lerch & Bogue product) (Ca/Si 2.0, H/Si None): Lerch & Bogue state their 'complete hydration' heats correspond to conversion to 2CaO·SiO2·xH2O, not 3CaO·2SiO2·xH2O. [R210]
- Per gram of C3S: water 0.4182 g H2O per g C3S [derived; NEW-CIAAW]; CH 0.4219 g CH per g C3S [derived; NEW-CIAAW]
- Heat: 502.0 J/g [sourced; R210] — 120 cal/g C3S, heat of complete hydration (Lerch & Bogue 1934, Table 1 and summary); converted at 4.184 J/cal (conversion derived).
- Heat: 535.0 J per g C3S (heat released, +) [derived; NEW-BENTZ-2005] — ΔrH° = -122.2 kJ per 1 mol C3S, from standard enthalpies of formation at 25 °C (NEW-BENTZ-2005). Mixed-source sets are approximate.
- Chemical shrinkage: 0.0695 cm3 per g C3S [derived; NEW-BENTZ-2005] — (ΣV reactants incl. water - ΣV products) = 15.86 cm3 per 1 mol C3S; 9.5 % of reactant volume. Positive = volume loss.

| Species | Side | Coef | M (g/mol) | g per g key | V (cm3/mol) | ρ (g/cm3) |
|---|---|---|---|---|---|---|
| Ca3SiO5 (alite, C3S) | reactant | 1 | 228.31 | -1.0 | 71.13 [NEW-BENTZ-2005] | 3.21 |
| H2O (liquid) | reactant | 5.3 | 18.02 | -0.4182 | 18.07 [NEW-BENTZ-2005] | 0.997 |
| C1.7SH4 (saturated C-S-H; = C3.4S2H8 per 2 Si) | product | 1 | 227.47 | 0.9963 | 108.0 [NEW-BENTZ-2005] | 2.106 |
| Ca(OH)2 (portlandite, CH) | product | 1.3 | 74.09 | 0.4219 | 33.1 [NEW-BENTZ-2005] | 2.238 |

Conditions and caveats: Ideal end-state reaction; C-S-H Ca/Si and water content vary with w/c, temperature, drying and SCMs. Heats from Lerch & Bogue refer to a C2S·xH2O end product.

Sources: NEW-BENTZ-2005, R3883

### RX02 · Belite (C2S) hydration

- Family: Clinker silicates
- Chemical: Ca2SiO4 + 4.3 H2O → (CaO)1.7·SiO2·(H2O)4 + 0.3 Ca(OH)2
- Cement notation: `C2S + 4.3H → C1.7SH4 + 0.3CH`
- Scheme basis: sourced
- C-S-H assumed: C1.7SH4 (Ca/Si 1.7, H/Si 4.0, saturated) — Tennis & Jennings write 2 Si as C3.4S2H8; Bentz CEMHYD3D uses C1.7SH4.0 with 108 cm3/mol.
  - alternative C3.4S2H8 (Ca/Si 1.7, H/Si 4.0): Same stoichiometry per Si (Tennis & Jennings Eq. 1-2). [R3883]
  - alternative C3.4S2H3 (D-dried) (Ca/Si 1.7, H/Si 1.5): Dried composition, density 1440 (LD) / 1750 (HD) kg/m3. [R3883]
  - alternative C1.67SH2.1 (CSH-II 'Jen' end member) (Ca/Si 1.67, H/Si 2.1): Thermodynamic end member, V° 78 cm3/mol; not saturated-gel water. [R334]
  - alternative C2SHx (Lerch & Bogue product) (Ca/Si 2.0, H/Si None): Lerch & Bogue state their 'complete hydration' heats correspond to conversion to 2CaO·SiO2·xH2O, not 3CaO·2SiO2·xH2O. [R210]
- Per gram of C2S: water 0.4498 g H2O per g C2S [derived; NEW-CIAAW]; CH 0.1291 g CH per g C2S [derived; NEW-CIAAW]
- Heat: 259.0 J/g [sourced; R210] — 62 cal/g β-C2S, heat of complete hydration (Lerch & Bogue 1934, Table 1 and summary); converted at 4.184 J/cal (conversion derived).
- Heat: 222.0 J per g C2S (heat released, +) [derived; NEW-BENTZ-2005] — ΔrH° = -38.2 kJ per 1 mol C2S, from standard enthalpies of formation at 25 °C (NEW-BENTZ-2005). Mixed-source sets are approximate.
- Chemical shrinkage: 0.0713 cm3 per g C2S [derived; NEW-BENTZ-2005] — (ΣV reactants incl. water - ΣV products) = 12.28 cm3 per 1 mol C2S; 9.4 % of reactant volume. Positive = volume loss.

| Species | Side | Coef | M (g/mol) | g per g key | V (cm3/mol) | ρ (g/cm3) |
|---|---|---|---|---|---|---|
| Ca2SiO4 (belite, C2S) | reactant | 1 | 172.24 | -1.0 | 52.51 [NEW-BENTZ-2005] | 3.28 |
| H2O (liquid) | reactant | 4.3 | 18.02 | -0.4498 | 18.07 [NEW-BENTZ-2005] | 0.997 |
| C1.7SH4 (saturated C-S-H; = C3.4S2H8 per 2 Si) | product | 1 | 227.47 | 1.3207 | 108.0 [NEW-BENTZ-2005] | 2.106 |
| Ca(OH)2 (portlandite, CH) | product | 0.3 | 74.09 | 0.1291 | 33.1 [NEW-BENTZ-2005] | 2.238 |

Conditions and caveats: Lerch & Bogue's β-C2S still held about 2-3 % unhydrated material when its heat was measured.

Sources: NEW-BENTZ-2005, R3883

### RX03 · C3A + gypsum → ettringite

- Family: Clinker aluminate (C3A)
- Chemical: Ca3Al2O6 + 3 CaSO4·2H2O + 26 H2O → Ca6Al2(SO4)3(OH)12·26H2O
- Cement notation: `C3A + 3CsH2 + 26H → C6As3H32`
- Scheme basis: sourced
- C-S-H assumed: None (no C-S-H).
- Per gram of C3A: water 1.7335 g H2O per g C3A [derived; NEW-CIAAW]; CH 0.0 g CH per g C3A [derived; NEW-CIAAW]
- Heat: 623.0 J per g SO3 combined (in addition to the C3A heat) [sourced; R210] — 149 cal/g SO3 for 3CaO·Al2O3·6H2O + 3CaSO4·2H2O + 19H2O → 3CaO·Al2O3·3CaSO4·31H2O (computed by Lerch & Bogue); converted at 4.184 J/cal.
- Heat: 1672.0 J per g C3A (heat released, +) [derived; NEW-BENTZ-2005] — ΔrH° = -451.8 kJ per 1 mol C3A, from standard enthalpies of formation at 25 °C (NEW-BENTZ-2005). Mixed-source sets are approximate.
- Chemical shrinkage: 0.1715 cm3 per g C3A [derived; NEW-BENTZ-2005] — (ΣV reactants incl. water - ΣV products) = 46.33 cm3 per 1 mol C3A; 5.9 % of reactant volume. Positive = volume loss.

| Species | Side | Coef | M (g/mol) | g per g key | V (cm3/mol) | ρ (g/cm3) |
|---|---|---|---|---|---|---|
| Ca3Al2O6 (C3A) | reactant | 1 | 270.19 | -1.0 | 88.94 [NEW-BENTZ-2005] | 3.038 |
| CaSO4·2H2O (gypsum) | reactant | 3 | 172.16 | -1.9116 | 74.21 [NEW-BENTZ-2005] | 2.32 |
| H2O (liquid) | reactant | 26 | 18.02 | -1.7335 | 18.07 [NEW-BENTZ-2005] | 0.997 |
| C6As3H32 (ettringite, AFt) | product | 1 | 1255.07 | 4.6451 | 735.01 [NEW-BENTZ-2005] | 1.708 |

Conditions and caveats: Early reaction while calcium sulfate is available. Lerch & Bogue give 149 cal per g SO3 for gypsum + C3A hydrate → sulfoaluminate (computed, on top of the C3A heat).

Sources: NEW-BENTZ-2005, R210, R3883

### RX04 · Ettringite → monosulfate (sulfate depleted)

- Family: Clinker aluminate (C3A)
- Chemical: 2 Ca3Al2O6 + Ca6Al2(SO4)3(OH)12·26H2O + 4 H2O → 3 Ca4Al2(SO4)(OH)12·6H2O
- Cement notation: `2C3A + C6As3H32 + 4H → 3C4AsH12`
- Scheme basis: sourced
- C-S-H assumed: None.
- Per gram of C3A: water 0.1333 g H2O per g C3A [derived; NEW-CIAAW]; CH 0.0 g CH per g C3A [derived; NEW-CIAAW]
- Heat: 881.0 J per g C3A (heat released, +) [derived; NEW-BENTZ-2005] — ΔrH° = -476.1 kJ per 2 mol C3A, from standard enthalpies of formation at 25 °C (NEW-BENTZ-2005). Mixed-source sets are approximate.
- Chemical shrinkage: 0.0864 cm3 per g C3A [derived; NEW-BENTZ-2005] — (ΣV reactants incl. water - ΣV products) = 46.70 cm3 per 2 mol C3A; 4.7 % of reactant volume. Positive = volume loss.

| Species | Side | Coef | M (g/mol) | g per g key | V (cm3/mol) | ρ (g/cm3) |
|---|---|---|---|---|---|---|
| Ca3Al2O6 (C3A) | reactant | 2 | 270.19 | -1.0 | 88.94 [NEW-BENTZ-2005] | 3.038 |
| C6As3H32 (ettringite, AFt) | reactant | 1 | 1255.07 | -2.3226 | 735.01 [NEW-BENTZ-2005] | 1.708 |
| H2O (liquid) | reactant | 4 | 18.02 | -0.1333 | 18.07 [NEW-BENTZ-2005] | 0.997 |
| C4AsH12 (monosulfate, AFm) | product | 3 | 622.51 | 3.4559 | 312.82 [NEW-BENTZ-2005] | 1.99 |

Conditions and caveats: Proceeds after calcium sulfate is consumed. In the presence of calcite, carboaluminates form instead and ettringite stays stable (see RX16).

Sources: NEW-BENTZ-2005, R3883

### RX05 · C3A hydration without sulfate → hydrogarnet

- Family: Clinker aluminate (C3A)
- Chemical: Ca3Al2O6 + 6 H2O → Ca3Al2(OH)12
- Cement notation: `C3A + 6H → C3AH6`
- Scheme basis: sourced
- C-S-H assumed: None.
- Per gram of C3A: water 0.4 g H2O per g C3A [derived; NEW-CIAAW]; CH 0.0 g CH per g C3A [derived; NEW-CIAAW]
- Heat: 866.0 J/g [sourced; R210] — 207 cal/g C3A, heat of complete hydration (Lerch & Bogue 1934, Table 1 and summary); converted at 4.184 J/cal (conversion derived).
- Heat: 908.0 J per g C3A (heat released, +) [derived; NEW-BENTZ-2005] — ΔrH° = -245.2 kJ per 1 mol C3A, from standard enthalpies of formation at 25 °C (NEW-BENTZ-2005). Mixed-source sets are approximate.
- Chemical shrinkage: 0.1748 cm3 per g C3A [derived; NEW-BENTZ-2005] — (ΣV reactants incl. water - ΣV products) = 47.23 cm3 per 1 mol C3A; 23.9 % of reactant volume. Positive = volume loss.

| Species | Side | Coef | M (g/mol) | g per g key | V (cm3/mol) | ρ (g/cm3) |
|---|---|---|---|---|---|---|
| Ca3Al2O6 (C3A) | reactant | 1 | 270.19 | -1.0 | 88.94 [NEW-BENTZ-2005] | 3.038 |
| H2O (liquid) | reactant | 6 | 18.02 | -0.4 | 18.07 [NEW-BENTZ-2005] | 0.997 |
| Ca3Al2(OH)12 (hydrogarnet / katoite, C3AH6) | product | 1 | 378.28 | 1.4 | 150.12 [NEW-BENTZ-2005] | 2.52 |

Conditions and caveats: Stable end product of pure C3A hydration; flash set in cement if no sulfate. Lerch & Bogue's 207 cal/g is for this complete hydration (Thorvaldson reported 214.3 cal/g to C3AH6).

Sources: NEW-BENTZ-2005, R210

### RX06 · C3A + CH without sulfate → C4AH13

- Family: Clinker aluminate (C3A)
- Chemical: Ca3Al2O6 + Ca(OH)2 + 12 H2O → Ca4Al2(OH)14·6H2O
- Cement notation: `C3A + CH + 12H → C4AH13`
- Scheme basis: sourced
- C-S-H assumed: None.
- Per gram of C3A: water 0.8001 g H2O per g C3A [derived; NEW-CIAAW]; CH -0.2742 g CH per g C3A [derived; NEW-CIAAW]
- Heat: 1060.0 J per g C3A (heat released, +) [derived; NEW-BENTZ-2005, R334] — ΔrH° = -286.4 kJ per 1 mol C3A, from standard enthalpies of formation at 25 °C (NEW-BENTZ-2005, R334). Mixed-source sets are approximate.
- Chemical shrinkage: 0.2399 cm3 per g C3A [derived; NEW-BENTZ-2005, R334] — (ΣV reactants incl. water - ΣV products) = 64.82 cm3 per 1 mol C3A; 19.1 % of reactant volume. Positive = volume loss.

| Species | Side | Coef | M (g/mol) | g per g key | V (cm3/mol) | ρ (g/cm3) |
|---|---|---|---|---|---|---|
| Ca3Al2O6 (C3A) | reactant | 1 | 270.19 | -1.0 | 89 [R334] | 3.036 |
| Ca(OH)2 (portlandite, CH) | reactant | 1 | 74.09 | -0.2742 | 33 [R334] | 2.245 |
| H2O (liquid) | reactant | 12 | 18.02 | -0.8001 | 18.07 [NEW-BENTZ-2005] | 0.997 |
| C4AH13 (hydroxy-AFm) | product | 1 | 560.46 | 2.0743 | 274 [R334] | 2.045 |

Conditions and caveats: Tennis & Jennings Eq. 5: continued C3A hydration after all ettringite is consumed.

Sources: R334, R3883

### RX07 · C4AF + gypsum → Fe-bearing ettringite + CH + FH3

- Family: Clinker ferrite (C4AF)
- Chemical: Ca4Al2Fe2O10 + 3 CaSO4·2H2O + 30 H2O → Ca6Al2(SO4)3(OH)12·26H2O + Ca(OH)2 + Fe2O3·3H2O
- Cement notation: `C4AF + 3CsH2 + 30H → C6As3H32 + CH + FH3`
- Scheme basis: derived
- C-S-H assumed: None.
- Per gram of C4AF: water 1.1121 g H2O per g C4AF [derived; NEW-CIAAW]; CH 0.1525 g CH per g C4AF [derived; NEW-CIAAW]
- Heat: 418.0 J/g [sourced; R210] — 100 cal/g C4AF, heat of complete hydration (end state, not this specific path) (Lerch & Bogue 1934, Table 1 and summary); converted at 4.184 J/cal (conversion derived).
- Chemical shrinkage: 0.1174 cm3 per g C4AF [derived; NEW-BENTZ-2005] — (ΣV reactants incl. water - ΣV products) = 57.05 cm3 per 1 mol C4AF; 6.4 % of reactant volume. Positive = volume loss.

| Species | Side | Coef | M (g/mol) | g per g key | V (cm3/mol) | ρ (g/cm3) |
|---|---|---|---|---|---|---|
| Ca4Al2Fe2O10 (C4AF) | reactant | 1 | 485.96 | -1.0 | 130.29 [NEW-BENTZ-2005] | 3.73 |
| CaSO4·2H2O (gypsum) | reactant | 3 | 172.16 | -1.0628 | 74.21 [NEW-BENTZ-2005] | 2.32 |
| H2O (liquid) | reactant | 30 | 18.02 | -1.1121 | 18.07 [NEW-BENTZ-2005] | 0.997 |
| C6As3H32 (ettringite, AFt) | product | 1 | 1255.07 | 2.5827 | 735.01 [NEW-BENTZ-2005] | 1.708 |
| Ca(OH)2 (portlandite, CH) | product | 1 | 74.09 | 0.1525 | 33.1 [NEW-BENTZ-2005] | 2.238 |
| Fe2O3·3H2O (FH3, iron hydroxide) | product | 1 | 213.73 | 0.4398 | 69.8 [NEW-BENTZ-2005] | 3.062 |

Conditions and caveats: Simplified: iron is written as separate FH3 and the AFt as Al-ettringite. Phase set as coded in CEMHYD3D (ETTRC4AF, FH3, CH); balance derived here. Real ferrite reacts slowly and Fe partly enters AFt/AFm/hydrogarnet.

Sources: NEW-BENTZ-2005

### RX08 · C4AF + ettringite → monosulfate + CH + FH3

- Family: Clinker ferrite (C4AF)
- Chemical: 2 Ca4Al2Fe2O10 + Ca6Al2(SO4)3(OH)12·26H2O + 12 H2O → 3 Ca4Al2(SO4)(OH)12·6H2O + 2 Ca(OH)2 + 2 Fe2O3·3H2O
- Cement notation: `2C4AF + C6As3H32 + 12H → 3C4AsH12 + 2CH + 2FH3`
- Scheme basis: derived
- C-S-H assumed: None.
- Per gram of C4AF: water 0.2224 g H2O per g C4AF [derived; NEW-CIAAW]; CH 0.1525 g CH per g C4AF [derived; NEW-CIAAW]
- Heat: unknown — no measured heat and incomplete enthalpy-of-formation data in the inspected sources
- Chemical shrinkage: 0.0701 cm3 per g C4AF [derived; NEW-BENTZ-2005] — (ΣV reactants incl. water - ΣV products) = 68.14 cm3 per 2 mol C4AF; 5.6 % of reactant volume. Positive = volume loss.

| Species | Side | Coef | M (g/mol) | g per g key | V (cm3/mol) | ρ (g/cm3) |
|---|---|---|---|---|---|---|
| Ca4Al2Fe2O10 (C4AF) | reactant | 2 | 485.96 | -1.0 | 130.29 [NEW-BENTZ-2005] | 3.73 |
| C6As3H32 (ettringite, AFt) | reactant | 1 | 1255.07 | -1.2913 | 735.01 [NEW-BENTZ-2005] | 1.708 |
| H2O (liquid) | reactant | 12 | 18.02 | -0.2224 | 18.07 [NEW-BENTZ-2005] | 0.997 |
| C4AsH12 (monosulfate, AFm) | product | 3 | 622.51 | 1.9215 | 312.82 [NEW-BENTZ-2005] | 1.99 |
| Ca(OH)2 (portlandite, CH) | product | 2 | 74.09 | 0.1525 | 33.1 [NEW-BENTZ-2005] | 2.238 |
| Fe2O3·3H2O (FH3, iron hydroxide) | product | 2 | 213.73 | 0.4398 | 69.8 [NEW-BENTZ-2005] | 3.062 |

Conditions and caveats: Simplified analogue of RX04 for ferrite; balance derived here using the CEMHYD3D phase set.

Sources: NEW-BENTZ-2005

### RX09 · C4AF + CH without sulfate → Fe-bearing hydrogarnet

- Family: Clinker ferrite (C4AF)
- Chemical: Ca4Al2Fe2O10 + 2 Ca(OH)2 + 10 H2O → 2 Ca3(Al,Fe)2(OH)12
- Cement notation: `C4AF + 2CH + 10H → 2C3(A,F)H6`
- Scheme basis: sourced
- C-S-H assumed: None.
- Per gram of C4AF: water 0.3707 g H2O per g C4AF [derived; NEW-CIAAW]; CH -0.3049 g CH per g C4AF [derived; NEW-CIAAW]
- Heat: 418.0 J/g [sourced; R210] — 100 cal/g C4AF, heat of complete hydration (Lerch & Bogue 1934, Table 1 and summary); converted at 4.184 J/cal (conversion derived).
- Chemical shrinkage: 0.1486 cm3 per g C4AF [derived; NEW-BENTZ-2005, R3883] — (ΣV reactants incl. water - ΣV products) = 72.19 cm3 per 1 mol C4AF; 19.1 % of reactant volume. Positive = volume loss.

| Species | Side | Coef | M (g/mol) | g per g key | V (cm3/mol) | ρ (g/cm3) |
|---|---|---|---|---|---|---|
| Ca4Al2Fe2O10 (C4AF) | reactant | 1 | 485.96 | -1.0 | 130.29 [NEW-BENTZ-2005] | 3.73 |
| Ca(OH)2 (portlandite, CH) | reactant | 2 | 74.09 | -0.3049 | 33.1 [NEW-BENTZ-2005] | 2.238 |
| H2O (liquid) | reactant | 10 | 18.02 | -0.3707 | 18.07 [NEW-BENTZ-2005] | 0.997 |
| C3(A,F)H6 (Fe-bearing hydrogarnet) | product | 2 | 407.15 | 1.6756 | 152.49 [R3883] | 2.67 |

Conditions and caveats: Tennis & Jennings Eq. 6 (hydrogarnet product).

Sources: R3883

### RX10 · Hemihydrate → gypsum

- Family: Calcium sulfates
- Chemical: CaSO4·0.5H2O + 1.5 H2O → CaSO4·2H2O
- Cement notation: `CsH0.5 + 1.5H → CsH2`
- Scheme basis: sourced
- C-S-H assumed: None.
- Per gram of CsH05: water 0.1862 g H2O per g CsH05 [derived; NEW-CIAAW]; CH 0.0 g CH per g CsH05 [derived; NEW-CIAAW]
- Heat: 107.0 J per g hemihydrate [derived; R210] — From 3.7 kcal/mol (Lerch & Bogue p. 652) ÷ molar mass of CaSO4·0.5H2O; 46 cal/g SO3 as printed.
- Heat: 132.0 J per g CsH05 (heat released, +) [derived; NEW-BENTZ-2005] — ΔrH° = -19.2 kJ per 1 mol CsH05, from standard enthalpies of formation at 25 °C (NEW-BENTZ-2005). Mixed-source sets are approximate.
- Chemical shrinkage: 0.0404 cm3 per g CsH05 [derived; NEW-BENTZ-2005] — (ΣV reactants incl. water - ΣV products) = 5.87 cm3 per 1 mol CsH05; 7.3 % of reactant volume. Positive = volume loss.

| Species | Side | Coef | M (g/mol) | g per g key | V (cm3/mol) | ρ (g/cm3) |
|---|---|---|---|---|---|---|
| CaSO4·0.5H2O (hemihydrate) | reactant | 1 | 145.14 | -1.0 | 52.97 [NEW-BENTZ-2005] | 2.74 |
| H2O (liquid) | reactant | 1.5 | 18.02 | -0.1862 | 18.07 [NEW-BENTZ-2005] | 0.997 |
| CaSO4·2H2O (gypsum) | product | 1 | 172.16 | 1.1862 | 74.21 [NEW-BENTZ-2005] | 2.32 |

Conditions and caveats: Lerch & Bogue: 3.7 kcal/mol (46 cal per g SO3); they recommend leaving it out of cement heat totals (about 1 cal/g cement, variable dehydration during grinding).

Sources: NEW-BENTZ-2005, R210

### RX11 · Anhydrite → gypsum

- Family: Calcium sulfates
- Chemical: CaSO4 + 2 H2O → CaSO4·2H2O
- Cement notation: `Cs + 2H → CsH2`
- Scheme basis: sourced
- C-S-H assumed: None.
- Per gram of Cs: water 0.2647 g H2O per g Cs [derived; NEW-CIAAW]; CH 0.0 g CH per g Cs [derived; NEW-CIAAW]
- Heat: 83.0 J per g anhydrite [derived; R210] — From 2.7 kcal/mol (soluble anhydrite, Lerch & Bogue p. 652) ÷ molar mass of CaSO4; 34 cal/g SO3 as printed.
- Heat: 193.0 J per g Cs (heat released, +) [derived; NEW-BENTZ-2005] — ΔrH° = -26.3 kJ per 1 mol Cs, from standard enthalpies of formation at 25 °C (NEW-BENTZ-2005). Mixed-source sets are approximate.
- Chemical shrinkage: 0.1035 cm3 per g Cs [derived; NEW-BENTZ-2005] — (ΣV reactants incl. water - ΣV products) = 14.09 cm3 per 1 mol Cs; 16.0 % of reactant volume. Positive = volume loss.

| Species | Side | Coef | M (g/mol) | g per g key | V (cm3/mol) | ρ (g/cm3) |
|---|---|---|---|---|---|---|
| CaSO4 (anhydrite) | reactant | 1 | 136.13 | -1.0 | 52.16 [NEW-BENTZ-2005] | 2.61 |
| H2O (liquid) | reactant | 2 | 18.02 | -0.2647 | 18.07 [NEW-BENTZ-2005] | 0.997 |
| CaSO4·2H2O (gypsum) | product | 1 | 172.16 | 1.2647 | 74.21 [NEW-BENTZ-2005] | 2.32 |

Conditions and caveats: Lerch & Bogue's 2.7 kcal/mol is for soluble (γ-) anhydrite; natural (insoluble) anhydrite reacts slowly. Bentz and Cemdata18 molar volumes for anhydrite differ (52.16 vs 46 cm3/mol).

Sources: NEW-BENTZ-2005, R210

### RX12 · Free lime hydration

- Family: Free lime and periclase
- Chemical: CaO + H2O → Ca(OH)2
- Cement notation: `C + H → CH`
- Scheme basis: sourced
- C-S-H assumed: None.
- Per gram of C: water 0.3213 g H2O per g C [derived; NEW-CIAAW]; CH 1.3213 g CH per g C [derived; NEW-CIAAW]
- Heat: 1166.0 J/g [sourced; R210] — 278.6 cal/g CaO (literature value quoted by Lerch & Bogue, Thorvaldson et al.) (Lerch & Bogue 1934, p. 651); converted at 4.184 J/cal (conversion derived).
- Heat: 1144.0 J per g C (heat released, +) [derived; NEW-BENTZ-2005, R334] — ΔrH° = -64.2 kJ per 1 mol C, from standard enthalpies of formation at 25 °C (NEW-BENTZ-2005, R334). Mixed-source sets are approximate.
- Chemical shrinkage: 0.0369 cm3 per g C [derived; NEW-BENTZ-2005, R334] — (ΣV reactants incl. water - ΣV products) = 2.07 cm3 per 1 mol C; 5.9 % of reactant volume. Positive = volume loss.

| Species | Side | Coef | M (g/mol) | g per g key | V (cm3/mol) | ρ (g/cm3) |
|---|---|---|---|---|---|---|
| CaO (free lime) | reactant | 1 | 56.08 | -1.0 | 17 [R334] | 3.299 |
| H2O (liquid) | reactant | 1 | 18.02 | -0.3213 | 18.07 [NEW-BENTZ-2005] | 0.997 |
| Ca(OH)2 (portlandite, CH) | product | 1 | 74.09 | 1.3213 | 33 [R334] | 2.245 |

Conditions and caveats: Large solid-volume increase (expansion risk when hard-burnt free lime hydrates late).

Sources: R210, R334

### RX13 · Periclase (MgO) hydration

- Family: Free lime and periclase
- Chemical: MgO + H2O → Mg(OH)2
- Cement notation: `M + H → MH`
- Scheme basis: sourced
- C-S-H assumed: None.
- Per gram of M: water 0.447 g H2O per g M [derived; NEW-CIAAW]; CH 0.0 g CH per g M [derived; NEW-CIAAW]
- Heat: 849.0 J/g [sourced; R210] — 203 cal/g MgO (literature value quoted by Lerch & Bogue) (Lerch & Bogue 1934, p. 651); converted at 4.184 J/cal (conversion derived).
- Chemical shrinkage: unknown — at least one species has no molar volume in the inspected sources

| Species | Side | Coef | M (g/mol) | g per g key | V (cm3/mol) | ρ (g/cm3) |
|---|---|---|---|---|---|---|
| MgO (periclase) | reactant | 1 | 40.3 | -1.0 | unknown  | unknown |
| H2O (liquid) | reactant | 1 | 18.02 | -0.447 | 18.07 [NEW-BENTZ-2005] | 0.997 |
| Mg(OH)2 (brucite) | product | 1 | 58.32 | 1.447 | unknown  | unknown |

Conditions and caveats: Slow for dead-burnt periclase in clinker; delayed expansion (soundness, autoclave test). Molar volumes of periclase/brucite were not found in the inspected sources.

Sources: R210

### RX14 · Hemicarbonate formation

- Family: Limestone (Type IL)
- Chemical: Ca3Al2O6 + 0.5 CaCO3 + 0.5 Ca(OH)2 + 11.5 H2O → Ca4Al2(CO3)0.5(OH)13·5.5H2O
- Cement notation: `C3A + 0.5Cc + 0.5CH + 11.5H → C4Ac0.5H12`
- Scheme basis: derived
- C-S-H assumed: None.
- Per gram of C3A: water 0.7668 g H2O per g C3A [derived; NEW-CIAAW]; CH -0.1371 g CH per g C3A [derived; NEW-CIAAW]
- Heat: 1207.0 J per g C3A (heat released, +) [derived; NEW-BENTZ-2005, R334] — ΔrH° = -326.0 kJ per 1 mol C3A, from standard enthalpies of formation at 25 °C (NEW-BENTZ-2005, R334). Mixed-source sets are approximate.
- Chemical shrinkage: 0.173 cm3 per g C3A [derived; NEW-BENTZ-2005, R334] — (ΣV reactants incl. water - ΣV products) = 46.75 cm3 per 1 mol C3A; 14.1 % of reactant volume. Positive = volume loss.

| Species | Side | Coef | M (g/mol) | g per g key | V (cm3/mol) | ρ (g/cm3) |
|---|---|---|---|---|---|---|
| Ca3Al2O6 (C3A) | reactant | 1 | 270.19 | -1.0 | 89 [R334] | 3.036 |
| CaCO3 (calcite) | reactant | 0.5 | 100.09 | -0.1852 | 36.93 [NEW-BENTZ-2005] | 2.71 |
| Ca(OH)2 (portlandite, CH) | reactant | 0.5 | 74.09 | -0.1371 | 33 [R334] | 2.245 |
| H2O (liquid) | reactant | 11.5 | 18.02 | -0.7668 | 18.07 [NEW-BENTZ-2005] | 0.997 |
| C4Ac0.5H12 (hemicarbonate) | product | 1 | 564.45 | 2.0891 | 285 [R334] | 1.981 |

Conditions and caveats: Forms at low carbonate availability, early; converts to monocarbonate as more calcite dissolves. Balance derived; phase data from Cemdata18.

Sources: R334

### RX15 · Monocarbonate formation

- Family: Limestone (Type IL)
- Chemical: Ca3Al2O6 + CaCO3 + 11 H2O → Ca4Al2(CO3)(OH)12·5H2O
- Cement notation: `C3A + Cc + 11H → C4AcH11`
- Scheme basis: derived
- C-S-H assumed: None.
- Per gram of C3A: water 0.7334 g H2O per g C3A [derived; NEW-CIAAW]; CH 0.0 g CH per g C3A [derived; NEW-CIAAW]
- Heat: 1251.0 J per g C3A (heat released, +) [derived; NEW-BENTZ-2005, R334] — ΔrH° = -338.0 kJ per 1 mol C3A, from standard enthalpies of formation at 25 °C (NEW-BENTZ-2005, R334). Mixed-source sets are approximate.
- Chemical shrinkage: 0.232 cm3 per g C3A [derived; NEW-BENTZ-2005, R334] — (ΣV reactants incl. water - ΣV products) = 62.68 cm3 per 1 mol C3A; 19.3 % of reactant volume. Positive = volume loss.

| Species | Side | Coef | M (g/mol) | g per g key | V (cm3/mol) | ρ (g/cm3) |
|---|---|---|---|---|---|---|
| Ca3Al2O6 (C3A) | reactant | 1 | 270.19 | -1.0 | 89 [R334] | 3.036 |
| CaCO3 (calcite) | reactant | 1 | 100.09 | -0.3704 | 36.93 [NEW-BENTZ-2005] | 2.71 |
| H2O (liquid) | reactant | 11 | 18.02 | -0.7334 | 18.07 [NEW-BENTZ-2005] | 0.997 |
| C4AcH11 (monocarbonate) | product | 1 | 568.44 | 2.1038 | 262 [R334] | 2.17 |

Conditions and caveats: Thermodynamically favoured over monosulfate when calcite is present. Only a small fraction of limestone reacts (Bentz: about 5 % of a 20 % limestone replacement in 180 d of simulated hydration).

Sources: NEW-BENTZ-2005, R334

### RX16 · Carboaluminate stabilisation of ettringite (monosulfate + calcite → monocarbonate + ettringite)

- Family: Limestone (Type IL)
- Chemical: 3 Ca4Al2(SO4)(OH)12·6H2O + 2 CaCO3 + 18 H2O → 2 Ca4Al2(CO3)(OH)12·5H2O + Ca6Al2(SO4)3(OH)12·26H2O
- Cement notation: `3C4AsH12 + 2Cc + 18H → 2C4AcH11 + C6As3H32`
- Scheme basis: sourced
- C-S-H assumed: None.
- Per gram of AFm: water 0.1736 g H2O per g AFm [derived; NEW-CIAAW]; CH 0.0 g CH per g AFm [derived; NEW-CIAAW]
- Heat: 107.0 J per g AFm (heat released, +) [derived; NEW-BENTZ-2005, R334] — ΔrH° = -200.4 kJ per 3 mol AFm, from standard enthalpies of formation at 25 °C (NEW-BENTZ-2005, R334). Mixed-source sets are approximate.
- Chemical shrinkage: 0.0525 cm3 per g AFm [derived; NEW-BENTZ-2005, R334] — (ΣV reactants incl. water - ΣV products) = 98.08 cm3 per 3 mol AFm; 7.4 % of reactant volume. Positive = volume loss.

| Species | Side | Coef | M (g/mol) | g per g key | V (cm3/mol) | ρ (g/cm3) |
|---|---|---|---|---|---|---|
| C4AsH12 (monosulfate, AFm) | reactant | 3 | 622.51 | -1.0 | 310 [R334] | 2.008 |
| CaCO3 (calcite) | reactant | 2 | 100.09 | -0.1072 | 36.93 [NEW-BENTZ-2005] | 2.71 |
| H2O (liquid) | reactant | 18 | 18.02 | -0.1736 | 18.07 [NEW-BENTZ-2005] | 0.997 |
| C4AcH11 (monocarbonate) | product | 2 | 568.44 | 0.6088 | 262 [R334] | 2.17 |
| C6As3H32 (ettringite, AFt) | product | 1 | 1255.07 | 0.6721 | 707 [R334] | 1.775 |

Conditions and caveats: Reaction as implemented in CEMHYD3D v3.0 (Bentz 2005, section on limestone). Cemdata18: calcium carbonate prevents destabilisation of ettringite to monosulfate. Net solid volume increases, one reason Type IL pastes can show lower porosity.

Sources: NEW-BENTZ-2005, R334

### RX17 · Pozzolanic reaction of silica (silica fume, siliceous fly ash glass, natural pozzolan)

- Family: Pozzolanic (siliceous)
- Chemical: SiO2 + 1.1 Ca(OH)2 + 2.8 H2O → (CaO)1.1·SiO2·(H2O)3.9
- Cement notation: `S + 1.1CH + 2.8H → C1.1SH3.9`
- Scheme basis: sourced
- C-S-H assumed: C1.1SH3.9 (Ca/Si 1.1, H/Si 3.9) — pozzolanic C-S-H in CEMHYD3D after Atlassi, de Larrard and Jensen.
  - alternative C1.7SH4 → C1.1SH3.9 conversion (Ca/Si 1.1, H/Si 3.9): CEMHYD3D optionally converts C1.7SH4 to C1.1SH3.9 releasing CH when silica fume is abundant. [NEW-BENTZ-2005]
- Per gram of S: water 0.8395 g H2O per g S [derived; NEW-CIAAW]; CH -1.3565 g CH per g S [derived; NEW-CIAAW]
- Heat: 780 J per g silica fume reacted [sourced; NEW-BENTZ-2005] — 'Assume 780 J/g S for pozzolanic reaction' (disrealnew.c listing).
- Chemical shrinkage: 0.2029 cm3 per g S [derived; NEW-BENTZ-2005] — (ΣV reactants incl. water - ΣV products) = 12.19 cm3 per 1 mol S; 10.7 % of reactant volume. Positive = volume loss.
- Chemical shrinkage (as published): 0.2 g H2O per g silica fume (≈ cm3/g) [sourced; NEW-BENTZ-2005] — Comment in disrealnew.c: 'gives a chemical shrinkage of 0.2 g H2O/g CSF'.

| Species | Side | Coef | M (g/mol) | g per g key | V (cm3/mol) | ρ (g/cm3) |
|---|---|---|---|---|---|---|
| SiO2 (reactive silica: silica fume / glass) | reactant | 1 | 60.08 | -1.0 | 27.0 [NEW-BENTZ-2005] | 2.225 |
| Ca(OH)2 (portlandite, CH) | reactant | 1.1 | 74.09 | -1.3565 | 33.1 [NEW-BENTZ-2005] | 2.238 |
| H2O (liquid) | reactant | 2.8 | 18.02 | -0.8395 | 18.07 [NEW-BENTZ-2005] | 0.997 |
| C1.1SH3.9 (pozzolanic C-S-H) | product | 1 | 192.03 | 3.196 | 101.81 [NEW-BENTZ-2005] | 1.886 |

Conditions and caveats: Bentz: gives about 0.2 g H2O per g silica fume chemical shrinkage; 780 J/g silica fume assumed. Real pozzolanic C-S-H Ca/Si depends on CH availability.

Sources: NEW-BENTZ-2005

### RX18 · Aluminosilicate glass (AS) + CH → strätlingite

- Family: Pozzolanic (aluminous)
- Chemical: Al2O3·SiO2 + 2 Ca(OH)2 + 6 H2O → Ca2Al2SiO7·8H2O
- Cement notation: `AS + 2CH + 6H → C2ASH8`
- Scheme basis: sourced
- C-S-H assumed: None (strätlingite).
- Per gram of AS: water 0.667 g H2O per g AS [derived; NEW-CIAAW]; CH -0.9145 g CH per g AS [derived; NEW-CIAAW]
- Heat: 800 J per g AS reacted [sourced; NEW-BENTZ-2005] — 'Assume 800 J/g AS for stratlingite formation (DeLarrard)' (disrealnew.c listing).
- Chemical shrinkage: 0.0548 cm3 per g AS [derived; NEW-BENTZ-2005] — (ΣV reactants incl. water - ΣV products) = 8.88 cm3 per 1 mol AS; 4.0 % of reactant volume. Positive = volume loss.

| Species | Side | Coef | M (g/mol) | g per g key | V (cm3/mol) | ρ (g/cm3) |
|---|---|---|---|---|---|---|
| Al2O3·SiO2 (aluminosilicate glass, 'ASG' in CEMHYD3D) | reactant | 1 | 162.04 | -1.0 | 49.9 [NEW-BENTZ-2005] | 3.247 |
| Ca(OH)2 (portlandite, CH) | reactant | 2 | 74.09 | -0.9145 | 33.1 [NEW-BENTZ-2005] | 2.238 |
| H2O (liquid) | reactant | 6 | 18.02 | -0.667 | 18.07 [NEW-BENTZ-2005] | 0.997 |
| C2ASH8 (strätlingite) | product | 1 | 418.32 | 2.5815 | 215.63 [NEW-BENTZ-2005] | 1.94 |

Conditions and caveats: CEMHYD3D fly-ash glass reaction. Strätlingite is only stable when portlandite is absent (R330), so with excess CH AFm/hydrogarnet may form instead.

Sources: NEW-BENTZ-2005, R330

### RX19 · Metakaolin / calcined clay + CH → strätlingite + C-S-H

- Family: Pozzolanic (aluminous)
- Chemical: Al2Si2O7 + 3.1 Ca(OH)2 + 8.8 H2O → Ca2Al2SiO7·8H2O + (CaO)1.1·SiO2·(H2O)3.9
- Cement notation: `AS2 + 3.1CH + 8.8H → C2ASH8 + C1.1SH3.9`
- Scheme basis: derived
- C-S-H assumed: C1.1SH3.9 (Bentz pozzolanic C-S-H) for the second Si.
- Per gram of AS2: water 0.7137 g H2O per g AS2 [derived; NEW-CIAAW]; CH -1.034 g CH per g AS2 [derived; NEW-CIAAW]
- Heat: unknown — no measured heat and incomplete enthalpy-of-formation data in the inspected sources
- Chemical shrinkage: unknown — at least one species has no molar volume in the inspected sources

| Species | Side | Coef | M (g/mol) | g per g key | V (cm3/mol) | ρ (g/cm3) |
|---|---|---|---|---|---|---|
| Al2Si2O7 (metakaolin, AS2) | reactant | 1 | 222.13 | -1.0 | unknown  | unknown |
| Ca(OH)2 (portlandite, CH) | reactant | 3.1 | 74.09 | -1.034 | 33.1 [NEW-BENTZ-2005] | 2.238 |
| H2O (liquid) | reactant | 8.8 | 18.02 | -0.7137 | 18.07 [NEW-BENTZ-2005] | 0.997 |
| C2ASH8 (strätlingite) | product | 1 | 418.32 | 1.8832 | 215.63 [NEW-BENTZ-2005] | 1.94 |
| C1.1SH3.9 (pozzolanic C-S-H) | product | 1 | 192.03 | 0.8645 | 101.81 [NEW-BENTZ-2005] | 1.886 |

Conditions and caveats: Low-CH end member; balance derived here by combining RX18-type strätlingite with Bentz pozzolanic C-S-H. Real LC3/metakaolin systems form C-A-S-H, carboaluminates and AFm (R547, R561, R3092 not used for numbers).

Sources: NEW-BENTZ-2005, R330

### RX20 · Metakaolin / calcined clay + excess CH → C4AH13 + C-S-H

- Family: Pozzolanic (aluminous)
- Chemical: Al2Si2O7 + 6.2 Ca(OH)2 + 14.6 H2O → Ca4Al2(OH)14·6H2O + 2 (CaO)1.1·SiO2·(H2O)3.9
- Cement notation: `AS2 + 6.2CH + 14.6H → C4AH13 + 2C1.1SH3.9`
- Scheme basis: derived
- C-S-H assumed: C1.1SH3.9 (Bentz pozzolanic C-S-H).
- Per gram of AS2: water 1.1841 g H2O per g AS2 [derived; NEW-CIAAW]; CH -2.0681 g CH per g AS2 [derived; NEW-CIAAW]
- Heat: unknown — no measured heat and incomplete enthalpy-of-formation data in the inspected sources
- Chemical shrinkage: unknown — at least one species has no molar volume in the inspected sources

| Species | Side | Coef | M (g/mol) | g per g key | V (cm3/mol) | ρ (g/cm3) |
|---|---|---|---|---|---|---|
| Al2Si2O7 (metakaolin, AS2) | reactant | 1 | 222.13 | -1.0 | unknown  | unknown |
| Ca(OH)2 (portlandite, CH) | reactant | 6.2 | 74.09 | -2.0681 | 33.1 [NEW-BENTZ-2005] | 2.238 |
| H2O (liquid) | reactant | 14.6 | 18.02 | -1.1841 | 18.07 [NEW-BENTZ-2005] | 0.997 |
| C4AH13 (hydroxy-AFm) | product | 1 | 560.46 | 2.5232 | 274 [R334] | 2.045 |
| C1.1SH3.9 (pozzolanic C-S-H) | product | 2 | 192.03 | 1.729 | 101.81 [NEW-BENTZ-2005] | 1.886 |

Conditions and caveats: High-CH end member; balance derived here. With calcite present, carboaluminates replace C4AH13 (LC3).

Sources: NEW-BENTZ-2005, R334

### RX21 · Belite + AH3 → strätlingite (CSA and blended systems)

- Family: Pozzolanic (aluminous)
- Chemical: Ca2SiO4 + Al2O3·3H2O + 5 H2O → Ca2Al2SiO7·8H2O
- Cement notation: `C2S + AH3 + 5H → C2ASH8`
- Scheme basis: sourced
- C-S-H assumed: None.
- Per gram of C2S: water 0.523 g H2O per g C2S [derived; NEW-CIAAW]; CH 0.0 g CH per g C2S [derived; NEW-CIAAW]
- Heat: 264.0 J per g C2S (heat released, +) [derived; NEW-BENTZ-2005, R334] — ΔrH° = -45.5 kJ per 1 mol C2S, from standard enthalpies of formation at 25 °C (NEW-BENTZ-2005, R334). Mixed-source sets are approximate.
- Chemical shrinkage: -0.0561 cm3 per g C2S [derived; NEW-BENTZ-2005, R334] — (ΣV reactants incl. water - ΣV products) = -9.66 cm3 per 1 mol C2S; -4.7 % of reactant volume. Positive = volume loss.

| Species | Side | Coef | M (g/mol) | g per g key | V (cm3/mol) | ρ (g/cm3) |
|---|---|---|---|---|---|---|
| Ca2SiO4 (belite, C2S) | reactant | 1 | 172.24 | -1.0 | 52 [R334] | 3.312 |
| Al2O3·3H2O = 2 Al(OH)3 (gibbsite / AH3) | reactant | 1 | 156.01 | -0.9058 | 64 [R334] | 2.438 |
| H2O (liquid) | reactant | 5 | 18.02 | -0.523 | 18.07 [NEW-BENTZ-2005] | 0.997 |
| C2ASH8 (strätlingite) | product | 1 | 418.32 | 2.4287 | 216 [R334] | 1.937 |

Conditions and caveats: Winnefeld & Lothenbach Eq. 3; seen after 28 d in CSA cements. Only stable without portlandite.

Sources: R330

### RX22 · Slag 1 (Bentz Table 2) + CH → mixed slag hydration product

- Family: Slag
- Chemical: slag glass (CaO)16.5(SiO2)17(MgO)6.5(Al2O3)2(SO3) + 4.75 Ca(OH)2 + 81.25 H2O → (CaO)21.25(SiO2)17(MgO)6.5(Al2O3)2(SO3)(H2O)86 (mixed C-S-H/AFm/hydrotalcite)
- Cement notation: `C16.5S17M6.5A2s + 4.75CH + 81.25H → C21.25S17M6.5A2sH86`
- Scheme basis: derived
- C-S-H assumed: Product Ca/Si 1.25 and H/Si 5.06 for the whole mixed product (C-S-H with AFm, hydrotalcite) — not a pure C-S-H.
- Per gram of SLAG1: water 0.5872 g H2O per g SLAG1 [derived; NEW-CIAAW]; CH -0.1412 g CH per g SLAG1 [derived; NEW-CIAAW]
- Heat: 800 J per g slag reacted [sourced; NEW-BENTZ-2005] — 'Assume 800 J/g S for slag reaction' (disrealnew.c listing; comment cites Biernacki & Richardson).
- Heat: 461 J per g slag (Grade 100) [sourced; NEW-LEON-CHEN-2021] — Schindler & Folliard (2005) as quoted by Leon & Chen 2021; 550 J/g for Grade 120.
- Chemical shrinkage: unknown — at least one species has no molar volume in the inspected sources

| Species | Side | Coef | M (g/mol) | g per g key | V (cm3/mol) | ρ (g/cm3) |
|---|---|---|---|---|---|---|
| Slag 1 of Bentz Table 2 (39.2 SiO2, 7.9 Al2O3, 36.25 CaO, 10.3 MgO, 3.1 SO3 %) | reactant | 1 | 2492.64 | -1.0 | unknown  | unknown |
| Ca(OH)2 (portlandite, CH) | reactant | 4.75 | 74.09 | -0.1412 | 33.1 [NEW-BENTZ-2005] | 2.238 |
| H2O (liquid) | reactant | 81.25 | 18.02 | -0.5872 | 18.07 [NEW-BENTZ-2005] | 0.997 |
| Slag 1 hydration product (Bentz Table 2) | product | 1 | 4308.29 | 1.7284 | unknown  | unknown |

Conditions and caveats: Slag and product compositions from Bentz 2005 Table 2 (slag 1, no extra C3A); CH and water coefficients derived by balance. Heat: Bentz assumes 800 J/g slag; Schindler & Folliard use 461 J/g (Grade 100) or 550 J/g (Grade 120).

Sources: NEW-BENTZ-2005, NEW-LEON-CHEN-2021

### RX23 · Slag 2 (Bentz Table 2) + CH → mixed product + 'extra C3A'

- Family: Slag
- Chemical: slag glass (CaO)21.5(SiO2)15(MgO)5.5(Al2O3)3(SO3) + 1.75 Ca(OH)2 + 81.25 H2O → C20.25S15M5.5A2sH83 + C3A (which then reacts as cement C3A)
- Cement notation: `C21.5S15M5.5A3s + 1.75CH + 81.25H → C20.25S15M5.5A2sH83 + C3A`
- Scheme basis: derived
- C-S-H assumed: Product Ca/Si 1.35, H/Si 5.533 (slagchar.dat example) for the mixed product.
- Per gram of SLAG2: water 0.5392 g H2O per g SLAG2 [derived; NEW-CIAAW]; CH -0.0478 g CH per g SLAG2 [derived; NEW-CIAAW]
- Heat: 800 J per g slag reacted [sourced; NEW-BENTZ-2005] — 'Assume 800 J/g S for slag reaction' (disrealnew.c).
- Chemical shrinkage: 0.2451 cm3 per g SLAG2 [derived; NEW-BENTZ-2005] — (ΣV reactants incl. water - ΣV products) = 665.20 cm3 per 1 mol SLAG2; 26.9 % of reactant volume. Positive = volume loss.

| Species | Side | Coef | M (g/mol) | g per g key | V (cm3/mol) | ρ (g/cm3) |
|---|---|---|---|---|---|---|
| Slag 2 of Bentz Table 2 (34.7 SiO2, 11.4 Al2O3, 45.5 CaO, 8.5 MgO, 3.0 SO3 %) | reactant | 1 | 2714.51 | -1.0 | 945.72 [NEW-BENTZ-2005] | 2.87 |
| Ca(OH)2 (portlandite, CH) | reactant | 1.75 | 74.09 | -0.0478 | 33.1 [NEW-BENTZ-2005] | 2.238 |
| H2O (liquid) | reactant | 81.25 | 18.02 | -0.5392 | 18.07 [NEW-BENTZ-2005] | 0.997 |
| Slag 2 hydration product (Bentz Table 2 / slagchar.dat) | product | 1 | 4037.7 | 1.4874 | 1717.53 [NEW-BENTZ-2005] | 2.351 |
| Ca3Al2O6 (C3A) | product | 1 | 270.19 | 0.0995 | 88.94 [NEW-BENTZ-2005] | 3.038 |

Conditions and caveats: CEMHYD3D: when Mg/Al is well below 2, extra Al reacts like C3A (ettringite, AFm, hydrogarnet). Molar volumes of slag (945.72) and product (1717.53 cm3/mol) from slagchar.dat; shrinkage here excludes the later hydration of the 'extra C3A'.

Sources: NEW-BENTZ-2005

### RX24 · Hydrotalcite formation from slag Mg and Al (schematic)

- Family: Slag
- Chemical: 4 MgO + Al2O3·3H2O + 7 H2O → Mg4Al2(OH)14·3H2O (oxide bookkeeping only)
- Cement notation: `4M + AH3 + 7H → M4AH10`
- Scheme basis: derived
- C-S-H assumed: None.
- Per gram of M: water 0.7822 g H2O per g M [derived; NEW-CIAAW]; CH 0.0 g CH per g M [derived; NEW-CIAAW]
- Heat: unknown — no measured heat and incomplete enthalpy-of-formation data in the inspected sources
- Chemical shrinkage: unknown — at least one species has no molar volume in the inspected sources

| Species | Side | Coef | M (g/mol) | g per g key | V (cm3/mol) | ρ (g/cm3) |
|---|---|---|---|---|---|---|
| MgO (periclase) | reactant | 4 | 40.3 | -1.0 | unknown  | unknown |
| Al2O3·3H2O = 2 Al(OH)3 (gibbsite / AH3) | reactant | 1 | 156.01 | -0.9677 | 64 [R334] | 2.438 |
| H2O (liquid) | reactant | 7 | 18.02 | -0.7822 | 18.07 [NEW-BENTZ-2005] | 0.997 |
| Mg4Al2(OH)14·3H2O (hydrotalcite-like, M4AH10) | product | 1 | 443.33 | 2.7499 | 220 [R334] | 2.015 |

Conditions and caveats: Bookkeeping reaction showing how slag Mg and Al end up in a hydrotalcite-like phase (Mg/Al = 2). Slag Mg and Al come from the glass, not from periclase/AH3; heat not defined.

Sources: R334

### RX25 · Ye'elimite without calcium sulfate → monosulfate + AH3

- Family: Calcium sulfoaluminate (ye'elimite)
- Chemical: Ca4Al6O12SO4 + 18 H2O → Ca4Al2(SO4)(OH)12·6H2O + 2 Al2O3·3H2O
- Cement notation: `C4A3s + 18H → C4AsH12 + 2AH3`
- Scheme basis: sourced
- C-S-H assumed: None.
- Per gram of C4A3s: water 0.5314 g H2O per g C4A3s [derived; NEW-CIAAW]; CH 0.0 g CH per g C4A3s [derived; NEW-CIAAW]
- Heat: unknown — no measured heat and incomplete enthalpy-of-formation data in the inspected sources
- Chemical shrinkage: unknown — at least one species has no molar volume in the inspected sources

| Species | Side | Coef | M (g/mol) | g per g key | V (cm3/mol) | ρ (g/cm3) |
|---|---|---|---|---|---|---|
| Ca4Al6O12SO4 (ye'elimite, C4A3s) | reactant | 1 | 610.25 | -1.0 | unknown  | unknown |
| H2O (liquid) | reactant | 18 | 18.02 | -0.5314 | 18.07 [NEW-BENTZ-2005] | 0.997 |
| C4AsH12 (monosulfate, AFm) | product | 1 | 622.51 | 1.0201 | 312.82 [NEW-BENTZ-2005] | 1.99 |
| Al2O3·3H2O = 2 Al(OH)3 (gibbsite / AH3) | product | 2 | 156.01 | 0.5113 | 64 [R334] | 2.438 |

Conditions and caveats: Winnefeld & Lothenbach Eq. 1. AH3 is usually poorly crystalline (gel). Ye'elimite molar volume not found in inspected sources, so shrinkage is unknown. CAH10 can also form when sulfate is low (R3079).

Sources: R3079, R330

### RX26 · Ye'elimite + gypsum → ettringite + AH3

- Family: Calcium sulfoaluminate (ye'elimite)
- Chemical: Ca4Al6O12SO4 + 2 CaSO4·2H2O + 34 H2O → Ca6Al2(SO4)3(OH)12·26H2O + 2 Al2O3·3H2O
- Cement notation: `C4A3s + 2CsH2 + 34H → C6As3H32 + 2AH3`
- Scheme basis: sourced
- C-S-H assumed: None.
- Per gram of C4A3s: water 1.0037 g H2O per g C4A3s [derived; NEW-CIAAW]; CH 0.0 g CH per g C4A3s [derived; NEW-CIAAW]
- Heat: unknown — no measured heat and incomplete enthalpy-of-formation data in the inspected sources
- Chemical shrinkage: unknown — at least one species has no molar volume in the inspected sources
- Chemical shrinkage (as published): 0.114 cm3 per g CSA cement (whole cement, 28 d, CSA-1; 0.115 for CSA-2) [sourced; R330] — Calculated by thermodynamic modelling for the cements, not for this single reaction.

| Species | Side | Coef | M (g/mol) | g per g key | V (cm3/mol) | ρ (g/cm3) |
|---|---|---|---|---|---|---|
| Ca4Al6O12SO4 (ye'elimite, C4A3s) | reactant | 1 | 610.25 | -1.0 | unknown  | unknown |
| CaSO4·2H2O (gypsum) | reactant | 2 | 172.16 | -0.5642 | 74.21 [NEW-BENTZ-2005] | 2.32 |
| H2O (liquid) | reactant | 34 | 18.02 | -1.0037 | 18.07 [NEW-BENTZ-2005] | 0.997 |
| C6As3H32 (ettringite, AFt) | product | 1 | 1255.07 | 2.0567 | 735.01 [NEW-BENTZ-2005] | 1.708 |
| Al2O3·3H2O = 2 Al(OH)3 (gibbsite / AH3) | product | 2 | 156.01 | 0.5113 | 64 [R334] | 2.438 |

Conditions and caveats: Winnefeld & Lothenbach Eq. 2. Winnefeld & Lothenbach report a calculated chemical shrinkage of 11.4-11.5 cm3/100 g for two whole CSA cements at 28 d.

Sources: R330

### RX27 · Ye'elimite + gypsum + CH → ettringite (expansive formulation)

- Family: Calcium sulfoaluminate (ye'elimite)
- Chemical: Ca4Al6O12SO4 + 8 CaSO4·2H2O + 6 Ca(OH)2 + 74 H2O → 3 Ca6Al2(SO4)3(OH)12·26H2O
- Cement notation: `C4A3s + 8CsH2 + 6CH + 74H → 3C6As3H32`
- Scheme basis: derived
- C-S-H assumed: None.
- Per gram of C4A3s: water 2.1845 g H2O per g C4A3s [derived; NEW-CIAAW]; CH -0.7285 g CH per g C4A3s [derived; NEW-CIAAW]
- Heat: unknown — no measured heat and incomplete enthalpy-of-formation data in the inspected sources
- Chemical shrinkage: unknown — at least one species has no molar volume in the inspected sources

| Species | Side | Coef | M (g/mol) | g per g key | V (cm3/mol) | ρ (g/cm3) |
|---|---|---|---|---|---|---|
| Ca4Al6O12SO4 (ye'elimite, C4A3s) | reactant | 1 | 610.25 | -1.0 | unknown  | unknown |
| CaSO4·2H2O (gypsum) | reactant | 8 | 172.16 | -2.257 | 74.21 [NEW-BENTZ-2005] | 2.32 |
| Ca(OH)2 (portlandite, CH) | reactant | 6 | 74.09 | -0.7285 | 33.1 [NEW-BENTZ-2005] | 2.238 |
| H2O (liquid) | reactant | 74 | 18.02 | -2.1845 | 18.07 [NEW-BENTZ-2005] | 0.997 |
| C6As3H32 (ettringite, AFt) | product | 3 | 1255.07 | 6.17 | 735.01 [NEW-BENTZ-2005] | 1.708 |

Conditions and caveats: All Al to ettringite when CH and sulfate are in excess (expansive/shrinkage-compensating systems). Balance derived here; this scheme was not taken from an inspected source.

Sources: balance derived only

### RX28 · CA → CAH10 (mainly below 15 °C)

- Family: Calcium aluminate cement (CA)
- Chemical: CaAl2O4 + 10 H2O → CaAl2O4·10H2O
- Cement notation: `CA + 10H → CAH10`
- Scheme basis: sourced
- C-S-H assumed: None.
- Per gram of CA: water 1.1399 g H2O per g CA [derived; NEW-CIAAW]; CH 0.0 g CH per g CA [derived; NEW-CIAAW]
- Heat: 651.0 J per g CA (heat released, +) [derived; NEW-BENTZ-2005, R334] — ΔrH° = -102.9 kJ per 1 mol CA, from standard enthalpies of formation at 25 °C (NEW-BENTZ-2005, R334). Mixed-source sets are approximate.
- Chemical shrinkage: 0.237 cm3 per g CA [derived; NEW-BENTZ-2005, R372] — (ΣV reactants incl. water - ΣV products) = 37.45 cm3 per 1 mol CA; 16.0 % of reactant volume. Positive = volume loss.
- Chemical shrinkage (as published): -36.97 cm3 per mol (theoretical) [sourced; R372] — Theoretical chemical shrinkage -36.97 cm3/mol or 15.8 % (Shirani et al., Table 1).

| Species | Side | Coef | M (g/mol) | g per g key | V (cm3/mol) | ρ (g/cm3) |
|---|---|---|---|---|---|---|
| CaAl2O4 (monocalcium aluminate, CA) | reactant | 1 | 158.04 | -1.0 | 53.39 [R372] | 2.96 |
| H2O (liquid) | reactant | 10 | 18.02 | -1.1399 | 18.07 [NEW-BENTZ-2005] | 0.997 |
| CaAl2O4·10H2O (CAH10) | product | 1 | 338.19 | 2.1399 | 196.62 [R372] | 1.72 |

Conditions and caveats: Metastable hydrate; converts with time and temperature (RX31, RX32).

Sources: R334, R372

### RX29 · CA → C2AH8 + AH3 (mainly 15-50 °C)

- Family: Calcium aluminate cement (CA)
- Chemical: 2 CaAl2O4 + 11 H2O → Ca2Al2O5·8H2O + 2 Al(OH)3
- Cement notation: `2CA + 11H → C2AH8 + AH3`
- Scheme basis: sourced
- C-S-H assumed: None.
- Per gram of CA: water 0.627 g H2O per g CA [derived; NEW-CIAAW]; CH 0.0 g CH per g CA [derived; NEW-CIAAW]
- Heat: unknown — no measured heat and incomplete enthalpy-of-formation data in the inspected sources
- Chemical shrinkage: 0.1707 cm3 per g CA [derived; NEW-BENTZ-2005, R334, R372] — (ΣV reactants incl. water - ΣV products) = 53.97 cm3 per 2 mol CA; 17.7 % of reactant volume. Positive = volume loss.
- Chemical shrinkage (as published): -39.44 cm3 per mol (theoretical) [sourced; R372] — Theoretical chemical shrinkage -39.44 cm3/mol or 12.9 % (Shirani et al., Table 1).

| Species | Side | Coef | M (g/mol) | g per g key | V (cm3/mol) | ρ (g/cm3) |
|---|---|---|---|---|---|---|
| CaAl2O4 (monocalcium aluminate, CA) | reactant | 2 | 158.04 | -1.0 | 53.39 [R372] | 2.96 |
| H2O (liquid) | reactant | 11 | 18.02 | -0.627 | 18.07 [NEW-BENTZ-2005] | 0.997 |
| Ca2Al2O5·8H2O (C2AH8) | product | 1 | 358.24 | 1.1334 | 187.56 [R372] | 1.91 |
| Al2O3·3H2O = 2 Al(OH)3 (gibbsite / AH3) | product | 1 | 156.01 | 0.4936 | 64 [R334] | 2.438 |

Conditions and caveats: Al(OH)3 forms as a gel (density about 2.00 g/cm3 used by Shirani et al.).

Sources: R372

### RX30 · CA → C3AH6 + AH3 (mainly above 50 °C)

- Family: Calcium aluminate cement (CA)
- Chemical: 3 CaAl2O4 + 12 H2O → Ca3Al2(OH)12 + 4 Al(OH)3
- Cement notation: `3CA + 12H → C3AH6 + 2AH3`
- Scheme basis: sourced
- C-S-H assumed: None.
- Per gram of CA: water 0.456 g H2O per g CA [derived; NEW-CIAAW]; CH 0.0 g CH per g CA [derived; NEW-CIAAW]
- Heat: 593.0 J per g CA (heat released, +) [derived; NEW-BENTZ-2005, R334] — ΔrH° = -281.1 kJ per 3 mol CA, from standard enthalpies of formation at 25 °C (NEW-BENTZ-2005, R334). Mixed-source sets are approximate.
- Chemical shrinkage: 0.2088 cm3 per g CA [derived; NEW-BENTZ-2005, R334, R372] — (ΣV reactants incl. water - ΣV products) = 98.99 cm3 per 3 mol CA; 26.3 % of reactant volume. Positive = volume loss.
- Chemical shrinkage (as published): -85.08 cm3 per mol (theoretical) [sourced; R372] — Theoretical chemical shrinkage -85.08 cm3/mol or 22.6 % (Shirani et al., Table 1).

| Species | Side | Coef | M (g/mol) | g per g key | V (cm3/mol) | ρ (g/cm3) |
|---|---|---|---|---|---|---|
| CaAl2O4 (monocalcium aluminate, CA) | reactant | 3 | 158.04 | -1.0 | 53.39 [R372] | 2.96 |
| H2O (liquid) | reactant | 12 | 18.02 | -0.456 | 18.07 [NEW-BENTZ-2005] | 0.997 |
| Ca3Al2(OH)12 (hydrogarnet / katoite, C3AH6) | product | 1 | 378.28 | 0.7979 | 150 [R334] | 2.522 |
| Al2O3·3H2O = 2 Al(OH)3 (gibbsite / AH3) | product | 2 | 156.01 | 0.6581 | 64 [R334] | 2.438 |

Conditions and caveats: Stable assemblage; high porosity if formed by conversion in place.

Sources: R334, R372

### RX31 · Conversion CAH10 → C2AH8 + AH3 + water

- Family: Calcium aluminate cement (CA)
- Chemical: 2 CaAl2O4·10H2O → Ca2Al2O5·8H2O + 2 Al(OH)3 + 9 H2O
- Cement notation: `2CAH10 → C2AH8 + AH3 + 9H`
- Scheme basis: sourced
- C-S-H assumed: None.
- Per gram of CAH10: water -0.2397 g H2O per g CAH10 [derived; NEW-CIAAW]; CH 0.0 g CH per g CAH10 [derived; NEW-CIAAW]
- Heat: unknown — no measured heat and incomplete enthalpy-of-formation data in the inspected sources
- Chemical shrinkage: -0.0309 cm3 per g CAH10 [derived; NEW-BENTZ-2005, R334, R372] — (ΣV reactants incl. water - ΣV products) = -20.93 cm3 per 2 mol CAH10; -5.3 % of reactant volume. Positive = volume loss.
- Chemical shrinkage (as published): 37.9 % of solid reactant volume turned into porosity [sourced; R372] — Secondary water porosity 162.18 cm3 per 2 mol CAH10.

| Species | Side | Coef | M (g/mol) | g per g key | V (cm3/mol) | ρ (g/cm3) |
|---|---|---|---|---|---|---|
| CaAl2O4·10H2O (CAH10) | reactant | 2 | 338.19 | -1.0 | 196.62 [R372] | 1.72 |
| Ca2Al2O5·8H2O (C2AH8) | product | 1 | 358.24 | 0.5296 | 187.56 [R372] | 1.91 |
| Al2O3·3H2O = 2 Al(OH)3 (gibbsite / AH3) | product | 1 | 156.01 | 0.2306 | 64 [R334] | 2.438 |
| H2O (liquid) | product | 9 | 18.02 | 0.2397 | 18.07 [NEW-BENTZ-2005] | 0.997 |

Conditions and caveats: Releases water and solid volume (secondary porosity 162.18 cm3, 37.9 % of solid reactant volume, Shirani et al.). Proceeds through solution, needs free water.

Sources: R372

### RX32 · Conversion C2AH8 → C3AH6 + AH3 + water

- Family: Calcium aluminate cement (CA)
- Chemical: 3 Ca2Al2O5·8H2O → 2 Ca3Al2(OH)12 + 2 Al(OH)3 + 9 H2O
- Cement notation: `3C2AH8 → 2C3AH6 + AH3 + 9H`
- Scheme basis: sourced
- C-S-H assumed: None.
- Per gram of C2AH8: water -0.1509 g H2O per g C2AH8 [derived; NEW-CIAAW]; CH 0.0 g CH per g C2AH8 [derived; NEW-CIAAW]
- Heat: unknown — no measured heat and incomplete enthalpy-of-formation data in the inspected sources
- Chemical shrinkage: 0.0336 cm3 per g C2AH8 [derived; NEW-BENTZ-2005, R334, R372] — (ΣV reactants incl. water - ΣV products) = 36.07 cm3 per 3 mol C2AH8; 6.4 % of reactant volume. Positive = volume loss.
- Chemical shrinkage (as published): 28.8 % of solid reactant volume turned into porosity [sourced; R372] — Secondary water porosity 162.18 cm3 per 3 mol C2AH8.

| Species | Side | Coef | M (g/mol) | g per g key | V (cm3/mol) | ρ (g/cm3) |
|---|---|---|---|---|---|---|
| Ca2Al2O5·8H2O (C2AH8) | reactant | 3 | 358.24 | -1.0 | 187.56 [R372] | 1.91 |
| Ca3Al2(OH)12 (hydrogarnet / katoite, C3AH6) | product | 2 | 378.28 | 0.704 | 150 [R334] | 2.522 |
| Al2O3·3H2O = 2 Al(OH)3 (gibbsite / AH3) | product | 1 | 156.01 | 0.1452 | 64 [R334] | 2.438 |
| H2O (liquid) | product | 9 | 18.02 | 0.1509 | 18.07 [NEW-BENTZ-2005] | 0.997 |

Conditions and caveats: Secondary porosity 162.18 cm3 or 28.8 % of solid reactant volume (Shirani et al.). Strength loss in CAC concrete above about w/c 0.40 is linked to conversion.

Sources: R372

### RX33 · Overall conversion CAH10 → C3AH6 + AH3 + water

- Family: Calcium aluminate cement (CA)
- Chemical: 3 CaAl2O4·10H2O → Ca3Al2(OH)12 + 4 Al(OH)3 + 18 H2O
- Cement notation: `3CAH10 → C3AH6 + 2AH3 + 18H`
- Scheme basis: derived
- C-S-H assumed: None.
- Per gram of CAH10: water -0.3196 g H2O per g CAH10 [derived; NEW-CIAAW]; CH 0.0 g CH per g CAH10 [derived; NEW-CIAAW]
- Heat: -27.0 J per g CAH10 (heat released, +) [derived; NEW-BENTZ-2005, R334] — ΔrH° = +27.6 kJ per 3 mol CAH10, from standard enthalpies of formation at 25 °C (NEW-BENTZ-2005, R334). Mixed-source sets are approximate.
- Chemical shrinkage: -0.0132 cm3 per g CAH10 [derived; NEW-BENTZ-2005, R334, R372] — (ΣV reactants incl. water - ΣV products) = -13.36 cm3 per 3 mol CAH10; -2.3 % of reactant volume. Positive = volume loss.

| Species | Side | Coef | M (g/mol) | g per g key | V (cm3/mol) | ρ (g/cm3) |
|---|---|---|---|---|---|---|
| CaAl2O4·10H2O (CAH10) | reactant | 3 | 338.19 | -1.0 | 196.62 [R372] | 1.72 |
| Ca3Al2(OH)12 (hydrogarnet / katoite, C3AH6) | product | 1 | 378.28 | 0.3729 | 150 [R334] | 2.522 |
| Al2O3·3H2O = 2 Al(OH)3 (gibbsite / AH3) | product | 2 | 156.01 | 0.3075 | 64 [R334] | 2.438 |
| H2O (liquid) | product | 18 | 18.02 | 0.3196 | 18.07 [NEW-BENTZ-2005] | 0.997 |

Conditions and caveats: Sum of RX31 and RX32 (balance derived). Endothermic ΔrH° here uses gibbsite; gel AH3 differs.

Sources: R334, R372

### RX34 · Metakaolin or low-Ca fly ash + NaOH / sodium silicate → N-A-S-H gel (schematic)

- Family: Alkali activation
- Chemical: Al2Si2O7 (+ SiO2 from silicate) + 2 NaOH + n H2O → Na2O·Al2O3·xSiO2·mH2O (N-A-S-H, Si/Al ≥ 1)
- Cement notation: `AS2 + N(H) + (S) + H → N-A-S-H`
- Scheme basis: schematic
- C-S-H assumed: No C-S-H. Gel Si/Al and water content depend on the activator modulus; Na/Al ≈ 1 for charge balance.
- Per gram of AS2: water unknown; CH unknown
- Heat: unknown — no value in the inspected sources
- Chemical shrinkage: unknown — no value in the inspected sources

| Species | Side | Coef | M (g/mol) | g per g key | V (cm3/mol) | ρ (g/cm3) |
|---|---|---|---|---|---|---|
| Al2Si2O7 (metakaolin, AS2) | reactant | 1 | 222.13 | — | unknown  | unknown |

Conditions and caveats: Schematic only. Cemdata18 provides zeolite and C-(N-)A-S-H data for alkali-activated materials but no single N-A-S-H reaction; no numeric stoichiometry is given here.

Sources: R334

### RX35 · Slag + NaOH or Na2SiO3 → C-(N-)A-S-H + hydrotalcite (schematic)

- Family: Alkali activation
- Chemical: slag glass (CaO-SiO2-Al2O3-MgO) + NaOH / Na2SiO3 + H2O → C-(N-)A-S-H (Ca/Si ≈ 1) + Mg-Al LDH (hydrotalcite) ± AFm
- Cement notation: `slag + N(H) / NS + H → C-(N-)A-S-H + M4AH10 (± AFm)`
- Scheme basis: schematic
- C-S-H assumed: C-(N-)A-S-H, e.g. Cemdata18 CNASH end members such as 5CNA = C1.25N0.25A0.125SH1.375 (V° 64.5 cm3/mol) or INFCNA = C1A0.156N0.344S1.188H1.313 (V° 69.3 cm3/mol).
  - alternative 5CNA: C5/4N1/4A1/8S1H11/8 (Ca/Si 1.25, H/Si 1.375): CNASH solid-solution end member (V° 64.5, ΔfH° -2568.7 kJ/mol). [R334]
  - alternative INFCNA: C1A5/32N11/32S38/32H42/32 (Ca/Si 0.842, H/Si 1.105): CNASH end member (V° 69.3, ΔfH° -2666.7 kJ/mol). [R334]
- Per gram of slag: water unknown; CH unknown
- Heat: unknown — no value in the inspected sources
- Chemical shrinkage: unknown — no value in the inspected sources

Conditions and caveats: Schematic only; Cemdata18 recommends its MgAl-OH-LDH data for alkali-activated materials.

Sources: R334

### RX36 · Brucite carbonation → magnesite (schematic end member)

- Family: MgO systems and carbonation
- Chemical: Mg(OH)2 + CO2 → MgCO3 + H2O
- Cement notation: `MH + c → Mc + H`
- Scheme basis: derived
- C-S-H assumed: None.
- Per gram of MH: water -0.3089 g H2O per g MH [derived; NEW-CIAAW]; CH 0.0 g CH per g MH [derived; NEW-CIAAW]
- Heat: unknown — no measured heat and incomplete enthalpy-of-formation data in the inspected sources
- Chemical shrinkage: unknown — at least one species has no molar volume in the inspected sources

| Species | Side | Coef | M (g/mol) | g per g key | V (cm3/mol) | ρ (g/cm3) |
|---|---|---|---|---|---|---|
| Mg(OH)2 (brucite) | reactant | 1 | 58.32 | -1.0 | unknown  | unknown |
| CO2 (gas) | reactant | 1 | 44.01 | -0.7546 | unknown  | unknown |
| MgCO3 (magnesite) | product | 1 | 84.31 | 1.4457 | unknown  | unknown |
| H2O (liquid) | product | 1 | 18.02 | 0.3089 | 18.07 [NEW-BENTZ-2005] | 0.997 |

Conditions and caveats: At ambient conditions hydrated Mg carbonates (e.g. nesquehonite, hydromagnesite) form rather than magnesite; masses only.

Sources: balance derived only

### RX37 · M-S-H formation from brucite and silica

- Family: MgO systems and carbonation
- Chemical: 1.5 Mg(OH)2 + SiO2 + H2O → (MgO)1.5·SiO2·(H2O)2.5
- Cement notation: `1.5MH + S + H → M1.5SH2.5`
- Scheme basis: derived
- C-S-H assumed: None (M-S-H, Mg/Si 1.5).
- Per gram of SH0: water 0.2998 g H2O per g SH0 [derived; NEW-CIAAW]; CH 0.0 g CH per g SH0 [derived; NEW-CIAAW]
- Heat: unknown — no measured heat and incomplete enthalpy-of-formation data in the inspected sources
- Chemical shrinkage: unknown — at least one species has no molar volume in the inspected sources

| Species | Side | Coef | M (g/mol) | g per g key | V (cm3/mol) | ρ (g/cm3) |
|---|---|---|---|---|---|---|
| Mg(OH)2 (brucite) | reactant | 1.5 | 58.32 | -1.456 | unknown  | unknown |
| SiO2 (silica gel, anhydrous basis) | reactant | 1 | 60.08 | -1.0 | 29 [R334] | 2.072 |
| H2O (liquid) | reactant | 1 | 18.02 | -0.2998 | 18.07 [NEW-BENTZ-2005] | 0.997 |
| M1.5SH2.5 (M-S-H, Mg/Si 1.5) | product | 1 | 165.58 | 2.7558 | 74 [R334] | 2.238 |

Conditions and caveats: M-S-H end member from Cemdata18 (Mg/Si 1.5). Brucite molar volume and ΔfH° not in the inspected sources, so shrinkage and heat are unknown.

Sources: R334

### RX38 · Carbonation of portlandite

- Family: MgO systems and carbonation
- Chemical: Ca(OH)2 + CO2 → CaCO3 + H2O
- Cement notation: `CH + c → Cc + H`
- Scheme basis: derived
- C-S-H assumed: None.
- Per gram of CH: water -0.2431 g H2O per g CH [derived; NEW-CIAAW]; CH -1.0 g CH per g CH [derived; NEW-CIAAW]
- Heat: 1527.0 J per g CH (heat released, +) [derived; NEW-BENTZ-2005, NEW-NIST-WEBBOOK-CO2] — ΔrH° = -113.1 kJ per 1 mol CH, from standard enthalpies of formation at 25 °C (NEW-BENTZ-2005, NEW-NIST-WEBBOOK-CO2). Mixed-source sets are approximate.
- Chemical shrinkage: -0.2956 cm3 per g CH [derived; NEW-BENTZ-2005] — Condensed phases only (CO2 gas excluded): ΣV reactants - ΣV products = -21.90 cm3 per 1 mol CH. Negative = solid+water volume increases.

| Species | Side | Coef | M (g/mol) | g per g key | V (cm3/mol) | ρ (g/cm3) |
|---|---|---|---|---|---|---|
| Ca(OH)2 (portlandite, CH) | reactant | 1 | 74.09 | -1.0 | 33.1 [NEW-BENTZ-2005] | 2.238 |
| CO2 (gas) | reactant | 1 | 44.01 | -0.594 | unknown  | unknown |
| CaCO3 (calcite) | product | 1 | 100.09 | 1.3508 | 36.93 [NEW-BENTZ-2005] | 2.71 |
| H2O (liquid) | product | 1 | 18.02 | 0.2431 | 18.07 [NEW-BENTZ-2005] | 0.997 |

Conditions and caveats: Solid volume increases (calcite larger than portlandite); pH drops. Volumes here count CO2 as zero-volume gas (only the solid and water volumes are compared).

Sources: NEW-BENTZ-2005, NEW-NIST-WEBBOOK-CO2

### RX39 · Carbonation of C-S-H (full decalcification)

- Family: MgO systems and carbonation
- Chemical: (CaO)1.7·SiO2·(H2O)4 + 1.7 CO2 → 1.7 CaCO3 + SiO2 (gel) + 4 H2O
- Cement notation: `C1.7SH4 + 1.7c → 1.7Cc + S + 4H`
- Scheme basis: derived
- C-S-H assumed: C1.7SH4 (Ca/Si 1.7, H/Si 4.0, saturated) — Tennis & Jennings write 2 Si as C3.4S2H8; Bentz CEMHYD3D uses C1.7SH4.0 with 108 cm3/mol.
- Per gram of CSH17: water -0.3168 g H2O per g CSH17 [derived; NEW-CIAAW]; CH 0.0 g CH per g CSH17 [derived; NEW-CIAAW]
- Heat: 642.0 J per g CSH17 (heat released, +) [derived; NEW-BENTZ-2005, NEW-NIST-WEBBOOK-CO2, R334] — ΔrH° = -146.1 kJ per 1 mol CSH17, from standard enthalpies of formation at 25 °C (NEW-BENTZ-2005, NEW-NIST-WEBBOOK-CO2, R334). Mixed-source sets are approximate.
- Chemical shrinkage: -0.2464 cm3 per g CSH17 [derived; NEW-BENTZ-2005, R334] — Condensed phases only (CO2 gas excluded): ΣV reactants - ΣV products = -56.05 cm3 per 1 mol CSH17. Negative = solid+water volume increases.

| Species | Side | Coef | M (g/mol) | g per g key | V (cm3/mol) | ρ (g/cm3) |
|---|---|---|---|---|---|---|
| C1.7SH4 (saturated C-S-H; = C3.4S2H8 per 2 Si) | reactant | 1 | 227.47 | -1.0 | 108.0 [NEW-BENTZ-2005] | 2.106 |
| CO2 (gas) | reactant | 1.7 | 44.01 | -0.3289 | unknown  | unknown |
| CaCO3 (calcite) | product | 1.7 | 100.09 | 0.748 | 36.93 [NEW-BENTZ-2005] | 2.71 |
| SiO2 (silica gel, anhydrous basis) | product | 1 | 60.08 | 0.2641 | 29 [R334] | 2.072 |
| H2O (liquid) | product | 4 | 18.02 | 0.3168 | 18.07 [NEW-BENTZ-2005] | 0.997 |

Conditions and caveats: End member: silica gel written anhydrous (its water content varies); partial decalcification gives low-Ca/Si C-S-H. Enthalpy mixes Bentz C-S-H and calcite, Cemdata18 SiO2(am) and NIST CO2 values: approximate.

Sources: NEW-BENTZ-2005, NEW-NIST-WEBBOOK-CO2, R334

### RX40 · Carbonation of ettringite

- Family: MgO systems and carbonation
- Chemical: Ca6Al2(SO4)3(OH)12·26H2O + 3 CO2 → 3 CaCO3 + 3 CaSO4·2H2O + Al2O3·3H2O + 23 H2O
- Cement notation: `C6As3H32 + 3c → 3Cc + 3CsH2 + AH3 + 23H`
- Scheme basis: derived
- C-S-H assumed: None.
- Per gram of AFt: water -0.3301 g H2O per g AFt [derived; NEW-CIAAW]; CH 0.0 g CH per g AFt [derived; NEW-CIAAW]
- Heat: 96.0 J per g AFt (heat released, +) [derived; NEW-BENTZ-2005, NEW-NIST-WEBBOOK-CO2, R334] — ΔrH° = -120.5 kJ per 1 mol AFt, from standard enthalpies of formation at 25 °C (NEW-BENTZ-2005, NEW-NIST-WEBBOOK-CO2, R334). Mixed-source sets are approximate.
- Chemical shrinkage: -0.0621 cm3 per g AFt [derived; NEW-BENTZ-2005, R334] — Condensed phases only (CO2 gas excluded): ΣV reactants - ΣV products = -77.97 cm3 per 1 mol AFt. Negative = solid+water volume increases.

| Species | Side | Coef | M (g/mol) | g per g key | V (cm3/mol) | ρ (g/cm3) |
|---|---|---|---|---|---|---|
| C6As3H32 (ettringite, AFt) | reactant | 1 | 1255.07 | -1.0 | 735.01 [NEW-BENTZ-2005] | 1.708 |
| CO2 (gas) | reactant | 3 | 44.01 | -0.1052 | unknown  | unknown |
| CaCO3 (calcite) | product | 3 | 100.09 | 0.2392 | 36.93 [NEW-BENTZ-2005] | 2.71 |
| CaSO4·2H2O (gypsum) | product | 3 | 172.16 | 0.4115 | 74.21 [NEW-BENTZ-2005] | 2.32 |
| Al2O3·3H2O = 2 Al(OH)3 (gibbsite / AH3) | product | 1 | 156.01 | 0.1243 | 64 [R334] | 2.438 |
| H2O (liquid) | product | 23 | 18.02 | 0.3301 | 18.07 [NEW-BENTZ-2005] | 0.997 |

Conditions and caveats: Balance derived here; scheme not taken from an inspected source. The solid volume falls by roughly half; the condensed-phase figure is negative only because the 23 H2O released is counted as liquid.

Sources: balance derived only

