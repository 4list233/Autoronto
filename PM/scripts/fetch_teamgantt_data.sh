#!/bin/bash

# TeamGantt Data Export Script
# Usage: ./fetch_teamgantt_data.sh [YOUR_API_TOKEN] [PROJECT_ID]
# If no arguments provided, will read from .env file
# If PROJECT_ID is not provided, script will list projects and ask you to pick one

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Load .env file if it exists (check both scripts dir and parent dir)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

if [ -f "$PROJECT_ROOT/.env" ]; then
    set -a  # Export all variables
    source "$PROJECT_ROOT/.env"
    set +a
elif [ -f "$SCRIPT_DIR/.env" ]; then
    set -a
    source "$SCRIPT_DIR/.env"
    set +a
fi

# Use arguments if provided, otherwise use .env values
if [ -n "$1" ]; then
    TEAMGANTT_TOKEN="$1"
else
    # Try both variable names for compatibility
    TEAMGANTT_TOKEN="${TEAMGANTT_API_KEY:-${TEAMGANTT_TOKEN}}"
fi

if [ -z "$TEAMGANTT_TOKEN" ]; then
    echo "Error: No API token provided."
    echo "Either pass it as an argument or set TEAMGANTT_API_KEY in .env file"
    echo ""
    echo "Usage: $0 [YOUR_API_TOKEN] [PROJECT_ID]"
    echo "Example: $0 abc123token"
    echo "Or: $0 abc123token 920883"
    echo "Or: Create a .env file with TEAMGANTT_TOKEN=your_token"
    exit 1
fi

if [ -n "$2" ]; then
    PROJECT_ID="$2"
else
    # Try both variable names for compatibility
    PROJECT_ID="${TEAMGANTT_PROJECT_ID:-${PROJECT_ID}}"
fi

echo -e "${GREEN}=== TeamGantt Data Exporter ===${NC}\n"

# Step 1: List all projects
echo -e "${YELLOW}Step 1: Fetching your projects...${NC}"
curl -s \
  -H "Authorization: Bearer $TEAMGANTT_TOKEN" \
  "https://api.teamgantt.com/v1/projects?status=active&limit=100" \
  > projects.json

if [ ! -s projects.json ]; then
    echo "Error: Failed to fetch projects. Check your API token."
    exit 1
fi

echo "✓ Projects saved to projects.json"

# If no PROJECT_ID provided, show list and prompt
if [ -z "$PROJECT_ID" ]; then
    echo -e "\n${YELLOW}Available Projects:${NC}"
    cat projects.json | python3 -c "
import sys, json
data = json.load(sys.stdin)
projects = data.get('data', [])
for p in projects:
    print(f\"  ID: {p.get('id', 'N/A'):>10} | {p.get('name', 'Unnamed')}\")
"
    echo ""
    read -p "Enter the PROJECT_ID you want to export: " PROJECT_ID
    if [ -z "$PROJECT_ID" ]; then
        echo "No project ID entered. Exiting."
        exit 1
    fi
fi

echo -e "\n${YELLOW}Step 2: Exporting project $PROJECT_ID to CSV...${NC}"

# Step 2: Request CSV export
curl -s -X POST \
  -H "Authorization: Bearer $TEAMGANTT_TOKEN" \
  "https://api.teamgantt.com/v1/projects/export/csv?ids[]=${PROJECT_ID}" \
  > export_job.json

if [ ! -s export_job.json ]; then
    echo "Error: Failed to request CSV export."
    exit 1
fi

EXPORT_URL=$(cat export_job.json | python3 -c "import sys, json; print(json.load(sys.stdin).get('download_url', ''))")

if [ -z "$EXPORT_URL" ]; then
    echo "Error: No download URL in export response."
    cat export_job.json
    exit 1
fi

echo "✓ Export job created. Downloading CSV..."

# Download the CSV
curl -L -s \
  -H "Authorization: Bearer $TEAMGANTT_TOKEN" \
  "$EXPORT_URL" \
  -o "teamgantt_export_${PROJECT_ID}.csv"

echo "✓ CSV saved to teamgantt_export_${PROJECT_ID}.csv"

# Step 3: Fetch full JSON structure (hierarchical)
echo -e "\n${YELLOW}Step 3: Fetching project structure (JSON)...${NC}"

curl -s \
  -H "Authorization: Bearer $TEAMGANTT_TOKEN" \
  "https://api.teamgantt.com/v1/projects/${PROJECT_ID}/children?is_flat_list=true" \
  > "children_flat_${PROJECT_ID}.json"

echo "✓ Flat task list saved to children_flat_${PROJECT_ID}.json"

# Also get hierarchical structure
curl -s \
  -H "Authorization: Bearer $TEAMGANTT_TOKEN" \
  "https://api.teamgantt.com/v1/projects/${PROJECT_ID}/children" \
  > "children_hierarchical_${PROJECT_ID}.json"

echo "✓ Hierarchical structure saved to children_hierarchical_${PROJECT_ID}.json"

# Step 4: Get project details
echo -e "\n${YELLOW}Step 4: Fetching project details...${NC}"

curl -s \
  -H "Authorization: Bearer $TEAMGANTT_TOKEN" \
  "https://api.teamgantt.com/v1/projects/${PROJECT_ID}" \
  > "project_${PROJECT_ID}.json"

echo "✓ Project details saved to project_${PROJECT_ID}.json"

# Summary
echo -e "\n${GREEN}=== Export Complete! ===${NC}\n"
echo "Files created:"
echo "  1. projects.json                              - All your projects"
echo "  2. teamgantt_export_${PROJECT_ID}.csv         - Full CSV export (tasks, dependencies, resources)"
echo "  3. children_flat_${PROJECT_ID}.json           - Flat list of all groups/tasks"
echo "  4. children_hierarchical_${PROJECT_ID}.json   - Hierarchical structure"
echo "  5. project_${PROJECT_ID}.json                 - Project metadata"
echo ""
echo -e "${YELLOW}Next step:${NC} Share these files (especially the CSV and JSON files) so we can analyze and reorganize!"
echo ""
echo "⚠️  Do NOT share export_job.json or your API token!"
