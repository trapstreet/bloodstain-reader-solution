# /// script
# requires-python = ">=3.11"
# dependencies = ["anthropic>=0.40"]
# ///
"""Bloodstain Reader solution — closed-book forensic vision.

Per case, trap pipes us a manifest pointing at inputs/<case>/ containing:
  - document.jpg   the bloodstain pattern (physical evidence)
  - question.txt   a hypothetical suspect statement + the ask

We send BOTH to a Claude vision model and ask for a one-word verdict —
"supports", "contradicts", or "fails" — reasoning ONLY from what is
visible in the pattern. The judge checks the leading word + no-hedge.
"""
from __future__ import annotations

import base64
import json
import os
import re
from pathlib import Path

import anthropic

MODEL = os.environ.get("CLAUDE_MODEL", "claude-opus-4-8")

manifest = json.loads(os.environ["TRAP_MANIFEST"])
inputs = Path(manifest["inputs_dir"])
question = (inputs / "question.txt").read_text().strip()
image_b64 = base64.standard_b64encode((inputs / "document.jpg").read_bytes()).decode()

client = anthropic.Anthropic()
msg = client.messages.create(
    model=MODEL,
    max_tokens=16,
    system=(
        "You are a forensic bloodstain-pattern analyst. Judge the suspect "
        "statement ONLY against what is physically visible in the pattern — "
        "number of impact events, spatter range/energy, directionality, "
        "distribution, and substrate. If the statement concerns something "
        "the blood evidence cannot speak to (timing, motive, relationships, "
        "drinking, lighting, aftermath actions), the verdict is 'fails'. "
        "Answer with EXACTLY one word: supports, contradicts, or fails."
    ),
    messages=[{
        "role": "user",
        "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_b64}},
            {"type": "text", "text": question},
        ],
    }],
)
text = "".join(b.text for b in msg.content if b.type == "text")
word = (re.search(r"[a-zA-Z]+", text) or [None]) and re.search(r"[a-zA-Z]+", text).group(0).lower()
print(word or text.strip())
