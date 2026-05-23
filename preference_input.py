"""
Structured Preference Input Pipeline for Advanced Directive Ontology

Takes patient preferences as JSON and instantiates OWL individuals
using owlready2. Supports CLI questionnaire mode and direct JSON input.

Usage:
    python preference_input.py --interactive          # CLI questionnaire
    python preference_input.py --json input.json      # Load from JSON file
    python preference_input.py --example              # Generate example JSON + populate ontology
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import date

try:
    from owlready2 import get_ontology, default_world, sync_reasoner_hermit
except ImportError:
    print("ERROR: owlready2 is not installed. Run: pip install owlready2")
    sys.exit(1)

OWL_FILE = Path(__file__).parent / "advanced_directives.owl"
OUTPUT_DIR = Path(__file__).parent / "populated_ontologies"

# ── Valid values for structured input ──────────────────────────────────────────

INTERVENTIONS = {
    "cpr": "CPR",
    "defibrillation": "Defibrillation",
    "transcutaneous_pacing": "TranscutaneousPacing",
    "intubation": "Intubation",
    "mechanical_ventilation": "MechanicalVentilation",
    "temporary_ventilation": "TemporaryVentilation",
    "indefinite_ventilation": "IndefiniteVentilation",
    "ventilation_withdrawal": "VentilationWithdrawal",
    "non_invasive_ventilation": "NonInvasiveVentilation",
    "icd_deactivation": "ICDDeactivation",
    "icd_shock_therapy": "ICDShockTherapy",
    "lvad_withdrawal": "LVADWithdrawal",
    "lvad_continuation": "LVADContinuation",
    "pacemaker_deactivation": "PacemakerDeactivation",
    "inotrope_escalation": "InotropeEscalation",
    "inotrope_withdrawal": "InotropeWithdrawal",
    "vasopressor_escalation": "VasopressorEscalation",
    "vasopressor_withdrawal": "VasopressorWithdrawal",
    "acute_dialysis": "AcuteDialysis",
    "chronic_dialysis": "ChronicDialysis",
    "dialysis_withdrawal": "DialysisWithdrawal",
}

CONDITIONS = {
    "heart_failure": "HeartFailure",
    "advanced_heart_failure": "AdvancedHeartFailure",
    "cardiac_arrest": "CardiacArrest",
    "cardiogenic_shock": "CardiogenicShock",
    "acute_decompensation": "AcuteDecompensation",
    "cardiorenal_syndrome": "CardiorenalSyndrome",
    "respiratory_failure": "RespiratoryFailure",
    "terminal_condition": "TerminalCondition",
    "permanent_unconsciousness": "PermanentUnconsciousness",
    "incapacity": "Incapacity",
}

NYHA_CLASSES = {
    "I": "NYHA_ClassI",
    "II": "NYHA_ClassII",
    "III": "NYHA_ClassIII",
    "IV": "NYHA_ClassIV",
}

PREFERENCE_STRENGTHS = ["Absolute", "Strong", "Conditional", "Weak"]

CARE_CONTEXTS = {
    "icu": "ICUSetting",
    "ed": "EmergencyDepartment",
    "hospice": "HospiceEnrollment",
    "outpatient": "OutpatientSetting",
    "prehospital": "PrehospitalSetting",
}

DOC_TYPES = {
    "living_will": "LivingWill",
    "hcpoa": "HealthCarePowerOfAttorney",
    "polst": "POLSTForm",
    "dnr": "DNROrder",
}


def make_id(text):
    """Convert a string into a safe OWL individual name."""
    return "".join(c if c.isalnum() else "_" for c in text).strip("_")


def load_ontology():
    """Load the base ADO ontology."""
    if not OWL_FILE.exists():
        print(f"ERROR: Ontology file not found at {OWL_FILE}")
        sys.exit(1)
    onto = get_ontology(str(OWL_FILE.resolve())).load()
    return onto


def get_or_create_individual(onto, class_name, individual_name):
    """Get an existing individual or create one of the given class."""
    existing = onto.search_one(iri=f"*{individual_name}")
    if existing:
        return existing
    cls = getattr(onto, class_name, None)
    if cls is None:
        print(f"  WARNING: Class '{class_name}' not found in ontology, skipping.")
        return None
    individual = cls(individual_name)
    return individual


def populate_patient(onto, patient_data):
    """
    Create a Patient individual and all associated preferences from structured data.

    patient_data schema:
    {
        "patient_id": "string",
        "patient_name": "string",
        "proxy": {
            "name": "string",
            "relationship": "string"
        },
        "source_document": {
            "type": "living_will|hcpoa|polst|dnr",
            "label": "string"
        },
        "preferences": [
            {
                "label": "string",
                "intervention": "key from INTERVENTIONS",
                "negated": true/false,
                "strength": "Absolute|Strong|Conditional|Weak",
                "original_text": "string",
                "type": "clear|vague|conditional",
                "activation_conditions": {
                    "nyha_class": "I|II|III|IV" (optional),
                    "conditions": ["keys from CONDITIONS"] (optional),
                    "reversible_cause": true/false/null (optional),
                    "time_bound": "string" (optional),
                    "care_context": "key from CARE_CONTEXTS" (optional)
                }
            }
        ]
    }
    """
    pid = make_id(patient_data["patient_id"])
    patient_name = patient_data.get("patient_name", pid)

    # Create patient
    patient = get_or_create_individual(onto, "Patient", f"Patient_{pid}")
    patient.label = [patient_name]
    print(f"\nCreated patient: {patient_name} ({patient.name})")

    # Create proxy if provided
    proxy_data = patient_data.get("proxy")
    if proxy_data:
        proxy_id = make_id(proxy_data["name"])
        proxy = get_or_create_individual(onto, "DecisionMaker", f"Proxy_{proxy_id}")
        proxy.label = [proxy_data["name"]]
        proxy.proxyName = [proxy_data["name"]]
        if "relationship" in proxy_data:
            proxy.proxyRelationship = [proxy_data["relationship"]]
        patient.hasProxy = [proxy]
        print(f"  Proxy: {proxy_data['name']} ({proxy_data.get('relationship', 'N/A')})")

    # Create source document if provided
    doc_data = patient_data.get("source_document")
    doc_individual = None
    if doc_data:
        doc_class = DOC_TYPES.get(doc_data.get("type"), "AdvanceDirectiveDocument")
        doc_individual = get_or_create_individual(
            onto, doc_class, f"Doc_{pid}_{make_id(doc_data.get('type', 'ad'))}"
        )
        if doc_individual:
            doc_individual.label = [doc_data.get("label", f"{patient_name}'s Advance Directive")]

    # Create preferences
    for i, pref_data in enumerate(patient_data.get("preferences", [])):
        pref_id = f"Pref_{pid}_{i+1}"
        pref_label = pref_data.get("label", f"Preference {i+1}")

        # Determine preference type class
        pref_type = pref_data.get("type", "clear")
        type_map = {
            "clear": "ClearPreference",
            "vague": "VaguePreference",
            "conditional": "ConditionalPreference",
        }
        pref_class = type_map.get(pref_type, "PreferenceStatement")

        pref = get_or_create_individual(onto, pref_class, pref_id)
        if pref is None:
            continue
        pref.label = [pref_label]

        # Link intervention
        intervention_key = pref_data.get("intervention")
        if intervention_key:
            intervention_class = INTERVENTIONS.get(intervention_key)
            if intervention_class:
                interv = get_or_create_individual(
                    onto, intervention_class, f"Interv_{pid}_{intervention_key}"
                )
                if interv:
                    pref.specifiesIntervention = [interv]

        # Set negation
        pref.isNegated = [pref_data.get("negated", False)]

        # Set preference strength
        strength = pref_data.get("strength", "Strong")
        if strength in PREFERENCE_STRENGTHS:
            pref.hasPreferenceStrength = [strength]

        # Set original text
        original = pref_data.get("original_text", "")
        if original:
            pref.originalText = [original]

        # Set date
        pref.dateDocumented = [date.today().isoformat()]

        # Link source document
        if doc_individual:
            pref.sourceDocument = [doc_individual]

        # Build activation conditions
        ac_data = pref_data.get("activation_conditions", {})
        if ac_data:
            ac = get_or_create_individual(onto, "ActivationCondition", f"AC_{pref_id}")
            if ac:
                ac.label = [f"Activation conditions for: {pref_label}"]

                # NYHA class
                nyha = ac_data.get("nyha_class")
                if nyha and nyha in NYHA_CLASSES:
                    nyha_individual = get_or_create_individual(
                        onto, NYHA_CLASSES[nyha], f"NYHA_{nyha}_for_{pref_id}"
                    )
                    if nyha_individual:
                        ac.requiresFunctionalStatus = [nyha_individual]

                # Clinical conditions
                conditions = ac_data.get("conditions", [])
                for cond_key in conditions:
                    cond_class = CONDITIONS.get(cond_key)
                    if cond_class:
                        cond = get_or_create_individual(
                            onto, cond_class, f"Cond_{pid}_{cond_key}"
                        )
                        if cond:
                            ac.requiresCondition.append(cond)

                # Reversible cause
                rev = ac_data.get("reversible_cause")
                if rev is not None:
                    ac.hasReversibleCause = [rev]

                # Time bound (human-readable string)
                tb = ac_data.get("time_bound")
                if tb:
                    ac.hasTimeBound = [tb]

                # Time bound (machine-comparable hours) — enables temporal reasoning
                tb_hours = ac_data.get("time_bound_hours")
                if tb_hours is not None:
                    ac.hasTimeBoundHours = [int(tb_hours)]

                # Care context (e.g., HospiceEnrollment, ICUSetting)
                ctx_key = ac_data.get("care_context")
                if ctx_key and ctx_key in CARE_CONTEXTS:
                    ctx_individual = get_or_create_individual(
                        onto, CARE_CONTEXTS[ctx_key], f"Ctx_{pid}_{ctx_key}"
                    )
                    if ctx_individual:
                        ac.requiresCareContext = [ctx_individual]

                pref.hasActivationCondition = [ac]

        # Link preference to patient
        patient.hasPreference.append(pref)

        negation_str = "DO NOT want" if pref_data.get("negated") else "want"
        print(f"  Preference {i+1}: {negation_str} {intervention_key} "
              f"[{strength}] ({pref_type})")

    return patient


def save_ontology(onto, patient_id):
    """Save the populated ontology to a new file."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    output_path = OUTPUT_DIR / f"ado_{patient_id}.owl"
    onto.save(file=str(output_path.resolve()), format="rdfxml")
    print(f"\nSaved populated ontology to: {output_path}")
    return output_path


def run_interactive():
    """CLI questionnaire mode for entering preferences."""
    print("=" * 60)
    print("  Advanced Directive Preference Input")
    print("  (Heart Failure End-of-Life Care)")
    print("=" * 60)

    patient_data = {"preferences": []}

    # Patient info
    patient_data["patient_id"] = input("\nPatient ID (e.g., initials or code): ").strip()
    patient_data["patient_name"] = input("Patient name (or pseudonym): ").strip()

    # Proxy
    proxy_name = input("\nHealthcare proxy name (or press Enter to skip): ").strip()
    if proxy_name:
        proxy_rel = input("Proxy relationship (e.g., Spouse, Child, Friend): ").strip()
        patient_data["proxy"] = {"name": proxy_name, "relationship": proxy_rel}

    # Document type
    print("\nSource document type:")
    for key, label in DOC_TYPES.items():
        print(f"  {key}: {label}")
    doc_type = input("Enter type (or press Enter to skip): ").strip()
    if doc_type in DOC_TYPES:
        patient_data["source_document"] = {"type": doc_type, "label": f"{patient_data['patient_name']}'s {DOC_TYPES[doc_type]}"}

    # Preferences — walk through each decision point
    decision_points = [
        {
            "name": "CPR / Resuscitation",
            "interventions": ["cpr", "defibrillation", "transcutaneous_pacing"],
            "description": "Would you want CPR if your heart stops?",
        },
        {
            "name": "Mechanical Ventilation",
            "interventions": [
                "intubation", "temporary_ventilation", "indefinite_ventilation",
                "non_invasive_ventilation", "ventilation_withdrawal",
            ],
            "description": "Would you want to be placed on a breathing machine?",
        },
        {
            "name": "ICD / Device Management",
            "interventions": [
                "icd_deactivation", "icd_shock_therapy",
                "lvad_withdrawal", "lvad_continuation", "pacemaker_deactivation",
            ],
            "description": "If you have an ICD or LVAD, when should it be deactivated?",
        },
        {
            "name": "Vasopressor / Inotrope Support",
            "interventions": [
                "inotrope_escalation", "inotrope_withdrawal",
                "vasopressor_escalation", "vasopressor_withdrawal",
            ],
            "description": "Would you want medications to support your heart's pumping and blood pressure?",
        },
        {
            "name": "Dialysis",
            "interventions": ["acute_dialysis", "chronic_dialysis", "dialysis_withdrawal"],
            "description": "Would you want dialysis if your kidneys fail?",
        },
    ]

    for dp in decision_points:
        print(f"\n{'─' * 50}")
        print(f"  Decision Point: {dp['name']}")
        print(f"  {dp['description']}")
        print(f"{'─' * 50}")

        print("\n  Available interventions:")
        for key in dp["interventions"]:
            print(f"    {key}: {INTERVENTIONS[key]}")

        while True:
            interv = input(f"\n  Enter intervention key (or 'next' to move on): ").strip()
            if interv == "next" or interv == "":
                break
            if interv not in INTERVENTIONS:
                print(f"  Unknown intervention '{interv}'. Try again.")
                continue

            negated_input = input("  Do you NOT want this? (y/n): ").strip().lower()
            negated = negated_input == "y"

            print("  Preference strength: Absolute / Strong / Conditional / Weak")
            strength = input("  Strength: ").strip()
            if strength not in PREFERENCE_STRENGTHS:
                strength = "Strong"

            original = input("  Original text (in your own words): ").strip()

            # Activation conditions
            print("\n  Activation conditions (press Enter to skip each):")
            nyha = input("    NYHA class (I/II/III/IV): ").strip()
            if nyha not in NYHA_CLASSES:
                nyha = None

            print("    Clinical conditions:")
            for key in CONDITIONS:
                print(f"      {key}")
            cond_input = input("    Conditions (comma-separated keys): ").strip()
            conditions = [c.strip() for c in cond_input.split(",") if c.strip() in CONDITIONS] if cond_input else []

            rev_input = input("    Reversible cause required? (y/n/skip): ").strip().lower()
            reversible = True if rev_input == "y" else (False if rev_input == "n" else None)

            time_bound = input("    Time bound (e.g., 'after 7 days'): ").strip() or None

            print(f"    Care contexts: {', '.join(CARE_CONTEXTS.keys())}")
            context = input("    Care context: ").strip()
            if context not in CARE_CONTEXTS:
                context = None

            pref_type = "conditional" if (nyha or conditions or reversible is not None or time_bound) else "clear"

            ac = {}
            if nyha:
                ac["nyha_class"] = nyha
            if conditions:
                ac["conditions"] = conditions
            if reversible is not None:
                ac["reversible_cause"] = reversible
            if time_bound:
                ac["time_bound"] = time_bound
            if context:
                ac["care_context"] = context

            action = "Do NOT want" if negated else "Want"
            label = f"{action} {INTERVENTIONS[interv]}"

            pref = {
                "label": label,
                "intervention": interv,
                "negated": negated,
                "strength": strength,
                "original_text": original,
                "type": pref_type,
            }
            if ac:
                pref["activation_conditions"] = ac

            patient_data["preferences"].append(pref)
            print(f"  ✓ Added: {label} [{strength}]")

    return patient_data


def generate_example():
    """Generate an example JSON file showing the input schema."""
    example = {
        "patient_id": "jane_doe_001",
        "patient_name": "Jane Doe",
        "proxy": {
            "name": "John Doe",
            "relationship": "Spouse"
        },
        "source_document": {
            "type": "living_will",
            "label": "Jane Doe's Living Will"
        },
        "preferences": [
            {
                "label": "No CPR if NYHA IV without reversible cause",
                "intervention": "cpr",
                "negated": True,
                "strength": "Absolute",
                "original_text": "If my heart stops and I am in NYHA Class IV with no reversible cause, do not attempt CPR.",
                "type": "conditional",
                "activation_conditions": {
                    "nyha_class": "IV",
                    "conditions": ["cardiac_arrest"],
                    "reversible_cause": False
                }
            },
            {
                "label": "Accept temporary ventilation if reversible cause",
                "intervention": "temporary_ventilation",
                "negated": False,
                "strength": "Conditional",
                "original_text": "I would accept temporary intubation if there is a reversible cause, but not indefinite ventilation.",
                "type": "conditional",
                "activation_conditions": {
                    "reversible_cause": True
                }
            },
            {
                "label": "No indefinite ventilation",
                "intervention": "indefinite_ventilation",
                "negated": True,
                "strength": "Absolute",
                "original_text": "I would accept temporary intubation if there is a reversible cause, but not indefinite ventilation.",
                "type": "clear"
            },
            {
                "label": "Deactivate ICD if enrolled in hospice",
                "intervention": "icd_deactivation",
                "negated": False,
                "strength": "Strong",
                "original_text": "Deactivate my ICD if I am enrolled in hospice.",
                "type": "conditional",
                "activation_conditions": {
                    "care_context": "hospice"
                }
            },
            {
                "label": "No chronic dialysis",
                "intervention": "chronic_dialysis",
                "negated": True,
                "strength": "Absolute",
                "original_text": "I do not want to be placed on long-term maintenance dialysis.",
                "type": "clear"
            },
            {
                "label": "Accept acute dialysis if recoverable",
                "intervention": "acute_dialysis",
                "negated": False,
                "strength": "Conditional",
                "original_text": "I would accept short-term dialysis if my kidney function is expected to recover.",
                "type": "conditional",
                "activation_conditions": {
                    "reversible_cause": True,
                    "conditions": ["cardiorenal_syndrome"]
                }
            },
            {
                "label": "Escalate inotropes only if LVAD or transplant planned",
                "intervention": "inotrope_escalation",
                "negated": False,
                "strength": "Conditional",
                "original_text": "Escalate inotropes only if there is a plan for LVAD or transplant evaluation.",
                "type": "conditional",
                "activation_conditions": {
                    "conditions": ["cardiogenic_shock"]
                }
            },
            {
                "label": "Withdraw vasopressors if no improvement after 72 hours",
                "intervention": "vasopressor_withdrawal",
                "negated": False,
                "strength": "Strong",
                "original_text": "If I am on vasopressors with no improvement after 3 days, withdraw them.",
                "type": "conditional",
                "activation_conditions": {
                    "time_bound": "no improvement after 72 hours",
                    "time_bound_hours": 72,
                    "conditions": ["cardiogenic_shock"]
                }
            },
            {
                "label": "Vague: no aggressive measures",
                "intervention": "non_invasive_ventilation",
                "negated": True,
                "strength": "Weak",
                "original_text": "If I am dying, I do not want aggressive measures or to be kept alive by machines.",
                "type": "vague"
            }
        ]
    }
    return example


def main():
    parser = argparse.ArgumentParser(
        description="Populate the Advanced Directive Ontology with patient preferences."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--interactive", action="store_true",
                       help="Enter preferences via CLI questionnaire")
    group.add_argument("--json", type=str,
                       help="Path to a JSON file with patient preference data")
    group.add_argument("--example", action="store_true",
                       help="Generate example JSON and populate ontology with it")
    args = parser.parse_args()

    if args.interactive:
        patient_data = run_interactive()
        # Save the raw JSON too for reproducibility
        json_path = OUTPUT_DIR / f"input_{make_id(patient_data['patient_id'])}.json"
        OUTPUT_DIR.mkdir(exist_ok=True)
        with open(json_path, "w") as f:
            json.dump(patient_data, f, indent=2)
        print(f"\nSaved input JSON to: {json_path}")

    elif args.json:
        json_path = Path(args.json)
        if not json_path.exists():
            print(f"ERROR: JSON file not found: {json_path}")
            sys.exit(1)
        with open(json_path) as f:
            patient_data = json.load(f)

    elif args.example:
        patient_data = generate_example()
        OUTPUT_DIR.mkdir(exist_ok=True)
        example_path = OUTPUT_DIR / "example_input.json"
        with open(example_path, "w") as f:
            json.dump(patient_data, f, indent=2)
        print(f"Example JSON saved to: {example_path}")

    # Load ontology and populate
    print("\nLoading ontology...")
    onto = load_ontology()

    with onto:
        populate_patient(onto, patient_data)

    # Save populated ontology
    output_path = save_ontology(onto, make_id(patient_data["patient_id"]))

    print(f"\nDone! Open {output_path} in Protege to inspect the populated ontology.")
    print("You can run the HermiT reasoner in Protege to check consistency and infer classifications.")


if __name__ == "__main__":
    main()
