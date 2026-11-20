#!/usr/bin/env python3
"""Generate data/reactions.json and research/reactions.md (cement reaction stoichiometry table).

Every number is either SOURCED (copied from a source that was opened and read on 2026-11-20,
with the location given) or DERIVED (computed here from sourced numbers and IUPAC/CIAAW atomic
weights). Fields without a sourced or derivable value are null with basis "unknown".
"""
import json, sys, datetime
from pathlib import Path

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
CAL = 4.184  # J per thermochemical calorie (conversion used for Lerch & Bogue cal/g values)

# ------------------------------------------------------------------ sources
SOURCES = {
 "R210": {"kind": "index", "title": "Heat of hydration of portland cement pastes (NBS RP684)", "authors": "W. Lerch, R.H. Bogue", "year": 1934,
          "url": "https://doi.org/10.6028/jres.012.057", "inspected": "https://nvlpubs.nist.gov/nistpubs/jres/12/jresv12n5p645_A2b.pdf",
          "used_for": "Heats of complete hydration of C3S, beta-C2S, C3A, C4AF (Table 1 and summary); MgO and free CaO values the authors took from the literature; 149 cal/g SO3 for sulfoaluminate formation; 3.7 and 2.7 kcal/mol for hemihydrate and soluble anhydrite to gypsum; clinker test cases (Table 1, series K-3)."},
 "R334": {"kind": "index", "title": "Cemdata18: A chemical thermodynamic database for hydrated Portland cements and alkali-activated materials", "authors": "B. Lothenbach, D.A. Kulik, T. Matschei, M. Balonis, L. Baquerizo, B. Dilnesa, G.D. Miron, R.J. Myers", "year": 2019,
          "url": "https://doi.org/10.1016/j.cemconres.2018.04.018", "inspected": "https://www.dora.lib4ri.ch/psi/dload/psi:25804/PDF2/view (accepted manuscript)",
          "used_for": "Standard molar volumes V° (cm3/mol) and enthalpies of formation ΔfH° (kJ/mol) at 25 °C, Tables 1, 3 and 4; statement that calcium carbonate prevents destabilisation of ettringite to monosulfate."},
 "R880": {"kind": "index", "title": "Calculation of Cement Composition Using a New Model Compared to the Bogue Model", "authors": "S.-H. Shim, T.-H. Lee, S.-J. Yang, N.B.Md. Noor, J.-H.-J. Kim", "year": 2021,
          "url": "https://doi.org/10.3390/ma14164663", "inspected": "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8401079/fullTextXML",
          "used_for": "Bogue equations as given for ASTM C150 including SO3 and CO2 terms, Eqs. (5)-(8)."},
 "R330": {"kind": "index", "title": "Hydration of calcium sulfoaluminate cements — Experimental findings and thermodynamic modelling", "authors": "F. Winnefeld, B. Lothenbach", "year": 2010,
          "url": "https://doi.org/10.1016/j.cemconres.2009.08.014", "inspected": "https://www.dora.lib4ri.ch/empa/dload/empa:3987/PDF2/view (accepted manuscript)",
          "used_for": "Ye'elimite hydration with and without calcium sulfate (Eqs. 1-2) and strätlingite formation from belite and AH3 (Eq. 3); strätlingite only stable without portlandite."},
 "R372": {"kind": "index", "title": "Calcium aluminate cement conversion analysed by ptychographic nanotomography", "authors": "S. Shirani, A. Cuesta, A.G. De la Torre, A. Diaz, P. Trtik, M. Holler, M.A.G. Aranda", "year": 2020,
          "url": "https://doi.org/10.1016/j.cemconres.2020.106201", "inspected": "https://www.dora.lib4ri.ch/psi/dload/psi:34224/PDF2/view (submitted manuscript)",
          "used_for": "CA hydration and conversion reactions (1)-(5) with molar masses, densities, molar volumes and theoretical chemical shrinkage / secondary porosity (Tables 1-2)."},
 "R1882": {"kind": "index", "title": "Hydration reactions in portland cement-silica fume blends", "authors": "Huang Cheng-yi, R.F. Feldman", "year": 1985,
          "url": "https://doi.org/10.1016/0008-8846(85)90056-0", "inspected": "https://nrc-publications.canada.ca/eng/view/ft/?id=d6e9dce9-a723-44fc-92a1-1e3e46143b6c",
          "used_for": "Cement, silica fume and fly ash oxide analyses and Bogue phases (Table I); Ca(OH)2 contents of plain and silica-fume pastes (test cases)."},
 "R3883": {"kind": "index", "title": "A model for two types of calcium silicate hydrate in the microstructure of Portland cement pastes", "authors": "P.D. Tennis, H.M. Jennings", "year": 2000,
          "url": "https://doi.org/10.1016/s0008-8846(00)00257-x", "inspected": "https://web.archive.org/web/20240413122239/https://hal.science/hal-03680316/document",
          "used_for": "Hydration reactions Eqs. (1)-(6) with C3.4S2H8 (=C1.7SH4) C-S-H; densities and molar masses (Table 1); saturated C-S-H density 1990 kg/m3; Avrami constants for degree of hydration by phase (Table 2)."},
 "R3079": {"kind": "index", "title": "Advances in understanding ye'elimite-rich cements", "authors": "M.A.G. Aranda, ... (review)", "year": 2019,
          "url": "https://doi.org/10.1016/j.cemconres.2019.105778", "inspected": "https://web.archive.org/web/20240414205653/https://hal.science/hal-02386829/document",
          "used_for": "Context only: CAH10 can form with ettringite and AH3 when calcium sulfate is low; AH3 gel density about 1.5 g/cm3 in CSA paste versus 2.40 g/cm3 for gibbsite."},
 "NEW-BENTZ-2005": {"kind": "new-candidate", "title": "CEMHYD3D: A Three-Dimensional Cement Hydration and Microstructure Development Modeling Package. Version 3.0 (NIST IR 7232)", "authors": "D.P. Bentz", "year": 2005,
          "url": "https://doi.org/10.6028/NIST.IR.7232", "inspected": "https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nistir7232.pdf",
          "used_for": "Molar volumes, specific gravities and heats of formation of cement phases and hydrates as coded in disrealnew.c (Appendix B, after Fukuhara et al. 1981); pozzolanic C1.1SH3.9 product; 780 J/g silica fume, 800 J/g slag, 800 J/g AS heats; slag hydration product stoichiometries (Table 2) and slagchar.dat example."},
 "NEW-BENTZ-2009": {"kind": "new-candidate", "title": "Limestone Fillers Conserve Cement; Part 1: An analysis based on Powers' model", "authors": "D.P. Bentz, E.F. Irassar, B.E. Bucher, W.J. Weiss", "year": 2009,
          "url": "https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=901137", "inspected": "https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=923437 (manuscript) and pub_id=901137 (Concrete International 31(11) 41-46)",
          "used_for": "Powers' model volume fractions with Jensen & Hansen parameters (non-evaporable water 0.23, chemical shrinkage 0.064, gel water 0.19 g/g), inert limestone filler, and worked results (w/c 0.356, 0.42, 8.7 % porosity, w/cm 0.338-0.267)."},
 "NEW-LEON-CHEN-2021": {"kind": "new-candidate", "title": "Thermal Analysis of Mass Concrete Containing Ground Granulated Blast Furnace Slag", "authors": "G. Leon, H.-L. Chen", "year": 2021,
          "url": "https://doi.org/10.3390/civileng2010014", "inspected": "https://www.mdpi.com/2673-4109/2/1/14",
          "used_for": "Secondary citation of Schindler & Folliard (2005): ultimate heat of GGBFS 461 J/g (Grade 100) and 550 J/g (Grade 120)."},
 "NEW-NIST-WEBBOOK-CO2": {"kind": "new-candidate", "title": "Carbon dioxide — Gas phase thermochemistry data (NIST Chemistry WebBook, SRD 69)", "authors": "NIST", "year": None,
          "url": "https://webbook.nist.gov/cgi/cbook.cgi?ID=C124389&Mask=1", "inspected": "https://webbook.nist.gov/cgi/cbook.cgi?ID=C124389&Mask=1",
          "used_for": "ΔfH° CO2(g) = -393.51 kJ/mol (CODATA)."},
 "NEW-CIAAW": {"kind": "new-candidate", "title": "Abridged Standard Atomic Weights", "authors": "IUPAC Commission on Isotopic Abundances and Atomic Weights (CIAAW)", "year": None,
          "url": "https://www.ciaaw.org/abridged-atomic-weights.htm", "inspected": "https://www.ciaaw.org/abridged-atomic-weights.htm",
          "used_for": "Atomic weights for all derived molar masses."},
}

# ------------------------------------------------------------------ atomic weights (CIAAW abridged)
AW = {"H": 1.0080, "C": 12.011, "O": 15.999, "Na": 22.990, "Mg": 24.305, "Al": 26.982, "Si": 28.085, "S": 32.06, "K": 39.098, "Ca": 40.078, "Fe": 55.845}
OX = {  # cement-notation oxide -> molar mass (derived)
 "C": AW["Ca"] + AW["O"], "S": AW["Si"] + 2*AW["O"], "A": 2*AW["Al"] + 3*AW["O"], "F": 2*AW["Fe"] + 3*AW["O"],
 "s": AW["S"] + 3*AW["O"], "H": 2*AW["H"] + AW["O"], "c": AW["C"] + 2*AW["O"], "M": AW["Mg"] + AW["O"],
 "N": 2*AW["Na"] + AW["O"], "K": 2*AW["K"] + AW["O"],
}

# ------------------------------------------------------------------ species
# oxide composition, then sourced molar volumes (cm3/mol), densities (g/cm3) and ΔfH (kJ/mol), by source
B, CD, TJ, R372 = "NEW-BENTZ-2005", "R334", "R3883", "R372"
SP = {}
def sp(key, ox, label, V=None, dH=None, rho=None, note=None):
    SP[key] = {"ox": ox, "label": label, "V": V or {}, "dH": dH or {}, "rho": rho or {}, "note": note}

sp("H", {"H": 1}, "H2O (liquid)", V={B: 18.068}, dH={B: -285.83}, rho={B: 0.99707})
sp("C3S", {"C": 3, "S": 1}, "Ca3SiO5 (alite, C3S)", V={B: 71.129, CD: 73}, dH={B: -2927.82, CD: -2931}, rho={B: 3.21, TJ: 3.150})
sp("C2S", {"C": 2, "S": 1}, "Ca2SiO4 (belite, C2S)", V={B: 52.513, CD: 52}, dH={B: -2311.6, CD: -2308}, rho={B: 3.28, TJ: 3.280})
sp("C3A", {"C": 3, "A": 1}, "Ca3Al2O6 (C3A)", V={B: 88.94, CD: 89}, dH={B: -3587.8, CD: -3561}, rho={B: 3.038, TJ: 3.030})
sp("C4AF", {"C": 4, "A": 1, "F": 1}, "Ca4Al2Fe2O10 (C4AF)", V={B: 130.29, CD: 130}, dH={B: -5090.3, CD: -5080}, rho={B: 3.73, TJ: 3.730})
sp("CsH2", {"C": 1, "s": 1, "H": 2}, "CaSO4·2H2O (gypsum)", V={B: 74.21, CD: 75}, dH={B: -2022.6, CD: -2023.36}, rho={B: 2.32, TJ: 2.320})
sp("CsH05", {"C": 1, "s": 1, "H": 0.5}, "CaSO4·0.5H2O (hemihydrate)", V={B: 52.973, CD: 62}, dH={B: -1574.65, CD: -1575.3}, rho={B: 2.74})
sp("Cs", {"C": 1, "s": 1}, "CaSO4 (anhydrite)", V={B: 52.16, CD: 46}, dH={B: -1424.6, CD: -1434.60}, rho={B: 2.61},
   note="Bentz codes anhydrite at SG 2.61 (52.16 cm3/mol); Cemdata18 gives 46 cm3/mol for anhydrite. The difference matters for shrinkage.")
sp("CH", {"C": 1, "H": 1}, "Ca(OH)2 (portlandite, CH)", V={B: 33.1, CD: 33}, dH={B: -986.1, CD: -985}, rho={B: 2.24, TJ: 2.240})
sp("C", {"C": 1}, "CaO (free lime)", V={CD: 17}, dH={CD: -635})
sp("M", {"M": 1}, "MgO (periclase)")
sp("MH", {"M": 1, "H": 1}, "Mg(OH)2 (brucite)")
sp("Mc", {"M": 1, "c": 1}, "MgCO3 (magnesite)")
sp("Cc", {"C": 1, "c": 1}, "CaCO3 (calcite)", V={B: 36.93}, dH={B: -1206.92}, rho={B: 2.71})
sp("c", {"c": 1}, "CO2 (gas)", dH={"NEW-NIST-WEBBOOK-CO2": -393.51})
sp("CSH17", {"C": 1.7, "S": 1, "H": 4}, "C1.7SH4 (saturated C-S-H; = C3.4S2H8 per 2 Si)", V={B: 108.0}, dH={B: -3283.0}, rho={B: 2.11, TJ: 1.990},
   note="Bentz molar volume 108 cm3/mol (SG 2.11) was tuned for chemical-shrinkage agreement; Tennis & Jennings give 1990 kg/m3 as the optimum saturated density.")
sp("CSH11", {"C": 1.1, "S": 1, "H": 3.9}, "C1.1SH3.9 (pozzolanic C-S-H)", V={B: 101.81}, dH={B: -2299.1}, rho={B: 1.884})
sp("S", {"S": 1}, "SiO2 (reactive silica: silica fume / glass)", V={B: 27.0, CD: 29}, dH={B: -907.5, CD: -903}, rho={B: 2.22},
   note="Bentz uses quartz ΔfH for unreacted pozzolan and SG 2.22; Cemdata18 SiO2(am) V° 29, ΔfH° -903.")
sp("AS", {"A": 1, "S": 1}, "Al2O3·SiO2 (aluminosilicate glass, 'ASG' in CEMHYD3D)", V={B: 49.9}, rho={B: 3.247})
sp("AS2", {"A": 1, "S": 2}, "Al2Si2O7 (metakaolin, AS2)")
sp("C3AH6", {"C": 3, "A": 1, "H": 6}, "Ca3Al2(OH)12 (hydrogarnet / katoite, C3AH6)", V={B: 150.12, CD: 150}, dH={B: -5548.0, CD: -5537.3}, rho={B: 2.52, R372: 2.53})
sp("C3AFH6", {"C": 3, "A": 0.5, "F": 0.5, "H": 6}, "C3(A,F)H6 (Fe-bearing hydrogarnet)", rho={TJ: 2.670})
sp("FH3", {"F": 1, "H": 3}, "Fe2O3·3H2O (FH3, iron hydroxide)", V={B: 69.803}, dH={B: -823.9}, rho={B: 3.062})
sp("AFt", {"C": 6, "A": 1, "s": 3, "H": 32}, "C6As3H32 (ettringite, AFt)", V={B: 735.01, CD: 707}, dH={B: -17539.0, CD: -17535}, rho={B: 1.7076, TJ: 1.750})
sp("AFm", {"C": 4, "A": 1, "s": 1, "H": 12}, "C4AsH12 (monosulfate, AFm)", V={B: 312.82, CD: 310}, dH={B: -8778.0, CD: -8758.6}, rho={B: 1.99, TJ: 1.990})
sp("C4AH13", {"C": 4, "A": 1, "H": 13}, "C4AH13 (hydroxy-AFm)", V={CD: 274}, dH={CD: -8262.4}, rho={TJ: 2.050})
sp("Hc", {"C": 4, "A": 1, "c": 0.5, "H": 12}, "C4Ac0.5H12 (hemicarbonate)", V={CD: 285}, dH={CD: -8270})
sp("Mc_AFm", {"C": 4, "A": 1, "c": 1, "H": 11}, "C4AcH11 (monocarbonate)", V={B: 261.91, CD: 262}, dH={CD: -8250}, rho={B: 2.17},
   note="Bentz leaves its heat of formation as 0 ('fill in later'), so only Cemdata18 ΔfH is used.")
sp("C2ASH8", {"C": 2, "A": 1, "S": 1, "H": 8}, "C2ASH8 (strätlingite)", V={B: 215.63, CD: 216}, dH={CD: -6360}, rho={B: 1.94})
sp("AH3", {"A": 1, "H": 3}, "Al2O3·3H2O = 2 Al(OH)3 (gibbsite / AH3)", V={CD: 64}, dH={CD: -2577.4}, rho={R372: 2.42},
   note="Cemdata18 lists Al(OH)3 gibbsite per Al(OH)3 (V° 32, ΔfH° -1288.7); values here are doubled for AH3. R372 uses gel densities 2.00-2.20 g/cm3 in its reactions; R3079 reports about 1.5 g/cm3 for AH3 gel in CSA paste.")
sp("C4A3s", {"C": 4, "A": 3, "s": 1}, "Ca4Al6O12SO4 (ye'elimite, C4A3s)")
sp("CA", {"C": 1, "A": 1}, "CaAl2O4 (monocalcium aluminate, CA)", V={CD: 54, R372: 53.39}, dH={CD: -2327}, rho={R372: 2.96})
sp("CAH10", {"C": 1, "A": 1, "H": 10}, "CaAl2O4·10H2O (CAH10)", V={CD: 193, R372: 196.62}, dH={CD: -5288.2}, rho={R372: 1.72})
sp("C2AH8", {"C": 2, "A": 1, "H": 8}, "Ca2Al2O5·8H2O (C2AH8)", V={R372: 187.56}, rho={R372: 1.91},
   note="Cemdata18 lists C2AH7.5 (V° 180, ΔfH° -5277.5), not C2AH8.")
sp("M4AH10", {"M": 4, "A": 1, "H": 10}, "Mg4Al2(OH)14·3H2O (hydrotalcite-like, M4AH10)", V={CD: 220}, dH={CD: -7196})
sp("MSH", {"M": 1.5, "S": 1, "H": 2.5}, "M1.5SH2.5 (M-S-H, Mg/Si 1.5)", V={CD: 74}, dH={CD: -2594.22})
sp("SLAG1", {"C": 16.5, "S": 17, "M": 6.5, "A": 2, "s": 1}, "Slag 1 of Bentz Table 2 (39.2 SiO2, 7.9 Al2O3, 36.25 CaO, 10.3 MgO, 3.1 SO3 %)")
sp("SLAG1P", {"C": 21.25, "S": 17, "M": 6.5, "A": 2, "s": 1, "H": 86}, "Slag 1 hydration product (Bentz Table 2)")
sp("SLAG2", {"C": 21.5, "S": 15, "M": 5.5, "A": 3, "s": 1}, "Slag 2 of Bentz Table 2 (34.7 SiO2, 11.4 Al2O3, 45.5 CaO, 8.5 MgO, 3.0 SO3 %)", V={B: 945.72}, rho={B: 2.87})
sp("SLAG2P", {"C": 20.25, "S": 15, "M": 5.5, "A": 2, "s": 1, "H": 83}, "Slag 2 hydration product (Bentz Table 2 / slagchar.dat)", V={B: 1717.53}, rho={B: 2.35})
sp("SH0", {"S": 1}, "SiO2 (silica gel, anhydrous basis)", V={CD: 29}, dH={CD: -903})

def M(key):
    return sum(n * OX[o] for o, n in SP[key]["ox"].items())

# ------------------------------------------------------------------ helpers
def sv(value, unit, basis, sources, note=None, **kw):
    d = {"value": value, "unit": unit, "basis": basis, "sources": sources}
    if note: d["note"] = note
    d.update(kw)
    return d

def unknown(unit, note):
    return {"value": None, "unit": unit, "basis": "unknown", "sources": [], "note": note}

def rnd(x, n=4):
    return None if x is None else float(f"{x:.{n}g}") if abs(x) < 1 else round(x, 2 if abs(x) < 100 else 1)

VOL_PREF = [B, CD, R372]
DH_SETS = [[B], [CD, B, "NEW-NIST-WEBBOOK-CO2"], [B, "NEW-NIST-WEBBOOK-CO2"]]

def pick_vol(key, pref):
    s = SP[key]
    for src in pref:
        if src in s["V"]:
            return s["V"][src], src
    for src in pref:
        if src in s["rho"]:
            return M(key) / s["rho"][src], src + " (density)"
    for src in VOL_PREF + [TJ]:  # fall back to any inspected source (e.g. water from Bentz)
        if src in s["V"]:
            return s["V"][src], src
    for src in VOL_PREF + [TJ]:
        if src in s["rho"]:
            return M(key) / s["rho"][src], src + " (density)"
    return None, None

def reaction(rid, family, name, lhs, rhs, chem, cement, key, csh, conditions, src_reaction, heat=None,
             vol_pref=None, dh_sets=None, extra=None, csh_alt=None, sourced_shrinkage=None, scheme_basis="sourced"):
    """lhs/rhs: list of (coef, species). key: species whose gram is the basis."""
    vol_pref = vol_pref or VOL_PREF
    # balance check
    bal = {}
    for c, k in lhs:
        for o, n in SP[k]["ox"].items(): bal[o] = bal.get(o, 0) - c * n
    for c, k in rhs:
        for o, n in SP[k]["ox"].items(): bal[o] = bal.get(o, 0) + c * n
    bad = {o: v for o, v in bal.items() if abs(v) > 1e-9}
    if bad:
        raise SystemExit(f"{rid} not balanced: {bad}")
    ck = next(c for c, k in lhs if k == key)
    mkey = ck * M(key)
    species = []
    for side, lst in (("reactant", lhs), ("product", rhs)):
        for c, k in lst:
            mm = M(k)
            v, vsrc = pick_vol(k, vol_pref)
            species.append({
                "species": k, "label": SP[k]["label"], "side": side, "coef": c,
                "molarMass": sv(round(mm, 2), "g/mol", "derived", ["NEW-CIAAW"]),
                "massPerGramKey": sv(round((c * mm / mkey) * (-1 if side == "reactant" else 1), 4), "g per g " + key, "derived", ["NEW-CIAAW"]),
                "molarVolume": (sv(round(v, 2), "cm3/mol", "sourced" if "density" not in vsrc else "derived", [vsrc.split(" ")[0]],
                                   note=("from density" if "density" in vsrc else None)) if v else unknown("cm3/mol", "no molar volume or density found in an inspected source")),
                "density": (sv(round(mm / v, 3), "g/cm3", "derived" if "density" not in vsrc else "sourced", [vsrc.split(" ")[0]]) if v else unknown("g/cm3", "no density found in an inspected source")),
            })
    water = sum(c for c, k in lhs if k == "H") - sum(c for c, k in rhs if k == "H")
    ch = sum(c for c, k in rhs if k == "CH") - sum(c for c, k in lhs if k == "CH")
    out = {
        "id": rid, "family": family, "name": name,
        "equationChemical": chem, "equationCement": cement,
        "schemeBasis": scheme_basis,
        "keyPhase": key, "keyPhaseLabel": SP[key]["label"],
        "cshStoichiometry": csh, "cshAlternatives": csh_alt or [],
        "species": species,
        "waterConsumedPerGram": sv(round(water * OX["H"] / mkey, 4), "g H2O per g " + key, "derived", ["NEW-CIAAW"],
                                   note="Water written into the products as balanced (saturated hydrates). Negative = water released."),
        "chPerGram": sv(round(ch * M("CH") / mkey, 4), "g CH per g " + key, "derived", ["NEW-CIAAW"], note="Positive = CH produced; negative = CH consumed."),
        "heat": [], "chemicalShrinkage": None, "conditions": conditions, "sources": sorted(set(src_reaction)),
    }
    # heats
    for h in (heat or []):
        out["heat"].append(h)
    for hs in (dh_sets or DH_SETS):
        tot = 0; used = set(); ok = True
        for side, lst in ((-1, lhs), (1, rhs)):
            for c, k in lst:
                val = None
                for src in hs:
                    if src in SP[k]["dH"]:
                        val = SP[k]["dH"][src]; used.add(src); break
                if val is None:
                    ok = False; break
                tot += side * c * val
            if not ok: break
        if ok:
            out["heat"].append(sv(round(-tot * 1000 / mkey, 0), "J per g " + key + " (heat released, +)", "derived", sorted(used),
                                  note=f"ΔrH° = {tot:+.1f} kJ per {ck:g} mol {key}, from standard enthalpies of formation at 25 °C ({', '.join(sorted(used))}). Mixed-source sets are approximate."))
            break
    if not out["heat"]:
        out["heat"].append(unknown("J/g", "no measured heat and incomplete enthalpy-of-formation data in the inspected sources"))
    # chemical shrinkage
    vr = vp = 0; vsrcs = set(); ok = True
    for side, lst in ((0, lhs), (1, rhs)):
        for c, k in lst:
            v, vsrc = pick_vol(k, vol_pref)
            if v is None:
                ok = False; break
            vsrcs.add(vsrc.split(" ")[0])
            if side == 0: vr += c * v
            else: vp += c * v
        if not ok: break
    if ok:
        out["chemicalShrinkage"] = sv(round((vr - vp) / mkey, 4), "cm3 per g " + key, "derived", sorted(vsrcs),
                                      note=f"(ΣV reactants incl. water - ΣV products) = {vr - vp:.2f} cm3 per {ck:g} mol {key}; {100 * (vr - vp) / vr:.1f} % of reactant volume. Positive = volume loss.",
                                      percentOfReactantVolume=round(100 * (vr - vp) / vr, 1))
    else:
        out["chemicalShrinkage"] = unknown("cm3/g", "at least one species has no molar volume in the inspected sources")
    if sourced_shrinkage:
        out["chemicalShrinkageSourced"] = sourced_shrinkage
    if extra:
        out.update(extra)
    return out

LB = lambda calg, what, loc: sv(round(calg * CAL, 0), "J/g", "sourced", ["R210"],
                                note=f"{calg} cal/g {what} (Lerch & Bogue 1934, {loc}); converted at 4.184 J/cal (conversion derived).", calPerGram=calg)

CSH17 = "C1.7SH4 (Ca/Si 1.7, H/Si 4.0, saturated) — Tennis & Jennings write 2 Si as C3.4S2H8; Bentz CEMHYD3D uses C1.7SH4.0 with 108 cm3/mol."
CSH17_ALT = [
    {"formula": "C3.4S2H8", "CaSi": 1.7, "HSi": 4.0, "note": "Same stoichiometry per Si (Tennis & Jennings Eq. 1-2).", "sources": ["R3883"]},
    {"formula": "C3.4S2H3 (D-dried)", "CaSi": 1.7, "HSi": 1.5, "note": "Dried composition, density 1440 (LD) / 1750 (HD) kg/m3.", "sources": ["R3883"]},
    {"formula": "C1.67SH2.1 (CSH-II 'Jen' end member)", "CaSi": 1.67, "HSi": 2.1, "note": "Thermodynamic end member, V° 78 cm3/mol; not saturated-gel water.", "sources": ["R334"]},
    {"formula": "C2SHx (Lerch & Bogue product)", "CaSi": 2.0, "HSi": None, "note": "Lerch & Bogue state their 'complete hydration' heats correspond to conversion to 2CaO·SiO2·xH2O, not 3CaO·2SiO2·xH2O.", "sources": ["R210"]},
]

R = []
# ---------------- clinker phases
R.append(reaction("RX01", "Clinker silicates", "Alite (C3S) hydration",
    [(1, "C3S"), (5.3, "H")], [(1, "CSH17"), (1.3, "CH")],
    "Ca3SiO5 + 5.3 H2O → (CaO)1.7·SiO2·(H2O)4 + 1.3 Ca(OH)2", "C3S + 5.3H → C1.7SH4 + 1.3CH", "C3S", CSH17,
    "Ideal end-state reaction; C-S-H Ca/Si and water content vary with w/c, temperature, drying and SCMs. Heats from Lerch & Bogue refer to a C2S·xH2O end product.",
    ["R3883", B], heat=[LB(120, "C3S, heat of complete hydration", "Table 1 and summary")], csh_alt=CSH17_ALT))
R.append(reaction("RX02", "Clinker silicates", "Belite (C2S) hydration",
    [(1, "C2S"), (4.3, "H")], [(1, "CSH17"), (0.3, "CH")],
    "Ca2SiO4 + 4.3 H2O → (CaO)1.7·SiO2·(H2O)4 + 0.3 Ca(OH)2", "C2S + 4.3H → C1.7SH4 + 0.3CH", "C2S", CSH17,
    "Lerch & Bogue's β-C2S still held about 2-3 % unhydrated material when its heat was measured.",
    ["R3883", B], heat=[LB(62, "β-C2S, heat of complete hydration", "Table 1 and summary")], csh_alt=CSH17_ALT))
R.append(reaction("RX03", "Clinker aluminate (C3A)", "C3A + gypsum → ettringite",
    [(1, "C3A"), (3, "CsH2"), (26, "H")], [(1, "AFt")],
    "Ca3Al2O6 + 3 CaSO4·2H2O + 26 H2O → Ca6Al2(SO4)3(OH)12·26H2O", "C3A + 3CsH2 + 26H → C6As3H32", "C3A", "None (no C-S-H).",
    "Early reaction while calcium sulfate is available. Lerch & Bogue give 149 cal per g SO3 for gypsum + C3A hydrate → sulfoaluminate (computed, on top of the C3A heat).",
    ["R3883", B, "R210"], heat=[sv(round(149 * CAL, 0), "J per g SO3 combined (in addition to the C3A heat)", "sourced", ["R210"],
        note="149 cal/g SO3 for 3CaO·Al2O3·6H2O + 3CaSO4·2H2O + 19H2O → 3CaO·Al2O3·3CaSO4·31H2O (computed by Lerch & Bogue); converted at 4.184 J/cal.", calPerGram=149)]))
R.append(reaction("RX04", "Clinker aluminate (C3A)", "Ettringite → monosulfate (sulfate depleted)",
    [(2, "C3A"), (1, "AFt"), (4, "H")], [(3, "AFm")],
    "2 Ca3Al2O6 + Ca6Al2(SO4)3(OH)12·26H2O + 4 H2O → 3 Ca4Al2(SO4)(OH)12·6H2O", "2C3A + C6As3H32 + 4H → 3C4AsH12", "C3A", "None.",
    "Proceeds after calcium sulfate is consumed. In the presence of calcite, carboaluminates form instead and ettringite stays stable (see RX16).",
    ["R3883", B]))
R.append(reaction("RX05", "Clinker aluminate (C3A)", "C3A hydration without sulfate → hydrogarnet",
    [(1, "C3A"), (6, "H")], [(1, "C3AH6")],
    "Ca3Al2O6 + 6 H2O → Ca3Al2(OH)12", "C3A + 6H → C3AH6", "C3A", "None.",
    "Stable end product of pure C3A hydration; flash set in cement if no sulfate. Lerch & Bogue's 207 cal/g is for this complete hydration (Thorvaldson reported 214.3 cal/g to C3AH6).",
    ["R210", B], heat=[LB(207, "C3A, heat of complete hydration", "Table 1 and summary")]))
R.append(reaction("RX06", "Clinker aluminate (C3A)", "C3A + CH without sulfate → C4AH13",
    [(1, "C3A"), (1, "CH"), (12, "H")], [(1, "C4AH13")],
    "Ca3Al2O6 + Ca(OH)2 + 12 H2O → Ca4Al2(OH)14·6H2O", "C3A + CH + 12H → C4AH13", "C3A", "None.",
    "Tennis & Jennings Eq. 5: continued C3A hydration after all ettringite is consumed.",
    ["R3883", "R334"], vol_pref=[CD, B], dh_sets=[[CD, B]]))
R.append(reaction("RX07", "Clinker ferrite (C4AF)", "C4AF + gypsum → Fe-bearing ettringite + CH + FH3",
    [(1, "C4AF"), (3, "CsH2"), (30, "H")], [(1, "AFt"), (1, "CH"), (1, "FH3")],
    "Ca4Al2Fe2O10 + 3 CaSO4·2H2O + 30 H2O → Ca6Al2(SO4)3(OH)12·26H2O + Ca(OH)2 + Fe2O3·3H2O",
    "C4AF + 3CsH2 + 30H → C6As3H32 + CH + FH3", "C4AF", "None.",
    "Simplified: iron is written as separate FH3 and the AFt as Al-ettringite. Phase set as coded in CEMHYD3D (ETTRC4AF, FH3, CH); balance derived here. Real ferrite reacts slowly and Fe partly enters AFt/AFm/hydrogarnet.",
    [B], heat=[LB(100, "C4AF, heat of complete hydration (end state, not this specific path)", "Table 1 and summary")], scheme_basis="derived", dh_sets=[["NONE"]],
    extra={"heatNote": "No enthalpy is derived: the FH3 heat of formation coded in CEMHYD3D (-823.9 kJ/mol) equals that of anhydrous Fe2O3, so a derived value would be wrong."}))
R.append(reaction("RX08", "Clinker ferrite (C4AF)", "C4AF + ettringite → monosulfate + CH + FH3",
    [(2, "C4AF"), (1, "AFt"), (12, "H")], [(3, "AFm"), (2, "CH"), (2, "FH3")],
    "2 Ca4Al2Fe2O10 + Ca6Al2(SO4)3(OH)12·26H2O + 12 H2O → 3 Ca4Al2(SO4)(OH)12·6H2O + 2 Ca(OH)2 + 2 Fe2O3·3H2O",
    "2C4AF + C6As3H32 + 12H → 3C4AsH12 + 2CH + 2FH3", "C4AF", "None.",
    "Simplified analogue of RX04 for ferrite; balance derived here using the CEMHYD3D phase set.", [B], scheme_basis="derived", dh_sets=[["NONE"]],
    extra={"heatNote": "No enthalpy is derived (see RX07: inconsistent FH3 heat of formation)."}))
R.append(reaction("RX09", "Clinker ferrite (C4AF)", "C4AF + CH without sulfate → Fe-bearing hydrogarnet",
    [(1, "C4AF"), (2, "CH"), (10, "H")], [(2, "C3AFH6")],
    "Ca4Al2Fe2O10 + 2 Ca(OH)2 + 10 H2O → 2 Ca3(Al,Fe)2(OH)12", "C4AF + 2CH + 10H → 2C3(A,F)H6", "C4AF", "None.",
    "Tennis & Jennings Eq. 6 (hydrogarnet product).", ["R3883"], vol_pref=[B, CD, TJ],
    heat=[LB(100, "C4AF, heat of complete hydration", "Table 1 and summary")]))
# ---------------- sulfates
R.append(reaction("RX10", "Calcium sulfates", "Hemihydrate → gypsum",
    [(1, "CsH05"), (1.5, "H")], [(1, "CsH2")],
    "CaSO4·0.5H2O + 1.5 H2O → CaSO4·2H2O", "CsH0.5 + 1.5H → CsH2", "CsH05", "None.",
    "Lerch & Bogue: 3.7 kcal/mol (46 cal per g SO3); they recommend leaving it out of cement heat totals (about 1 cal/g cement, variable dehydration during grinding).",
    ["R210", B], heat=[sv(round(3700 * CAL / M("CsH05"), 0), "J per g hemihydrate", "derived", ["R210"],
        note="From 3.7 kcal/mol (Lerch & Bogue p. 652) ÷ molar mass of CaSO4·0.5H2O; 46 cal/g SO3 as printed.")]))
R.append(reaction("RX11", "Calcium sulfates", "Anhydrite → gypsum",
    [(1, "Cs"), (2, "H")], [(1, "CsH2")],
    "CaSO4 + 2 H2O → CaSO4·2H2O", "Cs + 2H → CsH2", "Cs", "None.",
    "Lerch & Bogue's 2.7 kcal/mol is for soluble (γ-) anhydrite; natural (insoluble) anhydrite reacts slowly. Bentz and Cemdata18 molar volumes for anhydrite differ (52.16 vs 46 cm3/mol).",
    ["R210", B], heat=[sv(round(2700 * CAL / M("Cs"), 0), "J per g anhydrite", "derived", ["R210"],
        note="From 2.7 kcal/mol (soluble anhydrite, Lerch & Bogue p. 652) ÷ molar mass of CaSO4; 34 cal/g SO3 as printed.")]))
# ---------------- free lime / periclase
R.append(reaction("RX12", "Free lime and periclase", "Free lime hydration",
    [(1, "C"), (1, "H")], [(1, "CH")],
    "CaO + H2O → Ca(OH)2", "C + H → CH", "C", "None.",
    "Large solid-volume increase (expansion risk when hard-burnt free lime hydrates late).",
    ["R210", "R334"], heat=[LB(278.6, "CaO (literature value quoted by Lerch & Bogue, Thorvaldson et al.)", "p. 651")], vol_pref=[CD, B], dh_sets=[[CD, B]]))
R.append(reaction("RX13", "Free lime and periclase", "Periclase (MgO) hydration",
    [(1, "M"), (1, "H")], [(1, "MH")],
    "MgO + H2O → Mg(OH)2", "M + H → MH", "M", "None.",
    "Slow for dead-burnt periclase in clinker; delayed expansion (soundness, autoclave test). Molar volumes of periclase/brucite were not found in the inspected sources.",
    ["R210"], heat=[LB(203, "MgO (literature value quoted by Lerch & Bogue)", "p. 651")]))
# ---------------- limestone
R.append(reaction("RX14", "Limestone (Type IL)", "Hemicarbonate formation",
    [(1, "C3A"), (0.5, "Cc"), (0.5, "CH"), (11.5, "H")], [(1, "Hc")],
    "Ca3Al2O6 + 0.5 CaCO3 + 0.5 Ca(OH)2 + 11.5 H2O → Ca4Al2(CO3)0.5(OH)13·5.5H2O",
    "C3A + 0.5Cc + 0.5CH + 11.5H → C4Ac0.5H12", "C3A", "None.",
    "Forms at low carbonate availability, early; converts to monocarbonate as more calcite dissolves. Balance derived; phase data from Cemdata18.",
    ["R334"], vol_pref=[CD, B], dh_sets=[[CD, B]], scheme_basis="derived"))
R.append(reaction("RX15", "Limestone (Type IL)", "Monocarbonate formation",
    [(1, "C3A"), (1, "Cc"), (11, "H")], [(1, "Mc_AFm")],
    "Ca3Al2O6 + CaCO3 + 11 H2O → Ca4Al2(CO3)(OH)12·5H2O", "C3A + Cc + 11H → C4AcH11", "C3A", "None.",
    "Thermodynamically favoured over monosulfate when calcite is present. Only a small fraction of limestone reacts (Bentz: about 5 % of a 20 % limestone replacement in 180 d of simulated hydration).",
    ["R334", B], vol_pref=[CD, B], dh_sets=[[CD, B]], scheme_basis="derived"))
R.append(reaction("RX16", "Limestone (Type IL)", "Carboaluminate stabilisation of ettringite (monosulfate + calcite → monocarbonate + ettringite)",
    [(3, "AFm"), (2, "Cc"), (18, "H")], [(2, "Mc_AFm"), (1, "AFt")],
    "3 Ca4Al2(SO4)(OH)12·6H2O + 2 CaCO3 + 18 H2O → 2 Ca4Al2(CO3)(OH)12·5H2O + Ca6Al2(SO4)3(OH)12·26H2O",
    "3C4AsH12 + 2Cc + 18H → 2C4AcH11 + C6As3H32", "AFm", "None.",
    "Reaction as implemented in CEMHYD3D v3.0 (Bentz 2005, section on limestone). Cemdata18: calcium carbonate prevents destabilisation of ettringite to monosulfate. Net solid volume increases, one reason Type IL pastes can show lower porosity.",
    [B, "R334"], vol_pref=[CD, B], dh_sets=[[CD, B]]))
# ---------------- pozzolanic
R.append(reaction("RX17", "Pozzolanic (siliceous)", "Pozzolanic reaction of silica (silica fume, siliceous fly ash glass, natural pozzolan)",
    [(1, "S"), (1.1, "CH"), (2.8, "H")], [(1, "CSH11")],
    "SiO2 + 1.1 Ca(OH)2 + 2.8 H2O → (CaO)1.1·SiO2·(H2O)3.9", "S + 1.1CH + 2.8H → C1.1SH3.9", "S",
    "C1.1SH3.9 (Ca/Si 1.1, H/Si 3.9) — pozzolanic C-S-H in CEMHYD3D after Atlassi, de Larrard and Jensen.",
    "Bentz: gives about 0.2 g H2O per g silica fume chemical shrinkage; 780 J/g silica fume assumed. Real pozzolanic C-S-H Ca/Si depends on CH availability.",
    [B], heat=[sv(780, "J per g silica fume reacted", "sourced", [B], note="'Assume 780 J/g S for pozzolanic reaction' (disrealnew.c listing).")], dh_sets=[["NONE"]],
    extra={"heatNote": "No enthalpy is derived from the CEMHYD3D heats of formation: its C1.1SH3.9 value was back-fitted to 780 J/g with a different water accounting and gives an inconsistent result."},
    csh_alt=[{"formula": "C1.7SH4 → C1.1SH3.9 conversion", "CaSi": 1.1, "HSi": 3.9, "note": "CEMHYD3D optionally converts C1.7SH4 to C1.1SH3.9 releasing CH when silica fume is abundant.", "sources": [B]}],
    sourced_shrinkage=sv(0.2, "g H2O per g silica fume (≈ cm3/g)", "sourced", [B], note="Comment in disrealnew.c: 'gives a chemical shrinkage of 0.2 g H2O/g CSF'.")))
R.append(reaction("RX18", "Pozzolanic (aluminous)", "Aluminosilicate glass (AS) + CH → strätlingite",
    [(1, "AS"), (2, "CH"), (6, "H")], [(1, "C2ASH8")],
    "Al2O3·SiO2 + 2 Ca(OH)2 + 6 H2O → Ca2Al2SiO7·8H2O", "AS + 2CH + 6H → C2ASH8", "AS", "None (strätlingite).",
    "CEMHYD3D fly-ash glass reaction. Strätlingite is only stable when portlandite is absent (R330), so with excess CH AFm/hydrogarnet may form instead.",
    [B, "R330"], heat=[sv(800, "J per g AS reacted", "sourced", [B], note="'Assume 800 J/g AS for stratlingite formation (DeLarrard)' (disrealnew.c listing).")]))
R.append(reaction("RX19", "Pozzolanic (aluminous)", "Metakaolin / calcined clay + CH → strätlingite + C-S-H",
    [(1, "AS2"), (3.1, "CH"), (8.8, "H")], [(1, "C2ASH8"), (1, "CSH11")],
    "Al2Si2O7 + 3.1 Ca(OH)2 + 8.8 H2O → Ca2Al2SiO7·8H2O + (CaO)1.1·SiO2·(H2O)3.9",
    "AS2 + 3.1CH + 8.8H → C2ASH8 + C1.1SH3.9", "AS2", "C1.1SH3.9 (Bentz pozzolanic C-S-H) for the second Si.",
    "Low-CH end member; balance derived here by combining RX18-type strätlingite with Bentz pozzolanic C-S-H. Real LC3/metakaolin systems form C-A-S-H, carboaluminates and AFm (R547, R561, R3092 not used for numbers).",
    [B, "R330"], scheme_basis="derived"))
R.append(reaction("RX20", "Pozzolanic (aluminous)", "Metakaolin / calcined clay + excess CH → C4AH13 + C-S-H",
    [(1, "AS2"), (6.2, "CH"), (14.6, "H")], [(1, "C4AH13"), (2, "CSH11")],
    "Al2Si2O7 + 6.2 Ca(OH)2 + 14.6 H2O → Ca4Al2(OH)14·6H2O + 2 (CaO)1.1·SiO2·(H2O)3.9",
    "AS2 + 6.2CH + 14.6H → C4AH13 + 2C1.1SH3.9", "AS2", "C1.1SH3.9 (Bentz pozzolanic C-S-H).",
    "High-CH end member; balance derived here. With calcite present, carboaluminates replace C4AH13 (LC3).",
    [B, "R334"], scheme_basis="derived"))
R.append(reaction("RX21", "Pozzolanic (aluminous)", "Belite + AH3 → strätlingite (CSA and blended systems)",
    [(1, "C2S"), (1, "AH3"), (5, "H")], [(1, "C2ASH8")],
    "Ca2SiO4 + Al2O3·3H2O + 5 H2O → Ca2Al2SiO7·8H2O", "C2S + AH3 + 5H → C2ASH8", "C2S", "None.",
    "Winnefeld & Lothenbach Eq. 3; seen after 28 d in CSA cements. Only stable without portlandite.",
    ["R330"], vol_pref=[CD, B], dh_sets=[[CD, B]]))
# ---------------- slag
R.append(reaction("RX22", "Slag", "Slag 1 (Bentz Table 2) + CH → mixed slag hydration product",
    [(1, "SLAG1"), (4.75, "CH"), (81.25, "H")], [(1, "SLAG1P")],
    "slag glass (CaO)16.5(SiO2)17(MgO)6.5(Al2O3)2(SO3) + 4.75 Ca(OH)2 + 81.25 H2O → (CaO)21.25(SiO2)17(MgO)6.5(Al2O3)2(SO3)(H2O)86 (mixed C-S-H/AFm/hydrotalcite)",
    "C16.5S17M6.5A2s + 4.75CH + 81.25H → C21.25S17M6.5A2sH86", "SLAG1",
    "Product Ca/Si 1.25 and H/Si 5.06 for the whole mixed product (C-S-H with AFm, hydrotalcite) — not a pure C-S-H.",
    "Slag and product compositions from Bentz 2005 Table 2 (slag 1, no extra C3A); CH and water coefficients derived by balance. Heat: Bentz assumes 800 J/g slag; Schindler & Folliard use 461 J/g (Grade 100) or 550 J/g (Grade 120).",
    [B, "NEW-LEON-CHEN-2021"], heat=[
        sv(800, "J per g slag reacted", "sourced", [B], note="'Assume 800 J/g S for slag reaction' (disrealnew.c listing; comment cites Biernacki & Richardson)."),
        sv(461, "J per g slag (Grade 100)", "sourced", ["NEW-LEON-CHEN-2021"], note="Schindler & Folliard (2005) as quoted by Leon & Chen 2021; 550 J/g for Grade 120.")],
    scheme_basis="derived"))
R.append(reaction("RX23", "Slag", "Slag 2 (Bentz Table 2) + CH → mixed product + 'extra C3A'",
    [(1, "SLAG2"), (1.75, "CH"), (81.25, "H")], [(1, "SLAG2P"), (1, "C3A")],
    "slag glass (CaO)21.5(SiO2)15(MgO)5.5(Al2O3)3(SO3) + 1.75 Ca(OH)2 + 81.25 H2O → C20.25S15M5.5A2sH83 + C3A (which then reacts as cement C3A)",
    "C21.5S15M5.5A3s + 1.75CH + 81.25H → C20.25S15M5.5A2sH83 + C3A", "SLAG2",
    "Product Ca/Si 1.35, H/Si 5.533 (slagchar.dat example) for the mixed product.",
    "CEMHYD3D: when Mg/Al is well below 2, extra Al reacts like C3A (ettringite, AFm, hydrogarnet). Molar volumes of slag (945.72) and product (1717.53 cm3/mol) from slagchar.dat; shrinkage here excludes the later hydration of the 'extra C3A'.",
    [B], heat=[sv(800, "J per g slag reacted", "sourced", [B], note="'Assume 800 J/g S for slag reaction' (disrealnew.c).")], scheme_basis="derived"))
R.append(reaction("RX24", "Slag", "Hydrotalcite formation from slag Mg and Al (schematic)",
    [(4, "M"), (1, "AH3"), (7, "H")], [(1, "M4AH10")],
    "4 MgO + Al2O3·3H2O + 7 H2O → Mg4Al2(OH)14·3H2O (oxide bookkeeping only)",
    "4M + AH3 + 7H → M4AH10", "M", "None.",
    "Bookkeeping reaction showing how slag Mg and Al end up in a hydrotalcite-like phase (Mg/Al = 2). Slag Mg and Al come from the glass, not from periclase/AH3; heat not defined.",
    ["R334"], vol_pref=[CD], scheme_basis="derived"))
# ---------------- CSA
R.append(reaction("RX25", "Calcium sulfoaluminate (ye'elimite)", "Ye'elimite without calcium sulfate → monosulfate + AH3",
    [(1, "C4A3s"), (18, "H")], [(1, "AFm"), (2, "AH3")],
    "Ca4Al6O12SO4 + 18 H2O → Ca4Al2(SO4)(OH)12·6H2O + 2 Al2O3·3H2O", "C4A3s + 18H → C4AsH12 + 2AH3", "C4A3s", "None.",
    "Winnefeld & Lothenbach Eq. 1. AH3 is usually poorly crystalline (gel). Ye'elimite molar volume not found in inspected sources, so shrinkage is unknown. CAH10 can also form when sulfate is low (R3079).",
    ["R330", "R3079"]))
R.append(reaction("RX26", "Calcium sulfoaluminate (ye'elimite)", "Ye'elimite + gypsum → ettringite + AH3",
    [(1, "C4A3s"), (2, "CsH2"), (34, "H")], [(1, "AFt"), (2, "AH3")],
    "Ca4Al6O12SO4 + 2 CaSO4·2H2O + 34 H2O → Ca6Al2(SO4)3(OH)12·26H2O + 2 Al2O3·3H2O", "C4A3s + 2CsH2 + 34H → C6As3H32 + 2AH3", "C4A3s", "None.",
    "Winnefeld & Lothenbach Eq. 2. Winnefeld & Lothenbach report a calculated chemical shrinkage of 11.4-11.5 cm3/100 g for two whole CSA cements at 28 d.",
    ["R330"], sourced_shrinkage=sv(0.114, "cm3 per g CSA cement (whole cement, 28 d, CSA-1; 0.115 for CSA-2)", "sourced", ["R330"], note="Calculated by thermodynamic modelling for the cements, not for this single reaction.")))
R.append(reaction("RX27", "Calcium sulfoaluminate (ye'elimite)", "Ye'elimite + gypsum + CH → ettringite (expansive formulation)",
    [(1, "C4A3s"), (8, "CsH2"), (6, "CH"), (74, "H")], [(3, "AFt")],
    "Ca4Al6O12SO4 + 8 CaSO4·2H2O + 6 Ca(OH)2 + 74 H2O → 3 Ca6Al2(SO4)3(OH)12·26H2O",
    "C4A3s + 8CsH2 + 6CH + 74H → 3C6As3H32", "C4A3s", "None.",
    "All Al to ettringite when CH and sulfate are in excess (expansive/shrinkage-compensating systems). Balance derived here; this scheme was not taken from an inspected source.",
    [], scheme_basis="derived"))
# ---------------- CAC
R372_sh = lambda cm3, pct: sv(cm3, "cm3 per mol (theoretical)", "sourced", ["R372"], note=f"Theoretical chemical shrinkage {cm3} cm3/mol or {pct} % (Shirani et al., Table 1).")
R.append(reaction("RX28", "Calcium aluminate cement (CA)", "CA → CAH10 (mainly below 15 °C)",
    [(1, "CA"), (10, "H")], [(1, "CAH10")],
    "CaAl2O4 + 10 H2O → CaAl2O4·10H2O", "CA + 10H → CAH10", "CA", "None.",
    "Metastable hydrate; converts with time and temperature (RX31, RX32).",
    ["R372", "R334"], vol_pref=[R372, CD], dh_sets=[[CD, B]], sourced_shrinkage=R372_sh(-36.97, 15.8)))
R.append(reaction("RX29", "Calcium aluminate cement (CA)", "CA → C2AH8 + AH3 (mainly 15-50 °C)",
    [(2, "CA"), (11, "H")], [(1, "C2AH8"), (1, "AH3")],
    "2 CaAl2O4 + 11 H2O → Ca2Al2O5·8H2O + 2 Al(OH)3", "2CA + 11H → C2AH8 + AH3", "CA", "None.",
    "Al(OH)3 forms as a gel (density about 2.00 g/cm3 used by Shirani et al.).",
    ["R372"], vol_pref=[R372, CD], sourced_shrinkage=R372_sh(-39.44, 12.9)))
R.append(reaction("RX30", "Calcium aluminate cement (CA)", "CA → C3AH6 + AH3 (mainly above 50 °C)",
    [(3, "CA"), (12, "H")], [(1, "C3AH6"), (2, "AH3")],
    "3 CaAl2O4 + 12 H2O → Ca3Al2(OH)12 + 4 Al(OH)3", "3CA + 12H → C3AH6 + 2AH3", "CA", "None.",
    "Stable assemblage; high porosity if formed by conversion in place.",
    ["R372", "R334"], vol_pref=[R372, CD], dh_sets=[[CD, B]], sourced_shrinkage=R372_sh(-85.08, 22.6)))
R.append(reaction("RX31", "Calcium aluminate cement (CA)", "Conversion CAH10 → C2AH8 + AH3 + water",
    [(2, "CAH10")], [(1, "C2AH8"), (1, "AH3"), (9, "H")],
    "2 CaAl2O4·10H2O → Ca2Al2O5·8H2O + 2 Al(OH)3 + 9 H2O", "2CAH10 → C2AH8 + AH3 + 9H", "CAH10", "None.",
    "Releases water and solid volume (secondary porosity 162.18 cm3, 37.9 % of solid reactant volume, Shirani et al.). Proceeds through solution, needs free water.",
    ["R372"], vol_pref=[R372, CD],
    sourced_shrinkage=sv(37.9, "% of solid reactant volume turned into porosity", "sourced", ["R372"], note="Secondary water porosity 162.18 cm3 per 2 mol CAH10.")))
R.append(reaction("RX32", "Calcium aluminate cement (CA)", "Conversion C2AH8 → C3AH6 + AH3 + water",
    [(3, "C2AH8")], [(2, "C3AH6"), (1, "AH3"), (9, "H")],
    "3 Ca2Al2O5·8H2O → 2 Ca3Al2(OH)12 + 2 Al(OH)3 + 9 H2O", "3C2AH8 → 2C3AH6 + AH3 + 9H", "C2AH8", "None.",
    "Secondary porosity 162.18 cm3 or 28.8 % of solid reactant volume (Shirani et al.). Strength loss in CAC concrete above about w/c 0.40 is linked to conversion.",
    ["R372"], vol_pref=[R372, CD],
    sourced_shrinkage=sv(28.8, "% of solid reactant volume turned into porosity", "sourced", ["R372"], note="Secondary water porosity 162.18 cm3 per 3 mol C2AH8.")))
R.append(reaction("RX33", "Calcium aluminate cement (CA)", "Overall conversion CAH10 → C3AH6 + AH3 + water",
    [(3, "CAH10")], [(1, "C3AH6"), (2, "AH3"), (18, "H")],
    "3 CaAl2O4·10H2O → Ca3Al2(OH)12 + 4 Al(OH)3 + 18 H2O", "3CAH10 → C3AH6 + 2AH3 + 18H", "CAH10", "None.",
    "Sum of RX31 and RX32 (balance derived). Endothermic ΔrH° here uses gibbsite; gel AH3 differs.",
    ["R372", "R334"], vol_pref=[R372, CD], dh_sets=[[CD, B]], scheme_basis="derived"))
# ---------------- alkali activation (schematic)
R.append({"id": "RX34", "family": "Alkali activation", "name": "Metakaolin or low-Ca fly ash + NaOH / sodium silicate → N-A-S-H gel (schematic)",
    "equationChemical": "Al2Si2O7 (+ SiO2 from silicate) + 2 NaOH + n H2O → Na2O·Al2O3·xSiO2·mH2O (N-A-S-H, Si/Al ≥ 1)",
    "equationCement": "AS2 + N(H) + (S) + H → N-A-S-H", "schemeBasis": "schematic", "keyPhase": "AS2", "keyPhaseLabel": SP["AS2"]["label"],
    "cshStoichiometry": "No C-S-H. Gel Si/Al and water content depend on the activator modulus; Na/Al ≈ 1 for charge balance.", "cshAlternatives": [],
    "species": [{"species": "AS2", "label": SP["AS2"]["label"], "side": "reactant", "coef": 1, "molarMass": sv(round(M("AS2"), 2), "g/mol", "derived", ["NEW-CIAAW"])}],
    "waterConsumedPerGram": unknown("g/g", "Gel water content varies; much of the water is released (condensation), not bound."),
    "chPerGram": unknown("g CH per g precursor", "schematic reaction with no balanced stoichiometry; portlandite is not a reactant or product in the scheme"),
    "heat": [unknown("J/g", "no value in the inspected sources")], "chemicalShrinkage": unknown("cm3/g", "no value in the inspected sources"),
    "conditions": "Schematic only. Cemdata18 provides zeolite and C-(N-)A-S-H data for alkali-activated materials but no single N-A-S-H reaction; no numeric stoichiometry is given here.",
    "sources": ["R334"]})
R.append({"id": "RX35", "family": "Alkali activation", "name": "Slag + NaOH or Na2SiO3 → C-(N-)A-S-H + hydrotalcite (schematic)",
    "equationChemical": "slag glass (CaO-SiO2-Al2O3-MgO) + NaOH / Na2SiO3 + H2O → C-(N-)A-S-H (Ca/Si ≈ 1) + Mg-Al LDH (hydrotalcite) ± AFm",
    "equationCement": "slag + N(H) / NS + H → C-(N-)A-S-H + M4AH10 (± AFm)", "schemeBasis": "schematic", "keyPhase": "slag", "keyPhaseLabel": "slag glass",
    "cshStoichiometry": "C-(N-)A-S-H, e.g. Cemdata18 CNASH end members such as 5CNA = C1.25N0.25A0.125SH1.375 (V° 64.5 cm3/mol) or INFCNA = C1A0.156N0.344S1.188H1.313 (V° 69.3 cm3/mol).",
    "cshAlternatives": [{"formula": "5CNA: C5/4N1/4A1/8S1H11/8", "CaSi": 1.25, "HSi": 1.375, "note": "CNASH solid-solution end member (V° 64.5, ΔfH° -2568.7 kJ/mol).", "sources": ["R334"]},
                        {"formula": "INFCNA: C1A5/32N11/32S38/32H42/32", "CaSi": round(1 / (38 / 32), 3), "HSi": round((42 / 32) / (38 / 32), 3), "note": "CNASH end member (V° 69.3, ΔfH° -2666.7 kJ/mol).", "sources": ["R334"]}],
    "species": [], "waterConsumedPerGram": unknown("g/g", "depends on slag and activator; not given in inspected sources"),
    "chPerGram": unknown("g CH per g slag", "schematic reaction with no balanced stoichiometry; portlandite is not a product in the scheme"),
    "heat": [unknown("J/g", "no value in the inspected sources")], "chemicalShrinkage": unknown("cm3/g", "no value in the inspected sources"),
    "conditions": "Schematic only; Cemdata18 recommends its MgAl-OH-LDH data for alkali-activated materials.", "sources": ["R334"]})
# ---------------- MgO / carbonation
R.append(reaction("RX36", "MgO systems and carbonation", "Brucite carbonation → magnesite (schematic end member)",
    [(1, "MH"), (1, "c")], [(1, "Mc"), (1, "H")],
    "Mg(OH)2 + CO2 → MgCO3 + H2O", "MH + c → Mc + H", "MH", "None.",
    "At ambient conditions hydrated Mg carbonates (e.g. nesquehonite, hydromagnesite) form rather than magnesite; masses only.",
    [], scheme_basis="derived"))
R.append(reaction("RX37", "MgO systems and carbonation", "M-S-H formation from brucite and silica",
    [(1.5, "MH"), (1, "SH0"), (1, "H")], [(1, "MSH")],
    "1.5 Mg(OH)2 + SiO2 + H2O → (MgO)1.5·SiO2·(H2O)2.5", "1.5MH + S + H → M1.5SH2.5", "SH0", "None (M-S-H, Mg/Si 1.5).",
    "M-S-H end member from Cemdata18 (Mg/Si 1.5). Brucite molar volume and ΔfH° not in the inspected sources, so shrinkage and heat are unknown.",
    ["R334"], vol_pref=[CD], scheme_basis="derived"))
R.append(reaction("RX38", "MgO systems and carbonation", "Carbonation of portlandite",
    [(1, "CH"), (1, "c")], [(1, "Cc"), (1, "H")],
    "Ca(OH)2 + CO2 → CaCO3 + H2O", "CH + c → Cc + H", "CH", "None.",
    "Solid volume increases (calcite larger than portlandite); pH drops. Volumes here count CO2 as zero-volume gas (only the solid and water volumes are compared).",
    [B, "NEW-NIST-WEBBOOK-CO2"], vol_pref=[B], dh_sets=[[B, "NEW-NIST-WEBBOOK-CO2"]], scheme_basis="derived"))
R.append(reaction("RX39", "MgO systems and carbonation", "Carbonation of C-S-H (full decalcification)",
    [(1, "CSH17"), (1.7, "c")], [(1.7, "Cc"), (1, "SH0"), (4, "H")],
    "(CaO)1.7·SiO2·(H2O)4 + 1.7 CO2 → 1.7 CaCO3 + SiO2 (gel) + 4 H2O",
    "C1.7SH4 + 1.7c → 1.7Cc + S + 4H", "CSH17", CSH17,
    "End member: silica gel written anhydrous (its water content varies); partial decalcification gives low-Ca/Si C-S-H. Enthalpy mixes Bentz C-S-H and calcite, Cemdata18 SiO2(am) and NIST CO2 values: approximate.",
    [B, "R334", "NEW-NIST-WEBBOOK-CO2"], vol_pref=[B, CD], dh_sets=[[B, CD, "NEW-NIST-WEBBOOK-CO2"]], scheme_basis="derived"))
R.append(reaction("RX40", "MgO systems and carbonation", "Carbonation of ettringite",
    [(1, "AFt"), (3, "c")], [(3, "Cc"), (3, "CsH2"), (1, "AH3"), (23, "H")],
    "Ca6Al2(SO4)3(OH)12·26H2O + 3 CO2 → 3 CaCO3 + 3 CaSO4·2H2O + Al2O3·3H2O + 23 H2O",
    "C6As3H32 + 3c → 3Cc + 3CsH2 + AH3 + 23H", "AFt", "None.",
    "Balance derived here; scheme not taken from an inspected source. The solid volume falls by roughly half; the condensed-phase figure is negative only because the 23 H2O released is counted as liquid.",
    [], vol_pref=[B, CD], dh_sets=[[B, CD, "NEW-NIST-WEBBOOK-CO2"]], scheme_basis="derived"))

# CO2 volume: treat gas as zero solid volume for RX36/38/39/40
for r in R:
    for s in r.get("species", []):
        if s.get("species") == "c":
            s["molarVolume"] = unknown("cm3/mol", "gas; left out of the condensed-phase volume balance (shrinkage compares solids and liquid water only)")
            s["density"] = unknown("g/cm3", "gas")
# recompute shrinkage for CO2 reactions with gas = 0
SP["c"]["V"]["GAS0"] = 0.0
def recompute(rid, pref):
    r = next(x for x in R if x["id"] == rid)
    vr = vp = 0; ok = True; srcs = set()
    for s in r["species"]:
        k = s["species"]
        if k == "c":
            continue
        v, vs = pick_vol(k, pref)
        if v is None: ok = False; break
        srcs.add(vs.split(" ")[0])
        if s["side"] == "reactant": vr += s["coef"] * v
        else: vp += s["coef"] * v
    key = r["keyPhase"]; ck = next(s["coef"] for s in r["species"] if s["species"] == key and s["side"] == "reactant")
    if ok:
        r["chemicalShrinkage"] = sv(round((vr - vp) / (ck * M(key)), 4), "cm3 per g " + key, "derived", sorted(srcs),
            note=f"Condensed phases only (CO2 gas excluded): ΣV reactants - ΣV products = {vr - vp:.2f} cm3 per {ck:g} mol {key}. Negative = solid+water volume increases.",
            percentOfReactantVolume=round(100 * (vr - vp) / vr, 1))
for rid, pref in (("RX38", [B]), ("RX39", [B, CD]), ("RX40", [B, CD])):
    recompute(rid, pref)

# ------------------------------------------------------------------ counting
def walk(o, acc):
    if isinstance(o, dict):
        if "basis" in o and "value" in o:
            acc[o["basis"]] = acc.get(o["basis"], 0) + 1
        for v in o.values(): walk(v, acc)
    elif isinstance(o, list):
        for v in o: walk(v, acc)
counts = {}
walk(R, counts)

PHASE_DATA = {k: {"label": v["label"], "oxides": v["ox"], "molarMass": round(M(k), 3), "V": v["V"] and {s: x for s, x in v["V"].items() if s != "GAS0"}, "dH": v["dH"], "rho": v["rho"], "note": v["note"]} for k, v in SP.items()}

doc = {
    "title": "Cement reaction stoichiometry table",
    "version": "2026-11-20",
    "generated": "2026-11-20",
    "description": "Balanced cement and binder reactions with molar masses, per-gram water, CH, heat, molar volumes and chemical shrinkage. Each number is tagged sourced (copied from a source that was opened and read), derived (computed here from sourced numbers and CIAAW atomic weights) or unknown.",
    "disclaimer": "Idealised end-state stoichiometry for orientation. Real hydrate compositions, especially C-S-H, AFm, AFt and gels, vary with composition, temperature, w/c and age. Not a substitute for testing or thermodynamic modelling (e.g. GEMS with Cemdata18).",
    "notation": {"C": "CaO", "S": "SiO2", "A": "Al2O3", "F": "Fe2O3", "s": "SO3", "c": "CO2", "H": "H2O", "M": "MgO", "N": "Na2O", "K": "K2O", "CH": "Ca(OH)2"},
    "conventions": {"calorie": "4.184 J (thermochemical calorie) used to convert Lerch & Bogue cal/g values.",
                    "water": "Water consumed = H2O written into the balanced products (saturated hydrates), per gram of the key phase.",
                    "chemicalShrinkage": "(ΣV reactants incl. liquid water - ΣV products)/mass of key phase, using the molar volumes listed per species (source per value). Positive = volume loss.",
                    "heat": "Positive J/g = heat released per gram of the key phase (or the basis stated)."},
    "oxideMolarMasses": {k: round(v, 3) for k, v in OX.items()},
    "atomicWeights": AW,
    "counts": {"reactions": len(R), "sourcedValues": counts.get("sourced", 0), "derivedValues": counts.get("derived", 0), "unknownValues": counts.get("unknown", 0)},
    "sources": SOURCES,
    "phases": PHASE_DATA,
    "reactions": R,
}
(OUT / "data").mkdir(parents=True, exist_ok=True)
(OUT / "data/reactions.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

# ------------------------------------------------------------------ markdown
def fmt(v):
    if v is None: return "—"
    if isinstance(v, dict):
        if v.get("value") is None: return "unknown"
        return f"{v['value']} {v['unit']} [{v['basis']}; {', '.join(v['sources']) or '—'}]"
    return str(v)
L = ["# Cement reaction stoichiometry table", "",
     f"Generated 2026-11-20 from `data/reactions.json`. {len(R)} reactions; {counts.get('sourced',0)} sourced values, {counts.get('derived',0)} derived values, {counts.get('unknown',0)} unknown fields.", "",
     "> " + doc["disclaimer"], "",
     "Each number is tagged **sourced** (copied from a source opened and read on 2026-11-20), **derived** (computed from sourced numbers and CIAAW atomic weights), or **unknown** (left blank instead of guessed). Index R numbers point to records in `data/site-data.json`; `NEW-*` sources are recorded in `research/reactions-candidates.jsonl` for the daily run to verify and number.", "",
     "Notation: C = CaO, S = SiO2, A = Al2O3, F = Fe2O3, s = SO3, c = CO2, H = H2O, M = MgO, CH = Ca(OH)2.", "",
     "## Sources", ""]
for k, s in SOURCES.items():
    L.append(f"- **{k}** ({s['kind']}): {s['authors']} ({s['year'] or 'n.d.'}). *{s['title']}*. {s['url']} — inspected at {s['inspected']}. Used for: {s['used_for']}")
L += ["", "## Reactions", ""]
for r in R:
    L += [f"### {r['id']} · {r['name']}", "", f"- Family: {r['family']}", f"- Chemical: {r['equationChemical']}", f"- Cement notation: `{r['equationCement']}`",
          f"- Scheme basis: {r['schemeBasis']}", f"- C-S-H assumed: {r['cshStoichiometry']}"]
    for a in r.get("cshAlternatives", []):
        L.append(f"  - alternative {a['formula']} (Ca/Si {a['CaSi']}, H/Si {a['HSi']}): {a['note']} [{', '.join(a['sources'])}]")
    L.append(f"- Per gram of {r['keyPhase']}: water {fmt(r['waterConsumedPerGram'])}; CH {fmt(r['chPerGram'])}")
    for h in r["heat"]:
        L.append(f"- Heat: {fmt(h)}" + (f" — {h['note']}" if h.get("note") else ""))
    cs = r["chemicalShrinkage"]
    L.append(f"- Chemical shrinkage: {fmt(cs)}" + (f" — {cs['note']}" if cs and cs.get('note') else ""))
    if r.get("chemicalShrinkageSourced"):
        c2 = r["chemicalShrinkageSourced"]; L.append(f"- Chemical shrinkage (as published): {fmt(c2)} — {c2.get('note','')}")
    if r.get("species"):
        L += ["", "| Species | Side | Coef | M (g/mol) | g per g key | V (cm3/mol) | ρ (g/cm3) |", "|---|---|---|---|---|---|---|"]
        for s in r["species"]:
            mv = s.get("molarVolume", {}); de = s.get("density", {})
            L.append(f"| {s['label']} | {s['side']} | {s['coef']} | {s['molarMass']['value']} | {s.get('massPerGramKey',{}).get('value','—')} | "
                     f"{mv.get('value') if mv.get('value') is not None else 'unknown'} {('['+', '.join(mv.get('sources',[]))+']') if mv.get('sources') else ''} | "
                     f"{de.get('value') if de.get('value') is not None else 'unknown'} |")
    L += ["", f"Conditions and caveats: {r['conditions']}", "", f"Sources: {', '.join(r['sources']) or 'balance derived only'}", ""]
(OUT / "research").mkdir(parents=True, exist_ok=True)
(OUT / "research/reactions.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print(json.dumps(doc["counts"]))
