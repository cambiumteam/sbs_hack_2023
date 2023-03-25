# from https://gitlab.com/our-sci/software/stratipy/

from stratipy import utils
from stratipy import fetch
import numpy as np
import rasterio as rio
from tqdm.auto import tqdm
import asyncio
from collections import defaultdict, Counter
# from stratipy.constants import WGS84_CRS
WGS84_CRS = 'epsg:4326'
import rasterio.warp as rio_warp
from typing import Optional, Union, Callable, Tuple, List, Dict
from typing_extensions import Literal
from pystac_client import Client
import warnings

DateStringRange = Union[str, Tuple[str], Tuple[str, str], List[str]]
BBox = Union[Tuple[float, float, float, float], List[float]]

# TODO: add support for dates as sequence of strings, e.g. ('start', 'end'),
# ['start', 'end']
# TODO: add support for dates as sequence of datetime objects
def search_catalog(
    bbox: BBox,
    dates: Optional[str] = "2021-01-01T00:00:00Z/2021-12-31T23:59:59Z",
    query: Optional[Dict[str, Dict[str, Union[str, int, float, bool]]]] = {},
    fields: Optional[Dict[str, Dict[str, str]]] = {},
) -> dict:
    """
    Search Sentinel 2 STAC API for items

    Parameters:
        bbox: bounding box for area of interest (AOI)
        dates: date range for search
        query: STAC API query, used to filter based on the `properties` field of each item, see https://github.com/radiantearth/stac-api-spec/tree/master/fragments/query
        fields: STAC API fields, used to only return certain fields from each item, see https://github.com/radiantearth/stac-api-spec/tree/master/fragments/fields

    Returns:
        results: GeoJSON FeatureCollection of search results
    """
    URL = "https://earth-search.aws.element84.com/v0"
    if len(bbox) != 4:
        raise ValueError("invalid bbox")

    if type(dates) != str:
        raise ValueError("invalid dates")

    if not (type(query) == dict and all(type(key) == dict for key in query.values())):
        raise ValueError("invalid query")

    return (
        Client.open(URL)
        .search(
            collections=["sentinel-s2-l2a-cogs"],
            bbox=bbox,
            datetime=dates,
            query=query,
            fields=fields,
        )
        .get_all_items_as_dict()
    )


VALID_BANDS = {
    "AOT",
    "B01",
    "B02",
    "B03",
    "B04",
    "B05",
    "B06",
    "B07",
    "B08",
    "B09",
    "B10",
    "B11",
    "B12",
    "B08A",
    "SCL",
    "WVP",
}
Band = Literal[
    "AOT",
    "B01",
    "B02",
    "B03",
    "B04",
    "B05",
    "B06",
    "B07",
    "B08",
    "B09",
    "B10",
    "B11",
    "B12",
    "B08A",
    "SCL",
    "WVP",
]


def get_inputs(
    items: dict,
    bands: Optional[List[Band]] = ["B04", "B08", "SCL"],
    filt: Optional[Callable[[dict], bool]] = lambda _: True,
) -> Dict[str, Dict[Band, str]]:
    """
    Extract GeoTIFF URLs for relevant bands from STAC API search results

    Parameters:
        items: GeoJSON FeatureCollection with STAC API search results
        bands: list of Sentinel 2 bands of interest
        filt: filter lambda which takes each STAC API item (GeoJSON Feature) as an
            argument and returns a boolean

    Returns:
        mapping with item ids (satellite/scene id/date/processing level) to dict of
        bands to GeoTIFF URLs

    Examples:
    >>> get_inputs(search_results, bands=['B01'])
    {'S2A_18TXP_20200131_0_L2A': { 'B01': 'https://example.com/B01.tif' }}
    """
    if not all((band in VALID_BANDS) for band in bands):
        raise ValueError(
            f"invalid bands passed, each band must be one of {VALID_BANDS}"
        )

    if not len(bands) > 0:
        raise ValueError("at least one band must be passed")

    if not isinstance(filt, Callable):
        raise ValueError("filter must be a lambda")

    return {
        item["id"]: {band: item["assets"][band]["href"] for band in bands}
        for item in items["features"]
        if filt(item)
    }


def group_dict_by_scene(dct):
    grouped = defaultdict(list)
    for k in dct:
        scene_id = k.split("_")[1]
        grouped[scene_id].append(k)

    return dict(grouped)


async def fetch_async(inputs, bbox=None, bbox_crs=None):
    flat_ins_dict = {
        f"{item_key}.{band_key}": band_val
        for item_key, item_val in inputs.items()
        for band_key, band_val in item_val.items()
    }

    tasks = [
        asyncio.create_task(
            fetch.fetch_raster_async_wrapper(
                key,
                url,
                bbox=bbox,
                bbox_crs=bbox_crs,
            )
        )
        for key, url in flat_ins_dict.items()
    ]

    flat_results_list = []
    errors = []
    for task in tqdm(tasks, total=len(list(tasks))):
        try:
            flat_results_list.append(await task)
        except (rio.errors.WindowError, rio.errors.RasterioIOError) as exc:
            errors.append(exc)

    results = defaultdict(dict)
    for key, result in flat_results_list:
        if type(result) == tuple:  # When would this not be a tuple? for errors?
            item, band = key.split(".")
            results[item][band] = result

    # Print error metrics, count of error types
    print(f"Encountered {len(errors)} errors.")
    errors_counter = Counter([type(e) for e in errors])
    print([f"{k}: {v}" for k, v in zip(errors_counter.keys(), errors_counter.values())])
    print(errors)

    return dict(results), errors


def mask_only_veg_non_veg(r):
    return np.logical_or(r == 4, r == 5)


def get_masked_ndvi(red=None, nir=None, scl=None):
    if red is None or nir is None or scl is None:
        raise ValueError("red, nir, and scl input layer kwargs must be defined")

    # handle divide by zero case, fill with nans, where there would be /0
    # equivalent to ndvi = (nir - red) / (nir + red)
    num = nir - red
    den = nir + red
    out_fill = np.empty(num.shape)
    # initialize with all zeros
    out_fill[:] = 0
    ndvi = np.divide(num, den, out=out_fill, where=den != 0)
    scl_mask = mask_only_veg_non_veg(scl)
    masked_ndvi = np.where(scl_mask, ndvi, np.nan)
    return masked_ndvi


def get_max_ndvi_raster(masked_ndvi_rasters):
    return np.nanmax(np.stack(masked_ndvi_rasters), axis=0)


def calc_ndvi(item):
    red = item["B04"]
    nir = item["B08"]
    scl = item["SCL"]
    if scl[0].shape != red[0].shape:
        with rio.Env():
            scl_projected, _ = rio_warp.reproject(
                scl[0],
                np.zeros(red[0].shape),
                src_transform=scl[1],
                src_crs=scl[2],
                dst_transform=red[1],
                dst_crs=red[2],
                resampling=rio.enums.Resampling.nearest,
            )
    return get_masked_ndvi(red=red[0], nir=nir[0], scl=scl_projected)


def summarize_ndvi(item_rasters, masked_ratio_threshold=0.3, ndvi_max=1.0):
    is_good_raster = lambda x: np.logical_and(
        np.count_nonzero(np.isnan(x)) / x.size < masked_ratio_threshold,
        np.nanmax(x) <= ndvi_max,
    )
    ndvi_rasters = [calc_ndvi(item) for item in item_rasters]
    good_ndvi_rasters = filter(is_good_raster, ndvi_rasters)
    return get_max_ndvi_raster(good_ndvi_rasters)


async def get_ndvi_summary_by_bbox_async(
    bbox: BBox,
    dates: Optional[DateStringRange] = "2021-01-01T00:00:00Z/2021-12-31T23:59:59Z",
    dst_crs=None,
    masked_ratio_threshold: float = 0.3,
    ndvi_max: float = 1.0,
    search_query: Optional[Dict[str, Dict[str, Union[str, int, float]]]] = {
        "platform": {"eq": "sentinel-2a"}
    },
):
    items = get_inputs(search_catalog(bbox, dates=dates, query=search_query))
    rasters, errors = await fetch_async(items, bbox=bbox, bbox_crs=WGS84_CRS)
    if len(errors) > 0:
        warnings.warn(f"Encountered errors: {errors}")

    # 1. groupby scene id
    # 2. summarize ndvi foreach scene id
    # 3. merge summaries
    tile_keys_by_scene = group_dict_by_scene(rasters)
    ndvi_summaries = [
        (
            summarize_ndvi(
                [rasters[key] for key in scene_item_keys],
                masked_ratio_threshold=masked_ratio_threshold,
                ndvi_max=ndvi_max,
            ),
            rasters[scene_item_keys[0]]["B04"][1],  # transform from red raster, shared
            rasters[scene_item_keys[0]]["B04"][2],  # CRS from red raster, shared
        )
        for scene_item_keys in tile_keys_by_scene.values()
    ]

    if dst_crs is not None:
        return utils.merge_rasters(ndvi_summaries, dst_crs=dst_crs)

    return utils.merge_rasters(ndvi_summaries, dst_crs=ndvi_summaries[0][2])
