---
name: comment
description: Generate a concise, structured change comment (summary, what/why, bullet changes, accomplishment).
---

You generate a single change comment using the template below.

Rules

- Output ONLY the final comment. Do not include these instructions.
- Keep it concise and concrete; emphasize intent (why) over mechanics.
- If tests exist, do not mention test-only changes in the bullet list.
- Use present tense, active voice.

Output format (exact structure)

1. One line summary of the change.

2. 1-2 lines summarizing what changed and why.

3. A bullet list (use '-' bullets) of the substantive changes being made and why each is being made. Skip test-only items.

4. 1-2 freeform lines summarizing what has been accomplished.
