#!/usr/bin/env bash
# Builds the client proposal PDF.
# Requires: texlive-latex-base, texlive-latex-recommended, texlive-latex-extra,
#           texlive-fonts-recommended, texlive-fonts-extra
set -euo pipefail
cd "$(dirname "$0")"

OUT="Enterprise-Food-Delivery-Platform-Proposal.pdf"

# Three passes: content, then table of contents, then page cross-references.
for pass in 1 2 3; do
  pdflatex -interaction=nonstopmode -halt-on-error proposal.tex > "build-${pass}.log"
done

cp proposal.pdf "$OUT"
rm -f proposal.aux proposal.toc proposal.out proposal.log proposal.pdf build-*.log
echo "Built: $OUT"
