# Self-documenting Makefile, taken from
# https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html

setup_env: ## Set up the local environment by installing the required Python packages
	bash setup/python_env/setup_env.sh

create_config: ## Generate necessary configuration files based on user-specified configs.
	python setup/infra/create_config.py

deploy_infra: ## Deploy necessary infrastucture to GCP using terraform
	bash setup/infra/deploy_infra.sh

create_work_image: ## Build and push the docker image in which are our Prefect jobs will run
	python setup/infra/build_image.py

deploy_prefect_flows: ## Create the deployments for setup and analysis jobs on Prefect Cloud
	bash setup/infra/deploy_flows.sh

trigger_setup_flow: ## Trigger the Prefect flow to set up sensor location data
	bash setup/infra/trigger_setup_flow.sh

trigger_analysis_flow: ## Trigger the Prefect flow to perform air quality analysis
	bash setup/infra/trigger_analysis_flow.sh

help:
	@echo "Possible actions:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help