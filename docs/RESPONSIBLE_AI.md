# BIS Sahayak Responsible AI

## User Promise

BIS Sahayak helps users navigate official BIS information; it does not replace BIS, legal, regulatory, engineering, or conformity-assessment advice. The product must make that boundary visible at the point of use, especially for certification and mandatory-status questions.

## Evidence-First Behavior

- Retrieve before generating.
- Use only approved, traceable sources for BIS claims.
- Preserve page and clause context.
- Separate source evidence from AI explanation.
- State unknowns and missing product attributes.
- Refuse or ask for clarification when evidence is insufficient.
- Never treat model memory as a source.

## High-Risk Misinterpretations

Users may act on incorrect certification, safety, testing, or laboratory guidance. The system must avoid categorical claims unless authoritative evidence supports them. Certification status should be represented as mandatory, voluntary, conditional, or not verified. Laboratory results must be limited to current verified records and matched to the requested standard, test, and location.

## Language and Accessibility

English, Hindi, and Telugu responses should preserve technical identifiers, standard numbers, clauses, and official terminology. Translated explanations must not be presented as translated source evidence unless an official translation exists. The UI should support keyboard navigation, readable contrast, responsive layouts, accessible labels, and direct access to evidence.

## Security and Privacy

- Keep secrets in server-side environment configuration.
- Validate input size and content.
- Apply rate limits and abuse controls.
- Restrict crawler URLs to approved domains and safe redirect targets.
- Configure CORS narrowly in production.
- Avoid SSRF through user-controlled fetches.
- Redact secrets and unnecessary personal data from logs.
- Use database constraints and least-privilege credentials.
- Keep provider calls behind backend adapters.

## Model and Provider Governance

Record provider/model identifiers, prompt versions, retrieval configuration, and evaluation dataset versions for reproducibility. Review provider data-retention and regional processing terms before sending user queries. A provider outage must degrade to a controlled error or evidence-only response, never to ungrounded generation.

## Human Oversight

Provide a feedback path for incorrect, stale, or unsafe answers. Ingestion failures, citation mismatches, conflicts, and user reports should be reviewable by maintainers. High-impact updates to source policy, mandatory-status rules, or answer prompts require review and regression tests.

## Evaluation and Monitoring

Measure retrieval quality, citation support, refusal quality, multilingual fidelity, latency, and service errors on versioned datasets. Do not publish unmeasured accuracy or confidence claims. Monitor freshness, source failures, unsupported-query rates, citation validation failures, and provider costs.

## Known Limitations

The system can only reflect the approved BIS knowledge base and its freshness. It may not contain every current BIS publication or government notification. It must communicate that limitation rather than implying comprehensive authority.
