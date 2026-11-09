---
name: addons-paper
description: "Review and refine the python-addons mathematical paper in docs/addons/logical/main.lyx, including notation, foundational references, and illustrative protocol contracts. Use for this paper's drafting and editorial decisions, not ordinary library implementation work."
---

# Addons Paper

## Context

Work in the `python-addons` repository. Read
`docs/addons/logical/EDITORIAL.md` for settled choices, open questions, reference
recommendations, and listing conventions. Read the current `main.lyx` before
reviewing or editing; the manuscript has been substantially rewritten and old
conversation descriptions may no longer describe it. If the record is absent,
ask for its location rather than reconstructing decisions from guesses.

## Editorial approach

- Write for a mathematically knowledgeable reader: concentrated prose and
  purposeful notation, without repeating a formula in several verbal forms.
- Distinguish the mathematical carrier and laws from its representation and
  implementation requirements. A programming motivation does not require code
  in the mathematical argument.
- Check domains, codomains, quantifier scopes, ambient sets, and the laws actually
  asserted. Distinguish a definition from a consequence or a representation
  convention. Correctness takes precedence over shortening a statement.
- Ground reference recommendations in the actual relevant sections of primary
  sources. Use a consistent principal reference where appropriate, while marking
  project-specific conventions and claims that need separate sources. Do not
  turn a recommended book into an adopted reference without the author's choice.
- Code presence and placement remain open until the author decides. If code is
  requested, use illustrative `typing.Protocol` contracts and qualified `typing`
  names; keep representation and coercion machinery out of those illustrations
  unless it is the subject under discussion. Signatures do not prove laws.

## Scope and preservation

For review requests, report findings without rewriting the manuscript. For edit
requests, keep the patch scoped to the agreed passage or convention. Paper work
does not authorize changing library code or synchronizing the draft with it.

Preserve LyX structure, the custom listing preamble, intentional whitespace,
and existing formatting outside the requested change. Follow the editorial
record's distinction between display and inline listing sizes. Check changed
formulas and cross-references; render when a change affects visual layout, and
do not claim visual verification without inspecting the result.

Record new explicit decisions in `EDITORIAL.md`. Label proposals and unresolved
alternatives separately. Do not populate `main.bib` merely because a source was
consulted during review; add bibliography entries when requested or when doing
an agreed citation edit.
