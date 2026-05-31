# ADO Evaluation Results Summary

Generated: 2026-05-31

## Track 1 — Vignettes (development + held-out)

```
================================================================================
  VIGNETTE EVALUATION
================================================================================

################################################################################
  Development (n=16)
################################################################################
  [PASS] V1: got no/clear expected no/clear
  [PASS] V2: got partial/partial expected partial/partial
  [PASS] V3: got yes/clear expected yes/clear
  [PASS] V4: got no/clear expected no/clear
  [PASS] V5: got yes/clear expected yes/clear
  [PASS] V6: got partial/partial expected partial/partial
  [PASS] V7: got yes/clear expected yes/clear
  [PASS] V8: got no/clear expected no/clear
  [PASS] V9: got yes/clear expected yes/clear
  [PASS] V10: got yes/clear expected yes/clear
  [PASS] V11: got vague/vague expected vague/vague
  [PASS] V12: got no_coverage/no_coverage expected no_coverage/no_coverage
  [PASS] V13: got partial/partial expected partial/partial
  [PASS] V14: got partial/partial expected partial/partial
  [PASS] V15: got no/clear expected no/clear
  [PASS] V16: got no_coverage/no_coverage expected no_coverage/no_coverage

  Decision accuracy   : 16/16 (100%)
  Match-type accuracy : 16/16 (100%)

################################################################################
  Held-out (n=10)
################################################################################
  [PASS] H1: got no_coverage/no_coverage expected no_coverage/no_coverage
  [PASS] H2: got partial/partial expected partial/partial
  [PASS] H3: got yes/clear expected yes/clear
  [PASS] H4: got no_coverage/no_coverage expected no_coverage/no_coverage
  [PASS] H5: got no_coverage/no_coverage expected no_coverage/no_coverage
  [PASS] H6: got no_coverage/no_coverage expected no_coverage/no_coverage
  [PASS] H7: got yes/clear expected yes/clear
  [PASS] H8: got yes/clear expected yes/clear
  [PASS] H9: got partial/partial expected partial/partial
  [PASS] H10: got vague/vague expected vague/vague

  Decision accuracy   : 10/10 (100%)
  Match-type accuracy : 10/10 (100%)
```

## Track 1 — Ablation (condition-blind, development only)

```
================================================================================
  VIGNETTE EVALUATION
  Baseline: condition-blind
================================================================================

################################################################################
  Development (n=16)
################################################################################
  [PASS] V1: got no/clear expected no/clear
  [FAIL] V2: got no/clear expected partial/partial
  [PASS] V3: got yes/clear expected yes/clear
  [PASS] V4: got no/clear expected no/clear
  [PASS] V5: got yes/clear expected yes/clear
  [FAIL] V6: got yes/clear expected partial/partial
  [PASS] V7: got yes/clear expected yes/clear
  [PASS] V8: got no/clear expected no/clear
  [PASS] V9: got yes/clear expected yes/clear
  [PASS] V10: got yes/clear expected yes/clear
  [FAIL] V11: got no/clear expected vague/vague
  [PASS] V12: got no_coverage/no_coverage expected no_coverage/no_coverage
  [FAIL] V13: got yes/clear expected partial/partial
  [FAIL] V14: got yes/clear expected partial/partial
  [PASS] V15: got no/clear expected no/clear
  [PASS] V16: got no_coverage/no_coverage expected no_coverage/no_coverage

  Decision accuracy   : 11/16 (69%)
  Match-type accuracy : 11/16 (69%)
  Failures: V2, V6, V11, V13, V14
```

## Track 1b — Multi-patient cohort simulation

```
========================================================================
  MULTI-PATIENT COHORT SIMULATION (realistic / messy profiles)
========================================================================
  Cells evaluated     : 520 (20 patients × 12 scenarios × queried interventions)

  ADO decision vs ref : 46.9%
  ADO match-type vs ref: 48.7%
  Condition-blind     : 44.6%
  Checkbox (flat POLST, silent→full code): 19.0%
  Checkbox (silent→no coverage)          : 85.6%
  ADO on cells WITH directive coverage   : 24.1% (174/520 cells)
  Checkbox overconfident (nuanced gold → flat yes/no): 421 cells

  By messy_level tag:
    clean                  n=182  ADO dec  56.0%  match  58.8%  blind  49.5%  checkbox  22.5%
    contradictory          n= 26  ADO dec  46.2%  match  50.0%  blind  46.2%  checkbox  26.9%
    incomplete_encoding    n= 26  ADO dec  42.3%  match  42.3%  blind  42.3%  checkbox   7.7%
    minimal                n= 52  ADO dec  36.5%  match  36.5%  blind  44.2%  checkbox  19.2%
    typical                n=234  ADO dec  42.7%  match  44.0%  blind  41.0%  checkbox  16.7%

  Sample ADO≠reference cells (up to 25):
    cohort_01_jane S01 Defibrillation: ref no/clear → ADO no_coverage/no_coverage
    cohort_01_jane S01 ICDShockTherapy: ref partial/partial → ADO no_coverage/no_coverage
    cohort_01_jane S02 Defibrillation: ref partial/partial → ADO no_coverage/no_coverage
    cohort_01_jane S06 ICDShockTherapy: ref partial/partial → ADO no_coverage/no_coverage
    cohort_02_texas_dnr S01 Defibrillation: ref no/clear → ADO no_coverage/no_coverage
    cohort_02_texas_dnr S02 CPR: ref no/clear → ADO partial/partial
    cohort_02_texas_dnr S02 Defibrillation: ref no/clear → ADO no_coverage/no_coverage
    cohort_02_texas_dnr S03 TemporaryVentilation: ref no/clear → ADO yes/clear
    cohort_02_texas_dnr S03 NonInvasiveVentilation: ref no/clear → ADO no_coverage/no_coverage
    cohort_02_texas_dnr S03 Intubation: ref no/clear → ADO no_coverage/no_coverage
    cohort_02_texas_dnr S04 VentilationWithdrawal: ref no/clear → ADO no_coverage/no_coverage
    cohort_02_texas_dnr S05 ICDDeactivation: ref no_coverage/no_coverage → ADO yes/clear

```

## Track 3 — Code status / POLST

```
====================================================================================================
  TRACK 3 — Preference profile -> code-status / POLST mapping fidelity
====================================================================================================

[P1] National Catholic Bioethics Center directive   -> EXACT
     ok Code status  derived: Full code                                gold: Full code
     ok POLST A      derived: Attempt CPR/Full Resuscitation           gold: Attempt CPR/Full Resuscitation
     ok POLST B      derived: Full Treatment                           gold: Full Treatment

[P2] Texas Out-of-Hospital DNR   -> EXACT
     ok Code status  derived: DNR/DNI                                  gold: DNR/DNI
     ok POLST A      derived: Do Not Attempt Resuscitation (DNAR)      gold: Do Not Attempt Resuscitation (DNAR)
     ok POLST B      derived: Comfort-Focused Treatment                gold: Comfort-Focused Treatment

[P3] California Prehospital DNR (CPR only)   -> EXACT
     ok Code status  derived: DNR                                      gold: DNR
     ok POLST A      derived: Do Not Attempt Resuscitation (DNAR)      gold: Do Not Attempt Resuscitation (DNAR)
     ok POLST B      derived: Full Treatment                           gold: Full Treatment

[P4] NHS Wales ADRT — condition MET (permanent unconsciousness) [conditional]   -> EXACT
     ok Code status  derived: DNR/DNI                                  gold: DNR/DNI
     ok POLST A      derived: Do Not Attempt Resuscitation (DNAR)      gold: Do Not Attempt Resuscitation (DNAR)
     ok POLST B      derived: Comfort-Focused Treatment                gold: Comfort-Focused Treatment

[P5] NHS Wales ADRT — condition NOT met (same directive, conscious)   -> DIFF
     ok Code status  derived: Full code                                gold: Full code
     ok POLST A      derived: Attempt CPR/Full Resuscitation           gold: Attempt CPR/Full Resuscitation
     XX POLST B      derived: Not specified                            gold: Full Treatment

[P6] Five Wishes — comfort if terminal [conditional]   -> EXACT
     ok Code status  derived: DNR/DNI + Do Not Escalate                gold: DNR/DNI + Do Not Escalate
     ok POLST A      derived: Do Not Attempt Resuscitation (DNAR)      gold: Do Not Attempt Resuscitation (DNAR)
     ok POLST B      derived: Comfort-Focused Treatment                gold: Comfort-Focused Treatment

[P7] Floor 'do-not-escalate' HF patient   -> EXACT
     ok Code status  derived: Do Not Escalate                          gold: Do Not Escalate
     ok POLST A      derived: Attempt CPR/Full Resuscitation           gold: Attempt CPR/Full Resuscitation
     ok POLST B      derived: Selective Treatment                      gold: Selective Treatment

[P8] DNI patient who accepts CPR and BiPAP   -> EXACT
     ok Code status  derived: DNI                                      gold: DNI
     ok POLST A      derived: Attempt CPR/Full Resuscitation           gold: Attempt CPR/Full Resuscitation
     ok POLST B      derived: Selective Treatment                      gold: Selective Treatment

[P9] Conditional DNR — condition MET (NYHA IV, no reversible cause) [conditional]   -> EXACT
     ok Code status  derived: DNR                                      gold: DNR
     ok POLST A      derived: Do Not Attempt Resuscitation (DNAR)      gold: Do Not Attempt Resuscitation (DNAR)
     ok POLST B      derived: Selective Treatment                      gold: Selective Treatment

[P10] Conditional DNR — condition NOT met (same patient, NYHA III, reversible)   -> EXACT
     ok Code status  derived: Full code                                gold: Full code
     ok POLST A      derived: Attempt CPR/Full Resuscitation           gold: Attempt CPR/Full Resuscitation
     ok POLST B      derived: Selective Treatment                      gold: Selective Treatment

[P11] VA Form 10-0137 — full aggressive care   -> EXACT
     ok Code status  derived: Full code                                gold: Full code
     ok POLST A      derived: Attempt CPR/Full Resuscitation           gold: Attempt CPR/Full Resuscitation
     ok POLST B      derived: Full Treatment                           gold: Full Treatment

[P12] Dementia-specific directive — comfort if advanced/terminal [conditional]   -> EXACT
     ok Code status  derived: DNR/DNI + Do Not Escalate                gold: DNR/DNI + Do Not Escalate
     ok POLST A      derived: Do Not Attempt Resuscitation (DNAR)      gold: Do Not Attempt Resuscitation (DNAR)
     ok POLST B      derived: Comfort-Focused Treatment                gold: Comfort-Focused Treatment

====================================================================================================
  SUMMARY
====================================================================================================
  Profiles                : 12
  Exact-profile agreement : 11/12 (92%)
  Code status             : 12/12 (100%)
  POLST A                 : 12/12 (100%)
  POLST B                 : 11/12 (92%)
  Overall field agreement : 35/36 (97%)

  Cohen's kappa (ADO derived vs. independent POLST-semantics gold):
    Code status             : kappa = 1.00
    POLST A                 : kappa = 1.00
    POLST B                 : kappa = 0.88

  Code-status confusion (rows = gold, cols = derived):
                                          DNI             DNR         DNR/DNI  DNR/DNI + Do N  Do Not Escalat       Full code
  DNI                                       1               0               0               0               0               0
  DNR                                       0               2               0               0               0               0
  DNR/DNI                                   0               0               2               0               0               0
  DNR/DNI + Do Not Escalate                 0               0               0               2               0               0
  Do Not Escalate                           0               0               0               0               1               0
  Full code                                 0               0               0               0               0               4

  Divergences (worth discussing, not necessarily errors):
    P5: NHS Wales ADRT — condition NOT met (same directive, conscious)
```

## Coverage (30 inventory clauses)

```
================================================================================
  COVERAGE ANALYSIS — 30 inventory-sourced clauses
================================================================================

  Total clauses: 30
  Fully representable (HF in-scope): 14/30 (47%)
  Representable as vague only: 3/30
  Partial information loss if encoded: 3/30
  Who-decides / surrogate gap: 3/30
  OWL expressivity gap: 1/30
  Out of scope (other domains): 6/30

  By label:
    representable       : 14
    out_of_scope        : 6
    vague               : 3
    partial_loss        : 3
    who_decides_gap     : 3
    owl_gap             : 1

  Detail:
    [C01] representable      — CA AHCD: If I have a terminal condition, I do not want CPR....
    [C02] representable      — Texas OOH-DNR: Do not attempt resuscitation including CPR and defibrillatio...
    [C03] representable      — Living will: I would accept a ventilator temporarily if reversible, but n...
    [C04] vague              — Five Wishes: I do not want heroic measures if I am dying....
    [C05] representable      — POLST: Attempt cardiopulmonary resuscitation....
    [C06] representable      — ICD clause: Deactivate my ICD if I enroll in hospice....
    [C07] partial_loss       — HF clinic: No escalation to ICU-level vasopressors if no LVAD plan....
    [C08] out_of_scope       — Living will: I want feeding tubes if I might recover....
    [C09] out_of_scope       — Living will: No antibiotics if I am dying....
    [C10] who_decides_gap    — UC AHCD: My agent may override my written wishes....
    [C11] representable      — VA: I want all treatments necessary to keep me alive including C...
    [C12] representable      — NIV clause: Try BiPAP but never intubate....
    [C13] representable      — Dialysis: Short-term dialysis OK if kidneys may recover; no chronic di...
    [C14] owl_gap            — Time trial: Try a 2-week ICU trial then reassess....
    [C15] vague              — Comfort: Focus on comfort even if it shortens life....
    [C16] representable      — Pacing: No external pacing....
    [C17] representable      — LVAD: Do not turn off my LVAD....
    [C18] representable      — Shock: Allow ICD shocks if I collapse....
    [C19] representable      — Withdrawal: Stop vasopressors after 72 hours if no improvement....
    [C20] out_of_scope       — Organ donation: I wish to donate organs....
    [C21] out_of_scope       — Mental health: ECT is acceptable if I lose capacity....
    [C22] out_of_scope       — Pregnancy: Maintain life support until delivery if pregnant....
    [C23] partial_loss       — CA POLST B: Selective treatment — hospitalize, avoid ICU....
    [C24] representable      — Dementia: If severe dementia, no CPR....
    [C25] who_decides_gap    — Pediatric: Parents decide all care....
    [C26] vague              — Religious: Follow Catholic moral teaching on ordinary care....
    [C27] out_of_scope       — Research: Enroll me in any experimental trial....
    [C28] who_decides_gap    — Combined: No CPR, but family should decide if unsure....
    [C29] representable      — HF NYHA: No CPR if NYHA IV and no reversible cause....
    [C30] partial_loss       — Pain: Adequate pain control even with sedation....

  Interpretation: ADO covers the core HF intervention grammar well but cannot
  yet represent surrogate-override, nutrition/antibiotics, time-limited trials,
  or non-intervention goals (comfort-only) without loss.
```

## Inter-annotator agreement (extraction)

```
========================================================================
  INTER-ANNOTATOR AGREEMENT (statement-level)
========================================================================
  Annotator A: annotator_a.json
  Annotator B: annotator_b.json
  Statements compared: 10
  Cohen's κ (intervention): 0.88
  Cohen's κ (negation):     0.74

  Disagreements (2):
    E5: A={'id': 'E5', 'intervention': 'vague', 'negated': True, 'type': 'vague'}  B={'id': 'E5', 'intervention': 'cpr', 'negated': True, 'type': 'vague'}
    E8: A={'id': 'E8', 'intervention': 'vasopressor_escalation', 'negated': True, 'type': 'conditional'}  B={'id': 'E8', 'intervention': 'vasopressor_escalation', 'negated': False, 'type': 'conditional'}
```
