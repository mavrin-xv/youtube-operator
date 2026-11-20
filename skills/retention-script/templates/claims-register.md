# Claims register: <video>

Every factual sentence and every number shown or said gets a row. No row means the claim is cut or reworded.
Tag the sentence in the script with its id, like `[c1]`. `script_lint.py --claims` blocks tags with no row.

Types: measurement (we tested it), reference value (a published source), our case, method, model, illustration.

| id | exact wording | type | source or test | date | conditions and limits | on screen |
|---|---|---|---|---|---|---|
| c1 | | | | | | |
| c2 | | | | | | |

Rules:
- Measurements state their method on screen or in the description.
- Illustrative numbers are labelled or obviously illustrative.
- A source older than a year gets checked again before recording.
