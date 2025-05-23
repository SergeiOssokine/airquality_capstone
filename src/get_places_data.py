import glob
import os
import shutil
import zipfile
from functools import partial
from multiprocessing.pool import ThreadPool
from typing import List

import geopandas as gpd
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from shapely import Polygon
from src.utils import fetch_logger


def bbox_to_polygon(bbox):
    lon_low, lat_low, lon_high, lat_high = bbox
    coords = [
        (lon_low, lat_low),
        (lon_high, lat_low),
        (lon_high, lat_high),
        (lon_low, lat_high),
        (lon_low, lat_low),
    ]
    polygon = Polygon(coords)
    return polygon


def convert_to_gis(full: pd.DataFrame):
    return gpd.GeoDataFrame(full, geometry=full["bbox"].apply(bbox_to_polygon))[
        ["name", "location", "osm_id", "geometry"]
    ]


def download_file(
    url: str, chunk_size: int = 8192, results_dir: str = "places_data"
) -> str:
    """Download a file from the given url using chunking

    Args:
        url (str): The url of the file
        chunk_size (int, optional): The chunking to use. Defaults to 8192.
        results_dir (str, optional): The results folder. Defaults to "places_data".

    Returns:
        str: Full path to the saved file
    """
    logger = fetch_logger()
    local_filename = os.path.join(results_dir, url.split("/")[-1])
    logger.info(f"Download data from {url} to {local_filename}")

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=chunk_size):
                f.write(chunk)
    return local_filename


def get_list_of_files(url: str) -> List[str]:
    """Get a list of files to download by scraping url

    Args:
        url (str): The url to scrape

    Returns:
        List[str]: List of file names to download
    """
    logger = fetch_logger()
    logger.info("Generating list of files to download")
    response = requests.get(url)
    if response.ok:
        soup = BeautifulSoup(response.text, "html.parser")
        lines = soup.get_text().splitlines()
        res = []
        for line in lines:
            if ".zip" in line:
                res.append(line.split())
        df = pd.DataFrame(res, columns=["file_name", "date", "timestamp", "size"])
        df["size"] = df["size"].astype("int")
    else:
        df = pd.DataFrame()
    logger.info("Done")
    return df


def extract_data_from_file(
    file_name: str, directory_to_extract_to="tmp"
) -> pd.DataFrame:
    """Given the compressed downloaded file, uncompress it, read all ndjson files and
    combine the data into a single pandas DataFrame. Also cleans up by deleteing extracted
    files.

    Args:
        file_name (str): The path to the file to process
        directory_to_extract_to (str, optional): Where to temporarily extract data.
            Defaults to "tmp".

    Returns:
        pd.DataFrame: All the combined data from the file
    """
    logger = fetch_logger()
    logger.info(f"Extracing data from {file_name}")
    fname = file_name.split(".")[0]
    with zipfile.ZipFile(file_name, "r") as zip_ref:
        zip_ref.extractall(directory_to_extract_to)
    # Now return all the data
    temp = []
    loc = os.path.join(directory_to_extract_to, fname)
    files = glob.glob(f"{loc}/*.ndjson")
    logger.info(f"Processing all files in {loc}: {files}")
    for f in files:
        data = pd.read_json(f, lines=True)
        temp.append(data[["name", "location", "osm_id", "bbox"]])

    logger.info(f"Deleting all files in {loc}")
    shutil.rmtree(loc)
    logger.info("Done")
    return pd.concat(temp, ignore_index=True)


def get_location_bounding_boxes(staging_area: str = "/tmp/airquality_staging_area"):
    logger = fetch_logger()
    base_url = "https://www.geoapify.com/data-share/localities/"
    file_dir = get_list_of_files(base_url)
    n_files = file_dir.shape[0]
    total_size = file_dir["size"].sum() / 1024 / 1024
    logger.info(
        f"Will downloaded a total of {n_files} files, occupying {np.round(total_size)} MB of space"
    )

    files_to_download = [f"{base_url}/{f}" for f in file_dir["file_name"].values]
    pool = ThreadPool(8)
    pool.map(partial(download_file, results_dir=staging_area), files_to_download)
    downloaded_files = glob.glob(f"{staging_area}/*.zip")
    processed_names = []
    for file in downloaded_files:
        logger.info(f"Working on {file}")

        name = os.path.basename(file).split(".")[0]
        processed_name = os.path.join(staging_area, f"{name}.parquet")
        tmp = extract_data_from_file(file, directory_to_extract_to=staging_area)
        tmp_geo = convert_to_gis(tmp)
        tmp_geo.to_parquet(processed_name)
        processed_names.append(processed_name)
    logger.info(f"Processed names are {processed_names}")
    return processed_names
