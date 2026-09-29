# Jay Job Matcher — Browser Extension MVP

## Why this form

The browser extension reads the job page that Jay is already viewing.
This avoids a common problem where recruiting sites block external crawlers or search engines.

## User flow

1. Open a job posting in Chrome.
2. Click the Jay Job Matcher icon.
3. Click ANALYZE CURRENT JOB.
4. Extension extracts:
   - page title
   - current URL
   - visible page text
5. Sends it to the local analyzer at:
   http://127.0.0.1:8765/analyze
6. Popup displays:
   - A / B / Discard
   - match score
   - 3–4 strongest fit points
   - main gap
   - company intent context when available
   - recommended action
7. Analyzer saves a markdown report to the HR-agent report history.

## Why not start with paste-a-link only

Some recruiting sites return 403 to external crawlers.
Reading the current browser tab is more reliable because the user can already access the page.

Paste-a-link mode can be added later as a second input.

## Chrome installation during development

1. Open chrome://extensions
2. Turn on Developer mode.
3. Choose Load unpacked.
4. Select this browser-extension directory.
5. Pin Jay Job Matcher to the toolbar.

The extension UI is already scaffolded.
It needs the local analyzer service described in ../local_analyzer_contract.md.
