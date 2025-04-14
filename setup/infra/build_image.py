import os
import docker
import yaml
import logging
from rich.logging import RichHandler
from rich.traceback import install

pth = os.path.dirname(__file__)
# Sets up the logger to work with rich
logger = logging.getLogger(__name__)
logger.addHandler(RichHandler(rich_tracebacks=True, markup=True))
logger.setLevel("INFO")
# Setup rich to get nice tracebacks
install()

if __name__ == "__main__":
    config_path = os.path.join(pth, "../conf/.project_config.yaml")
    with open(config_path, "r") as fp:
        config = yaml.safe_load(fp)

    print(config)
    docker_client = docker.from_env()
    # Build the local image
    logger.info("Building the image")
    local_image, build_logs = docker_client.images.build(
        path=os.path.join(pth, "../../"), tag=config["docker_image_name"]
    )
    logger.info("Build logs:")
    # Print the build output
    for chunk in build_logs:
        if "stream" in chunk:
            print(chunk["stream"], end="")

    uri = config["docker_image"]
    logger.info(f"Tagging local image with the remote uri: {uri}")
    local_image.tag(uri)
    logger.info("Logging into the GCP artifact registry")
    logger.info("Pushing the image")
    push_logs = docker_client.images.push(uri)
    logger.info("Push logs:")
    print(push_logs)
    logger.info("Done")
