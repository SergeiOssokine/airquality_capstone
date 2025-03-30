# Air quality capstopne project

## Setitng up

You will need the following running on your machine:

* GNU make


### Python

You will need many python libraries to run this project. To quickly get there, simply run

```bash
make setup_env
```

which will:

* install [uv](https://github.com/astral-sh/uv)
* create a virtual environment for the project under `.capstone`
* install all the necessary libararies (see `setup/env/requirements.txt`)

### Google Cloud

You will need to set up a GCP account to run this project. Create a free account and then create a `terraform` service user as described in Week 1 of the [DEZoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/01-docker-terraform#movie_camera-introduction-terraform-concepts-and-overview-a-primer). Save the `json` service credentials in a safe place.


### Prefect Cloud

For orchestration we will use Prefect Cloud, which has a generous free tier. To get started, create a free account and then create an API key and save it as recommended via the `prefect cloud login -k <your-api-key>`.

### OpenAQ

In order to be able to download the air quality data you will need an OpenAQ API key. Create a free account and get the API key as described [here](https://docs.openaq.org/using-the-api/api-key) and store it in a safe place.

