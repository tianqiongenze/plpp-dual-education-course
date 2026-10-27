#!/usr/bin/env bash
# 同步 PLPP 项目最新文档到课程仓 project-references/<date>/
# 用法: ./tools/sync-from-plpp.sh [PLPP本地路径] (默认 ../personalized-learning-platform-plus)
set -euo pipefail
COURSE_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLPP="${1:-$COURSE_ROOT/../personalized-learning-platform-plus}"
[ -d "$PLPP" ] || { echo "PLPP repo not found: $PLPP"; exit 1; }
DATE=$(date +%Y-%m-%d)
STAGE=$(grep -oE "^## 阶段[0-9]+" "$PLPP/PROGRESS.md" | tail -1 | grep -oE "[0-9]+")
DEST="$COURSE_ROOT/project-references/$DATE-stage$STAGE"
mkdir -p "$DEST"
cp "$PLPP/PROGRESS.md" "$DEST/" 2>/dev/null || true
for f in AUDIT_DOC_VS_CODE_2026-10-24.md PERFORMANCE_TEST_REPORT.md \
         DEPLOYMENT_OPERATIONS_MANUAL.md MANUAL_TESTING_GUIDE.md \
         100K_ZERO_FAILURE_TEST_REPORT.md; do
  [ -f "$PLPP/docs/$f" ] && cp "$PLPP/docs/$f" "$DEST/"
done
echo "[sync] copied -> $DEST"
echo "[sync] PLPP stage: $STAGE (course docs base: check 07-项目对接与同步/项目对接与同步机制.md §6)"
echo "[sync] TODO: 人工复核情境/任务单是否需要重渲染: python tools/generate.py"
