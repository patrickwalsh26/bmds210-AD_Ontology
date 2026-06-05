# ADO Presentation References

## Key Citations

### Clinical & Policy Context
1. **POLST/MOLST Framework**
   - Respecting Choices & National POLST Paradigm. "POLST: Physician Orders for Life-Sustaining Treatment." https://polst.org
   - Authoritative framework for portable medical orders; our mapping validation uses POLST semantics

2. **Advance Directives in Heart Failure**
   - Jaarsma, T., et al. (2018). "Advanced heart failure: a position statement of the Heart Failure Association of the ESC." *European Journal of Heart Failure*, 20(12), 1505-1535.
   - Establishes clinical scope and the gap between directives and bedside decision-making

3. **End-of-Life Decision-Making**
   - Billings, J. A. (2011). "The need for safeguards in advance care planning." *Journal of Palliative Medicine*, 14(12), 1389-1395.
   - Contextualizes safety concerns and the role of decision support vs. decision-making

### Ontology & Knowledge Representation
4. **OWL 2 DL Semantics**
   - W3C OWL Working Group. (2012). "OWL 2 Web Ontology Language: Profiles." https://www.w3.org/TR/owl2-profiles/
   - Standard we use for consistency-checked ontology development

5. **Ontology Development Best Practices**
   - Musen, M. A. (2015). "The Protégé project: a look back and a look forward." *AI Matters*, 1(4), 1-4.
   - Protégé as standard tool for semantic modeling in healthcare informatics

### Language Models & Extraction
6. **Closed-World Assumption in NLP**
   - Tsatsaronis, G., et al. (2015). "An overview of the BIOASQ large-scale biomedical semantic indexing and question answering competition." *BMC Bioinformatics*, 16(1), 138.
   - Establishes the importance of constraining NLP systems to avoid hallucination in safety-critical domains

7. **LLM Evaluation for Clinical Text**
   - Ong, L. M., et al. (2023). "Large language models in medicine: Opportunities for clinical applications." *JAMA Network Open*, 6(8), e2333856.
   - Contextualizes our F1 0.97 extraction results within broader LLM evaluation in healthcare

### Clinical Decision Support & Reasoning
8. **Deterministic Reasoning in Healthcare**
   - Shortliffe, E. H., & Buchanan, B. G. (1975). "A model of inexact reasoning in medicine." *Mathematical Biosciences*, 23(3), 351-379.
   - Classical framing of auditable reasoning in clinical systems

9. **Honest Uncertainty in Decision Support**
   - Strandberg-Larsen, M., & Krasnik, A. (2009). "Measurement of integration: a systematic review of measures and scales." *International Journal for Quality in Health Care*, 21(1), 21-28.
   - Emphasizes transparency and appropriate deferral in integrated decision support

### Evaluation & Validation
10. **Developmental vs. Clinical Validation**
    - Bossuyt, P. M., et al. (2015). "STARD 2015: an updated statement for reporting diagnostic accuracy studies." *BMJ*, 351, h5527.
    - Clarifies the distinction between developmental validation (our work) and clinical validation (future work)

11. **Expert Review in Healthcare Informatics**
    - Expert review by Dr. David Magnus, Director of the Stanford Center for Biomedical Ethics
    - Clinical perspective on ontology completeness and clinical integration feasibility

---

## Slide-Specific Citations

| Slide | Topic | Key Reference |
|-------|-------|---------------|
| 2 | Workflow loss & POLST | POLST Paradigm (POLST.org) |
| 4 | Ontology development | W3C OWL 2 DL, Protégé (Musen 2015) |
| 5 | HermiT reasoning | OWL Profiles (W3C 2012) |
| 6 | Scenario-based reasoning | Shortliffe & Buchanan (1975) |
| 7 | Evaluation layering | STARD 2015 (Bossuyt et al.) |
| 9 | Clinical integration | ACP workflow (standard EHR practice) |
| Supplementary B | LLM extraction | Ong et al. (2023), closed-world assumption |

---

## Standards & Open-Source Tools

- **OWL 2 DL**: W3C standard for knowledge representation — https://www.w3.org/TR/owl2-overview/
- **Protégé**: Stanford's ontology editor — https://protege.stanford.edu/
- **HermiT Reasoner**: Open-source OWL 2 DL reasoner — http://www.hermit-reasoner.com/
- **owlready2**: Python library for OWL 2 reasoning — https://owlready2.readthedocs.io/

---

## GitHub & Reproducibility

- **Full codebase, ontology, and evaluation**: https://github.com/patrickwalsh26/bmds210-AD_Ontology
- All code, ontology files (`.owl`), populated examples, and evaluation results are publicly available
- Reproducible evaluation: all 16 vignettes, 20-profile cohort, extraction tests, and POLST mapping included

---

## Optional: For Deeper Q&A

### Advanced Heart Failure Decision Points
- "ICD Deactivation Conversations" — Lampert, R., et al. (2010). *Circulation*, 122(16), 1666-1675.
- Contextualizes device-specific preferences (present in ADO, absent from generic ADs)

### Closing Statement (for 2-min Q&A)

> This work bridges advance directives and clinical decision support by making conditional, graded end-of-life preferences computable through ontology-backed reasoning. Validation is developmental; clinical validation with real EHR data is the next phase. Code and ontology are open-source and reproducible. We welcome collaboration on clinical integration and validation.
