import logging
import os
from typing import Any, Dict, List

import pandas as pd
import requests
from prefect.blocks.system import Secret
from prefect.exceptions import MissingContextError
from prefect.logging import get_logger, get_run_logger

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
    try:
        logger = get_run_logger()
    except MissingContextError:
        logging.basicConfig()
        logger = get_logger()
        logger.setLevel("INFO")
    return logger


def get_all_locations(api_key_name: str = "openaq-api-key") -> List[Dict[str, Any]]:
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
            has_more = False

        else:
            logger.critical(f"Error: {response.status_code}")
            break

    return all_locations


# Process the locations to extract coordinates and country info


def extract_location_info(locations):
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


def get_sensor_location_info(staging_area: str = "/tmp/airquality_staging_area"):
    logger = fetch_logger()
    # Get all locations and extract coordinates and country information
    logger.info("Downloading all raw location data")
    locations = get_all_locations()
    logger.info("Done downloading the raw data")
    logger.info("Extracting useful data")
    location_info = extract_location_info(locations)
    logger.info("Done extracting data")
    output_name = os.path.join(staging_area, "sensor_overview.parquet")
    logger.info(f"Saving the data to {output_name}")
    print(location_info.head(5))
    location_info.to_parquet(output_name)
    return [output_name]


if __name__ == "__main__":
    get_sensor_location_info("./")
