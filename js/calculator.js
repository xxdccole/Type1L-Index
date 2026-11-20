/* Cement & Concrete Index — batch reaction calculator (client-side, no server).
 * Estimates only. Not a substitute for testing or thermodynamic modelling (e.g. GEMS + Cemdata18).
 * Every constant below carries the source it came from: an index record (R…) or a NEW-* source
 * listed in data/reactions.json. "derived" = computed from sourced numbers + CIAAW atomic weights.
 * Works in a browser (attaches to the form on calculator/) and in Node (module.exports.compute).
 */
(function (root) {
  "use strict";
  var AW = { H: 1.008, C: 12.011, O: 15.999, Na: 22.99, Mg: 24.305, Al: 26.982, Si: 28.085, S: 32.06, K: 39.098, Ca: 40.078, Fe: 55.845 }; // CIAAW
  var OX = {
    C: AW.Ca + AW.O, S: AW.Si + 2 * AW.O, A: 2 * AW.Al + 3 * AW.O, F: 2 * AW.Fe + 3 * AW.O,
    s: AW.S + 3 * AW.O, H: 2 * AW.H + AW.O, c: AW.C + 2 * AW.O, M: AW.Mg + AW.O
  };
  function mm(f) { var t = 0; for (var k in f) t += f[k] * OX[k]; return t; }
  // Phases: oxide formula, molar volume cm3/mol and its source.
  var P = {
    C3S: { f: { C: 3, S: 1 }, V: 71.129, src: "NEW-BENTZ-2005" },
    C2S: { f: { C: 2, S: 1 }, V: 52.513, src: "NEW-BENTZ-2005" },
    C3A: { f: { C: 3, A: 1 }, V: 88.94, src: "NEW-BENTZ-2005" },
    C4AF: { f: { C: 4, A: 1, F: 1 }, V: 130.29, src: "NEW-BENTZ-2005" },
    gypsum: { f: { C: 1, s: 1, H: 2 }, V: 74.21, src: "NEW-BENTZ-2005" },
    hemihydrate: { f: { C: 1, s: 1, H: 0.5 }, V: 52.973, src: "NEW-BENTZ-2005" },
    anhydrite: { f: { C: 1, s: 1 }, V: 52.16, src: "NEW-BENTZ-2005" },
    CH: { f: { C: 1, H: 1 }, V: 33.1, src: "NEW-BENTZ-2005" },
    CSH: { f: { C: 1.7, S: 1, H: 4 }, V: 108.0, src: "NEW-BENTZ-2005" },
    AFt: { f: { C: 6, A: 1, s: 3, H: 32 }, V: 735.01, src: "NEW-BENTZ-2005" },
    AFm: { f: { C: 4, A: 1, s: 1, H: 12 }, V: 312.82, src: "NEW-BENTZ-2005" },
    C4AH13: { f: { C: 4, A: 1, H: 13 }, V: 274, src: "R334" },
    C3AH6: { f: { C: 3, A: 1, H: 6 }, V: 150.12, src: "NEW-BENTZ-2005" },
    C3AFH6: { f: { C: 3, A: 0.5, F: 0.5, H: 6 }, V: null, rho: 2.67, src: "R3883" },
    FH3: { f: { F: 1, H: 3 }, V: 69.803, src: "NEW-BENTZ-2005" },
    Mc: { f: { C: 4, A: 1, c: 1, H: 11 }, V: 261.91, src: "NEW-BENTZ-2005" },
    calcite: { f: { C: 1, c: 1 }, V: 36.93, src: "NEW-BENTZ-2005" },
    lime: { f: { C: 1 }, V: 17, src: "R334" },
    periclase: { f: { M: 1 }, V: null, src: null },
    brucite: { f: { M: 1, H: 1 }, V: null, src: null },
    pCSH: { f: { C: 1.1, S: 1, H: 3.9 }, V: 101.81, src: "NEW-BENTZ-2005" },
    strat: { f: { C: 2, A: 1, S: 1, H: 8 }, V: 215.63, src: "NEW-BENTZ-2005" },
    water: { f: { H: 1 }, V: 18.068, src: "NEW-BENTZ-2005" }
  };
  for (var k in P) { P[k].M = mm(P[k].f); if (P[k].V == null && P[k].rho) P[k].V = P[k].M / P[k].rho; }

  // Heats of complete hydration, cal/g (Lerch & Bogue 1934, R210). 1 cal = 4.184 J.
  var LB = { C3S: 120, C2S: 62, C3A: 207, C4AF: 100, MgO: 203, CaO: 278.6, SO3_sulfoaluminate: 149 };
  var CAL = 4.184;
  // Avrami constants per phase (Tennis & Jennings 2000, Table 2, R3883): alpha = 1 - exp(-a (t-b)^c), t in days.
  var AVRAMI = { C3S: [0.25, 0.90, 0.70], C2S: [0.46, 0, 0.12], C3A: [0.28, 0.90, 0.77], C4AF: [0.26, 0.90, 0.55] };
  // Powers' model parameters as used by Bentz et al. 2009 after Jensen & Hansen (NEW-BENTZ-2009).
  var POWERS = { rhoW: 1.0, rhoC: 3.15, cs: 0.20, cw: 1.32, gw: 0.60, gs: 1.52, nonEvap: 0.23 };

  // SCM defaults. composition in mass %; rho in g/cm3; heat J/g reacted (null = unknown, excluded).
  var SCM_DEFAULTS = {
    silicaFume: { label: "Silica fume", comp: { SiO2: 95.17, Al2O3: 0.21, Fe2O3: 0.13, CaO: 0.23, MgO: 0.15, SO3: 0.12 }, compSrc: "R1882 Table I", rho: 2.22, rhoSrc: "NEW-BENTZ-2005 (SG of pozzolan)", heat: 780, heatSrc: "NEW-BENTZ-2005 (780 J/g silica fume)", model: "pozzolan" },
    flyAshF: { label: "Fly ash, Class F", comp: { SiO2: 55.6, Al2O3: 22.7, Fe2O3: 4.3, CaO: 13.3, MgO: 2.4, SO3: 0.16 }, compSrc: "R1882 Table I fly ash (the paper does not state its class; SiO2+Al2O3+Fe2O3 = 82.6 %, CaO 13.3 %)", rho: null, rhoSrc: "no sourced default — enter a measured density", heat: null, heatSrc: "no sourced value — enter one or heat is excluded", model: "pozzolan" },
    flyAshC: { label: "Fly ash, Class C", comp: null, compSrc: "no sourced default — enter the oxide analysis", rho: null, rhoSrc: "no sourced default", heat: null, heatSrc: "no sourced value", model: "pozzolan" },
    slag: { label: "Slag (GGBFS)", comp: { SiO2: 39.2, Al2O3: 7.9, Fe2O3: 0, CaO: 36.25, MgO: 10.3, SO3: 3.1 }, compSrc: "NEW-BENTZ-2005 Table 2, slag 1", rho: 2.87, rhoSrc: "NEW-BENTZ-2005 slagchar.dat example (slag 2)", heat: 800, heatSrc: "NEW-BENTZ-2005 (800 J/g); Schindler & Folliard 461 J/g Grade 100 via NEW-LEON-CHEN-2021", model: "slag", slagCaSi: 1.25, slagHSi: 86 / 17, slagRhoProduct: 2.35, slagSrc: "NEW-BENTZ-2005 Table 2 slag 1 product C21.25S17M6.5A2sH86; product SG 2.35 from slagchar.dat (slag 2)" },
    metakaolin: { label: "Metakaolin / calcined clay", comp: { SiO2: 100 * 2 * OX.S / (2 * OX.S + OX.A), Al2O3: 100 * OX.A / (2 * OX.S + OX.A), Fe2O3: 0, CaO: 0, MgO: 0, SO3: 0 }, compSrc: "derived: ideal metakaolin Al2Si2O7 (AS2)", rho: null, rhoSrc: "no sourced default", heat: null, heatSrc: "no sourced value", model: "pozzolan" },
    naturalPozzolan: { label: "Natural pozzolan", comp: null, compSrc: "no sourced default — enter the oxide analysis", rho: null, rhoSrc: "no sourced default", heat: null, heatSrc: "no sourced value", model: "pozzolan" },
    limestone: { label: "Limestone filler", comp: { CaCO3: 100 }, compSrc: "assumed pure calcite", rho: 2.71, rhoSrc: "NEW-BENTZ-2005 (CaCO3 SG 2.71)", heat: null, heatSrc: "monocarbonate heat of formation not available (Bentz leaves it 0)", model: "limestone" }
  };

  function num(x, d) { var v = Number(x); return (x === "" || x == null || isNaN(v)) ? d : v; }

  // ---- Bogue per ASTM C150 as given in R880 Eqs. (5)-(8); optional free-lime subtraction (as in R210 Table 1).
  function bogue(o, opts) {
    opts = opts || {};
    var CaO = num(o.CaO, 0) - (opts.subtractFreeLime ? num(o.freeCaO, 0) : 0);
    var S = num(o.SiO2, 0), A = num(o.Al2O3, 0), F = num(o.Fe2O3, 0), s = num(o.SO3, 0), c = num(o.CO2, 0);
    var C3S = 4.071 * CaO - 7.600 * S - 6.718 * A - 1.430 * F - 2.852 * s - 5.188 * c;
    var C2S = 2.867 * S - 0.7544 * C3S;
    var C3A = 2.650 * A - 1.692 * F;
    var C4AF = 3.043 * F;
    var w = [];
    if (F > 0 && A / F < 0.64) w.push("Al2O3/Fe2O3 is below 0.64: the standard Bogue form is not valid and the C4AF+C2F solid-solution form is not implemented. Treat phases as unreliable.");
    if (C3S < 0) { w.push("Bogue C3S came out negative; set to 0 (check the analysis)."); C3S = 0; C2S = 2.867 * S; }
    if (C2S < 0) { w.push("Bogue C2S came out negative; set to 0 (check the analysis)."); C2S = 0; }
    if (C3A < 0) { w.push("Bogue C3A came out negative; set to 0."); C3A = 0; }
    return { C3S: C3S, C2S: C2S, C3A: C3A, C4AF: C4AF, warnings: w };
  }

  function avrami(phase, t) {
    var p = AVRAMI[phase]; if (t <= p[1]) return 0;
    return 1 - Math.exp(-p[0] * Math.pow(t - p[1], p[2]));
  }

  // ---- main calculation. All masses kg per batch; moles in kmol (kg / (g/mol)).
  function compute(inp) {
    var W = [], notes = [];
    var cem = inp.cement || {};
    var cKg = num((inp.batch || {}).cementKg, 0);
    var scms = (inp.scms || []).filter(function (x) { return num(x.massKg, 0) > 0; });
    var scmKg = scms.reduce(function (a, x) { return a + num(x.massKg, 0); }, 0);
    var binder = cKg + scmKg;
    var waterKg = (inp.batch.waterKg != null && inp.batch.waterKg !== "") ? num(inp.batch.waterKg, 0) : num(inp.batch.wcm, 0) * binder;
    if (binder <= 0) throw new Error("Enter a cement and/or SCM mass.");

    // 1. cement phase composition, mass %
    var ph = {}, bg = null, sulfForm = cem.sulfateForm || "gypsum";
    var sulfM = { gypsum: P.gypsum.M, hemihydrate: P.hemihydrate.M, anhydrite: P.anhydrite.M }[sulfForm];
    if ((cem.mode || "oxides") === "oxides") {
      var o = cem.oxides || {};
      bg = bogue(o, { subtractFreeLime: cem.subtractFreeLime !== false });
      W = W.concat(bg.warnings);
      ph.C3S = bg.C3S; ph.C2S = bg.C2S; ph.C3A = bg.C3A; ph.C4AF = bg.C4AF;
      ph.sulfate = num(o.SO3, 0) * sulfM / OX.s;
      ph.limestone = num(o.CO2, 0) * P.calcite.M / OX.c;
      ph.freeCaO = num(o.freeCaO, 0);
      ph.periclase = num(cem.periclasePct, 0);
      ph.SO3 = num(o.SO3, 0);
    } else {
      var q = cem.phases || {};
      ph.C3S = num(q.C3S, 0); ph.C2S = num(q.C2S, 0); ph.C3A = num(q.C3A, 0); ph.C4AF = num(q.C4AF, 0);
      ph.sulfate = num(q.sulfate, 0); ph.limestone = num(q.limestone, 0); ph.freeCaO = num(q.freeCaO, 0); ph.periclase = num(q.periclase, 0);
      ph.SO3 = ph.sulfate * OX.s / sulfM;
    }
    var assigned = ph.C3S + ph.C2S + ph.C3A + ph.C4AF + ph.sulfate + ph.limestone + ph.freeCaO + ph.periclase;
    ph.other = 100 - assigned;
    if (ph.other < -0.5) W.push("Assigned phases add up to " + assigned.toFixed(1) + " % (> 100 %). Check the inputs.");

    // 2. degree of hydration
    var hyd = inp.hydration || {}, a = {};
    if (hyd.mode === "age") {
      var t = num(hyd.ageDays, 28);
      ["C3S", "C2S", "C3A", "C4AF"].forEach(function (k) { a[k] = avrami(k, t); });
      notes.push("Degree of hydration from age uses Tennis & Jennings (R3883) Avrami constants for one Type I cement at their test conditions; it ignores temperature, fineness, w/c and SCM effects.");
    } else {
      var al = Math.max(0, Math.min(1, num(hyd.alpha, 0.7)));
      a = { C3S: al, C2S: al, C3A: al, C4AF: al };
    }
    var clinkerMass = ph.C3S + ph.C2S + ph.C3A + ph.C4AF;
    var aBar = clinkerMass > 0 ? (a.C3S * ph.C3S + a.C2S * ph.C2S + a.C3A * ph.C3A + a.C4AF * ph.C4AF) / clinkerMass : 0;

    // masses kg in batch
    var m = {}; ["C3S", "C2S", "C3A", "C4AF", "sulfate", "limestone", "freeCaO", "periclase", "other"].forEach(function (k) { m[k] = cKg * ph[k] / 100; });
    var n = {}; // reacted kmol
    n.C3S = a.C3S * m.C3S / P.C3S.M; n.C2S = a.C2S * m.C2S / P.C2S.M; n.C3A = a.C3A * m.C3A / P.C3A.M; n.C4AF = a.C4AF * m.C4AF / P.C4AF.M;
    var prod = { CSH: 0, CH: 0, AFt: 0, AFm: 0, C4AH13: 0, C3AH6: 0, C3AFH6: 0, FH3: 0, Mc: 0, pCSH: 0, strat: 0, slagProduct: 0, brucite: 0 };
    var used = { water: 0 }; // kmol water consumed
    var vol = { reactants: 0, products: 0 }; // cm3*1000 per kmol -> L when multiplied appropriately (kmol * cm3/mol = L)

    // 3. silicates (editable C-S-H stoichiometry; default C1.7SH4)
    var x = num(cem.cshCaSi, 1.7), y = num(cem.cshHSi, 4.0), rhoCSH = num(cem.cshDensity, 2.11);
    var MCSH = x * OX.C + OX.S + y * OX.H, VCSH = (x === 1.7 && y === 4.0 && rhoCSH === 2.11) ? P.CSH.V : MCSH / rhoCSH;
    prod.CSH = n.C3S + n.C2S;
    prod.CH += (3 - x) * n.C3S + (2 - x) * n.C2S;
    used.water += (y + 3 - x) * n.C3S + (y + 2 - x) * n.C2S;
    if (x > 2) W.push("C-S-H Ca/Si above 2 makes C2S consume CH; check the C-S-H inputs.");

    // 4. sulfate: convert hemihydrate/anhydrite to gypsum equivalents (water counted, heat ignored per R210)
    var sKmol = m.sulfate / sulfM, sAvail = sKmol;
    if (sulfForm === "hemihydrate") used.water += 1.5 * sKmol; // RX10
    if (sulfForm === "anhydrite") used.water += 2 * sKmol;     // RX11
    // carbonate pool (cement limestone + limestone filler), reactive share only
    var lsFillerKg = scms.filter(function (s) { return s.type === "limestone"; }).reduce(function (q, s) { return q + num(s.massKg, 0); }, 0);
    var lsReact = Math.max(0, Math.min(1, num(inp.limestoneReactivity, 0)));
    var ccKmol = lsReact * (m.limestone + lsFillerKg) / P.calcite.M, ccUsed = 0;
    // aluminates
    var a3 = n.C3A, f4 = n.C4AF;
    var e1 = Math.min(a3, sAvail / 3); prod.AFt += e1; sAvail -= 3 * e1; a3 -= e1; used.water += 26 * e1;          // RX03
    var e2 = Math.min(f4, sAvail / 3); prod.AFt += e2; sAvail -= 3 * e2; f4 -= e2; prod.CH += e2; prod.FH3 += e2; used.water += 30 * e2; // RX07
    var mc = Math.min(a3, ccKmol); prod.Mc += mc; a3 -= mc; ccUsed += mc; used.water += 11 * mc;                    // RX15
    var conv1 = Math.min(a3 / 2, prod.AFt); prod.AFm += 3 * conv1; prod.AFt -= conv1; a3 -= 2 * conv1; used.water += 4 * conv1; // RX04
    var conv2 = Math.min(f4 / 2, prod.AFt); prod.AFm += 3 * conv2; prod.AFt -= conv2; f4 -= 2 * conv2; prod.CH += 2 * conv2; prod.FH3 += 2 * conv2; used.water += 12 * conv2; // RX08
    // leftovers without sulfate: C3A + CH + 12H -> C4AH13 (RX06), else C3A + 6H -> C3AH6 (RX05); C4AF + 2CH + 10H -> 2C3(A,F)H6 (RX09)
    var chNow = prod.CH;
    var c4ah13 = Math.min(a3, Math.max(0, chNow)); prod.C4AH13 += c4ah13; prod.CH -= c4ah13; used.water += 12 * c4ah13; a3 -= c4ah13;
    prod.C3AH6 += a3; used.water += 6 * a3; a3 = 0;
    var hg = Math.min(f4, Math.max(0, prod.CH) / 2); prod.C3AFH6 += 2 * hg; prod.CH -= 2 * hg; used.water += 10 * hg; f4 -= hg;
    if (f4 > 1e-12) { W.push("Not enough CH for all reacted C4AF to form hydrogarnet; the remainder is left unreacted."); n.C4AF -= f4; }
    // 5. free lime and periclase (assumed to react to the same overall degree; periclase is usually much slower)
    var nLime = aBar * m.freeCaO / P.lime.M; prod.CH += nLime; used.water += nLime;                                        // RX12
    var nPer = aBar * m.periclase / P.periclase.M; prod.brucite += nPer; used.water += nPer;                                  // RX13
    if (m.periclase > 0) W.push("Periclase is assumed to hydrate to the same degree as the clinker; dead-burnt periclase is much slower. Its volume change is excluded (no sourced brucite molar volume).");
    var chCement = prod.CH;

    // 6. SCMs
    var scmOut = [], chDemandTotal = 0, scmHeat = 0, scmVolR = 0, scmVolP = 0, scmWater = 0;
    var pending = [];
    scms.forEach(function (s) {
      if (s.type === "limestone") return;
      var d = SCM_DEFAULTS[s.type] || {};
      var comp = s.comp || d.comp;
      if (!comp) { W.push((d.label || s.type) + ": no oxide analysis entered; it is treated as inert."); scmOut.push({ type: s.type, label: d.label, reactedKg: 0, inert: true }); return; }
      var r = num(s.massKg, 0) * Math.max(0, Math.min(1, num(s.degree, 0)));
      var nS = r * num(comp.SiO2, 0) / 100 / OX.S, nA = r * num(comp.Al2O3, 0) / 100 / OX.A, nC = r * num(comp.CaO, 0) / 100 / OX.C;
      var rec = { type: s.type, label: d.label, reactedKg: r, nS: nS, nA: nA, nC: nC };
      if ((s.model || d.model) === "slag") {
        var p = num(s.slagCaSi, d.slagCaSi), hq = num(s.slagHSi, d.slagHSi);
        rec.chDemand = p * nS - nC; // + = consumes CH
        rec.waterBound = hq * nS - rec.chDemand; // free water consumed (RX22 form)
        rec.model = "slag";
        rec.rhoProduct = num(s.slagRhoProduct, d.slagRhoProduct);
      } else {
        var alp = s.alProduct || "stratlingite";
        var caNeed, hBound, sLeft = nS;
        if (alp === "afm") { caNeed = 4 * nA; hBound = 13 * nA; rec.C4AH13 = nA; }
        else { var st = Math.min(nA, nS); caNeed = 2 * st; hBound = 8 * st; sLeft -= st; rec.strat = st; if (nA > st) { caNeed += 4 * (nA - st); hBound += 13 * (nA - st); rec.C4AH13 = nA - st; } }
        caNeed += 1.1 * sLeft; hBound += 3.9 * sLeft; rec.pCSH = sLeft;
        rec.chDemand = caNeed - nC;
        rec.waterBound = hBound - rec.chDemand;
        rec.model = "pozzolan";
      }
      rec.heatJg = (s.heatJg != null && s.heatJg !== "") ? num(s.heatJg, null) : d.heat;
      rec.rho = num(s.rho, d.rho);
      pending.push(rec);
      chDemandTotal += Math.max(0, rec.chDemand);
    });
    // CH limit: scale pozzolanic/slag reactions if CH runs out
    var chAvail = Math.max(0, prod.CH) + pending.reduce(function (q, r) { return q + Math.max(0, -r.chDemand); }, 0);
    var scale = chDemandTotal > chAvail && chDemandTotal > 0 ? chAvail / chDemandTotal : 1;
    if (scale < 1) W.push("CH runs out: the SCMs would need " + (chDemandTotal * P.CH.M).toFixed(1) + " kg CH but only " + (chAvail * P.CH.M).toFixed(1) + " kg is available. Reaction of CH-consuming SCMs is cut to " + (100 * scale).toFixed(0) + " % of the entered degree.");
    pending.forEach(function (r) {
      var k = r.chDemand > 0 ? scale : 1;
      r.reactedKg *= k; ["nS", "nA", "nC", "chDemand", "waterBound", "strat", "pCSH", "C4AH13"].forEach(function (f) { if (r[f] != null) r[f] *= k; });
      prod.CH -= r.chDemand;
      used.water += r.waterBound;
      if (r.model === "slag") {
        var pm = r.reactedKg + r.chDemand * P.CH.M + r.waterBound * OX.H;
        r.productKg = pm; prod.slagProduct += pm;
        if (r.rho && r.rhoProduct) { scmVolR += r.reactedKg / r.rho; scmVolP += pm / r.rhoProduct; } else r.volUnknown = true;
      } else {
        prod.strat += r.strat || 0; prod.pCSH += r.pCSH || 0; prod.C4AH13 += r.C4AH13 || 0;
        if (r.rho) { scmVolR += r.reactedKg / r.rho; scmVolP += ((r.strat || 0) * P.strat.V + (r.pCSH || 0) * P.pCSH.V + (r.C4AH13 || 0) * P.C4AH13.V); } else r.volUnknown = true;
      }
      if (r.volUnknown) W.push((r.label || r.type) + ": no density entered, so its volume change is left out of the chemical shrinkage.");
      if (r.heatJg == null) W.push((r.label || r.type) + ": no heat of reaction entered; its heat is excluded from Q.");
      else scmHeat += r.reactedKg * r.heatJg; // kg * J/g = kJ
      scmOut.push(r);
    });
    if (prod.CH < -1e-9) W.push("CH balance is negative; check inputs.");

    // 7. heat (Lerch & Bogue phase heats, R210)
    var J = function (calg) { return calg * CAL; };
    var qInf = J(LB.C3S) * m.C3S + J(LB.C2S) * m.C2S + J(LB.C3A) * m.C3A + J(LB.C4AF) * m.C4AF + J(LB.MgO) * m.periclase + J(LB.CaO) * m.freeCaO + J(LB.SO3_sulfoaluminate) * cKg * ph.SO3 / 100; // kJ (kg * J/g)
    var so3Combined = (sKmol - sAvail) * OX.s; // kg SO3 now in AFt/AFm
    var qNow = J(LB.C3S) * a.C3S * m.C3S + J(LB.C2S) * a.C2S * m.C2S + J(LB.C3A) * a.C3A * m.C3A + J(LB.C4AF) * a.C4AF * m.C4AF + J(LB.MgO) * aBar * m.periclase + J(LB.CaO) * aBar * m.freeCaO + J(LB.SO3_sulfoaluminate) * so3Combined;
    var scmHeatInf = 0;
    scms.forEach(function (s) { var d = SCM_DEFAULTS[s.type] || {}; var h = (s.heatJg != null && s.heatJg !== "") ? num(s.heatJg, null) : d.heat; if (h != null && s.type !== "limestone") scmHeatInf += num(s.massKg, 0) * h; });

    // 8. masses of products (kg)
    var out = {};
    out.CSH = prod.CSH * MCSH; out.CH = Math.max(0, prod.CH) * P.CH.M; out.AFt = prod.AFt * P.AFt.M; out.AFm = prod.AFm * P.AFm.M;
    out.C4AH13 = prod.C4AH13 * P.C4AH13.M; out.C3AH6 = prod.C3AH6 * P.C3AH6.M; out.C3AFH6 = prod.C3AFH6 * P.C3AFH6.M; out.FH3 = prod.FH3 * P.FH3.M;
    out.monocarbonate = prod.Mc * P.Mc.M; out.pozzCSH = prod.pCSH * P.pCSH.M; out.stratlingite = prod.strat * P.strat.M; out.slagProduct = prod.slagProduct; out.brucite = prod.brucite * P.brucite.M;
    var remaining = { C3S: m.C3S - n.C3S * P.C3S.M, C2S: m.C2S - n.C2S * P.C2S.M, C3A: m.C3A - n.C3A * P.C3A.M, C4AF: m.C4AF - n.C4AF * P.C4AF.M,
      gypsumEq: sAvail * P.gypsum.M, calcite: (m.limestone + lsFillerKg) - ccUsed * P.calcite.M };
    var boundWater = used.water * OX.H;

    // 9. chemical shrinkage (stoichiometric, condensed phases; L per batch since kmol*cm3/mol = L)
    // Water that went into phases without a sourced molar volume (brucite, SCMs without density) is left out on both sides.
    var waterNoVol = nPer + pending.reduce(function (q, r) { return q + (r.volUnknown ? r.waterBound : 0); }, 0);
    var chNoVol = pending.reduce(function (q, r) { return q + (r.volUnknown ? r.chDemand : 0); }, 0);
    var Vr = n.C3S * P.C3S.V + n.C2S * P.C2S.V + n.C3A * P.C3A.V + n.C4AF * P.C4AF.V + (used.water - waterNoVol) * P.water.V
      + ccUsed * P.calcite.V + nLime * P.lime.V + scmVolR;
    var Vp = prod.CSH * VCSH + prod.AFt * P.AFt.V + prod.AFm * P.AFm.V + prod.C4AH13 * P.C4AH13.V + prod.C3AH6 * P.C3AH6.V + prod.C3AFH6 * P.C3AFH6.V
      + prod.FH3 * P.FH3.V + prod.Mc * P.Mc.V + scmVolP + (Math.max(0, prod.CH) + chNoVol) * P.CH.V;
    if (sulfForm === "gypsum") Vr += (sKmol - sAvail) * P.gypsum.V;             // reacted gypsum; unreacted gypsum cancels
    else { Vr += sKmol * P[sulfForm].V; Vp += sAvail * P.gypsum.V; }             // all converts to gypsum first (RX10/RX11)
    // initial (unconsumed) gypsum stays; reacted calcium sulfate already counted. Net CH volume = final CH (CH consumed internally cancels).
    var chemShrinkL = Vr - Vp;

    // 10. Powers' model (cement-only; SCMs and limestone treated as inert filler — Bentz et al. 2009 approach)
    var pc = Math.max(1e-9, cKg - m.limestone);
    var wc = waterKg / pc;
    var fillerVol = m.limestone / (P.calcite.M / P.calcite.V); // kg / (g/cm3) = L
    scms.forEach(function (s) { var d = SCM_DEFAULTS[s.type] || {}; var rho = num(s.rho, d.rho); if (rho) fillerVol += num(s.massKg, 0) / rho; else W.push((d.label || s.type) + ": no density, so it is left out of the Powers filler volume."); });
    var pasteVol = pc / POWERS.rhoC + waterKg / POWERS.rhoW;
    var VLF = fillerVol / (fillerVol + pasteVol);
    var p = wc / (wc + POWERS.rhoW / POWERS.rhoC);
    var f1 = 1 - VLF, al2 = aBar;
    var pw = {
      wcEffective: wc, p: p, fillerVolumeFraction: VLF,
      cement: f1 * (1 - p) * (1 - al2), gelSolids: f1 * POWERS.gs * (1 - p) * al2, gelWater: f1 * POWERS.gw * (1 - p) * al2,
      capillaryWater: f1 * (p - POWERS.cw * (1 - p) * al2), chemicalShrinkage: f1 * POWERS.cs * (1 - p) * al2
    };
    pw.capillaryPorositySealed = pw.capillaryWater + pw.chemicalShrinkage;
    pw.capillaryPorositySaturated = pw.capillaryWater + pw.chemicalShrinkage; // same pore volume; in saturated curing the shrinkage space is water-filled
    pw.gelPorosity = pw.gelWater;
    pw.alphaMaxSealed = Math.min(1, p / (POWERS.cw * (1 - p)));
    pw.alphaMaxSaturated = Math.min(1, p / ((POWERS.cw - POWERS.cs) * (1 - p)));
    pw.nonEvaporableWaterKg = POWERS.nonEvap * al2 * pc;
    var curing = inp.curing || "sealed";
    var amax = curing === "saturated" ? pw.alphaMaxSaturated : pw.alphaMaxSealed;
    if (al2 > amax + 1e-6) W.push("Degree of hydration " + al2.toFixed(2) + " exceeds the Powers limit of " + amax.toFixed(2) + " for " + curing + " curing at effective w/c " + wc.toFixed(3) + ".");
    if (pw.capillaryWater < 0) W.push("Powers' model gives negative capillary water: not enough water for this degree of hydration under sealed conditions.");
    if (boundWater > waterKg) W.push("Stoichiometric water demand (" + boundWater.toFixed(1) + " kg) exceeds the batch water (" + waterKg.toFixed(1) + " kg).");

    return {
      inputs: { cementKg: cKg, scmKg: scmKg, binderKg: binder, waterKg: waterKg, wcm: waterKg / binder },
      bogue: bg, phasesPct: ph, phasesKg: m, degree: { C3S: a.C3S, C2S: a.C2S, C3A: a.C3A, C4AF: a.C4AF, overall: aBar },
      products: out, remaining: remaining,
      water: { boundKg: boundWater, freeKg: waterKg - boundWater, powersNonEvaporableKg: pw.nonEvaporableWaterKg },
      CH: { fromCementKg: chCement * P.CH.M, consumedBySCMKg: pending.reduce(function (q, r) { return q + r.chDemand; }, 0) * P.CH.M, finalKg: out.CH, perKgBinder: out.CH / binder },
      heat: { QinfCementKJ: qInf, QinfSCMKJ: scmHeatInf, QnowCementKJ: qNow, QnowSCMKJ: scmHeat,
        QinfPerKgBinder: (qInf + scmHeatInf) / binder, QnowPerKgBinder: (qNow + scmHeat) / binder, QinfPerKgCement: cKg > 0 ? qInf / cKg : null },
      chemicalShrinkage: { litres: chemShrinkL, mlPerGBinder: chemShrinkL / binder },
      powers: pw, scm: scmOut, warnings: W, notes: notes
    };
  }

  var api = { compute: compute, bogue: bogue, avrami: avrami, constants: { P: P, LB: LB, AVRAMI: AVRAMI, POWERS: POWERS, SCM_DEFAULTS: SCM_DEFAULTS, OX: OX } };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  root.CCICalc = api;

  // ---------------------------------------------------------------- browser UI
  if (typeof document === "undefined") return;
  function $(id) { return document.getElementById(id); }
  function v(id) { var el = $(id); return el ? el.value : ""; }
  function f(x, d) { return (x == null || isNaN(x)) ? "—" : Number(x).toFixed(d == null ? 1 : d); }
  function row(label, val, unit, note) { return "<tr><th scope=\"row\">" + label + "</th><td class=\"num\">" + val + "</td><td>" + (unit || "") + "</td><td>" + (note || "") + "</td></tr>"; }
  function readSCMs() {
    var list = [];
    document.querySelectorAll("[data-scm]").forEach(function (box) {
      var t = box.getAttribute("data-scm");
      var g = function (n) { var el = box.querySelector("[name=" + n + "]"); return el ? el.value : ""; };
      var s = { type: t, massKg: g("mass"), degree: g("degree"), rho: g("rho"), heatJg: g("heat") };
      if (t !== "limestone") {
        var comp = {}, any = false;
        ["SiO2", "Al2O3", "Fe2O3", "CaO", "MgO", "SO3"].forEach(function (o) { var x = g(o); if (x !== "") { comp[o] = x; any = true; } });
        s.comp = any ? comp : null;
        s.alProduct = g("alProduct") || "stratlingite";
        if (t === "slag") { s.slagCaSi = g("slagCaSi"); s.slagHSi = g("slagHSi"); s.slagRhoProduct = g("slagRhoProduct"); s.model = "slag"; }
      }
      list.push(s);
    });
    return list;
  }
  function run(ev) {
    if (ev) ev.preventDefault();
    var mode = document.querySelector("input[name=cmode]:checked").value;
    var inp = {
      cement: { mode: mode, sulfateForm: v("sulfForm"), subtractFreeLime: $("subFL").checked, periclasePct: v("periclase"),
        cshCaSi: v("cshCaSi"), cshHSi: v("cshHSi"), cshDensity: v("cshRho"),
        oxides: { CaO: v("CaO"), SiO2: v("SiO2"), Al2O3: v("Al2O3"), Fe2O3: v("Fe2O3"), SO3: v("SO3"), MgO: v("MgO"), freeCaO: v("fCaO"), Na2O: v("Na2O"), K2O: v("K2O"), CO2: v("CO2") },
        phases: { C3S: v("pC3S"), C2S: v("pC2S"), C3A: v("pC3A"), C4AF: v("pC4AF"), sulfate: v("pSulf"), limestone: v("pLs"), freeCaO: v("pFCaO"), periclase: v("pMgO") } },
      scms: readSCMs(), limestoneReactivity: v("lsReact"),
      batch: { cementKg: v("cKg"), waterKg: $("wmode").value === "kg" ? v("wKg") : "", wcm: v("wcm") },
      hydration: { mode: document.querySelector("input[name=hmode]:checked").value, alpha: v("alpha"), ageDays: v("age") },
      curing: v("curing")
    };
    var r, out = $("results");
    try { r = compute(inp); } catch (e) { out.innerHTML = "<p class=\"notice\">" + e.message + "</p>"; return; }
    var B = r.inputs.binderKg, h = "";
    h += "<h2 id=\"res-summary\">Results (estimates)</h2>";
    if (r.warnings.length) h += "<div class=\"notice\" role=\"status\"><p><strong>Warnings</strong></p><ul>" + r.warnings.map(function (w) { return "<li>" + w + "</li>"; }).join("") + "</ul></div>";
    h += "<p class=\"meta\">Binder " + f(B) + " kg · water " + f(r.inputs.waterKg) + " kg · w/cm " + f(r.inputs.wcm, 3) + " · overall degree of hydration " + f(r.degree.overall, 3) + "</p>";
    h += "<h3>Cement phases</h3><div class=\"table-scroll\"><table><thead><tr><th>Phase</th><th>% of cement</th><th>kg in batch</th><th>Degree</th></tr></thead><tbody>";
    [["C3S", "C3S"], ["C2S", "C2S"], ["C3A", "C3A"], ["C4AF", "C4AF"]].forEach(function (k) { h += "<tr><th scope=\"row\">" + k[1] + "</th><td class=\"num\">" + f(r.phasesPct[k[0]], 2) + "</td><td class=\"num\">" + f(r.phasesKg[k[0]], 1) + "</td><td class=\"num\">" + f(r.degree[k[0]], 3) + "</td></tr>"; });
    [["sulfate", "Calcium sulfate (" + v("sulfForm") + ")"], ["limestone", "Limestone (CaCO3)"], ["freeCaO", "Free CaO"], ["periclase", "Periclase (MgO)"], ["other", "Other / unassigned"]].forEach(function (k) { h += "<tr><th scope=\"row\">" + k[1] + "</th><td class=\"num\">" + f(r.phasesPct[k[0]], 2) + "</td><td class=\"num\">" + f(r.phasesKg[k[0]], 1) + "</td><td></td></tr>"; });
    h += "</tbody></table></div>";
    h += "<h3>Products and water</h3><div class=\"table-scroll\"><table><thead><tr><th>Quantity</th><th>Value</th><th>Unit</th><th>Basis</th></tr></thead><tbody>";
    var p = r.products;
    h += row("C-S-H (cement)", f(p.CSH), "kg", "RX01–RX02") + row("Pozzolanic C-S-H (C1.1SH3.9)", f(p.pozzCSH), "kg", "RX17") + row("Slag hydration product", f(p.slagProduct), "kg", "RX22")
      + row("Strätlingite", f(p.stratlingite), "kg", "RX18") + row("Ettringite (AFt)", f(p.AFt), "kg", "RX03, RX07") + row("Monosulfate (AFm)", f(p.AFm), "kg", "RX04, RX08")
      + row("Monocarbonate", f(p.monocarbonate), "kg", "RX15") + row("C4AH13", f(p.C4AH13), "kg", "RX06, RX20") + row("Hydrogarnet C3AH6 / C3(A,F)H6", f(p.C3AH6 + p.C3AFH6), "kg", "RX05, RX09")
      + row("FH3", f(p.FH3), "kg", "RX07–RX08") + row("Brucite", f(p.brucite), "kg", "RX13")
      + row("CH from cement", f(r.CH.fromCementKg), "kg", "RX01–RX12") + row("CH consumed by SCMs", f(r.CH.consumedBySCMKg), "kg", "RX17–RX22") + row("CH remaining", f(r.CH.finalKg), "kg", f(100 * r.CH.perKgBinder, 1) + " % of binder")
      + row("Chemically bound water (stoichiometric)", f(r.water.boundKg), "kg", "saturated hydrates as written") + row("Free water remaining", f(r.water.freeKg), "kg", "")
      + row("Non-evaporable water, Powers (0.23 α c)", f(r.water.powersNonEvaporableKg), "kg", "comparison only");
    h += "</tbody></table></div>";
    h += "<h3>Heat</h3><div class=\"table-scroll\"><table><tbody>";
    h += row("Q∞ cement (Lerch & Bogue)", f(r.heat.QinfPerKgCement, 0), "kJ/kg cement", "R210") + row("Q∞ binder incl. SCMs with a heat value", f(r.heat.QinfPerKgBinder, 0), "kJ/kg binder", "")
      + row("Q at current degree", f(r.heat.QnowPerKgBinder, 0), "kJ/kg binder", "") + row("Q at current degree, batch", f((r.heat.QnowCementKJ + r.heat.QnowSCMKJ) / 1000, 1), "MJ", "")
      + row("Q∞, batch", f((r.heat.QinfCementKJ + r.heat.QinfSCMKJ) / 1000, 1), "MJ", "");
    h += "</tbody></table></div>";
    var w = r.powers;
    h += "<h3>Volumes</h3><div class=\"table-scroll\"><table><tbody>";
    h += row("Chemical shrinkage (stoichiometric)", f(r.chemicalShrinkage.litres, 2), "L per batch", f(r.chemicalShrinkage.mlPerGBinder * 1000 / 1000, 4) + " mL/g binder")
      + row("Powers: effective w/c (cement only)", f(w.wcEffective, 3), "", "SCMs and limestone as inert filler") + row("Powers: capillary porosity", f(100 * w.capillaryPorositySealed, 1), "% of paste volume", "capillary water + chemical shrinkage")
      + row("Powers: gel porosity (gel water)", f(100 * w.gelPorosity, 1), "% of paste volume", "") + row("Powers: gel solids", f(100 * w.gelSolids, 1), "% of paste volume", "")
      + row("Powers: unhydrated cement", f(100 * w.cement, 1), "% of paste volume", "") + row("Powers: filler (SCMs + limestone)", f(100 * w.fillerVolumeFraction, 1), "% of paste volume", "")
      + row("Powers: chemical shrinkage", f(100 * w.chemicalShrinkage, 1), "% of paste volume", "") + row("Powers α max, sealed / saturated", f(w.alphaMaxSealed, 3) + " / " + f(w.alphaMaxSaturated, 3), "", "");
    h += "</tbody></table></div>";
    if (r.notes.length) h += "<p class=\"evidence-note\">" + r.notes.join(" ") + "</p>";
    out.innerHTML = h;
  }
  function toggle() {
    var mode = document.querySelector("input[name=cmode]:checked").value;
    $("oxideBox").hidden = mode !== "oxides"; $("phaseBox").hidden = mode !== "phases";
    var hm = document.querySelector("input[name=hmode]:checked").value;
    $("alphaBox").hidden = hm !== "alpha"; $("ageBox").hidden = hm !== "age";
    $("wKgBox").hidden = $("wmode").value !== "kg"; $("wcmBox").hidden = $("wmode").value !== "wcm";
  }
  document.addEventListener("DOMContentLoaded", function () {
    var form = $("calc-form"); if (!form) return;
    // show the sourced defaults as placeholders; an empty field uses the default
    document.querySelectorAll("[data-scm]").forEach(function (box) {
      var d = SCM_DEFAULTS[box.getAttribute("data-scm")] || {};
      var set = function (n, val) { var el = box.querySelector("[name=" + n + "]"); if (el && val != null) el.placeholder = String(+Number(val).toFixed(3)); };
      set("rho", d.rho); set("heat", d.heat); set("slagCaSi", d.slagCaSi); set("slagHSi", d.slagHSi); set("slagRhoProduct", d.slagRhoProduct);
      if (d.comp) ["SiO2", "Al2O3", "Fe2O3", "CaO", "MgO", "SO3"].forEach(function (o) { set(o, d.comp[o]); });
      var src = box.querySelector(".scm-src"); if (src) src.textContent = "Defaults: composition " + d.compSrc + "; density " + d.rhoSrc + "; heat " + d.heatSrc + (d.slagSrc ? "; product " + d.slagSrc : "") + ".";
    });
    form.addEventListener("submit", run);
    form.addEventListener("change", toggle);
    toggle(); run();
  });
})(typeof window !== "undefined" ? window : globalThis);
