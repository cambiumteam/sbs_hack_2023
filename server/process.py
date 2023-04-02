import argparse
import asyncio
import json
import os

from geojson import FeatureCollection
import rasterio
from shapely.geometry import GeometryCollection, shape
import numpy as np

from server import utils
from server.sentinel2 import get_ndvi_summary_by_bbox_async, fetch_async, get_inputs, search_catalog

WGS84_CRS = 'epsg:4326'


async def ndvi_summary(start, end, bbox, output):
    """
    Calculate NDVI summary over a given time range for the bbox.
    """
    greenest, greenest_tf, greenest_crs = await get_ndvi_summary_by_bbox_async(
        bbox,
        dates=f"{start}/{end}",
    )
    with rasterio.Env():
        raster = greenest
        with rasterio.open(os.path.join(output, 'ndvi-summary.tif'), 'w',
                           driver="GTiff",
                           height=raster.shape[0],
                           width=raster.shape[1],
                           count=1,
                           dtype=raster.dtype,
                           transform=greenest_tf,
                           crs=greenest_crs,
                           compress='lzw'
                           ) as dst:
            dst.write(raster.astype(rasterio.float64), 1)


async def rgb(start, end, bbox, output):
    items = get_inputs(
        search_catalog(
            bbox,
            dates=f"{start}/{end}",
            query={"platform": {"eq": "sentinel-2a"}}
        ),
        bands=["B04", "B03", "B02"]
    )
    rasters, errors = await fetch_async(items, bbox=bbox, bbox_crs=WGS84_CRS)
    rgb = ["B04", "B03", "B02"]
    for raster_name, raster in rasters.items():
        first = raster["B04"]
        with rasterio.Env():
            with rasterio.open(os.path.join(output, f"{raster_name}-rgb.tif"), 'w',
                               driver="GTiff",
                               height=first[0].shape[0],
                               width=first[0].shape[1],
                               count=3,
                               dtype=rasterio.uint8,
                               transform=first[1],
                               crs=first[2],
                               compress='lzw'
                               ) as dst:
                for id, layer in enumerate(rgb, start=1):
                    data = raster[layer][0]
                    norm = (data * (255 / np.max(data))).astype(np.uint8)
                    dst.write_band(id, norm)


def parse_file(path):
    """
    Parse geojson geometries into an array.
    """
    geometries = []
    with open(path) as json_file:
        try:
            geojson = json.load(json_file)
            for feature in FeatureCollection(**geojson).features:
                geometries.append(shape(feature["geometry"]))
        except Exception as e:
            print(e)

    return geometries


async def process():
    """
    Main process function.
    """

    # Define and parse arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--start", required=True)
    parser.add_argument("-e", "--end", required=True)
    parser.add_argument("-i", "--input", default="/inputs")
    parser.add_argument("-o", "--output", default="/outputs")
    parser.add_argument("-p", "--process", default="ndvi-summary")
    args = parser.parse_args()

    # Collect geometries from geojson files in input directory.
    geometries = []
    input_path = args.input
    # Input path is a directory.
    if os.path.isdir(input_path):
        json_files = [file for file in os.listdir(input_path)]
        for filename in json_files:
            geometries.extend(parse_file(os.path.join(input_path, filename)))
    # Input path is a single file.
    elif os.path.isfile(input_path):
        geometries = parse_file(input_path)

    # Combine geometries and build bbox.
    geom_collection = GeometryCollection(geometries)
    boundary = shape(geom_collection)
    bbox_padded = utils.get_bbox(boundary, padding=1e-3)

    # Process.
    match args.process:
        case "ndvi-summary":
            await ndvi_summary(args.start, args.end, bbox_padded, args.output)
        case "rgb":
            await rgb(args.start, args.end, bbox_padded, args.output)


async def main():
    await asyncio.gather(process())


if __name__ == "__main__":
    import time

    s = time.perf_counter()
    asyncio.run(main())
    elapsed = time.perf_counter() - s
    print(f"{__file__} executed in {elapsed:-1.2f} seconds.")
