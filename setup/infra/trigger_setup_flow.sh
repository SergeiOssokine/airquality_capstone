#!/bin/bash
header_auth="Authorization: Bearer ${PREFECT_API_KEY}"
header_type="Content-Type: application/json"
base_url="https://api.prefect.cloud/api"

echo "Triggering the setup flow"
# Get account ID
account_id=$(
    curl -s -X GET "${base_url}/me/accounts" -H "$header_auth" -H "$header_type" | jq -r '.[].account_id'
)
# Get workspace ID
workspace_id=$(
    curl -s -X GET "${base_url}/me/workspaces" -H "$header_auth" -H "$header_type" | jq -r '.[].workspace_id'
)

# Given deployment name, get its ID
deployment_id=$(curl -s -X GET "${base_url}/accounts/${account_id}/workspaces/${workspace_id}/deployments/name/prepare-location-data-flow/prepare-location-data" -H "$header_auth" -H "$header_type" | jq -r '.id')

# Trigger a run of the deployment
flow_run_id=$(curl -s -X POST "${base_url}/accounts/${account_id}/workspaces/${workspace_id}/deployments/${deployment_id}/create_flow_run" -H "$header_auth" -H "$header_type" -d "{}" | jq -r '.id')
run_url="https://app.prefect.cloud/account/${account_id}/workspace/${workspace_id}/runs/flow-run/${flow_run_id}"
echo
echo "Go to ${run_url} to see your deployed flow"
echo "Done"
