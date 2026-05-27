#!/bin/bash
# ─── SentinelBrief Submission Packager ───
# Creates a clean zip for Devpost upload, excluding dev artifacts.

set -e

OUTFILE="SentinelBrief_Submission.zip"

echo "📦 Packaging SentinelBrief for submission..."

# Remove previous archive
rm -f "$OUTFILE"

# Create zip excluding dev/build artifacts
zip -r "$OUTFILE" . \
  -x "*.DS_Store" \
  -x "__pycache__/*" \
  -x "*.pyc" \
  -x "node_modules/*" \
  -x "frontend/node_modules/*" \
  -x ".env" \
  -x "venv/*" \
  -x ".git/*" \
  -x "dist/*" \
  -x "frontend/dist/*" \
  -x "*.zip"

SIZE=$(du -sh "$OUTFILE" | cut -f1)
echo ""
echo "✅ Submission ready: $OUTFILE ($SIZE)"
echo "   Upload this file to Devpost."
