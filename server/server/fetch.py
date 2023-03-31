# from https://gitlab.com/our-sci/software/stratipy/

import rasterio as rio
import functools
import asyncio
from . import utils
# from stratipy.constants import WSG84_CRS
WGS84_CRS = 'epsg:4326'

GDAL_FETCH_OPTIONS = {
    "CPL_VSIL_CURL_ALLOWED_EXTENSIONS": "tif",
    "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR",
    "VSI_CACHE": "TRUE",
    # needed for storage.googleapis.com 503
    "GDAL_HTTP_MAX_RETRY": "100",
    "GDAL_HTTP_RETRY_DELAY": "1",
}


def read_raster(url, bbox=None, bbox_crs=None, **kwargs):
    with rio.Env(**GDAL_FETCH_OPTIONS):
        # TODO: update S2 workflow to handle returned transform and crs
        # maybe we should skip window precalculation step and just perform it
        # directly when opening the raster by passing bbox into read_raster
        with rio.open(url) as src:
            if bbox is None:
                return src.read(1, **kwargs)

            bbox_crs_matches = (
                bbox is not None and bbox_crs is not None and bbox_crs != src.crs
            )
            bb = (
                utils.reproject_bbox(bbox, bbox_crs, src.crs)
                if bbox_crs_matches
                else bbox
            )

            window_tile = rio.windows.from_bounds(*src.bounds, transform=src.transform)
            window_bbox = (
                rio.windows.from_bounds(*bb, transform=src.transform)
                .round_lengths()
                .round_offsets()
            )
            window = window_bbox.intersection(window_tile)
            transform = rio.windows.transform(window, src.transform)
            return src.read(1, window=window, **kwargs), transform, src.crs, window


def run_in_executor(f):
    @functools.wraps(f)
    def inner(*args, **kwargs):
        loop = asyncio.get_running_loop()
        return loop.run_in_executor(None, lambda: f(*args, **kwargs))

    return inner


# wrapper for async use
@run_in_executor
def _read_raster_in_executor(url, **kwargs):
    return read_raster(url, **kwargs)


# modern async function (coroutine)
async def fetch_raster_async(url, **kwargs):
    return await _read_raster_in_executor(url, **kwargs)


async def fetch_raster_async_wrapper(key, url, **kwargs):
    try:
        return (key, await _read_raster_in_executor(url, **kwargs))
    except Exception as exc:
        raise type(exc)(f"{key}: {str(exc)}") from exc


clip = lambda x, l, u: l if x < l else u if x > u else x
slice_clip = lambda s, l, u: slice(clip(s.start, l, u), clip(s.stop, l, u))


def read_raster_xr(url, bbox=None, bbox_to_utm=False, **kwargs):
    with rio.Env(**GDAL_FETCH_OPTIONS):
        with rio.open(url) as src:
            da = xr.open_rasterio(src)
            if bbox is None:
                return da

            bb = utils.reproject_bbox(bbox, WSG84_CRS, src.crs)
            window = (
                rio.windows.from_bounds(*bb, transform=src.transform)
                .round_lengths()
                .round_offsets()
            )
            transform = rio.windows.transform(window, src.transform)
            rows, cols = window.toslices()
            rc = slice_clip(rows, 0, da.shape[1])
            cc = slice_clip(cols, 0, da.shape[2])
            # da.attrs['original_transform'] = da.attrs['transform']
            da.attrs["transform"] = tuple(transform)[0:6]
            return da[0, rc, cc]

