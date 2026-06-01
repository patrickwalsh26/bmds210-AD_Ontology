# ADO Evaluation Results Summary

Generated: 2026-06-01

## Track 1 — Vignettes (development + held-out)

```
Traceback (most recent call last):
  File "/workspace/evaluation/vignette_eval.py", line 24, in <module>
    from baselines import find_matching_preferences_condition_blind
  File "/workspace/evaluation/baselines.py", line 17
    from __future__ import annotations
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
SyntaxError: from __future__ imports must occur at the beginning of the file
```

## Track 1 — Ablation (condition-blind, development only)

```
Traceback (most recent call last):
  File "/workspace/evaluation/vignette_eval.py", line 24, in <module>
    from baselines import find_matching_preferences_condition_blind
  File "/workspace/evaluation/baselines.py", line 17
    from __future__ import annotations
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
SyntaxError: from __future__ imports must occur at the beginning of the file
```

## Track 1b — Multi-patient cohort simulation

```
  File "/workspace/evaluation/realistic_simulation.py", line 22
    from __future__ import annotations
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
SyntaxError: from __future__ imports must occur at the beginning of the file
```

## Track 3 — Code status / POLST

```
====================================================================================================
  TRACK 3 — Preference profile -> code-status / POLST mapping fidelity
====================================================================================================
Traceback (most recent call last):
  File "/workspace/evaluation/track3_evaluation.py", line 345, in <module>
    main()
  File "/workspace/evaluation/track3_evaluation.py", line 288, in main
    result, fm = evaluate_profile(p)
                 ^^^^^^^^^^^^^^^^^^^
  File "/workspace/evaluation/track3_evaluation.py", line 245, in evaluate_profile
    onto = world.get_ontology(str(BASE_OWL.resolve())).load()
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/ubuntu/.local/lib/python3.12/site-packages/owlready2/namespace.py", line 1026, in load
    fileobj = open(f, "rb")
              ^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: '/workspace/evaluation/advanced_directives.owl'
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
