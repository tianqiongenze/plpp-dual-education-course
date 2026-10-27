#!/usr/bin/env bash
# 全部 md → word/ + pdf/ (pandoc gfm→docx; docx→pdf 经 LibreOffice, 中文经 Noto/苹方回退)
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$ROOT/word" "$ROOT/pdf"
n=0
while IFS= read -r f; do
  rel="${f#$ROOT/}"; base=$(basename "$f" .md)
  safe=$(echo "$rel" | sed 's#/#__#g; s#\.md$##')
  pandoc -f gfm -t docx --toc-depth=2 -o "$ROOT/word/${safe}.docx" "$f" 2>/dev/null || { echo "docx FAIL: $rel"; continue; }
  soffice --headless --convert-to pdf --outdir "$ROOT/pdf" "$ROOT/word/${safe}.docx" >/dev/null 2>&1 || echo "pdf FAIL: $rel"
  n=$((n+1))
done < <(find "$ROOT" -name "*.md" -not -path "$ROOT/word/*" -not -path "$ROOT/pdf/*" -not -path "*/project-references/*" | sort)
echo "converted: $n md files"
