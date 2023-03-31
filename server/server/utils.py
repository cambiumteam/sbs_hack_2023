# from https://gitlab.com/our-sci/software/stratipy/

import utm
from affine import Affine
import rasterio.mask as rio_mask
import rasterio.merge as rio_merge
import rasterio.warp as rio_warp
from rasterio.io import MemoryFile
import rasterio as rio
import shapely
import shapely.ops
import pyproj
import functools
from contextlib import ExitStack
import numpy as np


def flatten_list(lst_lst):
    """
    Flatten a nested list by one level
    """
    return [item for sublist in lst_lst for item in sublist]


def bbox_to_utm(bbox):
    """
    Reprojects bounding box from WSG84/NAD (long/lat) to UTM

    Parameters:
        bbox: list<float>, required
        bounding box as a list [minLon, minLat, maxLon, maxLat]

    Returns:
        list<float>: the bounding box in UTM coordinates
    """
    ll = utm.from_latlon(bbox[1], bbox[0])
    ur = utm.from_latlon(bbox[3], bbox[2])
    return [ll[0], ll[1], ur[0], ur[1]]


def transform_array_to_affine(lst):
    """
    Converts affine transform as a list of numbers into Affine instance

    Parameters:
        lst: list, required
            affine transform as a list of numbers

    Returns:
        Affine: an Affine instance of the transform

    """
    #     affine_args = ['a', 'b', 'c', 'd', 'e', 'f']
    #     kwargs = {key: val for key, val in zip(affine_args, tf[0:6])}
    #     return Affine(**kwargs)
    return Affine(
        a=lst[0],
        b=lst[1],
        c=lst[2],
        d=lst[3],
        e=lst[4],
        f=lst[5],
    )


def mask_raster_with_geometry(raster, transform, shapes, crs=None, **kwargs):
    """Wrapper for rasterio.mask.mask to allow for in-memory processing.

    Docs: https://rasterio.readthedocs.io/en/latest/api/rasterio.mask.html
    References:
        - https://gis.stackexchange.com/a/387772
        - https://github.com/cheginit/pygeoutils/blob/master/pygeoutils/pygeoutils.py#L340
        - https://rasterio.readthedocs.io/en/latest/topics/memory-files.html

    Args:
        raster (numpy.ndarray): raster to be masked with dim: [H, W]
        transform (affine.Affine): the transform of the raster
        shapes, **kwargs: passed to rasterio.mask.mask

    Returns:
        masked: numpy.ndarray or numpy.ma.MaskedArray with dim: [H, W]
    """
    with MemoryFile() as memfile:
        with memfile.open(
            driver="GTiff",
            height=raster.shape[0],
            width=raster.shape[1],
            count=1,
            dtype=raster.dtype,
            transform=transform,
            crs=crs,
        ) as dataset:
            dataset.write(raster, 1)
        with memfile.open() as dataset:
            output, transform = rio_mask.mask(dataset, shapes, **kwargs)

    return output.squeeze(0), transform


def _write_memfile(memfile, raster, transform=None, crs=None):
    """Write raster to memfile
    Useful for some rasterio functions that only work on datasets

    Paramters:
        memfile: rasterio.io.MemoryFile, required
            a memory file to write the raster to
        transform: affine.Affine, optional
            affine transform for raster
        crs: rasterio.crs.CRS, optional
            CRS for raster
    """
    with memfile.open(
        driver="GTiff",
        height=raster.shape[0],
        width=raster.shape[1],
        count=1,
        dtype=raster.dtype,
        transform=transform,
        crs=crs,
    ) as dataset:
        dataset.write(raster, 1)


def merge_rasters(dss, dst_crs=None):
    """Merge rasters

    Parameters:
        dss: list(tuple(np.ndarray, affine.Affine, rasterio.crs.CRS)), required
            list of dataset tuples with raster, transform, and CRS

    Returns:
        np.ndarray:
            merged raster
        affine.Affine:
            transform for merged raster
    """
    dss_has_multiple_crs = len(set(ds[2] for ds in dss)) > 1
    if dst_crs is None and dss_has_multiple_crs:
        # raise ValueError("`dst_crs` required if rasters are not in the same CRS")
        dst_crs = dss[0][2]

    if dst_crs is not None and dss_has_multiple_crs:
        dssx = []
        for ds in dss:
            if ds[2] == dst_crs:
                dssx.append(ds)
            else:
                array_bounds = rio.transform.array_bounds(*ds[0].shape, ds[1])
                # print(array_bounds)
                tf, w, h = rio_warp.calculate_default_transform(
                    ds[2],
                    dst_crs,
                    # TODO: correct order for width and height?
                    ds[0].shape[1],
                    ds[0].shape[0],
                    left=array_bounds[0],
                    bottom=array_bounds[1],
                    right=array_bounds[2],
                    top=array_bounds[3],
                )

                ds_proj, ds_proj_tf = rio_warp.reproject(
                    ds[0],
                    np.zeros((h, w)),
                    src_transform=ds[1],
                    src_crs=ds[2],
                    # TODO: calculate transform?
                    # dst_transform=tf,
                    dst_crs=dst_crs,
                    resampling=rio.enums.Resampling.nearest,
                )
                dssx.append((ds_proj, ds_proj_tf, dst_crs))
    else:
        dssx = dss

    with ExitStack() as stack:
        mfs = [stack.enter_context(MemoryFile()) for ds in dssx]
        for mf, ds in zip(mfs, dssx):
            _write_memfile(mf, ds[0], transform=ds[1], crs=ds[2])

        mfdss = [stack.enter_context(mf.open()) for mf in mfs]
        merged, merged_tf = rio_merge.merge(mfdss)
        return merged.squeeze(0), merged_tf, dssx[0][2]



def get_bbox(shape, padding=0):
    """
    Get a bounding box for a shapely shape, optionally add padding

    Parameters:
        shape: shapely.geometry, required
            a shapely shape
    Returns:
        list: a bounding box with specified padding
    """
    bbox = shape.bounds
    return shapely.geometry.box(*bbox).buffer(padding, cap_style=2, join_style=2).bounds


def reproject_shape(shape, src_crs="", dst_crs=""):
    # https://gis.stackexchange.com/a/127432
    # wgs84 = pyproj.CRS('EPSG:4326')
    # utm = pyproj.CRS('EPSG:32618')
    project = pyproj.Transformer.from_crs(
        pyproj.CRS(src_crs), pyproj.CRS(dst_crs), always_xy=True
    ).transform
    return shapely.ops.transform(project, shape)


@functools.lru_cache(maxsize=128)
def get_crs_transformer(src_crs, dst_crs):
    return pyproj.Transformer.from_crs(src_crs, dst_crs, always_xy=True)


def reproject_bbox(bbox, src_crs, dst_crs):
    transform = get_crs_transformer(src_crs, dst_crs).transform
    return (*transform(*bbox[0:2]), *transform(*bbox[2:4]))
