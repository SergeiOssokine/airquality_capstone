FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim
RUN apt-get update && apt-get -y install git curl
COPY ["setup/python_env/requirements.txt", "./"]
RUN uv pip install --system -r requirements.txt
RUN uv pip install --system --pre prefect-dbt