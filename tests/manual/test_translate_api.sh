#!/bin/bash
set -e

# Default values
SRT_SIZE=${1:-"medium"}
TARGET_LANG=${2:-"Vietnamese"}
PORT=5100
MODE="fast"
# Validate SRT size
if [[ ! "$SRT_SIZE" =~ ^(short|medium|long)$ ]]; then
  echo "Error: SRT size must be 'short', 'medium', or 'long'"
  exit 1
fi

# Input and output file names
INPUT_FILE="tests/samples/${SRT_SIZE}.srt"
OUTPUT_FILE="${SRT_SIZE}_${TARGET_LANG}.srt"

# Test file upload and translation
echo "Testing file upload and translation..."
echo "Using ${INPUT_FILE} to translate to ${TARGET_LANG}..."
curl -X POST http://localhost:$PORT/translate \
  -F "file=@${INPUT_FILE}" \
  -F "target_lang=${TARGET_LANG}" \
  -F "speed_mode=${MODE}" \
  -o "${OUTPUT_FILE}"

echo "Check ${OUTPUT_FILE} for the translation output"