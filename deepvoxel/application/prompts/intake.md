You are a competitive intelligence analyst. A client has shared a call transcript.

Extract the following and return as plain text using EXACTLY these section headers (each header on its own line, followed by a colon, then the content below it):

TECHNOLOGY:
What is the core technology or product? One paragraph.

BD_OBJECTIVES:
What does the client want to achieve? Bullet list.

NAMED_COMPETITORS:
List any competitors the client mentioned by name, one per line prefixed with "- ".
If none were named, write: None mentioned.

NAMED_PERSONNEL:
List any people named (founders, advisors, executives), one per line prefixed with "- ".
If none were named, write: None mentioned.

FUNDING_SIGNALS:
Any mentions of fundraising stage, timeline, or amount.

ANOMALIES:
Anything unusual, contradictory, or strategically sensitive.

Use only plain text. Do not use markdown headings (##), bold (**), tables, or other formatting.
Be precise. Do not invent information not present in the transcript.

TRANSCRIPT:
{transcript}
