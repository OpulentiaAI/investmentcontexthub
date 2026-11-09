# Diego Workbook Evidence

## Mailbox scope

Two emails from Diego Waelter were found in Outlook:

- `Initial ICP Pass`, received 2026-07-23, with `All_Opulentia_Connections.xlsx` and `Opulentia_ICP_Connections_V1.xlsx`.
- `ICP List`, received 2026-07-30, with `26-0730_Opulentia_Connections_List.xlsx`.

The first email says the combined network was color-coded by owner, filtered to an ICP set, and still contained flagged or incomplete companies. The second says the refined workbook contains about 135 ICP contacts and 28 Jeremy connections with personalized LinkedIn messages.

## PII-safe workbook profile

The raw workbooks remain outside this skill. This reference includes only aggregates and operating implications.

### Network export

- 4,366 populated table rows; 4,245 rows have person names and 4,194 unique LinkedIn URLs.
- Only 77 rows have email addresses.
- 2,123 rows are flagged for unresolved industry or ICP classification.
- 1,232 are explicitly non-ICP.
- Ownership is described in email as cell color, while the textual owner column is largely empty. Ownership must be normalized into data before automation.

### Filtered ICP workbook

- 336 ICP contacts.
- Segment mix: 170 financial services, 130 consulting, 17 manufacturing, 13 private equity, and 6 tax and accounting.
- 333 unique LinkedIn URLs, 7 email addresses, and 333 personalized LinkedIn messages.
- Use cases are mapped one-to-one by segment in this version, so fit should be revalidated at the account level.

### Refined connection workbook

- 135 master ICP contacts and 28 Jeremy ICP connections.
- Master list segment mix: 60 financial services, 34 consulting, 12 manufacturing, 7 legal, 6 professional services, 6 insurance, 4 tax and accounting, 4 venture capital, and 2 private equity.
- Top use cases: 34 deal-flow triage and screening, 25 data analysis as an agent-run workflow, 11 contract termination review, and 11 portfolio intelligence automation.
- The 28 warm connections include 28 distinct LinkedIn messages and are the recommended first pilot cohort.

## Diego's process notes

- Mapping Opulent use cases to ICP contacts required two prompts and was medium difficulty.
- Industry classification and flagged-company enrichment required four prompts and was hard; generic company names remained untagged even after Fortune 1000 context was supplied.
- Decision-maker filtering required two prompts and was medium difficulty.
- Warm LinkedIn message creation required one prompt and was easy.

## Strategy implications

1. The bottleneck is company identity and evidence-backed classification, not message generation.
2. The account ladder should be: 28 warm connections -> 135 refined ICP contacts -> 336 filtered ICP contacts -> 4,245 named raw contacts.
3. Do not enrich every raw contact. Resolve and enrich only accounts that pass fit, signal, and owner gates.
4. Prioritize financial services and consulting because they dominate the refined list, but select the wedge by proof and access rather than volume alone.
5. Preserve Diego's messages as research inputs; revalidate their signal and sender voice before use.
