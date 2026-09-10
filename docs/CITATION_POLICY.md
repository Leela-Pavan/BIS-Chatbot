# BIS Sahayak Citation Policy

## Purpose

Citations let a user inspect why an answer was produced. A citation is an evidence pointer, not decorative metadata. The interface must distinguish `AI Explanation` from `Source Evidence`.

## Required Citation Fields

When available, an evidence card should show:

- document title and document ID
- standard number and title
- clause or section
- page number
- relevant excerpt
- document version/publication date
- official BIS source URL
- retrieval/freshness indicator

Unknown values remain unknown and are not replaced with guesses.

## Citation Lifecycle

1. Retrieval returns evidence chunks with stable IDs and provenance.
2. The answer generator receives only those chunks and their verified metadata.
3. The generator emits citation IDs or structured citation candidates.
4. The citation validator resolves each ID to stored evidence.
5. The validator checks document, page, clause, URL, and excerpt membership.
6. Unsupported or mismatched citations are removed from the user response and logged.
7. The UI links the surviving citation to the Evidence Viewer.

The validator must not accept a citation merely because the fields look plausible.

## Claim Coverage

Material claims such as applicable standards, certification status, test requirements, laboratory capabilities, and mandatory/voluntary language require supporting evidence. Explanatory connective text may be generated, but it must not introduce new factual claims. The response should expose warnings when a claim is conditional or when supporting evidence is incomplete.

## Evidence Viewer

Selecting a citation opens a structured view:

```text
Document -> Standard -> Clause/Section -> Page -> Excerpt -> Official source
```

The viewer must show the exact stored excerpt and provide the source URL. If the document has been superseded, show the version/date relationship and avoid presenting a historical citation as current without qualification.

## Confidence and Sufficiency

Confidence describes the answer's evidence quality, not model certainty. `High`, `medium`, and `low` values must be derived from retrieval, source authority, agreement, freshness, and citation coverage. `evidence_sufficient=false` takes precedence over a confidence label and requires a safe response or clarification.

## Prohibited Claims

The system must never invent or autocomplete:

- BIS standard numbers or titles
- clause or page numbers
- document names or URLs
- certification schemes or mandatory status
- laboratory names, contacts, accreditation, or capabilities
- evidence excerpts

If the knowledge base cannot verify a claim, say so plainly and point to the closest verified source or required clarification.

## Auditing

Record citation-validation outcomes, evidence IDs, prompt/model versions, and policy decisions in protected application logs. Do not log secrets or unnecessary personal data. Evaluation should measure citation support separately from answer fluency.
