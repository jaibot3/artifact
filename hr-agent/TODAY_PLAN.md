# TODAY PLAN

## Priority 1 — Lock the profile evidence
1. Re-read career.html and all portfolio detail pages.
2. Extract only verified capabilities.
3. Map every capability to at least one project.
4. Mark unsupported claims as prohibited.
5. Save the final profile in profile_schema.json.

Deliverable:
- profile_schema.json

## Priority 2 — Lock the job-language translation layer
1. List portfolio-native phrases.
2. Translate each into common Korean/English JD language.
3. Add synonyms without changing meaning.
4. Separate strong translations from weak/ambiguous translations.
5. Save in matching_rules.md.

Deliverable:
- matching_rules.md

## Priority 3 — Define A/B grading
1. Capability Fit = 40
2. Role Transferability = 25
3. Environment Fit = 20
4. Gap / Cost = 15
5. 80+ = A
6. 70–79 = B
7. Below 70 = discard
8. Fatal must-have gaps override score.

Deliverable:
- matching_rules.md

## Priority 4 — Build JobKorea collector
1. Search broad job families, not exact titles only.
2. Capture:
   - company
   - role
   - JD full text
   - requirements
   - preferred
   - location
   - experience level
   - posting date
   - deadline
   - URL
3. Deduplicate by company + title + URL.
4. Save raw jobs before scoring.

Suggested storage:
- data/jobs_raw/YYYY-MM-DD.json

## Priority 5 — Build JD parser
For each job:
1. Responsibilities
2. Must-haves
3. Preferred qualifications
4. Tools
5. Domain
6. Seniority
7. Collaboration structure
8. Ownership level
9. 0→1 vs maintenance
10. Red flags / fatal gaps

Suggested storage:
- data/jobs_parsed/YYYY-MM-DD.json

## Priority 6 — Build matcher
For each parsed JD:
1. Compare capabilities.
2. Compare transferable evidence.
3. Compare working environment.
4. Identify gaps.
5. Produce score.
6. Attach 3–4 strongest evidence links.
7. Assign A/B/discard.

Suggested storage:
- data/jobs_scored/YYYY-MM-DD.json

## Priority 7 — Build Company Intent Agent
For jobs scoring 70+ only:
1. Open official company website.
2. Read relevant product/service pages.
3. Read official newsroom/careers/IR when available.
4. Search recent credible news.
5. Identify current company movement.
6. Infer why this opening may exist.
7. Label inference confidence.
8. Feed context back to matcher.

Important:
Do NOT research every scraped job.
Research only 70+ jobs to control time and noise.

Suggested storage:
- data/company_context/YYYY-MM-DD.json

## Priority 8 — Re-rank after company context
1. Do not replace original score blindly.
2. Adjust confidence, not facts.
3. Promote jobs where company context strengthens evidence.
4. Demote jobs where the actual business need conflicts with the profile.

## Priority 9 — Generate daily shortlist
1. A Grade first.
2. B Grade second.
3. 3–4 fit reasons each.
4. Main gap each.
5. Hiring-intent note each.
6. Keep daily list concise.

Target:
- A Grade: all legitimate matches
- B Grade: practical backup + stretch roles
- Do not impose an arbitrary small count if the market gives more viable roles.
- Still sort by priority.

Deliverable:
- reports/YYYY-MM-DD.md

## Priority 10 — Feedback loop
After review, mark:
- APPLY
- DISMISS
- SAVE
- INTERVIEW
- REJECTED

For DISMISS, capture reason:
- title
- salary
- location
- company
- work type
- role too narrow
- role too technical
- role too junior
- role too senior
- not interested
- other

Use repeated dismiss reasons to refine preferences, but do not overwrite capability evidence.

## End-of-day success condition

Today is successful if:
1. One real JobKorea JD travels through the entire pipeline.
2. The system outputs a defensible A/B/discard result.
3. Every fit reason points to actual portfolio evidence.
4. Company Intent Agent adds useful context without inventing motive.
5. The output is reusable tomorrow.
