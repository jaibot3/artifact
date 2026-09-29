# Matching Rules

## Objective

Find JobKorea openings that are realistically actionable, not merely ideal.

Only keep jobs with a total match score of 70 or above.

## Score

### 1. Capability Fit — 40
How much of the actual work can be supported by portfolio/career evidence?

### 2. Role Transferability — 25
Can existing evidence transfer into the role even if the user never held the exact title?

### 3. Environment Fit — 20
Does the role reward cross-functional ownership, 0→1 work, external collaboration, creative + execution integration?

### 4. Gap / Cost — 15
How serious are missing must-haves?
Preferred qualifications should not be treated like must-haves.

## Grade

A Grade:
- 80+
- 3 or more strong evidence links
- no fatal must-have gap

B Grade:
- 70–79
- 2 or more relevant evidence links
- reasonable gap allowed
- include pragmatic and stretch applications

## Fatal gaps

Examples:
- mandatory legal license/certification not held
- advanced technical requirement that is central to the job and unsupported
- mandatory years of a very specific regulated/technical function
- language requirement clearly above demonstrated level
- explicit location/work authorization constraint that cannot be met

## Non-fatal gaps

Examples:
- exact industry not previously worked in
- preferred software
- preferred title history
- preferred sector exposure
- preferred MBA / graduate degree
- preferred years when actual capability evidence is strong

## Translation Ontology

Portfolio language -> JD language

Artist Coordination
- stakeholder management
- talent management
- external partner coordination
- project coordination
- cross-functional collaboration

Creative Direction
- brand direction
- campaign development
- creative strategy
- concept development
- visual direction
- content strategy

Production Management
- vendor management
- project delivery
- production planning
- execution management
- supply coordination
- operations

Government-supported proposal -> selection
- business planning
- proposal development
- new business
- public-sector project
- grant project management
- project acquisition

Wholesale / department store negotiation
- B2B sales
- account development
- channel development
- commercial negotiation
- retail partnership

Website build communication
- digital project management
- developer coordination
- web production
- digital experience delivery
- cross-functional delivery

Customer journey case study
- UX strategy
- service design thinking
- customer experience
- journey mapping
- digital strategy
- product/portal structure

## Output rule

For every retained job, return only the 3–4 strongest match points.
Do not dump every possible similarity.

Each point must use this structure:

JD requirement
→ matched capability
→ evidence

Example:
"유관부서 및 외부 파트너 협업"
→ Stakeholder / external partner management
→ AOLADO: external designer, manufacturer, website developer, department-store buyer coordination

## Calibration rule

Never award high scores for vague words like:
- communication
- creativity
- passion
- trend sensitivity

Score only when evidence is concrete.


## Core-role vs eligibility-filter rule

Do not treat every item under "Requirements" as equally important to job fit.

Classify each JD condition into one of four types:

1. CORE WORK
- Tasks the person will actually perform repeatedly.
- These drive Capability Fit and Transferability.

2. HARD ELIGIBILITY
- Legal, licensing, language, work authorization, or truly mandatory technical constraints.
- These may create a fatal gap.

3. BACKGROUND FILTER
- Industry years, prior sector exposure, preferred employer type, or broad experience requirements.
- These affect confidence, but should not dominate the score if the actual work maps strongly.

4. PREFERENCE
- Nice-to-have tools, degrees, sector familiarity, stylistic preferences.
- Minor impact only.

### Important example

"2+ years of fashion retail industry-related experience"

Do NOT automatically interpret this as:
- retail operations expertise required
- store management expertise required
- merchandising expertise required

First inspect the full JD.

If the actual responsibilities are concept planning, collaboration, research, brand direction, content, product planning, or cross-functional project work, then "fashion retail industry experience" is primarily a background/industry-context filter unless the JD repeatedly asks for retail operations-specific work.

### Candidate-specific evidence

Jay has verified fashion/retail-adjacent evidence:
- Founder & Creative Director of fashion brand SAKK
- Department-store wholesale sales and negotiation through AOLADO
- Retail channel / commercial negotiation exposure
- Product development and manufacturing coordination
- Fashion styling and brand collaboration projects

Therefore, a "fashion retail industry experience" requirement should not be scored as an unmet requirement by default.

### Scoring consequence

- CORE WORK mismatch: meaningful penalty.
- HARD ELIGIBILITY mismatch: severe or fatal penalty.
- BACKGROUND FILTER mismatch: small penalty only, and no penalty if equivalent industry-context evidence exists.
- PREFERENCE mismatch: minimal penalty.

Before penalizing any requirement, the model must explain what type it is and why.


## JD Structural Reading — Salience Before Keywords

The matcher must read the JD as a structured document, not as a bag of keywords.

Before scoring, identify:

### A. Primary hiring intent
What problem is this role mainly expected to solve?
Infer from the combination of:
- repeated responsibilities
- first-listed responsibilities
- section headings
- phrases tied to ownership such as "lead", "own", "drive", "plan", "develop"
- output/deliverable language
- collaboration targets
- portfolio / assignment / submission requirements
- repeated domain references
- unusually specific requirements

### B. Subtasks
Break the job into 3–6 subtasks.
For each subtask, estimate weight:

- CRITICAL: central to the role
- HIGH: repeated or clearly tied to expected output
- MEDIUM: supporting responsibility
- LOW: incidental / occasional

Do not give equal weight to all JD bullets.

### C. Salience signals

Increase weight when:
- the same responsibility appears in multiple sections
- similar wording is repeated
- the item appears near the top of responsibilities
- the company asks for a dedicated portfolio / assignment / work sample for it
- the company describes a concrete output connected to it
- the wording uses ownership verbs
- the requirement is unusually specific compared with generic bullets
- the qualification section repeats the same capability implied by responsibilities

Decrease weight when:
- the phrase is generic HR boilerplate
- it appears only once in a broad qualification line
- it is a background filter not reflected in actual responsibilities
- it is listed as preferred only
- it is a vague trait such as passion, communication, trend sensitivity

### D. Submission requirements are strong evidence of what the company values

If the JD asks for special materials beyond resume/CV, parse them separately.

Examples:
- portfolio
- project description
- writing sample
- assignment
- case study
- concept proposal
- work sample
- specific portfolio category
- mandatory links
- specific project count
- role-specific portfolio instructions

Treat this as a high-salience signal.

Example:
If a JD asks for:
"Portfolio including concept planning process"
then concept planning should receive substantially more weight than a generic industry-years requirement.

### E. Deliverable inference

Ask:
"What would this person probably have to produce in the first 3–6 months?"

Possible outputs:
- concepts
- campaign plans
- collection directions
- project roadmaps
- partnership proposals
- visual guidelines
- content systems
- product plans
- research decks
- operational processes

Then compare those likely outputs to Jay's evidence.

### F. Requirement interpretation rule

A requirement should NOT be penalized merely because its wording does not appear in the portfolio.

Instead:
1. identify the underlying task,
2. identify its importance in the JD,
3. identify equivalent portfolio evidence,
4. then score.

### G. Contradiction rule

If a qualification appears important linguistically but the actual responsibilities do not support it, downgrade its importance.

Example:
"2+ years fashion retail industry experience"
but responsibilities focus on:
- collection concept planning
- cultural research
- collaboration planning
- creative direction

Interpret "fashion retail" primarily as industry-context background unless retail operations repeatedly appear elsewhere.

### H. Required structured extraction before scoring

For every JD, first produce:

- primary_hiring_intent
- weighted_subtasks
- repeated_signals
- high_salience_phrases
- special_submission_requirements
- likely_first_6_month_outputs
- background_filters
- hard_eligibility
- preferences

Only after this step should the matcher calculate fit.
