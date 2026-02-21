#!/bin/bash
# PostgreSQL MCP wrapper — reads credentials from a creds file passed as $1
# Usage: pg-mcp.sh <creds-file>
# Creds file should contain a single line: postgresql://user:pass@host:5432/dbname

CREDS_FILE="$1"

if [ -z "$CREDS_FILE" ]; then
  echo "ERROR: No credentials file specified" >&2
  exit 1
fi

if [ ! -f "$CREDS_FILE" ]; then
  echo "ERROR: Credentials file not found at $CREDS_FILE" >&2
  echo "Create it with: echo 'postgresql://user:pass@host:5432/dbname' > $CREDS_FILE && chmod 600 $CREDS_FILE" >&2
  exit 1
fi

PG_URL=$(cat "$CREDS_FILE" | tr -d '[:space:]')

export NODE_EXTRA_CA_CERTS="${HOME}/.claude/certs/aws-rds-global-bundle.pem"

exec npx -y @modelcontextprotocol/server-postgres "$PG_URL"
