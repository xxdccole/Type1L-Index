// Node test cases for js/calculator.js against published worked values.
// Run from the repo root: node tests/calculator.test.js   (exit code 1 on failure)
"use strict";
const path = require("path");
const C = require(path.join(__dirname, "..", "js", "calculator.js"));
const results = [];
function check(id, what, got, want, tol, source) {
  const ok = Math.abs(got - want) <= tol;
  results.push({ id, what, got: +got.toFixed(4), published: want, tolerance: tol, pass: ok, source });
}
function note(id, what, got, published, source, comment) {
  results.push({ id, what, got: typeof got === "number" ? +got.toFixed(4) : got, published, tolerance: null, pass: null, source, comment });
}

// T1 Bogue (ASTM C150 form, R880 Eqs 5-8) vs Huang & Feldman 1985 Table I (R1882)
let b = C.bogue({ CaO: 63.07, SiO2: 21.16, Al2O3: 5.87, Fe2O3: 2.21, SO3: 3.29 });
check("T1a", "Bogue C3S, R1882 cement", b.C3S, 43.96, 0.05, "R1882 Table I");
check("T1b", "Bogue C2S, R1882 cement", b.C2S, 27.47, 0.05, "R1882 Table I");
check("T1c", "Bogue C3A, R1882 cement", b.C3A, 11.82, 0.05, "R1882 Table I");
check("T1d", "Bogue C4AF, R1882 cement", b.C4AF, 6.72, 0.05, "R1882 Table I");

// T2 Bogue with free-lime subtraction vs Lerch & Bogue 1934 Table 1, clinkers K-3 (R210); printed as integers
const K3 = [
  { no: 4, CaO: 63.7, Al2O3: 4.0, Fe2O3: 4.9, SiO2: 23.9, MgO: 3.1, fl: 0, ph: [44, 36, 2, 15], qCalc: 100, qExp: 97 },
  { no: 5, CaO: 64.7, Al2O3: 7.0, Fe2O3: 2.0, SiO2: 22.1, MgO: 3.7, fl: 0, ph: [46, 29, 15, 6], qCalc: 118, qExp: 126 },
  { no: 15, CaO: 66.6, Al2O3: 7.4, Fe2O3: 1.7, SiO2: 19.8, MgO: 4.0, fl: 1.5, ph: [62, 10, 17, 5], qCalc: 133, qExp: 145 },
  { no: 17, CaO: 65.4, Al2O3: 5.4, Fe2O3: 5.5, SiO2: 20.0, MgO: 3.3, fl: 0, ph: [69, 5, 5, 17], qCalc: 120, qExp: 119 },
];
K3.forEach(k => {
  const r = C.bogue({ CaO: k.CaO, SiO2: k.SiO2, Al2O3: k.Al2O3, Fe2O3: k.Fe2O3, SO3: 0, freeCaO: k.fl }, { subtractFreeLime: true });
  ["C3S", "C2S", "C3A", "C4AF"].forEach((p, i) => check(`T2-${k.no}-${p}`, `Bogue ${p}, clinker No. ${k.no}`, r[p], k.ph[i], 1.5, "R210 Table 1 (printed as integers; 1934 coefficients differ slightly from the ASTM C150 form)"));
});

// T3 Heat of complete hydration from compound composition vs Lerch & Bogue's computed values (R210 Table 1)
K3.forEach(k => {
  const r = C.compute({
    cement: { mode: "phases", phases: { C3S: k.ph[0], C2S: k.ph[1], C3A: k.ph[2], C4AF: k.ph[3], sulfate: 0, limestone: 0, freeCaO: k.fl, periclase: k.MgO } },
    batch: { cementKg: 1, waterKg: 0.5 }, hydration: { mode: "alpha", alpha: 1 }, scms: []
  });
  const calg = r.heat.QinfPerKgCement / 4.184;
  check(`T3-${k.no}`, `Q∞ cal/g, clinker No. ${k.no} (vs computed value)`, calg, k.qCalc, 1.0, "R210 Table 1 'calculated heat of hydration'");
  note(`T3-${k.no}x`, `Q∞ cal/g, clinker No. ${k.no} (vs experimental value)`, calg, k.qExp, "R210 Table 1 'heat evolved on complete hydration'",
       `difference ${(100 * (calg - k.qExp) / k.qExp).toFixed(1)} %; Lerch & Bogue report +3.1 to -8.3 % for these clinkers`);
});

// T4 Powers' model worked results (Bentz et al. 2009, NEW-BENTZ-2009)
function powers(wc, alpha, lsFrac) {
  const ls = lsFrac || 0;
  return C.compute({
    cement: { mode: "phases", phases: { C3S: 60, C2S: 15, C3A: 8, C4AF: 9, sulfate: 5, limestone: 0, freeCaO: 0, periclase: 0 } },
    batch: { cementKg: 1 - ls, waterKg: wc }, // wc here = water / (cement + limestone)
    scms: ls ? [{ type: "limestone", massKg: ls }] : [], limestoneReactivity: 0,
    hydration: { mode: "alpha", alpha: alpha }, curing: "saturated"
  }).powers;
}
let pw = powers(0.356, 1);
check("T4a", "Saturated curing, w/c 0.356, α=1: total capillary porosity (fraction)", pw.capillaryWater + pw.chemicalShrinkage, 0, 0.002, "NEW-BENTZ-2009: zero porosity below about w/c 0.356");
check("T4b", "w/c giving α_max = 1 under sealed curing", 1.32 * (1 / 3.15), 0.42, 0.002, "NEW-BENTZ-2009: w/c about 0.42 just sufficient (sealed)");
pw = powers(0.42, 1);
check("T4c", "Sealed curing, w/c 0.42, α=1: capillary porosity (%)", 100 * pw.capillaryPorositySealed, 8.7, 0.2, "NEW-BENTZ-2009: about 8.7 % empty porosity");
check("T4d", "α_max sealed at w/c 0.42", pw.alphaMaxSealed, 1.0, 0.005, "NEW-BENTZ-2009");
[[0.05, 0.338], [0.10, 0.32], [0.15, 0.303], [0.20, 0.285], [0.25, 0.267]].forEach(([mlf, want]) => {
  // find w/cm where final (α=1) saturated capillary porosity reaches zero
  let lo = 0.2, hi = 0.5;
  for (let i = 0; i < 60; i++) { const mid = (lo + hi) / 2; const q = powers(mid, 1, mlf); (q.capillaryWater + q.chemicalShrinkage > 0 ? hi = mid : lo = mid); }
  check(`T4e-${mlf * 100}`, `w/cm for zero porosity, ${mlf * 100} % limestone filler (saturated)`, (lo + hi) / 2, want, 0.002, "NEW-BENTZ-2009 Fig. 2 text");
});

// T5 CH plausibility vs Huang & Feldman 1985 (R1882): plain paste, w/(c+sf) 0.45, 180 d -> about 16.2 % Ca(OH)2
const hf = { CaO: 63.07, SiO2: 21.16, Al2O3: 5.87, Fe2O3: 2.21, SO3: 3.29, MgO: 1.56, freeCaO: 0, CO2: 0 };
let r5 = C.compute({ cement: { mode: "oxides", oxides: hf, sulfateForm: "gypsum" }, batch: { cementKg: 1, waterKg: 0.45 }, scms: [],
  hydration: { mode: "age", ageDays: 180 }, curing: "saturated" });
note("T5a", "CH % of cement, plain paste w/c 0.45, 180 d (degree from Tennis & Jennings Avrami)", 100 * r5.CH.perKgBinder, 16.2, "R1882 text (Fig. 2)",
     `plausibility only: overall degree ${r5.degree.overall.toFixed(3)}; measured by DSC on paste, basis not identical`);
let r5b = C.compute({ cement: { mode: "oxides", oxides: hf }, batch: { cementKg: 0.7, waterKg: 0.45 },
  scms: [{ type: "silicaFume", massKg: 0.3, degree: 0.5 }], hydration: { mode: "age", ageDays: 14 }, curing: "saturated" });
note("T5b", "30 % silica fume, w/(c+sf) 0.45, 14 d, assumed SF degree 0.5: CH remaining (% of binder)", 100 * r5b.CH.perKgBinder, 0, "R1882 text: CH levels of zero at 14 days for P30",
     "plausibility only: CH-exhaustion warning " + (r5b.warnings.some(w => w.startsWith("CH runs out")) ? "triggered" : "not triggered"));

// report
const failed = results.filter(r => r.pass === false);
console.log(JSON.stringify({ total: results.length, checked: results.filter(r => r.pass !== null).length, passed: results.filter(r => r.pass).length, failed: failed.length, results }, null, 1));
process.exit(failed.length ? 1 : 0);
