import asyncio
import os
from typing import Any, Dict
import yaml
from prefect.client.cloud import get_cloud_client

pth = os.path.dirname(__file__)


def get_config(config_path: str) -> Dict[str, Any]:
    """Load config from yaml file

    Args:
        config_path (str): The path to config.yaml

    Returns:
        Dict[str, Any]: The configuration for the project
    """
    with open(config_path, "r") as fp:
        config = yaml.safe_load(fp)
    return config


async def get_basic_prefect_info() -> Dict[str, str]:
    """Get Prefect account and workspace ID information

    Returns:
        Dict[str,str]: The desired info
    """
    async with get_cloud_client() as client:
        workspaces = await client.read_workspaces()
    result = dict(
        account_id=str(workspaces[0].account_id),
        workspace_id=str(workspaces[0].workspace_id),
    )
    return result


def write_tf_vars(target: str, config: Dict[str, Any]) -> None:
    """Write the tfvars file to be used with terraform infra
    provisioning

    Args:
        target (str): What are we configuring
        config (Dict[str,Any]): The configuration info
    """
    target_path = os.path.join(
        pth, f"../../infra/tf/{target}/project_variables_auto.tfvars"
    )
    with open(target_path, "w") as fw:
        for key, item in config[target].items():
            fw.write(f'{key} = "{item}"\n')


async def enrich_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Given basic prefect information, enrich it with some
    information about prefect account as well as gcp info.

    Args:
        config (Dict[str,Any]): Project config

    Returns:
        Dict[str,Any]: Enriched project config
    """
    prefect_info = await get_basic_prefect_info()
    pr = config["prefect"]
    gc = config["gcp"]
    # For prefect, we need some of the config from gcp side, so add it
    pr.update(**config["gcp"])
    # Add the basic prefect info to prefect config
    pr.update(**prefect_info)
    pr["docker_image"] = (
        f"{gc['gcp_region']}-docker.pkg.dev/{gc['gcp_project_name']}/{gc['artifact_registry_name']}/{pr['docker_image_name']}"
    )
    # Dump everything for use by other scripts
    with open(os.path.join(pth, "../conf/.project_config.yaml"), "w") as fw:
        yaml.dump(config["prefect"], fw)

    # Avoid annoying terraform warnings about unused variables
    for key in ["docker_image_name", "artifact_registry_name"]:
        pr.pop(key)
    return config


async def main():
    # Load the base config as specified by the user
    config = get_config(os.path.join(pth, "../conf/config.yaml"))
    # Get prefect account_id and workspace_id
    config = await enrich_config(config)
    print(config)
    write_tf_vars("gcp", config)
    write_tf_vars("prefect", config)


if __name__ == "__main__":
    asyncio.run(main())
