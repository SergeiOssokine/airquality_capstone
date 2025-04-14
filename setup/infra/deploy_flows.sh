#!/bin/bash
echo "Deploying orchestrator setup to Prefect cloud"
cd infra/tf/prefect
terraform init
terraform validate
terraform apply -var-file project_variables_auto.tfvars

echo "Done deploying"