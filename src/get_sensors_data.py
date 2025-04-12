import logging
import os
from typing import Any, Dict, List

import geopandas as gpd
import pandas as pd
import requests
from prefect.blocks.system import Secret
from prefect.exceptions import MissingContextError
from prefect.logging import get_logger, get_run_logger
from shapely import Point

possible_names = [
    "pm10",
    "pm25",
    "o3",
    "co",
    "no2",
    "so2",
    "no2",
    "co",
    "so2",
    "o3",
    "bc",
    "no2",
    "pm1",
    "co2",
]


def fetch_logger():
    """Return either a Prefect run logger if inside a Prefect task/flow
    or a regular logger if not

    Returns:
        logging.Logger: The logger instance
    """
    try:
        logger = get_run_logger()
    except MissingContextError:
        logging.basicConfig()
        logger = get_logger()
        logger.setLevel("INFO")
    return logger


def get_all_locations(api_key_name: str = "openaq-api-key") -> List[Dict[str, Any]]:
    """Download the list of all locations and corresponding sensor IDs

    Args:
        api_key_name (str, optional): The name of the Prefect block where your
            stored the OpenAQ API key. Defaults to "openaq-api-key".

    Returns:
        List[Dict[str, Any]]: The data structure of interest
    """
    secret_block = Secret.load(api_key_name)
    logger = fetch_logger()
    url = "https://api.openaq.org/v3/locations"
    params = {
        "limit": 1000,
        "page": 1,
    }
    headers = {
        "Content-type": "application/json",
        "x-api-key": f"{secret_block.get()}",
    }

    all_locations = []
    has_more = True
    while has_more:
        response = requests.get(url, params=params, headers=headers)

        if response.ok:
            data = response.json()
            results = data.get("results", [])
            all_locations.extend(results)

            # Check if there are more pages
            meta = data.get("meta", {})
            found = meta.get("found", 0)
            page = meta.get("page", 1)
            logger.info(f"Currently on page {page}, found {found}")
            if isinstance(found, str):
                if ">" in found:
                    params["page"] = page + 1
            else:
                has_more = False

        else:
            logger.critical(f"Error: {response.status_code}")
            break

    return all_locations


def extract_location_info(locations: List[Dict[str, Any]]) -> pd.DataFrame:
    """Given the raw data from OpenAQ in json format extract the information
    we care about:
    - location_id
    - name
    - lat,lon
    - country information
    - sensor_ids

    Args:
        locations (List[Dict[str, Any]]): Raw location data from OpenAQ

    Returns:
        pd.DataFrame: Subset of interesting information
    """
    location_info = []
    country_info = {}
    for loc in locations:
        tmp_info = loc.get("country")
        for key, item in tmp_info.items():
            country_info[f"country_{key}"] = item
        tmp_info = loc.get("sensors")
        sensor_ids = dict(zip(possible_names, [None] * (len(possible_names))))
        for sensor in tmp_info:
            parameter_name = sensor.get("parameter").get("name")
            if parameter_name in possible_names:
                sensor_ids[parameter_name] = sensor.get("id")
        info = {
            "location_id": loc.get("id"),
            "name": loc.get("name"),
            "latitude": loc.get("coordinates", {}).get("latitude"),
            "longitude": loc.get("coordinates", {}).get("longitude"),
        }

        info.update(**country_info)
        info.update(**sensor_ids)
        location_info.append(info)
    df = pd.DataFrame(location_info)
    for k in possible_names:
        df[k] = df[k].astype("Int64")
    return df


def row_to_point(row):
    return Point(row[0], row[1])


def add_geometry_info(df: pd.DataFrame) -> gpd.GeoDataFrame:
    """Given a pandas DataFrame containing longitude and
    latitude create a GeoPandas DataFrame where the geometry
    column is of type Point with those coordinates

    Args:
        df (pd.DataFrame): The location information

    Returns:
        gpd.GeoDataFrame: Data with GEOMETRY column
    """
    return gpd.GeoDataFrame(
        df, geometry=df[["longitude", "latitude"]].apply(row_to_point, axis=1)
    )


def get_sensor_location_info(
    staging_area: str = "/tmp/airquality_staging_area",
) -> List[str]:
    """Get information about the location of all sensors around the globe.

    This function downloads all location data from OpenAQ, and then stores it in GeoParquet
    format. This will be later combined with another GeoParquet data containing city/town/villages
    bounding boxes to associate every sensor location with a known geogephical location like
    "Berlin"

    Args:
        staging_area (str, optional): The folder where to temporarily download and write data. Defaults to "/tmp/airquality_staging_area".

    Returns:
        List[str]: List of output names
    """
    logger = fetch_logger()
    # Get all locations and extract coordinates and country information
    logger.info("Downloading all raw location data")
    locations = get_all_locations()
    logger.info("Done downloading the raw data")
    logger.info("Extracting useful data")
    location_info = extract_location_info(locations)
    location_info = add_geometry_info(location_info)
    logger.info("Done extracting data")
    output_name = os.path.join(staging_area, "sensor_overview.parquet")
    logger.info(f"Saving the data to {output_name}")
    location_info.to_parquet(output_name)
    return [output_name]


if __name__ == "__main__":
    get_sensor_location_info("./")
