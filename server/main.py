import json
import os
import subprocess
from typing import Annotated, Union, List

from fastapi import FastAPI, Query, HTTPException
from pydantic_geojson import PolygonModel
import server.utils as utils
from shapely.geometry import shape
import shapely.geometry
import utm
import rasterio as rio
from server import sentinel2

bacalhau_api_host = os.environ.get("BACALHAU_API_HOST")
docker_tag = "0.0.9"
docker_image = f"ghcr.io/cambiumteam/sentinel-processing:{docker_tag}"

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.post("/job")
async def create_job(inputs: Annotated[List[str], Query()], start: str, end: str, type: str = "ndvi-summary"):
    p = subprocess.run(
        [
            "bacalhau", "--api-host", bacalhau_api_host,
            "docker", "run", "--id-only", "--wait=false",
            "--network", "full",
            "--inputs", inputs[0],
            docker_image, "--",
            "python", "process.py", "-p", type, "-s", start, "-e", end,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if p.returncode == 0:
        return p.stdout.strip()
    else:
        raise HTTPException(status_code=400, detail=p.stdout.strip())


@app.get("/job/{job_id}")
async def get_job(job_id: str):
    p = subprocess.run(
        [
            "bacalhau", "--api-host", bacalhau_api_host,
            "describe", job_id, "--json",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if p.returncode == 0:
        return json.loads(p.stdout.strip())
    else:
        raise HTTPException(status_code=400, detail=p.stdout.strip())


@app.post("/process")
async def process(polygon: PolygonModel):
    boundary = shape(polygon.dict())
    bbox = utils.get_bbox(boundary)
    bbox_padded = utils.get_bbox(boundary, padding=1e-3)
    greenest, greenest_tf, greenest_crs = await sentinel2.get_ndvi_summary_by_bbox_async(
        bbox_padded, 
        dates = '2021-01-01/2021-12-31',
        masked_ratio_threshold=0.3,
    )
    boundary_utm = utils.reproject_shape(
        boundary, 
        src_crs=rio.crs.CRS.from_string('EPSG:4326'),
        dst_crs=greenest_crs
    )
    print(greenest, greenest_tf, greenest_crs)
    
    # bbox_utm = boundary_utm.bounds
    # bbox_padded_utm = utils.get_bbox(
    #     shapely.geometry.box(
    #         *utm.from_latlon(*reversed(bbox_padded[0:2]))[0:2],
    #         *utm.from_latlon(*reversed(bbox_padded[2:4]))[0:2],
    #     )
    # )




