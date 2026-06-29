#!/bin/bash
# Scaffold a new ecoscope workflow using wt-compiler
# Usage: ./scaffold.sh <workflow-name>
# Example: ./scaffold.sh wt-my-workflow

set -e

OUTPUT_DIR="/home/gitonga/Develop/PGAFF/repos/wt"

if [ -z "$1" ]; then
    echo "Usage: $0 <workflow-name>"
    echo "Example: $0 wt-my-workflow"
    exit 1
fi

REPO_NAME="$1"

if [[ ! "$REPO_NAME" =~ ^wt- ]]; then
    echo "Error: Workflow repo name must start with 'wt-'"
    exit 1
fi

WORKFLOW_ID="${REPO_NAME#wt-}"
WORKFLOW_ID="${WORKFLOW_ID//-/_}"

WORKFLOW_DIR="$OUTPUT_DIR/$REPO_NAME"

if [ -d "$WORKFLOW_DIR" ]; then
    echo "Error: Directory $WORKFLOW_DIR already exists"
    exit 1
fi

echo "Scaffolding workflow: $REPO_NAME (id: $WORKFLOW_ID)"

cd "$OUTPUT_DIR"

wt-compiler scaffold init --no-interactive \
  --workflow-id "$WORKFLOW_ID" \
  --workflow-name "$REPO_NAME" \
  --author-name "PGAFF" \
  --output-dir . \
  --requirements '{"name":"ecoscope-workflows-core","version":">=0.22.18,<0.23.0","channel":"https://repo.prefix.dev/ecoscope-workflows/"}' \
  --requirements '{"name":"ecoscope-workflows-ext-ecoscope","version":">=0.22.18,<0.23.0","channel":"https://repo.prefix.dev/ecoscope-workflows/"}' \
  --requirements '{"name":"ecoscope-workflows-ext-custom","version":">=0.0.46,<0.1.0","channel":"https://repo.prefix.dev/ecoscope-workflows-custom/"}'

# wt-compiler names the output dir after workflow-id; rename to wt-<name> convention
if [ -d "$WORKFLOW_ID" ]; then
    mv "$WORKFLOW_ID" "$REPO_NAME"
    echo "Renamed $WORKFLOW_ID → $REPO_NAME"
fi

echo ""
echo "Workflow scaffolded at $WORKFLOW_DIR"
echo ""
echo "Next steps:"
echo "  1. cd $WORKFLOW_DIR"
echo "  2. Edit spec.yaml to add your workflow tasks"
echo "  3. Update test-cases.yaml with test parameters"
echo "  4. wt-compiler compile --spec spec.yaml --pkg-name-prefix=ecoscope-workflows --results-env-var=ECOSCOPE_WORKFLOWS_RESULTS --clobber"
