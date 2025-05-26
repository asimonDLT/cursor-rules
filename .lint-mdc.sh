#!/bin/bash
# .lint-mdc.sh
lines=$(wc -l < "$1")
if [ "$lines" -gt 150 ]; then
  echo "❌ $1 exceeds 150 lines."
  exit 1
fi 