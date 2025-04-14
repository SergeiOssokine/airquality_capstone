# Air quality capstone project

## Introduction and Problem Statement

Cities face a lot of problems with poor air quality due to a number of polluting factors, such as high levels of industrialisation, more cars, and factories. Extensive studies have shown that poor air quality is connected to a vast range of long-term health ailments.

Recently, more and more detailed data has become available online through the coordination of universities, government agencies, companies, and citizen scientists, giving us a wealth of information about the extent of the problem and the impact that various approaches to tackling air pollutions might have.

**In this project we analyze 2024 air quality data for Berlin. In particular, we compute the daily averages for different pollutants and compare them to the recommendations by World Health Organization (WHO).**

We use the following tech stack:

- [Docker](https://www.docker.com/) for containerisation
- [Prefect Cloud](https://www.prefect.io/) for orchestration
- [Google Cloud Platform](https://cloud.google.com/) for cloud services, in particular Cloud Storage as a data lake, BigQuery as a data warehouse, and CloudRun for containerized executions of `Prefect` jobs.
- [dbt](https://www.getdbt.com/) to orchestrate and perform SQL transformations
- [Preset](https://preset.io/), a managed solution for [Apache Superset](https://superset.apache.org/) for dashboarding
- [Terraform](https://www.terraform.io/) for provisioning resources on GCP and Prefect Cloud
- [mkdocs](https://www.mkdocs.org/) for documentation

The overall architecture of the project is shown below:

![](./images/architecture.svg)



You can find detailed documentation [here](https://sergeiossokine.github.io/airquality_capstone/).