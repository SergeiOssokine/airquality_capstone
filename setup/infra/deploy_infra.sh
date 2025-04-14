#!/bin/bash
echo "Deploying infrastructure to GCP"
cd infra/tf/gcp
terraform init
terraform validate
terraform apply -var-file project_variables_auto.tfvars

echo "Done deploying infrastructure to GCP"