# Magnus Meeting — Talking Points & Run-of-Show

**Meeting:** Wednesday, May 27, 2026 (Olga scheduling)
**Length:** 15 minutes
**Attendees:** Patrick Walsh, Darren Chan, Dr. David Magnus

This is a working doc for the meeting, not a deck. Use it as a script and a Q&A prep sheet. Printed length: 2–3 pages.

---

## Goal of the meeting

Get Dr. Magnus's input on the **ethical framing** of the 4-category output, the **deployment story** at the bedside, and any blind spots in how we are formalizing preferences. He has already received the 2-page packet, so we do not need to re-explain the project — just demo it and ask.

## Run-of-show (15 minutes)

| Min  | What                                          | Who      |
|------|-----------------------------------------------|----------|
| 0–1  | Thank him; confirm he received the packet     | Patrick  |
| 1–3  | 90-second project orientation                 | Patrick  |
| 3–9  | Live demo — 6 scenarios via `demo.py --pause` | Darren   |
| 9–13 | Five questions (in priority order)            | Patrick  |
| 13–15| Wrap, ask for one written paragraph if time-constrained, thanks | Patrick |

Keep the demo to **about one minute per scenario**, with Scenario 6 getting ~2 minutes. If Magnus interrupts to discuss, follow him there — that is the meeting working as intended.

---

## 90-second project orientation (use only if needed)

> "Advance directives are free-text legal documents that clinicians have to interpret under time pressure at moments of acute crisis. At 2 AM in a code, no one reads a 6-page PDF.
>
> We built an OWL ontology that lets a reasoner match a patient's documented preferences to their current clinical state. It is scoped to advanced heart failure because that's where AD-related decisions happen most often and where existing AD templates fail most — they almost never address ICDs, LVADs, inotropes.
>
> The reasoner returns one of four outputs: Clear match, Partial match, No coverage, or Vague match. The 4-category output is the design choice we'd most value your input on. The point is to be *clinically honest* — flag uncertainty rather than force an answer.
>
> Let me show you what that looks like with our example patient, Jane Doe."

---

## Live demo cheat sheet

Open a terminal in the repo root. Run:

```bash
python demo.py --pause
```

The `--pause` flag stops between scenarios. Hit Enter to advance.

### Scenario 1 — Clear match (no CPR if NYHA IV)
- **Setup line:** "Jane's in cardiac arrest, NYHA IV, no reversible cause. Code team asks: CPR?"
- **System:** `no / clear` — all three activation conditions matched
- **Talking point:** "This is the easy case. The reasoner returns a decision plus an audit trail of which conditions matched. Defensible documentation."

### Scenario 2 — Partial match (ICD deactivation, hospice-conditional)
- **Setup line:** "Jane has an ICD. Her AD says deactivate it if she's in hospice. She's in the ICU, not hospice. Cardiology asks: deactivate?"
- **System:** `partial / partial` — care context HospiceEnrollment required, scenario has ICUSetting
- **Talking point:** "Before our May 22 fix, the reasoner treated this preference as unconditional and returned a false-positive *yes*. Now it honestly says: the AD addresses this only in hospice — escalate to the surrogate. This is exactly what we want clinically."

### Scenario 3 — No coverage (pacemaker deactivation)
- **Setup line:** "Jane has a pacemaker. AD never mentions it. Device team asks: deactivate?"
- **System:** `no_coverage / no_coverage`
- **Talking point:** "**This is the case I want your ethical read on most.** The system says 'no coverage' rather than fabricating an answer or defaulting to the related ICD preference. Is that the right ethical shape? Or does 'no coverage' get misread at the bedside as 'no preference, therefore proceed'?"

### Scenario 4 — Vague match ("aggressive measures")
- **Setup line:** "Jane has acute respiratory failure. Team asks: BiPAP? Her AD says: 'If I am dying, I do not want aggressive measures or to be kept alive by machines.'"
- **System:** `vague / vague` — surfaces the patient's original language verbatim
- **Talking point:** "This is the Letter Project–style design choice — preserve the patient's voice instead of flattening it to a binary. The system picks the nearest formal class (NIV) but refuses to force a yes/no. Decision deferred to a human with full context."

### Scenario 5 — Temporal reasoning (recent fix, optional)
- **Setup line:** "Jane is in cardiogenic shock, 96 hours on vasopressors with no improvement. AD: withdraw if no improvement after 3 days."
- **System:** `yes / clear` — 96h ≥ 72h, all conditions met
- **Talking point:** "Skip if running short. This is one of three reasoning improvements we landed this week. Before, the time bound was a natural-language string and the reasoner returned partial. Now it compares numerically. We have one more open gap — V9, the LVAD/transplant qualifier — that we are intentionally leaving open as a design question, not a bug."

### Scenario 6 — Full pipeline: free-text AD → LLM extraction → ontology → reasoner ⭐
- **Setup line:** "We give Claude (claude-opus-4-7) a verbatim paragraph from an advance directive. It converts it into the same JSON schema our pipeline already accepts. We pipe that into a fresh ontology and ask: should we attempt CPR for this patient in cardiac arrest at NYHA IV?"
- **System:** LLM extracts 8 preferences with original language preserved; reasoner returns `no / clear` from the LLM-populated ontology with all four activation conditions matching (NYHA IV ✓ CardiacArrest ✓ AdvancedHeartFailure ✓ Reversible cause: False ✓).
- **Talking point (this is the one that matters most for Dr. Magnus):** "Our position is not ontology *versus* LLM. It is ontology *with* LLMs at the boundaries. The LLM extracts; the ontology is the auditable, closed-world source of truth; the reasoner produces the defensible 4-category output. The system prompt instructs the LLM to encode ONLY what the patient explicitly stated — never to extrapolate — because the reasoner's 'no coverage' behavior depends on that discipline. In high-stakes EOL care, a pure LLM is medico-legally terrifying — non-deterministic, non-reproducible, prone to false confidence. An ontology + reasoner is auditable, closed-world, and honestly says 'no coverage' when the AD does not speak to a scenario. The LLM is the right glue at the edges, not the right core."

**The discovery story (have this ready — it's the most concrete illustration of the auditability argument):**

> "The first time we ran this pipeline, the system did something unexpected — and the way we resolved it is exactly the kind of behavior we think makes this architecture defensible.
>
> Claude extracted *two* CPR-relevant preferences from the paragraph: the specific one (`no CPR if NYHA IV with no reversible cause`), and a vague one mapped to CPR (`above all, no heroic measures if I am dying`). Critically, Claude faithfully captured the *if I am dying* qualifier as an explicit `TerminalCondition` activation rather than silently dropping it. The reasoner then returned `vague / vague`, because we had not written a precedence rule for *clear specific preference vs. vague preference with explicit but unmet conditions*. We named the rule that afternoon — a vague preference whose own activation conditions are explicitly unmet does not fire — wrote it into the code with a comment pointing at this exact case, and re-ran.
>
> Then it returned `partial`, because Claude had also extracted `advanced_heart_failure` as a separate activation condition for the specific preference, and our scenario state didn't include it. The LLM was right; our scenario was under-specified. We added `AdvancedHeartFailure` to the scenario representation — because a NYHA IV cardiac-arrest patient with HF is, by definition, in advanced HF — and the third run returned `no / clear`.
>
> That's the audit trail you don't get with an LLM-only system. The LLM surfaced two real design questions; the structured layer forced us to name and codify the rules; we now have explicit, defensible behavior in places where we'd previously had implicit assumptions. A pure-LLM system would have produced confident prose in all three runs and we'd never have known."

This is the story to use if Magnus pushes on Q1 ("4-category output") or Q3 ("liability and defensibility"). It demonstrates the auditability argument with concrete artifacts.

**Demo length budget:** ~6 minutes. If running long, skip Scenario 5 and shorten talking points on 1–4 to spend more time on Scenario 6.

**Important:** Scenario 6 calls the live Anthropic API. Make sure `ANTHROPIC_API_KEY` is exported in the terminal you're sharing — if not, the demo will fall back to the hand-coded ontology and print a yellow warning, which is much less compelling. Test before the meeting: `python demo.py --scenario 6 | head -30` should show "Extracting with Claude (claude-opus-4-7)…" followed by extracted preferences.

---

## The five questions, in priority order

These are in the packet. Lead with #1; if time runs short after the demo, get through #1, #4, #2 (in that order) — those are the ones his answer most affects what we ship.

### 1. The 4-category output (must-ask)
> "Our most important design choice is the four-category output. Is *Clear / Partial / No coverage / Vague* the right ethical shape? In particular — is there a real risk that 'No coverage' gets read at the bedside as 'no preference, therefore proceed,' when we mean 'the AD does not authorize action, escalate to surrogate'?"

**Listen for:** alternative phrasings he suggests, e.g. "AD silent" vs. "no coverage." Whatever he proposes, write it down verbatim.

**Anticipated probe:** *Why four categories and not five?* → "We considered separating *Partial* from *Inapplicable* — preferences whose activation conditions explicitly fail vs. partially fail. We collapsed them to keep the clinical output simple. Curious what you'd do."

### 2. Surrogate hierarchy
> "Where does a reasoner output sit relative to the surrogate? When the reasoner returns 'Clear match' and the surrogate disagrees, what should the system's default be — and what should it record in the chart?"

**Listen for:** any reference to the California Probate Code surrogate priority list, AMA Code, or the Stanford Hospital Ethics Committee's standing practice (he co-chairs it).

**Anticipated probe:** *Have you talked to clinical informatics about EHR write-back?* → Honest answer: not yet. We have not designed the EHR integration story; we have designed the reasoner.

### 3. Liability and defensibility
> "If a clinician relies on ADO output and is later second-guessed, what would the system need to produce to be ethically defensible? Is surfacing the patient's `originalText` plus the inference path enough?"

**Listen for:** specific documentation requirements he flags — e.g., timestamp, reasoner version, the activation conditions checked.

### 4. Category error (must-ask — this is the deepest question)
> "Is formalizing preferences as graded, conditional logic a *category error* — does it medicalize what should remain interpretive and relational? The Letter Project deliberately preserves narrative as a response to this concern. Where, in your view, is the line between useful structure and harmful flattening?"

**Listen for:** any framing that distinguishes *administrative* structure (helpful) from *interpretive* structure (problematic). This is likely to be his richest answer. If we only get one paragraph from him in writing, this is the one we want.

**Anticipated probe:** *What about the vague-match category as a response to this critique?* → That is exactly why we built it. Curious whether it goes far enough.

### 5. Documented vs. situational preferences
> "People change their minds when confronted with the actual scenario. Should the system explicitly model this divergence — for example, flag preferences known to be high-divergence — or does that risk paternalism?"

**Listen for:** whether he'd accept a "this kind of preference is statistically unstable" flag, or whether he sees that as overreach.

---

## If we get the meeting (vs. written reply)

If Dr. Magnus offers extended time, three follow-ups in order of priority:

1. **Would he be willing to be acknowledged in the final report?** (Most academics will, but ask.)
2. **Anyone he'd suggest we also talk to?** Specifically: Stanford Hospital ethics committee members, palliative care folks, anyone working on AD reform.
3. **Can we send the final report to him before the June 5 deadline for a sanity check?** Even just to read the section that quotes him.

If he is short on time:
- "We'd be grateful for even a paragraph in reply to question 1 or 4. Thank you."

---

## What to record

Bring two devices:
- Laptop running `demo.py --pause` (terminal full-screen, font ≥ 14pt)
- Phone or second laptop with a Google Doc open titled `Magnus_Notes_2026-05-27.md` — Darren takes verbatim quotes while Patrick drives the conversation

For each question, write down:
- His direct quote (in quotation marks)
- Any specific person/paper/concept he references
- Any disagreement with our framing

These quotes will become the "Expert Review" subsection of Section 5 (Evaluation) in the final report. Verbatim quotes are far more credible than paraphrases.

---

## What to do *after* the meeting (same day)

1. Send a thank-you email within 2 hours — one sentence, no ask.
2. Write up the meeting notes within 24 hours while it's fresh.
3. If he agreed to be acknowledged: add him to the report acknowledgments.
4. Identify any concrete action items (e.g., "rename 'No coverage' to 'AD silent'") and create todos.
5. If he made a specific suggestion that changes the ontology: implement it before the June 1 presentation if at all possible — being able to say "Dr. Magnus suggested X and we implemented it" in the presentation is enormously valuable.

---

## Quick reference — repository contents

| File                                      | What it is                                              |
|-------------------------------------------|---------------------------------------------------------|
| `advanced_directives.owl`                 | Base ontology (67 classes, 22 properties)               |
| `preference_input.py`                     | JSON → populated patient ontology pipeline              |
| `query_evaluation.py`                     | Scenario-based reasoner; 16 vignettes, 16/16 accuracy   |
| `llm_extraction.py`                       | Claude-powered free-text AD → structured JSON pipeline  |
| `demo.py`                                 | This meeting's live demo (6 scenarios)                  |
| `populated_ontologies/ado_jane_doe_001.owl` | Example populated ontology used in the demo           |
| `docs/Magnus_Review_Packet.tex`           | 2-page packet already sent                              |
| `docs/Progress_Report.tex`                | Full May 6 progress report                              |
| `docs/project_pipeline.md`                | Architecture and evaluation plan                        |
