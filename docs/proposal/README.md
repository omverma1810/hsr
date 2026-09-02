# Client Proposal — Enterprise Food Delivery & Operations Platform

LaTeX source for the commercial proposal and statement of work issued to the
London-based client for the multi-role food delivery, inventory and operations platform.

## Files

| File | Purpose |
|---|---|
| `proposal.tex` | Document body — all content lives here |
| `preamble.tex` | Brand palette, typography, table styles and callout boxes |
| `build.sh` | Builds the client-facing PDF |
| `Enterprise-Food-Delivery-Platform-Proposal.pdf` | The deliverable sent to the client |

## Building

```bash
./build.sh
```

Requires a TeX Live installation:

```bash
sudo apt-get install -y --no-install-recommends \
  texlive-latex-base texlive-latex-recommended texlive-latex-extra \
  texlive-fonts-recommended texlive-fonts-extra
```

The script runs `pdflatex` three times — once for content, once to resolve the table
of contents, and once for the `lastpage` page-count references in the footer — then
cleans up the intermediate files.

## Document structure

1. Executive Summary
2. Project Confirmation — scope as understood
3. The Commercial Case — marketplace commission comparison
4. Return on Investment — scenarios, payback, and the limits of the model
5. Plain-English walkthrough of the platform
6. Roles and Access Control — 13 roles
7. Feature & Requirements Specification — 15 modules, individually referenced (`FR-NN-NN`)
8. Technology Foundation
9. Project Plan & 45-Day Timeline
10. Quality Assurance, Testing & Acceptance
11. What We Need From You
12. Commercials & Payment Terms
13. Out of Scope — Chargeable Items
14. Assumptions, Dependencies & Risk Register
15. Support & Service Levels
16. Change Control Procedure
17. Acceptance & Sign-Off
18. Delivery Team

## Editing notes

- Every requirement carries a stable ID (`FR-07-04`). Keep these stable across
  revisions — they are referenced in acceptance testing and change requests.
- ROI figures in Section 4 are derived from the assumptions table in Section 4.1.
  If you change the AOV, the migration percentage or the commission rates, recompute
  every dependent figure in Sections 4.2 and 4.3 — they are hard-coded, not calculated.
- Bump the version and issue date in the Document Control table before re-issuing.
