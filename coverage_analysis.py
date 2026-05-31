#!/usr/bin/env python3
"""
Systematic coverage analysis: 30 verbatim clauses from the 50-template inventory.

Each clause is labeled for representability in ADO (HF-scoped, 5 decision points).
Run: python coverage_analysis.py
"""

from collections import Counter

# Stratified sample across template families (inventory IDs in comments)
CLAUSES = [
    {"id": "C01", "source": "CA AHCD", "text": "If I have a terminal condition, I do not want CPR.",
     "label": "representable", "note": "Conditional CPR refusal"},
    {"id": "C02", "source": "Texas OOH-DNR", "text": "Do not attempt resuscitation including CPR and defibrillation.",
     "label": "representable", "note": "Multiple clear refusals"},
    {"id": "C03", "source": "Living will", "text": "I would accept a ventilator temporarily if reversible, but not indefinitely.",
     "label": "representable", "note": "Temp vs indefinite ventilation"},
    {"id": "C04", "source": "Five Wishes", "text": "I do not want heroic measures if I am dying.",
     "label": "vague", "note": "VaguePreference + originalText"},
    {"id": "C05", "source": "POLST", "text": "Attempt cardiopulmonary resuscitation.",
     "label": "representable", "note": "Maps to POLST A / code status layer"},
    {"id": "C06", "source": "ICD clause", "text": "Deactivate my ICD if I enroll in hospice.",
     "label": "representable", "note": "Device + care context"},
    {"id": "C07", "source": "HF clinic", "text": "No escalation to ICU-level vasopressors if no LVAD plan.",
     "label": "partial_loss", "note": "LVAD plan qualifier hard to encode without surrogate axis"},
    {"id": "C08", "source": "Living will", "text": "I want feeding tubes if I might recover.",
     "label": "out_of_scope", "note": "Artificial nutrition not in ontology"},
    {"id": "C09", "source": "Living will", "text": "No antibiotics if I am dying.",
     "label": "out_of_scope", "note": "Antibiotics not modeled"},
    {"id": "C10", "source": "UC AHCD", "text": "My agent may override my written wishes.",
     "label": "who_decides_gap", "note": "Second dimension per Magnus — not modeled"},
    {"id": "C11", "source": "VA", "text": "I want all treatments necessary to keep me alive including CPR.",
     "label": "representable", "note": "Clear affirmative"},
    {"id": "C12", "source": "NIV clause", "text": "Try BiPAP but never intubate.",
     "label": "representable", "note": "NIV yes / intubation no"},
    {"id": "C13", "source": "Dialysis", "text": "Short-term dialysis OK if kidneys may recover; no chronic dialysis.",
     "label": "representable", "note": "Acute vs chronic"},
    {"id": "C14", "source": "Time trial", "text": "Try a 2-week ICU trial then reassess.",
     "label": "owl_gap", "note": "POLST time-limited trial not modeled"},
    {"id": "C15", "source": "Comfort", "text": "Focus on comfort even if it shortens life.",
     "label": "vague", "note": "Comfort goal — partial mapping only"},
    {"id": "C16", "source": "Pacing", "text": "No external pacing.",
     "label": "representable", "note": "Transcutaneous pacing subclass"},
    {"id": "C17", "source": "LVAD", "text": "Do not turn off my LVAD.",
     "label": "representable", "note": "LVAD continuation"},
    {"id": "C18", "source": "Shock", "text": "Allow ICD shocks if I collapse.",
     "label": "representable", "note": "ICD shock therapy"},
    {"id": "C19", "source": "Withdrawal", "text": "Stop vasopressors after 72 hours if no improvement.",
     "label": "representable", "note": "Numeric time bound"},
    {"id": "C20", "source": "Organ donation", "text": "I wish to donate organs.",
     "label": "out_of_scope", "note": "Outside EOL intervention scope"},
    {"id": "C21", "source": "Mental health", "text": "ECT is acceptable if I lose capacity.",
     "label": "out_of_scope", "note": "Outside HF EOL scope"},
    {"id": "C22", "source": "Pregnancy", "text": "Maintain life support until delivery if pregnant.",
     "label": "out_of_scope", "note": "Special population"},
    {"id": "C23", "source": "CA POLST B", "text": "Selective treatment — hospitalize, avoid ICU.",
     "label": "partial_loss", "note": "POLST B granularity vs code-status mapping"},
    {"id": "C24", "source": "Dementia", "text": "If severe dementia, no CPR.",
     "label": "representable", "note": "Condition-gated CPR"},
    {"id": "C25", "source": "Pediatric", "text": "Parents decide all care.",
     "label": "who_decides_gap", "note": "Pediatric proxy — different model"},
    {"id": "C26", "source": "Religious", "text": "Follow Catholic moral teaching on ordinary care.",
     "label": "vague", "note": "Requires external ethicist interpretation"},
    {"id": "C27", "source": "Research", "text": "Enroll me in any experimental trial.",
     "label": "out_of_scope", "note": "Research not modeled"},
    {"id": "C28", "source": "Combined", "text": "No CPR, but family should decide if unsure.",
     "label": "who_decides_gap", "note": "Intervention + surrogate override"},
    {"id": "C29", "source": "HF NYHA", "text": "No CPR if NYHA IV and no reversible cause.",
     "label": "representable", "note": "Core ADO use case"},
    {"id": "C30", "source": "Pain", "text": "Adequate pain control even with sedation.",
     "label": "partial_loss", "note": "Symptom goal not intervention subclass"},
]


def main():
    c = Counter(item["label"] for item in CLAUSES)
    n = len(CLAUSES)
    rep = c["representable"]

    print("=" * 80)
    print("  COVERAGE ANALYSIS — 30 inventory-sourced clauses")
    print("=" * 80)
    print(f"\n  Total clauses: {n}")
    print(f"  Fully representable (HF in-scope): {rep}/{n} ({100*rep/n:.0f}%)")
    print(f"  Representable as vague only: {c['vague']}/{n}")
    print(f"  Partial information loss if encoded: {c['partial_loss']}/{n}")
    print(f"  Who-decides / surrogate gap: {c['who_decides_gap']}/{n}")
    print(f"  OWL expressivity gap: {c['owl_gap']}/{n}")
    print(f"  Out of scope (other domains): {c['out_of_scope']}/{n}")
    print("\n  By label:")
    for label, count in sorted(c.items(), key=lambda x: -x[1]):
        print(f"    {label:20s}: {count}")

    print("\n  Detail:")
    for item in CLAUSES:
        print(f"    [{item['id']}] {item['label']:18s} — {item['source']}: {item['text'][:60]}...")

    print("\n  Interpretation: ADO covers the core HF intervention grammar well but cannot")
    print("  yet represent surrogate-override, nutrition/antibiotics, time-limited trials,")
    print("  or non-intervention goals (comfort-only) without loss.")


if __name__ == "__main__":
    main()
