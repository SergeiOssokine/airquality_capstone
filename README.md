# Air quality capstone project

## Background

**In this project we analyze 2024 air quality data for Berlin. In particular, we examine the daily,weekly and monthly trends for different pollutants and compare them to the recommendations by WHO.**

## Setting up

You will need the following running on your machine:

- Docker (v27.0 or later) with docker compose
- Terraform (v1.11.3 or later)
- jq-1.6
- GNU make (4.3 or later)
- Google Cloud CLI (`gcloud`).

Make sure all of these are in your `PATH`.

**Note that this project will work on Linux-like operating systems. If you are on Windows, you will need to use [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install).**

### Google Cloud

You will need to set up a GCP account and create a project. Create a free account and project and then create a `terraform` service user as described in Week 1 of the [DEZoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/01-docker-terraform#movie_camera-introduction-terraform-concepts-and-overview-a-primer). Save the `json` service credentials in a safe place. Then grant this service account the following roles:

- Artifact Registry Administrator
- BigQuery Admin
- Cloud Run Developer
- Logs Writer
- Service Account User
- Storage Admin

### Prefect Cloud

For orchestration we will use Prefect Cloud, which has a generous free tier. To get started, create a free account and then create an API key and save it as recommended via the `prefect cloud login -k <your-api-key>`.

### OpenAQ

In order to be able to download the air quality data you will need an OpenAQ API key. Create a free account and get the API key as described [here](https://docs.openaq.org/using-the-api/api-key) and store it in a safe place, in a `json` file that looks like

```json
{
    "value":"YOURAPIKEYHERE"
}
```

### Preset

The dashboards are hosted on [Preset Cloud](https://preset.io/), which is a managed solution for creating dashboards with [Apache Superset](https://superset.apache.org/), an open-source alternative to Tableau, etc. You will need to create a free account. You will also need to create a connection to the analysis data that will be stored in BigQuery. For detailed instructions, see [here](https://docs.preset.io/docs/big-query-database)

## Step-by-step instructions

Throughout the project,  we use `make` to perform various actions. Note that whenever a make command is mentioned, it should be invoked at the top-level of the repo. To see the full list of possible commands, simply run

```
make help
```

Log in to cloud services (use browser-based authentication)

```
gcloud auth login
```

and

```
prefect cloud login
```

### Setting up python

You will need many python libraries to run this project. To quickly get there, simply run

```bash
make setup_env
```

which will:

- install [uv](https://github.com/astral-sh/uv)
- create a virtual environment for the project under `.capstone`
- install all the necessary libararies (see `setup/python_env/requirements.txt`)

### Configuring the project

You will need to configure the project by editing the file `setup/conf/config.yaml`. At a minimum, you must provide the following:

- `gcp_project_name` - the name of the GCP project you have created
- `gcp_credentials` - the path to the JSON file with GCP credentials for the service account
- `openaq_credentials` - the path to the file that contains your OpenAQ API key

Once you have done this, run

```bash
make create_config
```

This will do the following:

- create `tfvars` files in `infra/tf/*` to configure the terraform infrastructure
- create a `setup/conf/.project_config.yaml` which will be used by other scripts

### Preparing GCP infrastructure

The project uses GCS as a data lake and BigQuery as a data warehouse. This infrastrture is managed via Terraform. To deploy it,
run

```bash
make deploy_infra
```

Terraform will show what infrastructure will be created. Type in "yes" when asked and hit enter.
Aside from a GCS bucket and a BigQuery dataset, we also create a Artifact Registry repository to hold the docker image that is used for analysis.

### Preparing Prefect deployments

We use Prefect as the orchestrator, similar to Kestra used in the course.

```bash
make deploy_prefect_flows
```

This will create all the necessary resources on Prefect cloud to be ready to run analysis jobs.

### Build and push the job docker image

To be able to push the docker image to the Artifact Registry on GCP that we created you need to authorize this. Do so by running:

```bash
gcloud auth configure-docker europe-west1-docker.pkg.dev
```

If you changed the `gcp_region` variable in `config.yaml` you will need to adjust the command accordingly.

```bash
make create_work_image
```

### Preparing the location data

OpenAQ provides data from thousands of different sensors around the globe. Each sensor has a unique ID (sensor_id) and location (encoded as longitude, latitude) as well as location ID. To analyze a particular geographical location by name (e.g. a city like Toronto or New Dehli) we need to associate the `location_id` with the geographical location. For a more detailed breakdown, see [here]().

```bash
make trigger_setup_flow
```

Follow the link to see the progress of this job. It should take around 10 minutes to run.

### Performing the analysis

Next we perform the actual analysis and obtain the dataset that computes that shows the hourly measurements of different pollutants at all the different stations in Berlin, as well as their spatial average. For more details, see [here]()

```bash
make trigger_analysis_flow
```

## Data sources

The measurement data comes from [OpenAQ](https://openaq.org/), which provides data via API as well as bulk download. We also make use of geographical location data from [GeoApify](https://www.geoapify.com/), see in particular [here](https://www.geoapify.com/download-all-the-cities-towns-villages/). The daily limits for exposure to different pollutants were taken from the [2021 WHO guidelines](https://www.who.int/news-room/feature-stories/detail/what-are-the-who-air-quality-guidelines)
