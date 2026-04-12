#!/bin/bash
# Check if otlg CLI is available and working
set -e

if which otlg > /dev/null 2>&1; then
  HELP_OUTPUT=$(otlg --help 2>&1) && EXIT_CODE=0 || EXIT_CODE=$?
  if [ "$EXIT_CODE" -eq 0 ]; then
    echo '{"status": "ok"}'
    exit 0
  fi
fi

echo '{"status": "not_found", "message": "otlg CLI not found in PATH. See references/INSTALL.md for installation options."}'
exit 1
